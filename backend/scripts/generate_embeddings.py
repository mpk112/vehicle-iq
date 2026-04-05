"""Generate embeddings for comparable vehicles using BGE-M3 service."""

import asyncio
import sys
from pathlib import Path
import httpx

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, update
from app.core.config import settings
from app.models.vehicle import ComparableVehicle


async def generate_embeddings():
    """Generate embeddings for all comparable vehicles without embeddings."""
    print("🔮 Generating embeddings for comparable vehicles...")
    print("=" * 60)
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Check if embeddings service is available
    embeddings_url = settings.EMBEDDINGS_URL or "http://localhost:8003"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{embeddings_url}/health")
            response.raise_for_status()
            print(f"✅ Embeddings service is available at {embeddings_url}")
    except Exception as e:
        print(f"❌ Embeddings service not available: {e}")
        print(f"   Make sure the service is running at {embeddings_url}")
        return
    
    async with async_session() as session:
        # Get all comparable vehicles without embeddings
        result = await session.execute(
            select(ComparableVehicle).where(ComparableVehicle.embedding.is_(None))
        )
        vehicles = result.scalars().all()
        
        if not vehicles:
            print("✅ All comparable vehicles already have embeddings")
            return
        
        print(f"📊 Found {len(vehicles)} vehicles without embeddings")
        print()
        
        success_count = 0
        error_count = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, vehicle in enumerate(vehicles, 1):
                try:
                    # Format vehicle description
                    description = {
                        "make": vehicle.make,
                        "model": vehicle.model,
                        "year": vehicle.year,
                        "variant": vehicle.variant,
                        "mileage": vehicle.mileage,
                        "condition_summary": vehicle.condition_summary or "",
                        "features": []  # Can be expanded later
                    }
                    
                    # Call embeddings service
                    response = await client.post(
                        f"{embeddings_url}/embeddings/vehicle",
                        json=description
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    embedding = result.get("embedding")
                    
                    if embedding and len(embedding) == 1024:
                        # Update vehicle with embedding
                        await session.execute(
                            update(ComparableVehicle)
                            .where(ComparableVehicle.id == vehicle.id)
                            .values(embedding=embedding)
                        )
                        success_count += 1
                        
                        # Progress indicator
                        if i % 10 == 0:
                            print(f"  Progress: {i}/{len(vehicles)} ({success_count} successful, {error_count} errors)")
                    else:
                        print(f"  ⚠️  Invalid embedding for vehicle {vehicle.id}: dimension {len(embedding) if embedding else 0}")
                        error_count += 1
                
                except Exception as e:
                    print(f"  ❌ Error generating embedding for vehicle {vehicle.id}: {e}")
                    error_count += 1
                
                # Commit in batches
                if i % 100 == 0:
                    await session.commit()
        
        # Final commit
        await session.commit()
        
        print()
        print("=" * 60)
        print("✅ Embedding generation completed!")
        print(f"  Successful: {success_count}")
        print(f"  Errors: {error_count}")
        print(f"  Total: {len(vehicles)}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(generate_embeddings())
