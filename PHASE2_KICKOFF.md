# Phase 2: Image Intelligence - Development Plan

## Overview
Phase 2 focuses on building the **Image Intelligence** capability - the foundation for analyzing vehicle photos.

## Goals
Build the ability to:
1. Upload and validate vehicle photos (quality gate)
2. Extract text from photos using OCR (odometer, VIN, registration)
3. Detect damage in photos using AI
4. Process 13 required photo angles for complete assessment

## What We'll Build

### 1. Photo Upload & Quality Gate (Task 7)
**Purpose:** Ensure photos are good enough for AI analysis

**Features:**
- Upload endpoint for vehicle photos
- Quality checks:
  - Blur detection (is photo sharp?)
  - Lighting check (too dark/bright?)
  - Framing check (is vehicle in frame?)
  - Resolution check (minimum 1024x768)
- Store photos in backend storage
- Track 13 required angles (front, rear, left, right, etc.)

**API Endpoint:**
```
POST /v1/photos/upload
- Accepts: multipart/form-data with image
- Returns: quality_score, passed/failed, feedback
```

### 2. PaddleOCR Service (Task 6)
**Purpose:** Extract text from photos automatically

**Features:**
- Standalone OCR microservice (port 8001)
- Extract from photos:
  - Odometer reading (0-999,999 km)
  - VIN (17-character vehicle ID)
  - Registration number (Indian format)
  - Owner name and registration date
- Validate extracted data
- Flag suspicious readings

**API Endpoint:**
```
POST /ocr/extract
- Accepts: image file
- Returns: extracted text with confidence scores
```

### 3. YOLOv8n Damage Detection (Task 8)
**Purpose:** Automatically detect vehicle damage

**Features:**
- Standalone YOLO microservice (port 8002)
- Detect 7 damage types:
  - Dent, Scratch, Rust, Crack
  - Missing part, Panel misalignment, Paint damage
- Provide bounding boxes (where damage is)
- Calculate severity (minor/moderate/severe)
- Aggregate damage across all 13 photos

**API Endpoint:**
```
POST /damage/detect
- Accepts: image file
- Returns: damage detections with locations and severity
```

### 4. Image Intelligence API (Task 9)
**Purpose:** Orchestrate the complete photo processing pipeline

**Features:**
- Process photos through quality gate → OCR → damage detection
- Parallel processing for speed
- Store results in database
- Track processing progress

**API Endpoints:**
```
POST /v1/assessments/{id}/photos
- Upload photo for an assessment
- Automatically process through pipeline

GET /v1/assessments/{id}/photos
- Get all photos and their analysis results
```

## Implementation Order

### Week 3 - Day 1-2: Photo Quality Gate
- [ ] Create photo upload endpoint
- [ ] Implement quality checks (blur, lighting, framing, resolution)
- [ ] Store photos in backend/storage/
- [ ] Test with sample vehicle photos

### Week 3 - Day 3-4: PaddleOCR Service
- [ ] Build PaddleOCR Docker service
- [ ] Implement OCR extraction functions
- [ ] Add validation and flagging
- [ ] Test with odometer/VIN photos

### Week 3 - Day 5-6: YOLO Damage Detection
- [ ] Build YOLOv8n Docker service
- [ ] Implement damage detection
- [ ] Calculate severity levels
- [ ] Test with damaged vehicle photos

### Week 3 - Day 7: Integration & Testing
- [ ] Create image intelligence API endpoints
- [ ] Integrate all three services
- [ ] End-to-end testing
- [ ] Property-based tests

## Technical Architecture

```
User Upload Photo
      ↓
Quality Gate Check (Backend)
      ↓ (if passed)
   ┌──┴──┐
   ↓     ↓
OCR     YOLO
(8001)  (8002)
   ↓     ↓
   └──┬──┘
      ↓
Store Results (Database)
```

## Success Criteria

By end of Phase 2, we should be able to:
- ✅ Upload 13 vehicle photos
- ✅ Automatically extract odometer, VIN, registration
- ✅ Automatically detect and locate damage
- ✅ Get quality scores for each photo
- ✅ See complete photo analysis results

## Test Data Needed

1. Sample vehicle photos (13 angles)
2. Photos with clear odometer readings
3. Photos with VIN plates
4. Photos with various damage types
5. Poor quality photos (for quality gate testing)

## Next Steps

Starting with **Task 7.1**: Create quality gate validation functions
- Implement blur detection
- Implement lighting check
- Implement framing check
- Implement resolution check

Ready to begin! 🚀
