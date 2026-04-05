"""Fraud detection schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID


class FraudDetectionRequest(BaseModel):
    """Schema for fraud detection request."""
    
    assessment_id: UUID = Field(..., description="Assessment ID to run fraud detection on")


class FraudSignal(BaseModel):
    """Schema for individual fraud signal."""
    
    signal_type: str = Field(..., description="Type of fraud signal")
    detected: bool = Field(..., description="Whether fraud was detected")
    confidence: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    evidence: Optional[str] = Field(None, description="Evidence description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")


class FraudDetectionResponse(BaseModel):
    """Schema for fraud detection response."""
    
    assessment_id: UUID
    fraud_confidence: float = Field(..., ge=0, le=100, description="Overall fraud confidence 0-100")
    fraud_gate_triggered: bool = Field(..., description="Whether fraud gate was triggered (>60)")
    recommended_action: str = Field(..., description="Recommended action based on confidence")
    
    signals: Dict[str, FraudSignal] = Field(..., description="Individual fraud signals")
    evidence: List[str] = Field(default_factory=list, description="List of evidence")
    
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class APIUsageStats(BaseModel):
    """Schema for API usage statistics."""
    
    service: str = Field(..., description="Service name (groq, together_ai, etc.)")
    total_requests: int = Field(..., description="Total requests today")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    fallback_triggered: int = Field(..., description="Times fallback was triggered")
    remaining_quota: Optional[int] = Field(None, description="Remaining free tier quota")
    quota_percentage: Optional[float] = Field(None, description="Percentage of quota used")
