"""Integration tests for fraud detection API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.models.assessment import Assessment
from app.models.user import User


@pytest.fixture
def test_assessment(db: Session, test_user: User) -> Assessment:
    """Create a test assessment."""
    assessment = Assessment(
        id=uuid4(),
        user_id=test_user.id,
        vin="1HGBH41JXMN109186",
        make="Honda",
        model="Civic",
        year=2021,
        variant="VX",
        fuel_type="Petrol",
        transmission="Manual",
        mileage=25000,
        location="Mumbai",
        registration_number="MH01AB1234",
        persona="Lender",
        status="processing",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def test_detect_fraud_success(
    client: TestClient,
    db: Session,
    test_assessment: Assessment,
    auth_headers: dict,
):
    """Test successful fraud detection."""
    response = client.post(
        "/v1/fraud/detect",
        json={"assessment_id": str(test_assessment.id)},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "assessment_id" in data
    assert "fraud_confidence" in data
    assert "fraud_gate_triggered" in data
    assert "recommended_action" in data
    assert "signals" in data
    assert "evidence" in data
    assert "processing_time_ms" in data
    
    # Check fraud confidence bounds
    assert 0 <= data["fraud_confidence"] <= 100
    
    # Check signals structure
    assert len(data["signals"]) == 9
    for signal_name, signal_data in data["signals"].items():
        assert "signal_type" in signal_data
        assert "detected" in signal_data
        assert "confidence" in signal_data
        assert 0 <= signal_data["confidence"] <= 100


def test_detect_fraud_not_found(
    client: TestClient,
    auth_headers: dict,
):
    """Test fraud detection with non-existent assessment."""
    fake_id = str(uuid4())
    response = client.post(
        "/v1/fraud/detect",
        json={"assessment_id": fake_id},
        headers=auth_headers,
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_detect_fraud_unauthorized(
    client: TestClient,
    test_assessment: Assessment,
):
    """Test fraud detection without authentication."""
    response = client.post(
        "/v1/fraud/detect",
        json={"assessment_id": str(test_assessment.id)},
    )
    
    assert response.status_code == 401


def test_get_api_usage_admin(
    client: TestClient,
    admin_headers: dict,
):
    """Test getting API usage statistics as admin."""
    response = client.get(
        "/v1/fraud/admin/api-usage",
        headers=admin_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "date" in data
    assert "services" in data
    assert "fallback_events_today" in data
    assert "rate_limits" in data
    
    # Check rate limits for all services
    expected_services = ["groq", "together_ai", "paddleocr", "yolo", "embeddings"]
    for service in expected_services:
        assert service in data["rate_limits"]
        assert "total_requests" in data["rate_limits"][service]
        assert "remaining" in data["rate_limits"][service]


def test_get_api_usage_non_admin(
    client: TestClient,
    auth_headers: dict,
):
    """Test getting API usage statistics as non-admin user."""
    response = client.get(
        "/v1/fraud/admin/api-usage",
        headers=auth_headers,
    )
    
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()


def test_get_service_usage_admin(
    client: TestClient,
    admin_headers: dict,
):
    """Test getting service-specific usage statistics."""
    response = client.get(
        "/v1/fraud/admin/api-usage/groq",
        headers=admin_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert data["service"] == "groq"
    assert "total_requests" in data
    assert "successful_requests" in data
    assert "failed_requests" in data
    assert "fallback_triggered" in data
    assert "remaining_quota" in data
    assert "quota_percentage" in data


def test_get_service_usage_invalid_service(
    client: TestClient,
    admin_headers: dict,
):
    """Test getting usage for invalid service name."""
    response = client.get(
        "/v1/fraud/admin/api-usage/invalid_service",
        headers=admin_headers,
    )
    
    assert response.status_code == 400
    assert "invalid service" in response.json()["detail"].lower()


def test_fraud_gate_triggering(
    client: TestClient,
    db: Session,
    test_assessment: Assessment,
    auth_headers: dict,
):
    """Test that fraud gate is triggered when confidence > 60."""
    # Create assessment with duplicate VIN to trigger fraud
    duplicate_assessment = Assessment(
        id=uuid4(),
        user_id=test_assessment.user_id,
        vin=test_assessment.vin,  # Same VIN
        make="Honda",
        model="Civic",
        year=2021,
        variant="VX",
        fuel_type="Petrol",
        transmission="Manual",
        mileage=25000,
        location="Delhi",
        registration_number="DL01AB5678",
        persona="Lender",
        status="processing",
    )
    db.add(duplicate_assessment)
    db.commit()
    
    response = client.post(
        "/v1/fraud/detect",
        json={"assessment_id": str(duplicate_assessment.id)},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # VIN clone should be detected
    assert data["signals"]["vin_clone"]["detected"] is True
    
    # Check if assessment was flagged for manual review
    db.refresh(duplicate_assessment)
    if data["fraud_gate_triggered"]:
        assert duplicate_assessment.requires_manual_review is True
        assert "fraud" in duplicate_assessment.manual_review_reason.lower()
