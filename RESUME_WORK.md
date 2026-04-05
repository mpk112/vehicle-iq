# 🔄 Resume Work After Restart

## Quick Resume (3 Commands)

After restarting your PC, here's how to get back to work:

```bash
# 1. Navigate to project
cd /Users/praveenkumar/Documents/vehicle_iq

# 2. Start all services
docker-compose up -d

# 3. Verify everything is running
docker-compose ps
```

**That's it!** Your data persists in Docker volumes, so no need to re-seed.

---

## 🔍 Detailed Resume Steps

### Step 1: Check Docker Desktop

**Before anything else:**
- [ ] Open Docker Desktop application
- [ ] Wait for it to fully start (green icon)
- [ ] Verify Docker is running: `docker ps`

### Step 2: Navigate to Project

```bash
cd /Users/praveenkumar/Documents/vehicle_iq
```

### Step 3: Start Services

```bash
docker-compose up -d
```

**What happens:**
- Docker reads `docker-compose.yml`
- Starts all 8 services
- Reconnects to existing volumes (your data is preserved!)
- Takes 30-60 seconds

### Step 4: Verify Services

```bash
docker-compose ps
```

**Expected output:**
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

### Step 5: Quick Health Check

```bash
# Backend
curl http://localhost:8000/health

# Frontend
open http://localhost:3000
```

---

## 💾 What Persists After Restart?

### ✅ Data That Persists (Stored in Docker Volumes)

- **Database:** All users, vehicles, assessments
- **Redis cache:** Session data
- **Uploaded files:** Photos and documents
- **Configuration:** .env files

### ❌ What Doesn't Persist

- **Running containers:** Need to restart with `docker-compose up -d`
- **In-memory data:** Redis cache may be cleared
- **Active sessions:** Users may need to re-login

---

## 🎯 Common Scenarios

### Scenario 1: Just Restarted PC

```bash
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d
# Wait 30 seconds
curl http://localhost:8000/health
```

### Scenario 2: Docker Desktop Was Quit

```bash
# 1. Start Docker Desktop
# 2. Wait for it to fully start
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d
```

### Scenario 3: Services Were Stopped

```bash
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d
```

### Scenario 4: Need to Continue Development

```bash
cd /Users/praveenkumar/Documents/vehicle_iq

# Start services
docker-compose up -d

# Open your code editor
code .  # VS Code
# or
open -a "Cursor" .  # Cursor

# View logs while developing
docker-compose logs -f backend
```

### Scenario 5: Need to Continue Testing

```bash
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d

# Continue where you left off
open START_HERE.md
```

---

## 🔧 Troubleshooting After Restart

### Issue: Services won't start

**Check Docker Desktop:**
```bash
docker ps
```

If error: "Cannot connect to Docker daemon"
- Open Docker Desktop
- Wait for it to fully start
- Try again

### Issue: Port already in use

**Find and kill process:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Restart services
docker-compose up -d
```

### Issue: Database connection failed

**Restart postgres:**
```bash
docker-compose restart postgres
sleep 10
docker-compose restart backend
```

### Issue: Services show "Restarting" status

**View logs to see what's wrong:**
```bash
docker-compose logs <service-name>

# Example:
docker-compose logs backend
```

**Common fix:**
```bash
docker-compose down
docker-compose up -d
```

---

## 📊 Verify Data Persists

After restart, verify your data is still there:

```bash
# Check database
docker-compose exec postgres psql -U vehicleiq -d vehicleiq

# Inside psql:
SELECT COUNT(*) FROM users;           -- Should be 3+
SELECT COUNT(*) FROM vehicle_registry; -- Should be 100
SELECT COUNT(*) FROM comparable_vehicles; -- Should be 50
\q
```

---

## 🚀 Quick Commands Reference

```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything (keeps data)
docker-compose down

# Restart a service
docker-compose restart backend

# Stop and remove everything (DELETES DATA!)
docker-compose down -v  # ⚠️ Use with caution!
```

---

## 📝 Daily Workflow

### Morning Routine

```bash
# 1. Start Docker Desktop (if not auto-starting)
# 2. Navigate to project
cd /Users/praveenkumar/Documents/vehicle_iq

# 3. Start services
docker-compose up -d

# 4. Verify
docker-compose ps
curl http://localhost:8000/health

