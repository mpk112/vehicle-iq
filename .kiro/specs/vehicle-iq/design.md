# VehicleIQ Design Document

## Overview

VehicleIQ is an AI-powered vehicle valuation platform targeting the Indian used vehicle market. The system addresses critical challenges including 8-18% inter-assessor variance, widespread odometer fraud (1 in 6 vehicles), and slow manual assessment times (48 hours). VehicleIQ delivers 90-second AI-powered assessments with sub-5% MAPE while providing comprehensive fraud detection, image intelligence, and persona-specific valuation reports.

### Design Goals

- **Speed**: Complete end-to-end assessments in under 90 seconds
- **Accuracy**: Achieve sub-5% MAPE on price predictions
- **Fraud Detection**: Identify 9 fraud signals with explainable confidence scoring
- **Scalability**: Support 1000+ assessments per day with horizontal scaling
- **Flexibility**: Support both cloud and local Docker deployments
- **Cost Efficiency**: Leverage free-tier APIs (Groq) with automatic fallback to paid services

### Key Capabilities

The platform integrates five AI capability domains:

1. **Domain A - Fraud Detection**: VIN cloning, odometer rollback, photo reuse, flood damage, document tampering, claim history anomalies
2. **Domain B - Price Prediction**: 4-layer pricing model with RAG-based comparable retrieval and quantile regression
3. **Domain C - Benchmarking**: Proprietary dataset management, MAPE tracking, market data integration
4. **Domain D - Image Intelligence**: 13-angle guided photo capture, OCR extraction, damage detection, quality gates
5. **Domain E - Health Score**: Persona-specific composite scoring (0-100) with fraud gate logic

## Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  Next.js 14 + shadcn/ui + TailwindCSS + Supabase Realtime     │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API + WebSocket
┌────────────────────────────┴────────────────────────────────────┐
│                      API Gateway Layer                          │
│              FastAPI + JWT Auth + Rate Limiting                 │
└─────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
      │          │          │          │          │
      ▼          ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Domain A │ │ Domain B │ │ Domain C │ │ Domain D │ │ Domain E │
│  Fraud   │ │  Price   │ │Benchmark │ │  Image   │ │  Health  │
│Detection │ │Prediction│ │  System  │ │   Intel  │ │  Score   │
└─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘
      │            │            │            │            │
      └────────────┴────────────┴────────────┴────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    Orchestration Layer                          │
│         Assessment Engine + Redis Queue + Worker Pool           │
└─────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
      │          │          │          │          │
      ▼          ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Groq    │ │Together  │ │PaddleOCR │ │ YOLOv8n  │ │  bge-m3  │
│   LLM    │ │.ai (FB)  │ │   v4     │ │ Damage   │ │Embeddings│
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                      Data Layer                                 │
│    Postgres + pgvector + Redis + S3-compatible Storage         │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Architectures

#### Cloud Deployment

```
Frontend: Vercel (Next.js 14)
    ↓
Backend: Railway/Hetzner (FastAPI + Workers)
    ↓
Database: Supabase (Postgres + pgvector + Realtime)
Queue: Upstash Redis
LLM: Groq API (free) → Together.ai (paid fallback)
Storage: Supabase Storage (S3-compatible)
```

#### Local Docker Deployment

```
docker-compose.yml orchestrates:
- frontend: Next.js dev server (port 3000)
- backend: FastAPI + Uvicorn (port 8000)
- postgres: Postgres 15 + pgvector extension (port 5432)
- redis: Redis 7 (port 6379)
- worker: Celery/ARQ worker pool
- paddleocr: PaddleOCR v4 service (port 8001)
- yolo: YOLOv8n service (port 8002)
- embeddings: bge-m3 service (port 8003)
```

### Assessment Pipeline Flow

```
1. Photo Upload (13 angles)
   ↓
2. Quality Gate Validation (Image Intelligence API)
   ↓
3. OCR Extraction (PaddleOCR: VIN, Odometer, Documents)
   ↓
4. Fraud Detection (9 signals → confidence score)
   ↓
5. Damage Detection (YOLOv8n → bounding boxes + severity)
   ↓
6. Embedding Generation (bge-m3 → 1024-dim vector)
   ↓
7. Comparable Retrieval (pgvector similarity search → top 10)
   ↓
8. Price Prediction (4-layer model + quantile regression)
   ↓
9. Health Score Calculation (persona-specific weights + fraud gate)
   ↓
10. Report Generation (PDF/JSON with explainability)
    ↓
11. Audit Trail Creation (immutable Assessment_Record)
```

**Target Timeline**: 90 seconds end-to-end

**Stage Breakdown**:
- Photo validation: 3s × 13 = 39s
- OCR extraction: 2s × 3 = 6s
- Fraud detection: 2s
- Damage detection: 2s × 13 = 26s (parallelized to ~5s)
- Embedding + search: 3s
- Price prediction: 5s
- Health score: 2s
- Report generation: 5s
- **Total**: ~68s (with 22s buffer for network/queue)

## Components and Interfaces

### Domain A: Fraud Detection Engine

**Purpose**: Detect 9 fraud signals and generate explainable confidence scores

**Fraud Signals**:
1. **VIN Clone Detection**: Query vehicle registry for duplicate VINs
2. **Odometer Rollback**: ML model analyzing dashboard photo for tampering indicators
3. **Photo Reuse**: Perceptual hash matching against known photo database
4. **Flood Damage**: Vision model detecting water lines, rust patterns, electrical corrosion
5. **Document Tampering**: OCR + metadata analysis for font inconsistencies, alignment anomalies
6. **Claim History**: Cross-match VIN against insurance claim databases
7. **Registration Mismatch**: Validate VIN vs registration document consistency
8. **Salvage Title**: Check for salvage/rebuilt title indicators
9. **Stolen Vehicle**: Cross-match against stolen vehicle databases

**Scoring Algorithm**:
```python
fraud_confidence = weighted_sum([
    (vin_clone_score, 0.20),
    (odometer_rollback_score, 0.18),
    (photo_reuse_score, 0.15),
    (flood_damage_score, 0.12),
    (document_tampering_score, 0.12),
    (claim_history_score, 0.10),
    (registration_mismatch_score, 0.08),
    (salvage_title_score, 0.03),
    (stolen_vehicle_score, 0.02)
])
# Each signal score: 0-100
# Final fraud_confidence: 0-100
```

**Fraud Gate Logic**:
```python
if fraud_confidence > 60:
    health_score = min(health_score, 30)  # Cap at 30
    add_to_manual_review_queue(priority="high")
```

**API Interface**:
```python
class FraudDetectionRequest(BaseModel):
    vin: str
    photos: List[PhotoData]
    documents: List[DocumentData]
    odometer_reading: int
    registration_number: str

class FraudSignal(BaseModel):
    signal_type: str  # e.g., "vin_clone", "odometer_rollback"
    confidence: float  # 0-100
    evidence: List[str]  # Explainable indicators
    severity: str  # "low", "medium", "high"

class FraudDetectionResponse(BaseModel):
    fraud_confidence: float  # 0-100
    signals: List[FraudSignal]
    fraud_gate_triggered: bool
    recommended_action: str  # "approve", "manual_review", "reject"
    processing_time_ms: int
```

**Implementation Notes**:
- VIN clone check: Direct Postgres query with index on VIN column
- Odometer rollback: Groq Vision API with prompt engineering for tampering detection
- Photo reuse: pHash library for perceptual hashing, stored in Redis for fast lookup
- Flood damage: YOLOv8n fine-tuned on flood damage dataset
- Document tampering: PaddleOCR + metadata extraction + LLM analysis
- Claim history: External API integration (mock for demo)

### Domain B: Price Prediction ML

**Purpose**: Calculate accurate vehicle valuations using 4-layer pricing model with RAG

**4-Layer Pricing Model**:

```
Layer 1: Base Price
- Market data lookup: make + model + year + variant
- Source: Proprietary dataset + external market data
- Output: base_price (INR)

Layer 2: Condition Adjustment
- Input: Vehicle_Health_Score (0-100)
- Multiplier: 0.70 (score=0) to 1.15 (score=100)
- Formula: adjusted_price = base_price × (0.70 + 0.45 × health_score/100)

Layer 3: Comparable Vehicle RAG
- Generate embedding vector (bge-m3, 1024-dim)
- Similarity search (pgvector cosine similarity)
- Retrieve top 10 comparables with constraints:
  * Same make + model
  * Year within ±2 years (relax to ±3 if <5 results)
  * Mileage within ±20k km (relax to ±30k if <5 results)
- Extract comparable prices: [p1, p2, ..., p10]

Layer 4: Quantile Regression
- Fit quantile regression on comparable prices
- Output: P10, P50, P90 predictions
- Adjust based on health score differential
```

**Persona-Specific Outputs**:
```python
if persona == "Lender":
    fsv = P10 × 0.95  # Conservative 5% discount
    return {"fsv": fsv, "loan_to_value_max": 0.80}

elif persona == "Insurer":
    idv = P50 × depreciation_factor(age_years)
    return {"idv": idv, "premium_adjustment": calculate_premium(health_score)}

elif persona == "Broker":
    asking_price = P90 × 1.05  # 5% market premium
    return {"asking_price": asking_price, "negotiation_floor": P50}
```

