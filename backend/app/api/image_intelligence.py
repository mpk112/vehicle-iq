"""Image Intelligence API endpoints."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import List
from app.services.image_intelligence import ImageIntelligenceService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/v1/image-intelligence", tags=["Image Intelligence"])


@router.post("/process")
async def process_single_photo(
    file: UploadFile = File(...),
    photo_angle: str = "unknown",
    current_user: User = Depends(get_current_user)
):
    """
    Process a single photo through complete pipeline: quality → OCR → damage detection.
    
    Args:
        file: Image file (JPEG/PNG)
        photo_angle: Photo angle type (front, rear, left, right, odometer, vin_plate, etc.)
        current_user: Authenticated user
        
    Returns:
        Complete analysis including quality check, OCR, and damage detection
    """
    try:
        # Read file content
        content = await file.read()
        
        # Process through pipeline
        service = ImageIntelligenceService()
        result = await service.process_photo_complete(content, photo_angle)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed: {str(e)}"
        )


@router.post("/process/batch")
async def process_batch_photos(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Process multiple photos in parallel (e.g., 13 required angles).
    
    Args:
        files: List of image files
        current_user: Authenticated user
        
    Returns:
        Aggregated analysis across all photos
    """
    try:
        # Prepare photos for processing
        photos = []
        for file in files:
            content = await file.read()
            # Try to infer angle from filename
            angle = _infer_angle_from_filename(file.filename)
            photos.append({"bytes": content, "angle": angle})
        
        # Process batch
        service = ImageIntelligenceService()
        result = await service.process_batch_photos(photos)
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch image processing failed: {str(e)}"
        )


def _infer_angle_from_filename(filename: str) -> str:
    """
    Infer photo angle from filename.
    
    Args:
        filename: Image filename
        
    Returns:
        Inferred angle or 'unknown'
    """
    filename_lower = filename.lower()
    
    angle_keywords = {
        "front": "front",
        "rear": "rear",
        "back": "rear",
        "left": "left_side",
        "right": "right_side",
        "odometer": "odometer",
        "odo": "odometer",
        "vin": "vin_plate",
        "registration": "registration_front",
        "reg": "registration_front",
        "interior": "interior",
        "dashboard": "dashboard",
        "engine": "engine",
        "trunk": "trunk",
        "boot": "trunk"
    }
    
    for keyword, angle in angle_keywords.items():
        if keyword in filename_lower:
            return angle
    
    return "unknown"
