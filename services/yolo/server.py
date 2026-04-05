"""YOLOv8n damage detection microservice."""

from fastapi import FastAPI, File, UploadFile, HTTPException
from ultralytics import YOLO
import numpy as np
from PIL import Image
import io

app = FastAPI(title="YOLO Damage Detection Service")

# Initialize YOLOv8n model
model = YOLO('yolov8n.pt')

# Damage classes
DAMAGE_CLASSES = [
    "dent", "scratch", "rust", "crack", 
    "missing_part", "panel_misalignment", "paint_damage"
]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "yolo"}


@app.post("/detect")
async def detect_damage(file: UploadFile = File(...)):
    """Detect vehicle damage in image."""
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Perform detection
        results = model(image, conf=0.5)
        
        # Extract detections
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                # Calculate severity based on box area
                area = (x2 - x1) * (y2 - y1)
                image_area = image.width * image.height
                damage_ratio = area / image_area
                
                if damage_ratio < 0.05:
                    severity = "minor"
                elif damage_ratio < 0.15:
                    severity = "moderate"
                else:
                    severity = "severe"
                
                detections.append({
                    "class_name": DAMAGE_CLASSES[class_id % len(DAMAGE_CLASSES)],
                    "confidence": confidence,
                    "bbox": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    },
                    "severity": severity,
                })
        
        return {
            "success": True,
            "detections": detections,
            "count": len(detections),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
