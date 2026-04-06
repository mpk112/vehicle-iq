"""Integration tests for price prediction service.

Tests the complete 4-layer pricing model with database integration.
Follows Requirements 2.1-2.10.
"""

import pytest
from sqlalchemy import select
from app.services.price_prediction import (
    PricePredictionService,
    PricePredictionRequest,
    price_prediction_service
)
from app.services.embeddings import VehicleAttributes
from app.models.vehicle import VehicleRegistry, ComparableVehicle


@pytest.mark.asyncio
async def test_get_base_price_from_registry(test_db):
    """Test Layer 1: Base price lookup from vehicle registry."""
    # Arrange
    vehicle = VehicleRegistry(
        make="Maruti",
        model="Swift",
        year=2020,
        variant="VXI",
        fuel_type="Petrol",
        transmission="Manual",
        base_price=650000.0
    )
    test_db.add(vehicle)
    await test_db.commit()
    
    service = PricePredictionService()
    
    # Act
    base_price = await service.get_base_price(
        session=test_db,
        make="Maruti",
        model="Swift",
        year=2020,
        variant="VXI"
    )
    
    # Assert
    assert base_price == 650000.0


@pytest.mark.asyncio
async def test_get_base_price_without_variant(test_db):
    """Test Layer 1: Base price lookup falls back when variant not found."""
    # Arrange
    vehicle = VehicleRegistry(
        make="Hyundai",
        model="i20",
        year=2021,
        variant="Sportz",
        fuel_type="Petrol",
        transmission="Manual",
        base_price=750000.0
    )
    test_db.add(vehicle)
    await test_db.commit()
    
    service = PricePredictionService()
    
    # Act - request with different variant
    base_price = await service.get_base_price(
        session=test_db,
        make="Hyundai",
        model="i20",
        year=2021,
        variant="Magna"  # Different variant
    )
    
    # Assert - should fall back to any variant
    assert base_price == 750000.0


@pytest.mark.asyncio
async def test_get_base_price_not_found(test_db):
    """Test Layer 1: Base price lookup raises error when not found."""
    service = PricePredictionService()
    
    # Act & Assert
    with pytest.raises(ValueError, match="No base price found"):
        await service.get_base_price(
            session=test_db,
            make="NonExistent",
            model="Model",
            year=2020
        )


def test_apply_condition_adjustment():
    """Test Layer 2: Condition adjustment calculation."""
    service = PricePredictionService()
    
    # Test with health score 0 (worst condition)
    adjusted = service.apply_condition_adjustment(1000000, 0)
    assert adjusted == 700000  # 70% of base
    
    # Test with health score 100 (perfect condition)
    adjusted = service.apply_condition_adjustment(1000000, 100)
    assert adjusted == 1150000  # 115% of base
    
    # Test with health score 50 (average condition)
    adjusted = service.apply_condition_adjustment(1000000, 50)
    expected = 1000000 * (0.70 + 0.45 * 0.5)
    assert abs(adjusted - expected) < 0.01


def test_apply_quantile_regression_with_sufficient_data():
    """Test Layer 4: Quantile regression with sufficient comparable data."""
    service = PricePredictionService()
    
    # Arrange - 10 comparable prices
    prices = [500000, 520000, 540000, 560000, 580000, 600000, 620000, 640000, 660000, 680000]
    
    # Act
    p10, p50, p90 = service.apply_quantile_regression(prices, health_score=70)
    
    # Assert
    assert p10 <= p50 <= p90  # Proper ordering (use <= instead of <)
    assert p10 >= 500000 * 0.9  # Within reasonable range
    assert p90 <= 680000 * 1.1  # Within reasonable range


def test_apply_quantile_regression_with_minimal_data():
    """Test Layer 4: Quantile regression with minimal comparable data."""
    service = PricePredictionService()
    
    # Arrange - only 2 prices
    prices = [500000, 600000]
    
    # Act
    p10, p50, p90 = service.apply_quantile_regression(prices, health_score=70)
    
    # Assert
    assert p10 <= p50 <= p90  # Proper ordering maintained
    assert p10 >= 500000 * 0.9  # Within reasonable range
    assert p90 <= 600000 * 1.1  # Within reasonable range


def test_calculate_persona_value_lender():
    """Test persona-specific value calculation for Lender."""
    service = PricePredictionService()
    
    # Act
    fsv = service.calculate_persona_value(
        p10=500000,
        p50=600000,
        p90=700000,
        persona="Lender",
        vehicle_age=3
    )
    
    # Assert
    expected_fsv = 500000 * 0.95  # P10 × 0.95
    assert abs(fsv - expected_fsv) < 0.01
    assert fsv <= 500000  # FSV should be <= P10


