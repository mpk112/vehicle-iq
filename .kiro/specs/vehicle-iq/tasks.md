# Implementation Plan: VehicleIQ

## Overview

This implementation plan breaks down the VehicleIQ platform into executable tasks following the 12-week roadmap defined in the design document. The platform integrates five AI capability domains (fraud detection, price prediction, benchmarking, image intelligence, health scoring) with dual deployment support (cloud + local Docker).

**Technology Stack:**
- Backend: Python 3.11+, FastAPI, SQLAlchemy, Celery/ARQ
- Frontend: Next.js 14, React 18, TypeScript, shadcn/ui, TailwindCSS
- Database: PostgreSQL 15 + pgvector, Redis 7
- AI/ML: Groq API, Together.ai, PaddleOCR v4, YOLOv8n, bge-m3 embeddings
- Testing: Hypothesis (Python PBT), fast-check (TypeScript PBT), pytest
- Deployment: Docker Compose (local), Vercel + Railway/Hetzner + Supabase (cloud)

**Implementation Approach:**
- Incremental development with validation at each step
- Property-based tests for all 51 correctness properties
- Dual deployment configuration from the start
- Seeded data for testing and demonstration

## Tasks


### Phase 1: Core Infrastructure Setup (Week 1-2)

- [ ] 1. Initialize project structure and development environment
  - [ ] 1.1 Create project directory structure
    - Create backend/ directory with FastAPI application structure
    - Create frontend/ directory with Next.js 14 application
    - Create services/ directory for AI microservices (paddleocr, yolo, embeddings)
    - Create scripts/ directory for database initialization and seeding
    - _Requirements: 13.2, 13.6_
  
  - [ ] 1.2 Set up Docker Compose for local development
    - Create docker-compose.yml with services: postgres, redis, backend, worker, frontend
    - Configure pgvector extension in postgres service
    - Add health checks for all services
    - Create .env.example with all required environment variables
    - _Requirements: 13.2, 13.6, 13.7_
  
  - [ ] 1.3 Configure Python backend dependencies
    - Create requirements.txt with FastAPI, SQLAlchemy, Pydantic, Celery, Hypothesis, pytest
    - Set up Black, Ruff for code formatting and linting
    - Configure pytest with coverage reporting
    - _Requirements: 30.4, 30.6_
  
  - [ ] 1.4 Configure TypeScript frontend dependencies
    - Initialize Next.js 14 with App Router
    - Install shadcn/ui, TailwindCSS, Supabase client, fast-check
    - Configure ESLint, Prettier for code formatting
    - Set up Jest and React Testing Library
    - _Requirements: 30.4, 30.6_

- [ ] 2. Set up database schema and migrations
  - [ ] 2.1 Create database schema with pgvector extension
    - Enable pgvector extension in init.sql
    - Create users table with role-based fields
    - Create vehicle_registry table with indexes
    - Create comparable_vehicles table with vector column and IVFFlat index
    - Create assessments table with JSONB fields for AI outputs
    - Create assessment_photos table with storage metadata
    - Create manual_review_queue table
    - Create fraud_cases, benchmarking_metrics, api_usage, audit_log tables
    - _Requirements: 3.1, 8.1, 8.3, 12.1_
  
  - [ ]* 2.2 Write property test for database schema
    - **Property 27: Assessment ID Uniqueness**
    - **Validates: Requirements 8.3**
    - Test that all generated assessment IDs are unique using Hypothesis
  
  - [ ] 2.3 Create SQLAlchemy ORM models
    - Define User, VehicleRegistry, ComparableVehicle, Assessment models
    - Define AssessmentPhoto, ManualReviewQueue, FraudCase models
    - Configure relationships and cascade behaviors
    - Add custom types for pgvector columns
    - _Requirements: 8.1, 12.1_
  
  - [ ] 2.4 Create database migration system
    - Set up Alembic for database migrations
    - Create initial migration from schema
    - Add migration commands to Makefile
    - _Requirements: 30.5_

- [ ] 3. Implement authentication and authorization
  - [ ] 3.1 Create JWT authentication system
    - Implement JWT token generation with 30-day expiry
    - Create login endpoint with password hashing (bcrypt)
    - Create token refresh endpoint
    - Add JWT middleware for protected routes
    - _Requirements: 6.2, 20.5_
  
  - [ ] 3.2 Implement role-based access control (RBAC)
    - Create role enum: Assessor, Lender, Insurer, Broker, Admin
    - Implement permission decorator for route protection
    - Create role-to-feature permission mapping
    - Add access denial logging to audit_log table
    - _Requirements: 6.1, 6.2, 6.8, 6.9_
  
  - [ ]* 3.3 Write property tests for RBAC
    - **Property 21: User Role Uniqueness**
    - **Validates: Requirements 6.2**
    - **Property 22: Role-Based Access Control**
    - **Validates: Requirements 6.8, 6.9**
    - Test that users have exactly one role and unauthorized access is denied
  
  - [ ] 3.4 Implement row-level security policies
    - Create Supabase RLS policies for assessments table
    - Create RLS policies for assessment_photos table
    - Test organization-level data isolation
    - _Requirements: 20.4_
  
  - [ ]* 3.5 Write property test for row-level security
    - **Property 47: Row-Level Security**
    - **Validates: Requirements 20.4**
    - Test that users cannot access assessments outside their organization

- [ ] 4. Create core API endpoints and error handling
  - [ ] 4.1 Implement base FastAPI application structure
    - Create main.py with FastAPI app initialization
    - Configure CORS middleware
    - Add request logging middleware
    - Create health check endpoint
    - _Requirements: 13.7, 29.2_
  
  - [ ] 4.2 Implement error handling and response formatting
    - Create ErrorResponse Pydantic model
    - Implement global exception handlers
    - Add error ID generation for support reference
    - Create retry strategy with exponential backoff
    - _Requirements: 21.3, 21.7_
  
  - [ ]* 4.3 Write unit tests for error handling
    - Test validation errors (HTTP 400)
    - Test authentication errors (HTTP 401/403)
    - Test resource not found errors (HTTP 404)
    - Test rate limiting errors (HTTP 429)
  
  - [ ] 4.4 Implement circuit breaker pattern for external services
    - Create CircuitBreaker class with failure threshold
    - Apply circuit breaker to Groq API calls
    - Apply circuit breaker to AI service calls (PaddleOCR, YOLO)
    - _Requirements: 29.7_

- [ ] 5. Checkpoint - Verify infrastructure setup
  - Ensure all tests pass, ask the user if questions arise.


### Phase 2: AI Domain Integration - Image Intelligence (Week 3)

- [ ] 6. Implement PaddleOCR service integration
  - [ ] 6.1 Create PaddleOCR microservice
    - Create services/paddleocr/Dockerfile with PaddleOCR v4
    - Create server.py with FastAPI endpoints for OCR extraction
    - Configure English + Hindi language support
    - Add health check endpoint
    - _Requirements: 4.6, 4.7, 4.8, 15.1, 15.2, 15.3_
  
  - [ ] 6.2 Implement OCR extraction functions
    - Create extract_odometer() function with regex pattern matching
    - Create extract_vin() function with 17-character validation
    - Create extract_registration() function for Indian registration format
    - Create extract_document_fields() for owner name and registration date
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [ ] 6.3 Implement OCR validation and flagging
    - Add odometer range validation (0-999999)
    - Add VIN format validation (17 alphanumeric characters)
    - Flag invalid extractions for manual verification
    - _Requirements: 15.6, 15.7_
  
  - [ ]* 6.4 Write property test for OCR validation
    - **Property 44: OCR Validation Bounds Checking**
    - **Validates: Requirements 15.6, 15.7**
    - Test that out-of-range odometer readings and invalid VINs are flagged
  
  - [ ] 6.5 Implement OCR pretty printer and parser
    - Create format_ocr_result() function for structured JSON output
    - Create parse_ocr_result() function for round-trip parsing
    - _Requirements: 15.8, 15.9_
  
  - [ ]* 6.6 Write property test for OCR round-trip
    - **Property 45: OCR Round-Trip**
    - **Validates: Requirements 15.9**
    - Test that pretty-printing then parsing produces equivalent data

