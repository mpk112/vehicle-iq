# Data Generation Strategy for VehicleIQ

## Overview

VehicleIQ requires realistic test data across multiple tables to demonstrate and test all features. This document outlines the strategy for generating and populating the database.

## Data Generation Approach

### 1. Synthetic Data Generation (Primary Method)

We'll use Python scripts with the `Faker` library and custom generators to create realistic Indian vehicle market data.

**Advantages:**
- Full control over data distribution
- Reproducible with seeds
- No privacy concerns
- Can generate large volumes quickly
- Tailored to Indian market specifics

### 2. Data Sources

**Indian Vehicle Market Data:**
- Make/Model combinations from popular Indian brands
- Realistic price ranges for Indian market (₹4L - ₹20L)
- Indian cities for location data
- Indian registration number formats (e.g., DL01AB1234)
- VIN patterns following international standards

## Tables to Populate

### Phase 1: Core Tables (Already Implemented)

#### 1. `users` Table
**Current Status:** ✅ Basic implementation exists

**Data:**
- 3 test users (Admin, Lender, Assessor)
- All 5 roles represented: Assessor, Lender, Insurer, Broker, Admin

**Enhancement Needed:**
- Add Insurer and Broker users
- Add multiple users per role for testing
- Add inactive users for testing

#### 2. `vehicle_registry` Table
**Current Status:** ✅ Basic implementation exists (100 records)

**Data:**
- 5 makes × 5 models × 7 years = 175 combinations
- Variants: Standard, Premium, Top
- Fuel types: Petrol, Diesel, CNG, Electric
- Transmissions: Manual, Automatic, AMT, CVT
- Base prices: ₹4L - ₹20L

**Enhancement Needed:**
- Expand to 1000+ records with more variants
- Add realistic specifications (engine size, seating, etc.)

#### 3. `comparable_vehicles` Table
**Current Status:** ✅ Basic implementation exists (50 records)

**Data:**
- 2000+ comparable listings
- Realistic mileage (10k - 150k km)
- Listing dates spanning 12 months
- 20+ Indian cities
- Embeddings (1024-dimensional vectors)

**Enhancement Needed:**
- Generate embeddings using BGE-M3 service
- Add more realistic price variations
- Add condition descriptions

### Phase 2: Assessment Tables (To Be Implemented)

#### 4. `assessments` Table
**Status:** 🚧 Schema needs to be created

**Data to Generate:**
- 500+ historical assessments
- Mix of all personas (Lender, Insurer, Broker)
- Various health scores (20-95)
- Various fraud confidence levels (0-80)
- Complete AI outputs (fraud, damage, price, health)
- Timestamps spanning 6 months

**Generation Strategy:**
```python
# For each assessment:
1. Pick random vehicle from registry
2. Generate random VIN
3. Assign random persona
4. Generate health score (weighted distribution: 70% good, 20% medium, 10% poor)
5. Generate fraud confidence (weighted: 85% low, 10% medium, 5% high)
6. Generate price prediction based on health score
7. Generate damage detections (0-10 damages)
8. Link to 13 photo records
9. Set status: completed, in_progress, failed (90% completed)
```

#### 5. `assessment_photos` Table
**Status:** 🚧 Schema needs to be created

**Data to Generate:**
- 13 photos per assessment × 500 assessments = 6,500 photo records
- Photo angles: front, rear, left, right, diagonals, interior, odometer, VIN, registration
- Storage paths (mock S3 or local paths)
- Quality gate results
- OCR results (for odometer, VIN, registration photos)
- Damage detection results

**Generation Strategy:**
```python
# For each assessment, create 13 photos:
angles = [
    "front", "rear", "left_side", "right_side",
    "front_left_diagonal", "front_right_diagonal",
    "rear_left_diagonal", "rear_right_diagonal",
    "interior_dashboard", "odometer", "vin_plate",
    "registration_front", "registration_back"
]

# For each photo:
1. Generate mock storage path
2. Set quality_passed = True (95% of time)
3. Generate OCR results for specific angles:
   - odometer: random reading (10k-150k)
   - vin_plate: assessment VIN
   - registration: Indian format
4. Generate damage detections (0-3 damages per photo)
```

