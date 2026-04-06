"""Price prediction service with RAG-based comparable vehicle retrieval.

This module implements the 4-layer pricing model with RAG (Retrieval-Augmented Generation)
for comparable vehicle retrieval using pgvector similarity search.

Follows Requirements 2.1-2.10, 9.1-9.8.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.linear_model import QuantileRegressor
import numpy as np
import redis.asyncio as aioredis

from app.models.vehicle import ComparableVehicle, VehicleRegistry
from app.services.embeddings import VehicleAttributes, embeddings_service
from app.core.exceptions import ServiceUnavailableError
from app.core.config import settings


class ComparableVehicleResult(BaseModel):
    """Comparable vehicle result with similarity score and explainability.
    
    Follows Requirements 9.5, 9.8.
    """
    id: str
    make: str
    model: str
    year: int
    variant: Optional[str]
    fuel_type: Optional[str]
    transmission: Optional[str]
    mileage: Optional[int]
    location: Optional[str]
    listing_price: float
    listing_date: Optional[datetime]
    similarity_score: float = Field(ge=0.0, le=1.0)
    key_differences: List[str] = Field(default_factory=list)


class ComparableSearchConstraints(BaseModel):
    """Constraints for comparable vehicle search.
    
    Follows Requirements 9.4, 9.6.
    """
    make: str
    model: str
    year: int
    mileage: int
    year_range: int = 2  # ±2 years initially
    mileage_range: int = 20000  # ±20k km initially
    min_results: int = 5  # Minimum results before relaxing constraints


class ComparableRetrievalService:
    """Service for RAG-based comparable vehicle retrieval.
    
    Implements vector similarity search with constraint relaxation.
    Follows Requirements 9.1-9.8.
    """
    
    async def search_similar_vehicles(
        self,
        session: AsyncSession,
        vehicle: VehicleAttributes,
        constraints: Optional[ComparableSearchConstraints] = None,
        limit: int = 10
    ) -> List[ComparableVehicleResult]:
        """
        Search for similar vehicles using pgvector cosine similarity.
        
        Follows Requirements 9.1, 9.2, 9.3, 9.4.
        
        Args:
            session: Database session
            vehicle: Vehicle attributes to search for
            constraints: Search constraints (optional, will be created from vehicle if not provided)
            limit: Maximum number of results (default 10)
            
        Returns:
            List of comparable vehicles ordered by similarity score
            
        Raises:
            ServiceUnavailableError: If embedding generation or search fails
        """
        # Generate embedding for the query vehicle (Requirement 9.1)
        try:
            embedding, _ = await embeddings_service.generate_embedding(vehicle)
        except Exception as e:
            raise ServiceUnavailableError(f"Failed to generate embedding: {str(e)}")
        
        # Create constraints if not provided
        if constraints is None:
            constraints = ComparableSearchConstraints(
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                mileage=vehicle.mileage
            )
        
        # Perform similarity search with constraints (Requirements 9.2, 9.3, 9.4)
        results = await self._search_with_constraints(
            session=session,
            embedding=embedding,
            constraints=constraints,
            limit=limit
        )
        
        # If fewer than min_results, relax constraints and retry (Requirement 9.6)
        if len(results) < constraints.min_results:
            relaxed_constraints = ComparableSearchConstraints(
                make=constraints.make,
                model=constraints.model,
                year=constraints.year,
                mileage=constraints.mileage,
                year_range=3,  # Relax to ±3 years
                mileage_range=30000,  # Relax to ±30k km
                min_results=constraints.min_results
            )
            
            results = await self._search_with_constraints(
                session=session,
                embedding=embedding,
                constraints=relaxed_constraints,
                limit=limit
            )
        
        # Add explainability to results (Requirements 9.5, 9.8)
        comparable_results = []
        for comp, similarity in results:
            key_differences = self._generate_key_differences(vehicle, comp)
            
            comparable_results.append(
                ComparableVehicleResult(
                    id=str(comp.id),
                    make=comp.make,
                    model=comp.model,
                    year=comp.year,
                    variant=comp.variant,
                    fuel_type=comp.fuel_type,
                    transmission=comp.transmission,
                    mileage=comp.mileage,
                    location=comp.location,
                    listing_price=comp.listing_price,
                    listing_date=comp.listing_date,
                    similarity_score=similarity,
                    key_differences=key_differences
                )
            )
        
        return comparable_results
    
    async def _search_with_constraints(
        self,
        session: AsyncSession,
        embedding: List[float],
        constraints: ComparableSearchConstraints,
        limit: int
    ) -> List[Tuple[ComparableVehicle, float]]:
        """
        Perform vector similarity search with constraints.
        
        Follows Requirements 9.2, 9.3, 9.4.
        
        Args:
            session: Database session
            embedding: Query embedding vector
            constraints: Search constraints
            limit: Maximum number of results
            
        Returns:
            List of (ComparableVehicle, similarity_score) tuples ordered by similarity
        """
        # Build constraint filters (Requirement 9.4)
        filters = [
            ComparableVehicle.make == constraints.make,
            ComparableVehicle.model == constraints.model,
            ComparableVehicle.year >= constraints.year - constraints.year_range,
            ComparableVehicle.year <= constraints.year + constraints.year_range,
            ComparableVehicle.embedding.isnot(None)  # Only vehicles with embeddings
        ]
        
        # Add mileage constraint if mileage is available
        if constraints.mileage > 0:
            filters.extend([
                ComparableVehicle.mileage >= constraints.mileage - constraints.mileage_range,
                ComparableVehicle.mileage <= constraints.mileage + constraints.mileage_range
            ])
        
        # Perform cosine similarity search using pgvector (Requirements 9.2, 9.3)
        # Note: pgvector's <=> operator returns distance, we convert to similarity
        query = (
            select(
                ComparableVehicle,
                (1 - ComparableVehicle.embedding.cosine_distance(embedding)).label('similarity')
            )
            .where(and_(*filters))
            .order_by(ComparableVehicle.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        
        result = await session.execute(query)
        rows = result.all()
        
        return [(row[0], float(row[1])) for row in rows]
    
    def _generate_key_differences(
        self,
        query_vehicle: VehicleAttributes,
        comparable: ComparableVehicle
    ) -> List[str]:
        """
        Generate explainable key differences between query and comparable vehicle.
        
        Follows Requirements 9.5, 9.8.
        
        Args:
            query_vehicle: Query vehicle attributes
            comparable: Comparable vehicle from database
            
        Returns:
            List of human-readable key differences
        """
        differences = []
        
        # Year difference
        year_diff = comparable.year - query_vehicle.year
        if year_diff != 0:
            if year_diff > 0:
                differences.append(f"{abs(year_diff)} year(s) newer")
            else:
                differences.append(f"{abs(year_diff)} year(s) older")
        
        # Mileage difference
        if comparable.mileage and query_vehicle.mileage:
            mileage_diff = comparable.mileage - query_vehicle.mileage
            if abs(mileage_diff) > 5000:  # Only report significant differences
                if mileage_diff > 0:
                    differences.append(f"{abs(mileage_diff):,} km more mileage")
                else:
                    differences.append(f"{abs(mileage_diff):,} km less mileage")
        
        # Variant difference
        if comparable.variant and query_vehicle.variant:
            if comparable.variant != query_vehicle.variant:
                differences.append(f"Different variant: {comparable.variant}")
        
        # Fuel type difference
        if comparable.fuel_type and query_vehicle.fuel_type:
            if comparable.fuel_type != query_vehicle.fuel_type:
                differences.append(f"Different fuel: {comparable.fuel_type}")
        
        # Transmission difference
        if comparable.transmission and query_vehicle.transmission:
            if comparable.transmission != query_vehicle.transmission:
                differences.append(f"Different transmission: {comparable.transmission}")
        
        # Location difference
        if comparable.location and query_vehicle.location:
            if comparable.location != query_vehicle.location:
                differences.append(f"Different location: {comparable.location}")
        
        # If no differences, indicate it's a close match
        if not differences:
            differences.append("Very similar vehicle")
        
        return differences


# Singleton instance
comparable_retrieval_service = ComparableRetrievalService()


class PricePredictionRequest(BaseModel):
    """Request model for price prediction.
    
    Follows Requirements 2.1-2.10.
    """
    make: str
    model: str
    year: int
    variant: Optional[str] = None
    fuel_type: str
    transmission: str
    mileage: int
    location: str
    health_score: float = Field(ge=0.0, le=100.0)
    persona: str  # "Lender", "Insurer", "Broker"


class PricePredictionResponse(BaseModel):
    """Response model for price prediction.
    
    Follows Requirements 2.1-2.10.
    """
    base_price: float
    adjusted_price: float
    p10: float
    p50: float
    p90: float
    persona_value: float
    comparables: List[ComparableVehicleResult]
    explanation: Dict[str, Any]
    processing_time_ms: int


class PricePredictionService:
    """Service implementing the 4-layer pricing model.
    
    Layer 1: Base price lookup
    Layer 2: Condition adjustment
    Layer 3: Comparable vehicle RAG
    Layer 4: Quantile regression
    
    Follows Requirements 2.1-2.10.
    """
    
    def __init__(self):
        """Initialize the price prediction service."""
        self.comparable_service = comparable_retrieval_service
        self._redis_client: Optional[aioredis.Redis] = None
    
    async def _get_redis(self) -> aioredis.Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis_client
    
    async def get_base_price(
        self,
        session: AsyncSession,
        make: str,
        model: str,
        year: int,
        variant: Optional[str] = None
    ) -> float:
        """
        Layer 1: Base price lookup from vehicle registry.
        
        Follows Requirement 2.1.
        
        Args:
            session: Database session
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            variant: Vehicle variant (optional)
            
        Returns:
            Base price in INR
            
        Raises:
            ValueError: If no base price found
        """
        # Check Redis cache first (24-hour TTL)
        redis = await self._get_redis()
        cache_key = f"base_price:{make}:{model}:{year}:{variant or 'default'}"
        
        cached_price = await redis.get(cache_key)
        if cached_price:
            return float(cached_price)
        
        # Query vehicle registry
        query = select(VehicleRegistry).where(
            and_(
                VehicleRegistry.make == make,
                VehicleRegistry.model == model,
                VehicleRegistry.year == year
            )
        )
        
        # Add variant filter if provided
        if variant:
            query = query.where(VehicleRegistry.variant == variant)
        
        result = await session.execute(query)
        vehicle = result.scalar_one_or_none()
        
        if vehicle and vehicle.base_price:
            base_price = vehicle.base_price
        else:
            # If no exact match, try without variant
            if variant:
                query = select(VehicleRegistry).where(
                    and_(
                        VehicleRegistry.make == make,
                        VehicleRegistry.model == model,
                        VehicleRegistry.year == year
                    )
                )
                result = await session.execute(query)
                vehicle = result.scalar_one_or_none()
                
                if vehicle and vehicle.base_price:
                    base_price = vehicle.base_price
                else:
                    raise ValueError(f"No base price found for {make} {model} {year}")
            else:
                raise ValueError(f"No base price found for {make} {model} {year}")
        
        # Cache for 24 hours
        await redis.setex(cache_key, 86400, str(base_price))
        
        return base_price
    
    def apply_condition_adjustment(
        self,
        base_price: float,
        health_score: float
    ) -> float:
        """
        Layer 2: Apply condition adjustment based on health score.
        
        Follows Requirement 2.2.
        
        Formula: adjusted_price = base_price × (0.70 + 0.45 × health_score/100)
        
        Args:
            base_price: Base price from Layer 1
            health_score: Vehicle health score (0-100)
            
        Returns:
            Condition-adjusted price
        """
        multiplier = 0.70 + 0.45 * (health_score / 100.0)
        adjusted_price = base_price * multiplier
        return adjusted_price
    
    async def retrieve_comparables(
        self,
        session: AsyncSession,
        vehicle: VehicleAttributes
    ) -> List[ComparableVehicleResult]:
        """
        Layer 3: Retrieve comparable vehicles using RAG.
        
        Follows Requirement 2.3.
        
        Args:
            session: Database session
            vehicle: Vehicle attributes
            
        Returns:
            List of comparable vehicles (up to 10)
        """
        comparables = await self.comparable_service.search_similar_vehicles(
            session=session,
            vehicle=vehicle,
            limit=10
        )
        return comparables
    
    def apply_quantile_regression(
        self,
        comparable_prices: List[float],
        health_score: float,
        avg_comparable_health: float = 70.0
    ) -> Tuple[float, float, float]:
        """
        Layer 4: Apply quantile regression to generate P10, P50, P90 predictions.
        
        Follows Requirement 2.4.
        
        Args:
            comparable_prices: List of comparable vehicle prices
            health_score: Query vehicle health score
            avg_comparable_health: Average health score of comparables (default 70)
            
        Returns:
            Tuple of (P10, P50, P90) predictions
        """
        if len(comparable_prices) < 3:
            # Not enough data for quantile regression, use simple percentiles
            sorted_prices = sorted(comparable_prices)
            p10 = sorted_prices[0]
            p50 = sorted_prices[len(sorted_prices) // 2]
            p90 = sorted_prices[-1]
        else:
            # Use quantile regression
            X = np.arange(len(comparable_prices)).reshape(-1, 1)
            y = np.array(comparable_prices)
            
            # Fit quantile regressors for P10, P50, P90
            q10_model = QuantileRegressor(quantile=0.10, alpha=0.0, solver='highs')
            q50_model = QuantileRegressor(quantile=0.50, alpha=0.0, solver='highs')
            q90_model = QuantileRegressor(quantile=0.90, alpha=0.0, solver='highs')
            
            q10_model.fit(X, y)
            q50_model.fit(X, y)
            q90_model.fit(X, y)
            
            # Predict at the median position
            mid_point = np.array([[len(comparable_prices) // 2]])
            p10 = float(q10_model.predict(mid_point)[0])
            p50 = float(q50_model.predict(mid_point)[0])
            p90 = float(q90_model.predict(mid_point)[0])
        
        # Adjust based on health score differential
        health_adjustment = (health_score - avg_comparable_health) / 100.0 * 0.1
        adjustment_factor = 1.0 + health_adjustment
        
        p10 = p10 * adjustment_factor
        p50 = p50 * adjustment_factor
        p90 = p90 * adjustment_factor
        
        # Ensure ordering: P10 <= P50 <= P90
        p10 = min(p10, p50)
        p90 = max(p50, p90)
        
        return p10, p50, p90
    
    def calculate_persona_value(
        self,
        p10: float,
        p50: float,
        p90: float,
        persona: str,
        vehicle_age: int
    ) -> float:
        """
        Calculate persona-specific value from quantile predictions.
        
        Follows Requirements 2.6, 2.7, 2.8.
        
        Args:
            p10: 10th percentile prediction
            p50: 50th percentile prediction
            p90: 90th percentile prediction
            persona: User persona ("Lender", "Insurer", "Broker")
            vehicle_age: Age of vehicle in years
            
        Returns:
            Persona-specific value (FSV, IDV, or asking price)
        """
        if persona == "Lender":
            # FSV = P10 × 0.95 (conservative 5% discount)
            return p10 * 0.95
        
        elif persona == "Insurer":
            # IDV = P50 × depreciation_factor(age)
            # Depreciation: 15% per year, capped at 70% total
            depreciation = max(0.30, 1.0 - (vehicle_age * 0.15))
            return p50 * depreciation
        
        elif persona == "Broker":
            # Asking price = P90 × 1.05 (5% market premium)
            return p90 * 1.05
        
        else:
            # Default to P50
            return p50
    
    async def predict_price(
        self,
        session: AsyncSession,
        request: PricePredictionRequest
    ) -> PricePredictionResponse:
        """
        Complete 4-layer price prediction pipeline.
        
        Follows Requirements 2.1-2.10.
        
        Args:
            session: Database session
            request: Price prediction request
            
        Returns:
            Price prediction response with all layers
            
        Raises:
            ValueError: If base price not found or invalid data
            ServiceUnavailableError: If external services fail
        """
        start_time = datetime.utcnow()
        
        # Layer 1: Base price lookup
        base_price = await self.get_base_price(
            session=session,
            make=request.make,
            model=request.model,
            year=request.year,
            variant=request.variant
        )
        
        # Layer 2: Condition adjustment
        adjusted_price = self.apply_condition_adjustment(
            base_price=base_price,
            health_score=request.health_score
        )
        
        # Layer 3: Comparable vehicle RAG
        vehicle_attrs = VehicleAttributes(
            make=request.make,
            model=request.model,
            year=request.year,
            variant=request.variant or "",
            fuel_type=request.fuel_type,
            transmission=request.transmission,
            mileage=request.mileage,
            location=request.location
        )
        
        comparables = await self.retrieve_comparables(
            session=session,
            vehicle=vehicle_attrs
        )
        
        # Extract comparable prices
        comparable_prices = [comp.listing_price for comp in comparables]
        
        if not comparable_prices:
            # Fallback: use adjusted price as all quantiles
            p10 = p50 = p90 = adjusted_price
        else:
            # Layer 4: Quantile regression
            p10, p50, p90 = self.apply_quantile_regression(
                comparable_prices=comparable_prices,
                health_score=request.health_score
            )
        
        # Calculate persona-specific value
        vehicle_age = datetime.utcnow().year - request.year
        persona_value = self.calculate_persona_value(
            p10=p10,
            p50=p50,
            p90=p90,
            persona=request.persona,
            vehicle_age=vehicle_age
        )
        
        # Build explanation
        explanation = {
            "base_price_source": f"Vehicle registry: {request.make} {request.model} {request.year}",
            "condition_adjustment": {
                "health_score": request.health_score,
                "multiplier": 0.70 + 0.45 * (request.health_score / 100.0),
                "adjusted_price": adjusted_price
            },
            "comparables_used": len(comparables),
            "persona_adjustment": {
                "persona": request.persona,
                "vehicle_age": vehicle_age,
                "calculation": self._get_persona_explanation(request.persona, vehicle_age)
            }
        }
        
        # Calculate processing time
        processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return PricePredictionResponse(
            base_price=base_price,
            adjusted_price=adjusted_price,
            p10=p10,
            p50=p50,
            p90=p90,
            persona_value=persona_value,
            comparables=comparables,
            explanation=explanation,
            processing_time_ms=processing_time_ms
        )
    
    def _get_persona_explanation(self, persona: str, vehicle_age: int) -> str:
        """Get human-readable explanation for persona calculation."""
        if persona == "Lender":
            return "FSV = P10 × 0.95 (conservative 5% discount for lending)"
        elif persona == "Insurer":
            depreciation = max(0.30, 1.0 - (vehicle_age * 0.15))
            return f"IDV = P50 × {depreciation:.2f} (depreciation factor for {vehicle_age} years)"
        elif persona == "Broker":
            return "Asking price = P90 × 1.05 (5% market premium for selling)"
        else:
            return "Default = P50 (median market value)"


# Singleton instance
price_prediction_service = PricePredictionService()
