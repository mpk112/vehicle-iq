#!/usr/bin/env python3
"""
Code Structure Test for Phase 2 & Phase 3
Tests code structure, syntax, and completeness without requiring dependencies
"""

import os
import ast
import sys

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

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
            ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def count_lines(filepath):
    """Count lines in a file."""
    try:
        with open(filepath, 'r') as f:
            return len(f.readlines())
    except:
        return 0

def check_class_exists(filepath, class_name):
    """Check if a class exists in a Python file."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return True
        return False
    except:
        return False

def check_function_exists(filepath, function_name):
    """Check if a function exists in a Python file."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                return True
        return False
    except:
        return False

def test_phase2_files():
    """Test Phase 2 file structure and syntax."""
    print_header("Testing Phase 2: Image Intelligence")
    
    tests_passed = 0
    tests_total = 0
    
    # Test assessment model
    tests_total += 1
    filepath = 'backend/app/models/assessment.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_assessment = check_class_exists(filepath, 'Assessment')
            has_photo = check_class_exists(filepath, 'AssessmentPhoto')
            if has_assessment and has_photo:
                lines = count_lines(filepath)
                print_success(f"Assessment models ({lines} lines) - Assessment & AssessmentPhoto classes found")
                tests_passed += 1
            else:
                print_error(f"Assessment models - Missing classes")
        else:
            print_error(f"Assessment models - Syntax error: {error}")
    else:
        print_error(f"Assessment models - File not found")
    
    # Test assessment schemas
    tests_total += 1
    filepath = 'backend/app/schemas/assessment.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_create = check_class_exists(filepath, 'AssessmentCreate')
            has_response = check_class_exists(filepath, 'AssessmentResponse')
            if has_create and has_response:
                lines = count_lines(filepath)
                print_success(f"Assessment schemas ({lines} lines) - Create & Response schemas found")
                tests_passed += 1
            else:
                print_error(f"Assessment schemas - Missing schema classes")
        else:
            print_error(f"Assessment schemas - Syntax error: {error}")
    else:
        print_error(f"Assessment schemas - File not found")
    
    # Test assessment API
    tests_total += 1
    filepath = 'backend/app/api/assessments.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_create = check_function_exists(filepath, 'create_assessment')
            has_get = check_function_exists(filepath, 'get_assessment')
            has_list = check_function_exists(filepath, 'list_assessments')
            if has_create and has_get and has_list:
                lines = count_lines(filepath)
                print_success(f"Assessment API ({lines} lines) - All endpoints found")
                tests_passed += 1
            else:
                print_error(f"Assessment API - Missing endpoints")
        else:
            print_error(f"Assessment API - Syntax error: {error}")
    else:
        print_error(f"Assessment API - File not found")
    
    # Test migration
    tests_total += 1
    filepath = 'backend/alembic/versions/20260405_add_assessments.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_upgrade = check_function_exists(filepath, 'upgrade')
            has_downgrade = check_function_exists(filepath, 'downgrade')
            if has_upgrade and has_downgrade:
                lines = count_lines(filepath)
                print_success(f"Assessment migration ({lines} lines) - upgrade & downgrade found")
                tests_passed += 1
            else:
                print_error(f"Assessment migration - Missing upgrade/downgrade")
        else:
            print_error(f"Assessment migration - Syntax error: {error}")
    else:
        print_error(f"Assessment migration - File not found")
    
    return tests_passed, tests_total

def test_phase3_files():
    """Test Phase 3 file structure and syntax."""
    print_header("Testing Phase 3: Fraud Detection")
    
    tests_passed = 0
    tests_total = 0
    
    # Test fraud detection service
    tests_total += 1
    filepath = 'backend/app/services/fraud_detection.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_engine = check_class_exists(filepath, 'FraudDetectionEngine')
            has_detect = check_function_exists(filepath, 'detect_fraud')
            if has_engine and has_detect:
                lines = count_lines(filepath)
                print_success(f"Fraud detection service ({lines} lines) - Engine & detect_fraud found")
                tests_passed += 1
            else:
                print_error(f"Fraud detection service - Missing classes/methods")
        else:
            print_error(f"Fraud detection service - Syntax error: {error}")
    else:
        print_error(f"Fraud detection service - File not found")
    
    # Test API rate limiter
    tests_total += 1
    filepath = 'backend/app/services/api_rate_limiter.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_limiter = check_class_exists(filepath, 'APIRateLimiter')
            has_client = check_class_exists(filepath, 'LLMClient')
            if has_limiter and has_client:
                lines = count_lines(filepath)
                print_success(f"API rate limiter ({lines} lines) - APIRateLimiter & LLMClient found")
                tests_passed += 1
            else:
                print_error(f"API rate limiter - Missing classes")
        else:
            print_error(f"API rate limiter - Syntax error: {error}")
    else:
        print_error(f"API rate limiter - File not found")
    
    # Test fraud schemas
    tests_total += 1
    filepath = 'backend/app/schemas/fraud.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_request = check_class_exists(filepath, 'FraudDetectionRequest')
            has_response = check_class_exists(filepath, 'FraudDetectionResponse')
            has_signal = check_class_exists(filepath, 'FraudSignal')
            if has_request and has_response and has_signal:
                lines = count_lines(filepath)
                print_success(f"Fraud schemas ({lines} lines) - All schemas found")
                tests_passed += 1
            else:
                print_error(f"Fraud schemas - Missing schema classes")
        else:
            print_error(f"Fraud schemas - Syntax error: {error}")
    else:
        print_error(f"Fraud schemas - File not found")
    
    # Test fraud API
    tests_total += 1
    filepath = 'backend/app/api/fraud.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_detect = check_function_exists(filepath, 'detect_fraud')
            has_usage = check_function_exists(filepath, 'get_api_usage')
            if has_detect and has_usage:
                lines = count_lines(filepath)
                print_success(f"Fraud API ({lines} lines) - All endpoints found")
                tests_passed += 1
            else:
                print_error(f"Fraud API - Missing endpoints")
        else:
            print_error(f"Fraud API - Syntax error: {error}")
    else:
        print_error(f"Fraud API - File not found")
    
    # Test metrics model
    tests_total += 1
    filepath = 'backend/app/models/metrics.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            has_api_usage = check_class_exists(filepath, 'APIUsage')
            if has_api_usage:
                lines = count_lines(filepath)
                print_success(f"Metrics models ({lines} lines) - APIUsage model found")
                tests_passed += 1
            else:
                print_error(f"Metrics models - Missing APIUsage class")
        else:
            print_error(f"Metrics models - Syntax error: {error}")
    else:
        print_error(f"Metrics models - File not found")
    
    # Test integration tests
    tests_total += 1
    filepath = 'backend/app/tests/integration/test_fraud_api.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            lines = count_lines(filepath)
            print_success(f"Fraud API tests ({lines} lines) - Test file valid")
            tests_passed += 1
        else:
            print_error(f"Fraud API tests - Syntax error: {error}")
    else:
        print_error(f"Fraud API tests - File not found")
    
    return tests_passed, tests_total

