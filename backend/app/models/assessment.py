"""Assessment-related models."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class AssessmentStatus(str, Enum):
    """Assessment status enum."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Assessment(Base):
    """Assessment model."""

    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Vehicle information
    vin = Column(String(17), nullable=True, index=True)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    variant = Column(String(200), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    mileage = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    registration_number = Column(String(50), nullable=True)
    
    # Persona
    persona = Column(String(50), nullable=False)
    
    # Status
    status = Column(String(20), default=AssessmentStatus.QUEUED.value, nullable=False)
    current_stage = Column(String(100), nullable=True)
    progress_percentage = Column(Integer, default=0)
    
    # AI Results (JSONB for flexibility)
    fraud_result = Column(JSONB, nullable=True)
    health_result = Column(JSONB, nullable=True)
    price_prediction = Column(JSONB, nullable=True)
    damage_detections = Column(JSONB, nullable=True)
    ocr_results = Column(JSONB, nullable=True)
    
    # Flags
    fraud_gate_triggered = Column(String(10), default="false")
    manual_review_required = Column(String(10), default="false")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Relationships
    photos = relationship("AssessmentPhoto", back_populates="assessment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_assessment_status", "status"),
        Index("idx_assessment_user", "user_id"),
        Index("idx_assessment_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Assessment {self.id} - {self.make} {self.model} ({self.status})>"


class AssessmentPhoto(Base):
    """Assessment photo model."""

    __tablename__ = "assessment_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    
    # Photo metadata
    angle = Column(String(50), nullable=False)  # front, rear, left, right, etc.
    file_path = Column(String(500), nullable=False)
    storage_url = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    
    # Quality gate results
    quality_passed = Column(String(10), default="false")
    quality_checks = Column(JSONB, nullable=True)
    
    # OCR and damage detection results
    ocr_result = Column(JSONB, nullable=True)
    damage_detections = Column(JSONB, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="photos")

    def __repr__(self) -> str:
        return f"<AssessmentPhoto {self.angle} for {self.assessment_id}>"
