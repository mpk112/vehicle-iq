# Requirements Document

## Introduction

VehicleIQ is an AI-powered vehicle valuation platform designed for the Indian used vehicle market. The system addresses critical challenges including 8-18% inter-assessor variance, odometer fraud affecting 1 in 6 vehicles, and 48-hour manual assessment times. VehicleIQ targets 90-second AI-powered assessments with sub-5% MAPE (Mean Absolute Percentage Error) while providing fraud detection, image intelligence, and persona-specific valuation reports.

## Glossary

- **VehicleIQ_Platform**: The complete AI-powered vehicle valuation system
- **Assessment_Engine**: Core component that orchestrates valuation workflow
- **Fraud_Detection_Engine**: AI subsystem detecting VIN clones, odometer rollback, photo reuse, flood damage, document tampering, and claim history anomalies
- **Price_Prediction_ML**: Machine learning subsystem calculating vehicle valuations using 4-layer pricing model
- **Benchmarking_System**: Component tracking MAPE, managing proprietary datasets, and integrating market data
- **Image_Intelligence_API**: Computer vision subsystem for guided photo capture, damage detection, OCR, and quality validation
- **Vehicle_Health_Score**: 0-100 composite score with persona-specific weights and fraud gate logic
- **Assessor**: User role performing vehicle inspections and data entry
- **Lender**: User role requiring Fair Sale Value (FSV) for loan decisions
- **Insurer**: User role requiring Insured Declared Value (IDV) for policy underwriting
- **Broker**: User role requiring asking price recommendations for vehicle sales
- **Admin**: User role managing system configuration and reviewing flagged assessments
- **VIN**: Vehicle Identification Number
- **MAPE**: Mean Absolute Percentage Error - accuracy metric for price predictions
- **FSV**: Fair Sale Value - valuation metric for lending decisions
- **IDV**: Insured Declared Value - valuation metric for insurance policies
- **RAG**: Retrieval-Augmented Generation - technique for finding comparable vehicles
- **Fraud_Gate**: Logic that caps health scores and triggers manual review when fraud indicators exceed thresholds
- **Assessment_Record**: Immutable audit trail entry for a vehicle assessment
- **Comparable_Vehicle**: Similar vehicle listing used for price benchmarking
- **Quality_Gate**: Validation checkpoint ensuring photo meets minimum standards
- **Odometer_Reading**: Mileage value extracted from vehicle dashboard via OCR
- **Photo_Angle**: One of 13 required vehicle photography positions
- **Quantile_Regression**: Statistical method producing P10/P50/P90 price predictions
- **Embedding_Vector**: Numerical representation of vehicle attributes for similarity search
- **Manual_Review_Queue**: List of assessments flagged for human verification


## Requirements

### Requirement 1: Fraud Detection Engine

**User Story:** As a Lender, I want the system to detect vehicle fraud indicators, so that I can avoid financing fraudulent vehicles and reduce portfolio risk.

#### Acceptance Criteria

1. WHEN a VIN is submitted, THE Fraud_Detection_Engine SHALL check for VIN clone patterns across the vehicle registry within 2 seconds
2. WHEN odometer photos are processed, THE Fraud_Detection_Engine SHALL apply ML models to detect rollback indicators with 85% minimum recall
3. WHEN vehicle photos are uploaded, THE Fraud_Detection_Engine SHALL perform perceptual hash matching against known photo databases to detect reuse
4. WHEN vehicle photos are analyzed, THE Fraud_Detection_Engine SHALL detect flood damage indicators including water lines, rust patterns, and electrical corrosion
5. WHEN vehicle documents are uploaded, THE Fraud_Detection_Engine SHALL detect tampering indicators including font inconsistencies, alignment anomalies, and metadata discrepancies
6. WHEN a VIN is provided, THE Fraud_Detection_Engine SHALL cross-match against insurance claim history databases
7. WHEN fraud indicators are detected, THE Fraud_Detection_Engine SHALL generate a fraud confidence score between 0 and 100
8. IF the fraud confidence score exceeds 60, THEN THE Fraud_Detection_Engine SHALL trigger the Fraud_Gate logic
9. FOR ALL fraud detections, THE Fraud_Detection_Engine SHALL provide explainable evidence including specific indicators and confidence levels

### Requirement 2: Price Prediction ML System

**User Story:** As an Assessor, I want accurate AI-powered price predictions, so that I can provide consistent valuations with sub-5% MAPE.

#### Acceptance Criteria

1. WHEN vehicle attributes are provided, THE Price_Prediction_ML SHALL calculate base price using market data for the make, model, year, and variant
2. WHEN Vehicle_Health_Score is available, THE Price_Prediction_ML SHALL apply condition adjustment multipliers to the base price
3. WHEN calculating final price, THE Price_Prediction_ML SHALL retrieve top 10 Comparable_Vehicle records using RAG with Embedding_Vector similarity
4. WHEN generating price range, THE Price_Prediction_ML SHALL apply Quantile_Regression to produce P10, P50, and P90 price predictions
5. THE Price_Prediction_ML SHALL achieve MAPE below 5% when validated against actual transaction prices
6. WHEN persona is Lender, THE Price_Prediction_ML SHALL output FSV calculated as P10 value with conservative adjustment
7. WHEN persona is Insurer, THE Price_Prediction_ML SHALL output IDV calculated as P50 value with depreciation factors
8. WHEN persona is Broker, THE Price_Prediction_ML SHALL output asking price calculated as P90 value with market premium
9. WHEN price prediction completes, THE Price_Prediction_ML SHALL return results within 5 seconds
10. FOR ALL price predictions, THE Price_Prediction_ML SHALL provide explainable factors including base price, adjustments, and comparable vehicles used


