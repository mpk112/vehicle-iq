"""Fraud detection API endpoints."""

import logging
from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import time

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.assessment import Assessment
from app.schemas.fraud import (
    FraudDetectionRequest,
    FraudDetectionResponse,
    FraudSignal,
    APIUsageStats,
)
from app.services.fraud_detection import FraudDetectionEngine
from app.services.api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/fraud", tags=["fraud"])


@router.post("/detect", response_model=FraudDetectionResponse)
async def detect_fraud(
    request: FraudDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FraudDetectionResponse:
    """
    Run fraud detection on an assessment.
    
    This endpoint analyzes an assessment for fraud indicators using 9 fraud signals:
    1. VIN clone detection
    2. Photo reuse detection
    3. Odometer rollback
    4. Flood damage
    5. Document tampering
    6. Claim history cross-match
    7. Registration mismatch
    8. Salvage title check
    9. Stolen vehicle check
    
    Returns overall fraud confidence (0-100) and detailed signal results.
    """
    start_time = time.time()
    
    # Get assessment
    assessment = db.query(Assessment).filter(Assessment.id == request.assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {request.assessment_id} not found",
        )
    
    # Check if user has access to this assessment
    # TODO: Implement proper authorization check based on organization
    
    # Initialize fraud detection engine
    fraud_engine = FraudDetectionEngine(db)
    
    # Run fraud detection
    try:
        # Get photo bytes (for now, use empty list as placeholder)
        # TODO: Load actual photo bytes from storage
        photos = []
        
        fraud_result = await fraud_engine.detect_fraud(
            vin=assessment.vin,
            photos=photos,
            ocr_results=assessment.ocr_results or {},
            damage_detections=assessment.damage_detections or {},
            mileage=assessment.mileage,
        )
        
        # Update assessment with fraud results
        assessment.fraud_result = fraud_result
        assessment.fraud_confidence = fraud_result["fraud_confidence"]
        assessment.fraud_gate_triggered = fraud_result["fraud_gate_triggered"]
        
        # If fraud gate triggered, add to manual review queue
        if fraud_result["fraud_gate_triggered"]:
            assessment.requires_manual_review = True
            assessment.manual_review_reason = "High fraud confidence detected"
            logger.warning(
                f"Fraud gate triggered for assessment {assessment.id}: "
                f"confidence={fraud_result['fraud_confidence']}"
            )
        
        db.commit()
        
        # Convert signals to schema format
        signals_dict = {}
        for signal_type, signal_data in fraud_result["signals"].items():
            signals_dict[signal_type] = FraudSignal(
                signal_type=signal_type,
                detected=signal_data["detected"],
                confidence=signal_data["confidence"],
                evidence=signal_data.get("evidence"),
                details=signal_data.get("details", {}),
            )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return FraudDetectionResponse(
            assessment_id=assessment.id,
            fraud_confidence=fraud_result["fraud_confidence"],
            fraud_gate_triggered=fraud_result["fraud_gate_triggered"],
            recommended_action=fraud_result["recommended_action"],
            signals=signals_dict,
            evidence=fraud_result["evidence"],
            processing_time_ms=processing_time_ms,
        )
        
    except Exception as e:
        logger.error(f"Fraud detection failed for assessment {assessment.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud detection failed: {str(e)}",
        )


@router.get("/admin/api-usage", response_model=Dict[str, Any])
async def get_api_usage(
    service: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get API usage statistics.
    
    Admin-only endpoint that returns usage statistics for external APIs:
    - Groq (LLM)
    - Together.ai (LLM fallback)
    - PaddleOCR (OCR)
    - YOLOv8n (damage detection)
    - BGE-M3 (embeddings)
    
    Shows total requests, success/failure counts, remaining quota, and fallback events.
    
    Args:
        service: Optional service name to filter by
    """
    # Check if user is admin
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    # Get usage statistics
    rate_limiter = APIRateLimiter(db)
    stats = rate_limiter.get_usage_stats(service_name=service)
    
    # Add fallback count
    fallback_count = rate_limiter.get_fallback_count()
    stats["fallback_events_today"] = fallback_count
    
    # Add rate limit status for each service
    rate_limits = {}
    for service_name in ["groq", "together_ai", "paddleocr", "yolo", "embeddings"]:
        rate_limits[service_name] = rate_limiter.check_rate_limit(service_name)
    
    stats["rate_limits"] = rate_limits
    
    return stats


@router.get("/admin/api-usage/{service}", response_model=APIUsageStats)
async def get_service_usage(
    service: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIUsageStats:
    """
    Get detailed usage statistics for a specific service.
    
    Args:
        service: Service name (groq, together_ai, paddleocr, yolo, embeddings)
    """
    # Check if user is admin
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    # Validate service name
    valid_services = ["groq", "together_ai", "paddleocr", "yolo", "embeddings"]
    if service not in valid_services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service name. Must be one of: {', '.join(valid_services)}",
        )
    
    # Get usage statistics
    rate_limiter = APIRateLimiter(db)
    stats = rate_limiter.get_usage_stats(service_name=service)
    
    if not stats["services"]:
        # No usage data for this service today
        return APIUsageStats(
            service=service,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            fallback_triggered=0,
            remaining_quota=rate_limiter.RATE_LIMITS.get(service, 999999),
            quota_percentage=0.0,
        )
    
    service_stats = stats["services"][0]
    
    # Get fallback count if this is groq
    fallback_count = 0
    if service == "groq":
        fallback_count = rate_limiter.get_fallback_count()
    
    return APIUsageStats(
        service=service,
        total_requests=service_stats["total_requests"],
        successful_requests=service_stats["successful_requests"],
        failed_requests=service_stats["failed_requests"],
        fallback_triggered=fallback_count,
        remaining_quota=service_stats["remaining_quota"],
        quota_percentage=service_stats["quota_percentage"],
    )