#### 6. `fraud_cases` Table
**Status:** 🚧 To be created

**Data to Generate:**
- 50+ confirmed fraud cases
- Various fraud types:
  - VIN clone (20%)
  - Photo reuse (15%)
  - Odometer rollback (25%)
  - Flood damage (10%)
  - Document tampering (15%)
  - Stolen vehicle (10%)
  - Multiple signals (5%)

**Generation Strategy:**
```python
fraud_types = [
    "vin_clone", "photo_reuse", "odometer_rollback",
    "flood_damage", "document_tampering", "stolen_vehicle"
]

# For each fraud case:
1. Pick fraud type
2. Generate high fraud confidence (60-95)
3. Create evidence dict with specific signals
4. Link to assessment
5. Set confirmed_at timestamp
6. Add investigator notes
```

#### 7. `manual_review_queue` Table
**Status:** 🚧 To be created

**Data to Generate:**
- 20-30 pending reviews
- Mix of priorities (high: fraud > 60, standard: health < 40)
- Various reasons: fraud_detected, low_health_score, high_value
- Some with review notes

**Generation Strategy:**
```python
# Create pending reviews:
1. Pick 20 assessments with fraud > 60 or health < 40
2. Set priority based on fraud confidence
3. Set status: pending (80%), in_review (15%), completed (5%)
4. Add submission timestamp (last 7 days)
5. For completed: add reviewed_by, reviewed_at, review_notes
```

### Phase 3: Benchmarking Tables

#### 8. `benchmarking_metrics` Table
**Status:** 🚧 To be created

**Data to Generate:**
- MAPE metrics over time
- Segmented by category, age, price range
- Daily snapshots for last 90 days

**Generation Strategy:**
```python
# For each day in last 90 days:
1. Calculate overall MAPE (target: 8-12%)
2. Calculate MAPE by make (varies 6-15%)
3. Calculate MAPE by age (newer = lower MAPE)
4. Calculate MAPE by price range
5. Store dataset size and assessment count
```

#### 9. `api_usage` Table
**Status:** 🚧 To be created

**Data to Generate:**
- API call logs for last 30 days
- Services: Groq, Together.ai, PaddleOCR, YOLO, Embeddings
- Success/failure rates
- Response times

**Generation Strategy:**
```python
# For each day:
1. Generate 50-200 API calls
2. Distribute across services (Groq: 40%, PaddleOCR: 30%, YOLO: 20%, Embeddings: 10%)
3. Set success rate: 95%
4. Generate response times (100-2000ms)
5. Track rate limit hits (5% of Groq calls)
```

#### 10. `audit_log` Table
**Status:** 🚧 To be created

**Data to Generate:**
- User actions for last 30 days
- Actions: login, assessment_create, assessment_view, report_download, manual_review

**Generation Strategy:**
```python
# For each user, generate 10-50 actions:
1. Pick action type based on role
2. Generate timestamp (last 30 days)
3. Add resource_id (assessment_id, user_id, etc.)
4. Add IP address (mock)
5. Add user agent (mock)
```

## Implementation Plan

### Step 1: Enhanced Seed Script (Phase 5 - Task 24)

Create `backend/scripts/seed_enhanced.py`:

```python
"""Enhanced seed script with comprehensive test data."""

import asyncio
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np

# Generators:
- UserGenerator: Create 20+ users across all roles
- VehicleRegistryGenerator: Create 1000+ vehicle records
- ComparableVehicleGenerator: Create 2000+ comparables with embeddings
- AssessmentGenerator: Create 500+ assessments with complete AI outputs
- PhotoGenerator: Create 13 photos per assessment
- FraudCaseGenerator: Create 50+ fraud cases
- ManualReviewGenerator: Create 20-30 pending reviews
- BenchmarkingMetricsGenerator: Create 90 days of MAPE data
- APIUsageGenerator: Create 30 days of API logs
- AuditLogGenerator: Create 30 days of user actions
```

### Step 2: Embedding Generation (Phase 5 - Task 23.9)

Create `backend/scripts/generate_embeddings.py`:

