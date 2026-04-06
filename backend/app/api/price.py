"""Price prediction API endpoints."""

import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.price_prediction import (
    PricePredictionService,
    PricePredictionRequest,
    PricePredictionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/price", tags=["price"])


@router.post("/predict", response_model=PricePredictionResponse)
async def predict_price(
    request: PricePredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PricePredictionResponse:
    """
    Predict vehicle price using 4-layer pricing model.
    
    This endpoint calculates vehicle valuation using:
    - Layer 1: Base price lookup from vehicle registry
    - Layer 2: Condition adjustment based on health score
    - Layer 3: RAG-based comparable vehicle retrieval
    - Layer 4: Quantile regression for P10/P50/P90 predictions
    
    Returns persona-specific values:
    - Lender: Fair Sale Value (FSV) = P10 × 0.95
    - Insurer: Insured Declared Value (IDV) = P50 × depreciation_factor
    - Broker: Asking price = P90 × 1.05
    
    Requirements: 2.9, 2.10
    Target: Complete within 5 seconds
    """
    start_time = time.time()
    
    # Validate persona
    valid_personas = ["Lender", "Insurer", "Broker"]
    if request.persona not in valid_personas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid persona. Must be one of: {', '.join(valid_personas)}",
        )
    
    # Initialize price prediction service
    price_service = PricePredictionService()
    
    try:
        # Run price prediction
        result = await price_service.predict_price(
            make=request.make,
            model=request.model,
            year=request.year,
            variant=request.variant,
            fuel_type=request.fuel_type,
            transmission=request.transmission,
            mileage=request.mileage,
            location=request.location,
            health_score=request.health_score,
            persona=request.persona,
            db=db,
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Log performance warning if exceeds 5 seconds
        if processing_time_ms > 5000:
            logger.warning(
                f"Price prediction exceeded 5s target: {processing_time_ms}ms "
                f"for {request.make} {request.model} {request.year}"
            )
        
        # Update processing time in result
        result["processing_time_ms"] = processing_time_ms
        
        return PricePredictionResponse(**result)
        
    except ValueError as e:
        # Handle validation errors (e.g., vehicle not found in registry)
        logger.error(f"Price prediction validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Price prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Price prediction failed: {str(e)}",
        )
