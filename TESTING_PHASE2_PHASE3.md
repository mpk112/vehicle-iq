# Testing Guide: Phase 2 & Phase 3

This guide covers testing Phase 2 (Image Intelligence) and Phase 3 (Fraud Detection) components both automatically and manually.

## Prerequisites

### 1. Start All Services

```bash
cd vehicle_iq
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- PaddleOCR service (port 8001)
- YOLOv8n service (port 8002)
- BGE-M3 embeddings service (port 8003)

### 2. Verify Services Are Running

```bash
# Check all containers
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check PaddleOCR health
curl http://localhost:8001/health

# Check YOLO health
curl http://localhost:8002/health

# Check embeddings health
curl http://localhost:8003/health
```

Expected: All services return `{"status": "healthy"}`

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Seed Database

```bash
cd backend
python scripts/seed_enhanced.py
```

This creates:
- 20 users (including admin, lender, assessor)
- 1,000 vehicle registry entries
- 2,000 comparable vehicles

## Method 1: Automated Testing (Recommended)

### Run All Tests

```bash
cd backend

# Run all tests with coverage
pytest -v --cov=app --cov-report=html

# Run only Phase 2 tests
pytest app/tests/integration/test_image_intelligence.py -v

# Run only Phase 3 tests
pytest app/tests/integration/test_fraud_api.py -v

# Run specific test
pytest app/tests/integration/test_fraud_api.py::test_detect_fraud_success -v
```

### Expected Results

**Phase 2 Tests** (if they exist):
- Photo upload and quality gate validation
- OCR extraction
- Damage detection
- Image intelligence orchestration

**Phase 3 Tests** (8 tests):
- ✅ test_detect_fraud_success
- ✅ test_detect_fraud_not_found
- ✅ test_detect_fraud_unauthorized
- ✅ test_get_api_usage_admin
- ✅ test_get_api_usage_non_admin
- ✅ test_get_service_usage_admin
- ✅ test_get_service_usage_invalid_service
- ✅ test_fraud_gate_triggering

## Method 2: Manual Testing via Swagger UI (Interactive)

### 1. Open Swagger UI

Navigate to: **http://localhost:8000/docs**

This provides an interactive API documentation interface where you can test all endpoints.

### 2. Authenticate

1. Click on **POST /v1/auth/login**
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "email": "admin@vehicleiq.com",
     "password": "Admin@123456"
   }
   ```
4. Click "Execute"
5. Copy the `access_token` from the response
6. Click the "Authorize" button at the top
7. Enter: `Bearer <your_token>`
8. Click "Authorize"

### 3. Test Phase 2: Image Intelligence

#### Test Photo Upload
1. Go to **POST /v1/photos/upload**
2. Click "Try it out"
3. Upload a test image file
4. Select photo_type: "dashboard"
5. Click "Execute"
6. Check response for quality gate results

#### Test Assessment Creation
1. Go to **POST /v1/assessments**
2. Click "Try it out"
3. Enter assessment data:
   ```json
   {
     "vin": "1HGBH41JXMN109186",
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
   ```
4. Click "Execute"
5. Copy the `assessment_id` from response

#### Test Get Assessment
1. Go to **GET /v1/assessments/{assessment_id}**
2. Click "Try it out"
3. Paste the assessment_id
4. Click "Execute"
5. Verify assessment details

### 4. Test Phase 3: Fraud Detection

#### Test Fraud Detection
1. Go to **POST /v1/fraud/detect**
2. Click "Try it out"
3. Enter:
   ```json
   {
     "assessment_id": "<paste_assessment_id_here>"
   }
   ```
4. Click "Execute"
5. Check response:
   - `fraud_confidence` (0-100)
   - `fraud_gate_triggered` (true/false)
   - `signals` (9 fraud signals)
   - `evidence` (list of detected issues)

#### Test API Usage Statistics (Admin Only)
1. Make sure you're logged in as admin
2. Go to **GET /v1/fraud/admin/api-usage**
3. Click "Try it out"
4. Click "Execute"
5. Check response:
   - Daily usage for all services
   - Remaining quota
   - Fallback events

