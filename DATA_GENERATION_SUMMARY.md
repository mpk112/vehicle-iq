# Data Generation Summary

## How Dataset Gets Generated

VehicleIQ uses **synthetic data generation** with Python scripts to populate all database tables with realistic test data.

## Current Implementation

### ✅ Phase 1 - Basic Seed Script (Already Working)

**File:** `backend/seed.py`

**What it creates:**
- 3 test users (Admin, Lender, Assessor)
- 100 vehicle registry entries
- 50 comparable vehicles (without embeddings)

**How to run:**
```bash
docker-compose exec backend python seed.py
```

### ✅ Enhanced Seed Script (New - Ready to Use)

**File:** `backend/scripts/seed_enhanced.py`

**What it creates:**
- 20 users across all 5 roles (Admin, Lender, Insurer, Broker, Assessor)
- 1,000 vehicle registry entries (10 makes × 10 models × 10 years × 4 variants)
- 2,000 comparable vehicles with realistic pricing

**Features:**
- Realistic Indian market data (Maruti, Hyundai, Tata, Honda, Toyota, etc.)
- Proper price distributions (₹4L - ₹20L)
- Indian cities (Mumbai, Delhi, Bangalore, etc.)
- VIN generation (17-character format)
- Indian registration numbers (DL01AB1234 format)
- Age-based depreciation
- Mileage-based pricing

**How to run:**
```bash
docker-compose exec backend python scripts/seed_enhanced.py
```

### ✅ Embedding Generation Script (New - Ready to Use)

**File:** `backend/scripts/generate_embeddings.py`

**What it does:**
- Generates 1024-dimensional embeddings for all comparable vehicles
- Uses BGE-M3 service (must be running)
- Formats vehicle descriptions and calls embeddings API
- Updates database with embedding vectors

**How to run:**
```bash
# Make sure embeddings service is running first
docker-compose up -d embeddings

# Then generate embeddings
docker-compose exec backend python scripts/generate_embeddings.py
```

## Complete Setup Process

### Step 1: Start Services
```bash
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose up -d
```

### Step 2: Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Step 3: Generate Seed Data
```bash
# Option A: Basic seed (quick, 150 records)
docker-compose exec backend python seed.py

# Option B: Enhanced seed (comprehensive, 3,000+ records)
docker-compose exec backend python scripts/seed_enhanced.py
```

### Step 4: Generate Embeddings
```bash
docker-compose exec backend python scripts/generate_embeddings.py
```

### Step 5: Verify Data
```bash
# Check database
docker-compose exec postgres psql -U vehicleiq -d vehicleiq -c "
SELECT 
  (SELECT COUNT(*) FROM users) as users,
  (SELECT COUNT(*) FROM vehicle_registry) as vehicles,
  (SELECT COUNT(*) FROM comparable_vehicles) as comparables,
  (SELECT COUNT(*) FROM comparable_vehicles WHERE embedding IS NOT NULL) as with_embeddings;
"
```

## Future Data Generation (Phase 5+)

### Assessment Data (To Be Implemented)

**File:** `backend/scripts/seed_assessments.py` (future)

**What it will create:**
- 500+ historical assessments
- 6,500+ photo records (13 per assessment)
- Complete AI outputs (fraud, damage, price, health)
- OCR results for specific photos
- Damage detection results

### Fraud Cases (To Be Implemented)

**File:** `backend/scripts/seed_fraud_cases.py` (future)

**What it will create:**
- 50+ confirmed fraud cases
- Various fraud types (VIN clone, photo reuse, odometer rollback, etc.)
- Evidence and investigator notes

### Manual Review Queue (To Be Implemented)

**What it will create:**
- 20-30 pending reviews
- Mix of priorities (high: fraud > 60, standard: health < 40)
- Review notes and timestamps

### Benchmarking Metrics (To Be Implemented)

**What it will create:**
- 90 days of MAPE data
- Segmented by category, age, price range
- Daily snapshots

### API Usage Logs (To Be Implemented)

**What it will create:**
- 30 days of API call logs
- Services: Groq, Together.ai, PaddleOCR, YOLO, Embeddings
- Success/failure rates and response times

### Audit Logs (To Be Implemented)

**What it will create:**
- 30 days of user actions
- Actions: login, assessment_create, assessment_view, report_download

## Data Quality

### Realistic Distributions

**Health Scores:**
- 70% in range 70-90 (good condition)
- 20% in range 50-69 (fair condition)
- 10% in range 20-49 (poor condition)

**Fraud Confidence:**
- 85% in range 0-30 (low risk)
- 10% in range 31-60 (medium risk)
- 5% in range 61-100 (high risk)

**Prices:**
- Based on make, model, year, variant
- Age-based depreciation (15% per year)
- Mileage-based adjustment (up to 30% reduction)
- Random variation (±10%)

### Data Consistency

**Cross-Table Relationships:**
- Comparable vehicles reference vehicle registry
- Prices are consistent with base prices
- Mileage increases with vehicle age
- Listing dates span 12 months

## Test Credentials

After running seed scripts, use these credentials:

```
Admin:    admin@vehicleiq.com / Admin@123456
Lender:   lender@example.com / Lender@123456
Insurer:  insurer@example.com / Insurer@123456
Broker:   broker@example.com / Broker@123456
Assessor: assessor@example.com / Assessor@123456
```

## Data Reset (For Demos)

To reset database to fresh seeded state:

```bash
# Stop services
docker-compose down

# Remove volumes (deletes all data)
docker volume rm vehicle_iq_postgres_data

# Start services
docker-compose up -d

# Wait for postgres to be ready
sleep 10

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed data
docker-compose exec backend python scripts/seed_enhanced.py

# Generate embeddings
docker-compose exec backend python scripts/generate_embeddings.py
```

## Tools and Libraries Used

**Python Libraries:**
- `Faker`: Generate realistic names, addresses, dates (to be added)
- `random`: Random selections and distributions
- `uuid`: Generate unique identifiers
- `datetime`: Timestamp generation
- `httpx`: Call embeddings service
- `asyncio`: Async data generation

**Custom Generators:**
- Indian vehicle data (makes, models, variants)
- Indian registration numbers (state codes)
- Indian cities and locations
- VIN generation (17-character format)
- Realistic price distributions

## Summary

The data generation uses a **two-step process**:

1. **Seed Script** (`seed_enhanced.py`): Generates all records with realistic data
2. **Embedding Script** (`generate_embeddings.py`): Adds AI embeddings to comparable vehicles

This approach provides:
- ✅ Reproducible data with random seeds
- ✅ No privacy concerns (100% synthetic)
- ✅ Realistic Indian market data
- ✅ Comprehensive test scenarios
- ✅ Easy to reset for demos
- ✅ Fast generation (< 5 minutes for 3,000+ records)

**Current Status:** Phase 1 complete, ready for Phase 2 assessment data generation.
