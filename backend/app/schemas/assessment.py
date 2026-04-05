"""Assessment schemas for API requests and responses."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AssessmentCreate(BaseModel):
    """Schema for creating a new assessment."""
    
    # Vehicle information
    vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2030)
    variant: Optional[str] = Field(None, max_length=100)
    fuel_type: Optional[str] = Field(None, max_length=50)
    transmission: Optional[str] = Field(None, max_length=50)
    mileage: Optional[int] = Field(None, ge=0, le=1000000)
    location: Optional[str] = Field(None, max_length=100)
    registration_number: Optional[str] = Field(None, max_length=20)
    
    # Assessment metadata
    persona: str = Field(..., description="Lender, Insurer, or Broker")
    
    @validator('persona')
    def validate_persona(cls, v):
        allowed = ['Lender', 'Insurer', 'Broker']
        if v not in allowed:
            raise ValueError(f'Persona must be one of: {", ".join(allowed)}')
        return v
    
    @validator('vin')
    def validate_vin(cls, v):
        # VIN should not contain I, O, Q
        if any(char in v.upper() for char in ['I', 'O', 'Q']):
            raise ValueError('VIN cannot contain letters I, O, or Q')
        return v.upper()


class AssessmentResponse(BaseModel):
    """Schema for assessment response."""
    
    id: UUID
    user_id: UUID
    organization: str
    
    # Vehicle information
    vin: str
    make: str
    model: str
    year: int
    variant: Optional[str]
    fuel_type: Optional[str]
    transmission: Optional[str]
    mileage: Optional[int]
    location: Optional[str]
    registration_number: Optional[str]
    
    # Assessment metadata
    persona: str
    status: str
    current_stage: Optional[str]
    progress_percentage: int
    
    # AI outputs
    fraud_result: Optional[Dict[str, Any]]
    health_result: Optional[Dict[str, Any]]
    price_prediction: Optional[Dict[str, Any]]
    damage_detections: Optional[Dict[str, Any]]
    ocr_results: Optional[Dict[str, Any]]
    
    # Fraud gate
    fraud_gate_triggered: bool
    fraud_confidence: float
    
    # Manual review
    requires_manual_review: bool
    manual_review_reason: Optional[str]
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    review_notes: Optional[str]
    
    # Processing metadata
    processing_time_ms: Optional[int]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    error_message: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentListItem(BaseModel):
    """Schema for assessment list item (summary)."""
    
    id: UUID
    vin: str
    make: str
    model: str
    year: int
    persona: str
    status: str
    fraud_confidence: float
    fraud_gate_triggered: bool
    requires_manual_review: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentPhotoUpload(BaseModel):
    """Schema for photo upload metadata."""
    
    assessment_id: UUID
    photo_angle: str = Field(..., description="front, rear, odometer, vin_plate, etc.")
    
    @validator('photo_angle')
    def validate_angle(cls, v):
        allowed = [
            'front', 'rear', 'left_side', 'right_side',
            'front_left_diagonal', 'front_right_diagonal',
            'rear_left_diagonal', 'rear_right_diagonal',
            'interior_dashboard', 'odometer', 'vin_plate',
            'registration_front', 'registration_back'
        ]
        if v not in allowed:
            raise ValueError(f'Photo angle must be one of: {", ".join(allowed)}')
        return v


class AssessmentPhotoResponse(BaseModel):
    """Schema for assessment photo response."""
    
    id: UUID
    assessment_id: UUID
    photo_angle: str
    storage_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    
    # Quality gate
    quality_passed: bool
    quality_checks: Optional[Dict[str, Any]]
    quality_feedback: Optional[str]
    
    # OCR results
    ocr_extracted: bool
    ocr_results: Optional[Dict[str, Any]]
    ocr_confidence: Optional[float]
    
    # Damage detection
    damage_detected: bool
    damage_detections: Optional[Dict[str, Any]]
    damage_count: int
    
    # Timestamps
    uploaded_at: datetime
    processed_at: Optional[datetime]
    processing_time_ms: Optional[int]
    
    class Config:
        from_attributes = True


class AssessmentFilter(BaseModel):
    """Schema for filtering assessments."""
    
    status: Optional[str] = None
    persona: Optional[str] = None
    fraud_flagged: Optional[bool] = None
    requires_review: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