### Requirement 3: Benchmarking System

**User Story:** As an Admin, I want to track valuation accuracy and manage market data, so that I can continuously improve prediction quality and maintain competitive benchmarks.

#### Acceptance Criteria

1. THE Benchmarking_System SHALL maintain a proprietary dataset of at least 2000 Comparable_Vehicle records with Embedding_Vector representations
2. WHEN new vehicle transactions are confirmed, THE Benchmarking_System SHALL add them to the proprietary dataset within 24 hours
3. THE Benchmarking_System SHALL calculate MAPE by comparing predicted prices against actual transaction prices
4. WHEN MAPE is calculated, THE Benchmarking_System SHALL segment results by vehicle category, age bracket, and price range
5. THE Benchmarking_System SHALL integrate market data from external sources at least once per week
6. WHEN market data is integrated, THE Benchmarking_System SHALL validate data quality and reject records with missing critical fields
7. THE Benchmarking_System SHALL maintain at least 500 historical Assessment_Record entries with known outcomes for model training
8. THE Benchmarking_System SHALL maintain at least 50 confirmed fraud cases for fraud model validation
9. WHEN Admin requests benchmarking report, THE Benchmarking_System SHALL generate accuracy metrics within 10 seconds
10. FOR ALL dataset updates, THE Benchmarking_System SHALL regenerate Embedding_Vector representations for new records

### Requirement 4: Image Intelligence API

**User Story:** As an Assessor, I want guided photo capture with automatic quality validation, so that I can collect consistent vehicle imagery for accurate AI analysis.

#### Acceptance Criteria

1. THE Image_Intelligence_API SHALL define 13 required Photo_Angle positions including front, rear, sides, interior, dashboard, odometer, VIN plate, engine bay, tires, and damage areas
2. WHEN Assessor initiates photo capture, THE Image_Intelligence_API SHALL provide real-time guidance overlays for each Photo_Angle
3. WHEN a photo is captured, THE Image_Intelligence_API SHALL apply Quality_Gate validation checking for blur, lighting, framing, and resolution
4. IF a photo fails Quality_Gate validation, THEN THE Image_Intelligence_API SHALL reject the photo and provide specific feedback for recapture
5. WHEN vehicle photos are submitted, THE Image_Intelligence_API SHALL detect visible damage including dents, scratches, rust, and panel misalignment
6. WHEN dashboard photo is processed, THE Image_Intelligence_API SHALL extract Odometer_Reading using OCR with 95% minimum accuracy
7. WHEN VIN plate photo is processed, THE Image_Intelligence_API SHALL extract VIN using OCR with 98% minimum accuracy
8. THE Image_Intelligence_API SHALL support Hindi text recognition for Indian vehicle documents
9. WHEN all 13 Photo_Angle images pass Quality_Gate validation, THE Image_Intelligence_API SHALL mark photo collection as complete
10. WHEN damage is detected, THE Image_Intelligence_API SHALL generate bounding boxes and severity classifications for each damage area
11. THE Image_Intelligence_API SHALL process each photo through Quality_Gate validation within 3 seconds


### Requirement 5: Vehicle Health Score Calculation

**User Story:** As a Lender, I want a standardized 0-100 health score with fraud protection, so that I can quickly assess vehicle condition and risk level.

#### Acceptance Criteria

1. THE Vehicle_Health_Score SHALL calculate a composite score between 0 and 100 based on condition factors, fraud indicators, and maintenance history
2. WHEN persona is Lender, THE Vehicle_Health_Score SHALL apply weights of 40% mechanical condition, 30% exterior condition, 20% fraud indicators, 10% service history
3. WHEN persona is Insurer, THE Vehicle_Health_Score SHALL apply weights of 35% accident history, 30% mechanical condition, 25% fraud indicators, 10% exterior condition
4. WHEN persona is Broker, THE Vehicle_Health_Score SHALL apply weights of 45% exterior condition, 25% mechanical condition, 20% market appeal, 10% fraud indicators
5. IF fraud confidence score exceeds 60, THEN THE Vehicle_Health_Score SHALL apply Fraud_Gate logic capping the health score at 30
6. WHEN Fraud_Gate is triggered, THE Vehicle_Health_Score SHALL add the Assessment_Record to Manual_Review_Queue
7. WHEN health score is below 40, THE Vehicle_Health_Score SHALL flag the assessment for manual review
8. THE Vehicle_Health_Score SHALL complete calculation within 2 seconds of receiving all input factors
9. FOR ALL health score calculations, THE Vehicle_Health_Score SHALL provide factor breakdown showing contribution of each component

