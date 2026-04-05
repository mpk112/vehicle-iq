"""Metrics and tracking models."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base


class BenchmarkingMetrics(Base):
    """Benchmarking metrics model."""

    __tablename__ = "benchmarking_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Segmentation
    category = Column(String(100), nullable=True)  # make, model, year range
    segment_value = Column(String(100), nullable=True)
    
    # Metrics
    mape = Column(Float, nullable=False)
    dataset_size = Column(Integer, nullable=False)
    
    # Time period
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_metrics_category", "category", "segment_value"),
    )

    def __repr__(self) -> str:
        return f"<BenchmarkingMetrics {self.category}={self.segment_value} MAPE={self.mape}>"


class APIUsage(Base):
    """API usage tracking model."""

    __tablename__ = "api_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # API details
    service_name = Column(String(100), nullable=False, index=True)  # groq, together, paddleocr, yolo
    endpoint = Column(String(200), nullable=True)
    
    # Usage
    request_count = Column(Integer, default=1)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Timing
    total_duration_ms = Column(Float, default=0)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD for daily aggregation

    __table_args__ = (
        Index("idx_api_usage_service_date", "service_name", "date"),
    )

    def __repr__(self) -> str:
        return f"<APIUsage {self.service_name} - {self.request_count} requests>"


class AuditLog(Base):
    """Audit log model."""

    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and action
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Details
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.resource_type} by {self.user_id}>"
