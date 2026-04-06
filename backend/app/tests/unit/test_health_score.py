"""Unit tests for health score calculation."""

import pytest
from datetime import datetime, timedelta

from app.services.health_score import HealthScoreEngine


class TestHealthScoreEngine:
    """Unit tests for HealthScoreEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create health score engine instance."""
        return HealthScoreEngine(db=None)
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_lender_persona(self, engine):
        """Test health score calculation for Lender persona."""
        damage_detections = {
            "detections": [
                {
                    "damage_type": "scratch",
                    "severity": "minor",
                    "confidence": 0.8,
                    "bbox": [0, 0, 100, 100]
                }
            ]
        }
        
        result = await engine.calculate_health_score(
            persona="Lender",
            damage_detections=damage_detections,
            odometer_reading=50000,
            service_records=None,
            accident_history=None,
            fraud_confidence=20.0,
            make="Maruti",
            model="Swift",
            color="white",
            year=2020
        )
        
        assert "health_score" in result
        assert 0 <= result["health_score"] <= 100
        assert result["fraud_gate_triggered"] is False
        assert "component_breakdown" in result
        assert "explanation" in result
    
    @pytest.mark.asyncio
    async def test_fraud_gate_triggers_at_60(self, engine):
        """Test that fraud gate triggers when confidence > 60."""
        damage_detections = {"detections": []}
        
        result = await engine.calculate_health_score(
            persona="Lender",
            damage_detections=damage_detections,
            odometer_reading=50000,
            service_records=None,
            accident_history=None,
            fraud_confidence=65.0,  # Above threshold
            make="Maruti",
            model="Swift",
            color="white",
            year=2020
        )
        
        assert result["fraud_gate_triggered"] is True
        assert result["health_score"] <= 30
        assert result["manual_review_required"] is True
        assert "fraud" in result["manual_review_reason"].lower()
    
    @pytest.mark.asyncio
    async def test_low_health_score_triggers_review(self, engine):
        """Test that low health score triggers manual review."""
        # Create severe damage to ensure low score
        damage_detections = {
            "detections": [
                {"damage_type": "engine", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
                {"damage_type": "transmission", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
                {"damage_type": "rust", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
                {"damage_type": "dent", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
            ]
        }
        
        result = await engine.calculate_health_score(
            persona="Lender",
            damage_detections=damage_detections,
            odometer_reading=250000,  # High mileage
            service_records=None,
            accident_history=[{"date": datetime.now(), "severity": "major"}],
            fraud_confidence=0.0,
            make="Unknown",
            model="Unknown",
            color="brown",
            year=2005
        )
        
        # Should have low health score
        assert result["health_score"] < 40
        assert result["manual_review_required"] is True
    
    @pytest.mark.asyncio
    async def test_mechanical_condition_calculation(self, engine):
        """Test mechanical condition component calculation."""
        # No damage, low mileage, recent service
        damage_detections = {"detections": []}
        service_records = [
            {
                "date": datetime.now() - timedelta(days=30),
                "service_type": "general_maintenance",
                "mileage": 50000
            }
        ]
        
        score = engine._calculate_mechanical_condition(
            damage_detections, 50000, service_records
        )
        
        # Should have high score (100 base + 5 bonus for recent service)
        assert score >= 95
        assert score <= 100
    
    @pytest.mark.asyncio
    async def test_mechanical_condition_with_damage(self, engine):
        """Test mechanical condition with engine damage."""
        damage_detections = {
            "detections": [
                {
                    "damage_type": "engine",
                    "severity": "severe",
                    "confidence": 0.9,
                    "bbox": [0, 0, 100, 100]
                }
            ]
        }
        
        score = engine._calculate_mechanical_condition(
            damage_detections, 50000, None
        )
        
        # Should have reduced score (100 - 30 for severe engine damage)
        assert score <= 70
    
    @pytest.mark.asyncio
    async def test_exterior_condition_calculation(self, engine):
        """Test exterior condition component calculation."""
        # Multiple exterior damages
        damage_detections = {
            "detections": [
                {"damage_type": "dent", "severity": "moderate", "confidence": 0.8, "bbox": [0, 0, 100, 100]},
                {"damage_type": "scratch", "severity": "minor", "confidence": 0.7, "bbox": [0, 0, 100, 100]},
                {"damage_type": "rust", "severity": "minor", "confidence": 0.6, "bbox": [0, 0, 100, 100]},
            ]
        }
        
        score = engine._calculate_exterior_condition(damage_detections)
        
        # Should have reduced score (100 - 10 - 3 - 3 = 84)
        assert score < 100
        assert score >= 80
    
    @pytest.mark.asyncio
    async def test_service_history_scoring(self, engine):
        """Test service history component calculation."""
        # No service records
        score_none = engine._calculate_service_history(None)
        assert score_none == 50.0
        
        # Few service records
        score_few = engine._calculate_service_history([{"date": datetime.now()}])
        assert score_few == 70.0
        
        # Many service records
        score_many = engine._calculate_service_history([
            {"date": datetime.now()} for _ in range(5)
        ])
        assert score_many == 100.0
    
    @pytest.mark.asyncio
    async def test_accident_history_scoring(self, engine):
        """Test accident history component calculation."""
        # No accidents
        score_none = engine._calculate_accident_history(None)
        assert score_none == 100.0
        
        # Minor accident
        score_minor = engine._calculate_accident_history([
            {"date": datetime.now(), "severity": "minor"}
        ])
        assert score_minor == 90.0
        
        # Major accident
        score_major = engine._calculate_accident_history([
            {"date": datetime.now(), "severity": "major"}
        ])
        assert score_major == 50.0
    
    @pytest.mark.asyncio
    async def test_market_appeal_popular_vehicle(self, engine):
        """Test market appeal for popular vehicle."""
        score = engine._calculate_market_appeal(
            make="Maruti",
            model="Swift",
            color="white",
            year=2022
        )
        
        # Popular make + popular model + desirable color + new = high score
        assert score >= 95
    
    @pytest.mark.asyncio
    async def test_market_appeal_unpopular_vehicle(self, engine):
        """Test market appeal for unpopular vehicle."""
        score = engine._calculate_market_appeal(
            make="Unknown",
            model="Unknown",
            color="brown",
            year=2005
        )
        
        # Unpopular make/model + undesirable color + old = low score
        assert score < 70
    
    @pytest.mark.asyncio
    async def test_persona_specific_weights(self, engine):
        """Test that different personas produce different scores."""
        damage_detections = {
            "detections": [
                {"damage_type": "dent", "severity": "minor", "confidence": 0.8, "bbox": [0, 0, 100, 100]}
            ]
        }
        
        accident_history = [{"date": datetime.now(), "severity": "major"}]
        
        # Calculate for each persona
        result_lender = await engine.calculate_health_score(
            persona="Lender",
            damage_detections=damage_detections,
            odometer_reading=50000,
            accident_history=accident_history,
            fraud_confidence=0.0,
            make="Maruti",
            model="Swift",
            year=2020
        )
        
        result_insurer = await engine.calculate_health_score(
            persona="Insurer",
            damage_detections=damage_detections,
            odometer_reading=50000,
            accident_history=accident_history,
            fraud_confidence=0.0,
            make="Maruti",
            model="Swift",
            year=2020
        )
        
        result_broker = await engine.calculate_health_score(
            persona="Broker",
            damage_detections=damage_detections,
            odometer_reading=50000,
            accident_history=accident_history,
            fraud_confidence=0.0,
            make="Maruti",
            model="Swift",
            year=2020
        )
        
        # Insurer should have lowest score (accident history weighted 35%)
        assert result_insurer["health_score"] < result_lender["health_score"]
        assert result_insurer["health_score"] < result_broker["health_score"]
    
    @pytest.mark.asyncio
    async def test_explanation_generation(self, engine):
        """Test that explanation is generated correctly."""
        damage_detections = {"detections": []}
        
        result = await engine.calculate_health_score(
            persona="Lender",
            damage_detections=damage_detections,
            odometer_reading=50000,
            fraud_confidence=0.0,
            make="Maruti",
            model="Swift",
            year=2020
        )
        
        explanation = result["explanation"]
        
        # Should have multiple explanation items
        assert len(explanation) > 0
        
        # First item should describe overall condition
        assert "condition" in explanation[0].lower()
        assert "score" in explanation[0].lower()
        
        # Should mention top components
        assert any("mechanical" in item.lower() for item in explanation)