#### Test Service-Specific Usage
1. Go to **GET /v1/fraud/admin/api-usage/{service}**
2. Click "Try it out"
3. Enter service: "groq"
4. Click "Execute"
5. Check detailed statistics

## Method 3: Manual Testing via curl (Command Line)

### 1. Get Authentication Token

```bash
# Login as admin
TOKEN=$(curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vehicleiq.com",
    "password": "Admin@123456"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Test Phase 2: Image Intelligence

#### Create Assessment
```bash
ASSESSMENT_ID=$(curl -X POST "http://localhost:8000/v1/assessments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1HGBH41JXMN109186",
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
  }' | jq -r '.id')

echo "Assessment ID: $ASSESSMENT_ID"
```

#### Get Assessment
```bash
curl -X GET "http://localhost:8000/v1/assessments/$ASSESSMENT_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### List Assessments
```bash
curl -X GET "http://localhost:8000/v1/assessments?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### Upload Photo
```bash
# Generate a test image first
cd backend
python scripts/generate_sample_images.py

# Upload photo
curl -X POST "http://localhost:8000/v1/photos/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@storage/sample_images/odometer_25000.png" \
  -F "photo_type=dashboard" | jq
```

### 3. Test Phase 3: Fraud Detection

#### Run Fraud Detection
```bash
curl -X POST "http://localhost:8000/v1/fraud/detect" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"assessment_id\": \"$ASSESSMENT_ID\"
  }" | jq
```

Expected response:
```json
{
  "assessment_id": "...",
  "fraud_confidence": 15.5,
  "fraud_gate_triggered": false,
  "recommended_action": "No significant fraud indicators detected",
  "signals": {
    "vin_clone": {
      "signal_type": "vin_clone",
      "detected": false,
      "confidence": 0,
      "evidence": null,
      "details": {}
    },
    ...
  },
  "evidence": [],
  "processing_time_ms": 1234
}
```

#### Get API Usage (Admin)
```bash
curl -X GET "http://localhost:8000/v1/fraud/admin/api-usage" \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### Get Service-Specific Usage
```bash
curl -X GET "http://localhost:8000/v1/fraud/admin/api-usage/groq" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 4. Test Fraud Gate Triggering

Create a duplicate VIN to trigger fraud detection:

```bash
# Create first assessment
ASSESSMENT_1=$(curl -X POST "http://localhost:8000/v1/assessments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | jq -r '.id')

# Create second assessment with SAME VIN
ASSESSMENT_2=$(curl -X POST "http://localhost:8000/v1/assessments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "TEST123456789ABCD",
    "make": "Honda",
    "model": "Civic",
    "year": 2021,
    "variant": "VX",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "mileage": 25000,
    "location": "Delhi",
    "registration_number": "DL01AB5678",
    "persona": "Lender"
  }' | jq -r '.id')

# Run fraud detection on second assessment
curl -X POST "http://localhost:8000/v1/fraud/detect" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"assessment_id\": \"$ASSESSMENT_2\"
  }" | jq

# Should show:
# - vin_clone.detected = true
# - vin_clone.confidence = 100
# - fraud_confidence > 60 (likely around 70-80)
# - fraud_gate_triggered = true
```

## Method 4: Test AI Microservices Directly

### Test PaddleOCR Service

```bash
# Health check
curl http://localhost:8001/health

# OCR extraction (requires image)
curl -X POST "http://localhost:8001/extract" \
  -F "file=@backend/storage/sample_images/odometer_25000.png" | jq
```

### Test YOLOv8n Service

```bash
# Health check
curl http://localhost:8002/health

# Damage detection (requires image)
curl -X POST "http://localhost:8002/detect" \
  -F "file=@backend/storage/sample_images/vehicle_front.png" | jq
```

### Test BGE-M3 Embeddings Service

```bash
# Health check
curl http://localhost:8003/health

# Generate embedding
curl -X POST "http://localhost:8003/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Honda Civic 2021 VX Petrol Manual 25000km Mumbai"
  }' | jq
