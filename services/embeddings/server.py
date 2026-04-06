"""BGE-M3 embeddings microservice for vehicle comparables retrieval."""

from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from pydantic import BaseModel, Field

app = FastAPI(
    title="BGE-M3 Embeddings Service",
    description="Text embeddings service for VehicleIQ comparable vehicle retrieval",
    version="1.0.0"
)

# Initialize BGE-M3 model (1024-dimensional embeddings)
model = SentenceTransformer('BAAI/bge-m3')


class TextInput(BaseModel):
    """Single text input for embedding generation."""
    text: str = Field(..., min_length=1, max_length=5000)


class BatchTextInput(BaseModel):
    """Batch text input for embedding generation."""
    texts: List[str] = Field(..., min_items=1, max_items=100)


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


class VehicleDescription(BaseModel):
    """Structured vehicle description for embedding generation (legacy)."""
    make: str
    model: str
    year: int
    variant: str
    mileage: int
    condition_summary: str = ""
    features: List[str] = []


class EmbeddingGenerator:
    """Embedding generation functions following Requirements 16.1-16.8."""
    
    @staticmethod
    def normalize_year(year: int) -> float:
        """
        Normalize year to 0-1 range.
        
        Args:
            year: Vehicle year (1990-2030)
            
        Returns:
            Normalized year value (0-1)
        """
        min_year = 1990
        max_year = 2030
        return (year - min_year) / (max_year - min_year)
    
    @staticmethod
    def normalize_mileage(mileage: int) -> float:
        """
        Normalize mileage to 0-1 range.
        
        Args:
            mileage: Vehicle mileage in km (0-999999)
            
        Returns:
            Normalized mileage value (0-1)
        """
        max_mileage = 999999
        return mileage / max_mileage
    
    @staticmethod
    def format_vehicle_attributes(vehicle: VehicleAttributes) -> str:
        """
        Format vehicle attributes into consistent text representation.
        Follows Requirement 16.2: concatenate in order: make, model, year, 
        variant, fuel_type, transmission, mileage, location.
        Follows Requirement 16.3: normalize numerical values.
        
        Args:
            vehicle: Structured vehicle attributes
            
        Returns:
            Formatted text description with normalized values
        """
        # Normalize numerical values
        normalized_year = EmbeddingGenerator.normalize_year(vehicle.year)
        normalized_mileage = EmbeddingGenerator.normalize_mileage(vehicle.mileage)
        
        # Concatenate in consistent order as per Requirement 16.2
        description = (
            f"Make: {vehicle.make}. "
            f"Model: {vehicle.model}. "
            f"Year: {vehicle.year} (normalized: {normalized_year:.4f}). "
            f"Variant: {vehicle.variant}. "
            f"Fuel Type: {vehicle.fuel_type}. "
            f"Transmission: {vehicle.transmission}. "
            f"Mileage: {vehicle.mileage} km (normalized: {normalized_mileage:.6f}). "
            f"Location: {vehicle.location}."
        )
        
        return description
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """
        Generate 1024-dimensional embedding for text.
        Follows Requirement 16.1: use bge-m3 model.
        Follows Requirement 16.4: return 1024 dimensions.
        
        Args:
            text: Input text
            
        Returns:
            1024-dimensional embedding vector
        """
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    @staticmethod
    def generate_vehicle_embedding(vehicle: VehicleAttributes) -> tuple[List[float], str]:
        """
        Generate embedding for vehicle attributes.
        Follows Requirements 16.1-16.4.
        
        Args:
            vehicle: Vehicle attributes
            
        Returns:
            Tuple of (1024-dimensional embedding vector, formatted text)
        """
        # Format vehicle attributes consistently
        description = EmbeddingGenerator.format_vehicle_attributes(vehicle)
        
        # Generate embedding
        embedding = EmbeddingGenerator.generate_embedding(description)
        
        return embedding, description
    
    @staticmethod
    def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        Follows Requirement 16.6: support at least 100 vehicles within 10 seconds.
        
        Args:
            texts: List of input texts (max 100)
            
        Returns:
            List of 1024-dimensional embedding vectors
        """
        embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()
    
    @staticmethod
    def generate_batch_vehicle_embeddings(vehicles: List[VehicleAttributes]) -> tuple[List[List[float]], List[str]]:
        """
        Generate embeddings for multiple vehicles in batch.
        Follows Requirement 16.6: support at least 100 vehicles within 10 seconds.
        
        Args:
            vehicles: List of vehicle attributes (max 100)
            
        Returns:
            Tuple of (list of embeddings, list of formatted descriptions)
        """
        # Format all vehicles consistently
        descriptions = [
            EmbeddingGenerator.format_vehicle_attributes(vehicle)
            for vehicle in vehicles
        ]
        
        # Generate embeddings in batch
        embeddings = EmbeddingGenerator.generate_batch_embeddings(descriptions)
        
        return embeddings, descriptions
    
    @staticmethod
    def format_vehicle_description(vehicle: VehicleDescription) -> str:
        """
        Format vehicle data into text description for embedding (legacy method).
        
        Args:
            vehicle: Structured vehicle data
            
        Returns:
            Formatted text description
        """
        description_parts = [
            f"{vehicle.year} {vehicle.make} {vehicle.model}",
            f"Variant: {vehicle.variant}",
            f"Mileage: {vehicle.mileage:,} km"
        ]
        
        if vehicle.condition_summary:
            description_parts.append(f"Condition: {vehicle.condition_summary}")
        
        if vehicle.features:
            features_str = ", ".join(vehicle.features)
            description_parts.append(f"Features: {features_str}")
        
        return ". ".join(description_parts)
    
    @staticmethod
    def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
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
        
        # Cosine similarity (vectors are already normalized)
        similarity = np.dot(vec1, vec2)
        
        return float(similarity)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "bge-m3-embeddings",
        "version": "1.0.0",
        "model": "BAAI/bge-m3",
        "embedding_dimension": 1024
    }


@app.post("/embeddings/generate")
async def generate_embedding(input_data: TextInput):
    """
    Generate embedding for a single text.
    
    Args:
        input_data: Text input
        
    Returns:
        1024-dimensional embedding vector
    """
    try:
        embedding = EmbeddingGenerator.generate_embedding(input_data.text)
        
        return {
            "success": True,
            "embedding": embedding,
            "dimension": len(embedding),
            "text_length": len(input_data.text)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {str(e)}"
        )


@app.post("/embeddings/batch")
async def generate_batch_embeddings(input_data: BatchTextInput):
    """
    Generate embeddings for multiple texts in batch.
    
    Args:
        input_data: List of texts
        
    Returns:
        List of 1024-dimensional embedding vectors
    """
    try:
        embeddings = EmbeddingGenerator.generate_batch_embeddings(input_data.texts)
        
        return {
            "success": True,
            "embeddings": embeddings,
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch embedding generation failed: {str(e)}"
        )


@app.post("/embeddings/vehicle")
async def generate_vehicle_embedding(vehicle: VehicleDescription):
    """
    Generate embedding for structured vehicle data (legacy endpoint).
    
    Args:
        vehicle: Structured vehicle description
        
    Returns:
        1024-dimensional embedding vector and formatted text
    """
    try:
        # Format vehicle data into text
        description = EmbeddingGenerator.format_vehicle_description(vehicle)
        
        # Generate embedding
        embedding = EmbeddingGenerator.generate_embedding(description)
        
        return {
            "success": True,
            "embedding": embedding,
            "dimension": len(embedding),
            "formatted_description": description
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vehicle embedding generation failed: {str(e)}"
        )


@app.post("/embeddings/vehicle-attributes")
async def generate_vehicle_attributes_embedding(vehicle: VehicleAttributes):
    """
    Generate embedding for vehicle attributes following Requirements 16.1-16.4.
    Concatenates attributes in consistent order and normalizes numerical values.
    
    Args:
        vehicle: Vehicle attributes (make, model, year, variant, fuel_type, 
                 transmission, mileage, location)
        
    Returns:
        1024-dimensional embedding vector and formatted text
    """
    try:
        # Generate embedding with proper formatting
        embedding, description = EmbeddingGenerator.generate_vehicle_embedding(vehicle)
        
        return {
            "success": True,
            "embedding": embedding,
            "dimension": len(embedding),
            "formatted_description": description,
            "vehicle": vehicle.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vehicle attributes embedding generation failed: {str(e)}"
        )


class BatchVehicleAttributes(BaseModel):
    """Batch vehicle attributes for embedding generation."""
    vehicles: List[VehicleAttributes] = Field(..., min_items=1, max_items=100)


@app.post("/embeddings/vehicle-attributes-batch")
async def generate_batch_vehicle_attributes_embeddings(batch: BatchVehicleAttributes):
    """
    Generate embeddings for multiple vehicles in batch.
    Follows Requirement 16.6: support at least 100 vehicles within 10 seconds.
    
    Args:
        batch: List of vehicle attributes (max 100)
        
    Returns:
        List of 1024-dimensional embedding vectors and formatted descriptions
    """
    try:
        import time
        start_time = time.time()
        
        # Generate embeddings in batch
        embeddings, descriptions = EmbeddingGenerator.generate_batch_vehicle_embeddings(
            batch.vehicles
        )
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "embeddings": embeddings,
            "descriptions": descriptions,
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0,
            "processing_time_seconds": round(processing_time, 3)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch vehicle embedding generation failed: {str(e)}"
        )


class SimilarityRequest(BaseModel):
    """Request for similarity calculation."""
    text1: str = Field(..., min_length=1)
    text2: str = Field(..., min_length=1)


@app.post("/embeddings/similarity")
async def calculate_similarity(request: SimilarityRequest):
    """
    Calculate similarity between two texts.
    
    Args:
        request: Similarity request with two texts
        
    Returns:
        Cosine similarity score (0-1)
    """
    try:
        # Generate embeddings
        embedding1 = EmbeddingGenerator.generate_embedding(request.text1)
        embedding2 = EmbeddingGenerator.generate_embedding(request.text2)
        
        # Calculate similarity
        similarity = EmbeddingGenerator.calculate_similarity(embedding1, embedding2)
        
        return {
            "success": True,
            "similarity": similarity,
            "text1_length": len(request.text1),
            "text2_length": len(request.text2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Similarity calculation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