**API Interface**:
```python
class PricePredictionRequest(BaseModel):
    make: str
    model: str
    year: int
    variant: str
    fuel_type: str
    transmission: str
    mileage: int
    location: str
    health_score: float
    persona: str  # "Lender", "Insurer", "Broker"

class ComparableVehicle(BaseModel):
    id: str
    make: str
    model: str
    year: int
    mileage: int
    price: float
    similarity_score: float  # 0-1
    listing_date: datetime
    key_differences: List[str]

class PricePredictionResponse(BaseModel):
    base_price: float
    adjusted_price: float
    p10: float
    p50: float
    p90: float
    persona_value: float  # FSV, IDV, or asking_price
    comparables: List[ComparableVehicle]
    explanation: Dict[str, Any]
    processing_time_ms: int
```

**Implementation Notes**:
- Embedding generation: bge-m3 model via Hugging Face Transformers
- Vector search: pgvector extension with cosine similarity operator (<=>)
- Quantile regression: scikit-learn QuantileRegressor
- MAPE tracking: Store predicted vs actual in benchmarking table
- Caching: Redis cache for base prices (TTL: 24 hours)

### Domain C: Benchmarking System

**Purpose**: Manage proprietary datasets, track MAPE, integrate market data

**Dataset Management**:
- **Comparable Vehicles**: 2000+ records with embeddings
- **Historical Assessments**: 500+ records with known outcomes
- **Fraud Cases**: 50+ confirmed fraud cases for model validation
- **Market Data**: Weekly integration from external sources

**MAPE Calculation**:
```python
def calculate_mape(predictions: List[float], actuals: List[float]) -> float:
    """Mean Absolute Percentage Error"""
    errors = [abs(pred - actual) / actual for pred, actual in zip(predictions, actuals)]
    return sum(errors) / len(errors) * 100

# Segmented MAPE tracking
mape_by_category = {
    "sedan": calculate_mape(sedan_predictions, sedan_actuals),
    "suv": calculate_mape(suv_predictions, suv_actuals),
    "hatchback": calculate_mape(hatchback_predictions, hatchback_actuals)
}

mape_by_age = {
    "0-3_years": calculate_mape(...),
    "3-5_years": calculate_mape(...),
    "5+_years": calculate_mape(...)
}

mape_by_price_range = {
    "0-5L": calculate_mape(...),
    "5-10L": calculate_mape(...),
    "10L+": calculate_mape(...)
}
```

**Flywheel Logic**:
```
1. Assessment completed → predicted price stored
2. Webhook receives actual transaction price (outcome pairing)
3. Calculate error: |predicted - actual| / actual
4. Update MAPE metrics
5. If MAPE > 5%, flag for model retraining
6. Add transaction to comparable dataset
7. Regenerate embeddings for new comparable
8. Improved dataset → better future predictions
```

**API Interface**:
```python
class MarketDataRecord(BaseModel):
    make: str
    model: str
    year: int
    variant: str
    fuel_type: str
    transmission: str
    mileage: int
    price: float
    location: str
    listing_date: datetime
    listing_url: Optional[str]
    vin: Optional[str]

class BenchmarkingMetrics(BaseModel):
    overall_mape: float
    mape_by_category: Dict[str, float]
    mape_by_age: Dict[str, float]
    mape_by_price_range: Dict[str, float]
    dataset_size: int
    last_updated: datetime
    assessments_with_outcomes: int

class OutcomePairingRequest(BaseModel):
    assessment_id: str
    actual_transaction_price: float
    transaction_date: datetime
    source: str  # "manual", "webhook", "api"
```

**Implementation Notes**:
- Market data ingestion: REST API with API key authentication
- Deduplication: Hash of (VIN, listing_url) stored in Redis
- Embedding regeneration: Batch job runs nightly for new records
- MAPE dashboard: Real-time updates via Supabase Realtime
- Data validation: Pydantic models with strict field validation

### Domain D: Image Intelligence API

**Purpose**: Guided photo capture, OCR extraction, damage detection, quality validation

**13 Required Photo Angles**:
1. Front view (straight on)
2. Rear view (straight on)
3. Driver side (full length)
4. Passenger side (full length)
5. Front-left quarter
6. Front-right quarter
7. Rear-left quarter
8. Rear-right quarter
9. Interior dashboard
10. Odometer close-up
11. VIN plate close-up
12. Engine bay
13. Damage areas (if applicable)

**Quality Gate Validation**:
```python
class QualityGate:
    def validate(self, image: np.ndarray, angle: str) -> QualityResult:
        checks = [
            self.check_blur(image),           # Laplacian variance > threshold
            self.check_lighting(image),       # Mean brightness 50-200
            self.check_framing(image, angle), # Object detection for expected content
            self.check_resolution(image)      # Min 1024x768
        ]
        
        passed = all(check.passed for check in checks)
        feedback = [check.message for check in checks if not check.passed]
        
        return QualityResult(passed=passed, feedback=feedback)
```

**OCR Extraction Pipeline**:
```
PaddleOCR v4 Configuration:
- Language: English + Hindi (lang='en,hi')
- Detection model: ch_PP-OCRv4_det
- Recognition model: ch_PP-OCRv4_rec
- Use GPU if available, fallback to CPU

Extraction Targets:
1. Odometer: Regex pattern \d{1,6} km
2. VIN: 17-character alphanumeric, validate checksum
3. Registration: State code + district + series + number
4. Owner name: Hindi/English text extraction
5. Registration date: Date parsing with multiple formats
```

**Damage Detection**:
```python
# YOLOv8n configuration
model = YOLO('yolov8n.pt')  # Pretrained, fine-tuned on vehicle damage dataset

damage_classes = [
    "dent", "scratch", "rust", "crack", 
    "missing_part", "panel_misalignment", "paint_damage"
]

def detect_damage(image: np.ndarray) -> List[DamageDetection]:
    results = model(image, conf=0.5)  # 50% confidence threshold
    
    detections = []
    for box in results[0].boxes:
        detection = DamageDetection(
            class_name=damage_classes[int(box.cls)],
            confidence=float(box.conf),
            bbox=[int(x) for x in box.xyxy[0]],
            severity=calculate_severity(box)
        )
        detections.append(detection)
    
    return detections

def calculate_severity(box) -> str:
    area = (box.xyxy[0][2] - box.xyxy[0][0]) * (box.xyxy[0][3] - box.xyxy[0][1])
    if area < 5000: return "minor"
    elif area < 20000: return "moderate"
    else: return "severe"
```

**API Interface**:
```python
class PhotoUploadRequest(BaseModel):
    angle: str  # One of 13 required angles
    image_data: str  # Base64 encoded
    assessment_id: str

class QualityResult(BaseModel):
    passed: bool
    feedback: List[str]
    blur_score: float
    lighting_score: float
    framing_score: float

class OCRExtractionResult(BaseModel):
    field: str  # "odometer", "vin", "registration"
    value: str
    confidence: float
    requires_verification: bool

class DamageDetection(BaseModel):
    class_name: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    severity: str  # "minor", "moderate", "severe"
```

### Domain E: Vehicle Health Score

**Purpose**: Calculate 0-100 composite score with persona-specific weights and fraud gate

**Scoring Components**:
```python
class HealthScoreComponents:
    mechanical_condition: float  # 0-100 (engine, transmission, suspension)
    exterior_condition: float    # 0-100 (paint, body, glass)
    interior_condition: float    # 0-100 (seats, dashboard, electronics)
    accident_history: float      # 0-100 (no accidents=100, major=0)
    service_history: float       # 0-100 (regular service=100, none=50)
    fraud_indicators: float      # 0-100 (no fraud=100, high fraud=0)
    market_appeal: float         # 0-100 (popular model/color=100)
```

**Persona-Specific Weights**:
```python
PERSONA_WEIGHTS = {
    "Lender": {
        "mechanical_condition": 0.40,
        "exterior_condition": 0.30,
        "fraud_indicators": 0.20,
        "service_history": 0.10
    },
    "Insurer": {
        "accident_history": 0.35,
        "mechanical_condition": 0.30,
        "fraud_indicators": 0.25,
        "exterior_condition": 0.10
    },
    "Broker": {
        "exterior_condition": 0.45,
        "mechanical_condition": 0.25,
        "market_appeal": 0.20,
        "fraud_indicators": 0.10
    }
}

def calculate_health_score(components: HealthScoreComponents, 
                          persona: str,
                          fraud_confidence: float) -> float:
    weights = PERSONA_WEIGHTS[persona]
    
    score = sum(
        getattr(components, component) * weight
        for component, weight in weights.items()
    )
    
    # Fraud gate logic
    if fraud_confidence > 60:
        score = min(score, 30)
    
    return round(score, 2)
```

**Component Calculation**:
```python
def calculate_mechanical_condition(damage_detections: List[DamageDetection],
                                   odometer_reading: int,
                                   service_records: List[ServiceRecord]) -> float:
    base_score = 100.0
    
    # Deduct for damage
    for damage in damage_detections:
        if damage.class_name in ["engine_issue", "transmission_issue"]:
            if damage.severity == "severe": base_score -= 30
            elif damage.severity == "moderate": base_score -= 15
            else: base_score -= 5
    
    # Deduct for high mileage
    if odometer_reading > 150000:
        base_score -= (odometer_reading - 150000) / 10000 * 2
    
    # Bonus for recent service
    if service_records and service_records[-1].date > (datetime.now() - timedelta(days=180)):
        base_score += 5
    
    return max(0, min(100, base_score))

def calculate_exterior_condition(damage_detections: List[DamageDetection]) -> float:
    base_score = 100.0
    
    for damage in damage_detections:
        if damage.class_name in ["dent", "scratch", "rust", "paint_damage"]:
            if damage.severity == "severe": base_score -= 20
            elif damage.severity == "moderate": base_score -= 10
            else: base_score -= 3
    
    return max(0, min(100, base_score))
```

