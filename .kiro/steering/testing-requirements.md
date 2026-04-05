---
inclusion: fileMatch
fileMatchPattern: '**/*.test.*,**/test_*.py'
---

# VehicleIQ Testing Requirements

## Overview

VehicleIQ requires comprehensive testing across three dimensions:
1. **Property-Based Tests**: 51 universal correctness properties
2. **Unit Tests**: Individual functions and components
3. **Integration Tests**: End-to-end workflows and API contracts

Minimum 80% code coverage required across all test types.

## Property-Based Testing

### Framework
- **Python**: Hypothesis with pytest
- **TypeScript**: fast-check with Jest

### Test Structure
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=100))
def test_property_X_descriptive_name(input_value):
    """Property X: Brief Description
    Validates: Requirements X.Y, X.Z
    """
    result = function_under_test(input_value)
    assert expected_condition(result)
```

### Execution Requirements
- Minimum 100 iterations per property test
- Use deterministic seeds for reproducibility: `@settings(derandomize=True)`
- Tag with requirement IDs for traceability
- Document which correctness property is being tested

## 51 Correctness Properties

### Fraud Detection (Properties 1-4)

**Property 1: Fraud Confidence Score Bounds**
- Validates: Requirements 1.7
- Test: `0 <= fraud_confidence <= 100`

**Property 2: Fraud Gate Consistency**
- Validates: Requirements 1.8, 5.5, 5.6, 11.1
- Test: `fraud_confidence > 60` triggers gate, caps health_score at 30, adds to manual review

**Property 3: Fraud Detection Output Structure**
- Validates: Requirements 1.9
- Test: Output contains explainable evidence for each signal

**Property 4: Photo Hash Round-Trip**
- Validates: Requirements 1.3
- Test: Computing perceptual hash twice produces identical values

### Price Prediction (Properties 5-8)

**Property 5: Price Prediction Monotonicity**
- Validates: Requirements 2.2
- Test: Higher health_score produces higher or equal adjusted price

**Property 6: Quantile Ordering**
- Validates: Requirements 2.4
- Test: `P10 <= P50 <= P90`

**Property 7: Persona-Specific Value Bounds**
- Validates: Requirements 2.6, 2.8
- Test: Lender FSV <= P10 and Broker asking_price >= P90

**Property 8: Price Prediction Explainability**
- Validates: Requirements 2.10
- Test: Explanation contains base_price_source, condition_adjustment, persona_adjustment

### Benchmarking (Properties 9-12)

**Property 9: Comparable Retrieval Count and Ordering**
- Validates: Requirements 2.3, 9.3
- Test: Results ordered by similarity, count <= 10, scores in [0,1]

**Property 10: MAPE Calculation Correctness**
- Validates: Requirements 3.3
- Test: MAPE equals mean(|predicted - actual| / actual) × 100

**Property 11: Market Data Validation**
- Validates: Requirements 3.6, 23.3
- Test: Records with missing required fields are rejected

**Property 12: Embedding Generation for New Records**
- Validates: Requirements 3.10, 16.4
- Test: New comparable records have 1024-dimensional embeddings

### Image Intelligence (Properties 13-16)

**Property 13: Quality Gate Validation Structure**
- Validates: Requirements 4.3
- Test: Quality gate returns all required checks (blur, lighting, framing, resolution)

**Property 14: Quality Gate Rejection with Feedback**
- Validates: Requirements 4.4
- Test: Failed quality gate provides specific feedback

**Property 15: Photo Collection Completeness**
- Validates: Requirements 4.9
- Test: Assessment marked complete only when all 13 angles pass

**Property 16: Damage Detection Output Structure**
- Validates: Requirements 4.10, 17.3
- Test: Each damage detection contains class_name, confidence, bbox, severity

### Health Scoring (Properties 17-20)

**Property 17: Health Score Bounds**
- Validates: Requirements 5.1
- Test: `0 <= health_score <= 100`

**Property 18: Health Score Weighted Sum Correctness**
- Validates: Requirements 5.2, 5.3, 5.4
- Test: Health score equals weighted sum of components (before fraud gate)

**Property 19: Low Health Score Manual Review**
- Validates: Requirements 5.7, 11.2
- Test: `health_score < 40` triggers manual review flag

**Property 20: Health Score Explainability**
- Validates: Requirements 5.9
- Test: Result contains component breakdown

### Authorization (Properties 21-22)

**Property 21: User Role Uniqueness**
- Validates: Requirements 6.2
- Test: Users have exactly one role

**Property 22: Role-Based Access Control**
- Validates: Requirements 6.8, 6.9
- Test: Unauthorized access is denied based on role

### Assessment Pipeline (Properties 23-28)

**Property 23: Pipeline Stage Ordering**
- Validates: Requirements 7.4
- Test: Stages executed in defined sequence

**Property 24: Pipeline Failure Handling**
- Validates: Requirements 7.5
- Test: Stage failure halts processing and returns error

**Property 25: Assessment Record Creation**
- Validates: Requirements 7.6, 8.1
- Test: Completed assessments create records with all required fields

**Property 26: Assessment Record Immutability**
- Validates: Requirements 8.2, 8.6
- Test: Core data cannot be modified after creation

**Property 27: Assessment ID Uniqueness**
- Validates: Requirements 8.3
- Test: All generated assessment IDs are unique

**Property 28: Fraud Indicator Linkage**
- Validates: Requirements 8.5
- Test: `fraud_confidence > 0` includes fraud indicators in record

### Embeddings & RAG (Properties 29-33)

**Property 29: Embedding Generation Determinism**
- Validates: Requirements 16.8
- Test: Identical attributes produce identical embeddings

**Property 30: Embedding Round-Trip**
- Validates: Requirements 16.7
- Test: Storing and retrieving embedding produces equivalent vector

**Property 31: Comparable Constraint Satisfaction**
- Validates: Requirements 9.4
- Test: All comparables satisfy constraints (make/model, year ±2, mileage ±20k)

**Property 32: Comparable Constraint Relaxation**
- Validates: Requirements 9.6
- Test: Constraints relaxed when results < 5

**Property 33: Comparable Explainability**
- Validates: Requirements 9.5, 9.8
- Test: Each comparable includes similarity_score, listing_price, listing_date, key_differences

### Reporting (Properties 34-36)

**Property 34: Persona-Specific Report Structure**
- Validates: Requirements 10.1, 10.2, 10.3
- Test: Each persona report contains required fields

**Property 35: Report Export Format Support**
- Validates: Requirements 10.6
- Test: Reports can be exported to both PDF and JSON

**Property 36: Fraud Highlighting in Reports**
- Validates: Requirements 10.8
- Test: Fraud indicators highlighted when present

### Manual Review (Properties 37-40)

**Property 37: Manual Review Queue Sorting**
- Validates: Requirements 11.3
- Test: Queue sorted by priority then submission time

**Property 38: Manual Review Approval State Transition**
- Validates: Requirements 11.5
- Test: Approval marks as reviewed and removes from queue

**Property 39: Manual Review Override Recording**
- Validates: Requirements 11.6
- Test: Override records reason and adjusted values

**Property 40: Queue Notification Threshold**
- Validates: Requirements 11.7
- Test: Queue > 20 triggers admin notification

### API & Fallback (Properties 41-43)

**Property 41: API Request Tracking**
- Validates: Requirements 14.1
- Test: All API calls increment usage tracking

**Property 42: API Fallback Triggering**
- Validates: Requirements 14.2, 14.5
- Test: Rate limit triggers fallback to secondary API

**Property 43: API Fallback Transparency**
- Validates: Requirements 14.6
- Test: Fallback output format matches primary API

### OCR (Properties 44-45)

**Property 44: OCR Validation Bounds Checking**
- Validates: Requirements 15.6, 15.7
- Test: Out-of-range odometer and invalid VINs are flagged

**Property 45: OCR Round-Trip**
- Validates: Requirements 15.9
- Test: Pretty-printing then parsing produces equivalent data

### Embeddings (Property 46)

**Property 46: Embedding Attribute Concatenation Consistency**
- Validates: Requirements 16.2
- Test: Concatenation order is consistent across calls

### Security (Property 47)

**Property 47: Row-Level Security**
- Validates: Requirements 20.4
- Test: Users cannot access assessments outside their organization

### Upload & Retry (Property 48)

**Property 48: Upload Retry Logic**
- Validates: Requirements 21.1
- Test: Failed uploads retry up to 3 times with exponential backoff

### Batch Processing (Property 49)

**Property 49: Batch Processing Completeness**
- Validates: Requirements 22.8
- Test: N valid records produce exactly N results (success or failure)

### Market Data (Property 50)

**Property 50: Market Data Deduplication**
- Validates: Requirements 23.4
- Test: Duplicate VIN or listing_url is rejected

### Notifications (Property 51)

**Property 51: Notification Rate Limiting**
- Validates: Requirements 25.7
- Test: Notifications per user per hour <= 10

## Unit Testing

### Coverage Requirements
- Minimum 80% line coverage
- Minimum 70% branch coverage
- All public functions must have tests
- All error paths must be tested

### Test Organization
```
backend/app/tests/
├── unit/
│   ├── test_fraud_detection.py
│   ├── test_price_prediction.py
│   └── test_health_scoring.py
├── integration/
│   ├── test_api_assessments.py
│   └── test_api_fraud.py
└── property/
    ├── test_properties_fraud.py
    └── test_properties_price.py
