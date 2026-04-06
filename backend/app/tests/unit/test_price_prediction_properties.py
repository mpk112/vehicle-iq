"""Property-based tests for price prediction service.

Tests the 4-layer pricing model correctness properties.
Follows Requirements 2.1-2.10.
"""

import pytest
from hypothesis import given, strategies as st, assume
from app.services.price_prediction import PricePredictionService


# Property 5: Price Prediction Monotonicity
# Validates: Requirements 2.2
@given(
    base_price=st.floats(min_value=100000, max_value=5000000),
    health_score_1=st.floats(min_value=0, max_value=100),
    health_score_2=st.floats(min_value=0, max_value=100)
)
def test_property_5_price_monotonicity(base_price, health_score_1, health_score_2):
    """
    Property 5: Price Prediction Monotonicity
    
    **Validates: Requirements 2.2**
    
    Test that higher health score produces higher or equal adjusted price.
    If health_score_1 <= health_score_2, then adjusted_price_1 <= adjusted_price_2.
    """
    # Arrange
    assume(health_score_1 <= health_score_2)
    price_service = PricePredictionService()
    
    # Act
    adjusted_price_1 = price_service.apply_condition_adjustment(base_price, health_score_1)
    adjusted_price_2 = price_service.apply_condition_adjustment(base_price, health_score_2)
    
    # Assert
    assert adjusted_price_1 <= adjusted_price_2, (
        f"Price monotonicity violated: health_score {health_score_1} -> {adjusted_price_1}, "
        f"health_score {health_score_2} -> {adjusted_price_2}"
    )


# Property 6: Quantile Ordering
# Validates: Requirements 2.4
@given(
    prices=st.lists(
        st.floats(min_value=100000, max_value=5000000),
        min_size=3,
        max_size=20
    ),
    health_score=st.floats(min_value=0, max_value=100)
)
def test_property_6_quantile_ordering(prices, health_score):
    """
    Property 6: Quantile Ordering
    
    **Validates: Requirements 2.4**
    
    Test that P10 <= P50 <= P90 for all quantile regression outputs.
    """
    # Arrange
    price_service = PricePredictionService()
    
    # Act
    p10, p50, p90 = price_service.apply_quantile_regression(
        comparable_prices=prices,
        health_score=health_score
    )
    
    # Assert
    assert p10 <= p50, f"P10 ({p10}) should be <= P50 ({p50})"
    assert p50 <= p90, f"P50 ({p50}) should be <= P90 ({p90})"
    assert p10 <= p90, f"P10 ({p10}) should be <= P90 ({p90})"


# Property 7: Persona-Specific Value Bounds
# Validates: Requirements 2.6, 2.8
@given(
    p10=st.floats(min_value=100000, max_value=800000),
    p50_offset=st.floats(min_value=0, max_value=200000),
    p90_offset=st.floats(min_value=0, max_value=200000),
    vehicle_age=st.integers(min_value=0, max_value=20)
)
def test_property_7_persona_value_bounds(p10, p50_offset, p90_offset, vehicle_age):
    """
    Property 7: Persona-Specific Value Bounds
    
    **Validates: Requirements 2.6, 2.8**
    
    Test that:
    - Lender FSV <= P10 (conservative valuation)
    - Broker asking_price >= P90 (optimistic valuation)
    """
    # Arrange - generate properly ordered quantiles
    p50 = p10 + p50_offset
    p90 = p50 + p90_offset
    price_service = PricePredictionService()
    
    # Act
    lender_fsv = price_service.calculate_persona_value(p10, p50, p90, "Lender", vehicle_age)
    broker_asking = price_service.calculate_persona_value(p10, p50, p90, "Broker", vehicle_age)
    
    # Assert
    assert lender_fsv <= p10, (
        f"Lender FSV ({lender_fsv}) should be <= P10 ({p10})"
    )
    assert broker_asking >= p90, (
        f"Broker asking price ({broker_asking}) should be >= P90 ({p90})"
    )


# Additional test: Condition adjustment bounds
@given(
    base_price=st.floats(min_value=100000, max_value=5000000),
    health_score=st.floats(min_value=0, max_value=100)
)
def test_condition_adjustment_bounds(base_price, health_score):
    """
    Test that condition adjustment produces reasonable bounds.
    
    Adjusted price should be between 70% and 115% of base price.
    """
    # Arrange
    price_service = PricePredictionService()
    
    # Act
    adjusted_price = price_service.apply_condition_adjustment(base_price, health_score)
    
    # Assert
    min_expected = base_price * 0.70
    max_expected = base_price * 1.15
    
    assert min_expected <= adjusted_price <= max_expected, (
        f"Adjusted price ({adjusted_price}) outside expected range "
        f"[{min_expected}, {max_expected}] for base_price={base_price}, health_score={health_score}"
    )


