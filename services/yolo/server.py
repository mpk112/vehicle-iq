"""YOLOv8n microservice for vehicle damage detection."""

from fastapi import FastAPI, File, UploadFile, HTTPException
from ultralytics import YOLO
import numpy as np
import cv2
from typing import Dict, List
from enum import Enum

app = FastAPI(
    title="YOLOv8n Damage Detection Service",
    description="Vehicle damage detection service for VehicleIQ",
    version="1.0.0"
)

# Initialize YOLOv8n model
# Note: In production, you would train a custom model on vehicle damage dataset
# For now, we'll use the base model and map classes to damage types
model = YOLO('yolov8n.pt')


class DamageType(str, Enum):
    """7 damage types for vehicle assessment."""
    DENT = "dent"
    SCRATCH = "scratch"
    CRACK = "crack"
    RUST = "rust"
    BROKEN_PART = "broken_part"
    PAINT_DAMAGE = "paint_damage"
    MISSING_PART = "missing_part"


class DamageSeverity(str, Enum):
    """Damage severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class DamageDetector:
    """Damage detection and analysis functions."""
    
    @staticmethod
    def detect_damage(image_bytes: bytes, confidence_threshold: float = 0.25) -> List[Dict]:
        """
        Detect damage in vehicle image using YOLOv8n.
        
        Args:
            image_bytes: Image file bytes
            confidence_threshold: Minimum confidence for detection (0-1)
            
        Returns:
            List of detected damage with bounding boxes, type, and severity
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
        
        # Run YOLO detection
        results = model(img, conf=confidence_threshold)
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                
                # Map YOLO class to damage type
                # Note: This is a placeholder mapping. In production, you would
                # train a custom model with specific damage classes
                damage_type = DamageDetector._map_class_to_damage_type(class_id)
                
                # Calculate damage severity based on size and confidence
                bbox_area = (x2 - x1) * (y2 - y1)
                image_area = img.shape[0] * img.shape[1]
                damage_ratio = bbox_area / image_area
                
                severity = DamageDetector._calculate_severity(damage_ratio, confidence)
                
                detections.append({
                    "damage_type": damage_type,
                    "severity": severity,
                    "confidence": confidence,
                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2)
                    },
                    "area_percentage": round(damage_ratio * 100, 2)
                })
        
        return detections
    
    @staticmethod
    def _map_class_to_damage_type(class_id: int) -> str:
        """
        Map YOLO class ID to damage type.
        
        Note: This is a placeholder. In production, train a custom model
        with specific damage classes.
        
        Args:
            class_id: YOLO class ID
            
        Returns:
            Damage type string
        """
        # Placeholder mapping - in production, use custom trained model
        damage_mapping = {
            0: DamageType.DENT,
            1: DamageType.SCRATCH,
            2: DamageType.CRACK,
            3: DamageType.RUST,
            4: DamageType.BROKEN_PART,
            5: DamageType.PAINT_DAMAGE,
            6: DamageType.MISSING_PART,
        }
        
        # Default to dent if class not in mapping
        return damage_mapping.get(class_id % 7, DamageType.DENT)
    
    @staticmethod
    def _calculate_severity(damage_ratio: float, confidence: float) -> str:
        """
        Calculate damage severity based on size and confidence.
        
        Args:
            damage_ratio: Damage area / total image area
            confidence: Detection confidence (0-1)
            
        Returns:
            Severity level (minor, moderate, severe)
        """
        # Weighted score: 70% size, 30% confidence
        severity_score = (damage_ratio * 0.7) + (confidence * 0.3)
        
        if severity_score < 0.15:
            return DamageSeverity.MINOR
        elif severity_score < 0.35:
            return DamageSeverity.MODERATE
        else:
            return DamageSeverity.SEVERE
    
    @staticmethod
    def aggregate_damage_summary(detections: List[Dict]) -> Dict:
        """
        Aggregate damage detections into summary statistics.
        
        Args:
            detections: List of damage detections
            
        Returns:
            Summary with counts by type and severity
        """
        summary = {
            "total_damages": len(detections),
            "by_type": {},
            "by_severity": {
                DamageSeverity.MINOR: 0,
                DamageSeverity.MODERATE: 0,
                DamageSeverity.SEVERE: 0
            },
            "total_affected_area_percentage": 0.0,
            "max_severity": None
        }
        
        if not detections:
            return summary
        
        # Count by type and severity
        for detection in detections:
            damage_type = detection["damage_type"]
            severity = detection["severity"]
            
            # Count by type
            if damage_type not in summary["by_type"]:
                summary["by_type"][damage_type] = 0
            summary["by_type"][damage_type] += 1
            
            # Count by severity
            summary["by_severity"][severity] += 1
            
            # Sum affected area
            summary["total_affected_area_percentage"] += detection["area_percentage"]
        
        # Determine max severity
        if summary["by_severity"][DamageSeverity.SEVERE] > 0:
            summary["max_severity"] = DamageSeverity.SEVERE
        elif summary["by_severity"][DamageSeverity.MODERATE] > 0:
            summary["max_severity"] = DamageSeverity.MODERATE
        elif summary["by_severity"][DamageSeverity.MINOR] > 0:
            summary["max_severity"] = DamageSeverity.MINOR
        
        # Round total affected area
        summary["total_affected_area_percentage"] = round(
            summary["total_affected_area_percentage"], 2
        )
        
        return summary


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "yolo-damage-detection",
        "version": "1.0.0",
        "model": "yolov8n"
    }


@app.post("/damage/detect")
async def detect_damage(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.25
):
    """
    Detect damage in vehicle image.
    
    Args:
        file: Image file (JPEG/PNG)
        confidence_threshold: Minimum confidence for detection (0-1)
        
    Returns:
        List of detected damage with bounding boxes and severity
    """
    try:
        # Validate confidence threshold
        if not 0 <= confidence_threshold <= 1:
            raise HTTPException(
                status_code=400,
                detail="Confidence threshold must be between 0 and 1"
            )
        
        # Read file content
        content = await file.read()
        
        # Detect damage
        detections = DamageDetector.detect_damage(content, confidence_threshold)
        
        # Generate summary
        summary = DamageDetector.aggregate_damage_summary(detections)
        
        return {
            "success": True,
            "detections": detections,
            "summary": summary
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Damage detection failed: {str(e)}"
        )


@app.post("/damage/batch")
async def detect_damage_batch(files: List[UploadFile] = File(...)):
    """
    Detect damage across multiple images (e.g., 13 required angles).
    
    Args:
        files: List of image files
        
    Returns:
        Aggregated damage analysis across all images
    """
    try:
        all_detections = []
        per_image_results = []
        
        for idx, file in enumerate(files):
            content = await file.read()
            detections = DamageDetector.detect_damage(content)
            
            per_image_results.append({
                "image_index": idx,
                "filename": file.filename,
                "detections": detections,
                "summary": DamageDetector.aggregate_damage_summary(detections)
            })
            
            all_detections.extend(detections)
        
        # Overall summary across all images
        overall_summary = DamageDetector.aggregate_damage_summary(all_detections)
        
        return {
            "success": True,
            "total_images": len(files),
            "per_image_results": per_image_results,
            "overall_summary": overall_summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch damage detection failed: {str(e)}"
        )


@app.get("/damage/types")
async def get_damage_types():
    """
    Get list of supported damage types.
    
    Returns:
        List of damage types and severity levels
    """
    return {
        "damage_types": [dt.value for dt in DamageType],
        "severity_levels": [sl.value for sl in DamageSeverity],
        "total_types": len(DamageType)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