### Requirement 6: Multi-Role Access Control

**User Story:** As an Admin, I want role-based access control, so that users can only access features appropriate to their role.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL support four user roles: Assessor, Lender, Insurer, Broker, and Admin
2. WHEN a user authenticates, THE VehicleIQ_Platform SHALL assign exactly one primary role
3. WHEN Assessor accesses the system, THE VehicleIQ_Platform SHALL provide access to photo capture, data entry, and assessment submission features
4. WHEN Lender accesses the system, THE VehicleIQ_Platform SHALL provide access to FSV reports, fraud indicators, and assessment history
5. WHEN Insurer accesses the system, THE VehicleIQ_Platform SHALL provide access to IDV reports, accident history, and claim cross-match results
6. WHEN Broker accesses the system, THE VehicleIQ_Platform SHALL provide access to asking price recommendations and market comparables
7. WHEN Admin accesses the system, THE VehicleIQ_Platform SHALL provide access to Manual_Review_Queue, system configuration, and benchmarking reports
8. THE VehicleIQ_Platform SHALL deny access attempts to features outside the user's assigned role
9. WHEN user attempts unauthorized access, THE VehicleIQ_Platform SHALL log the attempt and return an error message within 500 milliseconds

### Requirement 7: Real-Time Assessment Pipeline

**User Story:** As an Assessor, I want real-time progress updates during assessment processing, so that I can track the 90-second workflow and identify any delays.

#### Acceptance Criteria

1. WHEN an assessment is submitted, THE Assessment_Engine SHALL initiate processing within 1 second
2. THE Assessment_Engine SHALL complete end-to-end assessment processing within 90 seconds for 95% of assessments
3. WHEN assessment progresses through pipeline stages, THE Assessment_Engine SHALL publish status updates via real-time subscriptions
4. THE Assessment_Engine SHALL process stages in sequence: photo validation, OCR extraction, fraud detection, damage analysis, price prediction, health score calculation, report generation
5. WHEN any pipeline stage fails, THE Assessment_Engine SHALL halt processing and return a descriptive error message
6. WHEN assessment completes successfully, THE Assessment_Engine SHALL create an immutable Assessment_Record
7. THE Assessment_Engine SHALL support concurrent processing of at least 10 assessments without performance degradation
8. WHEN assessment is queued, THE Assessment_Engine SHALL provide estimated completion time based on current queue depth


### Requirement 8: Immutable Audit Trail

**User Story:** As an Admin, I want an immutable audit trail of all assessments, so that I can ensure compliance, resolve disputes, and analyze historical patterns.

#### Acceptance Criteria

1. WHEN an assessment completes, THE VehicleIQ_Platform SHALL create an Assessment_Record with timestamp, user ID, vehicle details, all input data, all AI outputs, and final valuation
2. THE VehicleIQ_Platform SHALL prevent modification or deletion of Assessment_Record entries after creation
3. WHEN Assessment_Record is created, THE VehicleIQ_Platform SHALL assign a unique immutable identifier
4. THE VehicleIQ_Platform SHALL store all uploaded photos with Assessment_Record references for minimum 7 years
5. WHEN fraud is detected, THE VehicleIQ_Platform SHALL link fraud indicators to the Assessment_Record
6. WHEN manual review is performed, THE VehicleIQ_Platform SHALL append review notes and decisions to Assessment_Record without modifying original data
7. WHEN Admin queries audit trail, THE VehicleIQ_Platform SHALL support filtering by date range, user, vehicle, fraud flags, and review status
8. THE VehicleIQ_Platform SHALL return audit trail query results within 5 seconds for queries spanning up to 1 year

### Requirement 9: RAG-Based Comparable Vehicle Retrieval

**User Story:** As a Lender, I want to see comparable vehicle listings that influenced the valuation, so that I can verify the AI's pricing logic against real market data.

#### Acceptance Criteria

1. WHEN vehicle attributes are provided, THE Price_Prediction_ML SHALL generate an Embedding_Vector representation
2. WHEN searching for comparables, THE Price_Prediction_ML SHALL perform vector similarity search against the Comparable_Vehicle database
3. THE Price_Prediction_ML SHALL retrieve the top 10 most similar Comparable_Vehicle records based on cosine similarity
4. WHEN filtering comparables, THE Price_Prediction_ML SHALL apply constraints for make, model, year range within 2 years, and mileage range within 20000 km
5. WHEN comparables are retrieved, THE Price_Prediction_ML SHALL include similarity scores, listing prices, listing dates, and key attribute differences
6. IF fewer than 5 comparables match the constraints, THEN THE Price_Prediction_ML SHALL relax year range to 3 years and mileage range to 30000 km
7. THE Price_Prediction_ML SHALL complete comparable retrieval within 3 seconds
8. FOR ALL comparable retrievals, THE Price_Prediction_ML SHALL explain why each comparable was selected based on attribute similarity

### Requirement 10: Persona-Specific Report Generation

**User Story:** As a Lender, I want a report tailored to lending decisions with FSV and risk indicators, so that I can make informed loan approval decisions.

#### Acceptance Criteria