def test_calculate_persona_value_insurer():
    """Test persona-specific value calculation for Insurer."""
    service = PricePredictionService()
    
    # Act
    idv = service.calculate_persona_value(
        p10=500000,
        p50=600000,
        p90=700000,
        persona="Insurer",
        vehicle_age=3
    )
    
    # Assert
    expected_depreciation = 1.0 - (3 * 0.15)  # 15% per year
    expected_idv = 600000 * expected_depreciation
    assert abs(idv - expected_idv) < 0.01
    assert idv <= 600000  # IDV should be <= P50


def test_calculate_persona_value_broker():
    """Test persona-specific value calculation for Broker."""
    service = PricePredictionService()
    
    # Act
    asking_price = service.calculate_persona_value(
        p10=500000,
        p50=600000,
        p90=700000,
        persona="Broker",
        vehicle_age=3
    )
    
    # Assert
    expected_asking = 700000 * 1.05  # P90 × 1.05
    assert abs(asking_price - expected_asking) < 0.01
    assert asking_price >= 700000  # Asking price should be >= P90


@pytest.mark.asyncio
async def test_complete_price_prediction_pipeline(test_db):
    """Test complete 4-layer pricing pipeline end-to-end."""
    # Arrange - Create test data
    # 1. Vehicle registry entry
    vehicle = VehicleRegistry(
        make="Maruti",
        model="Swift",
        year=2020,
        variant="VXI",
        fuel_type="Petrol",
        transmission="Manual",
        base_price=650000.0
    )
    test_db.add(vehicle)
    
    # 2. Comparable vehicles (with embeddings would be ideal, but we'll test without)
    # Note: In real scenario, these would have embeddings generated
    comparables = [
        ComparableVehicle(
            make="Maruti",
            model="Swift",
            year=2020,
            variant="VXI",
            fuel_type="Petrol",
            transmission="Manual",
            mileage=25000,
            location="Mumbai",
            listing_price=580000.0
        ),
        ComparableVehicle(
            make="Maruti",
            model="Swift",
            year=2019,
            variant="VXI",
            fuel_type="Petrol",
            transmission="Manual",
            mileage=35000,
            location="Delhi",
            listing_price=550000.0
        ),
        ComparableVehicle(
            make="Maruti",
            model="Swift",
            year=2021,
            variant="VXI",
            fuel_type="Petrol",
            transmission="Manual",
            mileage=15000,
            location="Bangalore",
            listing_price=620000.0
        )
    ]
    for comp in comparables:
        test_db.add(comp)
    
    await test_db.commit()
    
    # Create request
    request = PricePredictionRequest(
        make="Maruti",
        model="Swift",
        year=2020,
        variant="VXI",
        fuel_type="Petrol",
        transmission="Manual",
        mileage=30000,
        location="Mumbai",
        health_score=75.0,
        persona="Lender"
    )
    
    service = PricePredictionService()
    
    # Act
    response = await service.predict_price(
        session=test_db,
        request=request
    )
    
    # Assert
    assert response.base_price == 650000.0
    assert response.adjusted_price > 0
    assert response.p10 <= response.p50 <= response.p90
    assert response.persona_value <= response.p10  # Lender FSV should be <= P10
    assert len(response.explanation) > 0
    assert response.processing_time_ms > 0
    
    # Verify explanation structure
    assert "base_price_source" in response.explanation
    assert "condition_adjustment" in response.explanation
    assert "persona_adjustment" in response.explanation
    
    # Verify condition adjustment
    expected_multiplier = 0.70 + 0.45 * (75.0 / 100.0)
    expected_adjusted = 650000.0 * expected_multiplier
    assert abs(response.adjusted_price - expected_adjusted) < 0.01


@pytest.mark.asyncio
async def test_price_prediction_with_no_comparables(test_db):
    """Test price prediction when no comparable vehicles are found."""
    # Arrange - Only vehicle registry, no comparables
    vehicle = VehicleRegistry(
        make="Tesla",
        model="Model 3",
        year=2023,
        variant="Long Range",
        fuel_type="Electric",
        transmission="Automatic",
        base_price=4500000.0
    )
    test_db.add(vehicle)
    await test_db.commit()
    
    request = PricePredictionRequest(
        make="Tesla",
        model="Model 3",
        year=2023,
        variant="Long Range",
        fuel_type="Electric",
        transmission="Automatic",
        mileage=5000,
        location="Mumbai",
        health_score=95.0,
        persona="Broker"
    )
    
    service = PricePredictionService()
    
    # Act
    response = await service.predict_price(
        session=test_db,
        request=request
    )
    
    # Assert - Should fall back to adjusted price
    assert response.base_price == 4500000.0
    assert response.adjusted_price > 0
    # When no comparables, all quantiles should equal adjusted price
    assert response.p10 == response.adjusted_price
    assert response.p50 == response.adjusted_price
    assert response.p90 == response.adjusted_price
    assert len(response.comparables) == 0
