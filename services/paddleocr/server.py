"""PaddleOCR microservice for text extraction from vehicle photos."""

from fastapi import FastAPI, File, UploadFile, HTTPException
from paddleocr import PaddleOCR
import numpy as np
import cv2
from typing import Dict, List, Optional
import re
from datetime import datetime

app = FastAPI(
    title="PaddleOCR Service",
    description="OCR text extraction service for VehicleIQ",
    version="1.0.0"
)

# Initialize PaddleOCR with English and Hindi support
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en',  # Primary language
    use_gpu=False,  # Set to True if GPU available
    show_log=False
)


class OCRExtractor:
    """OCR extraction and validation functions."""
    
    # Validation patterns
    VIN_PATTERN = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')  # 17 alphanumeric, excluding I, O, Q
    INDIAN_REG_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$')
    ODOMETER_PATTERN = re.compile(r'\d{1,6}')
    
    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> List[Dict]:
        """
        Extract all text from image using PaddleOCR.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            List of detected text with bounding boxes and confidence
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
        
        # Run OCR
        result = ocr.ocr(img, cls=True)
        
        if not result or not result[0]:
            return []
        
        # Format results
        extracted_texts = []
        for line in result[0]:
            bbox = line[0]  # Bounding box coordinates
            text_info = line[1]  # (text, confidence)
            
            extracted_texts.append({
                "text": text_info[0],
                "confidence": float(text_info[1]),
                "bbox": [[int(coord) for coord in point] for point in bbox]
            })
        
        return extracted_texts
    
    @staticmethod
    def extract_odometer(extracted_texts: List[Dict]) -> Optional[Dict]:
        """
        Extract odometer reading from OCR results.
        
        Args:
            extracted_texts: List of extracted text with confidence
            
        Returns:
            Dict with odometer value and validation status
        """
        for item in extracted_texts:
            text = item["text"].replace(",", "").replace(" ", "")
            matches = OCRExtractor.ODOMETER_PATTERN.findall(text)
            
            for match in matches:
                value = int(match)
                # Validate range (0-999,999 km)
                if 0 <= value <= 999999:
                    return {
                        "value": value,
                        "raw_text": item["text"],
                        "confidence": item["confidence"],
                        "valid": True,
                        "validation_message": "Odometer reading is within valid range"
                    }
                else:
                    return {
                        "value": value,
                        "raw_text": item["text"],
                        "confidence": item["confidence"],
                        "valid": False,
                        "validation_message": f"Odometer reading {value} is out of range (0-999,999)"
                    }
        
        return None
    
    @staticmethod
    def extract_vin(extracted_texts: List[Dict]) -> Optional[Dict]:
        """
        Extract VIN (Vehicle Identification Number) from OCR results.
        
        Args:
            extracted_texts: List of extracted text with confidence
            
        Returns:
            Dict with VIN and validation status
        """
        for item in extracted_texts:
            text = item["text"].replace(" ", "").replace("-", "").upper()
            
            # Check if text matches VIN pattern
            if OCRExtractor.VIN_PATTERN.match(text):
                return {
                    "value": text,
                    "raw_text": item["text"],
                    "confidence": item["confidence"],
                    "valid": True,
                    "validation_message": "VIN format is valid"
                }
            
            # Check if text is close to VIN length (might have OCR errors)
            if 15 <= len(text) <= 19:
                # Remove invalid characters
                cleaned = re.sub(r'[^A-HJ-NPR-Z0-9]', '', text)
                if len(cleaned) == 17:
                    return {
                        "value": cleaned,
                        "raw_text": item["text"],
                        "confidence": item["confidence"],
                        "valid": True,
                        "validation_message": "VIN extracted with character cleaning"
                    }
        
        return None
    
    @staticmethod
    def extract_registration(extracted_texts: List[Dict]) -> Optional[Dict]:
        """
        Extract vehicle registration number (Indian format) from OCR results.
        
        Args:
            extracted_texts: List of extracted text with confidence
            
        Returns:
            Dict with registration number and validation status
        """
        for item in extracted_texts:
            text = item["text"].replace(" ", "").replace("-", "").upper()
            
            # Check if text matches Indian registration pattern
            if OCRExtractor.INDIAN_REG_PATTERN.match(text):
                return {
                    "value": text,
                    "raw_text": item["text"],
                    "confidence": item["confidence"],
                    "valid": True,
                    "validation_message": "Registration number format is valid"
                }
        
        return None
    
    @staticmethod
    def extract_document_fields(extracted_texts: List[Dict]) -> Dict:
        """
        Extract owner name and registration date from document.
        
        Args:
            extracted_texts: List of extracted text with confidence
            
        Returns:
            Dict with owner name and registration date if found
        """
        result = {
            "owner_name": None,
            "registration_date": None
        }
        
        # Look for common field labels
        for i, item in enumerate(extracted_texts):
            text_lower = item["text"].lower()
            
            # Look for owner name
            if any(keyword in text_lower for keyword in ["owner", "name", "registered to"]):
                # Next text item might be the name
                if i + 1 < len(extracted_texts):
                    next_text = extracted_texts[i + 1]["text"]
                    # Basic validation: name should have letters and be reasonable length
                    if re.search(r'[a-zA-Z]{2,}', next_text) and 3 <= len(next_text) <= 50:
                        result["owner_name"] = {
                            "value": next_text,
                            "confidence": extracted_texts[i + 1]["confidence"]
                        }
            
            # Look for registration date
            if any(keyword in text_lower for keyword in ["date", "registered on", "reg date"]):
                # Next text item might be the date
                if i + 1 < len(extracted_texts):
                    next_text = extracted_texts[i + 1]["text"]
                    # Look for date patterns (DD/MM/YYYY, DD-MM-YYYY, etc.)
                    date_match = re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', next_text)
                    if date_match:
                        result["registration_date"] = {
                            "value": date_match.group(),
                            "confidence": extracted_texts[i + 1]["confidence"]
                        }
        
        return result


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "paddleocr",
        "version": "1.0.0"
    }


@app.post("/ocr/extract")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract all text from an image.
    
    Args:
        file: Image file (JPEG/PNG)
        
    Returns:
        All extracted text with bounding boxes and confidence scores
    """
    try:
        # Read file content
        content = await file.read()
        
        # Extract text
        extracted_texts = OCRExtractor.extract_text_from_image(content)
        
        return {
            "success": True,
            "extracted_texts": extracted_texts,
            "total_detections": len(extracted_texts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")


@app.post("/ocr/extract/odometer")
async def extract_odometer(file: UploadFile = File(...)):
    """
    Extract odometer reading from an image.
    
    Args:
        file: Image file of odometer
        
    Returns:
        Odometer reading with validation
    """
    try:
        content = await file.read()
        extracted_texts = OCRExtractor.extract_text_from_image(content)
        odometer = OCRExtractor.extract_odometer(extracted_texts)
        
        if odometer:
            return {
                "success": True,
                "odometer": odometer
            }
        else:
            return {
                "success": False,
                "message": "No odometer reading detected",
                "extracted_texts": extracted_texts
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Odometer extraction failed: {str(e)}")


@app.post("/ocr/extract/vin")
async def extract_vin(file: UploadFile = File(...)):
    """
    Extract VIN from an image.
    
    Args:
        file: Image file of VIN plate
        
    Returns:
        VIN with validation
    """
    try:
        content = await file.read()
        extracted_texts = OCRExtractor.extract_text_from_image(content)
        vin = OCRExtractor.extract_vin(extracted_texts)
        
        if vin:
            return {
                "success": True,
                "vin": vin
            }
        else:
            return {
                "success": False,
                "message": "No VIN detected",
                "extracted_texts": extracted_texts
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VIN extraction failed: {str(e)}")


@app.post("/ocr/extract/registration")
async def extract_registration(file: UploadFile = File(...)):
    """
    Extract registration number from an image.
    
    Args:
        file: Image file of registration plate/document
        
    Returns:
        Registration number with validation
    """
    try:
        content = await file.read()
        extracted_texts = OCRExtractor.extract_text_from_image(content)
        registration = OCRExtractor.extract_registration(extracted_texts)
        
        if registration:
            return {
                "success": True,
                "registration": registration
            }
        else:
            return {
                "success": False,
                "message": "No registration number detected",
                "extracted_texts": extracted_texts
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration extraction failed: {str(e)}")


@app.post("/ocr/extract/document")
async def extract_document(file: UploadFile = File(...)):
    """
    Extract owner name and registration date from document.
    
    Args:
        file: Image file of registration document
        
    Returns:
        Owner name and registration date if found
    """
    try:
        content = await file.read()
        extracted_texts = OCRExtractor.extract_text_from_image(content)
        document_fields = OCRExtractor.extract_document_fields(extracted_texts)
        
        return {
            "success": True,
            "document_fields": document_fields,
            "all_extracted_texts": extracted_texts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document extraction failed: {str(e)}")


@app.post("/ocr/extract/all")
async def extract_all_fields(file: UploadFile = File(...)):
    """
    Extract all possible fields from an image.
    
    Args:
        file: Image file
        
    Returns:
        All extracted fields (odometer, VIN, registration, document fields)
    """
    try:
        content = await file.read()
        extracted_texts = OCRExtractor.extract_text_from_image(content)
        
        # Try to extract all fields
        odometer = OCRExtractor.extract_odometer(extracted_texts)
        vin = OCRExtractor.extract_vin(extracted_texts)
        registration = OCRExtractor.extract_registration(extracted_texts)
        document_fields = OCRExtractor.extract_document_fields(extracted_texts)
        
        return {
            "success": True,
            "odometer": odometer,
            "vin": vin,
            "registration": registration,
            "document_fields": document_fields,
            "raw_extractions": extracted_texts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Field extraction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