- [ ] 7. Implement photo quality gate validation
  - [ ] 7.1 Create quality gate validation functions
    - Implement check_blur() using Laplacian variance
    - Implement check_lighting() using mean brightness
    - Implement check_framing() using basic object detection
    - Implement check_resolution() for minimum 1024x768
    - _Requirements: 4.3_
  
  - [ ] 7.2 Create photo upload endpoint
    - Create POST /v1/photos/upload endpoint
    - Accept multipart/form-data with image file
    - Validate file format (JPEG/PNG) and size (max 10MB)
    - Run quality gate validation
    - Store photo in Supabase Storage or local filesystem
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [ ]* 7.3 Write property tests for quality gate
    - **Property 13: Quality Gate Validation Structure**
    - **Validates: Requirements 4.3**
    - **Property 14: Quality Gate Rejection with Feedback**
    - **Validates: Requirements 4.4**
    - Test that quality gate returns all required checks and provides feedback on failure
  
  - [ ] 7.4 Implement photo collection completeness check
    - Define 13 required photo angles as enum
    - Create check_photo_collection_complete() function
    - Mark assessment as ready when all angles pass quality gate
    - _Requirements: 4.1, 4.9_
  
  - [ ]* 7.5 Write property test for photo collection completeness
    - **Property 15: Photo Collection Completeness**
    - **Validates: Requirements 4.9**
    - Test that assessment is marked complete only when all 13 angles pass

- [ ] 8. Implement YOLOv8n damage detection service
  - [ ] 8.1 Create YOLOv8n microservice
    - Create services/yolo/Dockerfile with YOLOv8n model
    - Create server.py with FastAPI endpoint for damage detection
    - Load pretrained YOLOv8n model (fine-tune on vehicle damage dataset if available)
    - Add health check endpoint
    - _Requirements: 4.5, 4.10, 17.1, 17.2_
  
  - [ ] 8.2 Implement damage detection function
    - Create detect_damage() function with 50% confidence threshold
    - Detect damage classes: dent, scratch, rust, crack, missing_part, panel_misalignment, paint_damage
    - Generate bounding boxes with coordinates
    - Calculate severity based on damage area (minor/moderate/severe)
    - _Requirements: 17.2, 17.3, 17.4_
  
  - [ ]* 8.3 Write property test for damage detection output
    - **Property 16: Damage Detection Output Structure**
    - **Validates: Requirements 4.10, 17.3**
    - Test that each damage detection contains class_name, confidence, bbox, severity
  
  - [ ] 8.4 Implement damage aggregation across photos
    - Create aggregate_damage_detections() function
    - Combine detections from all 13 photo angles
    - Remove duplicate detections using IoU (Intersection over Union)
    - Generate comprehensive damage report
    - _Requirements: 17.8_

- [ ] 9. Create Image Intelligence API endpoints
  - [ ] 9.1 Implement photo processing pipeline
    - Create process_photo() function orchestrating quality gate, OCR, damage detection
    - Add async processing for parallel damage detection
    - Store results in assessment_photos table
    - _Requirements: 4.11, 7.4_
  
  - [ ] 9.2 Create GET /v1/photos/{photo_id} endpoint
    - Return photo metadata and signed URL
    - Include OCR results and damage detections
    - Set URL expiry to 1 hour
    - _Requirements: 8.4_
  
  - [ ]* 9.3 Write integration tests for photo endpoints
    - Test photo upload with valid image
    - Test photo upload with invalid format
    - Test quality gate rejection
    - Test OCR extraction from dashboard photo
    - Test damage detection from exterior photo

- [ ] 10. Checkpoint - Verify image intelligence domain
  - Ensure all tests pass, ask the user if questions arise.


### Phase 3: AI Domain Integration - Fraud Detection (Week 4)

- [ ] 11. Implement fraud detection signals
  - [ ] 11.1 Implement VIN clone detection
    - Create check_vin_clone() function querying vehicle_registry
    - Add index on VIN column for fast lookup
    - Return confidence score based on duplicate count
    - _Requirements: 1.1_
  
  - [ ] 11.2 Implement photo reuse detection
    - Create compute_perceptual_hash() using pHash library
    - Store photo hashes in Redis with 90-day TTL
    - Create check_photo_reuse() function matching against hash database
    - Return confidence score based on hash similarity
    - _Requirements: 1.3_
  
  - [ ]* 11.3 Write property test for photo hash determinism
    - **Property 4: Photo Hash Round-Trip**
    - **Validates: Requirements 1.3**
    - Test that computing perceptual hash twice produces identical values
  
  - [ ] 11.4 Implement odometer rollback detection
    - Create check_odometer_rollback() using Groq Vision API
    - Craft prompt for detecting tampering indicators
    - Parse LLM response for confidence score
    - _Requirements: 1.2_
  
  - [ ] 11.5 Implement flood damage detection
    - Create check_flood_damage() using YOLOv8n model
    - Detect water lines, rust patterns, electrical corrosion
    - Calculate confidence score based on detection count and severity
    - _Requirements: 1.4_
  
  - [ ] 11.6 Implement document tampering detection
    - Create check_document_tampering() using OCR + LLM analysis
    - Extract metadata from document photos
    - Use Groq API to analyze font inconsistencies and alignment anomalies
    - _Requirements: 1.5_
  
  - [ ] 11.7 Implement claim history cross-match (mock)
    - Create check_claim_history() function with mock external API
    - Return mock confidence score based on VIN
    - Add TODO comment for production integration
    - _Requirements: 1.6_
  
  - [ ] 11.8 Implement registration mismatch validation
    - Create check_registration_mismatch() comparing VIN vs registration document
    - Use OCR results for comparison
    - Return confidence score based on field consistency
    - _Requirements: 1.6_
  
  - [ ] 11.9 Implement salvage title and stolen vehicle checks (mock)
    - Create check_salvage_title() with mock logic
    - Create check_stolen_vehicle() with mock logic
    - Add TODO comments for production database integration
    - _Requirements: 1.6_

- [ ] 12. Implement fraud confidence scoring
  - [ ] 12.1 Create fraud detection orchestration
    - Create FraudDetectionEngine class
    - Implement detect_fraud() method calling all 9 signal checks
    - Apply weighted sum for fraud confidence calculation
    - Generate explainable evidence for each signal
    - _Requirements: 1.7, 1.9_
  
  - [ ]* 12.2 Write property tests for fraud detection
    - **Property 1: Fraud Confidence Score Bounds**
    - **Validates: Requirements 1.7**
    - **Property 3: Fraud Detection Output Structure**
    - **Validates: Requirements 1.9**
    - Test that fraud confidence is 0-100 and output contains explainable evidence
  
  - [ ] 12.3 Implement fraud gate logic
    - Create apply_fraud_gate() function
    - If fraud_confidence > 60, cap health_score at 30
    - Add assessment to manual_review_queue with high priority
    - Set fraud_gate_triggered flag
    - _Requirements: 1.8, 5.5, 5.6, 11.1_
  
  - [ ]* 12.4 Write property test for fraud gate consistency
    - **Property 2: Fraud Gate Consistency**
    - **Validates: Requirements 1.8, 5.5, 5.6, 11.1**
    - Test that fraud_confidence > 60 triggers gate, caps health score, and adds to manual review

- [ ] 13. Create fraud detection API endpoints
  - [ ] 13.1 Create POST /v1/fraud/detect endpoint
    - Accept VIN, photos, documents, odometer_reading, registration_number
    - Call FraudDetectionEngine.detect_fraud()
    - Return fraud confidence, signals, recommended action
    - _Requirements: 1.7, 1.9_
  
  - [ ]* 13.2 Write integration tests for fraud detection
    - Test VIN clone detection with duplicate VIN
    - Test photo reuse detection with known hash
    - Test fraud gate triggering with high confidence
    - Test explainable evidence in response

- [ ] 14. Implement API rate limiting and fallback
  - [ ] 14.1 Create API usage tracking
    - Create track_api_usage() function writing to api_usage table
    - Track request counts for Groq, Together.ai, PaddleOCR
    - Implement daily rate limit check (14,400 for Groq free tier)
    - _Requirements: 14.1_
  
  - [ ] 14.2 Implement automatic API fallback
    - Create call_llm_with_fallback() function
    - Try Groq API first, fallback to Together.ai on rate limit
    - Log fallback events with timestamp and reason
    - _Requirements: 14.2, 14.3, 14.4, 14.5_
  
  - [ ]* 14.3 Write property tests for API fallback
    - **Property 42: API Fallback Triggering**
    - **Validates: Requirements 14.2, 14.5**
    - **Property 43: API Fallback Transparency**
    - **Validates: Requirements 14.6**
    - Test that rate limit triggers fallback and output format matches
  
  - [ ] 14.4 Create API usage dashboard endpoint
    - Create GET /v1/admin/api-usage endpoint
    - Return usage statistics and remaining free tier quota
    - Send notification when quota drops below 10%
    - _Requirements: 14.7, 14.8_