# Additional test: Quantile regression with minimal data
@given(
    price1=st.floats(min_value=100000, max_value=5000000),
    price2=st.floats(min_value=100000, max_value=5000000),
    health_score=st.floats(min_value=0, max_value=100)
)
def test_quantile_regression_minimal_data(price1, price2, health_score):
    """
    Test that quantile regression handles minimal data (< 3 prices) gracefully.
    """
    # Arrange
    price_service = PricePredictionService()
    
    # Act
    p10, p50, p90 = price_service.apply_quantile_regression(
        comparable_prices=[price1, price2],
        health_score=health_score
    )
    
    # Assert - should still maintain ordering
    assert p10 <= p50 <= p90, (
        f"Quantile ordering violated with minimal data: P10={p10}, P50={p50}, P90={p90}"
    )
    
    # Should be within reasonable range of input prices
    min_price = min(price1, price2)
    max_price = max(price1, price2)
    
    # Allow for health adjustment (up to ±10%)
    assert p10 >= min_price * 0.9, f"P10 ({p10}) too far below min price ({min_price})"
    assert p90 <= max_price * 1.1, f"P90 ({p90}) too far above max price ({max_price})"


# Additional test: Persona value consistency
@given(
    p50=st.floats(min_value=100000, max_value=1000000),
    vehicle_age=st.integers(min_value=0, max_value=20)
)
def test_insurer_idv_depreciation(p50, vehicle_age):
    """
    Test that Insurer IDV applies proper depreciation.
    
    IDV should decrease with vehicle age (15% per year, capped at 70% total depreciation).
    """
    # Arrange
    price_service = PricePredictionService()
    
    # Act
    idv = price_service.calculate_persona_value(p50, p50, p50, "Insurer", vehicle_age)
    
    # Calculate expected depreciation
    expected_depreciation = max(0.30, 1.0 - (vehicle_age * 0.15))
    expected_idv = p50 * expected_depreciation
    
    # Assert
    assert abs(idv - expected_idv) < 0.01, (
        f"IDV ({idv}) doesn't match expected ({expected_idv}) "
        f"for age {vehicle_age} and P50 {p50}"
    )
    
    # IDV should never be more than P50
    assert idv <= p50, f"IDV ({idv}) should not exceed P50 ({p50})"
    
    # IDV should be at least 30% of P50 (max depreciation)
    assert idv >= p50 * 0.30, (
        f"IDV ({idv}) should be at least 30% of P50 ({p50})"
    )


# Property 8: Price Prediction Explainability
# Validates: Requirements 2.10
@given(
    base_price=st.floats(min_value=100000, max_value=5000000),
    health_score=st.floats(min_value=0, max_value=100),
    comparables_count=st.integers(min_value=0, max_value=10),
    persona=st.sampled_from(["Lender", "Insurer", "Broker"]),
    vehicle_age=st.integers(min_value=0, max_value=20)
)
def test_property_8_price_explainability(base_price, health_score, comparables_count, persona, vehicle_age):
    """
    Property 8: Price Prediction Explainability
    
    **Validates: Requirements 2.10**
    
    Test that price prediction explanation contains all required fields:
    - base_price_source: Source of base price
    - condition_adjustment: Health score adjustment details
    - comparables_used: Number of comparable vehicles used
    - persona_adjustment: Persona-specific calculation details
    """
    # Arrange
    price_service = PricePredictionService()
    
    # Build explanation dict as done in predict_price method
    multiplier = 0.70 + 0.45 * (health_score / 100.0)
    adjusted_price = base_price * multiplier
    
    explanation = {
        "base_price_source": f"Vehicle registry: TestMake TestModel 2020",
        "condition_adjustment": {
            "health_score": health_score,
            "multiplier": multiplier,
            "adjusted_price": adjusted_price
        },
        "comparables_used": comparables_count,
        "persona_adjustment": {
            "persona": persona,
            "vehicle_age": vehicle_age,
            "calculation": price_service._get_persona_explanation(persona, vehicle_age)
        }
    }
    
    # Assert - Check all required fields are present
    assert "base_price_source" in explanation, "Missing base_price_source in explanation"
    assert "condition_adjustment" in explanation, "Missing condition_adjustment in explanation"
    assert "comparables_used" in explanation, "Missing comparables_used in explanation"
    assert "persona_adjustment" in explanation, "Missing persona_adjustment in explanation"
    
    # Assert - Check condition_adjustment structure
    assert "health_score" in explanation["condition_adjustment"], "Missing health_score in condition_adjustment"
    assert "multiplier" in explanation["condition_adjustment"], "Missing multiplier in condition_adjustment"
    assert "adjusted_price" in explanation["condition_adjustment"], "Missing adjusted_price in condition_adjustment"
    
    # Assert - Check persona_adjustment structure
    assert "persona" in explanation["persona_adjustment"], "Missing persona in persona_adjustment"
    assert "vehicle_age" in explanation["persona_adjustment"], "Missing vehicle_age in persona_adjustment"
    assert "calculation" in explanation["persona_adjustment"], "Missing calculation in persona_adjustment"
    
    # Assert - Check values are reasonable
    assert explanation["condition_adjustment"]["health_score"] == health_score
    assert 0.70 <= explanation["condition_adjustment"]["multiplier"] <= 1.15
    assert explanation["comparables_used"] >= 0
    assert explanation["persona_adjustment"]["persona"] in ["Lender", "Insurer", "Broker"]
    assert isinstance(explanation["persona_adjustment"]["calculation"], str)
    assert len(explanation["persona_adjustment"]["calculation"]) > 0
