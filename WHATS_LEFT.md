# What's Left to Build - VehicleIQ

## Phase 2: Image Intelligence (Current - 70% Complete)

### Remaining Tasks:

**Task 11: Assessment Models & Database Schema**
- [ ] Create `assessment` table with photo references
- [ ] Create `assessment_photos` table with storage paths
- [ ] Add OCR extraction results storage
- [ ] Add damage detection results storage
- [ ] Create database migration

**Task 12: Assessment Creation API**
- [ ] `POST /v1/assessments` - Create new assessment
- [ ] `GET /v1/assessments/{id}` - Get assessment status
- [ ] `GET /v1/assessments` - List assessments with filtering
- [ ] Link photos to assessments
- [ ] Store OCR and damage results

**Task 13: Integration Testing**
- [ ] End-to-end test: Upload 13 photos → Process → Store results
- [ ] Test quality gate rejection scenarios
- [ ] Test OCR extraction accuracy
- [ ] Test damage detection accuracy
- [ ] Test parallel processing performance

---

## Phase 3: Fraud Detection (Week 4)

**9 Fraud Signals to Implement:**
1. VIN clone detection
2. Photo reuse detection (perceptual hashing)
3. Odometer rollback detection (LLM-based)
4. Flood damage detection
5. Document tampering detection
6. Claim history cross-match (mock)
7. Registration mismatch validation
8. Salvage title check (mock)
9. Stolen vehicle check (mock)

**Fraud Confidence Scoring:**
- Weighted sum of 9 signals → 0-100 score
- Fraud gate: If > 60, cap health_score at 30 + manual review
- Explainable evidence for each signal

**API Endpoints:**
- `POST /v1/fraud/detect` - Run fraud detection
- API rate limiting and fallback (Groq → Together.ai)

---

## Phase 4: Price Prediction (Week 5)

**4-Layer Pricing Model:**
1. Base price lookup (from vehicle_registry)
2. Condition adjustment (based on health_score)
3. RAG comparable retrieval (pgvector similarity search)
4. Quantile regression (P10, P50, P90)

**Persona-Specific Values:**
- Lender: FSV = P10 × 0.95
- Insurer: IDV = P50 × depreciation_factor
- Broker: asking_price = P90 × 1.05

**Embeddings Service:**
- Already built! (BGE-M3 at port 8003)
- Need to integrate with comparable vehicle retrieval

**API Endpoints:**
- `POST /v1/price/predict` - Get price prediction

---

## Phase 5: Health Score & Benchmarking (Week 6-7)

**Health Score Components:**
1. Mechanical condition
2. Exterior condition
3. Interior condition
4. Accident history
5. Service history
6. Market appeal

**Persona-Specific Weighting:**
- Different weights for Lender, Insurer, Broker
- Fraud gate integration (cap at 30 if fraud detected)
- Low health score flagging (< 40 → manual review)

**Benchmarking System:**
- MAPE calculation (Mean Absolute Percentage Error)
- Outcome pairing (link predictions to actual prices)
- Market data ingestion
- Nightly embedding regeneration

**Seeded Dataset:**
- 1000+ vehicle registry records
- 2000+ comparable vehicles with embeddings
- 500+ historical assessments
- 50+ fraud cases

---

## Phase 6: Assessment Pipeline (Week 7)

**Assessment Orchestration:**
- State machine for pipeline stages
- Parallel processing (OCR + damage detection)
- Target: < 90 seconds for complete assessment
- Real-time progress updates via Supabase Realtime

**Celery Worker:**
- Async processing with Redis queue
- 4 concurrent workers
- Error handling and retry logic

**Immutable Audit Trail:**
- Assessment records with unique IDs
- Prevent modification after creation
- 7-year photo retention

---

## Phase 7: Manual Review & Reporting (Week 8)

**Manual Review Queue:**
- Priority-based queue (high if fraud > 60)
- Approve/override endpoints
- Queue notifications (> 20 items or > 24 hours)

**Report Generation:**
- Persona-specific templates (Lender, Insurer, Broker)
- PDF and JSON export
- Damage annotations on photos
- Explainable AI sections
- Fraud highlighting

