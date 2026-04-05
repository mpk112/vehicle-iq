# VehicleIQ Phase 1 - Complete Testing Guide

## 📚 Testing Documentation Overview

We've created multiple testing documents for different needs:

1. **QUICK_TEST.md** ⚡ - Start here! (15-20 min)
   - Copy-paste commands
   - Fastest way to validate setup
   - Perfect for first-time testing

2. **TEST_CHECKLIST.md** ✅ - Systematic validation (30 min)
   - Level-by-level testing
   - Clear pass/fail criteria
   - Results template included

3. **TESTING_WALKTHROUGH.md** 📖 - Comprehensive guide (60-70 min)
   - Detailed explanations
   - Troubleshooting for every step
   - Complete reference guide

4. **test-setup.sh** 🤖 - Automated testing (10 min)
   - Automated script
   - Runs all basic tests
   - Quick validation

---

## 🎯 Recommended Testing Path

### For First-Time Setup:
```
1. Read QUICK_TEST.md
2. Run the commands
3. Verify with TEST_CHECKLIST.md Level 1-3
4. If issues: Check TESTING_WALKTHROUGH.md
```

### For Thorough Validation:
```
1. Follow TESTING_WALKTHROUGH.md completely
2. Mark off TEST_CHECKLIST.md as you go
3. Document any issues
```

### For Quick Verification:
```
1. Run test-setup.sh (if on Mac/Linux)
2. Or follow QUICK_TEST.md
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     VehicleIQ System                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  (Next.js)   │     │  (FastAPI)   │     │  + pgvector  │
│  Port: 3000  │     │  Port: 8000  │     │  Port: 5432  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            │
                     ┌──────┴──────┐
                     │             │
                     ▼             ▼
              ┌──────────┐   ┌──────────┐
              │  Redis   │   │  Worker  │
              │ Port:6379│   │ (Celery) │
              └──────────┘   └──────────┘

┌─────────────────────────────────────────────────────────────┐
│                   AI Microservices                          │
├──────────────┬──────────────┬──────────────────────────────┤
│  PaddleOCR   │     YOLO     │      Embeddings             │
│  Port: 8001  │  Port: 8002  │      Port: 8003             │
│  (OCR)       │  (Damage)    │      (bge-m3)               │
└──────────────┴──────────────┴──────────────────────────────┘
```

---

## 🔍 What Each Service Does

### Frontend (Port 3000)
- **Purpose:** User interface
- **Tech:** Next.js 14, React, TypeScript
- **Test:** Open http://localhost:3000
- **Expected:** Landing page with 4 feature cards

### Backend (Port 8000)
- **Purpose:** Main API server
- **Tech:** FastAPI, Python 3.11
- **Test:** `curl http://localhost:8000/health`
- **Expected:** `{"status":"healthy"}`

### PostgreSQL (Port 5432)
- **Purpose:** Main database
- **Tech:** PostgreSQL 15 + pgvector
- **Test:** `docker-compose exec postgres psql -U vehicleiq -d vehicleiq`
- **Expected:** Can connect and see 10 tables

### Redis (Port 6379)
- **Purpose:** Cache and message broker
- **Tech:** Redis 7
- **Test:** `docker-compose exec redis redis-cli ping`
- **Expected:** `PONG`

### Worker
- **Purpose:** Async task processing
- **Tech:** Celery
- **Test:** `docker-compose logs worker`
- **Expected:** No errors, "ready" message

### PaddleOCR (Port 8001)
- **Purpose:** Text extraction from images
- **Tech:** PaddleOCR v4
- **Test:** `curl http://localhost:8001/health`
- **Expected:** `{"status":"healthy","service":"paddleocr"}`

### YOLO (Port 8002)
- **Purpose:** Damage detection
- **Tech:** YOLOv8n
- **Test:** `curl http://localhost:8002/health`
- **Expected:** `{"status":"healthy","service":"yolo"}`

### Embeddings (Port 8003)
- **Purpose:** Generate vector embeddings
- **Tech:** bge-m3 (1024-dimensional)
- **Test:** `curl http://localhost:8003/health`
- **Expected:** `{"status":"healthy","service":"embeddings"}`

---

## 📊 Test Data Overview

After seeding, you'll have:

### Users (3)
```
admin@vehicleiq.com    / Admin@123456    (Admin role)
lender@example.com     / Lender@123456   (Lender role)
assessor@example.com   / Assessor@123456 (Assessor role)
```

### Vehicle Registry (100 records)
- Makes: Maruti, Hyundai, Tata, Honda, Toyota
- Models: Various popular models
- Years: 2018-2024
- Includes: base_price, fuel_type, transmission

