"""Assessment API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.assessment import Assessment, AssessmentPhoto
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentListItem,
    AssessmentFilter
)

router = APIRouter(prefix="/v1/assessments", tags=["Assessments"])


@router.post("", response_model=AssessmentResponse, status_code=201)
async def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new vehicle assessment.
    
    Creates an assessment record with status 'queued' for async processing.
    Returns assessment_id and estimated completion time.
    """
    # Create assessment
    assessment = Assessment(
        id=uuid.uuid4(),
        user_id=current_user.id,
        organization=current_user.organization or "Unknown",
        vin=assessment_data.vin,
        make=assessment_data.make,
        model=assessment_data.model,
        year=assessment_data.year,
        variant=assessment_data.variant,
        fuel_type=assessment_data.fuel_type,
        transmission=assessment_data.transmission,
        mileage=assessment_data.mileage,
        location=assessment_data.location,
        registration_number=assessment_data.registration_number,
        persona=assessment_data.persona,
        status="queued",
        progress_percentage=0,
        fraud_gate_triggered=False,
        fraud_confidence=0.0,
        requires_manual_review=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    
    return assessment


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get assessment by ID.
    
    Returns complete assessment data including AI outputs and processing status.
    """
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Check access (user can only see their own assessments unless Admin)
    if current_user.role != "Admin" and assessment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return assessment


@router.get("", response_model=List[AssessmentListItem])
async def list_assessments(
    status: Optional[str] = Query(None),
    persona: Optional[str] = Query(None),
    fraud_flagged: Optional[bool] = Query(None),
    requires_review: Optional[bool] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List assessments with filtering and pagination.
    
    Supports filtering by status, persona, fraud flags, review status, and date range.
    """
    # Build query
    query = select(Assessment)
    
    # Filter by user (unless Admin)
    if current_user.role != "Admin":
        query = query.where(Assessment.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.where(Assessment.status == status)
    
    if persona:
        query = query.where(Assessment.persona == persona)
    
    if fraud_flagged is not None:
        query = query.where(Assessment.fraud_gate_triggered == fraud_flagged)
    
    if requires_review is not None:
        query = query.where(Assessment.requires_manual_review == requires_review)
    
    if date_from:
        query = query.where(Assessment.created_at >= date_from)
    
    if date_to:
        query = query.where(Assessment.created_at <= date_to)
    
    # Order by created_at desc
    query = query.order_by(Assessment.created_at.desc())
    
    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute
    result = await db.execute(query)
    assessments = result.scalars().all()
    
    return assessments


@router.get("/{assessment_id}/photos", response_model=List[dict])
async def get_assessment_photos(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all photos for an assessment.
    
    Returns photo metadata, quality gate results, OCR results, and damage detections.
    """
    # Check assessment exists and user has access
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if current_user.role != "Admin" and assessment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get photos
    result = await db.execute(
        select(AssessmentPhoto).where(AssessmentPhoto.assessment_id == assessment_id)
    )
    photos = result.scalars().all()
    
    return [
        {
            "id": str(photo.id),
            "photo_angle": photo.photo_angle,
            "storage_path": photo.storage_path,
            "quality_passed": photo.quality_passed,
            "quality_checks": photo.quality_checks,
            "ocr_results": photo.ocr_results,
            "damage_detections": photo.damage_detections,
            "damage_count": photo.damage_count,
            "uploaded_at": photo.uploaded_at.isoformat() if photo.uploaded_at else None
        }
        for photo in photos
    ]


@router.delete("/{assessment_id}", status_code=204)
async def delete_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an assessment (Admin only or own assessment if not completed).
    
    Deletes assessment and all associated photos (cascade).
    """
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Check permissions
    if current_user.role != "Admin":
        if assessment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        if assessment.status == "completed":
            raise HTTPException(status_code=403, detail="Cannot delete completed assessment")
    
    await db.delete(assessment)
    await db.commit()
    
    return None
