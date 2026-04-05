"""PaddleOCR microservice."""

from fastapi import FastAPI, File, UploadFile, HTTPException
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io
import re

app = FastAPI(title="PaddleOCR Service")

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "paddleocr"}


@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    """Extract text from image using OCR."""
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        img_array = np.array(image)
        
        # Perform OCR
        result = ocr.ocr(img_array, cls=True)
        
        # Extract text
        extracted_text = []
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            extracted_text.append({
                "text": text,
                "confidence": confidence,
            })
        
        return {
            "success": True,
            "extracted_text": extracted_text,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract/odometer")
async def extract_odometer(file: UploadFile = File(...)):
    """Extract odometer reading from dashboard photo."""
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        img_array = np.array(image)
        
        # Perform OCR
        result = ocr.ocr(img_array, cls=True)
        
        # Extract odometer reading (look for numbers)
        odometer_pattern = r'\d{1,6}'
        odometer_reading = None
        
        for line in result[0]:
            text = line[1][0]
            match = re.search(odometer_pattern, text)
            if match:
                reading = int(match.group())
                if 0 <= reading <= 999999:
                    odometer_reading = reading
                    break
        
        return {
            "success": True,
            "odometer_reading": odometer_reading,
            "valid": odometer_reading is not None and 0 <= odometer_reading <= 999999,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