1. WHEN assessment completes for Lender persona, THE VehicleIQ_Platform SHALL generate a report containing FSV, Vehicle_Health_Score, fraud indicators, and loan-to-value recommendations
2. WHEN assessment completes for Insurer persona, THE VehicleIQ_Platform SHALL generate a report containing IDV, accident history, claim cross-match results, and underwriting risk factors
3. WHEN assessment completes for Broker persona, THE VehicleIQ_Platform SHALL generate a report containing asking price recommendation, market positioning, and comparable listings
4. THE VehicleIQ_Platform SHALL include high-resolution vehicle photos with damage annotations in all reports
5. THE VehicleIQ_Platform SHALL include explainable AI sections showing factors that influenced valuation and health score
6. WHEN report is generated, THE VehicleIQ_Platform SHALL support export formats including PDF and JSON
7. THE VehicleIQ_Platform SHALL generate reports within 5 seconds of assessment completion
8. WHEN fraud indicators are present, THE VehicleIQ_Platform SHALL highlight them prominently in all report types


### Requirement 11: Manual Review Queue Management

**User Story:** As an Admin, I want to review assessments flagged by fraud detection or low health scores, so that I can verify AI decisions and override when necessary.

#### Acceptance Criteria

1. WHEN Fraud_Gate is triggered, THE VehicleIQ_Platform SHALL add the assessment to Manual_Review_Queue with priority level based on fraud confidence score
2. WHEN health score is below 40, THE VehicleIQ_Platform SHALL add the assessment to Manual_Review_Queue with standard priority
3. WHEN Admin accesses Manual_Review_Queue, THE VehicleIQ_Platform SHALL display assessments sorted by priority and submission time
4. WHEN Admin reviews an assessment, THE VehicleIQ_Platform SHALL display all original inputs, AI outputs, fraud indicators, and comparable vehicles
5. WHEN Admin approves an assessment, THE VehicleIQ_Platform SHALL mark it as reviewed and remove it from Manual_Review_Queue
6. WHEN Admin overrides an assessment, THE VehicleIQ_Platform SHALL record the override reason and adjusted values in the Assessment_Record
7. THE VehicleIQ_Platform SHALL send notifications to Admin when Manual_Review_Queue exceeds 20 pending items
8. WHEN assessment remains in Manual_Review_Queue for more than 24 hours, THE VehicleIQ_Platform SHALL escalate priority and send reminder notification

### Requirement 12: Seeded Vehicle Registry

**User Story:** As a developer, I want a seeded vehicle registry with realistic Indian market data, so that I can test and demonstrate the platform without requiring production data.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL include a seeded vehicle registry with at least 1000 vehicle records representing popular Indian makes and models
2. THE VehicleIQ_Platform SHALL include realistic attributes for each vehicle including make, model, year, variant, fuel type, transmission, and typical mileage ranges
3. THE VehicleIQ_Platform SHALL include at least 2000 Comparable_Vehicle listings with prices, locations, and listing dates spanning the past 12 months
4. THE VehicleIQ_Platform SHALL include at least 500 historical Assessment_Record entries with complete data and known outcomes
5. THE VehicleIQ_Platform SHALL include at least 50 confirmed fraud case records for testing fraud detection models
6. WHEN seeded data is loaded, THE VehicleIQ_Platform SHALL generate Embedding_Vector representations for all Comparable_Vehicle records
7. THE VehicleIQ_Platform SHALL support resetting to seeded data state for demo and testing purposes
8. THE VehicleIQ_Platform SHALL clearly mark seeded data to distinguish it from production data

### Requirement 13: Deployment Configuration Management

**User Story:** As a developer, I want flexible deployment options supporting both cloud and local environments, so that I can choose the deployment path that fits my needs and budget.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL support cloud deployment using Vercel for frontend and Railway or Hetzner for backend services
2. THE VehicleIQ_Platform SHALL support local deployment using a single docker-compose.yml file that orchestrates all services
3. WHEN deployed to cloud, THE VehicleIQ_Platform SHALL use Supabase for database, Upstash Redis for queue, and Groq API for LLM inference
4. WHEN deployed locally, THE VehicleIQ_Platform SHALL use Postgres with pgvector for database, Redis for queue, and Ollama for LLM inference
5. THE VehicleIQ_Platform SHALL provide environment variable configuration for switching between cloud and local service providers
6. WHEN local deployment is initiated, THE VehicleIQ_Platform SHALL start all services including database, queue, backend API, frontend, and AI models within 5 minutes
7. THE VehicleIQ_Platform SHALL include health check endpoints for all services
8. WHEN service health checks fail, THE VehicleIQ_Platform SHALL log errors and provide diagnostic information


### Requirement 14: API Rate Limiting and Fallback

**User Story:** As a developer, I want automatic fallback between free and paid AI services, so that I can stay within free tier limits during development and scale to paid services for production.

#### Acceptance Criteria

