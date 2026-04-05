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


class VehicleDescription(BaseModel):
    """Structured vehicle description for embedding generation."""
    make: str
    model: str
    year: int
    variant: str
    mileage: int
    condition_summary: str = ""
    features: List[str] = []


class EmbeddingGenerator:
    """Embedding generation functions."""
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """
        Generate 1024-dimensional embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            1024-dimensional embedding vector
        """
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    @staticmethod
    def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of 1024-dimensional embedding vectors
        """
        embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()
    
    @staticmethod
    def format_vehicle_description(vehicle: VehicleDescription) -> str:
        """
        Format vehicle data into text description for embedding.
        
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
    Generate embedding for structured vehicle data.
    
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


@app.post("/embeddings/similarity")
async def calculate_similarity(
    text1: str = Field(..., min_length=1),
    text2: str = Field(..., min_length=1)
):
    """
    Calculate similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Cosine similarity score (0-1)
    """
    try:
        # Generate embeddings
        embedding1 = EmbeddingGenerator.generate_embedding(text1)
        embedding2 = EmbeddingGenerator.generate_embedding(text2)
        
        # Calculate similarity
        similarity = EmbeddingGenerator.calculate_similarity(embedding1, embedding2)
        
        return {
            "success": True,
            "similarity": similarity,
            "text1_length": len(text1),
            "text2_length": len(text2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Similarity calculation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