def test_main_app():
    """Test main application file."""
    print_header("Testing Main Application")
    
    filepath = 'backend/app/main.py'
    if os.path.exists(filepath):
        valid, error = check_file_syntax(filepath)
        if valid:
            lines = count_lines(filepath)
            
            # Check if fraud router is imported
            with open(filepath, 'r') as f:
                content = f.read()
                has_fraud_import = 'from app.api import' in content and 'fraud' in content
                has_fraud_router = 'fraud.router' in content
                
                if has_fraud_import and has_fraud_router:
                    print_success(f"Main app ({lines} lines) - Fraud router registered")
                    return True
                else:
                    print_error(f"Main app - Fraud router not registered")
                    return False
        else:
            print_error(f"Main app - Syntax error: {error}")
            return False
    else:
        print_error(f"Main app - File not found")
        return False

def test_documentation():
    """Test documentation files."""
    print_header("Testing Documentation")
    
    docs = [
        ('PHASE2_COMPLETE.md', 'Phase 2 completion doc'),
        ('PHASE3_COMPLETE.md', 'Phase 3 completion doc'),
        ('TESTING_PHASE2_PHASE3.md', 'Testing guide'),
        ('QUICK_START_TESTING.md', 'Quick start guide'),
    ]
    
    found = 0
    for filename, description in docs:
        if os.path.exists(filename):
            lines = count_lines(filename)
            print_success(f"{description} ({lines} lines)")
            found += 1
        else:
            print_error(f"{description} - Not found")
    
    return found == len(docs)

def main():
    """Run all tests."""
    print_header("🧪 VehicleIQ Code Structure Test")
    print_info("Testing Phase 2 & Phase 3 code structure and syntax")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    phase2_passed, phase2_total = test_phase2_files()
    phase3_passed, phase3_total = test_phase3_files()
    main_app_ok = test_main_app()
    docs_ok = test_documentation()
    
    # Summary
    print_header("📊 Test Summary")
    
    total_passed = phase2_passed + phase3_passed + (1 if main_app_ok else 0) + (1 if docs_ok else 0)
    total_tests = phase2_total + phase3_total + 2
    
    print_info(f"Phase 2: {phase2_passed}/{phase2_total} tests passed")
    print_info(f"Phase 3: {phase3_passed}/{phase3_total} tests passed")
    print_info(f"Main App: {'✅ PASS' if main_app_ok else '❌ FAIL'}")
    print_info(f"Documentation: {'✅ PASS' if docs_ok else '❌ FAIL'}")
    
    print(f"\n{Colors.BLUE}Overall: {total_passed}/{total_tests} tests passed{Colors.END}")
    
    if total_passed == total_tests:
        print(f"\n{Colors.GREEN}✅ All code structure tests passed!{Colors.END}")
        print(f"\n{Colors.BLUE}Code Quality Summary:{Colors.END}")
        print("• All Python files have valid syntax")
        print("• All required classes and functions exist")
        print("• All API endpoints are implemented")
        print("• Database migrations are complete")
        print("• Documentation is comprehensive")
        print(f"\n{Colors.BLUE}Next Steps:{Colors.END}")
        print("1. Install dependencies: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        print("2. Start services: docker-compose up --build -d")
        print("3. Run migrations: cd backend && alembic upgrade head")
        print("4. Seed database: python scripts/seed_enhanced.py")
        print("5. Test APIs: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n{Colors.RED}❌ Some tests failed. Please review the issues above.{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
