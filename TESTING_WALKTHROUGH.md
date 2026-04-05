# VehicleIQ Phase 1 Testing Walkthrough

## Prerequisites Check

Before starting, ensure you have:
- [ ] Docker Desktop installed and running
- [ ] Docker Compose installed (usually comes with Docker Desktop)
- [ ] Terminal/Command Prompt access
- [ ] Web browser
- [ ] curl or Postman (for API testing)

Check versions:
```bash
docker --version          # Should be 20.x or higher
docker-compose --version  # Should be 2.x or higher
```

---

## Step 1: Initial Setup (5 minutes)

### 1.1 Navigate to Project Directory
```bash
cd /Users/praveenkumar/Documents/vehicle_iq
```

### 1.2 Create Environment Files
```bash
# Backend environment
cp backend/.env.example backend/.env

# Frontend environment
cp frontend/.env.example frontend/.env
```

**Note:** For local testing, the default values in .env.example should work fine.

### 1.3 Verify File Structure
```bash
# Check if key files exist
ls -la docker-compose.yml
ls -la backend/requirements.txt
ls -la frontend/package.json
```

Expected: All files should exist.

---

## Step 2: Start Services (10 minutes)

### 2.1 Start Docker Services
```bash
# Start all services in detached mode
docker-compose up -d
```

**What's happening:**
- PostgreSQL database starting
- Redis cache starting
- Backend API building and starting
- Frontend building and starting
- AI services (PaddleOCR, YOLO, Embeddings) building and starting

**Expected output:**
```
Creating network "vehicleiq_default" with the default driver
Creating volume "vehicleiq_postgres_data" with default driver
Creating volume "vehicleiq_redis_data" with default driver
Creating vehicleiq-postgres ... done
Creating vehicleiq-redis    ... done
Creating vehicleiq-backend  ... done
Creating vehicleiq-frontend ... done
Creating vehicleiq-paddleocr ... done
Creating vehicleiq-yolo     ... done
Creating vehicleiq-embeddings ... done
```

### 2.2 Check Service Status
```bash
# View running containers
docker-compose ps
```

**Expected output:** All services should show "Up" status:
```
NAME                    STATUS
vehicleiq-postgres      Up (healthy)
vehicleiq-redis         Up (healthy)
vehicleiq-backend       Up (healthy)
vehicleiq-worker        Up
vehicleiq-frontend      Up
vehicleiq-paddleocr     Up (healthy)
vehicleiq-yolo          Up (healthy)
vehicleiq-embeddings    Up (healthy)
```

**If any service is not "Up":**
```bash
# View logs for specific service
docker-compose logs <service-name>

# Example:
docker-compose logs backend
```

### 2.3 Wait for Services to Initialize
```bash
# Watch logs until services are ready
docker-compose logs -f backend
```

**Look for:** "Application startup complete" or similar message.
**Press Ctrl+C** to stop watching logs.

---

## Step 3: Database Setup (5 minutes)

### 3.1 Run Database Migrations
```bash
# Enter backend container
docker-compose exec backend bash

# Inside container, run migrations
alembic upgrade head

# Exit container
exit
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial schema
```

**Alternative (if above doesn't work):**
```bash
# Run migration directly
docker-compose exec backend alembic upgrade head
```

### 3.2 Verify Database Schema
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U vehicleiq -d vehicleiq

# Inside psql, list tables
\dt

# Expected tables:
# - users
# - vehicle_registry
# - comparable_vehicles
# - assessments
# - assessment_photos
# - manual_review_queue
# - fraud_cases
# - benchmarking_metrics
# - api_usage
# - audit_log

# Exit psql
\q
```

### 3.3 Seed Test Data
```bash
# Run seed script
docker-compose exec backend python scripts/seed.py
```

**Expected output:**
```
🌱 Seeding database...
Creating users...
Creating vehicle registry...
Creating comparable vehicles...
✅ Database seeded successfully!

Test Users:
  Admin: admin@vehicleiq.com / Admin@123456
  Lender: lender@example.com / Lender@123456
  Assessor: assessor@example.com / Assessor@123456
```

---

## Step 4: Test Backend API (10 minutes)

### 4.1 Test Health Check
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "vehicleiq-api"
}
```

### 4.2 Test API Documentation
Open browser: http://localhost:8000/docs

**Expected:** Swagger UI with API endpoints:
- POST /v1/auth/register
- POST /v1/auth/login
- GET /health

### 4.3 Test User Registration

**Using curl:**
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "role": "Assessor",
    "organization": "Test Org"
  }'
