"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import VehicleIQException
from app.core.error_handlers import (
    vehicleiq_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.api import auth, photos, image_intelligence

app = FastAPI(
    title="VehicleIQ API",
    description="AI-powered vehicle assessment platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(VehicleIQException, vehicleiq_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(photos.router)
app.include_router(image_intelligence.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "vehicleiq-api",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "VehicleIQ API",
        "docs": "/docs",
        "health": "/health",
    }