**API Interface**:
```python
class HealthScoreRequest(BaseModel):
    components: HealthScoreComponents
    persona: str
    fraud_confidence: float
    damage_detections: List[DamageDetection]
    odometer_reading: int

class HealthScoreResponse(BaseModel):
    health_score: float  # 0-100
    component_breakdown: Dict[str, float]
    fraud_gate_triggered: bool
    manual_review_required: bool
    explanation: List[str]
```

## Data Models

### Database Schema

**Postgres + pgvector Schema**:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users and authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Assessor', 'Lender', 'Insurer', 'Broker', 'Admin')),
    organization_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Vehicle registry (seeded data)
CREATE TABLE vehicle_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    variant VARCHAR(100),
    fuel_type VARCHAR(50),
    transmission VARCHAR(50),
    base_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vehicle_registry_lookup ON vehicle_registry(make, model, year);

-- Comparable vehicles with embeddings
CREATE TABLE comparable_vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    variant VARCHAR(100),
    fuel_type VARCHAR(50),
    transmission VARCHAR(50),
    mileage INT,
    price DECIMAL(10, 2) NOT NULL,
    location VARCHAR(100),
    listing_date TIMESTAMP,
    listing_url TEXT,
    vin VARCHAR(17),
    embedding vector(1024),  -- pgvector type
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_comparable_embedding ON comparable_vehicles 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_comparable_lookup ON comparable_vehicles(make, model, year);
```

```sql
-- Assessment records (immutable audit trail)
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    vin VARCHAR(17) NOT NULL,
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    variant VARCHAR(100),
    fuel_type VARCHAR(50),
    transmission VARCHAR(50),
    mileage INT NOT NULL,
    location VARCHAR(100),
    odometer_reading INT,
    registration_number VARCHAR(50),
    
    -- AI outputs
    fraud_confidence DECIMAL(5, 2),
    fraud_signals JSONB,
    health_score DECIMAL(5, 2),
    health_components JSONB,
    predicted_price JSONB,  -- {p10, p50, p90, persona_value}
    damage_detections JSONB,
    comparable_ids UUID[],
    
    -- Status and metadata
    status VARCHAR(50) DEFAULT 'processing',
    persona VARCHAR(50),
    fraud_gate_triggered BOOLEAN DEFAULT FALSE,
    manual_review_required BOOLEAN DEFAULT FALSE,
    processing_time_ms INT,
    
    -- Outcome pairing
    actual_transaction_price DECIMAL(10, 2),
    transaction_date TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_assessments_user ON assessments(user_id);
CREATE INDEX idx_assessments_vin ON assessments(vin);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_assessments_fraud ON assessments(fraud_gate_triggered) WHERE fraud_gate_triggered = TRUE;
CREATE INDEX idx_assessments_created ON assessments(created_at DESC);
```

```sql
-- Photos storage metadata
CREATE TABLE assessment_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES assessments(id),
    angle VARCHAR(50) NOT NULL,
    storage_path TEXT NOT NULL,  -- S3/Supabase Storage path
    quality_passed BOOLEAN,
    quality_feedback JSONB,
    ocr_results JSONB,
    damage_detections JSONB,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_photos_assessment ON assessment_photos(assessment_id);

-- Manual review queue
CREATE TABLE manual_review_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES assessments(id),
    priority VARCHAR(20) DEFAULT 'standard',  -- 'high', 'standard'
    reason VARCHAR(255),
    assigned_to UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    review_notes TEXT,
    override_values JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

CREATE INDEX idx_review_queue_status ON manual_review_queue(status, priority, created_at);

-- Fraud cases (for model training)
CREATE TABLE fraud_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES assessments(id),
    fraud_type VARCHAR(100) NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    evidence JSONB,
    reported_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Benchmarking metrics
CREATE TABLE benchmarking_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_date DATE NOT NULL,
    overall_mape DECIMAL(5, 2),
    mape_by_category JSONB,
    mape_by_age JSONB,
    mape_by_price_range JSONB,
    dataset_size INT,
    assessments_with_outcomes INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_metrics_date ON benchmarking_metrics(metric_date DESC);
```

```sql
-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service VARCHAR(50) NOT NULL,  -- 'groq', 'together_ai', 'paddleocr'
    endpoint VARCHAR(100),
    request_count INT DEFAULT 1,
    error_count INT DEFAULT 0,
    fallback_triggered BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_usage_service ON api_usage(service, timestamp);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_log(user_id, timestamp DESC);
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);
```

### Pydantic Models

**Core Domain Models**:

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ASSESSOR = "Assessor"
    LENDER = "Lender"
    INSURER = "Insurer"
    BROKER = "Broker"
    ADMIN = "Admin"

class Persona(str, Enum):
    LENDER = "Lender"
    INSURER = "Insurer"
    BROKER = "Broker"
```

```python
class VehicleAttributes(BaseModel):
    make: str
    model: str
    year: int = Field(ge=1990, le=2024)
    variant: Optional[str]
    fuel_type: str  # "Petrol", "Diesel", "CNG", "Electric"
    transmission: str  # "Manual", "Automatic"
    mileage: int = Field(ge=0, le=999999)
    location: str
    vin: str = Field(min_length=17, max_length=17)
    registration_number: str

class FraudSignal(BaseModel):
    signal_type: str
    confidence: float = Field(ge=0, le=100)
    evidence: List[str]
    severity: str  # "low", "medium", "high"

class FraudDetectionResult(BaseModel):
    fraud_confidence: float = Field(ge=0, le=100)
    signals: List[FraudSignal]
    fraud_gate_triggered: bool
    recommended_action: str
    processing_time_ms: int

class DamageDetection(BaseModel):
    class_name: str
    confidence: float = Field(ge=0, le=1)
    bbox: List[int] = Field(min_items=4, max_items=4)
    severity: str  # "minor", "moderate", "severe"

class HealthScoreComponents(BaseModel):
    mechanical_condition: float = Field(ge=0, le=100)
    exterior_condition: float = Field(ge=0, le=100)
    interior_condition: float = Field(ge=0, le=100)
    accident_history: float = Field(ge=0, le=100)
    service_history: float = Field(ge=0, le=100)
    fraud_indicators: float = Field(ge=0, le=100)
    market_appeal: float = Field(ge=0, le=100)

class HealthScoreResult(BaseModel):
    health_score: float = Field(ge=0, le=100)
    component_breakdown: Dict[str, float]
    fraud_gate_triggered: bool
    manual_review_required: bool
    explanation: List[str]
```

```python
class ComparableVehicle(BaseModel):
    id: str
    make: str
    model: str
    year: int
    mileage: int
    price: float
    similarity_score: float = Field(ge=0, le=1)
    listing_date: datetime
    key_differences: List[str]

class PricePrediction(BaseModel):
    base_price: float
    adjusted_price: float
    p10: float
    p50: float
    p90: float
    persona_value: float
    comparables: List[ComparableVehicle]
    explanation: Dict[str, Any]
    processing_time_ms: int

class AssessmentRecord(BaseModel):
    id: str
    user_id: str
    vehicle: VehicleAttributes
    fraud_result: FraudDetectionResult
    health_result: HealthScoreResult
    price_prediction: PricePrediction
    damage_detections: List[DamageDetection]
    status: str
    persona: Persona
    processing_time_ms: int
    created_at: datetime
    completed_at: Optional[datetime]
    actual_transaction_price: Optional[float]
    transaction_date: Optional[datetime]

class AssessmentStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"
```

### Redis Data Structures

**Queue Management**:
```python
# Assessment processing queue
QUEUE_KEY = "vehicleiq:assessments:queue"
# List structure: LPUSH for enqueue, RPOP for dequeue

# Photo hash cache (for reuse detection)
PHOTO_HASH_KEY = "vehicleiq:photos:hashes:{hash}"
# String structure: SET with TTL of 90 days

# API rate limiting
RATE_LIMIT_KEY = "vehicleiq:ratelimit:{service}:{date}"
# String structure: INCR with TTL of 24 hours

# Base price cache
PRICE_CACHE_KEY = "vehicleiq:prices:{make}:{model}:{year}"
# String structure: SET with TTL of 24 hours

# Session data
SESSION_KEY = "vehicleiq:session:{user_id}"
# Hash structure: HSET for key-value pairs, TTL of 30 minutes
```

### Assessment State Machine

```
QUEUED → PROCESSING → [COMPLETED | FAILED | MANUAL_REVIEW]
                ↓
         (Pipeline Stages)
         1. photo_validation
         2. ocr_extraction
         3. fraud_detection
         4. damage_analysis
         5. embedding_generation
         6. comparable_retrieval
         7. price_prediction
         8. health_score_calculation
         9. report_generation
         10. audit_trail_creation
```