```

### Naming Conventions
- Test files: `test_*.py` or `*.test.ts`
- Test functions: `test_<function_name>_<scenario>`
- Example: `test_detect_fraud_returns_high_confidence_for_vin_clone`

## Integration Testing

### API Endpoint Tests
Test all endpoints with:
- Valid inputs (happy path)
- Invalid inputs (validation errors)
- Authentication errors (401/403)
- Rate limiting (429)
- Server errors (500)

### Workflow Tests
- Complete assessment submission workflow
- Fraud detection with various scenarios
- Manual review approval workflow
- Batch processing workflow
- Report generation and export

### Test Data
- Use seeded data from database
- Create test fixtures for common scenarios
- Clean up test data after each test
- Use transactions for database tests

## Test Execution

### Local Development
```bash
# Python tests
pytest --cov=app --cov-report=html

# TypeScript tests
npm test -- --coverage
```

### CI/CD Pipeline
- Run all tests on every commit
- Block merge if tests fail
- Generate coverage reports
- Fail if coverage < 80%

### Performance Tests
- Assessment completion < 90 seconds
- API response times < 5 seconds
- Batch processing >= 20 per minute
- Concurrent processing: 10 assessments

## Test Documentation

### Docstrings Required
```python
def test_fraud_confidence_bounds():
    """Test that fraud confidence is always between 0 and 100.
    
    Property 1: Fraud Confidence Score Bounds
    Validates: Requirements 1.7
    
    Given: Any valid assessment input
    When: Fraud detection is performed
    Then: Confidence score is in range [0, 100]
    """
```

### Traceability
- Tag tests with requirement IDs
- Link property tests to design document
- Document test assumptions
- Explain complex test setups
