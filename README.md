# VehicleIQ

AI-powered vehicle assessment platform with fraud detection, price prediction, and health scoring.

## 🚀 Quick Start

**New to VehicleIQ?** → Start here: **[START_HERE.md](START_HERE.md)**

### Super Quick Setup (5 commands)
```bash
cd /Users/praveenkumar/Documents/vehicle_iq
cp backend/.env.example backend/.env && cp frontend/.env.example frontend/.env
docker-compose up -d
docker-compose exec backend alembic upgrade head && docker-compose exec backend python scripts/seed.py
curl http://localhost:8000/health
```

Then open: http://localhost:3000

## 📚 Documentation

**New to VehicleIQ?** → **[START_HERE.md](START_HERE.md)** ⭐

**Complete Documentation Index:** → **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** 📚

### Getting Started
- **[START_HERE.md](START_HERE.md)** - Begin here!
- **[RESUME_WORK.md](RESUME_WORK.md)** - Resume after restart (3 commands)
- **[CHEATSHEET.md](CHEATSHEET.md)** - Quick command reference

### Testing & Setup
- **[QUICK_TEST.md](QUICK_TEST.md)** - Fast testing (15 min)
- **[TEST_CHECKLIST.md](TEST_CHECKLIST.md)** - Systematic validation (30 min)
- **[TESTING_WALKTHROUGH.md](TESTING_WALKTHROUGH.md)** - Complete guide (60 min)
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Overview & diagrams

### Development
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guide
- **[PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)** - Phase 1 summary

### Specifications
- [Requirements](.kiro/specs/vehicle-iq/requirements.md) - 30 requirements
- [Design](.kiro/specs/vehicle-iq/design.md) - Technical design
- [Tasks](.kiro/specs/vehicle-iq/tasks.md) - Implementation tasks

### Architecture
- [Architecture Principles](.kiro/steering/architecture-principles.md)
- [Coding Standards](.kiro/steering/coding-standards.md)
- [Testing Requirements](.kiro/steering/testing-requirements.md)

### Development Workflow
- [Branching Strategy](BRANCHING_STRATEGY.md) - Git workflow and branch management

## ✨ Features

- **Fraud Detection**: 9 fraud signals with explainable AI
- **Price Prediction**: 4-layer model with RAG-based comparables
- **Image Intelligence**: OCR extraction and damage detection
- **Health Scoring**: Persona-specific weighted scoring
- **Benchmarking**: MAPE tracking and continuous improvement

## 🛠️ Technology Stack

### Backend
- Python 3.11+ with FastAPI
- PostgreSQL 15 + pgvector
- Redis 7
- Celery for async processing

### Frontend
- Next.js 14 with App Router
- TypeScript
- shadcn/ui + TailwindCSS

### AI/ML
- PaddleOCR v4 (OCR)
- YOLOv8n (damage detection)
- bge-m3 (embeddings)
- Groq API / Ollama (LLM)

## 🌐 Access Points

Once running:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🔐 Test Credentials

```
Admin:    admin@vehicleiq.com / Admin@123456
Lender:   lender@example.com / Lender@123456
Assessor: assessor@example.com / Assessor@123456
```

## 🎯 Quick Commands

```bash
make up          # Start all services
make down        # Stop all services
make logs        # View logs
make test        # Run tests
make migrate     # Run database migrations
make seed        # Seed test data
```

## Architecture

```
User Upload → Quality Gate → OCR + Damage Detection → Fraud Detection
                                                              ↓
                                                    Health Score Calculation
                                                              ↓
                                                    Embedding Generation
                                                              ↓
                                                    RAG Comparable Retrieval
                                                              ↓
                                                    Price Prediction
                                                              ↓
                                                    Report Generation
```

## License

MIT