```

**Expected response:**
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test User",
  "role": "Assessor",
  "organization": "Test Org",
  "is_active": "true",
  "created_at": "2026-04-05T10:30:00Z",
  "updated_at": "2026-04-05T10:30:00Z"
}
```

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Click on "POST /v1/auth/register"
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

### 4.4 Test User Login

**Using curl:**
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vehicleiq.com",
    "password": "Admin@123456"
  }'
```

**Expected response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 2592000
}
```

**Save the access_token** - you'll need it for authenticated requests!

### 4.5 Test Authentication

**Using curl with token:**
```bash
# Replace <YOUR_TOKEN> with actual token from login
curl -X GET http://localhost:8000/v1/assessments \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

**Expected:** Should return empty list (no assessments yet) or 404 if endpoint not implemented yet.

---

## Step 5: Test AI Microservices (10 minutes)

### 5.1 Test PaddleOCR Service
```bash
# Health check
curl http://localhost:8001/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "paddleocr"
}
```

### 5.2 Test YOLO Service
```bash
# Health check
curl http://localhost:8002/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "yolo"
}
```

### 5.3 Test Embeddings Service
```bash
# Health check
curl http://localhost:8003/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "embeddings"
}
```

### 5.4 Test Embeddings Generation
```bash
curl -X POST http://localhost:8003/embed \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Maruti Swift 2020 Petrol Manual 50000km Mumbai"
  }'
```

**Expected:**
```json
{
  "success": true,
  "embedding": [0.123, -0.456, ...],
  "dimension": 1024
}
```

---

## Step 6: Test Frontend (5 minutes)

### 6.1 Access Frontend
Open browser: http://localhost:3000

**Expected:** Landing page with:
- "VehicleIQ" heading
- "AI-Powered Vehicle Assessment Platform" subtitle
- 4 feature cards:
  - Fraud Detection
  - Price Prediction
  - Image Intelligence
  - Health Scoring

### 6.2 Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for any errors

**Expected:** No errors (warnings are okay)

### 6.3 Check Network Requests
1. In DevTools, go to Network tab
2. Refresh page
3. Check if page loads successfully

**Expected:** All resources load with 200 status

---

## Step 7: Test Database Connectivity (5 minutes)

### 7.1 Verify Seeded Data
```bash
# Connect to database
docker-compose exec postgres psql -U vehicleiq -d vehicleiq

# Check users
SELECT email, role FROM users;

# Expected: 3 users (admin, lender, assessor)

# Check vehicle registry
SELECT COUNT(*) FROM vehicle_registry;

# Expected: 100 records

# Check comparable vehicles
SELECT COUNT(*) FROM comparable_vehicles;

# Expected: 50 records

# Exit
\q
```

### 7.2 Test pgvector Extension
```bash
docker-compose exec postgres psql -U vehicleiq -d vehicleiq

# Check if pgvector is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

# Expected: One row showing vector extension

\q
```

---

## Step 8: Test Error Handling (5 minutes)

### 8.1 Test Invalid Login
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@example.com",
    "password": "WrongPassword"
  }'
```

**Expected:** 401 Unauthorized with error message

### 8.2 Test Validation Error
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "password": "short"
  }'