```

## Method 5: Database Verification

### Check Data in Database

```bash
# Connect to database
docker exec -it vehicle_iq-postgres-1 psql -U vehicleiq -d vehicleiq

# Check users
SELECT id, email, role FROM users;

# Check assessments
SELECT id, vin, make, model, status, fraud_confidence FROM assessments;

# Check API usage
SELECT service_name, date, request_count, success_count FROM api_usage;

# Exit
\q
```

## Common Test Scenarios

### Scenario 1: Complete Assessment Flow

1. **Login** → Get token
2. **Create Assessment** → Get assessment_id
3. **Upload 13 Photos** → One for each required angle
4. **Run Fraud Detection** → Check for fraud signals
5. **Get Assessment** → Verify all data is stored
6. **Check API Usage** → Verify tracking works

### Scenario 2: Fraud Detection Flow

1. **Create Assessment with Duplicate VIN**
2. **Run Fraud Detection** → Should detect VIN clone
3. **Verify Fraud Gate Triggered** → fraud_confidence > 60
4. **Check Manual Review Flag** → requires_manual_review = true
5. **Verify Health Score Capped** → health_score <= 30 (when implemented)

### Scenario 3: API Rate Limiting

1. **Check Current Usage** → GET /v1/fraud/admin/api-usage
2. **Make Multiple Requests** → Simulate API calls
3. **Check Updated Usage** → Verify request count increased
4. **Test Fallback** → When Groq limit exceeded (mock)

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs backend
docker-compose logs paddleocr
docker-compose logs yolo
docker-compose logs embeddings

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose up --build
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker exec -it vehicle_iq-postgres-1 psql -U vehicleiq -d vehicleiq -c "SELECT 1;"
```

### Authentication Issues

```bash
# Verify user exists
docker exec -it vehicle_iq-postgres-1 psql -U vehicleiq -d vehicleiq \
  -c "SELECT email, role FROM users WHERE email='admin@vehicleiq.com';"

# If user doesn't exist, run seed script
cd backend
python scripts/seed_enhanced.py
```

### API Returns 500 Error

```bash
# Check backend logs
docker-compose logs backend --tail=50

# Check for Python errors
docker exec -it vehicle_iq-backend-1 python -c "from app.main import app; print('OK')"
```

## Test Credentials

### Admin User
- Email: `admin@vehicleiq.com`
- Password: `Admin@123456`
- Role: Admin (full access)

### Lender User
- Email: `lender@example.com`
- Password: `Lender@123456`
- Role: Lender

### Assessor User
- Email: `assessor@example.com`
- Password: `Assessor@123456`
- Role: Assessor

## Expected Test Results

### Phase 2 (Image Intelligence)
- ✅ Photo upload works
- ✅ Quality gate validates images
- ✅ OCR extracts text from images
- ✅ YOLO detects damage
- ✅ Embeddings generate 1024-dim vectors
- ✅ Assessments are created and stored

### Phase 3 (Fraud Detection)
- ✅ Fraud detection runs on assessments
- ✅ 9 fraud signals are checked
- ✅ Confidence score is 0-100
- ✅ Fraud gate triggers at >60%
- ✅ Manual review flag is set
- ✅ API usage is tracked
- ✅ Admin can view statistics
- ✅ Non-admin cannot access admin endpoints

## Performance Benchmarks

- **Fraud Detection**: < 2 seconds
- **Photo Upload**: < 1 second
- **OCR Extraction**: < 3 seconds
- **Damage Detection**: < 2 seconds per photo
- **Assessment Creation**: < 500ms
- **API Usage Query**: < 100ms

## Next Steps

After verifying Phase 2 and Phase 3:
1. Review test results
2. Fix any failing tests
3. Check API response times
4. Verify data is stored correctly
5. Proceed to Phase 4 (Price Prediction)

---

**Quick Start Command**:
```bash
# Start everything and run tests
cd vehicle_iq
docker-compose up -d
cd backend
alembic upgrade head
python scripts/seed_enhanced.py
pytest -v
```

Then open: **http://localhost:8000/docs** for interactive testing!