```python
"""Generate embeddings for comparable vehicles."""

import asyncio
import httpx
from sqlalchemy import select

async def generate_embeddings():
    # For each comparable vehicle:
    1. Format description: "{year} {make} {model} {variant}, {mileage}km, {location}"
    2. Call embeddings service: POST http://embeddings:8003/embeddings/vehicle
    3. Store 1024-dimensional vector in embedding column
    4. Commit to database
```

### Step 3: Data Reset Functionality (Phase 5 - Task 24.5)

Create `backend/app/api/admin.py`:

```python
@router.post("/admin/reset-data")
async def reset_to_seeded_data():
    """Reset database to seeded state (demo/testing only)."""
    1. Truncate all tables (except users)
    2. Run seed_enhanced.py
    3. Generate embeddings
    4. Return success message
```

## Data Quality Considerations

### Realistic Distributions

**Health Scores:**
- 70% in range 70-90 (good condition)
- 20% in range 50-69 (fair condition)
- 10% in range 20-49 (poor condition)

**Fraud Confidence:**
- 85% in range 0-30 (low risk)
- 10% in range 31-60 (medium risk)
- 5% in range 61-100 (high risk)

**Price Predictions:**
- Base price ± 20% based on health score
- P10 < P50 < P90 (quantile ordering)
- Persona values: FSV < IDV < asking_price

### Data Consistency

**Cross-Table Relationships:**
- Every assessment has 13 photos
- Every photo has quality gate results
- Odometer/VIN/registration photos have OCR results
- Fraud cases link to assessments with fraud > 60
- Manual review queue contains assessments with fraud > 60 or health < 40

**Temporal Consistency:**
- Assessment created_at < photo uploaded_at < completed_at
- Listing dates for comparables span 12 months
- API usage logs align with assessment timestamps

## Testing Data Scenarios

### Scenario 1: Clean Assessment
- Health score: 85
- Fraud confidence: 5
- No damage detections
- All photos pass quality gate
- Price prediction: P50 = ₹8.5L

### Scenario 2: Fraud Detected
- Health score: 30 (capped by fraud gate)
- Fraud confidence: 75
- Multiple fraud signals: VIN clone + photo reuse
- Manual review: high priority
- Price prediction: P50 = ₹6L (adjusted down)

### Scenario 3: Poor Condition
- Health score: 35
- Fraud confidence: 10
- 8 damage detections (dents, scratches, rust)
- Manual review: standard priority
- Price prediction: P50 = ₹5L

### Scenario 4: High Value
- Health score: 90
- Fraud confidence: 0
- Luxury vehicle (Toyota Fortuner 2023)
- Price prediction: P50 = ₹18L
- Notification triggered (high value)

## Maintenance

### Nightly Jobs

**Embedding Regeneration:**
- Run nightly at 2 AM IST
- Generate embeddings for new comparable vehicles
- Update existing embeddings if vehicle data changed

**Metrics Calculation:**
- Calculate daily MAPE
- Update benchmarking_metrics table
- Archive old metrics (> 90 days)

### Data Cleanup

**Photo Retention:**
- Keep photos for 7 years minimum
- Archive old assessments (> 2 years) to cold storage

**API Logs:**
- Keep detailed logs for 30 days
- Aggregate to daily summaries after 30 days
- Delete aggregated logs after 90 days

## Tools and Libraries

**Python Libraries:**
- `Faker`: Generate realistic names, addresses, dates
- `numpy`: Generate embeddings and numerical data
- `random`: Random selections and distributions
- `httpx`: Call embeddings service
- `asyncio`: Async data generation

**Custom Generators:**
- Indian vehicle data (makes, models, variants)
- Indian registration numbers (state codes)
- Indian cities and locations
- VIN generation (17-character format)
- Realistic price distributions

## Summary

The data generation strategy uses synthetic data generation with realistic distributions to populate all tables. The enhanced seed script will create 10,000+ records across 10+ tables, providing comprehensive test data for all features.

**Key Benefits:**
- Reproducible with random seeds
- No privacy concerns
- Realistic Indian market data
- Comprehensive test scenarios
- Easy to reset for demos
