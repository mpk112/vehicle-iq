"""Health score API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.health_score import HealthScoreRequest, HealthScoreResponse
from app.schemas.common import ErrorResponse
from app.services.health_score import HealthScoreEngine

router = APIRouter(prefix="/v1/health-score", tags=["health-score"])


@router.post(
    "/calculate",
    response_model=HealthScoreResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Calculate vehicle health score",
    description="""
    Calculate vehicle health score with persona-specific weighting.
    
    The health score is a composite 0-100 score based on:
    - Mechanical condition (engine, transmission, suspension)
    - Exterior condition (paint, body, glass)
    - Interior condition (seats, dashboard, electronics)
    - Accident history
    - Service history
    - Market appeal
    - Fraud indicators
    
    Persona-specific weights:
    - **Lender**: Mechanical (40%), Exterior (30%), Fraud (20%), Service (10%)
    - **Insurer**: Accident (35%), Mechanical (30%), Fraud (25%), Exterior (10%)
    - **Broker**: Exterior (45%), Mechanical (25%), Market Appeal (20%), Fraud (10%)
    
    **Fraud Gate Logic**: If fraud_confidence > 60, health score is capped at 30 and 
    manual review is triggered.
    
    **Low Health Score**: If health_score < 40, manual review is triggered.
    """
)
async def calculate_health_score(
    request: HealthScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> HealthScoreResponse:
    """
    Calculate vehicle health score.
    
    Args:
        request: Health score calculation request
        db: Database session
        current_user: Authenticated user
        
    Returns:
        HealthScoreResponse with score, component breakdown, and explanation
    """
    try:
        # Initialize health score engine
        engine = HealthScoreEngine(db)
        
        # Convert service records to dict format
        service_records = None
        if request.service_records:
            service_records = [record.model_dump() for record in request.service_records]
        
        # Convert accident history to dict format
        accident_history = None
        if request.accident_history:
            accident_history = [record.model_dump() for record in request.accident_history]
        
        # Calculate health score
        result = await engine.calculate_health_score(
            persona=request.persona,
            damage_detections=request.damage_detections,
            odometer_reading=request.odometer_reading,
            service_records=service_records,
            accident_history=accident_history,
            fraud_confidence=request.fraud_confidence,
            make=request.make,
            model=request.model,
            color=request.color,
            year=request.year
        )
        
        return HealthScoreResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate health score: {str(e)}"
        )


@router.get(
    "/persona-weights",
    response_model=Dict[str, Dict[str, float]],
    status_code=status.HTTP_200_OK,
    summary="Get persona-specific component weights",
    description="""
    Get the component weights used for each persona.
    
    This endpoint returns the weighting configuration used to calculate
    persona-specific health scores.
    """
)
async def get_persona_weights(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Dict[str, float]]:
    """
    Get persona-specific component weights.
    
    Returns:
        Dict mapping persona to component weights
    """
    return HealthScoreEngine.PERSONA_WEIGHTS
