# Quick Start: Testing Phase 2 & Phase 3

## 🚀 Fastest Way to Test (3 Methods)

### Method 1: Interactive Swagger UI (Recommended for Beginners)

1. **Start services**:
   ```bash
   cd vehicle_iq
   docker-compose up -d
   ```

2. **Wait for services to start** (30-60 seconds)

3. **Open your browser**:
   ```
   http://localhost:8000/docs
   ```

4. **Login**:
   - Click on `POST /v1/auth/login`
   - Click "Try it out"
   - Use credentials:
     ```json
     {
       "email": "admin@vehicleiq.com",
       "password": "Admin@123456"
     }
     ```
   - Click "Execute"
   - Copy the `access_token`

5. **Authorize**:
   - Click the "Authorize" button (🔒 icon at top)
   - Enter: `Bearer <your_token>`
   - Click "Authorize"

6. **Test Phase 2 - Create Assessment**:
   - Go to `POST /v1/assessments`
   - Click "Try it out"
   - Use the example data (already filled)
   - Click "Execute"
   - Copy the `id` from response

7. **Test Phase 3 - Fraud Detection**:
   - Go to `POST /v1/fraud/detect`
   - Click "Try it out"
   - Paste the assessment ID:
     ```json
     {
       "assessment_id": "<paste_id_here>"
     }
     ```
   - Click "Execute"
   - See fraud detection results!

8. **Test Admin Features**:
   - Go to `GET /v1/fraud/admin/api-usage`
   - Click "Try it out"
   - Click "Execute"
   - See API usage statistics

**That's it!** You can now explore all endpoints interactively.

---

### Method 2: Automated Python Script (Recommended for Quick Testing)

1. **Start services**:
   ```bash
   cd vehicle_iq
   docker-compose up -d
   ```

2. **Run the test script**:
   ```bash
   python3 test_manual.py
   ```

This will automatically:
- ✅ Check all services are running
- ✅ Login and get token
- ✅ Create an assessment
- ✅ Run fraud detection
- ✅ Test duplicate VIN detection
- ✅ Check API usage statistics
- ✅ List assessments

**Output**: Colored terminal output showing all test results.

---

### Method 3: Manual curl Commands (For Advanced Users)

1. **Start services**:
   ```bash
   cd vehicle_iq
   docker-compose up -d
   ```

2. **Login**:
   ```bash
   TOKEN=$(curl -s -X POST "http://localhost:8000/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@vehicleiq.com",
       "password": "Admin@123456"
     }' | jq -r '.access_token')
   
   echo "Token: $TOKEN"
   ```

3. **Create Assessment**:
   ```bash
   ASSESSMENT_ID=$(curl -s -X POST "http://localhost:8000/v1/assessments" \
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
   
   echo "Assessment ID: $ASSESSMENT_ID"
   ```

4. **Run Fraud Detection**:
   ```bash
   curl -s -X POST "http://localhost:8000/v1/fraud/detect" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d "{
       \"assessment_id\": \"$ASSESSMENT_ID\"
     }" | jq
   ```

5. **Check API Usage**:
   ```bash
   curl -s -X GET "http://localhost:8000/v1/fraud/admin/api-usage" \
     -H "Authorization: Bearer $TOKEN" | jq
   ```

---

## 🔍 What to Look For

### Phase 2 (Image Intelligence) Tests

When you create an assessment, check:
- ✅ Assessment is created with unique ID
- ✅ All vehicle details are stored correctly
- ✅ Status is set to "queued" or "processing"
- ✅ Response time < 1 second

### Phase 3 (Fraud Detection) Tests

When you run fraud detection, check:
- ✅ `fraud_confidence` is between 0-100
- ✅ All 9 signals are present:
  - vin_clone
  - photo_reuse
  - odometer_rollback
  - flood_damage
  - document_tampering
  - claim_history
  - registration_mismatch
  - salvage_title
  - stolen_vehicle