**State Transitions**:
```python
class AssessmentStateMachine:
    def __init__(self, assessment_id: str):
        self.assessment_id = assessment_id
        self.current_stage = None
    
    async def transition(self, stage: str):
        # Publish status update via Supabase Realtime
        await supabase.from_('assessments').update({
            'status': 'processing',
            'current_stage': stage
        }).eq('id', self.assessment_id).execute()
        
        # Emit real-time event
        await supabase.realtime.send({
            'event': 'assessment_progress',
            'payload': {
                'assessment_id': self.assessment_id,
                'stage': stage,
                'timestamp': datetime.now().isoformat()
            }
        })
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all 30 requirements with 200+ acceptance criteria, I identified testable properties and performed redundancy elimination:

**Redundancies Identified**:
- Properties about "output structure contains field X" can be combined into comprehensive structure validation properties
- Multiple persona-specific weight calculations (5.2, 5.3, 5.4) can be combined into one property about weighted sum correctness
- Fraud gate properties (1.8, 5.5, 5.6) are related and can be consolidated
- Multiple bounds checking properties (fraud score, health score, similarity scores) follow the same pattern
- OCR validation properties (15.6, 15.7) can be combined into general validation property

**Properties Retained After Reflection**:
The following properties provide unique validation value and cannot be subsumed by others.

### Property 1: Fraud Confidence Score Bounds

*For any* fraud detection result, the fraud confidence score SHALL be between 0 and 100 inclusive.

**Validates: Requirements 1.7**

### Property 2: Fraud Gate Consistency

*For any* assessment where fraud confidence score exceeds 60, the fraud gate SHALL be triggered AND the health score SHALL be capped at 30 AND the assessment SHALL be added to the manual review queue with high priority.

**Validates: Requirements 1.8, 5.5, 5.6, 11.1**

### Property 3: Fraud Detection Output Structure

*For any* fraud detection result, it SHALL contain explainable evidence including specific indicators and confidence levels for each signal detected.

**Validates: Requirements 1.9**

### Property 4: Photo Hash Round-Trip

*For any* vehicle photo, computing the perceptual hash twice SHALL produce identical hash values (deterministic hashing).

**Validates: Requirements 1.3**

### Property 5: Price Prediction Monotonicity

*For any* two vehicles with identical attributes except health score, IF health_score_A > health_score_B, THEN adjusted_price_A >= adjusted_price_B.

**Validates: Requirements 2.2**

### Property 6: Quantile Ordering

*For any* price prediction result, the quantile values SHALL satisfy P10 <= P50 <= P90.

**Validates: Requirements 2.4**

### Property 7: Persona-Specific Value Bounds

*For any* price prediction with Lender persona, FSV SHALL be <= P10.
*For any* price prediction with Broker persona, asking_price SHALL be >= P90.

**Validates: Requirements 2.6, 2.8**

### Property 8: Price Prediction Explainability

*For any* price prediction result, it SHALL contain explanation fields including base price, adjustments, and comparable vehicles used.

**Validates: Requirements 2.10**

### Property 9: Comparable Retrieval Count and Ordering

*For any* comparable vehicle search, the results SHALL contain at most 10 vehicles AND SHALL be ordered by similarity score in descending order AND all similarity scores SHALL be between 0 and 1.

**Validates: Requirements 2.3, 9.3**

### Property 10: MAPE Calculation Correctness

*For any* set of predicted prices and actual prices, MAPE SHALL equal mean(|predicted - actual| / actual) × 100.

**Validates: Requirements 3.3**

### Property 11: Market Data Validation

*For any* market data record with missing required fields (make, model, year, price, mileage, listing_date), the record SHALL be rejected with validation error details.

**Validates: Requirements 3.6, 23.3**

### Property 12: Embedding Generation for New Records

*For any* new comparable vehicle record added to the dataset, it SHALL have an associated embedding vector with exactly 1024 dimensions.

**Validates: Requirements 3.10, 16.4**

### Property 13: Quality Gate Validation Structure

*For any* photo processed through quality gate, the result SHALL contain checks for blur, lighting, framing, and resolution with pass/fail status and feedback.

**Validates: Requirements 4.3**

### Property 14: Quality Gate Rejection with Feedback

*For any* photo that fails quality gate validation, it SHALL be rejected AND specific feedback SHALL be provided indicating which checks failed.

**Validates: Requirements 4.4**

### Property 15: Photo Collection Completeness

*For any* assessment where all 13 required photo angles pass quality gate validation, the photo collection SHALL be marked as complete.

**Validates: Requirements 4.9**

### Property 16: Damage Detection Output Structure

*For any* damage detection result, each detected damage SHALL contain class_name, confidence score, bounding box coordinates, and severity classification.

**Validates: Requirements 4.10, 17.3**

### Property 17: Health Score Bounds

*For any* health score calculation, the result SHALL be between 0 and 100 inclusive.

**Validates: Requirements 5.1**

### Property 18: Health Score Weighted Sum Correctness

*For any* health score calculation with persona P, the health score (before fraud gate) SHALL equal the weighted sum of components using the weights defined for persona P.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 19: Low Health Score Manual Review

*For any* assessment with health score below 40, the assessment SHALL be flagged for manual review.

**Validates: Requirements 5.7, 11.2**

### Property 20: Health Score Explainability

*For any* health score result, it SHALL contain a component breakdown showing the contribution of each component to the final score.

**Validates: Requirements 5.9**

### Property 21: User Role Uniqueness

*For any* authenticated user, they SHALL have exactly one primary role assigned.

**Validates: Requirements 6.2**

### Property 22: Role-Based Access Control

*For any* user with role R attempting to access feature F, IF F is not in the permitted features for role R, THEN access SHALL be denied with an error message AND the attempt SHALL be logged.

**Validates: Requirements 6.8, 6.9**

### Property 23: Pipeline Stage Ordering

*For any* assessment processing, the pipeline stages SHALL be executed in the defined sequence: photo validation, OCR extraction, fraud detection, damage analysis, embedding generation, comparable retrieval, price prediction, health score calculation, report generation, audit trail creation.

**Validates: Requirements 7.4**

### Property 24: Pipeline Failure Handling

*For any* pipeline stage that fails, processing SHALL halt immediately AND a descriptive error message SHALL be returned.

**Validates: Requirements 7.5**

### Property 25: Assessment Record Creation

*For any* successfully completed assessment, an immutable Assessment_Record SHALL be created containing all required fields: user_id, vehicle attributes, fraud results, health score, price prediction, damage detections, status, persona, timestamps.

**Validates: Requirements 7.6, 8.1**

### Property 26: Assessment Record Immutability

*For any* Assessment_Record, once created, the core assessment data (vehicle attributes, AI outputs, timestamps) SHALL remain unchanged. Only append-only fields (review notes, override values) MAY be modified.

**Validates: Requirements 8.2, 8.6**

### Property 27: Assessment ID Uniqueness

*For any* two Assessment_Records, they SHALL have different unique identifiers.

**Validates: Requirements 8.3**

### Property 28: Fraud Indicator Linkage

*For any* assessment where fraud is detected (fraud_confidence > 0), the Assessment_Record SHALL contain the fraud indicators and signals.

**Validates: Requirements 8.5**

### Property 29: Embedding Generation Determinism

*For any* vehicle with identical attributes, generating embeddings multiple times SHALL produce identical embedding vectors.

**Validates: Requirements 16.8**

### Property 30: Embedding Round-Trip

*For any* vehicle record, generating an embedding vector then performing similarity search SHALL return the original vehicle as the top result with similarity score >= 0.99.

**Validates: Requirements 16.7**

### Property 31: Comparable Constraint Satisfaction

*For any* comparable vehicle returned in search results, it SHALL satisfy the constraints: same make and model, year within ±2 years (or ±3 if relaxed), mileage within ±20k km (or ±30k if relaxed).

**Validates: Requirements 9.4**

### Property 32: Comparable Constraint Relaxation

*For any* comparable search that returns fewer than 5 results with strict constraints, the constraints SHALL be relaxed (year ±3, mileage ±30k) and search SHALL be retried.

**Validates: Requirements 9.6**

### Property 33: Comparable Explainability

*For any* comparable vehicle in search results, it SHALL include similarity score, listing price, listing date, and key attribute differences.

**Validates: Requirements 9.5, 9.8**

### Property 34: Persona-Specific Report Structure

*For any* report generated with Lender persona, it SHALL contain FSV, health score, fraud indicators, and loan-to-value recommendations.
*For any* report generated with Insurer persona, it SHALL contain IDV, accident history, claim cross-match results, and underwriting risk factors.
*For any* report generated with Broker persona, it SHALL contain asking price, market positioning, and comparable listings.

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 35: Report Export Format Support

*For any* generated report, it SHALL be exportable to both PDF and JSON formats.

**Validates: Requirements 10.6**

### Property 36: Fraud Highlighting in Reports

*For any* report where fraud indicators are present (fraud_confidence > 0), the fraud indicators SHALL be prominently highlighted in the report.

**Validates: Requirements 10.8**

### Property 37: Manual Review Queue Sorting

*For any* manual review queue view, assessments SHALL be sorted first by priority (high before standard) then by submission time (oldest first).

**Validates: Requirements 11.3**

### Property 38: Manual Review Approval State Transition

*For any* assessment approved by admin, it SHALL be marked as reviewed AND removed from the manual review queue.

**Validates: Requirements 11.5**

### Property 39: Manual Review Override Recording

*For any* assessment overridden by admin, the Assessment_Record SHALL contain the override reason and adjusted values.

**Validates: Requirements 11.6**

### Property 40: Queue Notification Threshold

*For any* manual review queue state where the count exceeds 20 pending items, a notification SHALL be sent to admin users.

**Validates: Requirements 11.7**

### Property 41: API Request Tracking

*For any* API call to Groq or Together.ai, the request count SHALL be incremented in the usage tracking system.

**Validates: Requirements 14.1**

### Property 42: API Fallback Triggering

*For any* API request when the rate limit for the primary service (Groq) is exceeded, the system SHALL automatically fallback to the secondary service (Together.ai) AND log the fallback event.

**Validates: Requirements 14.2, 14.5**

### Property 43: API Fallback Transparency

*For any* assessment processed via fallback API, processing SHALL continue without user-visible errors AND the output format SHALL match the primary API output format.

**Validates: Requirements 14.6**

### Property 44: OCR Validation Bounds Checking

*For any* OCR extraction of odometer reading, IF the value is outside the range 0-999999, THEN it SHALL be flagged for manual verification.
*For any* OCR extraction of VIN, IF it does not match the 17-character alphanumeric format, THEN it SHALL be flagged for manual verification.

**Validates: Requirements 15.6, 15.7**

### Property 45: OCR Round-Trip

*For any* OCR extraction result, pretty-printing the data then parsing it back SHALL produce data equivalent to the original extraction.

**Validates: Requirements 15.9**

### Property 46: Embedding Attribute Concatenation Consistency

*For any* vehicle attributes, the concatenation order for embedding generation SHALL be consistent: make, model, year, variant, fuel_type, transmission, mileage, location.

**Validates: Requirements 16.2**

### Property 47: Row-Level Security

*For any* user attempting to access an assessment, IF the assessment does not belong to the user's organization, THEN access SHALL be denied.

**Validates: Requirements 20.4**

### Property 48: Upload Retry Logic

*For any* photo upload that fails, the system SHALL retry up to 3 times with exponential backoff before reporting failure to the user.

**Validates: Requirements 21.1**

### Property 49: Batch Processing Completeness

*For any* batch assessment request with N valid records, the system SHALL produce exactly N assessment results (each marked as success or failure).

**Validates: Requirements 22.8**

### Property 50: Market Data Deduplication

*For any* incoming market data record, IF a record with the same VIN or listing_url already exists, THEN the new record SHALL be rejected as a duplicate.

**Validates: Requirements 23.4**

### Property 51: Notification Rate Limiting

*For any* user, the number of notifications delivered within any 1-hour window SHALL NOT exceed 10.

**Validates: Requirements 25.7**

## Error Handling

### Error Categories

**1. Validation Errors** (HTTP 400)
- Invalid vehicle attributes (year out of range, invalid VIN format)
- Missing required fields
- Invalid photo format or size
- Malformed request payloads

**2. Authentication/Authorization Errors** (HTTP 401/403)
- Invalid or expired JWT token
- Insufficient permissions for requested operation
- Row-level security violations

**3. Resource Not Found Errors** (HTTP 404)
- Assessment ID not found
- User not found
- Comparable vehicle not found

**4. Rate Limiting Errors** (HTTP 429)
- API rate limit exceeded (with automatic fallback)
- User request rate limit exceeded

**5. External Service Errors** (HTTP 502/503)
- Groq API unavailable (triggers fallback to Together.ai)
- PaddleOCR service timeout
- YOLOv8n service failure
- Database connection lost

**6. Processing Errors** (HTTP 500)
- Pipeline stage failure
- Embedding generation failure
- Price prediction calculation error
- Report generation failure

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error_id: str  # Unique identifier for support reference
    error_code: str  # Machine-readable error code
    message: str  # User-friendly error message
    details: Optional[Dict[str, Any]]  # Additional context
    timestamp: datetime
    retry_after: Optional[int]  # Seconds to wait before retry (for rate limiting)

# Example error responses
{
    "error_id": "err_a1b2c3d4",
    "error_code": "INVALID_VIN_FORMAT",
    "message": "VIN must be exactly 17 alphanumeric characters",
    "details": {"provided_vin": "ABC123", "expected_length": 17},
    "timestamp": "2024-01-15T10:30:00Z"
}

{
    "error_id": "err_e5f6g7h8",
    "error_code": "API_RATE_LIMIT_EXCEEDED",
    "message": "Groq API rate limit exceeded, automatically falling back to Together.ai",
    "details": {"service": "groq", "fallback": "together_ai"},
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Retry Strategy

**Exponential Backoff**:
```python
def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, 0.1 * delay)  # Add jitter to prevent thundering herd
    return delay + jitter

