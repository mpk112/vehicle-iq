# VehicleIQ Command Cheatsheet

## 🚀 Essential Commands

### First Time Setup
```bash
cd /Users/praveenkumar/Documents/vehicle_iq
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed.py
```

### Resume After Restart
```bash
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d
```

### Stop Everything
```bash
docker-compose down
```

---

## 📊 Status & Monitoring

```bash
# Check service status
docker-compose ps

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Check backend health
curl http://localhost:8000/health

# Check AI services
curl http://localhost:8001/health  # PaddleOCR
curl http://localhost:8002/health  # YOLO
curl http://localhost:8003/health  # Embeddings
```

---

## 🔄 Service Management

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart postgres

# Stop all services (keeps data)
docker-compose down

# Stop and remove data (⚠️ DELETES EVERYTHING)
docker-compose down -v

# Rebuild a service
docker-compose build backend
docker-compose up -d backend
```

---

## 🗄️ Database Commands

```bash
# Connect to database
docker-compose exec postgres psql -U vehicleiq -d vehicleiq

# Inside psql:
\dt                              # List tables
\d users                         # Describe users table
SELECT COUNT(*) FROM users;      # Count users
SELECT * FROM users LIMIT 5;    # View first 5 users
\q                              # Exit

# Run migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Seed database
docker-compose exec backend python scripts/seed.py
```

---

## 🧪 Testing Commands

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest app/tests/unit/test_security.py

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run tests by marker
docker-compose exec backend pytest -m unit
docker-compose exec backend pytest -m integration
```

---

## 🐳 Docker Commands

```bash
# Enter backend container
docker-compose exec backend bash

# Enter postgres container
docker-compose exec postgres bash

# View container resource usage
docker stats

# Remove unused Docker resources
docker system prune

# View Docker volumes
docker volume ls

# Inspect a volume
docker volume inspect vehicleiq_postgres_data
```

---

## 🌐 Access Points

```bash
# Open in browser
open http://localhost:3000        # Frontend
open http://localhost:8000/docs   # API Docs

# Test with curl
curl http://localhost:8000/health
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@vehicleiq.com","password":"Admin@123456"}'
```

---

## 🔐 Test Credentials

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

## 🛠️ Development Commands

```bash
# Format Python code
docker-compose exec backend black app/

# Lint Python code
docker-compose exec backend ruff check app/

# Fix linting issues
docker-compose exec backend ruff check --fix app/

# Install new Python package
docker-compose exec backend pip install <package>
docker-compose exec backend pip freeze > requirements.txt

# Install new npm package (frontend)
docker-compose exec frontend npm install <package>
```

---

## 🔍 Debugging Commands

```bash
# View last 50 log lines
docker-compose logs --tail=50

# Follow logs in real-time
docker-compose logs -f

# Check disk space
df -h

# Check what's using a port
lsof -i :8000
lsof -i :3000
lsof -i :5432

# Kill process on port
kill -9 $(lsof -t -i:8000)

# Check Docker Desktop status
docker ps
```

---

## 🚨 Emergency Commands

```bash
# Full restart
docker-compose down
docker-compose up -d

# Rebuild everything
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Reset database (⚠️ DELETES DATA)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed.py

# View all running containers
docker ps -a

# Stop all Docker containers
docker stop $(docker ps -aq)

# Remove all Docker containers
docker rm $(docker ps -aq)
```

---

## 📝 Git Commands (When Ready)

```bash
# Check status
git status

# Add files
git add .

# Commit
git commit -m "feat: complete Phase 1 infrastructure"

# View history
git log --oneline

# Create branch
git checkout -b feature/phase-2

# Push to remote
git push origin main
```

---

## 💡 Useful Aliases

Add to `~/.zshrc` or `~/.bash_profile`:

```bash
# VehicleIQ shortcuts
alias viq='cd /Users/praveenkumar/Documents/vehicle_iq'
alias viq-start='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose up -d'
alias viq-stop='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose down'
alias viq-restart='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose restart'
alias viq-logs='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose logs -f'
alias viq-ps='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose ps'
alias viq-test='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose exec backend pytest'
alias viq-db='cd /Users/praveenkumar/Documents/vehicle_iq && docker-compose exec postgres psql -U vehicleiq -d vehicleiq'
```

Then reload: `source ~/.zshrc`

Use: `viq-start`, `viq-logs`, etc.

---

## 🎯 Common Workflows

### Daily Start
```bash
viq-start  # or: docker-compose up -d
viq-ps     # or: docker-compose ps
```

### Check Logs
```bash
viq-logs   # or: docker-compose logs -f
```

### Run Tests
```bash
viq-test   # or: docker-compose exec backend pytest
```

### Database Work
```bash
viq-db     # or: docker-compose exec postgres psql -U vehicleiq -d vehicleiq
```

### End of Day
```bash
viq-stop   # or: docker-compose down
# or just leave running
```

---

## 📞 Quick Help

| Problem | Command |
|---------|---------|
| Services won't start | `docker-compose down && docker-compose up -d` |
| Port in use | `lsof -i :8000` then `kill -9 <PID>` |
| Database error | `docker-compose restart postgres` |
| Frontend blank | `docker-compose restart frontend` |
| Need fresh start | `docker-compose down -v && docker-compose up -d` |
| Check logs | `docker-compose logs -f <service>` |

---

**Print this page for quick reference!** 📄