- ✅ `fraud_gate_triggered` is true when confidence > 60
- ✅ `recommended_action` provides guidance
- ✅ `evidence` list shows detected issues
- ✅ Processing time < 2 seconds

### API Usage Statistics

When you check admin API usage, verify:
- ✅ All services are tracked (groq, together_ai, paddleocr, yolo, embeddings)
- ✅ Request counts are accurate
- ✅ Remaining quota is calculated correctly
- ✅ Fallback events are tracked

---

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check status
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs paddleocr

# Restart
docker-compose restart

# Rebuild if needed
docker-compose up --build -d
```

### Database Not Seeded

```bash
cd backend

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed_enhanced.py
```

### Authentication Fails

```bash
# Check if admin user exists
docker exec -it vehicle_iq-postgres-1 psql -U vehicleiq -d vehicleiq \
  -c "SELECT email, role FROM users WHERE email='admin@vehicleiq.com';"

# If not found, run seed script
cd backend
python scripts/seed_enhanced.py
```

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

---

## 📊 Expected Results

### Successful Test Output

```
✅ Backend API is running
✅ PaddleOCR service is running
✅ YOLOv8n service is running
✅ BGE-M3 embeddings service is running
✅ Authentication successful
✅ Assessment created
✅ Assessment retrieved
✅ Fraud detection completed
✅ VIN clone detection working
✅ API usage statistics retrieved
✅ Assessment listing working
```

### Sample Fraud Detection Response

```json
{
  "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
  "fraud_confidence": 15.5,
  "fraud_gate_triggered": false,
  "recommended_action": "No significant fraud indicators detected",
  "signals": {
    "vin_clone": {
      "signal_type": "vin_clone",
      "detected": false,
      "confidence": 0,
      "evidence": null
    },
    "photo_reuse": {
      "signal_type": "photo_reuse",
      "detected": false,
      "confidence": 0,
      "evidence": null
    }
    // ... 7 more signals
  },
  "evidence": [],
  "processing_time_ms": 1234
}
```

---

## 🎯 Test Scenarios to Try

### Scenario 1: Normal Assessment
- Create assessment with unique VIN
- Run fraud detection
- Should show low fraud confidence (< 30%)
- No fraud gate triggered

### Scenario 2: Duplicate VIN (Fraud Detection)
- Create first assessment with VIN "TEST123"
- Create second assessment with same VIN "TEST123"
- Run fraud detection on second assessment
- Should detect VIN clone
- Fraud confidence should be high (> 60%)
- Fraud gate should trigger

### Scenario 3: API Rate Limiting
- Check initial API usage
- Make several fraud detection requests
- Check updated API usage
- Verify request counts increased

### Scenario 4: Admin vs Non-Admin
- Login as admin → Can access `/v1/fraud/admin/api-usage`
- Login as lender → Cannot access admin endpoints (403 error)

---

## 📚 Additional Resources

- **Full Testing Guide**: `TESTING_PHASE2_PHASE3.md`
- **Phase 2 Documentation**: `PHASE2_COMPLETE.md`
- **Phase 3 Documentation**: `PHASE3_COMPLETE.md`
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎉 Success Criteria

You've successfully tested Phase 2 & 3 if:

- [x] All 4 services are running
- [x] You can login and get a token
- [x] You can create assessments
- [x] You can run fraud detection
- [x] Fraud detection returns 9 signals
- [x] Duplicate VIN is detected
- [x] API usage is tracked
- [x] Admin endpoints work
- [x] Non-admin users are blocked from admin endpoints

**Next Step**: Proceed to Phase 4 (Price Prediction)

---

## 💡 Pro Tips

1. **Use Swagger UI** for exploring - it's the easiest way to test
2. **Check logs** if something fails: `docker-compose logs backend`
3. **Use jq** for pretty JSON output: `curl ... | jq`
4. **Save your token** in a variable to reuse it
5. **Test with different users** to verify authorization
6. **Monitor API usage** to see rate limiting in action

---

**Need Help?** Check the logs:
```bash
docker-compose logs backend --tail=50
```
