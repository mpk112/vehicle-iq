"""Integration tests for embeddings service.

Tests the integration between backend and embeddings microservice.
"""

import pytest
from app.services.embeddings import embeddings_service, VehicleAttributes


class TestEmbeddingsIntegration:
    """Integration tests for embeddings service."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test embeddings service health check."""
        health = await embeddings_service.health_check()
        
        assert health["status"] == "healthy"
        assert health["service"] == "bge-m3-embeddings"
        assert health["embedding_dimension"] == 1024
        assert health["model"] == "BAAI/bge-m3"
    
    @pytest.mark.asyncio
    async def test_generate_single_embedding(self):
        """Test generating embedding for a single vehicle."""
        vehicle = VehicleAttributes(
            make="Maruti",
            model="Swift",
            year=2020,
            variant="VXi",
            fuel_type="Petrol",
            transmission="Manual",
            mileage=50000,
            location="Mumbai"
        )
        
        embedding, description = await embeddings_service.generate_embedding(vehicle)
        
        # Check embedding dimension
        assert len(embedding) == 1024
        
        # Check description contains all attributes
        assert "Maruti" in description
        assert "Swift" in description
        assert "2020" in description
        assert "VXi" in description
        assert "Petrol" in description
        assert "Manual" in description
        assert "50000" in description
        assert "Mumbai" in description
    
    @pytest.mark.asyncio
    async def test_generate_batch_embeddings(self):
        """Test generating embeddings for multiple vehicles."""
        vehicles = [
            VehicleAttributes(
                make="Maruti",
                model="Swift",
                year=2020,
                variant="VXi",
                fuel_type="Petrol",
                transmission="Manual",
                mileage=50000,
                location="Mumbai"
            ),
            VehicleAttributes(
                make="Hyundai",
                model="i20",
                year=2021,
                variant="Sportz",
                fuel_type="Diesel",
                transmission="Automatic",
                mileage=30000,
                location="Delhi"
            ),
            VehicleAttributes(
                make="Tata",
                model="Nexon",
                year=2022,
                variant="XZ+",
                fuel_type="Electric",
                transmission="Automatic",
                mileage=15000,
                location="Bangalore"
            )
        ]
        
        embeddings, descriptions = await embeddings_service.generate_batch_embeddings(vehicles)
        
        # Check we got correct number of embeddings
        assert len(embeddings) == 3
        assert len(descriptions) == 3
        
        # Check all embeddings have correct dimension
        for emb in embeddings:
            assert len(emb) == 1024
        
        # Check descriptions contain vehicle info
        assert "Maruti" in descriptions[0]
        assert "Hyundai" in descriptions[1]
        assert "Tata" in descriptions[2]
    
    @pytest.mark.asyncio
    async def test_calculate_similarity(self):
        """Test calculating similarity between embeddings."""
        vehicle1 = VehicleAttributes(
            make="Maruti",
            model="Swift",
            year=2020,
            variant="VXi",
            fuel_type="Petrol",
            transmission="Manual",
            mileage=50000,
            location="Mumbai"
        )
        
        vehicle2 = VehicleAttributes(
            make="Maruti",
            model="Swift",
            year=2021,
            variant="VXi",
            fuel_type="Petrol",
            transmission="Manual",
            mileage=30000,
            location="Mumbai"
        )
        
        # Generate embeddings
        embedding1, _ = await embeddings_service.generate_embedding(vehicle1)
        embedding2, _ = await embeddings_service.generate_embedding(vehicle2)
        
        # Calculate similarity
        similarity = await embeddings_service.calculate_similarity(
            embedding1, embedding2
        )
        
        # Similar vehicles should have high similarity
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.8  # Very similar vehicles
    
    @pytest.mark.asyncio
    async def test_deterministic_embeddings(self):
        """Test that identical vehicles produce identical embeddings."""
        vehicle = VehicleAttributes(
            make="Maruti",
            model="Swift",
            year=2020,
            variant="VXi",
            fuel_type="Petrol",
            transmission="Manual",
            mileage=50000,
            location="Mumbai"
        )
        
        # Generate embedding twice
        embedding1, desc1 = await embeddings_service.generate_embedding(vehicle)
        embedding2, desc2 = await embeddings_service.generate_embedding(vehicle)
        
        # Should be identical
        assert embedding1 == embedding2
        assert desc1 == desc2
    
    @pytest.mark.asyncio
    async def test_batch_size_validation(self):
        """Test that batch size is limited to 100 vehicles."""
        # Create 101 vehicles
        vehicles = [
            VehicleAttributes(
                make="Maruti",
                model="Swift",
                year=2020,
                variant="VXi",
                fuel_type="Petrol",
                transmission="Manual",
                mileage=50000 + i,
                location="Mumbai"
            )
            for i in range(101)
        ]
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="exceeds maximum of 100"):
            await embeddings_service.generate_batch_embeddings(vehicles)