```

**Expected:** 400 Bad Request with validation errors

### 8.3 Test Missing Authentication
```bash
curl -X GET http://localhost:8000/v1/assessments
```

**Expected:** 401 or 403 error (no token provided)

---

## Step 9: View Logs (5 minutes)

### 9.1 View All Logs
```bash
# View logs from all services
docker-compose logs --tail=50
```

### 9.2 View Specific Service Logs
```bash
# Backend logs
docker-compose logs backend --tail=50

# Frontend logs
docker-compose logs frontend --tail=50

# Database logs
docker-compose logs postgres --tail=50
```

### 9.3 Follow Logs in Real-Time
```bash
# Watch backend logs
docker-compose logs -f backend

# Press Ctrl+C to stop
```

---

## Step 10: Run Backend Tests (5 minutes)

### 10.1 Run Unit Tests
```bash
# Enter backend container
docker-compose exec backend bash

# Run tests
pytest app/tests/unit/

# Expected: All tests pass
# PASSED app/tests/unit/test_security.py::test_password_hashing
# PASSED app/tests/unit/test_security.py::test_create_and_decode_token
# PASSED app/tests/unit/test_security.py::test_decode_invalid_token

exit
```

### 10.2 Run Tests with Coverage
```bash
docker-compose exec backend pytest --cov=app --cov-report=term-missing
```

**Expected:** Coverage report showing tested files

---

## Troubleshooting Guide

### Issue: Services won't start

**Solution:**
```bash
# Check Docker is running
docker ps

# Check for port conflicts
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL

# Restart Docker Desktop
# Then try again:
docker-compose down
docker-compose up -d
```

### Issue: Database connection failed

**Solution:**
```bash
# Check if postgres is healthy
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Wait 10 seconds, then try migrations again
```

### Issue: Frontend shows blank page

**Solution:**
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose down
docker-compose build frontend
docker-compose up -d frontend
```

### Issue: AI services not responding

**Solution:**
```bash
# These services take longer to start (downloading models)
# Wait 2-3 minutes after first start

# Check logs
docker-compose logs paddleocr
docker-compose logs yolo
docker-compose logs embeddings

# If still failing, check available disk space
df -h
```

### Issue: Migration fails

**Solution:**
```bash
# Drop and recreate database
docker-compose exec postgres psql -U vehicleiq -d postgres

DROP DATABASE vehicleiq;
CREATE DATABASE vehicleiq;
\q

# Run migrations again
docker-compose exec backend alembic upgrade head
```

---

## Success Checklist

After completing all steps, verify:

- [ ] All 8 Docker containers are running
- [ ] Database has 10 tables
- [ ] 3 test users exist in database
- [ ] 100 vehicle registry records exist
- [ ] 50 comparable vehicles exist
- [ ] Backend health check returns 200
- [ ] API docs accessible at /docs
- [ ] Can register new user
- [ ] Can login and get JWT token
- [ ] All 3 AI services respond to health checks
- [ ] Frontend loads at localhost:3000
- [ ] No errors in browser console
- [ ] Backend unit tests pass

---

## Quick Commands Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild a service
docker-compose build backend
docker-compose up -d backend

# Enter a container
docker-compose exec backend bash

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec backend python scripts/seed.py

# Run tests
docker-compose exec backend pytest

# Clean everything (WARNING: deletes data)
docker-compose down -v
```

---

## Next Steps After Testing

Once all tests pass:
1. ✅ Phase 1 is validated and working
2. 🚀 Ready to proceed with Phase 2 (Image Intelligence)
3. 📝 Document any issues encountered
4. 💾 Commit working code to Git

---

## Support

If you encounter issues not covered here:
1. Check Docker Desktop is running
2. Check available disk space (need ~5GB)
3. Check available RAM (need ~4GB)
4. Review service logs for specific errors
5. Try restarting Docker Desktop
6. Try `docker-compose down -v` and start fresh

**Estimated Total Testing Time:** 60-70 minutes