- [ ] 15. Checkpoint - Verify fraud detection domain
  - Ensure all tests pass, ask the user if questions arise.


### Phase 4: AI Domain Integration - Price Prediction (Week 5)

- [ ] 16. Implement embedding generation service
  - [ ] 16.1 Create bge-m3 embeddings microservice
    - Create services/embeddings/Dockerfile with Hugging Face Transformers
    - Load BAAI/bge-m3 model (1024-dimensional embeddings)
    - Create server.py with FastAPI endpoint for embedding generation
    - Add health check endpoint
    - _Requirements: 16.1, 16.4_
  
  - [ ] 16.2 Implement embedding generation function
    - Create generate_embedding() function
    - Concatenate vehicle attributes in consistent order: make, model, year, variant, fuel_type, transmission, mileage, location
    - Normalize numerical values (year, mileage) to standard ranges
    - Return 1024-dimensional vector
    - _Requirements: 16.1, 16.2, 16.3_
  
  - [ ]* 16.3 Write property tests for embedding generation
    - **Property 29: Embedding Generation Determinism**
    - **Validates: Requirements 16.8**
    - **Property 46: Embedding Attribute Concatenation Consistency**
    - **Validates: Requirements 16.2**
    - Test that identical attributes produce identical embeddings and concatenation order is consistent
  
  - [ ] 16.4 Implement batch embedding generation
    - Create generate_embeddings_batch() function
    - Support at least 100 vehicles per batch
    - Complete batch processing within 10 seconds
    - _Requirements: 16.6_

- [ ] 17. Implement comparable vehicle retrieval (RAG)
  - [ ] 17.1 Create vector similarity search function
    - Create search_similar_vehicles() using pgvector cosine similarity
    - Query comparable_vehicles table with embedding vector
    - Apply constraints: same make/model, year ±2, mileage ±20k
    - Return top 10 results ordered by similarity score
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 17.2 Write property tests for comparable retrieval
    - **Property 9: Comparable Retrieval Count and Ordering**
    - **Validates: Requirements 2.3, 9.3**
    - **Property 30: Embedding Round-Trip**
    - **Validates: Requirements 16.7**
    - **Property 31: Comparable Constraint Satisfaction**
    - **Validates: Requirements 9.4**
    - Test that results are ordered by similarity, count <= 10, scores in [0,1], and constraints are satisfied
  
  - [ ] 17.3 Implement constraint relaxation logic
    - If fewer than 5 results, relax year to ±3 and mileage to ±30k
    - Retry search with relaxed constraints
    - _Requirements: 9.6_
  
  - [ ]* 17.4 Write property test for constraint relaxation
    - **Property 32: Comparable Constraint Relaxation**
    - **Validates: Requirements 9.6**
    - Test that constraints are relaxed when results < 5
  
  - [ ] 17.5 Add comparable explainability
    - Include similarity score, listing price, listing date for each comparable
    - Generate key_differences list comparing attributes
    - _Requirements: 9.5, 9.8_
  
  - [ ]* 17.6 Write property test for comparable explainability
    - **Property 33: Comparable Explainability**
    - **Validates: Requirements 9.5, 9.8**
    - Test that each comparable includes required explainability fields

- [ ] 18. Implement 4-layer pricing model
  - [ ] 18.1 Implement Layer 1: Base price lookup
    - Create get_base_price() function querying vehicle_registry
    - Match on make, model, year, variant
    - Cache results in Redis with 24-hour TTL
    - _Requirements: 2.1_
  
  - [ ] 18.2 Implement Layer 2: Condition adjustment
    - Create apply_condition_adjustment() function
    - Calculate multiplier: 0.70 + 0.45 × (health_score / 100)
    - Apply to base price
    - _Requirements: 2.2_
  
  - [ ]* 18.3 Write property test for price monotonicity
    - **Property 5: Price Prediction Monotonicity**
    - **Validates: Requirements 2.2**
    - Test that higher health score produces higher or equal adjusted price
  
  - [ ] 18.3 Implement Layer 3: Comparable vehicle RAG
    - Integrate search_similar_vehicles() from task 17.1
    - Extract comparable prices into list
    - _Requirements: 2.3_
  
  - [ ] 18.4 Implement Layer 4: Quantile regression
    - Install scikit-learn QuantileRegressor
    - Fit quantile regression on comparable prices
    - Generate P10, P50, P90 predictions
    - Adjust based on health score differential
    - _Requirements: 2.4_
  
  - [ ]* 18.5 Write property test for quantile ordering
    - **Property 6: Quantile Ordering**
    - **Validates: Requirements 2.4**
    - Test that P10 <= P50 <= P90

- [ ] 19. Implement persona-specific valuation
  - [ ] 19.1 Create persona-specific value calculation
    - For Lender: FSV = P10 × 0.95
    - For Insurer: IDV = P50 × depreciation_factor(age_years)
    - For Broker: asking_price = P90 × 1.05
    - _Requirements: 2.6, 2.7, 2.8_
  
  - [ ]* 19.2 Write property test for persona-specific bounds
    - **Property 7: Persona-Specific Value Bounds**
    - **Validates: Requirements 2.6, 2.8**
    - Test that Lender FSV <= P10 and Broker asking_price >= P90
  
  - [ ] 19.3 Add price prediction explainability
    - Create explanation dict with base_price_source, condition_adjustment, persona_adjustment
    - Include comparable vehicles used
    - _Requirements: 2.10_
  
  - [ ]* 19.4 Write property test for price explainability
    - **Property 8: Price Prediction Explainability**
    - **Validates: Requirements 2.10**
    - Test that explanation contains required fields

- [ ] 20. Create price prediction API endpoints
  - [ ] 20.1 Create POST /v1/price/predict endpoint
    - Accept vehicle attributes, health_score, persona
    - Call PricePredictionML.predict()
    - Return base_price, adjusted_price, P10, P50, P90, persona_value, comparables, explanation
    - Complete within 5 seconds
    - _Requirements: 2.9, 2.10_
  
  - [ ]* 20.2 Write integration tests for price prediction
    - Test price prediction with Lender persona
    - Test price prediction with Insurer persona
    - Test price prediction with Broker persona
    - Test comparable retrieval and constraint relaxation
    - Test processing time < 5 seconds

- [ ] 21. Checkpoint - Verify price prediction domain
  - Ensure all tests pass, ask the user if questions arise.


### Phase 5: AI Domain Integration - Health Score & Benchmarking (Week 6-7)

- [ ] 22. Implement vehicle health score calculation
  - [ ] 22.1 Create health score component calculations
    - Implement calculate_mechanical_condition() based on damage detections, odometer, service records
    - Implement calculate_exterior_condition() based on damage detections
    - Implement calculate_interior_condition() based on interior photo analysis
    - Implement calculate_accident_history() (mock for demo)
    - Implement calculate_service_history() based on service records
    - Implement calculate_market_appeal() based on make/model/color popularity
    - _Requirements: 5.1_
  
  - [ ] 22.2 Implement persona-specific weighted scoring
    - Define PERSONA_WEIGHTS dict for Lender, Insurer, Broker
    - Create calculate_health_score() applying persona-specific weights
    - Calculate weighted sum of components
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ]* 22.3 Write property tests for health score
    - **Property 17: Health Score Bounds**
    - **Validates: Requirements 5.1**
    - **Property 18: Health Score Weighted Sum Correctness**
    - **Validates: Requirements 5.2, 5.3, 5.4**
    - Test that health score is 0-100 and equals weighted sum before fraud gate
  
  - [ ] 22.4 Integrate fraud gate logic
    - Apply fraud gate from task 12.3
    - Cap health score at 30 if fraud_confidence > 60
    - _Requirements: 5.5, 5.6_
  
  - [ ] 22.5 Implement low health score flagging
    - If health_score < 40, add to manual_review_queue with standard priority
    - _Requirements: 5.7, 11.2_
  
  - [ ]* 22.6 Write property test for low health score review
    - **Property 19: Low Health Score Manual Review**
    - **Validates: Requirements 5.7, 11.2**
    - Test that health_score < 40 triggers manual review flag
  
  - [ ] 22.7 Add health score explainability
    - Create component_breakdown dict showing contribution of each component
    - Generate explanation list with human-readable factors
    - _Requirements: 5.9_
  
  - [ ]* 22.8 Write property test for health score explainability
    - **Property 20: Health Score Explainability**
    - **Validates: Requirements 5.9**
    - Test that result contains component breakdown

