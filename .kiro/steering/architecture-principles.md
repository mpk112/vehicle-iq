# VehicleIQ Architecture Principles

## Core Philosophy

### Open Source First
- Use 100% open-source technology stack
- No vendor lock-in or proprietary dependencies
- Support both cloud and local deployment with feature parity
- Prefer established open-source projects over custom solutions

### Dual Deployment Strategy
VehicleIQ must support two deployment modes with identical functionality:

**Cloud Deployment:**
- LLM: Groq API (free tier) with Together.ai fallback
- Database: Supabase (Postgres + pgvector + Storage + Realtime)
- Backend: Railway or Hetzner VPS
- Frontend: Vercel
- Cache: Upstash Redis

**Local Docker Deployment:**
- LLM: Ollama (local inference)
- Database: Postgres 15 + pgvector extension
- Backend: Docker container
- Frontend: Docker container
- Cache: Redis 7 Docker container

### Microservices Architecture
Separate AI services from core backend:
- Core Backend: FastAPI application (business logic, API, database)
- PaddleOCR Service: Standalone FastAPI service for OCR
- YOLOv8n Service: Standalone FastAPI service for damage detection
- Embeddings Service: Standalone FastAPI service for bge-m3 embeddings

Benefits: Independent scaling, easier debugging, service isolation

## Technology Stack

### Backend (Python 3.11+)
- **Framework**: FastAPI (async, automatic OpenAPI docs)
- **ORM**: SQLAlchemy 2.0+ (async support)
- **Validation**: Pydantic v2 (type safety, serialization)
- **Task Queue**: Celery with Redis broker (async processing)
- **Database**: PostgreSQL 15 + pgvector extension
- **Cache**: Redis 7 (caching, queues, rate limiting)
- **Testing**: pytest, Hypothesis (property-based testing)

### Frontend (TypeScript)
- **Framework**: Next.js 14 with App Router
- **UI Library**: shadcn/ui (Radix UI + TailwindCSS)
- **State Management**: React hooks + Supabase Realtime
- **API Client**: Supabase client + fetch API
- **Testing**: Jest, React Testing Library, fast-check

### AI/ML Stack
- **OCR**: PaddleOCR v4 (English + Hindi support)
- **Object Detection**: YOLOv8n (damage detection)
- **Embeddings**: bge-m3 from Hugging Face (1024-dimensional)
- **LLM (Cloud)**: Groq API (llama-3.1-70b) with Together.ai fallback
- **LLM (Local)**: Ollama (llama3.1 or mistral)
- **ML Library**: scikit-learn (quantile regression)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database Migrations**: Alembic
- **API Documentation**: Swagger UI (FastAPI automatic)
- **Monitoring**: Health check endpoints + logging

## System Architecture

### Five AI Capability Domains

**1. Fraud Detection**
- 9 fraud signals: VIN clone, photo reuse, odometer rollback, flood damage, document tampering, claim history, registration mismatch, salvage title, stolen vehicle
- Weighted confidence scoring (0-100)
- Fraud gate: If confidence > 60, cap health_score at 30 and trigger manual review

**2. Price Prediction**
- 4-layer model: Base price lookup → Condition adjustment → RAG comparables → Quantile regression
- Persona-specific values: Lender (FSV), Insurer (IDV), Broker (asking price)
- Explainable predictions with comparable vehicles

**3. Image Intelligence**
- Photo quality gate: Blur, lighting, framing, resolution checks
- 13 required photo angles for complete assessment
- OCR extraction: Odometer, VIN, registration, owner details
- Damage detection: 7 damage classes with bounding boxes and severity

**4. Health Scoring**
- 6 components: Mechanical, exterior, interior, accident history, service history, market appeal
- Persona-specific weighted scoring
- Fraud gate integration (cap at 30 if fraud detected)
- Explainable component breakdown

**5. Benchmarking**
- MAPE calculation for price prediction accuracy
- Segmented MAPE by category, age, price range
- Outcome pairing: Link predictions to actual transaction prices
- Continuous model improvement with feedback loop