# Photo upload retry
for attempt in range(3):
    try:
        upload_photo(photo_data)
        break
    except UploadError:
        if attempt < 2:
            time.sleep(exponential_backoff(attempt))
        else:
            raise
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Service temporarily unavailable")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

# Usage for external API calls
groq_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def call_groq_api(prompt: str):
    return groq_circuit_breaker.call(groq_client.chat.completions.create, ...)
```

### Progress Preservation

```python
# Save assessment progress to browser localStorage every 30 seconds
class AssessmentProgressManager:
    def save_progress(self, assessment_id: str, data: Dict[str, Any]):
        progress_key = f"assessment_progress_{assessment_id}"
        localStorage.setItem(progress_key, json.dumps({
            "data": data,
            "timestamp": datetime.now().isoformat()
        }))
    
    def restore_progress(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        progress_key = f"assessment_progress_{assessment_id}"
        saved = localStorage.getItem(progress_key)
        if saved:
            progress = json.loads(saved)
            # Only restore if less than 24 hours old
            if datetime.fromisoformat(progress["timestamp"]) > datetime.now() - timedelta(hours=24):
                return progress["data"]
        return None
```

## Testing Strategy

### Dual Testing Approach

VehicleIQ employs a comprehensive testing strategy combining unit tests and property-based tests:

**Unit Tests**: Verify specific examples, edge cases, error conditions, and integration points
**Property Tests**: Verify universal properties across all inputs using randomized test data

Both approaches are complementary and necessary for comprehensive coverage. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Property-Based Testing Configuration

**Library Selection**:
- **Python Backend**: Hypothesis (https://hypothesis.readthedocs.io/)
- **TypeScript Frontend**: fast-check (https://github.com/dubzzz/fast-check)

**Configuration**:
```python
# Python: Hypothesis configuration
from hypothesis import given, settings, strategies as st

@settings(max_examples=100)  # Minimum 100 iterations per property test
@given(
    fraud_confidence=st.floats(min_value=0, max_value=100),
    health_score=st.floats(min_value=0, max_value=100)
)
def test_fraud_gate_consistency(fraud_confidence, health_score):
    """
    Feature: vehicle-iq, Property 2: Fraud Gate Consistency
    For any assessment where fraud confidence score exceeds 60,
    the fraud gate SHALL be triggered AND the health score SHALL be capped at 30.
    """
    result = calculate_health_score_with_fraud_gate(health_score, fraud_confidence)
    
    if fraud_confidence > 60:
        assert result.fraud_gate_triggered == True
        assert result.final_health_score <= 30
        assert result.manual_review_required == True
```

```typescript
// TypeScript: fast-check configuration
import fc from 'fast-check';

test('Property 6: Quantile Ordering', () => {
  /**
   * Feature: vehicle-iq, Property 6: Quantile Ordering
   * For any price prediction result, P10 <= P50 <= P90.
   */
  fc.assert(
    fc.property(
      fc.record({
        basePrice: fc.float({ min: 100000, max: 10000000 }),
        healthScore: fc.float({ min: 0, max: 100 }),
        comparables: fc.array(fc.float({ min: 100000, max: 10000000 }), { minLength: 5, maxLength: 10 })
      }),
      (input) => {
        const prediction = calculatePricePrediction(input);
        expect(prediction.p10).toBeLessThanOrEqual(prediction.p50);
        expect(prediction.p50).toBeLessThanOrEqual(prediction.p90);
      }
    ),
    { numRuns: 100 }  // Minimum 100 iterations
  );
});
```

### Property Test Coverage

Each of the 51 correctness properties defined in this design SHALL be implemented as a property-based test with the following tag format:

```python
"""
Feature: vehicle-iq, Property {number}: {property_title}
{property_statement}
"""
```

### Unit Test Strategy

**Unit tests focus on**:
1. **Specific Examples**: Concrete test cases with known inputs and expected outputs
2. **Edge Cases**: Boundary conditions, empty inputs, maximum values
3. **Error Conditions**: Invalid inputs, missing data, malformed requests
4. **Integration Points**: API endpoints, database operations, external service calls

**Example Unit Tests**:

```python
# Example: Fraud detection with specific VIN clone scenario
def test_vin_clone_detection_specific_case():
    """Test VIN clone detection with known duplicate VIN"""
    # Setup: Insert vehicle with VIN "1HGBH41JXMN109186"
    existing_vehicle = create_test_vehicle(vin="1HGBH41JXMN109186")
    
    # Test: Submit assessment with same VIN
    result = fraud_detection_engine.check_vin_clone("1HGBH41JXMN109186")
    
    # Assert: VIN clone detected
    assert result.signal_type == "vin_clone"
    assert result.confidence > 90
    assert "duplicate VIN found" in result.evidence

# Example: Price prediction with zero health score (edge case)
def test_price_prediction_zero_health_score():
    """Test price prediction with minimum health score"""
    vehicle = VehicleAttributes(
        make="Maruti", model="Swift", year=2020,
        health_score=0, mileage=50000
    )
    
    prediction = price_prediction_ml.predict(vehicle)
    
    # With health_score=0, adjustment multiplier should be 0.70
    expected_adjusted = prediction.base_price * 0.70
    assert abs(prediction.adjusted_price - expected_adjusted) < 100

# Example: OCR extraction error handling
def test_ocr_extraction_invalid_image():
    """Test OCR extraction with corrupted image"""
    corrupted_image = b"not_a_valid_image"
    
    with pytest.raises(OCRExtractionError) as exc_info:
        image_intelligence_api.extract_odometer(corrupted_image)
    
    assert "invalid image format" in str(exc_info.value).lower()
```

### Integration Testing

**API Endpoint Tests**:
```python
# Test complete assessment pipeline
def test_assessment_pipeline_integration():
    """Integration test for complete assessment workflow"""
    client = TestClient(app)
    
    # 1. Upload photos
    photos = [create_test_photo(angle) for angle in REQUIRED_ANGLES]
    for photo in photos:
        response = client.post("/api/photos/upload", files={"file": photo})
        assert response.status_code == 200
    
    # 2. Submit assessment
    assessment_data = {
        "vin": "1HGBH41JXMN109186",
        "make": "Maruti", "model": "Swift", "year": 2020,
        "mileage": 50000, "persona": "Lender"
    }
    response = client.post("/api/assessments", json=assessment_data)
    assert response.status_code == 201
    assessment_id = response.json()["id"]
    
    # 3. Poll for completion
    for _ in range(30):  # Wait up to 90 seconds
        response = client.get(f"/api/assessments/{assessment_id}")
        if response.json()["status"] == "completed":
            break
        time.sleep(3)
    
    # 4. Verify results
    result = response.json()
    assert result["status"] == "completed"
    assert "fraud_confidence" in result
    assert "health_score" in result
    assert "price_prediction" in result
    assert result["processing_time_ms"] < 90000
```

### Test Coverage Requirements

- **Minimum 80% code coverage** for unit tests
- **100% property coverage** - all 51 properties implemented as property-based tests
- **Integration tests** for all API endpoints
- **End-to-end tests** for critical user workflows (assessment submission, manual review)

### Test Data Generation

**Hypothesis Strategies for Domain Models**:
```python
from hypothesis import strategies as st

# Vehicle attributes strategy
vehicle_attributes = st.builds(
    VehicleAttributes,
    make=st.sampled_from(["Maruti", "Hyundai", "Tata", "Honda", "Toyota"]),
    model=st.text(min_size=3, max_size=20),
    year=st.integers(min_value=2010, max_value=2024),
    variant=st.text(min_size=2, max_size=30),
    fuel_type=st.sampled_from(["Petrol", "Diesel", "CNG", "Electric"]),
    transmission=st.sampled_from(["Manual", "Automatic"]),
    mileage=st.integers(min_value=0, max_value=300000),
    location=st.sampled_from(["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]),
    vin=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Nd")), min_size=17, max_size=17),
    registration_number=st.text(min_size=8, max_size=12)
)

# Fraud signal strategy
fraud_signal = st.builds(
    FraudSignal,
    signal_type=st.sampled_from(["vin_clone", "odometer_rollback", "photo_reuse", "flood_damage"]),
    confidence=st.floats(min_value=0, max_value=100),
    evidence=st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=5),
    severity=st.sampled_from(["low", "medium", "high"])
)

# Damage detection strategy
damage_detection = st.builds(
    DamageDetection,
    class_name=st.sampled_from(["dent", "scratch", "rust", "crack", "missing_part"]),
    confidence=st.floats(min_value=0.5, max_value=1.0),
    bbox=st.lists(st.integers(min_value=0, max_value=1920), min_size=4, max_size=4),
    severity=st.sampled_from(["minor", "moderate", "severe"])
)
```

## API Design

### REST API Endpoints

**Base URL**: 
- Cloud: `https://api.vehicleiq.com/v1`
- Local: `http://localhost:8000/v1`

**Authentication**: JWT Bearer token in Authorization header

#### Assessment Endpoints

```
POST /assessments
Create new assessment

Request:
{
  "vin": "1HGBH41JXMN109186",
  "make": "Maruti",
  "model": "Swift",
  "year": 2020,
  "variant": "VXI",
  "fuel_type": "Petrol",
  "transmission": "Manual",
  "mileage": 50000,
  "location": "Mumbai",
  "registration_number": "MH01AB1234",
  "persona": "Lender"
}

Response: 201 Created
{
  "id": "ast_a1b2c3d4",
  "status": "queued",
  "estimated_completion_time": "2024-01-15T10:32:30Z",
  "created_at": "2024-01-15T10:31:00Z"
}

---

GET /assessments/{assessment_id}
Get assessment status and results

Response: 200 OK
{
  "id": "ast_a1b2c3d4",
  "status": "completed",
  "vehicle": {...},
  "fraud_result": {...},
  "health_result": {...},
  "price_prediction": {...},
  "damage_detections": [...],
  "processing_time_ms": 68234,
  "completed_at": "2024-01-15T10:32:08Z"
}

---

GET /assessments
List assessments with filtering

Query params:
- status: queued|processing|completed|failed|manual_review
- persona: Lender|Insurer|Broker
- fraud_flagged: true|false
- date_from: ISO 8601 date
- date_to: ISO 8601 date
- page: int (default 1)
- page_size: int (default 20, max 100)

Response: 200 OK
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

#### Photo Endpoints

```
POST /photos/upload
Upload vehicle photo

Request: multipart/form-data
- file: image file (JPEG/PNG, max 10MB)
- assessment_id: string
- angle: string (one of 13 required angles)

Response: 200 OK
{
  "id": "pht_e5f6g7h8",
  "assessment_id": "ast_a1b2c3d4",
  "angle": "front_view",
  "quality_result": {
    "passed": true,
    "blur_score": 0.92,
    "lighting_score": 0.88,
    "framing_score": 0.95
  },
  "storage_path": "assessments/ast_a1b2c3d4/front_view.jpg"
}

---

GET /photos/{photo_id}
Get photo metadata and signed URL

Response: 200 OK
{
  "id": "pht_e5f6g7h8",
  "assessment_id": "ast_a1b2c3d4",
  "angle": "front_view",
  "signed_url": "https://storage.vehicleiq.com/...",
  "expires_at": "2024-01-15T11:31:00Z",
  "ocr_results": {...},
  "damage_detections": [...]
}
```

#### Fraud Detection Endpoints

```
POST /fraud/detect
Run fraud detection on vehicle data

Request:
{
  "vin": "1HGBH41JXMN109186",
  "photos": ["pht_e5f6g7h8", "pht_i9j0k1l2"],
  "documents": ["doc_m3n4o5p6"],
  "odometer_reading": 50000,
  "registration_number": "MH01AB1234"
}

Response: 200 OK
{
  "fraud_confidence": 35.5,
  "signals": [
    {
      "signal_type": "odometer_rollback",
      "confidence": 45.0,
      "evidence": ["Digital display inconsistency detected"],
      "severity": "medium"
    }
  ],
  "fraud_gate_triggered": false,
  "recommended_action": "approve",
  "processing_time_ms": 1850
}
```

#### Price Prediction Endpoints

```
POST /price/predict
Calculate price prediction

Request:
{
  "make": "Maruti",
  "model": "Swift",
  "year": 2020,
  "variant": "VXI",
  "fuel_type": "Petrol",
  "transmission": "Manual",
  "mileage": 50000,
  "location": "Mumbai",
  "health_score": 75.5,
  "persona": "Lender"
}

Response: 200 OK
{
  "base_price": 550000,
  "adjusted_price": 585000,
  "p10": 520000,
  "p50": 585000,
  "p90": 650000,
  "persona_value": 494000,
  "comparables": [
    {
      "id": "cmp_q7r8s9t0",
      "make": "Maruti",
      "model": "Swift",
      "year": 2020,
      "mileage": 48000,
      "price": 580000,
      "similarity_score": 0.96,
      "listing_date": "2024-01-10T00:00:00Z",
      "key_differences": ["Mileage: 2000 km less"]
    }
  ],
  "explanation": {
    "base_price_source": "Market data average for Maruti Swift 2020 VXI",
    "condition_adjustment": "Health score 75.5 → 1.06x multiplier",
    "persona_adjustment": "Lender FSV = P10 × 0.95"
  },
  "processing_time_ms": 4250
}
```

#### Manual Review Endpoints

```
GET /manual-review/queue
Get manual review queue

Query params:
- priority: high|standard
- status: pending|in_progress|completed

Response: 200 OK
{
  "items": [
    {
      "id": "rev_u1v2w3x4",
      "assessment_id": "ast_a1b2c3d4",
      "priority": "high",
      "reason": "Fraud confidence score 75.5 exceeds threshold",
      "created_at": "2024-01-15T10:32:08Z",
      "status": "pending"
    }
  ],
  "total": 15
}

---

POST /manual-review/{review_id}/approve
Approve assessment

Response: 200 OK
{
  "id": "rev_u1v2w3x4",
  "status": "completed",
  "reviewed_by": "usr_y5z6a7b8",
  "reviewed_at": "2024-01-15T11:00:00Z"
}

---

POST /manual-review/{review_id}/override
Override assessment values

Request:
{
  "reason": "Odometer reading verified manually",
  "adjusted_values": {
    "fraud_confidence": 15.0,
    "health_score": 80.0
  }
}

Response: 200 OK
{
  "id": "rev_u1v2w3x4",
  "status": "completed",
  "override_applied": true,
  "reviewed_by": "usr_y5z6a7b8",
  "reviewed_at": "2024-01-15T11:00:00Z"
}
```

#### Benchmarking Endpoints

```
POST /benchmarking/market-data
Ingest external market data

Request:
{
  "records": [
    {
      "make": "Maruti",
      "model": "Swift",
      "year": 2020,
      "variant": "VXI",
      "fuel_type": "Petrol",
      "transmission": "Manual",
      "mileage": 52000,
      "price": 575000,
      "location": "Mumbai",
      "listing_date": "2024-01-14T00:00:00Z",
      "listing_url": "https://example.com/listing/123"
    }
  ]
}

Response: 201 Created
{
  "accepted": 1,
  "rejected": 0,
  "duplicates": 0,
  "errors": []
}

---

POST /benchmarking/outcome-pairing
Pair assessment with actual transaction price

Request:
{
  "assessment_id": "ast_a1b2c3d4",
  "actual_transaction_price": 580000,
  "transaction_date": "2024-01-20T00:00:00Z",
  "source": "manual"
}

Response: 200 OK
{
  "assessment_id": "ast_a1b2c3d4",
  "predicted_price": 585000,
  "actual_price": 580000,
  "error_percentage": 0.86,
  "mape_updated": true
}

---

GET /benchmarking/metrics
Get benchmarking metrics

Response: 200 OK
{
  "overall_mape": 4.2,
  "mape_by_category": {
    "sedan": 3.8,
    "suv": 4.5,
    "hatchback": 4.1
  },
  "mape_by_age": {
    "0-3_years": 3.5,
    "3-5_years": 4.2,
    "5+_years": 5.1
  },
  "dataset_size": 2150,
  "assessments_with_outcomes": 523,
  "last_updated": "2024-01-15T10:00:00Z"
}
```

### WebSocket / Realtime Subscriptions

**Supabase Realtime for Assessment Progress**:

```typescript
// Frontend: Subscribe to assessment progress
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const channel = supabase
  .channel('assessment-progress')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'assessments',
      filter: `id=eq.${assessmentId}`
    },
    (payload) => {
      console.log('Assessment updated:', payload.new);
      updateUI(payload.new);
    }
  )
  .subscribe();

