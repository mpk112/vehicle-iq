"""Common schemas used across the application."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from uuid import UUID


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ResponseMetadata(BaseModel):
    """Response metadata schema."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[UUID] = None
    processing_time_ms: Optional[float] = None


class APIResponse(BaseModel):
    """Standard API response wrapper."""

    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response schema."""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