### Data Flow

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

### Assessment Pipeline Stages
1. Photo validation (quality gate)
2. OCR extraction (odometer, VIN, documents)
3. Fraud detection (9 signals)
4. Damage analysis (YOLOv8n across 13 photos)
5. Embedding generation (bge-m3)
6. Comparable retrieval (pgvector similarity search)
7. Price prediction (4-layer model)
8. Health score calculation (persona-weighted)
9. Report generation (PDF + JSON)
10. Audit trail creation (immutable record)

Target: Complete within 90 seconds

## Database Schema

### Core Tables
- `users`: Authentication, roles (Assessor, Lender, Insurer, Broker, Admin)
- `vehicle_registry`: Base vehicle data (make, model, year, variant, base_price)
- `comparable_vehicles`: Market listings with embeddings (pgvector column)
- `assessments`: Assessment records (immutable core data)
- `assessment_photos`: Photo metadata and storage references
- `manual_review_queue`: Flagged assessments requiring human review
- `fraud_cases`: Confirmed fraud cases for model training
- `benchmarking_metrics`: MAPE tracking and accuracy metrics
- `api_usage`: API call tracking for rate limiting and fallback
- `audit_log`: Comprehensive audit trail for compliance

### Vector Search
- Use pgvector extension for similarity search
- IVFFlat index on embedding column (1024 dimensions)
- Cosine similarity for comparable vehicle retrieval
- Constraints: Same make/model, year ±2, mileage ±20k

## API Design

### RESTful Principles
- Resource-based URLs: `/v1/assessments`, `/v1/fraud/detect`
- HTTP methods: GET (read), POST (create), PUT (update), DELETE (delete)
- Stateless: Each request contains all necessary information
- Versioned: `/v1/` prefix for API version 1

### Key Endpoints
- `POST /v1/assessments` - Create new assessment
- `GET /v1/assessments/{id}` - Get assessment status and results
- `GET /v1/assessments` - List assessments with filtering
- `POST /v1/photos/upload` - Upload photo with quality gate
- `POST /v1/fraud/detect` - Run fraud detection
- `POST /v1/price/predict` - Get price prediction
- `GET /v1/assessments/{id}/report` - Download report (PDF/JSON)
- `GET /v1/manual-review/queue` - Get manual review queue
- `POST /v1/benchmarking/outcome-pairing` - Link prediction to actual price

### Response Format
```json
{
  "data": { ... },
  "error": null,
  "metadata": {
    "timestamp": "2026-04-05T10:30:00Z",
    "request_id": "uuid",
    "processing_time_ms": 1234
  }
}
```

## Security Architecture

### Authentication & Authorization
- JWT tokens with 30-day expiry
- Role-based access control (RBAC)
- Row-level security (RLS) for multi-tenant data isolation
- Session timeout: 30 minutes of inactivity

### Data Protection
- Encryption at rest: AES-256 for photos and sensitive data
- Encryption in transit: TLS 1.3 for all communications
- PII hashing: SHA-256 for owner names and contact details
- Audit logging: All data access events logged

### API Security
- Rate limiting: 10 assessments per minute per user
- Input validation: Pydantic models with strict validation
- CORS: Configured for frontend domain only
- Circuit breaker: Prevent cascading failures from external services

## Performance Requirements

### Response Times
- Assessment completion: < 90 seconds (target: 60-75 seconds)
- API endpoints: < 5 seconds for queries, < 500ms for health checks
- Search queries: < 3 seconds for 1-year date ranges
- Batch processing: Minimum 20 assessments per minute

### Scalability
- Support 1000 assessments per day
- Concurrent processing: 10 assessments simultaneously
- Database connection pool: Min 10, max 20 connections
- Auto-scaling: Min 2, max 10 replicas (cloud deployment)

### Optimization Strategies
- Redis caching: Base prices (24h TTL), embeddings (7d TTL), photo hashes (90d TTL)
- Parallel processing: Damage detection across 13 photos using asyncio
- Database indexes: B-tree on frequently queried columns, IVFFlat on vectors
- Lazy loading: Frontend components and images

