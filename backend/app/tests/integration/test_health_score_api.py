"""Integration tests for health score API endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime

from app.main import app


class TestHealthScoreAPI:
    """Integration tests for health score API."""
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful health score calculation."""
        request_data = {
            "persona": "Lender",
            "damage_detections": {
                "detections": [
                    {
                        "damage_type": "scratch",
                        "severity": "minor",
                        "confidence": 0.8,
                        "bbox": [0, 0, 100, 100]
                    }
                ]
            },
            "odometer_reading": 50000,
            "service_records": [
                {
                    "date": datetime.now().isoformat(),
                    "service_type": "oil_change",
                    "mileage": 50000,
                    "cost": 3000.0
                }
            ],
            "accident_history": None,
            "fraud_confidence": 20.0,
            "make": "Maruti",
            "model": "Swift",
            "color": "white",
            "year": 2020
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "health_score" in data
        assert 0 <= data["health_score"] <= 100
        assert "component_breakdown" in data
        assert "fraud_gate_triggered" in data
        assert "manual_review_required" in data
        assert "explanation" in data
        assert isinstance(data["explanation"], list)
        assert len(data["explanation"]) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_fraud_gate(self, client: AsyncClient, auth_headers: dict):
        """Test health score calculation with fraud gate triggered."""
        request_data = {
            "persona": "Lender",
            "damage_detections": {"detections": []},
            "odometer_reading": 50000,
            "fraud_confidence": 75.0,  # Above threshold
            "make": "Maruti",
            "model": "Swift",
            "year": 2020
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["fraud_gate_triggered"] is True
        assert data["health_score"] <= 30
        assert data["manual_review_required"] is True
        assert "fraud" in data["manual_review_reason"].lower()
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_insurer_persona(self, client: AsyncClient, auth_headers: dict):
        """Test health score calculation for Insurer persona."""
        request_data = {
            "persona": "Insurer",
            "damage_detections": {"detections": []},
            "odometer_reading": 50000,
            "accident_history": [
                {
                    "date": datetime.now().isoformat(),
                    "severity": "major",
                    "description": "Front collision",
                    "repair_cost": 150000.0,
                    "airbag_deployed": True
                }
            ],
            "fraud_confidence": 10.0,
            "make": "Hyundai",
            "model": "Creta",
            "year": 2021
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        # Insurer persona weights accident history heavily (35%)
        # Major accident should significantly reduce score
        assert data["health_score"] < 80
        assert "accident_history" in data["component_breakdown"]
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_broker_persona(self, client: AsyncClient, auth_headers: dict):
        """Test health score calculation for Broker persona."""
        request_data = {
            "persona": "Broker",
            "damage_detections": {
                "detections": [
                    {
                        "damage_type": "dent",
                        "severity": "severe",
                        "confidence": 0.9,
                        "bbox": [0, 0, 200, 200]
                    }
                ]
            },
            "odometer_reading": 30000,
            "fraud_confidence": 5.0,
            "make": "Toyota",
            "model": "Fortuner",
            "color": "white",
            "year": 2022
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        # Broker persona weights exterior condition heavily (45%)
        # Severe dent should reduce score
        assert "exterior_condition" in data["component_breakdown"]
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_invalid_persona(self, client: AsyncClient, auth_headers: dict):
        """Test health score calculation with invalid persona."""
        request_data = {
            "persona": "InvalidPersona",
            "damage_detections": {"detections": []},
            "odometer_reading": 50000,
            "fraud_confidence": 0.0,
            "make": "Maruti",
            "model": "Swift",
            "year": 2020
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data,
            headers=auth_headers
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_invalid_odometer(self, client: AsyncClient, auth_headers: dict):
        """Test health score calculation with invalid odometer reading."""
        request_data = {
            "persona": "Lender",
            "damage_detections": {"detections": []},
            "odometer_reading": -1000,  # Invalid negative value
            "fraud_confidence": 0.0,
            "make": "Maruti",
            "model": "Swift",
            "year": 2020
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data,
            headers=auth_headers
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_persona_weights(self, client: AsyncClient, auth_headers: dict):
        """Test getting persona-specific weights."""
        response = await client.get(
            "/v1/health-score/persona-weights",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "Lender" in data
        assert "Insurer" in data
        assert "Broker" in data
        
        # Check Lender weights
        lender_weights = data["Lender"]
        assert "mechanical_condition" in lender_weights
        assert lender_weights["mechanical_condition"] == 0.40
        assert "exterior_condition" in lender_weights
        assert lender_weights["exterior_condition"] == 0.30
        
        # Check Insurer weights
        insurer_weights = data["Insurer"]
        assert "accident_history" in insurer_weights
        assert insurer_weights["accident_history"] == 0.35
        
        # Check Broker weights
        broker_weights = data["Broker"]
        assert "exterior_condition" in broker_weights
        assert broker_weights["exterior_condition"] == 0.45
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_unauthorized(self, client: AsyncClient):
        """Test health score calculation without authentication."""
        request_data = {
            "persona": "Lender",
            "damage_detections": {"detections": []},
            "odometer_reading": 50000,
            "fraud_confidence": 0.0,
            "make": "Maruti",
            "model": "Swift",
            "year": 2020
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data
        )
        
        # Should return 401 for unauthorized
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_calculate_health_score_component_breakdown(self, client: AsyncClient, auth_headers: dict):
        """Test that component breakdown contains all required components."""
        request_data = {
            "persona": "Lender",
            "damage_detections": {"detections": []},
            "odometer_reading": 50000,
            "fraud_confidence": 0.0,
            "make": "Maruti",
            "model": "Swift",
            "year": 2020
        }
        
        response = await client.post(
            "/v1/health-score/calculate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        breakdown = data["component_breakdown"]
        
        # Check all required components are present
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
            assert component in breakdown
            assert 0 <= breakdown[component] <= 100
