"""Manual review models."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base


class ReviewPriority(str, Enum):
    """Review priority enum."""

    STANDARD = "standard"
    HIGH = "high"


class ReviewStatus(str, Enum):
    """Review status enum."""

    PENDING = "pending"
    APPROVED = "approved"
    OVERRIDDEN = "overridden"


class ManualReviewQueue(Base):
    """Manual review queue model."""

    __tablename__ = "manual_review_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    
    # Review details
    priority = Column(String(20), default=ReviewPriority.STANDARD.value, nullable=False)
    status = Column(String(20), default=ReviewStatus.PENDING.value, nullable=False)
    reason = Column(Text, nullable=False)
    
    # Review outcome
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    override_values = Column(JSONB, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ManualReviewQueue {self.assessment_id} - {self.priority} ({self.status})>"


class FraudCase(Base):
    """Confirmed fraud case model."""

    __tablename__ = "fraud_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=True)
    
    # Fraud details
    fraud_type = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    evidence = Column(JSONB, nullable=False)
    
    # Investigation
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    confirmed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<FraudCase {self.fraud_type} - {self.confidence_score}>"