1. WHEN using Groq API, THE VehicleIQ_Platform SHALL track request counts against free tier limits of 14400 requests per day
2. IF Groq API rate limit is exceeded, THEN THE VehicleIQ_Platform SHALL automatically fallback to Together.ai API
3. WHEN using Groq Vision API, THE VehicleIQ_Platform SHALL track request counts against free tier limits of 14400 requests per day
4. IF Groq Vision API rate limit is exceeded, THEN THE VehicleIQ_Platform SHALL automatically fallback to Together.ai vision models
5. THE VehicleIQ_Platform SHALL log all API fallback events with timestamp and reason
6. WHEN API fallback occurs, THE VehicleIQ_Platform SHALL continue processing without user-visible errors
7. THE VehicleIQ_Platform SHALL provide Admin dashboard showing API usage statistics and remaining free tier quota
8. WHEN free tier quota drops below 10%, THE VehicleIQ_Platform SHALL send notification to Admin

### Requirement 15: OCR Parser and Pretty Printer

**User Story:** As a developer, I want reliable OCR parsing with validation, so that I can extract vehicle data from images and verify extraction accuracy.

#### Acceptance Criteria

1. WHEN odometer photo is processed, THE Image_Intelligence_API SHALL parse the Odometer_Reading using PaddleOCR v4
2. WHEN VIN plate photo is processed, THE Image_Intelligence_API SHALL parse the VIN using PaddleOCR v4
3. WHEN document photo is processed, THE Image_Intelligence_API SHALL parse text fields including registration number, owner name, and registration date
4. THE Image_Intelligence_API SHALL support Hindi text recognition for Indian vehicle documents
5. WHEN OCR parsing completes, THE Image_Intelligence_API SHALL validate extracted data against expected formats and ranges
6. IF Odometer_Reading is outside the range 0 to 999999, THEN THE Image_Intelligence_API SHALL flag it for manual verification
7. IF VIN does not match the expected 17-character alphanumeric format, THEN THE Image_Intelligence_API SHALL flag it for manual verification
8. THE Image_Intelligence_API SHALL provide a pretty printer that formats extracted data into structured JSON with field labels
9. FOR ALL OCR extractions, parsing the pretty-printed output SHALL produce data equivalent to the original extraction (round-trip property)
10. THE Image_Intelligence_API SHALL complete OCR parsing within 2 seconds per image

### Requirement 16: Embedding Vector Generation and Similarity Search

**User Story:** As a developer, I want consistent embedding generation for vehicle attributes, so that I can perform accurate similarity searches for comparable vehicles.

#### Acceptance Criteria

1. WHEN vehicle attributes are provided, THE Price_Prediction_ML SHALL generate an Embedding_Vector using bge-m3 model
2. THE Price_Prediction_ML SHALL concatenate vehicle attributes in consistent order: make, model, year, variant, fuel_type, transmission, mileage, location
3. WHEN generating embeddings, THE Price_Prediction_ML SHALL normalize numerical values to standard ranges
4. THE Price_Prediction_ML SHALL store Embedding_Vector representations with 1024 dimensions
5. WHEN performing similarity search, THE Price_Prediction_ML SHALL use cosine similarity metric
6. THE Price_Prediction_ML SHALL support batch embedding generation for at least 100 vehicles within 10 seconds
7. FOR ALL vehicle records, generating an embedding then searching for the same vehicle SHALL return it as the top result with similarity score above 0.99 (round-trip property)
8. WHEN vehicle attributes are identical, THE Price_Prediction_ML SHALL generate identical Embedding_Vector representations (deterministic property)


### Requirement 17: Damage Detection Model

**User Story:** As an Assessor, I want automatic damage detection from vehicle photos, so that I can ensure all visible damage is documented and factored into the valuation.

#### Acceptance Criteria

1. WHEN vehicle photos are uploaded, THE Image_Intelligence_API SHALL apply YOLOv8n model to detect damage areas
2. THE Image_Intelligence_API SHALL detect damage types including dents, scratches, rust, cracks, missing parts, and panel misalignment
3. WHEN damage is detected, THE Image_Intelligence_API SHALL generate bounding boxes with coordinates and confidence scores
4. THE Image_Intelligence_API SHALL classify damage severity as minor, moderate, or severe based on size and location
5. WHEN multiple damage areas are detected in a single photo, THE Image_Intelligence_API SHALL return separate bounding boxes for each area
6. THE Image_Intelligence_API SHALL process damage detection within 2 seconds per photo
7. WHEN damage detection confidence is below 70%, THE Image_Intelligence_API SHALL flag the area for manual verification
8. THE Image_Intelligence_API SHALL aggregate damage detections across all 13 Photo_Angle images into a comprehensive damage report

### Requirement 18: Frontend Responsive Design

**User Story:** As an Assessor, I want a mobile-responsive interface for field assessments, so that I can capture vehicle data and photos using a smartphone or tablet.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL provide a responsive web interface that adapts to screen sizes from 320px to 2560px width
2. WHEN accessed on mobile devices, THE VehicleIQ_Platform SHALL optimize photo capture interface for portrait orientation
3. WHEN accessed on tablets, THE VehicleIQ_Platform SHALL provide split-screen layout showing photo preview and data entry forms
4. WHEN accessed on desktop, THE VehicleIQ_Platform SHALL provide multi-column layout with photo gallery, data entry, and real-time results
5. THE VehicleIQ_Platform SHALL support touch gestures for photo capture, zoom, and navigation on mobile devices
6. THE VehicleIQ_Platform SHALL maintain consistent branding and user experience across all screen sizes
7. WHEN network connectivity is poor, THE VehicleIQ_Platform SHALL queue photo uploads and retry automatically
8. THE VehicleIQ_Platform SHALL provide offline capability for data entry with sync when connectivity is restored