### Comparable Vehicles (50 records)
- Similar structure to vehicle registry
- Includes: listing_price, location, mileage
- Ready for RAG-based price prediction

---

## 🎬 Step-by-Step Visual Guide

### Step 1: Start Services
```bash
$ docker-compose up -d

Creating network "vehicleiq_default"...
Creating vehicleiq-postgres...  ✓
Creating vehicleiq-redis...     ✓
Creating vehicleiq-backend...   ✓
Creating vehicleiq-frontend...  ✓
Creating vehicleiq-paddleocr... ✓
Creating vehicleiq-yolo...      ✓
Creating vehicleiq-embeddings...✓
```

### Step 2: Check Status
```bash
$ docker-compose ps

NAME                    STATUS
vehicleiq-postgres      Up (healthy)  ✓
vehicleiq-redis         Up (healthy)  ✓
vehicleiq-backend       Up (healthy)  ✓
vehicleiq-worker        Up            ✓
vehicleiq-frontend      Up            ✓
vehicleiq-paddleocr     Up (healthy)  ✓
vehicleiq-yolo          Up (healthy)  ✓
vehicleiq-embeddings    Up (healthy)  ✓
```

### Step 3: Run Migrations
```bash
$ docker-compose exec backend alembic upgrade head

INFO  [alembic.runtime.migration] Running upgrade -> 001_initial
✓ Migration successful
```

### Step 4: Seed Data
```bash
$ docker-compose exec backend python scripts/seed.py

🌱 Seeding database...
Creating users...        ✓
Creating vehicles...     ✓
Creating comparables...  ✓
✅ Database seeded successfully!
```

### Step 5: Test API
```bash
$ curl http://localhost:8000/health

{
  "status": "healthy",
  "version": "0.1.0",
  "service": "vehicleiq-api"
}
✓ Backend is healthy
```

### Step 6: Test Login
```bash
$ curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@vehicleiq.com","password":"Admin@123456"}'

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 2592000
}
✓ Authentication works
```

### Step 7: Open Frontend
```
Browser: http://localhost:3000

┌─────────────────────────────────────┐
│          VehicleIQ                  │
│  AI-Powered Vehicle Assessment      │
│                                     │
│  ┌─────────┐  ┌─────────┐         │
│  │ Fraud   │  │ Price   │         │
│  │Detection│  │Predict  │         │
│  └─────────┘  └─────────┘         │
│  ┌─────────┐  ┌─────────┐         │
│  │ Image   │  │ Health  │         │
│  │Intel    │  │ Score   │         │
│  └─────────┘  └─────────┘         │
└─────────────────────────────────────┘
✓ Frontend loads
```

---

## 🎯 Success Criteria

### Minimum (Must Pass):
- ✅ All 8 services running
- ✅ Backend health check passes
- ✅ Can login and get JWT token
- ✅ Frontend loads

### Recommended (Should Pass):
- ✅ All AI services respond
- ✅ Database has seeded data
- ✅ API docs accessible
- ✅ No errors in logs

### Excellent (Nice to Have):
- ✅ All unit tests pass
- ✅ Can query database
- ✅ All health checks pass
- ✅ No warnings in browser console

---

## 🚀 Quick Commands Cheat Sheet

```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart a service
docker-compose restart backend

# Enter a container
docker-compose exec backend bash

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database
docker-compose exec backend python scripts/seed.py

# Run tests
docker-compose exec backend pytest

# Check database
docker-compose exec postgres psql -U vehicleiq -d vehicleiq
```

---

## 📞 Getting Help

### If services won't start:
1. Check Docker Desktop is running
2. Check ports aren't in use: `lsof -i :8000`
3. View logs: `docker-compose logs <service>`
4. Restart Docker Desktop

### If tests fail:
1. Check service logs
2. Verify database connection
3. Ensure migrations ran
4. Check seed data exists

### If frontend is blank:
1. Check frontend logs
2. Verify backend is running
3. Check browser console for errors
4. Restart frontend service

---

## ✅ Final Checklist

Before proceeding to Phase 2:

- [ ] All services are running
- [ ] Database is seeded
- [ ] Can login successfully
- [ ] Frontend loads correctly
- [ ] API docs are accessible
- [ ] All health checks pass
- [ ] No critical errors in logs

---

## 🎉 Success!

If all checks pass, you have:
- ✅ Working backend API
- ✅ Functional database with test data
- ✅ Authentication system
- ✅ AI microservices ready
- ✅ Frontend interface
- ✅ Complete development environment

**You're ready for Phase 2!** 🚀

---

**Estimated Testing Time:**
- Quick validation: 15-20 minutes
- Thorough testing: 60-70 minutes
- Automated script: 10 minutes
