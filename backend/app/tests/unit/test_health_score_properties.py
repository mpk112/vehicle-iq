"""Property-based tests for health score calculation."""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from app.services.health_score import HealthScoreEngine


# Test data generators
@st.composite
def damage_detection_strategy(draw):
    """Generate damage detection data."""
    num_damages = draw(st.integers(min_value=0, max_value=10))
    
    damage_types = [
        "dent", "scratch", "rust", "paint", "panel", "bumper",
        "engine", "transmission", "suspension", "brake",
        "seat", "dashboard", "interior"
    ]
    
    severities = ["minor", "moderate", "severe"]
    
    detections = []
    for _ in range(num_damages):
        detections.append({
            "damage_type": draw(st.sampled_from(damage_types)),
            "severity": draw(st.sampled_from(severities)),
            "confidence": draw(st.floats(min_value=0.5, max_value=1.0)),
            "bbox": [
                draw(st.integers(min_value=0, max_value=1000)),
                draw(st.integers(min_value=0, max_value=1000)),
                draw(st.integers(min_value=0, max_value=1000)),
                draw(st.integers(min_value=0, max_value=1000))
            ]
        })
    
    return {"detections": detections}


@st.composite
def service_records_strategy(draw):
    """Generate service records."""
    num_records = draw(st.integers(min_value=0, max_value=10))
    
    service_types = ["oil_change", "brake_service", "general_maintenance", "tire_rotation"]
    
    records = []
    base_date = datetime.now() - timedelta(days=365 * 3)  # 3 years ago
    
    for i in range(num_records):
        records.append({
            "date": base_date + timedelta(days=i * 90),  # Every 3 months
            "service_type": draw(st.sampled_from(service_types)),
            "mileage": draw(st.integers(min_value=10000, max_value=200000)),
            "cost": draw(st.floats(min_value=1000, max_value=50000))
        })
    
    return records


@st.composite
def accident_history_strategy(draw):
    """Generate accident history."""
    num_accidents = draw(st.integers(min_value=0, max_value=5))
    
    severities = ["minor", "moderate", "major"]
    
    accidents = []
    for _ in range(num_accidents):
        accidents.append({
            "date": datetime.now() - timedelta(days=draw(st.integers(min_value=30, max_value=1825))),
            "severity": draw(st.sampled_from(severities)),
            "description": "Test accident",
            "repair_cost": draw(st.floats(min_value=5000, max_value=500000)),
            "airbag_deployed": draw(st.booleans())
        })
    
    return accidents