// Backend: Publish progress update
await supabase
  .from('assessments')
  .update({
    status: 'processing',
    current_stage: 'fraud_detection',
    progress_percentage: 40
  })
  .eq('id', assessment_id);
```

### Webhook Integration

**Outcome Pairing Webhook**:

```
POST https://your-server.com/webhooks/vehicleiq/outcome-pairing
Authorization: Bearer {webhook_secret}

Payload:
{
  "event": "transaction.completed",
  "assessment_id": "ast_a1b2c3d4",
  "actual_transaction_price": 580000,
  "transaction_date": "2024-01-20T00:00:00Z",
  "source": "external_system"
}

Expected Response: 200 OK
{
  "received": true,
  "assessment_id": "ast_a1b2c3d4"
}
```

## Deployment

### Environment Variables

**Shared Configuration**:
```bash
# Application
NODE_ENV=production|development
API_BASE_URL=https://api.vehicleiq.com/v1
FRONTEND_URL=https://vehicleiq.com

# Authentication
JWT_SECRET=your-secret-key-here
JWT_EXPIRY=30d

# Database
DATABASE_URL=postgresql://user:pass@host:5432/vehicleiq
DATABASE_POOL_SIZE=20

# Redis/Queue
REDIS_URL=redis://host:6379
QUEUE_CONCURRENCY=10