### Requirement 19: Performance Monitoring and Metrics

**User Story:** As an Admin, I want real-time performance metrics and error tracking, so that I can identify bottlenecks and maintain system reliability.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL track assessment processing time for each pipeline stage
2. THE VehicleIQ_Platform SHALL calculate and display average processing time over rolling 24-hour windows
3. WHEN processing time exceeds 90 seconds, THE VehicleIQ_Platform SHALL log a performance warning with stage breakdown
4. THE VehicleIQ_Platform SHALL track API error rates for all external services including Groq, Together.ai, and Supabase
5. WHEN API error rate exceeds 5% over a 1-hour window, THE VehicleIQ_Platform SHALL send alert notification to Admin
6. THE VehicleIQ_Platform SHALL track MAPE metrics updated daily based on confirmed transaction outcomes
7. THE VehicleIQ_Platform SHALL provide Admin dashboard displaying key metrics including assessments per day, average processing time, API usage, error rates, and MAPE trends
8. THE VehicleIQ_Platform SHALL retain performance metrics for at least 90 days


### Requirement 20: Data Privacy and Security

**User Story:** As a Lender, I want vehicle and customer data to be securely stored and accessed, so that I can comply with data protection regulations and maintain customer trust.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL encrypt all vehicle photos at rest using AES-256 encryption
2. THE VehicleIQ_Platform SHALL encrypt all API communications using TLS 1.3
3. WHEN storing Assessment_Record entries, THE VehicleIQ_Platform SHALL hash personally identifiable information including owner names and contact details
4. THE VehicleIQ_Platform SHALL implement row-level security policies ensuring users can only access assessments within their organization
5. WHEN user authenticates, THE VehicleIQ_Platform SHALL enforce password requirements of minimum 12 characters with mixed case, numbers, and special characters
6. THE VehicleIQ_Platform SHALL implement session timeout of 30 minutes for inactive users
7. WHEN suspicious login patterns are detected, THE VehicleIQ_Platform SHALL require multi-factor authentication
8. THE VehicleIQ_Platform SHALL log all data access events including user ID, timestamp, resource accessed, and action performed
9. WHEN Admin requests data export, THE VehicleIQ_Platform SHALL redact sensitive fields and provide audit log of the export

### Requirement 21: Error Handling and Recovery

**User Story:** As an Assessor, I want clear error messages and automatic recovery, so that I can resolve issues quickly without losing assessment progress.

#### Acceptance Criteria

1. WHEN photo upload fails, THE VehicleIQ_Platform SHALL retry up to 3 times with exponential backoff before reporting failure
2. WHEN OCR extraction fails, THE VehicleIQ_Platform SHALL provide manual entry option with the failed photo displayed for reference
3. WHEN AI model inference fails, THE VehicleIQ_Platform SHALL log the error with full context and return a user-friendly error message
4. WHEN database connection is lost, THE VehicleIQ_Platform SHALL queue pending operations and retry when connection is restored
5. THE VehicleIQ_Platform SHALL preserve assessment progress in browser local storage every 30 seconds
6. WHEN user session expires during assessment, THE VehicleIQ_Platform SHALL restore progress from local storage after re-authentication
7. WHEN critical error occurs, THE VehicleIQ_Platform SHALL provide error ID for support reference and log full stack trace
8. THE VehicleIQ_Platform SHALL display error messages in user's preferred language with actionable resolution steps

### Requirement 22: Batch Assessment Processing

**User Story:** As a Lender, I want to process multiple vehicle assessments in batch mode, so that I can efficiently value entire vehicle portfolios.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL support batch upload of vehicle data via CSV file with minimum 100 records per batch
2. WHEN batch file is uploaded, THE VehicleIQ_Platform SHALL validate file format and data completeness before processing
3. THE VehicleIQ_Platform SHALL process batch assessments asynchronously with progress tracking
4. WHEN batch processing is initiated, THE VehicleIQ_Platform SHALL provide estimated completion time based on batch size
5. THE VehicleIQ_Platform SHALL process batch assessments at minimum rate of 20 assessments per minute
6. WHEN batch processing completes, THE VehicleIQ_Platform SHALL generate summary report with success count, failure count, and average valuation
7. THE VehicleIQ_Platform SHALL support exporting batch results to CSV and JSON formats
8. WHEN batch assessment fails for individual records, THE VehicleIQ_Platform SHALL continue processing remaining records and report failures separately


### Requirement 23: Market Data Integration API

**User Story:** As an Admin, I want to integrate external market data sources, so that I can keep comparable vehicle listings current and improve valuation accuracy.

#### Acceptance Criteria

