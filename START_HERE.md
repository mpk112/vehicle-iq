# 🚀 VehicleIQ - START HERE

## Welcome to VehicleIQ Phase 1 Testing!

This guide will help you test the Phase 1 implementation in the fastest way possible.

---

## ⚡ Super Quick Start (5 Commands)

```bash
# 1. Navigate to project
cd /Users/praveenkumar/Documents/vehicle_iq

# 2. Setup environment
cp backend/.env.example backend/.env && cp frontend/.env.example frontend/.env

# 3. Start services (takes 5-10 min first time)
docker-compose up -d

# 4. Setup database
docker-compose exec backend alembic upgrade head && docker-compose exec backend python scripts/seed.py

# 5. Test it works
curl http://localhost:8000/health
```

**Then open browser:** http://localhost:3000

---

## � Resuming After Restart?

**Already set up and just restarted your PC?**
→ Read **[RESUME_WORK.md](RESUME_WORK.md)** (3 commands to resume)

---

## 📚 Choose Your Testing Path

### 🏃 I want the fastest test (15 min)
→ Read **[QUICK_TEST.md](QUICK_TEST.md)**
- Copy-paste commands
- Minimal explanation
- Quick validation

### ✅ I want systematic testing (30 min)
→ Read **[TEST_CHECKLIST.md](TEST_CHECKLIST.md)**
- Level-by-level checks
- Clear pass/fail criteria
- Results template

### 📖 I want detailed explanations (60 min)
→ Read **[TESTING_WALKTHROUGH.md](TESTING_WALKTHROUGH.md)**
- Step-by-step guide
- Troubleshooting included
- Complete reference

### 🎯 I want an overview first
→ Read **[TESTING_GUIDE.md](TESTING_GUIDE.md)**
- Visual diagrams
- Architecture overview
- Success criteria

---

## 🎯 What You're Testing

Phase 1 includes:
- ✅ Backend API (FastAPI)
- ✅ Frontend UI (Next.js)
- ✅ Database (PostgreSQL + pgvector)
- ✅ Authentication (JWT)
- ✅ 3 AI Microservices (OCR, YOLO, Embeddings)
- ✅ Test data (users, vehicles)

---

## 🔍 Quick Health Check

After starting services, verify:

```bash
# Backend
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Frontend
open http://localhost:3000
# Expected: Landing page loads

# AI Services
curl http://localhost:8001/health  # PaddleOCR
curl http://localhost:8002/health  # YOLO
curl http://localhost:8003/health  # Embeddings
# Expected: All return {"status":"healthy"}
```

---

## 🎓 Test Credentials

After seeding database:

```
Admin:
  Email: admin@vehicleiq.com
  Password: Admin@123456

Lender:
  Email: lender@example.com
  Password: Lender@123456

Assessor:
  Email: assessor@example.com
  Password: Assessor@123456
```

---

## 🌐 Access Points

Once running:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **PaddleOCR:** http://localhost:8001
- **YOLO:** http://localhost:8002
- **Embeddings:** http://localhost:8003

---

## 🆘 Common Issues

### Services won't start
```bash
docker-compose down
docker-compose up -d
```

### Migration fails
```bash
docker-compose restart postgres
sleep 10
docker-compose exec backend alembic upgrade head
```

### Need to see logs
```bash
docker-compose logs -f
```

### Want to start fresh
```bash
docker-compose down -v
# Then start from Step 1
```

---

## ✅ Success Checklist

Minimum to pass:
- [ ] All services show "Up" in `docker-compose ps`
- [ ] Backend health check returns 200
- [ ] Can login with test credentials
- [ ] Frontend loads at localhost:3000

---

## 📊 What's Next?

After successful testing:
1. ✅ Phase 1 is validated
2. 📝 Review [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)
3. 🚀 Ready for Phase 2 (Image Intelligence)

---

## 💡 Pro Tips

**View all logs:**
```bash
docker-compose logs -f
```

**Restart a service:**
```bash
docker-compose restart backend
```

**Stop everything:**
```bash
docker-compose down
```

**Check database:**
```bash
docker-compose exec postgres psql -U vehicleiq -d vehicleiq
```

---

## 📞 Need More Help?

- **Quick reference:** [QUICK_TEST.md](QUICK_TEST.md)
- **Detailed guide:** [TESTING_WALKTHROUGH.md](TESTING_WALKTHROUGH.md)
- **Checklist:** [TEST_CHECKLIST.md](TEST_CHECKLIST.md)
- **Overview:** [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Development:** [DEVELOPMENT.md](DEVELOPMENT.md)

---

## 🎉 Ready to Test?

Pick your path above and start testing!

**Estimated time:** 15-60 minutes depending on path chosen

**Good luck!** 🚀