- [ ] 23. Implement benchmarking system
  - [ ] 23.1 Create MAPE calculation function
    - Implement calculate_mape() function: mean(|predicted - actual| / actual) × 100
    - Support segmented MAPE by category, age, price range
    - _Requirements: 3.3, 3.4_
  
  - [ ]* 23.2 Write property test for MAPE calculation
    - **Property 10: MAPE Calculation Correctness**
    - **Validates: Requirements 3.3**
    - Test that MAPE equals the correct formula
  
  - [ ] 23.3 Create market data ingestion endpoint
    - Create POST /v1/benchmarking/market-data endpoint
    - Validate required fields: make, model, year, price, mileage, listing_date
    - Reject records with missing fields
    - _Requirements: 3.6, 23.2, 23.3_
  
  - [ ]* 23.4 Write property test for market data validation
    - **Property 11: Market Data Validation**
    - **Validates: Requirements 3.6, 23.3**
    - Test that records with missing required fields are rejected
  
  - [ ] 23.5 Implement market data deduplication
    - Create check_duplicate() function using hash of (VIN, listing_url)
    - Store hashes in Redis for fast lookup
    - Reject duplicate records
    - _Requirements: 23.4_
  
  - [ ]* 23.6 Write property test for deduplication
    - **Property 50: Market Data Deduplication**
    - **Validates: Requirements 23.4**
    - Test that duplicate VIN or listing_url is rejected
  
  - [ ] 23.7 Implement outcome pairing
    - Create POST /v1/benchmarking/outcome-pairing endpoint
    - Accept assessment_id, actual_transaction_price, transaction_date
    - Update assessment record with actual price
    - Calculate error and update MAPE metrics
    - Add transaction to comparable dataset
    - _Requirements: 3.2, 3.3_
  
  - [ ] 23.8 Create benchmarking metrics endpoint
    - Create GET /v1/benchmarking/metrics endpoint
    - Return overall_mape, mape_by_category, mape_by_age, dataset_size
    - Complete within 10 seconds
    - _Requirements: 3.9_
  
  - [ ] 23.9 Implement nightly embedding regeneration job
    - Create batch job to regenerate embeddings for new comparable records
    - Schedule to run nightly
    - _Requirements: 3.10_
  
  - [ ]* 23.10 Write property test for embedding regeneration
    - **Property 12: Embedding Generation for New Records**
    - **Validates: Requirements 3.10, 16.4**
    - Test that new comparable records have 1024-dimensional embeddings

- [ ] 24. Create seeded dataset
  - [ ] 24.1 Generate seeded vehicle registry
    - Create seed script with 1000+ vehicle records
    - Include popular Indian makes: Maruti, Hyundai, Tata, Honda, Toyota
    - Include realistic attributes: variants, fuel types, transmissions
    - _Requirements: 12.1, 12.2_
  
  - [ ] 24.2 Generate seeded comparable vehicles
    - Create seed script with 2000+ comparable vehicle listings
    - Include prices, locations, listing dates spanning 12 months
    - Generate embeddings for all records
    - _Requirements: 3.1, 12.3_
  
  - [ ] 24.3 Generate seeded historical assessments
    - Create seed script with 500+ assessment records
    - Include complete data and known outcomes
    - _Requirements: 3.7, 12.4_
  
  - [ ] 24.4 Generate seeded fraud cases
    - Create seed script with 50+ confirmed fraud case records
    - Include various fraud types for model validation
    - _Requirements: 3.8, 12.5_
  
  - [ ] 24.5 Add data reset functionality
    - Create reset_to_seeded_data() function
    - Add endpoint for demo/testing purposes
    - Mark seeded data clearly to distinguish from production
    - _Requirements: 12.7, 12.8_

- [ ] 25. Checkpoint - Verify health score and benchmarking domains
  - Ensure all tests pass, ask the user if questions arise.


### Phase 6: Assessment Pipeline & Real-Time Processing (Week 7)

- [ ] 26. Implement assessment orchestration engine
  - [ ] 26.1 Create assessment state machine
    - Create AssessmentStateMachine class
    - Define pipeline stages: photo_validation, ocr_extraction, fraud_detection, damage_analysis, embedding_generation, comparable_retrieval, price_prediction, health_score_calculation, report_generation, audit_trail_creation
    - Implement transition() method publishing status updates
    - _Requirements: 7.4_
  
  - [ ]* 26.2 Write property test for pipeline stage ordering
    - **Property 23: Pipeline Stage Ordering**
    - **Validates: Requirements 7.4**
    - Test that stages are executed in defined sequence
  
  - [ ] 26.3 Implement pipeline failure handling
    - Add try-catch blocks for each stage
    - Halt processing on failure
    - Return descriptive error message
    - _Requirements: 7.5_
  
  - [ ]* 26.4 Write property test for pipeline failure handling
    - **Property 24: Pipeline Failure Handling**
    - **Validates: Requirements 7.5**
    - Test that stage failure halts processing and returns error
  
  - [ ] 26.4 Create assessment processing function
    - Create process_assessment() orchestrating all pipeline stages
    - Call fraud detection, damage analysis, price prediction, health score in sequence
    - Track processing time for each stage
    - Target total time < 90 seconds
    - _Requirements: 7.2, 7.4_
  
  - [ ] 26.5 Implement parallel damage detection
    - Use asyncio.gather() to process all 13 photos in parallel
    - Reduce damage detection time from 26s to ~5s
    - _Requirements: 7.2_

- [ ] 27. Create assessment API endpoints
  - [ ] 27.1 Create POST /v1/assessments endpoint
    - Accept vehicle attributes, VIN, persona
    - Create assessment record with status "queued"
    - Add to Redis queue for async processing
    - Return assessment_id and estimated completion time
    - _Requirements: 7.1, 7.8_
  
  - [ ] 27.2 Create GET /v1/assessments/{assessment_id} endpoint
    - Return assessment status and results
    - Include all AI outputs: fraud_result, health_result, price_prediction, damage_detections
    - _Requirements: 7.6_
  
  - [ ] 27.3 Create GET /v1/assessments endpoint with filtering
    - Support query params: status, persona, fraud_flagged, date_from, date_to, page, page_size
    - Return paginated results
    - Complete within 5 seconds for 1-year queries
    - _Requirements: 8.7, 26.1, 26.4_
  
  - [ ]* 27.4 Write integration tests for assessment endpoints
    - Test assessment creation and queuing
    - Test assessment status polling
    - Test assessment filtering and pagination
    - Test processing time < 90 seconds

- [ ] 28. Implement Celery/ARQ worker for async processing
  - [ ] 28.1 Set up Celery worker configuration
    - Create worker.py with Celery app
    - Configure Redis as message broker
    - Set concurrency to 4 workers
    - _Requirements: 7.7_
  
  - [ ] 28.2 Create assessment processing task
    - Create @celery.task process_assessment_task()
    - Call process_assessment() from task 26.4
    - Update assessment status on completion
    - Handle errors and update status to "failed"
    - _Requirements: 7.2, 7.5, 7.6_
  
  - [ ] 28.3 Add worker health monitoring
    - Track queue depth
    - Log capacity warnings when load > 80%
    - _Requirements: 28.6_

- [ ] 29. Implement real-time progress updates
  - [ ] 29.1 Configure Supabase Realtime
    - Enable Realtime publication for assessments table
    - Configure RLS policies for Realtime subscriptions
    - _Requirements: 7.3_
  
  - [ ] 29.2 Publish progress updates during processing
    - Update assessment record with current_stage and progress_percentage
    - Emit real-time events via Supabase Realtime
    - _Requirements: 7.3_
  
  - [ ] 29.3 Create frontend subscription handler (placeholder)
    - Add TODO comment for frontend implementation in Phase 8
    - Document subscription pattern for assessment progress
    - _Requirements: 7.3_

