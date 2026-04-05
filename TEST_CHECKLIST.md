# VehicleIQ Phase 1 - Testing Checklist

## Pre-Flight Checks

- [ ] Docker Desktop is running
- [ ] Terminal is open
- [ ] In project directory: `/Users/praveenkumar/Documents/vehicle_iq`

---

## 🟢 Level 1: Basic Setup (Must Pass)

### Environment Setup
- [ ] Created `backend/.env` from example
- [ ] Created `frontend/.env` from example

### Docker Services
- [ ] Ran `docker-compose up -d`
- [ ] All 8 containers show "Up" status
- [ ] No error messages in `docker-compose ps`

### Database
- [ ] Migrations ran successfully
- [ ] Seed script completed
- [ ] Can connect to postgres

**Commands:**
```bash
docker-compose up -d
docker-compose ps
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed.py
```

---

## 🟡 Level 2: API Testing (Should Pass)

### Health Checks
- [ ] Backend: `curl http://localhost:8000/health` returns healthy
- [ ] PaddleOCR: `curl http://localhost:8001/health` returns healthy
- [ ] YOLO: `curl http://localhost:8002/health` returns healthy
- [ ] Embeddings: `curl http://localhost:8003/health` returns healthy

### API Documentation
- [ ] Can access http://localhost:8000/docs
- [ ] Swagger UI loads correctly
- [ ] See auth endpoints listed

### Authentication
- [ ] Can register new user via API
- [ ] Can login with admin@vehicleiq.com
- [ ] Receive JWT token
- [ ] Token is valid (not expired)

**Test Commands:**
```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Login
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@vehicleiq.com","password":"Admin@123456"}'
```

---

## 🔵 Level 3: Frontend Testing (Should Pass)

### Basic Access
- [ ] Can access http://localhost:3000
- [ ] Page loads without errors
- [ ] See "VehicleIQ" heading
- [ ] See 4 feature cards

### Browser Console
- [ ] Open DevTools (F12)
- [ ] No red errors in Console
- [ ] Network tab shows successful requests

---

## 🟣 Level 4: Database Verification (Should Pass)

### Data Integrity
- [ ] 3 users exist (admin, lender, assessor)
- [ ] 100+ vehicle registry records
- [ ] 50+ comparable vehicles
- [ ] pgvector extension enabled

**Verification Commands:**
```bash
docker-compose exec postgres psql -U vehicleiq -d vehicleiq

# Inside psql:
SELECT COUNT(*) FROM users;           -- Should be 3
SELECT COUNT(*) FROM vehicle_registry; -- Should be 100
SELECT COUNT(*) FROM comparable_vehicles; -- Should be 50
\q
```

---

## 🔴 Level 5: Advanced Testing (Optional)

### Error Handling
- [ ] Invalid login returns 401
- [ ] Invalid email format returns 400
- [ ] Missing auth token returns 401/403

### Unit Tests
- [ ] Backend tests pass
- [ ] No test failures

**Test Commands:**
```bash
# Run tests
docker-compose exec backend pytest app/tests/unit/ -v

# Expected: All tests pass
```

---

## 📊 Results Summary

### Minimum to Pass Phase 1:
- ✅ All Level 1 checks (Basic Setup)
- ✅ All Level 2 checks (API Testing)
- ✅ All Level 3 checks (Frontend Testing)

### Bonus Points:
- ✅ Level 4 (Database Verification)
- ✅ Level 5 (Advanced Testing)

---

## 🚨 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Port already in use | `docker-compose down` then retry |
| Migration fails | `docker-compose restart postgres` wait 10s, retry |
| Service not healthy | Check logs: `docker-compose logs <service>` |
| Frontend blank | `docker-compose restart frontend` |
| Can't connect to DB | `docker-compose restart postgres` |

---

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

Level 1 (Basic Setup):        [ ] Pass  [ ] Fail
Level 2 (API Testing):        [ ] Pass  [ ] Fail
Level 3 (Frontend Testing):   [ ] Pass  [ ] Fail
Level 4 (Database):           [ ] Pass  [ ] Fail
Level 5 (Advanced):           [ ] Pass  [ ] Fail

Issues Encountered:
_________________________________
_________________________________
_________________________________

Overall Status:               [ ] PASS  [ ] FAIL

Notes:
_________________________________
_________________________________
```

---

## ✅ When All Tests Pass

You're ready for:
1. ✅ Phase 1 is validated
2. 🚀 Proceed to Phase 2 (Image Intelligence)
3. 💾 Commit code to Git
4. 📖 Review Phase 2 tasks

---

## 🆘 Need Help?

1. Check logs: `docker-compose logs -f`
2. Restart services: `docker-compose restart <service>`
3. Full reset: `docker-compose down -v` then start over
4. Review: [TESTING_WALKTHROUGH.md](TESTING_WALKTHROUGH.md)
