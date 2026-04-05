"""Global error handlers for FastAPI."""

import uuid
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

from app.core.exceptions import (
    VehicleIQException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    RateLimitException,
)

logger = structlog.get_logger()


async def vehicleiq_exception_handler(request: Request, exc: VehicleIQException):
    """Handle VehicleIQ custom exceptions."""
    error_id = str(uuid.uuid4())
    
    logger.error(
        "application_error",
        error_id=error_id,
        code=exc.code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    # Map exception types to HTTP status codes
    status_code_map = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "INTERNAL_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "error_id": error_id,
            },
            "metadata": {
                "timestamp": None,  # Will be set by middleware
            },
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors."""
    error_id = str(uuid.uuid4())
    
    logger.error(
        "validation_error",
        error_id=error_id,
        errors=exc.errors(),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()},
                "error_id": error_id,
            },
            "metadata": {
                "timestamp": None,
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    error_id = str(uuid.uuid4())
    
    logger.exception(
        "unexpected_error",
        error_id=error_id,
        error_type=type(exc).__name__,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
                "error_id": error_id,
            },
            "metadata": {
                "timestamp": None,
            },
        },
    )