- [ ] 30. Implement immutable audit trail
  - [ ] 30.1 Create assessment record on completion
    - Create Assessment_Record with all required fields
    - Include user_id, vehicle attributes, AI outputs, timestamps
    - Assign unique immutable identifier
    - _Requirements: 8.1, 8.3_
  
  - [ ]* 30.2 Write property tests for assessment record
    - **Property 25: Assessment Record Creation**
    - **Validates: Requirements 7.6, 8.1**
    - **Property 27: Assessment ID Uniqueness**
    - **Validates: Requirements 8.3**
    - Test that completed assessments create records with all required fields and unique IDs
  
  - [ ] 30.3 Implement assessment record immutability
    - Prevent modification of core assessment data after creation
    - Allow append-only fields: review_notes, override_values
    - _Requirements: 8.2, 8.6_
  
  - [ ]* 30.4 Write property test for immutability
    - **Property 26: Assessment Record Immutability**
    - **Validates: Requirements 8.2, 8.6**
    - Test that core data cannot be modified after creation
  
  - [ ] 30.5 Link fraud indicators to assessment record
    - Store fraud_signals JSONB in assessment record
    - _Requirements: 8.5_
  
  - [ ]* 30.6 Write property test for fraud indicator linkage
    - **Property 28: Fraud Indicator Linkage**
    - **Validates: Requirements 8.5**
    - Test that fraud_confidence > 0 includes fraud indicators in record
  
  - [ ] 30.7 Store photos with assessment references
    - Link assessment_photos to assessments via foreign key
    - Set retention policy to 7 years minimum
    - _Requirements: 8.4_

- [ ] 31. Checkpoint - Verify assessment pipeline
  - Ensure all tests pass, ask the user if questions arise.


### Phase 7: Manual Review & Reporting (Week 8)

- [ ] 32. Implement manual review queue management
  - [ ] 32.1 Create manual review queue entry function
    - Create add_to_manual_review_queue() function
    - Set priority based on fraud_confidence (high if > 60, standard otherwise)
    - Include reason and assessment reference
    - _Requirements: 11.1, 11.2_
  
  - [ ] 32.2 Create GET /v1/manual-review/queue endpoint
    - Support filtering by priority and status
    - Sort by priority (high first) then submission time (oldest first)
    - _Requirements: 11.3_
  
  - [ ]* 32.3 Write property test for queue sorting
    - **Property 37: Manual Review Queue Sorting**
    - **Validates: Requirements 11.3**
    - Test that queue is sorted by priority then time
  
  - [ ] 32.4 Create POST /v1/manual-review/{review_id}/approve endpoint
    - Mark assessment as reviewed
    - Remove from manual review queue
    - Record reviewed_by and reviewed_at
    - _Requirements: 11.5_
  
  - [ ]* 32.5 Write property test for approval state transition
    - **Property 38: Manual Review Approval State Transition**
    - **Validates: Requirements 11.5**
    - Test that approval marks as reviewed and removes from queue
  
  - [ ] 32.6 Create POST /v1/manual-review/{review_id}/override endpoint
    - Accept override reason and adjusted values
    - Append override to assessment record (immutable core data preserved)
    - Mark as reviewed and remove from queue
    - _Requirements: 11.6_
  
  - [ ]* 32.7 Write property test for override recording
    - **Property 39: Manual Review Override Recording**
    - **Validates: Requirements 11.6**
    - Test that override records reason and adjusted values in assessment
  
  - [ ] 32.8 Implement queue notification logic
    - Send notification when queue exceeds 20 pending items
    - Send escalation notification for items pending > 24 hours
    - _Requirements: 11.7, 11.8_
  
  - [ ]* 32.9 Write property test for queue notifications
    - **Property 40: Queue Notification Threshold**
    - **Validates: Requirements 11.7**
    - Test that queue > 20 triggers admin notification
  
  - [ ] 32.10 Create admin review interface endpoint
    - Create GET /v1/manual-review/{review_id}/details endpoint
    - Return all original inputs, AI outputs, fraud indicators, comparables
    - _Requirements: 11.4_

- [ ] 33. Implement report generation
  - [ ] 33.1 Create persona-specific report structure
    - Define Lender report template: FSV, health_score, fraud_indicators, loan_to_value
    - Define Insurer report template: IDV, accident_history, claim_cross_match, underwriting_risk
    - Define Broker report template: asking_price, market_positioning, comparables
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ]* 33.2 Write property test for report structure
    - **Property 34: Persona-Specific Report Structure**
    - **Validates: Requirements 10.1, 10.2, 10.3**
    - Test that each persona report contains required fields
  
  - [ ] 33.3 Add photos with damage annotations to reports
    - Include high-resolution vehicle photos
    - Overlay bounding boxes for damage detections
    - _Requirements: 10.4_
  
  - [ ] 33.4 Add explainable AI sections to reports
    - Include factors influencing valuation
    - Include factors influencing health score
    - Show comparable vehicles used
    - _Requirements: 10.5_
  
  - [ ] 33.5 Implement fraud highlighting in reports
    - If fraud_confidence > 0, prominently highlight fraud indicators
    - Include fraud signal details and evidence
    - _Requirements: 10.8_
  
  - [ ]* 33.6 Write property test for fraud highlighting
    - **Property 36: Fraud Highlighting in Reports**
    - **Validates: Requirements 10.8**
    - Test that fraud indicators are highlighted when present
  
  - [ ] 33.7 Implement PDF report generation
    - Use ReportLab or WeasyPrint for PDF generation
    - Apply consistent branding and styling
    - Generate within 5 seconds
    - _Requirements: 10.6, 10.7_
  
  - [ ] 33.8 Implement JSON report export
    - Create structured JSON format for all report data
    - Include all fields from PDF report
    - _Requirements: 10.6_
  
  - [ ]* 33.9 Write property test for export format support
    - **Property 35: Report Export Format Support**
    - **Validates: Requirements 10.6**
    - Test that reports can be exported to both PDF and JSON
  
  - [ ] 33.10 Create GET /v1/assessments/{assessment_id}/report endpoint
    - Accept format query param: pdf or json
    - Generate and return report
    - _Requirements: 10.6, 10.7_

- [ ] 34. Implement notification system
  - [ ] 34.1 Create notification delivery functions
    - Create send_email_notification() (mock for demo)
    - Create send_sms_notification() (mock for demo)
    - Create send_in_app_notification() storing in database
    - _Requirements: 25.1_
  
  - [ ] 34.2 Implement notification triggers
    - Trigger on high-value assessment completion (configurable threshold)
    - Trigger on fraud_confidence > 60
    - Trigger on manual review queue > 20
    - Trigger on manual review item pending > 24 hours
    - _Requirements: 25.2, 25.3, 25.4, 25.5_
  
  - [ ] 34.3 Implement notification preferences
    - Create user_notification_preferences table
    - Allow users to configure channels and thresholds
    - _Requirements: 25.6_
  
  - [ ] 34.4 Implement notification rate limiting
    - Limit to 10 notifications per user per hour
    - _Requirements: 25.7_
  
  - [ ]* 34.5 Write property test for notification rate limiting
    - **Property 51: Notification Rate Limiting**
    - **Validates: Requirements 25.7**
    - Test that notifications per user per hour <= 10
  
  - [ ] 34.6 Implement notification retry logic
    - Retry failed deliveries up to 3 times
    - Log delivery failures
    - _Requirements: 25.8_

- [ ] 35. Checkpoint - Verify manual review and reporting
  - Ensure all tests pass, ask the user if questions arise.


### Phase 8: Frontend Development (Week 9-10)