1. THE Benchmarking_System SHALL provide REST API endpoints for ingesting external market data
2. WHEN external data is received, THE Benchmarking_System SHALL validate required fields including make, model, year, price, mileage, and listing_date
3. THE Benchmarking_System SHALL reject records with missing required fields and return validation error details
4. WHEN valid market data is received, THE Benchmarking_System SHALL deduplicate against existing Comparable_Vehicle records using VIN or listing URL
5. THE Benchmarking_System SHALL normalize price values to INR currency
6. THE Benchmarking_System SHALL normalize mileage values to kilometers
7. WHEN market data is integrated, THE Benchmarking_System SHALL generate Embedding_Vector representations within 1 hour
8. THE Benchmarking_System SHALL support bulk import of at least 1000 market data records per API call
9. THE Benchmarking_System SHALL provide API authentication using API keys with rate limiting of 100 requests per hour

### Requirement 24: Model Versioning and A/B Testing

**User Story:** As an Admin, I want to test new AI model versions against production models, so that I can validate improvements before full deployment.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL support running multiple versions of Price_Prediction_ML models concurrently
2. WHEN A/B test is configured, THE VehicleIQ_Platform SHALL randomly assign assessments to model versions based on configured traffic split
3. THE VehicleIQ_Platform SHALL track MAPE separately for each model version
4. WHEN assessment is processed with test model, THE VehicleIQ_Platform SHALL log model version in Assessment_Record
5. THE VehicleIQ_Platform SHALL provide Admin interface for configuring A/B test parameters including traffic split and duration
6. WHEN A/B test completes, THE VehicleIQ_Platform SHALL generate comparison report showing MAPE, processing time, and error rates for each model version
7. THE VehicleIQ_Platform SHALL support promoting test model to production with single-click deployment
8. WHEN model version is changed, THE VehicleIQ_Platform SHALL maintain backward compatibility for reading historical Assessment_Record entries

### Requirement 25: Notification System

**User Story:** As a Lender, I want notifications when high-value assessments complete or fraud is detected, so that I can respond quickly to time-sensitive decisions.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL support notification delivery via email, SMS, and in-app channels
2. WHEN assessment completes for vehicle valued above configurable threshold, THE VehicleIQ_Platform SHALL send notification to subscribed users
3. WHEN fraud confidence score exceeds 60, THE VehicleIQ_Platform SHALL send immediate notification to Admin and requesting user
4. WHEN Manual_Review_Queue exceeds 20 pending items, THE VehicleIQ_Platform SHALL send notification to all Admin users
5. WHEN assessment remains in Manual_Review_Queue for more than 24 hours, THE VehicleIQ_Platform SHALL send escalation notification
6. THE VehicleIQ_Platform SHALL allow users to configure notification preferences including channels and thresholds
7. THE VehicleIQ_Platform SHALL implement notification rate limiting to prevent spam, with maximum 10 notifications per user per hour
8. WHEN notification delivery fails, THE VehicleIQ_Platform SHALL retry up to 3 times and log delivery failures


### Requirement 26: Search and Filter Capabilities

**User Story:** As a Lender, I want to search and filter historical assessments, so that I can analyze patterns and retrieve specific vehicle valuations.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL provide search functionality across Assessment_Record entries by VIN, make, model, year, and date range
2. THE VehicleIQ_Platform SHALL support filtering assessments by Vehicle_Health_Score range, fraud flags, and manual review status
3. THE VehicleIQ_Platform SHALL support filtering assessments by price range and valuation persona
4. WHEN search query is submitted, THE VehicleIQ_Platform SHALL return results within 3 seconds for queries spanning up to 1 year
5. THE VehicleIQ_Platform SHALL support sorting results by date, price, health score, and fraud confidence
6. THE VehicleIQ_Platform SHALL provide faceted search showing count of results by make, model, year, and fraud status
7. THE VehicleIQ_Platform SHALL support saving search filters as named queries for reuse
8. WHEN search returns more than 100 results, THE VehicleIQ_Platform SHALL implement pagination with configurable page size

### Requirement 27: Documentation and API Reference

**User Story:** As a developer, I want comprehensive API documentation and integration examples, so that I can integrate VehicleIQ with external systems.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL provide OpenAPI 3.0 specification for all REST API endpoints
2. THE VehicleIQ_Platform SHALL provide interactive API documentation using Swagger UI or similar tool
3. THE VehicleIQ_Platform SHALL include code examples for API integration in Python, JavaScript, and cURL
4. THE VehicleIQ_Platform SHALL document all request and response schemas with field descriptions and validation rules
5. THE VehicleIQ_Platform SHALL document authentication requirements and API key management
6. THE VehicleIQ_Platform SHALL provide webhook documentation for real-time assessment status updates
7. THE VehicleIQ_Platform SHALL include deployment guides for both cloud and local Docker configurations
8. THE VehicleIQ_Platform SHALL provide troubleshooting guide covering common errors and resolution steps

## Non-Functional Requirements

### Requirement 28: Scalability

