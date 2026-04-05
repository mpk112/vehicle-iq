# Quick Testing Guide - VehicleIQ Phase 1

## 🚀 Quick Start (Copy & Paste Commands)

### 1. Setup Environment (30 seconds)
```bash
cd /Users/praveenkumar/Documents/vehicle_iq
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Start All Services (5-10 minutes first time)
```bash
docker-compose up -d
```

Wait for services to start. Check status:
```bash
docker-compose ps
```

All services should show "Up" status.

### 3. Setup Database (2 minutes)
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed test data
docker-compose exec backend python scripts/seed.py
```

### 4. Quick Health Checks (1 minute)

**Backend:**
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"healthy",...}`

**Frontend:**
Open browser: http://localhost:3000
Expected: Landing page with "VehicleIQ" heading

**API Docs:**
Open browser: http://localhost:8000/docs
Expected: Swagger UI with API endpoints

### 5. Test Authentication (2 minutes)

**Login:**
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@vehicleiq.com","password":"Admin@123456"}'
```

Expected: JSON with `access_token`

**Or use Swagger UI:**
1. Go to http://localhost:8000/docs
2. Click "POST /v1/auth/login"
3. Click "Try it out"
4. Use: admin@vehicleiq.com / Admin@123456
5. Click "Execute"

### 6. Test AI Services (1 minute)
```bash
curl http://localhost:8001/health  # PaddleOCR
curl http://localhost:8002/health  # YOLO
curl http://localhost:8003/health  # Embeddings
```

All should return: `{"status":"healthy",...}`

---

## ✅ Success Checklist

- [ ] `docker-compose ps` shows all services "Up"
- [ ] Backend health check returns 200
- [ ] Frontend loads at localhost:3000
- [ ] API docs accessible at localhost:8000/docs
- [ ] Can login with admin credentials
- [ ] All 3 AI services respond to health checks

---

## 🔧 If Something Fails

**Services won't start:**
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

**Migration fails:**
```bash
docker-compose restart postgres
sleep 10
docker-compose exec backend alembic upgrade head
```

**Can't connect to database:**
```bash
docker-compose logs postgres
docker-compose restart postgres
```

**Frontend blank page:**
```bash
docker-compose logs frontend
docker-compose restart frontend
```

---

## 🛑 Stop Everything
```bash
docker-compose down
```

---

## 📊 What's Working

After successful setup, you have:
- ✅ Backend API with authentication
- ✅ PostgreSQL database with 10 tables
- ✅ 3 test users (Admin, Lender, Assessor)
- ✅ 100+ vehicle records
- ✅ 50+ comparable vehicles
- ✅ 3 AI microservices ready
- ✅ Frontend landing page
- ✅ API documentation

---

## 🎯 Next: Detailed Testing

For comprehensive testing, see: [TESTING_WALKTHROUGH.md](TESTING_WALKTHROUGH.md)

---

## 💡 Pro Tips

**View logs:**
```bash
docker-compose logs -f backend    # Watch backend logs
docker-compose logs --tail=50     # Last 50 lines from all services
```

**Restart a service:**
```bash
docker-compose restart backend
```

**Enter a container:**
```bash
docker-compose exec backend bash
```

**Check database:**
```bash
docker-compose exec postgres psql -U vehicleiq -d vehicleiq
\dt                    # List tables
SELECT COUNT(*) FROM users;
\q                     # Exit
```

---

**Estimated Time:** 15-20 minutes total
