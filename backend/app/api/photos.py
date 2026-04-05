"""Photo upload and management API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime
import os
from pathlib import Path

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.assessment import Assessment, AssessmentPhoto
from app.services.photo_quality import PhotoQualityGate
from app.schemas.common import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/v1/photos", tags=["photos"])

# Photo storage configuration
STORAGE_PATH = Path("/app/storage/photos")
STORAGE_PATH.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Required photo angles
REQUIRED_ANGLES = [
    "front",
    "rear",
    "left_side",
    "right_side",
    "front_left",
    "front_right",
    "rear_left",
    "rear_right",
    "interior_dashboard",
    "interior_seats",
    "odometer",
    "vin_plate",
    "engine_bay"
]


@router.post("/upload")
async def upload_photo(
    assessment_id: str,
    angle: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a photo for an assessment with quality gate validation.
    
    Args:
        assessment_id: UUID of the assessment
        angle: Photo angle (front, rear, left_side, etc.)
        file: Image file (JPEG/PNG, max 10MB)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Photo metadata with quality check results
    """
    # Validate angle
    if angle not in REQUIRED_ANGLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid angle. Must be one of: {', '.join(REQUIRED_ANGLES)}"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Check if assessment exists and user has access
    result = await db.execute(
        select(Assessment).where(Assessment.id == uuid.UUID(assessment_id))
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check if user owns this assessment
    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload photos for this assessment"
        )
    
    # Run quality gate validation
    quality_result = PhotoQualityGate.validate_photo(file_content)
    
    # Generate unique filename
    photo_id = uuid.uuid4()
    filename = f"{assessment_id}_{angle}_{photo_id}{file_ext}"
    file_path = STORAGE_PATH / filename
    
    # Save file to storage
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create photo record in database
    photo = AssessmentPhoto(
        id=photo_id,
        assessment_id=uuid.UUID(assessment_id),
        angle=angle,
        file_path=str(file_path),
        storage_url=f"/storage/photos/{filename}",
        file_size_bytes=len(file_content),
        quality_passed="true" if quality_result["passed"] else "false",
        quality_checks=quality_result,
        created_at=datetime.utcnow()
    )
    
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    
    return SuccessResponse(
        data={
            "photo_id": str(photo.id),
            "assessment_id": assessment_id,
            "angle": angle,
            "filename": filename,
            "file_size_bytes": len(file_content),
            "quality_passed": quality_result["passed"],
            "quality_score": quality_result["overall_score"],
            "quality_checks": quality_result["checks"],
            "feedback": quality_result["feedback"],
            "storage_url": photo.storage_url,
            "created_at": photo.created_at.isoformat()
        }
    )


@router.get("/{assessment_id}")
async def get_assessment_photos(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all photos for an assessment.
    
    Args:
        assessment_id: UUID of the assessment
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of photos with metadata
    """
    # Check if assessment exists and user has access
    result = await db.execute(
        select(Assessment).where(Assessment.id == uuid.UUID(assessment_id))
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Check if user owns this assessment
    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view photos for this assessment"
        )
    
    # Get all photos
    result = await db.execute(
        select(AssessmentPhoto)
        .where(AssessmentPhoto.assessment_id == uuid.UUID(assessment_id))
        .order_by(AssessmentPhoto.created_at)
    )
    photos = result.scalars().all()
    
    # Check collection completeness
    uploaded_angles = {photo.angle for photo in photos if photo.quality_passed == "true"}
    missing_angles = set(REQUIRED_ANGLES) - uploaded_angles
    is_complete = len(missing_angles) == 0
    
    return SuccessResponse(
        data={
            "assessment_id": assessment_id,
            "photos": [
                {
                    "photo_id": str(photo.id),
                    "angle": photo.angle,
                    "storage_url": photo.storage_url,
                    "file_size_bytes": photo.file_size_bytes,
                    "quality_passed": photo.quality_passed == "true",
                    "quality_checks": photo.quality_checks,
                    "created_at": photo.created_at.isoformat()
                }
                for photo in photos
            ],
            "collection_status": {
                "total_photos": len(photos),
                "passed_photos": len(uploaded_angles),
                "required_angles": len(REQUIRED_ANGLES),
                "missing_angles": list(missing_angles),
                "is_complete": is_complete
            }
        }
    )


@router.get("/angles/required")
async def get_required_angles():
    """
    Get list of required photo angles.
    
    Returns:
        List of required angles with descriptions
    """
    angle_descriptions = {
        "front": "Front view of vehicle",
        "rear": "Rear view of vehicle",
        "left_side": "Left side view",
        "right_side": "Right side view",
        "front_left": "Front left corner",
        "front_right": "Front right corner",
        "rear_left": "Rear left corner",
        "rear_right": "Rear right corner",
        "interior_dashboard": "Dashboard and steering wheel",
        "interior_seats": "Front and rear seats",
        "odometer": "Odometer reading (close-up)",
        "vin_plate": "VIN plate (close-up)",
        "engine_bay": "Engine compartment"
    }
    
    return SuccessResponse(
        data={
            "required_angles": [
                {
                    "angle": angle,
                    "description": angle_descriptions[angle]
                }
                for angle in REQUIRED_ANGLES
            ],
            "total_required": len(REQUIRED_ANGLES)
        }
    )
