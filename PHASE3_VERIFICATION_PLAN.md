# Phase 3: Fraud Detection - Verification Plan

## Overview
This document outlines the comprehensive verification plan for Phase 3 of the VehicleIQ project, which implements the Fraud Detection domain.

## What Phase 3 Includes

### 1. Fraud Detection Service (`backend/app/services/fraud_detection.py`)
- **9 Fraud Signals Implemented:**
  1. VIN Clone Detection - Checks for duplicate VINs in database
  2. Photo Reuse Detection - Uses perceptual hashing to detect reused photos
  3. Odometer Rollback Detection - Compares OCR reading with reported mileage
  4. Flood Damage Detection - Analyzes damage detections for flood indicators
  5. Document Tampering Detection - Checks OCR confidence scores
  6. Claim History Cross-Match - Mock implementation (TODO: integrate with external API)
  7. Registration Mismatch Validation - Compares VIN from OCR with reported VIN
  8. Salvage Title Check - Mock implementation (TODO: integrate with DMV/RTO)
  9. Stolen Vehicle Check - Mock implementation (TODO: integrate with police database)

- **Fraud Confidence Scoring:**
  - Weighted sum of all signal confidences (0-100)
  - Each signal has a specific weight based on importance
  - Returns explainable evidence for detected fraud

- **Fraud Gate Logic:**
  - If fraud_confidence > 60, triggers fraud gate
  - Caps health_score at 30
  - Adds assessment to manual review queue with high priority
  - Sets fraud_gate_triggered flag

### 2. Fraud Detection API (`backend/app/api/fraud.py`)
- **POST /v1/fraud/detect** - Run fraud detection on an assessment
  - Accepts assessment_id
  - Returns fraud_confidence, signals, evidence, recommended_action
  - Updates assessment with fraud results
  - Triggers manual review if needed

- **GET /v1/fraud/admin/api-usage** - Get API usage statistics (Admin only)
  - Returns usage stats for all external APIs
  - Shows remaining quota and fallback events
  - Tracks rate limits for Groq, Together.ai, PaddleOCR, YOLO, Embeddings

- **GET /v1/fraud/admin/api-usage/{service}** - Get service-specific usage stats

### 3. API Rate Limiter (`backend/app/services/api_rate_limiter.py`)
- Tracks API usage for external services
- Implements rate limiting
- Automatic fallback from Groq to Together.ai when rate limit exceeded
- Logs all API calls and fallback events

### 4. Integration Tests (`backend/app/tests/integration/test_fraud_api.py`)
- Test fraud detection success
- Test fraud detection with non-existent assessment
- Test unauthorized access
- Test API usage statistics (admin only)
- Test fraud gate triggering with duplicate VIN
- Test all 9 fraud signals

## Verification Steps

### Step 1: Infrastructure Verification
- [ ] Docker services are running (postgres, redis, backend, worker, frontend, paddleocr, yolo, embeddings)
- [ ] Backend API is accessible at http://localhost:8000
- [ ] Health check endpoint returns 200 OK
- [ ] Database migrations have been applied
- [ ] All AI microservices are healthy

### Step 2: Authentication & Authorization
- [ ] User registration works
- [ ] User login returns JWT token
- [ ] Protected endpoints require authentication
- [ ] Admin endpoints require Admin role
- [ ] Non-admin users cannot access admin endpoints

### Step 3: Assessment Creation
- [ ] Can create assessment with valid data
- [ ] Assessment is stored in database
- [ ] Assessment has unique ID
- [ ] Assessment status is set to "queued"

### Step 4: Fraud Detection Functionality
- [ ] Fraud detection endpoint accepts assessment_id
- [ ] Returns fraud_confidence between 0-100
- [ ] Returns all 9 fraud signals
- [ ] Each signal has: detected, confidence, evidence, details
- [ ] Processing time is reasonable (< 30 seconds)