class TestHealthScoreProperties:
    """Property-based tests for health score calculation."""
    
    @pytest.fixture
    def engine(self):
        """Create health score engine instance."""
        return HealthScoreEngine(db=None)  # No DB needed for these tests
    
    @given(
        persona=st.sampled_from(["Lender", "Insurer", "Broker"]),
        damage_detections=damage_detection_strategy(),
        odometer_reading=st.integers(min_value=0, max_value=999999),
        fraud_confidence=st.floats(min_value=0, max_value=100),
        year=st.integers(min_value=2000, max_value=2024)
    )
    @settings(max_examples=100, deadline=None)
    async def test_property_17_health_score_bounds(
        self,
        engine,
        persona,
        damage_detections,
        odometer_reading,
        fraud_confidence,
        year
    ):
        """
        Property 17: Health Score Bounds
        Validates: Requirements 5.1
        
        Test that health score is always between 0 and 100.
        """
        result = await engine.calculate_health_score(
            persona=persona,
            damage_detections=damage_detections,
            odometer_reading=odometer_reading,
            service_records=None,
            accident_history=None,
            fraud_confidence=fraud_confidence,
            make="Maruti",
            model="Swift",
            color="white",
            year=year
        )
        
        # Health score must be between 0 and 100
        assert 0 <= result["health_score"] <= 100, \
            f"Health score {result['health_score']} is out of bounds [0, 100]"
        
        # All component scores must be between 0 and 100
        for component, score in result["component_breakdown"].items():
            assert 0 <= score <= 100, \
                f"Component {component} score {score} is out of bounds [0, 100]"
    
    @given(
        persona=st.sampled_from(["Lender", "Insurer", "Broker"]),
        damage_detections=damage_detection_strategy(),
        odometer_reading=st.integers(min_value=0, max_value=999999),
        service_records=service_records_strategy(),
        accident_history=accident_history_strategy(),
        fraud_confidence=st.floats(min_value=0, max_value=59.9),  # Below fraud gate
        year=st.integers(min_value=2000, max_value=2024)
    )
    @settings(max_examples=100, deadline=None)
    async def test_property_18_health_score_weighted_sum_correctness(
        self,
        engine,
        persona,
        damage_detections,
        odometer_reading,
        service_records,
        accident_history,
        fraud_confidence,
        year
    ):
        """
        Property 18: Health Score Weighted Sum Correctness
        Validates: Requirements 5.2, 5.3, 5.4
        
        Test that health score equals weighted sum of components (before fraud gate).
        """
        result = await engine.calculate_health_score(
            persona=persona,
            damage_detections=damage_detections,
            odometer_reading=odometer_reading,
            service_records=service_records,
            accident_history=accident_history,
            fraud_confidence=fraud_confidence,
            make="Maruti",
            model="Swift",
            color="white",
            year=year
        )
        
        # Get persona weights
        weights = HealthScoreEngine.PERSONA_WEIGHTS[persona]
        
        # Calculate expected weighted sum
        expected_score = 0.0
        for component, weight in weights.items():
            component_score = result["component_breakdown"][component]
            expected_score += component_score * weight
        
        # Health score should match weighted sum (within rounding tolerance)
        assert abs(result["health_score"] - expected_score) < 0.1, \
            f"Health score {result['health_score']} does not match weighted sum {expected_score:.2f}"
    
    @given(
        persona=st.sampled_from(["Lender", "Insurer", "Broker"]),
        damage_detections=damage_detection_strategy(),
        odometer_reading=st.integers(min_value=0, max_value=999999),
        fraud_confidence=st.floats(min_value=60.1, max_value=100),  # Above fraud gate
        year=st.integers(min_value=2000, max_value=2024)
    )
    @settings(max_examples=50, deadline=None)
    async def test_property_2_fraud_gate_consistency(
        self,
        engine,
        persona,
        damage_detections,
        odometer_reading,
        fraud_confidence,
        year
    ):
        """
        Property 2: Fraud Gate Consistency
        Validates: Requirements 1.8, 5.5, 5.6, 11.1
        
        Test that fraud_confidence > 60 triggers gate, caps health score at 30,
        and requires manual review.
        """
        result = await engine.calculate_health_score(
            persona=persona,
            damage_detections=damage_detections,
            odometer_reading=odometer_reading,
            service_records=None,
            accident_history=None,
            fraud_confidence=fraud_confidence,
            make="Maruti",
            model="Swift",
            color="white",
            year=year
        )
        
        # Fraud gate should be triggered
        assert result["fraud_gate_triggered"] is True, \
            f"Fraud gate not triggered with confidence {fraud_confidence}"
        
        # Health score should be capped at 30
        assert result["health_score"] <= 30, \
            f"Health score {result['health_score']} not capped at 30 despite fraud gate"
        
        # Manual review should be required
        assert result["manual_review_required"] is True, \
            "Manual review not required despite fraud gate"
        
        # Review reason should mention fraud gate
        assert result["manual_review_reason"] is not None, \
            "No manual review reason provided"
        assert "fraud" in result["manual_review_reason"].lower(), \
            f"Review reason does not mention fraud: {result['manual_review_reason']}"
    
    @given(
        persona=st.sampled_from(["Lender", "Insurer", "Broker"]),
        damage_detections=damage_detection_strategy(),
        odometer_reading=st.integers(min_value=0, max_value=999999),
        fraud_confidence=st.floats(min_value=0, max_value=59.9),  # Below fraud gate
        year=st.integers(min_value=2000, max_value=2024)
    )
    @settings(max_examples=100, deadline=None)
    async def test_property_19_low_health_score_manual_review(
        self,
        engine,
        persona,
        damage_detections,
        odometer_reading,
        fraud_confidence,
        year
    ):
        """
        Property 19: Low Health Score Manual Review
        Validates: Requirements 5.7, 11.2
        
        Test that health_score < 40 triggers manual review flag.
        """
        # Add severe damages to ensure low health score
        severe_damages = {
            "detections": [
                {
                    "damage_type": "engine",
                    "severity": "severe",
                    "confidence": 0.9,
                    "bbox": [0, 0, 100, 100]
                },
                {
                    "damage_type": "transmission",
                    "severity": "severe",
                    "confidence": 0.9,
                    "bbox": [0, 0, 100, 100]
                },
                {
                    "damage_type": "rust",
                    "severity": "severe",
                    "confidence": 0.9,
                    "bbox": [0, 0, 100, 100]
                },
                {
                    "damage_type": "dent",
                    "severity": "severe",
                    "confidence": 0.9,
                    "bbox": [0, 0, 100, 100]
                }
            ]
        }
        
        result = await engine.calculate_health_score(
            persona=persona,
            damage_detections=severe_damages,
            odometer_reading=250000,  # High mileage
            service_records=None,  # No service history
            accident_history=[
                {"date": datetime.now(), "severity": "major", "description": "Major accident"}
            ],
            fraud_confidence=fraud_confidence,
            make="Unknown",
            model="Unknown",
            color="brown",
            year=2005  # Old vehicle
        )
        
        # If health score is below 40, manual review should be required
        if result["health_score"] < 40:
            assert result["manual_review_required"] is True, \
                f"Manual review not required for low health score {result['health_score']}"
            
            assert result["manual_review_reason"] is not None, \
                "No manual review reason provided for low health score"
    
    @given(
        persona=st.sampled_from(["Lender", "Insurer", "Broker"]),
        damage_detections=damage_detection_strategy(),
        odometer_reading=st.integers(min_value=0, max_value=999999),
        fraud_confidence=st.floats(min_value=0, max_value=100),
        year=st.integers(min_value=2000, max_value=2024)
    )
    @settings(max_examples=100, deadline=None)
    async def test_property_20_health_score_explainability(
        self,
        engine,
        persona,
        damage_detections,
        odometer_reading,
        fraud_confidence,
        year
    ):
        """
        Property 20: Health Score Explainability
        Validates: Requirements 5.9
        
        Test that result contains component breakdown and explanation.
        """
        result = await engine.calculate_health_score(
            persona=persona,
            damage_detections=damage_detections,
            odometer_reading=odometer_reading,
            service_records=None,
            accident_history=None,
            fraud_confidence=fraud_confidence,
            make="Maruti",
            model="Swift",
            color="white",
            year=year
        )
        
        # Component breakdown must be present
        assert "component_breakdown" in result, \
            "Component breakdown missing from result"
        
        assert isinstance(result["component_breakdown"], dict), \
            "Component breakdown is not a dictionary"
        
        # All required components must be present
        required_components = [
            "mechanical_condition",
            "exterior_condition",
            "interior_condition",
            "accident_history",
            "service_history",
            "market_appeal",
            "fraud_indicators"
        ]
        
        for component in required_components:
            assert component in result["component_breakdown"], \
                f"Component {component} missing from breakdown"
        
        # Explanation must be present and non-empty
        assert "explanation" in result, \
            "Explanation missing from result"
        
        assert isinstance(result["explanation"], list), \
            "Explanation is not a list"
        
        assert len(result["explanation"]) > 0, \
            "Explanation is empty"
        
        # Explanation should contain human-readable text
        for item in result["explanation"]:
            assert isinstance(item, str), \
                f"Explanation item is not a string: {item}"
            assert len(item) > 0, \
                "Explanation item is empty"
