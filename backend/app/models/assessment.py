"""Assessment models for VehicleIQ."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Assessment(Base):
    """Assessment model - immutable core record of vehicle assessment."""
    
    __tablename__ = "assessments"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and organization
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization = Column(String(255), nullable=False)
    
    # Vehicle information
    vin = Column(String(17), nullable=False, index=True)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    variant = Column(String(100))
    fuel_type = Column(String(50))
    transmission = Column(String(50))
    mileage = Column(Integer)
    location = Column(String(100))
    registration_number = Column(String(20), index=True)
    
    # Assessment metadata
    persona = Column(String(50), nullable=False)  # Lender, Insurer, Broker
    status = Column(String(50), nullable=False, default="queued", index=True)  # queued, processing, completed, failed
    current_stage = Column(String(100))  # Current pipeline stage
    progress_percentage = Column(Integer, default=0)
    
    # AI outputs (JSONB for flexibility)
    fraud_result = Column(JSONB)  # {confidence, signals, evidence}
    health_result = Column(JSONB)  # {score, components, explanation}
    price_prediction = Column(JSONB)  # {base_price, p10, p50, p90, persona_value, comparables}
    damage_detections = Column(JSONB)  # {detections, summary}
    ocr_results = Column(JSONB)  # {odometer, vin, registration, owner}
    
    # Fraud gate
    fraud_gate_triggered = Column(Boolean, default=False, index=True)
    fraud_confidence = Column(Float, default=0.0, index=True)
    
    # Manual review
    requires_manual_review = Column(Boolean, default=False, index=True)
    manual_review_reason = Column(String(255))
    reviewed_at = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_notes = Column(Text)
    
    # Override values (append-only, preserves immutability)
    override_values = Column(JSONB)  # {field: {old, new, reason, by, at}}
    
    # Benchmarking
    actual_transaction_price = Column(Float)
    transaction_date = Column(DateTime)
    transaction_type = Column(String(50))  # sale, loan, insurance
    prediction_error = Column(Float)  # actual - predicted
    
    # Processing metadata
    processing_time_ms = Column(Integer)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="assessments")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    photos = relationship("AssessmentPhoto", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment {self.id} - {self.year} {self.make} {self.model} - {self.status}>"


class AssessmentPhoto(Base):
    """Assessment photo model - stores photo metadata and AI results."""
    
    __tablename__ = "assessment_photos"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False, index=True)
    
    # Photo metadata
    photo_angle = Column(String(50), nullable=False)  # front, rear, odometer, vin_plate, etc.
    storage_path = Column(String(500), nullable=False)  # S3 path or local path
    file_size = Column(Integer)  # bytes
    mime_type = Column(String(50))
    
    # Quality gate results
    quality_passed = Column(Boolean, default=False)
    quality_checks = Column(JSONB)  # {blur, lighting, resolution, framing}
    quality_feedback = Column(Text)
    
    # OCR results (for specific angles)
    ocr_extracted = Column(Boolean, default=False)
    ocr_results = Column(JSONB)  # {odometer, vin, registration, owner, etc.}
    ocr_confidence = Column(Float)
    
    # Damage detection results
    damage_detected = Column(Boolean, default=False)
    damage_detections = Column(JSONB)  # [{type, severity, confidence, bbox}]
    damage_count = Column(Integer, default=0)
    
    # Processing metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    processing_time_ms = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="photos")
    
    def __repr__(self):
        return f"<AssessmentPhoto {self.id} - {self.photo_angle} - Quality: {self.quality_passed}>"
