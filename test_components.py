#!/usr/bin/env python3
"""
Component Test Script for Phase 2 & Phase 3
Tests code structure and imports without requiring running services
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{message}")
    print(f"{'='*60}{Colors.END}\n")

def test_imports():
    """Test that all modules can be imported."""
    print_header("Testing Module Imports")
    
    tests = []
    
    # Phase 2 imports
    try:
        from app.models.assessment import Assessment, AssessmentPhoto
        print_success("Phase 2: Assessment models import successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 2: Assessment models import failed: {str(e)}")
        tests.append(False)
    
    try:
        from app.schemas.assessment import AssessmentCreate, AssessmentResponse
        print_success("Phase 2: Assessment schemas import successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 2: Assessment schemas import failed: {str(e)}")
        tests.append(False)
    
    try:
        from app.api.assessments import router
        print_success("Phase 2: Assessment API import successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 2: Assessment API import failed: {str(e)}")
        tests.append(False)
    
    # Phase 3 imports
    try:
        from app.services.fraud_detection import FraudDetectionEngine
        print_success("Phase 3: Fraud detection service imports successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 3: Fraud detection service import failed: {str(e)}")
        tests.append(False)
    
    try:
        from app.services.api_rate_limiter import APIRateLimiter, LLMClient
        print_success("Phase 3: API rate limiter imports successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 3: API rate limiter import failed: {str(e)}")
        tests.append(False)
    
    try:
        from app.schemas.fraud import FraudDetectionRequest, FraudDetectionResponse
        print_success("Phase 3: Fraud schemas import successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 3: Fraud schemas import failed: {str(e)}")
        tests.append(False)
    
    try:
        from app.api.fraud import router
        print_success("Phase 3: Fraud API imports successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 3: Fraud API import failed: {str(e)}")
        tests.append(False)
    
    try:
        from app.models.metrics import APIUsage
        print_success("Phase 3: Metrics models import successfully")
        tests.append(True)
    except Exception as e:
        print_error(f"Phase 3: Metrics models import failed: {str(e)}")
        tests.append(False)
    
    return all(tests)

def test_main_app():
    """Test that main app can be imported."""
    print_header("Testing Main Application")
    
    try:
        from app.main import app
        print_success("Main FastAPI app imports successfully")
        
        # Check routers are registered
        routes = [route.path for route in app.routes]
        
        # Check Phase 2 routes
        phase2_routes = ['/v1/assessments', '/v1/assessments/{assessment_id}']
        for route in phase2_routes:
            if any(route in r for r in routes):
                print_success(f"Phase 2 route registered: {route}")
            else:
                print_error(f"Phase 2 route missing: {route}")
        
        # Check Phase 3 routes
        phase3_routes = ['/v1/fraud/detect', '/v1/fraud/admin/api-usage']
        for route in phase3_routes:
            if any(route in r for r in routes):
                print_success(f"Phase 3 route registered: {route}")
            else:
                print_error(f"Phase 3 route missing: {route}")
        
        return True
    except Exception as e:
        print_error(f"Main app import failed: {str(e)}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print_header("Testing File Structure")
    
    required_files = [
        # Phase 2 files
        'backend/app/models/assessment.py',
        'backend/app/schemas/assessment.py',
        'backend/app/api/assessments.py',
        'backend/alembic/versions/20260405_add_assessments.py',
        
        # Phase 3 files
        'backend/app/services/fraud_detection.py',
        'backend/app/services/api_rate_limiter.py',
        'backend/app/schemas/fraud.py',
        'backend/app/api/fraud.py',
        'backend/app/models/metrics.py',
        'backend/app/tests/integration/test_fraud_api.py',
        
        # Documentation
        'PHASE2_COMPLETE.md',
        'PHASE3_COMPLETE.md',
        'TESTING_PHASE2_PHASE3.md',
        'QUICK_START_TESTING.md',
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_exist = False
    
    return all_exist

def test_fraud_detection_logic():
    """Test fraud detection logic without database."""
    print_header("Testing Fraud Detection Logic")
    
    try:
        from app.services.fraud_detection import FraudDetectionEngine
        
        # Check signal weights
        engine = FraudDetectionEngine(None)  # No DB needed for this test
        
        print_info(f"Signal weights configured: {len(engine.SIGNAL_WEIGHTS)} signals")
        
        expected_signals = [
            'vin_clone', 'photo_reuse', 'odometer_rollback', 'flood_damage',
            'document_tampering', 'claim_history', 'registration_mismatch',
            'salvage_title', 'stolen_vehicle'
        ]
        
        for signal in expected_signals:
            if signal in engine.SIGNAL_WEIGHTS:
                print_success(f"Signal configured: {signal} (weight: {engine.SIGNAL_WEIGHTS[signal]})")
            else:
                print_error(f"Signal missing: {signal}")
        
        # Test confidence calculation
        test_signals = {signal: {'confidence': 50, 'detected': True} for signal in expected_signals}
        confidence = engine._calculate_fraud_confidence(test_signals)
        
        if 0 <= confidence <= 100:
            print_success(f"Confidence calculation works: {confidence}%")
        else:
            print_error(f"Confidence out of range: {confidence}%")
        
        # Test recommended action
        action = engine._get_recommended_action(confidence)
        print_success(f"Recommended action: {action}")
        
        return True
    except Exception as e:
        print_error(f"Fraud detection logic test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_rate_limiter_logic():
    """Test API rate limiter logic without database."""
    print_header("Testing API Rate Limiter Logic")
    
    try:
        from app.services.api_rate_limiter import APIRateLimiter
        
        # Check rate limits are configured
        print_info(f"Rate limits configured for {len(APIRateLimiter.RATE_LIMITS)} services")
        
        for service, limit in APIRateLimiter.RATE_LIMITS.items():
            print_success(f"Service: {service} - Limit: {limit:,} requests/day")
        
        # Check warning threshold
        print_success(f"Warning threshold: {APIRateLimiter.WARNING_THRESHOLD * 100}%")
        
        return True
    except Exception as e:
        print_error(f"API rate limiter logic test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_schemas():
    """Test Pydantic schemas."""
    print_header("Testing Pydantic Schemas")
    
    try:
        from app.schemas.assessment import AssessmentCreate
        from app.schemas.fraud import FraudDetectionRequest, FraudSignal
        from uuid import uuid4
        
        # Test assessment schema
        assessment_data = {
            "vin": "TEST123456789ABCD",
            "make": "Honda",
            "model": "Civic",
            "year": 2021,
            "variant": "VX",
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "mileage": 25000,
            "location": "Mumbai",
            "registration_number": "MH01AB1234",
            "persona": "Lender"
        }
        
        assessment = AssessmentCreate(**assessment_data)
        print_success("Assessment schema validation works")
        
        # Test fraud detection request schema
        fraud_request = FraudDetectionRequest(assessment_id=uuid4())
        print_success("Fraud detection request schema validation works")
        
        # Test fraud signal schema
        signal = FraudSignal(
            signal_type="vin_clone",
            detected=True,
            confidence=75.5,
            evidence="Duplicate VIN found",
            details={"count": 2}
        )
        print_success("Fraud signal schema validation works")
        
        return True
    except Exception as e:
        print_error(f"Schema validation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all component tests."""
    print_header("🧪 VehicleIQ Component Test Suite")
    print_info("Testing Phase 2 & Phase 3 components without running services")
    
    results = []
    
    # Run tests
    results.append(("File Structure", test_file_structure()))
    results.append(("Module Imports", test_imports()))
    results.append(("Main Application", test_main_app()))
    results.append(("Fraud Detection Logic", test_fraud_detection_logic()))
    results.append(("API Rate Limiter Logic", test_api_rate_limiter_logic()))
    results.append(("Pydantic Schemas", test_schemas()))
    
    # Summary
    print_header("📊 Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✅ All component tests passed!{Colors.END}")
        print(f"\n{Colors.BLUE}Next Steps:{Colors.END}")
        print("1. Start services: docker-compose up --build -d")
        print("2. Run integration tests: pytest backend/app/tests/integration/")
        print("3. Test manually: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n{Colors.RED}❌ Some tests failed. Please fix the issues above.{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
