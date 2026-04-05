# VehicleIQ Development Guide

## Project Structure

```
vehicleiq/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── tests/          # Test suite
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/               # Next.js 14 frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   └── lib/               # Utilities
├── services/              # AI microservices
│   ├── paddleocr/        # OCR service
│   ├── yolo/             # Damage detection
│   └── embeddings/       # bge-m3 embeddings
├── scripts/              # Utility scripts
└── docker-compose.yml    # Local development setup
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd vehicleiq
   ```

2. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit .env files with your configuration
   ```

3. **Start all services:**
   ```bash
   make up
   ```

4. **Run migrations:**
   ```bash
   make migrate
   ```

5. **Seed test data:**
   ```bash
   make seed
   ```

6. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development Workflow

### Backend Development

```bash
# Install dependencies
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Format code
black app/
ruff check --fix app/

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Run tests
npm test

# Format code
npm run format

# Lint
npm run lint
```

### AI Services Development

Each service is independent:

```bash
# PaddleOCR service
cd services/paddleocr
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# YOLO service
cd services/yolo
pip install -r requirements.txt
uvicorn server:app --reload --port 8002

# Embeddings service
cd services/embeddings
pip install -r requirements.txt
uvicorn server:app --reload --port 8003
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest app/tests/unit/test_security.py

# Run with markers
pytest -m unit
pytest -m integration
pytest -m property

# Run with coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm test -- --coverage
```

### Property-Based Tests

Property tests validate universal correctness properties:

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=100))
def test_property_fraud_confidence_bounds(health_score):
    """Property 1: Fraud Confidence Score Bounds"""
    result = detect_fraud(health_score=health_score)
    assert 0 <= result.fraud_confidence <= 100
```

## Database Management

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "add new table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Seeding Data

```bash
# Seed database with test data
python scripts/seed.py

# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head
python scripts/seed.py
```

## API Documentation

### Swagger UI

Visit http://localhost:8000/docs for interactive API documentation.

### Authentication

All protected endpoints require JWT token:

```bash
# Register user
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User",
    "role": "Assessor"
  }'

# Login
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Use token
curl -X GET http://localhost:8000/v1/assessments \
  -H "Authorization: Bearer <token>"
```

## Deployment

### Local Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloud Deployment

See [deployment guide](docs/deployment.md) for:
- Vercel (frontend)
- Railway/Hetzner (backend)
- Supabase (database)
- Upstash (Redis)

## Troubleshooting

### Database Connection Issues

```bash
# Check if postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U vehicleiq -d vehicleiq
```

### Service Health Checks

```bash
# Backend
curl http://localhost:8000/health

# PaddleOCR
curl http://localhost:8001/health

# YOLO
curl http://localhost:8002/health

# Embeddings
curl http://localhost:8003/health
```

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Docker build fails:**
```bash
# Clean Docker cache
docker system prune -a
# Rebuild
docker-compose build --no-cache
```

## Code Quality

### Pre-commit Checks

```bash
# Backend
black app/
ruff check --fix app/
pytest

# Frontend
npm run format
npm run lint
npm test
```

### Coverage Requirements

- Minimum 80% code coverage
- All public APIs must have tests
- All correctness properties must have property tests

## Contributing

1. Create feature branch from `main`
2. Follow coding standards (see `.kiro/steering/coding-standards.md`)
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

## Resources

- [Requirements](.kiro/specs/vehicle-iq/requirements.md)
- [Design](.kiro/specs/vehicle-iq/design.md)
- [Tasks](.kiro/specs/vehicle-iq/tasks.md)
- [Architecture Principles](.kiro/steering/architecture-principles.md)
- [Coding Standards](.kiro/steering/coding-standards.md)
- [Testing Requirements](.kiro/steering/testing-requirements.md)