### Step 5: Fraud Signal Validation
- [ ] VIN clone detection works with duplicate VINs
- [ ] Photo reuse detection is implemented (even if mock)
- [ ] Odometer rollback detection compares OCR vs reported
- [ ] Flood damage detection analyzes damage types
- [ ] Document tampering checks OCR confidence
- [ ] Claim history returns mock data
- [ ] Registration mismatch compares VINs
- [ ] Salvage title returns mock data
- [ ] Stolen vehicle returns mock data

### Step 6: Fraud Gate Logic
- [ ] Fraud gate triggers when confidence > 60
- [ ] Assessment is flagged for manual review
- [ ] Manual review reason is set
- [ ] Fraud gate flag is set in assessment record

### Step 7: API Rate Limiting
- [ ] API usage is tracked for all services
- [ ] Usage statistics are accessible to admins
- [ ] Rate limits are enforced
- [ ] Fallback mechanism works (Groq → Together.ai)

### Step 8: Integration Tests
- [ ] All integration tests pass
- [ ] Test coverage is adequate
- [ ] Tests cover happy path and error cases

## Test Execution

### Automated Test Script
Run the comprehensive test script:
```bash
cd vehicle_iq
python3 test_phase3_fraud_detection.py
```

This script will:
1. Check backend health
2. Register test users (regular and admin)
3. Login and get JWT tokens
4. Create test assessments
5. Run fraud detection
6. Verify all 9 signals
7. Test fraud gate with duplicate VIN
8. Check API usage statistics
9. Validate response structures

### Manual Testing
1. **Start Docker services:**
   ```bash
   cd vehicle_iq
   docker-compose up -d
   ```

2. **Check service health:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8001/health  # PaddleOCR
   curl http://localhost:8002/health  # YOLO
   curl http://localhost:8003/health  # Embeddings
   ```

3. **Access API documentation:**
   - Open http://localhost:8000/docs in browser
   - Test endpoints interactively

4. **Run integration tests:**
   ```bash
   cd vehicle_iq/backend
   pytest app/tests/integration/test_fraud_api.py -v
   ```

## Expected Results

### Success Criteria
✓ All Docker services start successfully
✓ Backend API responds to health checks
✓ User registration and authentication work
✓ Assessment creation succeeds
✓ Fraud detection returns valid results
✓ All 9 fraud signals are present in response
✓ Fraud confidence is between 0-100
✓ Fraud gate triggers correctly (confidence > 60)
✓ API usage tracking works
✓ Admin endpoints are protected
✓ All integration tests pass

### Performance Criteria
- Fraud detection completes in < 30 seconds
- API response time < 5 seconds for queries
- Health checks respond in < 500ms

## Known Limitations (MVP)

1. **Photo Reuse Detection:** Uses simple MD5 hash instead of perceptual hashing (pHash)
   - TODO: Implement imagehash library for better detection

2. **Claim History:** Mock implementation
   - TODO: Integrate with insurance claim database API

3. **Salvage Title Check:** Mock implementation
   - TODO: Integrate with DMV/RTO database

4. **Stolen Vehicle Check:** Mock implementation
   - TODO: Integrate with police database

5. **LLM Integration:** Not yet integrated for odometer rollback and document tampering
   - TODO: Add Groq API calls for visual analysis

## Next Steps After Phase 3

Once Phase 3 is verified:
1. Move to Phase 4: Price Prediction
2. Implement embedding generation service
3. Implement comparable vehicle retrieval (RAG)
4. Implement 4-layer pricing model
5. Implement persona-specific valuation

## Troubleshooting

### Docker Build Issues
- If services fail to build, check Docker logs: `docker-compose logs <service>`
- Common issues: Missing dependencies, network timeouts, insufficient memory
- Solution: Rebuild with `docker-compose build --no-cache <service>`

### Database Connection Issues
- Check if postgres container is running: `docker-compose ps postgres`
- Check database logs: `docker-compose logs postgres`
- Verify connection string in backend/.env

### API Errors
- Check backend logs: `docker-compose logs backend`
- Verify all environment variables are set
- Check if database migrations have been applied

### Test Failures
- Ensure all services are running
- Check if test database is clean
- Verify test user credentials
- Check API endpoint URLs

## Contact & Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review API docs: http://localhost:8000/docs
- Run health checks on all services
- Check database connectivity
