# Best Strategy: Images, Dataset & ML Models for VehicleIQ

## Original Plan vs Best Strategy

### What Was Originally Planned

The original design specified:

**Price Prediction:**
- 4-layer model: Base price → Condition adjustment → RAG comparables → **Quantile Regression**
- Use scikit-learn QuantileRegressor
- No XGBoost mentioned

**Images:**
- 13 required photo angles
- Quality gate validation
- OCR extraction (PaddleOCR)
- Damage detection (YOLOv8n)
- No specific strategy for image generation

**Dataset:**
- Proprietary comparable vehicles dataset
- Market data integration
- Outcome pairing (predicted vs actual)
- MAPE tracking for benchmarking

## Best Strategy (Revised & Practical)

### 🎯 Strategy 1: Images

#### Phase 1-2 (Current - MVP): Synthetic + Placeholders ✅

**What to use:**
- ✅ Programmatically generated images (odometer, VIN, registration)
- ✅ Placeholder images for vehicle angles
- ✅ 5-10 real sample photos from free sources

**Why:**
- Fast development
- No licensing issues
- Sufficient for testing all APIs
- OCR works perfectly with synthetic images

**Implementation:**
```bash
# Already built!
docker-compose exec backend python scripts/generate_sample_images.py
```

#### Phase 3-5 (Testing): Real Sample Dataset

**What to use:**
- Download 50-100 real car photos from Unsplash/Pexels
- Organize by angle (front, rear, sides, etc.)
- Reuse across assessments with variation

**Sources:**
- Unsplash: https://unsplash.com/s/photos/car
- Pexels: https://www.pexels.com/search/car/
- Pixabay: https://pixabay.com/images/search/car/

**Script to download:**
```python
# backend/scripts/download_sample_photos.py
import requests
from pathlib import Path

UNSPLASH_URLS = [
    "https://images.unsplash.com/photo-car-front-1",
    "https://images.unsplash.com/photo-car-rear-2",
    # ... 50 URLs
]

def download_photos():
    storage = Path("backend/storage/real_samples")
    storage.mkdir(exist_ok=True)
    
    for i, url in enumerate(UNSPLASH_URLS):
        response = requests.get(url)
        with open(storage / f"car_{i:03d}.jpg", "wb") as f:
            f.write(response.content)
```

#### Phase 6+ (Production): User Uploads + Optional AI

**What to use:**
- Real user uploads (primary)
- Optional: Stable Diffusion for synthetic test data
- Optional: Public datasets for training damage detection

**For Damage Detection Training:**
- Use public datasets:
  - Car Damage Detection Dataset (Kaggle)
  - COCO dataset (filtered for vehicles)
  - Custom labeled dataset (100-500 images)

### 🎯 Strategy 2: Price Prediction Model

#### Original Plan: Quantile Regression Only

```python
# Layer 4: Quantile Regression
from sklearn.linear_model import QuantileRegressor

# Fit on comparable prices
qr_10 = QuantileRegressor(quantile=0.10)
qr_50 = QuantileRegressor(quantile=0.50)
qr_90 = QuantileRegressor(quantile=0.90)

# Predict
p10 = qr_10.predict(features)
p50 = qr_50.predict(features)
p90 = qr_90.predict(features)
```

**Pros:**
- Simple, interpretable
- Fast training
- Good for quantile predictions

**Cons:**
- Limited feature learning
- May not capture complex patterns
- Requires good feature engineering

#### Best Strategy: Hybrid Approach

**Phase 4 (Initial): Quantile Regression (As Planned)**

Use scikit-learn QuantileRegressor for MVP:

```python
# backend/app/services/price_prediction.py

from sklearn.linear_model import QuantileRegressor
import numpy as np

class PricePredictionML:
    def __init__(self):
        self.qr_10 = QuantileRegressor(quantile=0.10, alpha=0.1)
        self.qr_50 = QuantileRegressor(quantile=0.50, alpha=0.1)
        self.qr_90 = QuantileRegressor(quantile=0.90, alpha=0.1)
    
    def fit(self, comparable_prices, features):
        """Fit quantile regressors on comparable prices."""
        X = np.array(features).reshape(-1, 1)
        y = np.array(comparable_prices)
        
        self.qr_10.fit(X, y)
        self.qr_50.fit(X, y)
        self.qr_90.fit(X, y)
    
    def predict(self, health_score):
        """Predict P10, P50, P90 based on health score."""
        X = np.array([[health_score]])
        
        return {
            "p10": float(self.qr_10.predict(X)[0]),
            "p50": float(self.qr_50.predict(X)[0]),
            "p90": float(self.qr_90.predict(X)[0])
        }
```

**Phase 5+ (Enhanced): Add XGBoost for Better Accuracy**

Add XGBoost as an optional enhancement:

```python
# backend/app/services/price_prediction_xgb.py

import xgboost as xgb
from sklearn.model_selection import train_test_split

class PricePredictionXGB:
    def __init__(self):
        # XGBoost for P50 (median) prediction
        self.model_p50 = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1
        )
        
        # Quantile regression for P10, P90
        self.model_p10 = xgb.XGBRegressor(
            objective='reg:quantileerror',
            quantile_alpha=0.10,
            n_estimators=100
        )
        
        self.model_p90 = xgb.XGBRegressor(
            objective='reg:quantileerror',
            quantile_alpha=0.90,
            n_estimators=100
        )
    
    def fit(self, X_train, y_train):
        """Train XGBoost models."""
        self.model_p50.fit(X_train, y_train)
        self.model_p10.fit(X_train, y_train)
        self.model_p90.fit(X_train, y_train)
    
    def predict(self, features):
        """Predict with XGBoost."""
        return {
            "p10": float(self.model_p10.predict([features])[0]),
            "p50": float(self.model_p50.predict([features])[0]),
            "p90": float(self.model_p90.predict([features])[0])
        }
```

**Why Hybrid?**
- Start simple with Quantile Regression (MVP)
- Add XGBoost later for better accuracy
- A/B test both models
- Choose best performer based on MAPE

**Feature Engineering:**
```python
def extract_features(vehicle, health_score, comparables):
    """Extract features for price prediction."""
    return {
        # Vehicle features
        "age_years": 2024 - vehicle.year,
        "mileage": vehicle.mileage,
        "health_score": health_score,
        
        # Comparable features
        "avg_comparable_price": np.mean([c.price for c in comparables]),
        "min_comparable_price": np.min([c.price for c in comparables]),
        "max_comparable_price": np.max([c.price for c in comparables]),
        "comparable_count": len(comparables),
        
        # Market features
        "location_factor": get_location_factor(vehicle.location),
        "fuel_type_factor": get_fuel_type_factor(vehicle.fuel_type),
        "transmission_factor": get_transmission_factor(vehicle.transmission),
        
        # Categorical encoded
        "make_encoded": encode_make(vehicle.make),
        "model_encoded": encode_model(vehicle.model),
    }
```

### 🎯 Strategy 3: Dataset for Training & Benchmarking

#### Phase 1-3: Synthetic Dataset (Current) ✅

**What we have:**
- 1,000 vehicle registry entries
- 2,000 comparable vehicles with embeddings
- Realistic price distributions

**Sufficient for:**
- Testing RAG comparable retrieval
- Testing quantile regression logic
- Testing API endpoints
- Demo purposes

#### Phase 4-5: Enhanced Synthetic + Real Market Data

**Approach 1: Web Scraping (Recommended)**

Scrape Indian car listing websites:

```python
# backend/scripts/scrape_market_data.py

import httpx
from bs4 import BeautifulSoup
import asyncio

SOURCES = [
    "https://www.cars24.com/buy-used-cars",
    "https://www.olx.in/cars",
    "https://www.cardekho.com/used-cars",
]

async def scrape_listings():
    """Scrape car listings from Indian websites."""
    async with httpx.AsyncClient() as client:
        for source in SOURCES:
            response = await client.get(source)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract: make, model, year, price, mileage, location
            listings = parse_listings(soup)
            
            # Store in comparable_vehicles table
            await store_listings(listings)
```