# Storage
STORAGE_PROVIDER=supabase|s3
STORAGE_BUCKET=vehicleiq-photos
```

**Cloud Deployment (Groq + Together.ai)**:
```bash
# LLM APIs
GROQ_API_KEY=your-groq-api-key
GROQ_RATE_LIMIT=14400  # requests per day
TOGETHER_API_KEY=your-together-api-key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Upstash Redis
UPSTASH_REDIS_URL=your-upstash-redis-url
UPSTASH_REDIS_TOKEN=your-token

# AI Services (cloud endpoints)
PADDLEOCR_URL=https://paddleocr-service.railway.app
YOLO_URL=https://yolo-service.railway.app
EMBEDDINGS_URL=https://embeddings-service.railway.app
```

**Local Docker Deployment**:
```bash
# LLM (local)
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b

# Database (local)
DATABASE_URL=postgresql://vehicleiq:vehicleiq@postgres:5432/vehicleiq

# Redis (local)
REDIS_URL=redis://redis:6379

# AI Services (local containers)
PADDLEOCR_URL=http://paddleocr:8001
YOLO_URL=http://yolo:8002
EMBEDDINGS_URL=http://embeddings:8003

# Storage (local)
STORAGE_PROVIDER=local
STORAGE_PATH=/app/storage
```

### Docker Compose Configuration

**docker-compose.yml** (Local Deployment):

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: vehicleiq
      POSTGRES_USER: vehicleiq
      POSTGRES_PASSWORD: vehicleiq
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vehicleiq"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://vehicleiq:vehicleiq@postgres:5432/vehicleiq
      REDIS_URL: redis://redis:6379
      PADDLEOCR_URL: http://paddleocr:8001
      YOLO_URL: http://yolo:8002
      EMBEDDINGS_URL: http://embeddings:8003
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - storage_data:/app/storage
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://vehicleiq:vehicleiq@postgres:5432/vehicleiq
      REDIS_URL: redis://redis:6379
      PADDLEOCR_URL: http://paddleocr:8001
      YOLO_URL: http://yolo:8002
      EMBEDDINGS_URL: http://embeddings:8003
    depends_on:
      - postgres
      - redis
    command: python -m celery -A worker worker --loglevel=info --concurrency=4
```

  paddleocr:
    build:
      context: ./services/paddleocr
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    volumes:
      - paddleocr_models:/root/.paddleocr
    environment:
      LANG: en,hi
    command: python server.py
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  yolo:
    build:
      context: ./services/yolo
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    volumes:
      - yolo_models:/root/.cache/torch
    command: python server.py
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  embeddings:
    build:
      context: ./services/embeddings
      dockerfile: Dockerfile
    ports:
      - "8003:8003"
    volumes:
      - embeddings_models:/root/.cache/huggingface
    environment:
      MODEL_NAME: BAAI/bge-m3
    command: python server.py
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/v1
      NEXT_PUBLIC_SUPABASE_URL: http://localhost:54321
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
  storage_data:
  paddleocr_models:
  yolo_models:
  embeddings_models:
```

### Cloud Deployment Architecture

**Vercel (Frontend)**:
```bash
# vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.vehicleiq.com/v1",
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase-url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase-anon-key"
  }
}
```

**Railway/Hetzner (Backend)**:
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Supabase Configuration**:
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable Row Level Security
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_photos ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their org's assessments"
  ON assessments FOR SELECT
  USING (
    organization_id = (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  );

CREATE POLICY "Users can insert assessments"
  ON assessments FOR INSERT
  WITH CHECK (
    user_id = auth.uid()
  );

-- Realtime publication
ALTER PUBLICATION supabase_realtime ADD TABLE assessments;
```

### Health Check Endpoints

```python
# Backend health check
@app.get("/health")
async def health_check():
    """System health check"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "paddleocr": await check_service("paddleocr"),
        "yolo": await check_service("yolo"),
        "embeddings": await check_service("embeddings"),
        "groq_api": await check_groq_api(),
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
    )

async def check_database():
    try:
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False

async def check_redis():
    try:
        await redis.ping()
        return True
    except Exception:
        return False

async def check_service(service_name: str):
    try:
        url = os.getenv(f"{service_name.upper()}_URL")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/health", timeout=5.0)
            return response.status_code == 200
    except Exception:
        return False
```

### Monitoring and Observability

**Metrics to Track**:
- Assessment processing time (p50, p95, p99)
- API error rates by endpoint
- External service availability (Groq, Together.ai, PaddleOCR, YOLO)
- Database query performance
- Queue depth and processing rate
- MAPE trends over time
- Fraud detection rate
- Manual review queue size

**Logging Strategy**:
```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info(
    "assessment_completed",
    assessment_id=assessment_id,
    processing_time_ms=processing_time,
    fraud_confidence=fraud_confidence,
    health_score=health_score,
    persona=persona
)
```

## Implementation Guidance

### Development Phases

**Phase 1: Core Infrastructure (Week 1-2)**
- Database schema setup with pgvector
- Authentication and authorization (JWT + RLS)
- Basic API endpoints (assessments, photos)
- Docker Compose local development environment

**Phase 2: AI Domain Integration (Week 3-5)**
- Domain A: Fraud Detection Engine (VIN clone, photo hash, basic signals)
- Domain B: Price Prediction ML (base price, comparable retrieval, quantile regression)
- Domain D: Image Intelligence (PaddleOCR integration, quality gates)
- Domain E: Health Score (weighted calculation, fraud gate)

**Phase 3: Advanced Features (Week 6-7)**
- Domain C: Benchmarking System (MAPE tracking, market data ingestion)
- Manual review queue management
- Real-time progress updates (Supabase Realtime)
- Report generation (PDF/JSON export)

**Phase 4: Frontend Development (Week 8-9)**
- Assessment submission workflow
- Photo capture with guided overlays
- Real-time progress tracking
- Admin dashboard (manual review, metrics)
- Responsive design for mobile/tablet/desktop

**Phase 5: Testing & Optimization (Week 10-11)**
- Property-based tests for all 51 properties
- Integration tests for API endpoints
- Performance optimization (caching, query optimization)
- Load testing (concurrent assessments)

**Phase 6: Deployment & Documentation (Week 12)**
- Cloud deployment setup (Vercel + Railway/Hetzner + Supabase)
- API documentation (OpenAPI/Swagger)
- Deployment guides (cloud + local Docker)
- Seeded data generation

### Technology Stack Summary

**Frontend**:
- Next.js 14 (App Router)
- React 18
- TypeScript
- shadcn/ui components
- TailwindCSS
- Supabase Realtime client
- fast-check (property-based testing)

**Backend**:
- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- Celery/ARQ (async workers)
- Hypothesis (property-based testing)
- pytest

**Database & Storage**:
- PostgreSQL 15 with pgvector extension
- Redis 7 (queue + cache)
- Supabase Storage / S3-compatible storage

**AI/ML Services**:
- Groq API (free tier, primary LLM)
- Together.ai (paid fallback)
- PaddleOCR v4 (in-container)
- YOLOv8n (in-container)
- bge-m3 embeddings (Hugging Face Transformers)

