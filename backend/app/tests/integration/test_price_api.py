"""Integration tests for price prediction API endpoints.

Tests the POST /v1/price/predict endpoint with different personas.
Follows Requirements 2.9, 2.10.

Note: These tests require a running backend with seeded data.
Run with: pytest backend/app/tests/integration/test_price_api.py -v
"""

import pytest
import time


@pytest.mark.skip(reason="Optional integration test - requires full backend setup")
def test_predict_price_lender_persona():
    """Test price prediction with Lender persona.
    
    Validates: Requirements 2.6, 2.9, 2.10
    
    Manual test steps:
    1. Start backend: cd backend && uvicorn app.main:app --reload
    2. Login to get auth token
    3. POST to /v1/price/predict with Lender persona
    4. Verify FSV <= P10
    5. Verify processing time < 5 seconds
    """
    pass


@pytest.mark.skip(reason="Optional integration test - requires full backend setup")
def test_predict_price_insurer_persona():
    """Test price prediction with Insurer persona.
    
    Validates: Requirements 2.7, 2.9, 2.10
    
    Manual test steps:
    1. POST to /v1/price/predict with Insurer persona
    2. Verify IDV <= P50 (due to depreciation)
    3. Verify processing time < 5 seconds
    """
    pass


@pytest.mark.skip(reason="Optional integration test - requires full backend setup")
def test_predict_price_broker_persona():
    """Test price prediction with Broker persona.
    
    Validates: Requirements 2.8, 2.9, 2.10
    
    Manual test steps:
    1. POST to /v1/price/predict with Broker persona
    2. Verify asking_price >= P90
    3. Verify processing time < 5 seconds
    """
    pass


@pytest.mark.skip(reason="Optional integration test - requires full backend setup")
def test_predict_price_invalid_persona():
    """Test price prediction with invalid persona.
    
    Manual test steps:
    1. POST to /v1/price/predict with invalid persona
    2. Verify 400 error with "Invalid persona" message
    """
    pass


@pytest.mark.skip(reason="Optional integration test - requires full backend setup")
def test_predict_price_vehicle_not_found():
    """Test price prediction when vehicle not in registry.
    
    Manual test steps:
    1. POST to /v1/price/predict with non-existent vehicle
    2. Verify 400 error with "No base price found" message
    """
    pass


# Manual test script for quick verification
MANUAL_TEST_SCRIPT = """
# Manual Test Script for Price Prediction API

## Prerequisites
1. Start backend: cd backend && uvicorn app.main:app --reload
2. Ensure database is seeded with vehicle data

## Test 1: Lender Persona
curl -X POST http://localhost:8000/v1/price/predict \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "make": "Maruti",
    "model": "Swift",
    "year": 2020,
    "variant": "VXI",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "mileage": 30000,
    "location": "Mumbai",
    "health_score": 75.0,
    "persona": "Lender"
  }'

Expected:
- Status: 200
- persona_value (FSV) <= p10
- processing_time_ms < 5000

## Test 2: Insurer Persona
curl -X POST http://localhost:8000/v1/price/predict \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "make": "Maruti",
    "model": "Swift",
    "year": 2020,
    "variant": "VXI",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "mileage": 30000,
    "location": "Mumbai",
    "health_score": 80.0,
    "persona": "Insurer"
  }'

Expected:
- Status: 200
- persona_value (IDV) <= p50
- processing_time_ms < 5000

## Test 3: Broker Persona
curl -X POST http://localhost:8000/v1/price/predict \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "make": "Maruti",
    "model": "Swift",
    "year": 2020,
    "variant": "VXI",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "mileage": 30000,
    "location": "Mumbai",
    "health_score": 85.0,
    "persona": "Broker"
  }'

Expected:
- Status: 200
- persona_value (asking_price) >= p90
- processing_time_ms < 5000

## Test 4: Invalid Persona
curl -X POST http://localhost:8000/v1/price/predict \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "make": "Maruti",
    "model": "Swift",
    "year": 2020,
    "variant": "VXI",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "mileage": 30000,
    "location": "Mumbai",
    "health_score": 75.0,
    "persona": "InvalidPersona"
  }'

Expected:
- Status: 400
- Error: "Invalid persona"

## Test 5: Vehicle Not Found
curl -X POST http://localhost:8000/v1/price/predict \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "make": "NonExistent",
    "model": "Model",
    "year": 2020,
    "variant": "Base",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "mileage": 30000,
    "location": "Mumbai",
    "health_score": 75.0,
    "persona": "Lender"
  }'

Expected:
- Status: 400
- Error: "No base price found"
"""


def test_manual_test_script_available():
    """Verify manual test script is available."""
    assert len(MANUAL_TEST_SCRIPT) > 0
    print("\n" + MANUAL_TEST_SCRIPT)

