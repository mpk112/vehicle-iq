"""bge-m3 embeddings microservice."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from typing import List

app = FastAPI(title="Embeddings Service")

# Initialize bge-m3 model
model = SentenceTransformer('BAAI/bge-m3')


class EmbeddingRequest(BaseModel):
    """Embedding request schema."""
    text: str


class BatchEmbeddingRequest(BaseModel):
    """Batch embedding request schema."""
    texts: List[str]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "embeddings"}


@app.post("/embed")
async def generate_embedding(request: EmbeddingRequest):
    """Generate embedding for text."""
    try:
        embedding = model.encode(request.text)
        
        return {
            "success": True,
            "embedding": embedding.tolist(),
            "dimension": len(embedding),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed/batch")
async def generate_embeddings_batch(request: BatchEmbeddingRequest):
    """Generate embeddings for multiple texts."""
    try:
        embeddings = model.encode(request.texts)
        
        return {
            "success": True,
            "embeddings": [emb.tolist() for emb in embeddings],
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if len(embeddings) > 0 else 0,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
