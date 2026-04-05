# Image Generation for VehicleIQ - Explained

## Quick Answer

**Are images generated?** Yes and No:
- ✅ **Sample images**: Programmatically generated for testing (odometer, VIN, registration)
- ✅ **Placeholder images**: Generated for vehicle angles (front, rear, sides, etc.)
- ❌ **Realistic car photos**: Not generated (use placeholders or real samples)

## Why This Approach?

### For MVP and Testing:
1. **Database testing** - Don't need real images, just file paths
2. **API testing** - Can test upload/download with any image
3. **OCR testing** - Synthetic images work great (readable text)
4. **Damage detection testing** - Placeholders sufficient for logic testing
5. **Demo purposes** - Sample images show the concept

### Real images only needed for:
- Production deployment with real users
- Realistic damage detection training
- Marketing materials and screenshots

## What Gets Generated

### ✅ Currently Generated (Programmatic)

**1. Odometer Images**
```
📸 odometer_15000.jpg  - Shows "015000 KM"
📸 odometer_45000.jpg  - Shows "045000 KM"
📸 odometer_75000.jpg  - Shows "075000 KM"
📸 odometer_120000.jpg - Shows "120000 KM"
```
- Black background with digital display
- OCR-friendly font
- Realistic layout

**2. VIN Plate Images**
```
📸 vin_plate_1.jpg - Shows "1HGBH41JXMN109186"
📸 vin_plate_2.jpg - Shows "2HGFG12648H542890"
📸 vin_plate_3.jpg - Shows "3VWFE21C04M000001"
```
- Silver plate background
- Bold black text
- Standard VIN format (17 characters)

**3. Registration Document Images**
```
📸 registration_1.jpg - DL01AB1234, Rajesh Kumar
📸 registration_2.jpg - MH02CD5678, Priya Sharma
📸 registration_3.jpg - KA03EF9012, Amit Patel
```
- White document background
- Indian registration format
- Owner name and date

**4. Placeholder Vehicle Images**
```
📸 front.jpg
📸 rear.jpg
📸 left_side.jpg
📸 right_side.jpg
📸 front_left_diagonal.jpg
📸 front_right_diagonal.jpg
📸 rear_left_diagonal.jpg
📸 rear_right_diagonal.jpg
📸 interior_dashboard.jpg
```
- Gray background with text label
- Shows angle name
- Consistent size (1024x768)

### ❌ Not Generated (Would Need Real Photos or AI)

**Realistic Car Photos:**
- Actual vehicle exteriors with damage
- Real interior conditions
- Authentic lighting and angles
- Genuine wear and tear

## How to Generate Images

### Step 1: Install Dependencies
```bash
# Pillow (PIL) is already in requirements.txt
pip install Pillow
```

### Step 2: Run Generation Script
```bash
cd /Users/praveenkumar/Documents/vehicle_iq
docker-compose exec backend python scripts/generate_sample_images.py
```

### Step 3: Verify Output
```bash
ls -lh backend/storage/samples/
```

Expected output:
```
odometer_15000.jpg
odometer_45000.jpg
odometer_75000.jpg
odometer_120000.jpg
vin_plate_1.jpg
vin_plate_2.jpg
vin_plate_3.jpg
registration_1.jpg
registration_2.jpg
registration_3.jpg
front.jpg
rear.jpg
left_side.jpg
right_side.jpg
front_left_diagonal.jpg
front_right_diagonal.jpg
rear_left_diagonal.jpg
rear_right_diagonal.jpg
interior_dashboard.jpg
```

## Using Generated Images

### In Assessment Seed Script (Future)
```python
# When creating assessment photos
SAMPLE_IMAGES = {
    "odometer": "storage/samples/odometer_45000.jpg",
    "vin_plate": "storage/samples/vin_plate_1.jpg",
    "registration_front": "storage/samples/registration_1.jpg",
    "front": "storage/samples/front.jpg",
    "rear": "storage/samples/rear.jpg",
    # ... etc
}

for angle in REQUIRED_ANGLES:
    photo = AssessmentPhoto(
        assessment_id=assessment.id,
        photo_angle=angle,
        storage_path=SAMPLE_IMAGES[angle],
        quality_passed=True
    )
```

### Testing OCR Service
```bash
# Test with generated odometer image
curl -X POST http://localhost:8001/ocr/extract/odometer \
  -F "file=@backend/storage/samples/odometer_45000.jpg"

# Expected response:
{
  "success": true,
  "odometer": {
    "value": 45000,
    "confidence": 0.95,
    "valid": true
  }
}
```

### Testing Photo Upload API
```bash
# Upload generated image
curl -X POST http://localhost:8000/v1/photos/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@backend/storage/samples/front.jpg" \
  -F "assessment_id=<uuid>" \
  -F "photo_angle=front"
```

## Options for Real Car Photos

### Option 1: Use Sample Photos (Recommended)
- Find 13 real car photos online (Creative Commons)
- Save to `backend/storage/samples/`
- Use for all assessments

**Sources:**
- Unsplash (free, high quality)
- Pexels (free, commercial use)
- Pixabay (free, no attribution)

### Option 2: Use Public Datasets
- Stanford Cars Dataset (16,185 images)
- CompCars Dataset (100,000+ images)
- Download and organize by angle

### Option 3: AI Generation (Advanced)
- Use Stable Diffusion API
- Generate unique images per assessment
- Costs money, slower

### Option 4: User Uploads (Production)
- Real users upload real photos
- Best for production deployment
- No generation needed

## Image Storage Strategy

### Development/Testing:
```
backend/storage/
├── samples/           # Generated sample images (committed to git)
│   ├── odometer_*.jpg
│   ├── vin_plate_*.jpg
│   ├── registration_*.jpg
│   └── *.jpg (angles)
└── assessments/       # User uploaded images (not in git)
    └── {assessment_id}/
        ├── front.jpg
        ├── rear.jpg
        └── ...
```

### Production:
```
# Cloud storage (Supabase Storage or S3)
/assessments/{assessment_id}/
├── front.jpg
├── rear.jpg
└── ...

# Or local filesystem with same structure
```

## Summary

**Current Implementation:**
- ✅ Programmatic generation for OCR-testable images (odometer, VIN, registration)
- ✅ Placeholder generation for vehicle angles
- ✅ Sufficient for testing all APIs and business logic
- ✅ Fast, free, reproducible

**For Production:**
- Use real sample photos (13 angles) for demos
- Accept user uploads for real assessments
- Optional: AI generation for synthetic test data

**Bottom Line:** You don't need realistic car photos to build and test VehicleIQ. The generated images are perfect for development, and you can add real photos later when needed for demos or production.