# 5. Start coding!
```

### End of Day

**Option 1: Leave Running (Recommended)**
```bash
# Just close your terminal
# Services keep running in background
# Fast startup next day
```

**Option 2: Stop Services**
```bash
# Stop services but keep data
docker-compose down

# Next day: docker-compose up -d
```

**Option 3: Full Shutdown**
```bash
# Stop Docker Desktop
# Saves system resources
# Slower startup next day
```

---

## 🔄 Different Resume Scenarios

### After 1 Hour Break
```bash
# Services should still be running
# Just continue working
curl http://localhost:8000/health  # Quick check
```

### After Overnight
```bash
# If you left services running:
docker-compose ps  # Check status

# If you stopped services:
docker-compose up -d
```

### After Weekend
```bash
# Services likely stopped
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d

# Verify data integrity
docker-compose exec postgres psql -U vehicleiq -d vehicleiq
SELECT COUNT(*) FROM users;
\q
```

### After System Update/Restart
```bash
# 1. Ensure Docker Desktop is running
# 2. Navigate to project
cd /Users/praveenkumar/Documents/vehicle_iq

# 3. Start services
docker-compose up -d

# 4. If issues, try full restart:
docker-compose down
docker-compose up -d
```

---

## 💡 Pro Tips

### Tip 1: Auto-start Docker Desktop
- Open Docker Desktop settings
- Enable "Start Docker Desktop when you log in"
- Services will be ready faster

### Tip 2: Create Terminal Alias
Add to `~/.zshrc` or `~/.bash_profile`:
```bash
alias viq='cd /Users/praveenkumar/Documents/vehicle_iq'
alias viq-start='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose up -d'
alias viq-stop='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose down'
alias viq-logs='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose logs -f'
```

Then use:
```bash
viq-start  # Start everything
viq-logs   # View logs
viq-stop   # Stop everything
```

### Tip 3: Check Before Starting
```bash
# See if services are already running
docker-compose ps

# If already running, no need to start again!
```

### Tip 4: Monitor Resources
```bash
# Check Docker resource usage
docker stats

# If high CPU/memory, restart services:
docker-compose restart
```

---

## 🎯 Quick Decision Tree

```
Did you restart your PC?
├─ Yes → Start Docker Desktop → docker-compose up -d
└─ No
    ├─ Are services running? (docker-compose ps)
    │   ├─ Yes → Continue working
    │   └─ No → docker-compose up -d
    └─ Is Docker Desktop running? (docker ps)
        ├─ Yes → docker-compose up -d
        └─ No → Start Docker Desktop → docker-compose up -d
```

---

## 📋 Resume Checklist

Before continuing work:

- [ ] Docker Desktop is running
- [ ] In project directory: `/Users/praveenkumar/Documents/vehicle_iq`
- [ ] Services started: `docker-compose up -d`
- [ ] All services "Up": `docker-compose ps`
- [ ] Backend healthy: `curl http://localhost:8000/health`
- [ ] Frontend loads: http://localhost:3000

---

## 🆘 When Things Go Wrong

### Nuclear Option (Start Fresh)

If nothing works:

```bash
# 1. Stop everything
docker-compose down

# 2. Restart Docker Desktop
# (Quit and reopen Docker Desktop app)

# 3. Wait 30 seconds

# 4. Start fresh
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d

# 5. Wait 60 seconds

# 6. Check status
docker-compose ps
```

### Data Recovery

If you accidentally deleted data:

```bash
# Re-run migrations and seed
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed.py
```

---

## 📞 Need Help?

1. Check service logs: `docker-compose logs <service>`
2. Restart specific service: `docker-compose restart <service>`
3. Full restart: `docker-compose down && docker-compose up -d`
4. Check Docker Desktop is running
5. Verify disk space: `df -h`

---

## ✅ Success Indicators

You're ready to continue when:

- ✅ `docker-compose ps` shows all services "Up"
- ✅ `curl http://localhost:8000/health` returns healthy
- ✅ http://localhost:3000 loads in browser
- ✅ No errors in `docker-compose logs`

---

## 🎉 You're Back!

Once all checks pass, you can:
- Continue development
- Run tests
- Access API docs at http://localhost:8000/docs
- Use test credentials to login

**Happy coding!** 🚀
