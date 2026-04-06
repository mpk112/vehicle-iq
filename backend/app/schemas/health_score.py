"""Health score schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class ServiceRecord(BaseModel):
    """Service record schema."""
    date: datetime
    service_type: str = Field(..., description="oil_change, brake_service, general_maintenance, etc.")
    mileage: Optional[int] = None
    cost: Optional[float] = None
    notes: Optional[str] = None


class AccidentRecord(BaseModel):
    """Accident record schema."""
    date: datetime
    severity: str = Field(..., description="minor, moderate, major")
    description: Optional[str] = None
    repair_cost: Optional[float] = None
    airbag_deployed: bool = False


class HealthScoreRequest(BaseModel):
    """Request schema for health score calculation."""
    persona: str = Field(..., description="Lender, Insurer, or Broker")
    damage_detections: Dict
    odometer_reading: int = Field(..., ge=0, le=999999)
    service_records: Optional[List[ServiceRecord]] = None
    accident_history: Optional[List[AccidentRecord]] = None
    fraud_confidence: float = Field(0.0, ge=0, le=100)
    make: str = ""
    model: str = ""
    color: Optional[str] = None
    year: int = Field(..., ge=1990, le=2030)


class HealthScoreComponents(BaseModel):
    """Health score component breakdown."""
    mechanical_condition: float = Field(..., ge=0, le=100)
    exterior_condition: float = Field(..., ge=0, le=100)
    interior_condition: float = Field(..., ge=0, le=100)
    accident_history: float = Field(..., ge=0, le=100)
    service_history: float = Field(..., ge=0, le=100)
    market_appeal: float = Field(..., ge=0, le=100)
    fraud_indicators: float = Field(..., ge=0, le=100)


class HealthScoreResponse(BaseModel):
    """Response schema for health score calculation."""
    health_score: float = Field(..., ge=0, le=100, description="Overall health score (0-100)")
    component_breakdown: Dict[str, float] = Field(..., description="Individual component scores")
    fraud_gate_triggered: bool = Field(..., description="Whether fraud gate was triggered")
    manual_review_required: bool = Field(..., description="Whether manual review is required")
    manual_review_reason: Optional[str] = Field(None, description="Reason for manual review")
    explanation: List[str] = Field(..., description="Human-readable explanation of score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "health_score": 75.5,
                "component_breakdown": {
                    "mechanical_condition": 85.0,
                    "exterior_condition": 70.0,
                    "interior_condition": 80.0,
                    "accident_history": 100.0,
                    "service_history": 70.0,
                    "market_appeal": 75.0,
                    "fraud_indicators": 90.0
                },
                "fraud_gate_triggered": False,
                "manual_review_required": False,
                "manual_review_reason": None,
                "explanation": [
                    "Good overall condition (score: 75.5/100)",
                    "✓ Mechanical Condition: Excellent (85.0/100, weight: 40%)",
                    "• Exterior Condition: Good (70.0/100, weight: 30%)",
                    "✓ Fraud Indicators: Excellent (90.0/100, weight: 20%)"
                ]
            }
        }