**Deployment**:
- Vercel (frontend hosting)
- Railway/Hetzner (backend + workers)
- Supabase (database + realtime + storage)
- Upstash Redis (cloud queue)
- Docker Compose (local development)

### Key Design Decisions

1. **Dual Deployment Support**: Cloud-first with local Docker fallback enables flexible deployment based on budget and requirements

2. **Free-Tier First with Fallback**: Groq API free tier (14,400 req/day) covers development and small-scale production, with automatic fallback to Together.ai for scale

3. **Property-Based Testing**: 51 correctness properties ensure system reliability across the input space, complementing traditional unit tests

4. **Immutable Audit Trail**: Append-only Assessment_Record design ensures compliance and enables dispute resolution

5. **Persona-Specific Design**: Health score weights and price outputs tailored to Lender/Insurer/Broker use cases

6. **RAG-Based Comparables**: pgvector similarity search with bge-m3 embeddings provides explainable price predictions

7. **Fraud Gate Logic**: Hard cap at health score 30 when fraud confidence > 60 protects against high-risk vehicles

8. **Real-Time Progress**: Supabase Realtime provides live assessment status updates without polling

9. **Microservice AI Components**: Separate containers for PaddleOCR, YOLO, and embeddings enable independent scaling

10. **90-Second Target**: Pipeline optimization with parallel processing (damage detection) and caching (base prices) achieves sub-90s assessments

## Security Considerations

### Authentication & Authorization

- **JWT Tokens**: 30-day expiry with refresh token rotation
- **Row-Level Security**: Supabase RLS policies enforce organization-level data isolation
- **API Key Authentication**: For external market data integration (rate limited to 100 req/hour)
- **Role-Based Access Control**: Five roles with distinct permission sets

### Data Protection

- **Encryption at Rest**: AES-256 for photos in storage
- **Encryption in Transit**: TLS 1.3 for all API communications
- **PII Hashing**: SHA-256 hashing for owner names and contact details in Assessment_Record
- **Photo Retention**: 7-year minimum retention with automatic archival

### Security Best Practices

- **Input Validation**: Pydantic models with strict field validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: React automatic escaping + Content Security Policy headers
- **CSRF Protection**: SameSite cookies + CSRF tokens for state-changing operations
- **Rate Limiting**: Per-user and per-IP rate limits to prevent abuse
- **Audit Logging**: All data access events logged with user ID, timestamp, and action

### Compliance

- **Data Retention**: Configurable retention policies for GDPR/local regulations
- **Right to Erasure**: Soft delete with anonymization for user data
- **Data Export**: JSON export capability for data portability
- **Audit Trail**: Immutable logs for regulatory compliance

## Performance Optimization

### Caching Strategy

**Redis Cache Layers**:
```python
# Layer 1: Base price cache (24-hour TTL)
cache_key = f"base_price:{make}:{model}:{year}"
cached_price = await redis.get(cache_key)
if cached_price:
    return float(cached_price)

# Layer 2: Embedding cache (7-day TTL)
cache_key = f"embedding:{vehicle_hash}"
cached_embedding = await redis.get(cache_key)
if cached_embedding:
    return np.frombuffer(cached_embedding, dtype=np.float32)

# Layer 3: Photo hash cache (90-day TTL)
cache_key = f"photo_hash:{perceptual_hash}"
cached_match = await redis.get(cache_key)
if cached_match:
    return json.loads(cached_match)
```

### Database Optimization

**Indexes**:
- B-tree indexes on frequently queried columns (VIN, user_id, created_at)
- IVFFlat index on embedding vectors for fast similarity search
- Partial indexes on filtered queries (fraud_gate_triggered = TRUE)

**Query Optimization**:
```sql
-- Use EXPLAIN ANALYZE to identify slow queries
EXPLAIN ANALYZE
SELECT * FROM assessments
WHERE user_id = $1 AND created_at > $2
ORDER BY created_at DESC
LIMIT 20;

-- Optimize with covering index
CREATE INDEX idx_assessments_user_created_covering
ON assessments(user_id, created_at DESC)
INCLUDE (status, fraud_confidence, health_score);
```

**Connection Pooling**:
- Minimum 10 connections, maximum 20 connections
- Connection timeout: 30 seconds
- Idle connection timeout: 10 minutes

### Parallel Processing

**Damage Detection Parallelization**:
```python
import asyncio

async def process_photos_parallel(photos: List[Photo]) -> List[DamageDetection]:
    """Process all photos in parallel for damage detection"""
    tasks = [detect_damage(photo) for photo in photos]
    results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]  # Flatten

# Reduces 13 photos × 2s = 26s to ~5s with parallel processing
```

### API Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Per-user rate limiting
@app.post("/assessments", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_assessment(...):
    """Limited to 10 assessments per minute per user"""
    pass

# Per-IP rate limiting for public endpoints
@app.post("/api/public/estimate", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def public_estimate(...):
    """Limited to 5 requests per minute per IP"""
    pass
```

## Scalability Considerations

### Horizontal Scaling

**Worker Pool Scaling**:
```yaml
# Scale workers based on queue depth
services:
  worker:
    deploy:
      replicas: 4  # Start with 4 workers
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      CELERY_CONCURRENCY: 4  # 4 concurrent tasks per worker
```

**Auto-Scaling Rules** (Cloud Deployment):
- Scale up: Queue depth > 50 OR CPU > 80% for 5 minutes
- Scale down: Queue depth < 10 AND CPU < 30% for 10 minutes
- Min replicas: 2, Max replicas: 10

### Database Scaling

**Read Replicas**:
- Primary: Write operations + critical reads
- Replica 1: Assessment history queries
- Replica 2: Benchmarking metrics + reporting

**Partitioning Strategy**:
```sql
-- Partition assessments table by created_at (monthly partitions)
CREATE TABLE assessments_2024_01 PARTITION OF assessments
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE assessments_2024_02 PARTITION OF assessments
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Automatic partition management with pg_partman
```

### CDN and Asset Optimization

**Photo Delivery**:
- Supabase Storage with CDN for fast photo delivery
- Image transformations: Resize on-the-fly for thumbnails
- Lazy loading for photo galleries

**Frontend Optimization**:
- Next.js static generation for marketing pages
- Code splitting for route-based chunks
- Image optimization with next/image

### Load Testing

**Target Metrics**:
- 1000 assessments per day = ~0.7 assessments per minute average
- Peak load: 10 concurrent assessments
- Response time: p95 < 90 seconds for assessment completion

**Load Test Script** (Locust):
```python
from locust import HttpUser, task, between

class VehicleIQUser(HttpUser):
    wait_time = between(5, 15)
    
    @task(3)
    def create_assessment(self):
        self.client.post("/v1/assessments", json={
            "vin": generate_random_vin(),
            "make": "Maruti",
            "model": "Swift",
            "year": 2020,
            "mileage": 50000,
            "persona": "Lender"
        })
    
    @task(1)
    def get_assessment(self):
        assessment_id = self.get_random_assessment_id()
        self.client.get(f"/v1/assessments/{assessment_id}")
```

## Future Enhancements

### Phase 2 Features (Post-MVP)

1. **Mobile Apps**: Native iOS/Android apps with offline photo capture
2. **Advanced Fraud Detection**: Integration with government databases (RTO, insurance)
3. **Video Assessment**: 360° video capture with automated frame extraction
4. **Blockchain Audit Trail**: Immutable assessment records on blockchain
5. **Multi-Language Support**: Hindi, Tamil, Telugu, Bengali UI translations
6. **Advanced Analytics**: Predictive maintenance recommendations, resale value forecasting
7. **API Marketplace**: Third-party integrations (dealerships, banks, insurance companies)
8. **White-Label Solution**: Customizable branding for enterprise customers
9. **Automated Valuation Model (AVM)**: Fully automated assessments without human input
10. **Integration with IoT**: OBD-II device integration for real-time vehicle diagnostics

### Technical Debt to Address

1. **Model Retraining Pipeline**: Automated retraining when MAPE exceeds threshold
2. **A/B Testing Framework**: Production-ready A/B testing for model versions
3. **Advanced Monitoring**: Distributed tracing with OpenTelemetry
4. **Disaster Recovery**: Multi-region deployment with automatic failover
5. **Data Warehouse**: Separate analytics database for historical analysis
6. **GraphQL API**: Alternative to REST for flexible client queries
7. **Batch Processing Optimization**: Parallel processing for large batch uploads
8. **Advanced Caching**: Redis Cluster for distributed caching
9. **Service Mesh**: Istio/Linkerd for microservice communication
10. **Cost Optimization**: Reserved instances, spot instances for non-critical workloads

---

## Summary

This design document provides a comprehensive technical blueprint for VehicleIQ, an AI-powered vehicle valuation platform targeting the Indian used vehicle market. The system integrates five AI capability domains (fraud detection, price prediction, benchmarking, image intelligence, health scoring) into a unified platform delivering 90-second assessments with sub-5% MAPE.

Key architectural decisions include dual deployment support (cloud + local Docker), free-tier-first API strategy with automatic fallback, property-based testing for 51 correctness properties, and persona-specific outputs for Lenders, Insurers, and Brokers. The design emphasizes scalability, security, and maintainability while leveraging modern open-source technologies.

Implementation follows a 12-week phased approach, with core infrastructure, AI domain integration, frontend development, comprehensive testing, and deployment. The system is designed to handle 1000+ assessments per day with horizontal scaling capabilities and maintains an immutable audit trail for compliance and dispute resolution.