- [ ] 36. Set up Next.js frontend application
  - [ ] 36.1 Initialize Next.js 14 with App Router
    - Create app/ directory structure
    - Configure TypeScript, ESLint, Prettier
    - Install shadcn/ui components
    - Configure TailwindCSS with custom theme
    - _Requirements: 18.1, 30.4_
  
  - [ ] 36.2 Set up Supabase client
    - Install @supabase/supabase-js
    - Configure Supabase URL and anon key
    - Create Supabase client singleton
    - _Requirements: 7.3, 29.1_
  
  - [ ] 36.3 Create authentication pages
    - Create /login page with email/password form
    - Create /register page for new users
    - Implement JWT token storage in localStorage
    - Add session timeout handling (30 minutes)
    - _Requirements: 20.5, 20.6_
  
  - [ ] 36.4 Create protected route wrapper
    - Create withAuth() HOC for protected pages
    - Redirect to /login if not authenticated
    - Restore assessment progress from localStorage after re-auth
    - _Requirements: 21.5, 21.6_

- [ ] 37. Implement assessment submission workflow
  - [ ] 37.1 Create vehicle data entry form
    - Create /assessments/new page
    - Add form fields: VIN, make, model, year, variant, fuel_type, transmission, mileage, location, registration_number
    - Add persona selector: Lender, Insurer, Broker
    - Implement form validation with Zod
    - _Requirements: 6.3, 6.4, 6.5, 6.6_
  
  - [ ] 37.2 Implement guided photo capture interface
    - Create photo capture component with 13 angle guidance
    - Display real-time overlay for each required angle
    - Show progress indicator (X of 13 photos captured)
    - Support mobile camera access
    - _Requirements: 4.1, 4.2, 18.2_
  
  - [ ] 37.3 Implement photo upload with quality feedback
    - Upload photos to backend /v1/photos/upload endpoint
    - Display quality gate results in real-time
    - Show specific feedback for failed photos
    - Allow recapture for rejected photos
    - _Requirements: 4.3, 4.4_
  
  - [ ] 37.4 Implement assessment progress persistence
    - Save form data and uploaded photos to localStorage every 30 seconds
    - Restore progress on page reload
    - Clear localStorage on successful submission
    - _Requirements: 21.5, 21.6_
  
  - [ ]* 37.5 Write property test for upload retry logic
    - **Property 48: Upload Retry Logic**
    - **Validates: Requirements 21.1**
    - Test that failed uploads retry up to 3 times with exponential backoff
  
  - [ ] 37.6 Submit assessment and navigate to results page
    - Call POST /v1/assessments endpoint
    - Navigate to /assessments/{assessment_id} on success
    - Display error messages on failure
    - _Requirements: 7.1, 21.2, 21.8_

- [ ] 38. Implement real-time assessment progress tracking
  - [ ] 38.1 Create assessment progress page
    - Create /assessments/{assessment_id} page
    - Display current pipeline stage
    - Show progress bar with percentage
    - Display estimated completion time
    - _Requirements: 7.3, 7.8_
  
  - [ ] 38.2 Subscribe to Supabase Realtime updates
    - Subscribe to assessments table changes for specific assessment_id
    - Update UI in real-time as stages complete
    - Handle connection errors gracefully
    - _Requirements: 7.3_
  
  - [ ] 38.3 Display assessment results on completion
    - Show fraud confidence and signals
    - Show health score with component breakdown
    - Show price prediction with P10/P50/P90 and persona value
    - Show damage detections with annotated photos
    - Show comparable vehicles
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 38.4 Add report download buttons
    - Add "Download PDF" button calling /v1/assessments/{id}/report?format=pdf
    - Add "Download JSON" button calling /v1/assessments/{id}/report?format=json
    - _Requirements: 10.6_

- [ ] 39. Implement assessment history and search
  - [ ] 39.1 Create assessment list page
    - Create /assessments page with table view
    - Display assessment summary: VIN, make/model, date, status, health_score, fraud_flagged
    - Implement pagination with configurable page size
    - _Requirements: 26.1, 26.8_
  
  - [ ] 39.2 Implement search and filter UI
    - Add search input for VIN, make, model
    - Add filter dropdowns: status, persona, fraud_flagged, health_score range, price range
    - Add date range picker
    - _Requirements: 26.1, 26.2, 26.3_
  
  - [ ] 39.3 Implement sorting controls
    - Add sort options: date, price, health_score, fraud_confidence
    - Support ascending/descending order
    - _Requirements: 26.5_
  
  - [ ] 39.4 Implement faceted search display
    - Show result counts by make, model, year, fraud status
    - _Requirements: 26.6_
  
  - [ ] 39.5 Implement saved search queries
    - Add "Save Filter" button storing query params
    - Display saved queries in sidebar
    - Allow loading saved queries
    - _Requirements: 26.7_

- [ ] 40. Implement admin dashboard
  - [ ] 40.1 Create admin dashboard page
    - Create /admin page (Admin role only)
    - Display key metrics: assessments per day, average processing time, API usage, error rates, MAPE trends
    - Add charts using Recharts or similar library
    - _Requirements: 19.7_
  
  - [ ] 40.2 Create manual review queue interface
    - Display manual review queue with priority sorting
    - Show assessment details in modal
    - Add "Approve" and "Override" buttons
    - _Requirements: 11.3, 11.4, 11.5, 11.6_
  
  - [ ] 40.3 Create API usage monitoring page
    - Display API usage statistics for Groq, Together.ai, PaddleOCR, YOLO
    - Show remaining free tier quota
    - Display fallback events
    - _Requirements: 14.7_
  
  - [ ] 40.4 Create benchmarking metrics page
    - Display overall MAPE and segmented MAPE
    - Show dataset size and assessments with outcomes
    - Add chart showing MAPE trends over time
    - _Requirements: 3.9_

- [ ] 41. Implement responsive design
  - [ ] 41.1 Optimize for mobile devices (320px-768px)
    - Optimize photo capture for portrait orientation
    - Use single-column layout
    - Implement touch gestures for photo zoom
    - _Requirements: 18.1, 18.2, 18.5_
  
  - [ ] 41.2 Optimize for tablets (768px-1024px)
    - Use split-screen layout: photo preview + data entry
    - _Requirements: 18.1, 18.3_
  
  - [ ] 41.3 Optimize for desktop (1024px+)
    - Use multi-column layout: photo gallery + data entry + results
    - _Requirements: 18.1, 18.4_
  
  - [ ] 41.4 Implement offline capability
    - Queue photo uploads when offline
    - Retry automatically when connectivity restored
    - Show offline indicator in UI
    - _Requirements: 18.7, 18.8_
  
  - [ ]* 41.5 Write integration tests for frontend workflows
    - Test assessment submission workflow
    - Test photo upload and quality gate feedback
    - Test real-time progress updates
    - Test report download
    - Test search and filter

- [ ] 42. Checkpoint - Verify frontend implementation
  - Ensure all tests pass, ask the user if questions arise.


### Phase 9: Advanced Features & Batch Processing (Week 10)

- [ ] 43. Implement batch assessment processing
  - [ ] 43.1 Create batch upload endpoint
    - Create POST /v1/assessments/batch endpoint
    - Accept CSV file with minimum 100 records
    - Validate file format and data completeness
    - _Requirements: 22.1, 22.2_
  
  - [ ] 43.2 Implement async batch processing
    - Create process_batch_assessments() Celery task
    - Process assessments at minimum 20 per minute
    - Track progress and update batch status
    - _Requirements: 22.3, 22.5_
  
  - [ ] 43.3 Provide batch progress tracking
    - Create GET /v1/assessments/batch/{batch_id} endpoint
    - Return estimated completion time based on batch size
    - Show success count, failure count, current progress
    - _Requirements: 22.4_
  
  - [ ] 43.4 Generate batch summary report
    - Create batch completion report with success/failure counts
    - Calculate average valuation across batch
    - List failed records with error details
    - _Requirements: 22.6_
  
  - [ ] 43.5 Implement batch result export
    - Support CSV export with all assessment results
    - Support JSON export with detailed results
    - _Requirements: 22.7_
  
  - [ ] 43.6 Handle individual record failures gracefully
    - Continue processing remaining records on failure
    - Report failures separately in summary
    - _Requirements: 22.8_
  
  - [ ]* 43.7 Write property test for batch completeness
    - **Property 49: Batch Processing Completeness**
    - **Validates: Requirements 22.8**
    - Test that N valid records produce exactly N results (success or failure)