**Legal Considerations:**
- Check robots.txt
- Respect rate limits
- Use for research/testing only
- Don't redistribute scraped data

**Approach 2: Public Datasets**

Use existing car price datasets:

**Sources:**
- Kaggle: "Used Car Price Prediction" datasets
- UCI ML Repository: "Automobile Data Set"
- GitHub: Various car price datasets

**Adapt to Indian market:**
```python
# Convert USD to INR
# Map makes/models to Indian equivalents
# Adjust for Indian market conditions
```

**Approach 3: Manual Data Entry (Small Scale)**

For initial testing:
- Manually collect 100-200 real listings
- From Cars24, OLX, CarDekho
- Store in spreadsheet
- Import to database

#### Phase 6+: Production Dataset Strategy

**Outcome Pairing (Key for Accuracy):**

```python
# When assessment completes and vehicle sells:
POST /v1/benchmarking/outcome-pairing
{
    "assessment_id": "uuid",
    "actual_transaction_price": 850000,
    "transaction_date": "2024-04-15",
    "transaction_type": "sale"  # or "loan", "insurance"
}

# This:
1. Updates assessment with actual price
2. Calculates prediction error
3. Updates MAPE metrics
4. Adds to training dataset for model improvement
```

**Continuous Learning:**
```python
# Nightly job
async def retrain_models():
    """Retrain price prediction models with new data."""
    # Get all assessments with outcomes
    assessments = await get_assessments_with_outcomes()
    
    # Extract features and targets
    X, y = prepare_training_data(assessments)
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train new model version
    model = train_model(X_train, y_train)
    
    # Evaluate
    mape = calculate_mape(model, X_test, y_test)
    
    # If better than current model, promote
    if mape < current_model_mape:
        promote_model(model)
```

## Recommended Implementation Timeline

### Phase 2 (Current - Week 3): ✅
- ✅ Synthetic images (odometer, VIN, registration)
- ✅ Placeholder vehicle images
- ✅ Synthetic comparable dataset (2,000 records)

### Phase 3 (Week 4):
- Download 50-100 real car photos
- Organize by angle
- Test with real images

### Phase 4 (Week 5):
- Implement Quantile Regression (as planned)
- Use synthetic dataset for training
- Test price prediction API

### Phase 5 (Week 6-7):
- Scrape 500-1,000 real listings (or use public dataset)
- Generate embeddings for real data
- Retrain models with real data
- Implement MAPE tracking

### Phase 6+ (Week 8+):
- Implement outcome pairing
- Add XGBoost as alternative model
- A/B test Quantile Regression vs XGBoost
- Continuous model improvement

## Summary: Best Strategy

### Images:
1. **MVP**: Synthetic + placeholders (done ✅)
2. **Testing**: 50-100 real samples from Unsplash/Pexels
3. **Production**: User uploads + optional AI generation

### Price Prediction:
1. **MVP**: Quantile Regression (as planned)
2. **Enhanced**: Add XGBoost for comparison
3. **Production**: A/B test both, choose best performer

### Dataset:
1. **MVP**: Synthetic 2,000 comparables (done ✅)
2. **Testing**: Scrape 500-1,000 real listings
3. **Production**: Outcome pairing + continuous learning

### Why This Strategy?

**Pragmatic:**
- Start simple, add complexity as needed
- Test with synthetic data first
- Validate with real data later

**Cost-Effective:**
- Free synthetic data
- Free real samples (Unsplash/Pexels)
- Free web scraping (for research)

**Scalable:**
- Synthetic data for unlimited testing
- Real data for accuracy validation
- Outcome pairing for continuous improvement

**Compliant:**
- No licensing issues with synthetic data
- Proper attribution for real samples
- Respect robots.txt for scraping

**Bottom Line:** The original plan (Quantile Regression) is solid for MVP. Add XGBoost later if needed. Use synthetic data for development, real data for validation, and outcome pairing for production accuracy.