**Notification System:**
- Email, SMS, in-app notifications (mock for demo)
- Configurable preferences
- Rate limiting (10 per user per hour)

---

## Phase 8: Frontend Development (Week 9-10)

**Next.js 14 Application:**
- Authentication pages (login/register)
- Vehicle data entry form
- Guided photo capture (13 angles)
- Real-time progress tracking
- Assessment results display
- Assessment history and search
- Admin dashboard
- Manual review interface
- Responsive design (mobile, tablet, desktop)
- Offline capability

---

## Phase 9: Advanced Features (Week 10)

**Batch Processing:**
- CSV upload (100+ records)
- Process 20 assessments per minute
- Batch progress tracking
- Summary reports

**Search & Filter:**
- Advanced search by VIN, make, model, year, date range
- Filtering by health_score, fraud flags, price range
- Sorting and pagination
- Saved search queries

**Model Versioning:**
- A/B testing for price prediction models
- MAPE tracking by version
- Model promotion

**Performance Monitoring:**
- Processing time tracking
- API error rates
- Performance alerts
- Metrics dashboard

---

## Phase 10: Security & Testing (Week 11)

**Security Hardening:**
- Data encryption (AES-256)
- PII hashing (SHA-256)
- Password requirements
- Session timeout (30 minutes)
- Suspicious login detection
- Comprehensive audit logging
- Rate limiting

**Property-Based Testing:**
- 51 correctness properties to implement
- Hypothesis (Python) and fast-check (TypeScript)
- Minimum 100 iterations per test

**Test Coverage:**
- Minimum 80% code coverage
- Unit tests for all components
- Integration tests for workflows
- End-to-end tests

**Performance Optimization:**
- Redis caching strategy
- Database query optimization
- Connection pooling
- Parallel processing
- Frontend optimizations

---

## Phase 11: Deployment & Documentation (Week 12)

**Cloud Deployment:**
- Vercel (frontend)
- Railway/Hetzner (backend + AI services)
- Supabase (database + storage + realtime)
- Upstash Redis (cache + queue)
- Groq API + Together.ai (LLM)

**Local Docker Deployment:**
- Complete docker-compose.yml
- Ollama for local LLM
- Database initialization scripts
- Seeded data

**Reliability:**
- Health check endpoints
- Automatic service restart
- Database backups (24-hour interval, 30-day retention)
- Point-in-time recovery (5-minute interval)
- 99% uptime target

**Documentation:**
- OpenAPI 3.0 specification
- Swagger UI at /docs
- API integration examples
- Deployment guides
- User guides

---

## Summary by Completion Status

### ✅ Completed (Phase 1 + 70% of Phase 2):
- Core infrastructure (Docker, database, auth, RBAC)
- PaddleOCR service (OCR extraction)
- YOLOv8n service (damage detection)
- BGE-M3 service (embeddings)
- Photo quality gate
- Image intelligence orchestration
- Photo upload API

### 🚧 In Progress (30% of Phase 2):
- Assessment database schema
- Assessment creation API
- Integration testing

### 📋 Not Started (Phases 3-11):
- Fraud detection (9 signals)
- Price prediction (4-layer model)
- Health score calculation
- Benchmarking system
- Assessment pipeline orchestration
- Manual review queue
- Report generation
- Frontend (Next.js)
- Batch processing
- Search & filter
- Security hardening
- Property-based testing
- Deployment configuration
- Documentation

---

## Estimated Remaining Work

**By Phase:**
- Phase 2 (30%): ~1-2 days
- Phase 3: ~5 days
- Phase 4: ~5 days
- Phase 5: ~10 days
- Phase 6: ~5 days
- Phase 7: ~5 days
- Phase 8: ~10 days
- Phase 9: ~5 days
- Phase 10: ~5 days
- Phase 11: ~5 days

**Total Remaining: ~8-9 weeks of development**

---

## Next Immediate Steps

1. Complete Phase 2 (Assessment schema + API)
2. Test the AI microservices with real photos
3. Start Phase 3 (Fraud detection)
4. Build incrementally, testing at each checkpoint