- [ ] 44. Implement search and filter capabilities
  - [ ] 44.1 Create advanced search endpoint
    - Create GET /v1/assessments/search endpoint
    - Support search by VIN, make, model, year, date range
    - Support filtering by health_score range, fraud flags, manual review status, price range, persona
    - Return results within 3 seconds for 1-year queries
    - _Requirements: 26.1, 26.2, 26.3, 26.4_
  
  - [ ] 44.2 Implement sorting functionality
    - Support sorting by date, price, health_score, fraud_confidence
    - Support ascending/descending order
    - _Requirements: 26.5_
  
  - [ ] 44.3 Implement faceted search
    - Return result counts by make, model, year, fraud status
    - _Requirements: 26.6_
  
  - [ ] 44.4 Implement saved search queries
    - Create saved_searches table
    - Create POST /v1/saved-searches endpoint
    - Create GET /v1/saved-searches endpoint
    - _Requirements: 26.7_
  
  - [ ] 44.5 Implement pagination
    - Support page and page_size query params
    - Return total count and page metadata
    - _Requirements: 26.8_

- [ ] 45. Implement model versioning and A/B testing
  - [ ] 45.1 Create model version management
    - Create model_versions table
    - Support multiple concurrent price prediction models
    - _Requirements: 24.1_
  
  - [ ] 45.2 Implement A/B test configuration
    - Create ab_tests table with traffic_split and duration
    - Create POST /v1/admin/ab-tests endpoint
    - Randomly assign assessments to model versions
    - _Requirements: 24.2, 24.5_
  
  - [ ] 45.3 Track MAPE by model version
    - Log model_version in assessment records
    - Calculate MAPE separately for each version
    - _Requirements: 24.3, 24.4_
  
  - [ ] 45.4 Generate A/B test comparison report
    - Create GET /v1/admin/ab-tests/{test_id}/report endpoint
    - Compare MAPE, processing time, error rates
    - _Requirements: 24.6_
  
  - [ ] 45.5 Implement model promotion
    - Create POST /v1/admin/models/{version}/promote endpoint
    - Switch production model with single click
    - Maintain backward compatibility for historical records
    - _Requirements: 24.7, 24.8_

- [ ] 46. Implement performance monitoring
  - [ ] 46.1 Track assessment processing time
    - Record processing time for each pipeline stage
    - Store in assessment record
    - _Requirements: 19.1_
  
  - [ ] 46.2 Calculate rolling average processing time
    - Create GET /v1/admin/metrics/processing-time endpoint
    - Calculate average over 24-hour windows
    - _Requirements: 19.2_
  
  - [ ] 46.3 Log performance warnings
    - Log warning when processing time > 90 seconds
    - Include stage breakdown in log
    - _Requirements: 19.3_
  
  - [ ] 46.4 Track API error rates
    - Track error rates for Groq, Together.ai, Supabase
    - Calculate error rate over 1-hour windows
    - _Requirements: 19.4_
  
  - [ ] 46.5 Send performance alerts
    - Send alert when API error rate > 5% over 1 hour
    - Send alert to Admin users
    - _Requirements: 19.5_
  
  - [ ] 46.6 Create performance metrics dashboard
    - Display assessments per day, average processing time, API usage, error rates, MAPE trends
    - Retain metrics for 90 days
    - _Requirements: 19.7, 19.8_

- [ ] 47. Checkpoint - Verify advanced features
  - Ensure all tests pass, ask the user if questions arise.


### Phase 10: Security, Testing & Optimization (Week 11)

- [ ] 48. Implement security hardening
  - [ ] 48.1 Implement data encryption
    - Encrypt photos at rest using AES-256
    - Configure TLS 1.3 for all API communications
    - _Requirements: 20.1, 20.2_
  
  - [ ] 48.2 Implement PII hashing
    - Hash owner names and contact details using SHA-256
    - Store hashed values in assessment records
    - _Requirements: 20.3_
  
  - [ ] 48.3 Enforce password requirements
    - Validate minimum 12 characters with mixed case, numbers, special characters
    - Implement password strength meter in frontend
    - _Requirements: 20.5_
  
  - [ ] 48.4 Implement session timeout
    - Set session timeout to 30 minutes of inactivity
    - Clear JWT token on timeout
    - _Requirements: 20.6_
  
  - [ ] 48.5 Implement suspicious login detection
    - Track login attempts by IP and user
    - Require MFA for suspicious patterns (multiple failed attempts, new location)
    - _Requirements: 20.7_
  
  - [ ] 48.6 Implement comprehensive audit logging
    - Log all data access events: user_id, timestamp, resource, action
    - Store in audit_log table
    - _Requirements: 20.8_
  
  - [ ] 48.7 Implement data export with redaction
    - Create GET /v1/admin/data-export endpoint
    - Redact sensitive fields (PII)
    - Log export events in audit_log
    - _Requirements: 20.9_
  
  - [ ] 48.8 Implement input validation
    - Use Pydantic models with strict field validation
    - Validate all user inputs at API boundary
    - Prevent SQL injection using SQLAlchemy ORM
    - _Requirements: 21.3_
  
  - [ ] 48.9 Implement XSS and CSRF protection
    - Configure Content Security Policy headers
    - Use SameSite cookies for CSRF protection
    - React automatic escaping for XSS prevention
    - _Requirements: 21.3_
  
  - [ ] 48.10 Implement rate limiting
    - Add per-user rate limits: 10 assessments per minute
    - Add per-IP rate limits for public endpoints: 5 requests per minute
    - _Requirements: 14.1_

- [ ] 49. Complete property-based test coverage
  - [ ]* 49.1 Write remaining property tests for assessment pipeline
    - **Property 41: API Request Tracking**
    - **Validates: Requirements 14.1**
    - Test that all API calls increment usage tracking
  
  - [ ]* 49.2 Write property tests for data privacy
    - Test that PII is hashed in assessment records
    - Test that session timeout clears authentication
    - Test that audit log captures all data access
  
  - [ ]* 49.3 Write property tests for error handling
    - Test that validation errors return HTTP 400
    - Test that authentication errors return HTTP 401/403
    - Test that rate limit errors return HTTP 429
    - Test that circuit breaker opens after threshold failures
  
  - [ ]* 49.4 Verify all 51 correctness properties are implemented
    - Review property test coverage report
    - Ensure each property has corresponding test with feature tag
    - Run all property tests with minimum 100 iterations
    - _Requirements: 30.3_

- [ ] 50. Complete unit and integration test coverage
  - [ ]* 50.1 Write unit tests for fraud detection signals
    - Test VIN clone detection with duplicate VIN
    - Test photo reuse detection with known hash
    - Test odometer rollback detection with tampered photo
    - Test document tampering detection
  
  - [ ]* 50.2 Write unit tests for price prediction
    - Test base price lookup and caching
    - Test condition adjustment calculation
    - Test quantile regression with edge cases
    - Test persona-specific value calculation
  
  - [ ]* 50.3 Write unit tests for health score
    - Test component calculations with various inputs
    - Test persona-specific weighting
    - Test fraud gate capping at 30
    - Test low health score flagging
  
  - [ ]* 50.4 Write integration tests for complete workflows
    - Test end-to-end assessment submission and processing
    - Test manual review approval workflow
    - Test manual review override workflow
    - Test batch assessment processing
    - Test report generation and export
  
  - [ ]* 50.5 Achieve minimum 80% code coverage
    - Run pytest with coverage reporting
    - Identify uncovered code paths
    - Add tests for uncovered areas
    - _Requirements: 30.1_

- [ ] 51. Implement performance optimizations
  - [ ] 51.1 Implement Redis caching strategy
    - Cache base prices with 24-hour TTL
    - Cache embeddings with 7-day TTL
    - Cache photo hashes with 90-day TTL
    - _Requirements: 28.5_
  
  - [ ] 51.2 Optimize database queries
    - Add B-tree indexes on frequently queried columns
    - Add IVFFlat index on embedding vectors
    - Add partial indexes on filtered queries
    - Use EXPLAIN ANALYZE to identify slow queries
    - _Requirements: 28.5_
  
  - [ ] 51.3 Implement database connection pooling
    - Configure minimum 10, maximum 20 connections
    - Set connection timeout to 30 seconds
    - Set idle connection timeout to 10 minutes
    - _Requirements: 28.4_
  
  - [ ] 51.4 Optimize parallel processing
    - Use asyncio.gather() for damage detection across 13 photos
    - Reduce processing time from 26s to ~5s
    - _Requirements: 7.2_
  
  - [ ] 51.5 Implement frontend optimizations
    - Use Next.js static generation for marketing pages
    - Implement code splitting for route-based chunks
    - Use next/image for image optimization
    - Implement lazy loading for photo galleries
    - _Requirements: 18.1_

