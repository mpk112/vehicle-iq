"""Property-based tests for embedding generation.

Tests Properties 29 and 46 from the design document.
Task 16.3 (optional).
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
from app.services.embeddings import VehicleAttributes


# Strategy for generating valid vehicle attributes
@composite
def vehicle_attributes_strategy(draw):
    """Generate valid vehicle attributes for testing."""
    makes = ["Maruti", "Hyundai", "Tata", "Honda", "Toyota", "Mahindra"]
    models = ["Swift", "i20", "Nexon", "City", "Fortuner", "XUV700"]
    variants = ["LXi", "VXi", "ZXi", "Base", "Mid", "Top"]
    fuel_types = ["Petrol", "Diesel", "CNG", "Electric"]
    transmissions = ["Manual", "Automatic"]
    locations = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad"]
    
    return VehicleAttributes(
        make=draw(st.sampled_from(makes)),
        model=draw(st.sampled_from(models)),
        year=draw(st.integers(min_value=1990, max_value=2030)),
        variant=draw(st.sampled_from(variants)),
        fuel_type=draw(st.sampled_from(fuel_types)),
        transmission=draw(st.sampled_from(transmissions)),
        mileage=draw(st.integers(min_value=0, max_value=999999)),
        location=draw(st.sampled_from(locations))
    )


class TestEmbeddingProperties:
    """Property-based tests for embedding generation."""
    
    @pytest.mark.asyncio
    @given(vehicle=vehicle_attributes_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_property_29_embedding_generation_determinism(self, vehicle):
        """
        Property 29: Embedding Generation Determinism
        Validates: Requirements 16.8
        
        WHEN vehicle attributes are identical,
        THEN the system SHALL generate identical Embedding_Vector representations.
        """
        from app.services.embeddings import embeddings_service
        
        # Generate embedding twice for the same vehicle
        embedding1, desc1 = await embeddings_service.generate_embedding(vehicle)
        embedding2, desc2 = await embeddings_service.generate_embedding(vehicle)
        
        # Embeddings should be identical (deterministic)
        assert embedding1 == embedding2, (
            f"Embeddings should be deterministic for identical inputs. "
            f"Vehicle: {vehicle.dict()}"
        )
        
        # Descriptions should also be identical
        assert desc1 == desc2, (
            f"Descriptions should be deterministic for identical inputs. "
            f"Vehicle: {vehicle.dict()}"
        )
        
        # Embedding should have correct dimension (Requirement 16.4)
        assert len(embedding1) == 1024, (
            f"Embedding dimension should be 1024, got {len(embedding1)}"
        )
    
    @pytest.mark.asyncio
    @given(vehicle=vehicle_attributes_strategy())
    @settings(max_examples=50, deadline=None)
    async def test_property_46_embedding_attribute_concatenation_consistency(self, vehicle):
        """
        Property 46: Embedding Attribute Concatenation Consistency
        Validates: Requirements 16.2
        
        WHEN generating embeddings,
        THEN the system SHALL concatenate vehicle attributes in consistent order:
        make, model, year, variant, fuel_type, transmission, mileage, location.
        """
        from app.services.embeddings import embeddings_service
        
        # Generate embedding
        embedding, description = await embeddings_service.generate_embedding(vehicle)
        
        # Check that description contains all attributes in the correct order
        # The order should be: make, model, year, variant, fuel_type, transmission, mileage, location
        
        # Find positions of each attribute in the description
        make_pos = description.find(f"Make: {vehicle.make}")
        model_pos = description.find(f"Model: {vehicle.model}")
        year_pos = description.find(f"Year: {vehicle.year}")
        variant_pos = description.find(f"Variant: {vehicle.variant}")
        fuel_pos = description.find(f"Fuel Type: {vehicle.fuel_type}")
        trans_pos = description.find(f"Transmission: {vehicle.transmission}")
        mileage_pos = description.find(f"Mileage: {vehicle.mileage}")
        location_pos = description.find(f"Location: {vehicle.location}")
        
        # All attributes should be present
        assert make_pos >= 0, f"Make not found in description: {description}"
        assert model_pos >= 0, f"Model not found in description: {description}"
        assert year_pos >= 0, f"Year not found in description: {description}"
        assert variant_pos >= 0, f"Variant not found in description: {description}"
        assert fuel_pos >= 0, f"Fuel type not found in description: {description}"
        assert trans_pos >= 0, f"Transmission not found in description: {description}"
        assert mileage_pos >= 0, f"Mileage not found in description: {description}"
        assert location_pos >= 0, f"Location not found in description: {description}"
        
        # Attributes should appear in the correct order (Requirement 16.2)
        assert make_pos < model_pos, "Make should come before Model"
        assert model_pos < year_pos, "Model should come before Year"
        assert year_pos < variant_pos, "Year should come before Variant"
        assert variant_pos < fuel_pos, "Variant should come before Fuel Type"
        assert fuel_pos < trans_pos, "Fuel Type should come before Transmission"
        assert trans_pos < mileage_pos, "Transmission should come before Mileage"
        assert mileage_pos < location_pos, "Mileage should come before Location"
        
        # Embedding should have correct dimension
        assert len(embedding) == 1024, (
            f"Embedding dimension should be 1024, got {len(embedding)}"
        )
    
    @pytest.mark.asyncio
    @given(
        vehicle1=vehicle_attributes_strategy(),
        vehicle2=vehicle_attributes_strategy()
    )
    @settings(max_examples=30, deadline=None)
    async def test_embedding_similarity_bounds(self, vehicle1, vehicle2):
        """
        Test that cosine similarity is always between 0 and 1.
        Validates Requirement 16.5: use cosine similarity metric.
        """
        from app.services.embeddings import embeddings_service
        
        # Generate embeddings
        embedding1, _ = await embeddings_service.generate_embedding(vehicle1)
        embedding2, _ = await embeddings_service.generate_embedding(vehicle2)
        
        # Calculate similarity
        similarity = await embeddings_service.calculate_similarity(
            embedding1, embedding2
        )
        
        # Similarity should be between 0 and 1 (cosine similarity property)
        assert 0.0 <= similarity <= 1.0, (
            f"Cosine similarity should be between 0 and 1, got {similarity}"
        )
    
    @pytest.mark.asyncio
    @given(vehicle=vehicle_attributes_strategy())
    @settings(max_examples=30, deadline=None)
    async def test_embedding_self_similarity(self, vehicle):
        """
        Test that a vehicle's embedding has similarity ~1.0 with itself.
        Validates Requirement 16.7: round-trip property.
        """
        from app.services.embeddings import embeddings_service
        
        # Generate embedding
        embedding, _ = await embeddings_service.generate_embedding(vehicle)
        
        # Calculate self-similarity
        similarity = await embeddings_service.calculate_similarity(
            embedding, embedding
        )
        
        # Self-similarity should be very close to 1.0 (Requirement 16.7)
        assert similarity > 0.99, (
            f"Self-similarity should be > 0.99, got {similarity}. "
            f"Vehicle: {vehicle.dict()}"
        )
    
    @pytest.mark.asyncio
    async def test_batch_embedding_generation_performance(self):
        """
        Test that batch embedding generation completes within 10 seconds for 100 vehicles.
        Validates Requirement 16.6.
        """
        import time
        from app.services.embeddings import embeddings_service
        
        # Generate 100 test vehicles
        vehicles = []
        for i in range(100):
            vehicle = VehicleAttributes(
                make="Maruti",
                model="Swift",
                year=2020,
                variant="VXi",
                fuel_type="Petrol",
                transmission="Manual",
                mileage=50000 + i * 100,
                location="Mumbai"
            )
            vehicles.append(vehicle)
        
        # Measure batch processing time
        start_time = time.time()
        embeddings, descriptions = await embeddings_service.generate_batch_embeddings(vehicles)
        processing_time = time.time() - start_time
        
        # Should complete within 10 seconds (Requirement 16.6)
        assert processing_time < 10.0, (
            f"Batch processing took {processing_time:.2f}s, "
            f"should be < 10s for 100 vehicles"
        )
        
        # Should return correct number of embeddings
        assert len(embeddings) == 100, (
            f"Expected 100 embeddings, got {len(embeddings)}"
        )
        
        # All embeddings should have correct dimension
        for i, emb in enumerate(embeddings):
            assert len(emb) == 1024, (
                f"Embedding {i} has dimension {len(emb)}, expected 1024"
            )
    
    @pytest.mark.asyncio
    async def test_batch_size_limit(self):
        """
        Test that batch embedding generation enforces max 100 vehicles limit.
        """
        from app.services.embeddings import embeddings_service
        
        # Try to generate embeddings for 101 vehicles
        vehicles = []
        for i in range(101):
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
            vehicles.append(vehicle)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="exceeds maximum of 100"):
            await embeddings_service.generate_batch_embeddings(vehicles)
