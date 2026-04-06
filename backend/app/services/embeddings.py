"""Embeddings service integration for VehicleIQ.

This module provides integration with the bge-m3 embeddings microservice
for generating 1024-dimensional embeddings for vehicle comparables retrieval.

Follows Requirements 16.1-16.8.
"""

import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.circuit_breaker import CircuitBreaker
from app.core.exceptions import ServiceUnavailableError


class VehicleAttributes(BaseModel):
    """Vehicle attributes for embedding generation following Requirement 16.2."""
    make: str
    model: str
    year: int = Field(ge=1990, le=2030)
    variant: str
    fuel_type: str  # "Petrol", "Diesel", "CNG", "Electric"
    transmission: str  # "Manual", "Automatic"
    mileage: int = Field(ge=0, le=999999)
    location: str


class EmbeddingsService:
    """
    Service for generating embeddings using bge-m3 model.
    Follows Requirements 16.1-16.8.
    """
    
    def __init__(self):
        self.base_url = settings.EMBEDDINGS_URL
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            name="embeddings"
        )
        self.timeout = httpx.Timeout(30.0, connect=10.0)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if embeddings service is healthy.
        
        Returns:
            Health status information
            
        Raises:
            ServiceUnavailableError: If service is not available
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise ServiceUnavailableError(
                f"Embeddings service unavailable: {str(e)}"
            )
    
    async def generate_embedding(
        self,
        vehicle: VehicleAttributes
    ) -> tuple[List[float], str]:
        """
        Generate 1024-dimensional embedding for vehicle attributes.
        Follows Requirements 16.1-16.4.
        
        Args:
            vehicle: Vehicle attributes
            
        Returns:
            Tuple of (embedding vector, formatted description)
            
        Raises:
            ServiceUnavailableError: If embeddings service fails
        """
        async def _call_service():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings/vehicle-attributes",
                    json=vehicle.dict()
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success"):
                    raise ServiceUnavailableError(
                        "Embedding generation failed"
                    )
                
                embedding = data["embedding"]
                description = data["formatted_description"]
                
                # Validate embedding dimension (Requirement 16.4)
                if len(embedding) != 1024:
                    raise ServiceUnavailableError(
                        f"Invalid embedding dimension: {len(embedding)}, expected 1024"
                    )
                
                return embedding, description
        
        try:
            return await self.circuit_breaker.call(_call_service)
        except Exception as e:
            raise ServiceUnavailableError(
                f"Failed to generate embedding: {str(e)}"
            )
    
    async def generate_batch_embeddings(
        self,
        vehicles: List[VehicleAttributes]
    ) -> tuple[List[List[float]], List[str]]:
        """
        Generate embeddings for multiple vehicles in batch.
        Follows Requirement 16.6: support at least 100 vehicles within 10 seconds.
        
        Args:
            vehicles: List of vehicle attributes (max 100)
            
        Returns:
            Tuple of (list of embeddings, list of descriptions)
            
        Raises:
            ServiceUnavailableError: If embeddings service fails
            ValueError: If more than 100 vehicles provided
        """
        if len(vehicles) > 100:
            raise ValueError(
                f"Batch size {len(vehicles)} exceeds maximum of 100"
            )
        
        async def _call_service():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings/vehicle-attributes-batch",
                    json={"vehicles": [v.dict() for v in vehicles]}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data.get("success"):
                    raise ServiceUnavailableError(
                        "Batch embedding generation failed"
                    )
                
                embeddings = data["embeddings"]
                descriptions = data["descriptions"]
                processing_time = data.get("processing_time_seconds", 0)
                
                # Validate batch processing time (Requirement 16.6)
                if processing_time > 10.0:
                    print(
                        f"Warning: Batch processing took {processing_time}s, "
                        f"exceeds 10s requirement"
                    )
                
                # Validate all embeddings have correct dimension
                for i, emb in enumerate(embeddings):
                    if len(emb) != 1024:
                        raise ServiceUnavailableError(
                            f"Invalid embedding dimension at index {i}: "
                            f"{len(emb)}, expected 1024"
                        )
                
                return embeddings, descriptions
        
        try:
            return await self.circuit_breaker.call(_call_service)
        except Exception as e:
            raise ServiceUnavailableError(
                f"Failed to generate batch embeddings: {str(e)}"
            )
    
    async def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        Follows Requirement 16.5: use cosine similarity metric.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        import numpy as np
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity (vectors are already normalized by bge-m3)
        similarity = float(np.dot(vec1, vec2))
        
        return similarity


# Singleton instance
embeddings_service = EmbeddingsService()