- [ ] 52. Checkpoint - Verify security and testing
  - Ensure all tests pass, ask the user if questions arise.


### Phase 11: Deployment & Documentation (Week 12)

- [ ] 53. Configure cloud deployment
  - [ ] 53.1 Set up Vercel frontend deployment
    - Create vercel.json configuration
    - Configure environment variables for production
    - Set up custom domain (optional)
    - _Requirements: 13.1_
  
  - [ ] 53.2 Set up Railway/Hetzner backend deployment
    - Create Dockerfile for backend service
    - Configure environment variables for cloud services
    - Set up health check endpoint
    - Configure auto-scaling rules (min 2, max 10 replicas)
    - _Requirements: 13.1, 28.7_
  
  - [ ] 53.3 Configure Supabase database
    - Create Supabase project
    - Run database migrations
    - Configure RLS policies
    - Enable Realtime publication
    - Set up database backups (24-hour interval, 30-day retention)
    - _Requirements: 13.3, 29.4, 29.5_
  
  - [ ] 53.4 Configure Upstash Redis
    - Create Upstash Redis instance
    - Configure connection URL
    - Test queue and cache operations
    - _Requirements: 13.3_
  
  - [ ] 53.5 Deploy AI microservices
    - Deploy PaddleOCR service to Railway/Hetzner
    - Deploy YOLOv8n service to Railway/Hetzner
    - Deploy bge-m3 embeddings service to Railway/Hetzner
    - Configure service URLs in backend environment
    - _Requirements: 13.3_
  
  - [ ] 53.6 Configure Groq and Together.ai API keys
    - Set up Groq API key (free tier)
    - Set up Together.ai API key (paid fallback)
    - Configure rate limits and fallback logic
    - _Requirements: 13.3, 14.1, 14.2_
  
  - [ ] 53.7 Set up monitoring and alerts
    - Configure health check monitoring
    - Set up alert notifications for service failures
    - Configure performance metric tracking
    - _Requirements: 29.2, 29.6_

- [ ] 54. Configure local Docker deployment
  - [ ] 54.1 Complete docker-compose.yml configuration
    - Verify all services: postgres, redis, backend, worker, frontend, paddleocr, yolo, embeddings
    - Configure health checks for all services
    - Set up volume mounts for persistent data
    - _Requirements: 13.2, 13.6_
  
  - [ ] 54.2 Create local environment configuration
    - Create .env.local with local service URLs
    - Configure Ollama for local LLM inference
    - Configure local storage paths
    - _Requirements: 13.4_
  
  - [ ] 54.3 Test local deployment startup
    - Run docker-compose up
    - Verify all services start within 5 minutes
    - Test health check endpoints
    - _Requirements: 13.6, 13.7_
  
  - [ ] 54.4 Create database initialization script
    - Create scripts/init.sql with schema and pgvector extension
    - Create scripts/seed.py for seeded data
    - Run initialization on first startup
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 55. Implement reliability and availability features
  - [ ] 55.1 Implement health check endpoints
    - Create /health endpoint checking database, redis, AI services
    - Return status within 500 milliseconds
    - _Requirements: 29.2_
  
  - [ ] 55.2 Implement automatic service restart
    - Configure Docker restart policies
    - Implement service degradation detection
    - Auto-restart failed components
    - _Requirements: 29.3_
  
  - [ ] 55.3 Implement database backup
    - Configure automated backups every 24 hours
    - Set 30-day retention policy
    - Test backup restoration
    - _Requirements: 29.4_
  
  - [ ] 55.4 Implement point-in-time recovery
    - Configure WAL archiving for Postgres
    - Support 5-minute interval recovery
    - _Requirements: 29.5_
  
  - [ ] 55.5 Implement critical failure alerts
    - Send alert within 1 minute of critical service failure
    - Alert Admin users via configured channels
    - _Requirements: 29.6_
  
  - [ ] 55.6 Verify 99% uptime target
    - Set up uptime monitoring
    - Track availability during business hours (9 AM - 6 PM IST, Mon-Sat)
    - _Requirements: 29.1_

- [ ] 56. Create comprehensive documentation
  - [ ] 56.1 Generate OpenAPI 3.0 specification
    - Use FastAPI automatic OpenAPI generation
    - Add detailed descriptions for all endpoints
    - Document request/response schemas
    - _Requirements: 27.1, 27.4_
  
  - [ ] 56.2 Set up Swagger UI
    - Configure Swagger UI at /docs endpoint
    - Add authentication support in Swagger
    - _Requirements: 27.2_
  
  - [ ] 56.3 Create API integration examples
    - Write Python example for assessment submission
    - Write JavaScript example for frontend integration
    - Write cURL examples for all endpoints
    - _Requirements: 27.3_
  
  - [ ] 56.4 Document authentication and API keys
    - Document JWT authentication flow
    - Document API key generation and management
    - Document rate limiting policies
    - _Requirements: 27.5_
  
  - [ ] 56.5 Create webhook documentation
    - Document outcome pairing webhook format
    - Document webhook authentication
    - Provide webhook integration examples
    - _Requirements: 27.6_
  
  - [ ] 56.6 Create deployment guides
    - Write cloud deployment guide (Vercel + Railway + Supabase)
    - Write local Docker deployment guide
    - Document environment variable configuration
    - _Requirements: 27.7_
  
  - [ ] 56.7 Create troubleshooting guide
    - Document common errors and resolutions
    - Document health check interpretation
    - Document performance optimization tips
    - _Requirements: 27.8_
  
  - [ ] 56.8 Create README.md
    - Add project overview and features
    - Add quick start guide
    - Add links to detailed documentation
    - Add architecture diagram
    - _Requirements: 27.1, 27.7_

- [ ] 57. Set up continuous integration
  - [ ] 57.1 Create CI pipeline configuration
    - Create .github/workflows/ci.yml (or equivalent)
    - Run tests on every commit
    - Run linters (Black, Ruff, ESLint, Prettier)
    - Generate test coverage reports
    - _Requirements: 30.6, 30.7_
  
  - [ ] 57.2 Configure automated security scanning
    - Scan dependencies for vulnerabilities
    - Use Dependabot or similar for automated updates
    - _Requirements: 30.8_
  
  - [ ] 57.3 Configure code quality checks
    - Enforce minimum 80% code coverage
    - Enforce linting rules
    - Block merge on failing tests
    - _Requirements: 30.1, 30.4_

- [ ] 58. Final integration testing and validation
  - [ ]* 58.1 Run complete end-to-end test suite
    - Test assessment submission workflow
    - Test fraud detection with various scenarios
    - Test price prediction accuracy
    - Test manual review workflow
    - Test batch processing
    - Test report generation
  
  - [ ]* 58.2 Run all property-based tests
    - Verify all 51 properties pass with 100+ iterations
    - Review any failures and fix issues
    - _Requirements: 30.3_
  
  - [ ]* 58.3 Run performance tests
    - Test 90-second assessment completion target
    - Test concurrent processing (10 assessments)
    - Test batch processing rate (20 per minute)
    - Test API response times
    - _Requirements: 7.2, 22.5, 28.1, 28.3_
  
  - [ ]* 58.4 Run load tests
    - Simulate 1000 assessments per day
    - Test system capacity at 80% load
    - Verify no performance degradation
    - _Requirements: 28.1, 28.3_
  
  - [ ] 58.5 Validate seeded data
    - Verify 1000+ vehicle registry records
    - Verify 2000+ comparable vehicles with embeddings
    - Verify 500+ historical assessments
    - Verify 50+ fraud cases
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ] 58.6 Test dual deployment configurations
    - Test cloud deployment with Groq/Together.ai
    - Test local Docker deployment with Ollama
    - Verify feature parity between deployments
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [ ] 59. Final checkpoint - Production readiness verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at phase boundaries
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and error conditions
- Integration tests validate end-to-end workflows and API contracts
- The implementation follows a 12-week phased approach with clear milestones
- Both cloud and local Docker deployments are supported from the start
- All 51 correctness properties from the design document are mapped to property-based tests
- The seeded dataset enables immediate testing and demonstration without production data

