"""Custom exceptions for the application."""

from typing import Optional, Dict, Any


class VehicleIQException(Exception):
    """Base exception for VehicleIQ application."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(VehicleIQException):
    """Validation error exception."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class AuthenticationException(VehicleIQException):
    """Authentication error exception."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationException(VehicleIQException):
    """Authorization error exception."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, code="AUTHORIZATION_ERROR")


class ResourceNotFoundException(VehicleIQException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, code="RESOURCE_NOT_FOUND")


class RateLimitException(VehicleIQException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED")


class ExternalServiceException(VehicleIQException):
    """External service error exception."""

    def __init__(self, service: str, message: str):
        super().__init__(
            f"External service '{service}' error: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
        )