## Reliability & Availability

### Uptime Target
- 99% availability during business hours (9 AM - 6 PM IST, Mon-Sat)
- Health check endpoints: < 500ms response time
- Automatic service restart on failure

### Data Durability
- Database backups: Every 24 hours, 30-day retention
- Point-in-time recovery: 5-minute interval
- Photo retention: Minimum 7 years
- Audit log retention: Minimum 7 years

### Error Handling
- Retry logic: 3 attempts with exponential backoff
- Circuit breaker: Open after 5 consecutive failures
- Graceful degradation: Continue processing on non-critical failures
- Comprehensive error logging with context

## Testing Strategy

### Property-Based Testing
- 51 correctness properties derived from requirements
- Hypothesis (Python) and fast-check (TypeScript)
- Minimum 100 iterations per property test
- Tag tests with requirement IDs for traceability

### Test Coverage
- Minimum 80% code coverage (unit + integration tests)
- All API endpoints have integration tests
- All fraud signals have unit tests
- All correctness properties have property tests

### Test Types
- Unit tests: Individual functions and classes
- Integration tests: API endpoints and workflows
- Property tests: Universal correctness properties
- End-to-end tests: Complete assessment pipeline

## Reference Documents

### Primary Implementation Reference
#[[file:claude/vehicle-iq/vehicleiq-1day-build-v2.html]]
- Open-source solution architecture
- Technology stack details
- Implementation patterns

### Specification Documents
- Requirements: #[[file:.kiro/specs/vehicle-iq/requirements.md]]
- Design: #[[file:.kiro/specs/vehicle-iq/design.md]]
- Tasks: #[[file:.kiro/specs/vehicle-iq/tasks.md]]

### Supporting References
- Full MVP: #[[file:claude/vehicle-iq/vehicleiq-mvp.html]]
- Day 1 Hackathon: #[[file:claude/vehicle-iq/vehicleiq-1day-build.html]]

## Development Workflow

### Implementation Phases
1. Core Infrastructure (Week 1-2)
2. Image Intelligence (Week 3)
3. Fraud Detection (Week 4)
4. Price Prediction (Week 5)
5. Health Score & Benchmarking (Week 6-7)
6. Assessment Pipeline (Week 7)
7. Manual Review & Reporting (Week 8)
8. Frontend Development (Week 9-10)
9. Advanced Features (Week 10)
10. Security & Testing (Week 11)
11. Deployment & Documentation (Week 12)

### Checkpoints
- Validate at end of each phase
- Run all tests before proceeding
- Ask user for clarification on crucial choices
- Document decisions and trade-offs

## Deployment Strategy

### Local Docker (Development & Demo)
```bash
docker-compose up
# All services start automatically
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Postgres: localhost:5432
# Redis: localhost:6379
```

### Cloud Production
1. Deploy frontend to Vercel (automatic from Git)
2. Deploy backend + AI services to Railway/Hetzner
3. Configure Supabase database and storage
4. Set up Upstash Redis
5. Configure environment variables
6. Run database migrations
7. Seed initial data

### Environment Variables
- Separate configs for local vs cloud
- Never commit secrets to Git
- Use `.env.example` as template
- Validate required variables on startup

## Monitoring & Observability

### Metrics to Track
- Assessments per day
- Average processing time per stage
- API usage (Groq, Together.ai, PaddleOCR, YOLO)
- Error rates by service
- MAPE trends over time
- Manual review queue depth

### Alerting
- Critical service failures: Alert within 1 minute
- API error rate > 5% over 1 hour: Alert admin
- Manual review queue > 20 items: Alert admin
- Processing time > 90 seconds: Log warning

### Logging
- Structured logging with context (user_id, assessment_id, timestamp)
- Log levels: DEBUG (development), INFO (production), ERROR (always)
- Audit log for all data access and modifications
- Never log sensitive data (passwords, tokens, PII)