**User Story:** As an Admin, I want the platform to scale to handle increasing assessment volumes, so that I can grow the business without performance degradation.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL support processing at least 1000 assessments per day without performance degradation
2. THE VehicleIQ_Platform SHALL support horizontal scaling by adding worker instances for assessment processing
3. THE VehicleIQ_Platform SHALL maintain sub-90-second processing time at 80% system capacity
4. THE VehicleIQ_Platform SHALL support database connection pooling with minimum 20 concurrent connections
5. THE VehicleIQ_Platform SHALL implement caching for frequently accessed data including vehicle registry and model predictions
6. WHEN system load exceeds 80% capacity, THE VehicleIQ_Platform SHALL log capacity warnings
7. THE VehicleIQ_Platform SHALL support auto-scaling configuration for cloud deployments


### Requirement 29: Reliability and Availability

**User Story:** As a Lender, I want the platform to be available during business hours, so that I can process assessments without service interruptions.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL maintain 99% uptime during business hours (9 AM to 6 PM IST, Monday to Saturday)
2. THE VehicleIQ_Platform SHALL implement health check endpoints returning status within 500 milliseconds
3. WHEN service degradation is detected, THE VehicleIQ_Platform SHALL automatically restart failed components
4. THE VehicleIQ_Platform SHALL implement database backup every 24 hours with 30-day retention
5. THE VehicleIQ_Platform SHALL support point-in-time recovery for database within 5-minute intervals
6. WHEN critical service fails, THE VehicleIQ_Platform SHALL send alert notification to Admin within 1 minute
7. THE VehicleIQ_Platform SHALL implement circuit breaker pattern for external API calls with 5-second timeout

### Requirement 30: Maintainability and Code Quality

**User Story:** As a developer, I want clean, well-documented code with comprehensive tests, so that I can maintain and extend the platform efficiently.

#### Acceptance Criteria

1. THE VehicleIQ_Platform SHALL maintain minimum 80% code coverage for unit tests
2. THE VehicleIQ_Platform SHALL include integration tests for all API endpoints
3. THE VehicleIQ_Platform SHALL include property-based tests for critical functions including price prediction, embedding generation, and OCR parsing
4. THE VehicleIQ_Platform SHALL follow consistent code style enforced by linters for Python (Black, Ruff) and TypeScript (ESLint, Prettier)
5. THE VehicleIQ_Platform SHALL include inline documentation for all public functions and classes
6. THE VehicleIQ_Platform SHALL implement continuous integration pipeline running tests on every commit
7. THE VehicleIQ_Platform SHALL generate test coverage reports accessible to developers
8. THE VehicleIQ_Platform SHALL maintain dependency versions in lock files with automated security vulnerability scanning

## Correctness Properties for Property-Based Testing

### Property 1: Price Prediction Monotonicity

FOR ALL vehicles with identical attributes except Vehicle_Health_Score, IF health_score_A > health_score_B, THEN predicted_price_A >= predicted_price_B

### Property 2: Embedding Round-Trip

FOR ALL vehicle records, generating an Embedding_Vector then searching for the most similar vehicle SHALL return the original vehicle as the top result with similarity score >= 0.99

### Property 3: OCR Round-Trip

FOR ALL OCR extractions, parsing the pretty-printed output SHALL produce data equivalent to the original extraction

### Property 4: Fraud Score Bounds

FOR ALL fraud detections, the fraud confidence score SHALL be between 0 and 100 inclusive

### Property 5: Health Score Bounds

FOR ALL health score calculations, the Vehicle_Health_Score SHALL be between 0 and 100 inclusive

### Property 6: Fraud Gate Consistency

FOR ALL assessments where fraud confidence score > 60, the Vehicle_Health_Score SHALL be capped at 30

### Property 7: Assessment Immutability

FOR ALL Assessment_Record entries, once created, the core assessment data SHALL remain unchanged (modifications only via append-only review notes)

### Property 8: Comparable Vehicle Similarity

FOR ALL comparable vehicle retrievals, the similarity scores SHALL be in descending order and all scores SHALL be between 0 and 1

### Property 9: Photo Quality Gate Idempotence

FOR ALL photos that pass Quality_Gate validation, running validation again SHALL produce the same pass result

### Property 10: Price Prediction Determinism

FOR ALL vehicles with identical attributes, generating price predictions multiple times SHALL produce identical results (given same model version and comparable dataset)

### Property 11: MAPE Calculation Correctness

FOR ALL MAPE calculations, the result SHALL equal the mean of absolute percentage errors: mean(|predicted - actual| / actual) * 100

### Property 12: Batch Processing Completeness

FOR ALL batch assessment requests with N valid records, the system SHALL produce exactly N assessment results (success or failure)

### Property 13: Role-Based Access Invariant

FOR ALL users with role R, attempting to access feature F not permitted for role R SHALL result in access denial

### Property 14: Notification Rate Limiting

FOR ALL users, the number of notifications delivered within any 1-hour window SHALL NOT exceed 10

### Property 15: API Fallback Consistency

FOR ALL assessments processed via fallback API, the output format and data structure SHALL match the primary API output format

---

## Summary

This requirements document defines 30 functional and non-functional requirements for VehicleIQ, covering fraud detection, price prediction, image intelligence, health scoring, multi-role access, real-time processing, audit trails, deployment flexibility, and system reliability. The document includes 15 correctness properties suitable for property-based testing to ensure system correctness and consistency.
