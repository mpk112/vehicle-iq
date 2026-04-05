"""Image Intelligence service - orchestrates photo quality, OCR, and damage detection."""

import httpx
import asyncio
from typing import Dict, List, Optional
from app.core.config import settings
from app.services.photo_quality import PhotoQualityChecker


class ImageIntelligenceService:
    """Orchestrates image processing pipeline: quality gate → OCR → damage detection."""
    
    def __init__(self):
        self.paddleocr_url = settings.PADDLEOCR_URL
        self.yolo_url = settings.YOLO_URL
        self.quality_checker = PhotoQualityChecker()
    
    async def process_photo_complete(
        self,
        photo_bytes: bytes,
        photo_angle: str
    ) -> Dict:
        """
        Complete photo processing pipeline.
        
        Args:
            photo_bytes: Image file bytes
            photo_angle: Photo angle type (e.g., 'front', 'odometer', 'vin_plate')
            
        Returns:
            Dict with quality check, OCR results, and damage detection
        """
        # Step 1: Quality gate
        quality_result = self.quality_checker.check_quality(photo_bytes)
        
        if not quality_result["passed"]:
            return {
                "success": False,
                "stage": "quality_gate",
                "quality_check": quality_result,
                "message": "Photo failed quality gate"
            }
        
        # Step 2 & 3: Run OCR and damage detection in parallel
        ocr_task = self._extract_ocr(photo_bytes, photo_angle)
        damage_task = self._detect_damage(photo_bytes)
        
        ocr_result, damage_result = await asyncio.gather(ocr_task, damage_task)
        
        return {
            "success": True,
            "quality_check": quality_result,
            "ocr": ocr_result,
            "damage": damage_result,
            "photo_angle": photo_angle
        }
    
    async def process_batch_photos(
        self,
        photos: List[Dict]  # List of {bytes, angle}
    ) -> Dict:
        """
        Process multiple photos in parallel.
        
        Args:
            photos: List of dicts with 'bytes' and 'angle' keys
            
        Returns:
            Aggregated results from all photos
        """
        # Process all photos in parallel
        tasks = [
            self.process_photo_complete(photo["bytes"], photo["angle"])
            for photo in photos
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Aggregate results
        passed_quality = sum(1 for r in results if r.get("success", False))
        failed_quality = len(results) - passed_quality
        
        # Collect all OCR extractions
        all_ocr = {
            "odometer": None,
            "vin": None,
            "registration": None,
            "owner_name": None,
            "registration_date": None
        }
        
        for result in results:
            if result.get("success") and result.get("ocr"):
                ocr_data = result["ocr"]
                # Update with non-null values
                if ocr_data.get("odometer"):
                    all_ocr["odometer"] = ocr_data["odometer"]
                if ocr_data.get("vin"):
                    all_ocr["vin"] = ocr_data["vin"]
                if ocr_data.get("registration"):
                    all_ocr["registration"] = ocr_data["registration"]
                if ocr_data.get("document_fields"):
                    doc = ocr_data["document_fields"]
                    if doc.get("owner_name"):
                        all_ocr["owner_name"] = doc["owner_name"]
                    if doc.get("registration_date"):
                        all_ocr["registration_date"] = doc["registration_date"]
        
        # Aggregate damage detections
        all_damages = []
        for result in results:
            if result.get("success") and result.get("damage"):
                damage_data = result["damage"]
                if damage_data.get("detections"):
                    all_damages.extend(damage_data["detections"])
        
        # Calculate overall damage summary
        damage_summary = self._aggregate_damage_summary(all_damages)
        
        return {
            "success": True,
            "total_photos": len(photos),
            "passed_quality": passed_quality,
            "failed_quality": failed_quality,
            "per_photo_results": results,
            "aggregated_ocr": all_ocr,
            "aggregated_damage": {
                "total_detections": len(all_damages),
                "detections": all_damages,
                "summary": damage_summary
            }
        }
    
    async def _extract_ocr(self, photo_bytes: bytes, photo_angle: str) -> Dict:
        """
        Extract OCR data from photo based on angle type.
        
        Args:
            photo_bytes: Image file bytes
            photo_angle: Photo angle type
            
        Returns:
            OCR extraction results
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": ("photo.jpg", photo_bytes, "image/jpeg")}
                
                # Choose endpoint based on photo angle
                if photo_angle == "odometer":
                    response = await client.post(
                        f"{self.paddleocr_url}/ocr/extract/odometer",
                        files=files
                    )
                elif photo_angle == "vin_plate":
                    response = await client.post(
                        f"{self.paddleocr_url}/ocr/extract/vin",
                        files=files
                    )
                elif photo_angle in ["registration_front", "registration_back"]:
                    response = await client.post(
                        f"{self.paddleocr_url}/ocr/extract/document",
                        files=files
                    )
                else:
                    # For other angles, try to extract all fields
                    response = await client.post(
                        f"{self.paddleocr_url}/ocr/extract/all",
                        files=files
                    )
                
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"OCR service error: {str(e)}"
            }
    
    async def _detect_damage(self, photo_bytes: bytes) -> Dict:
        """
        Detect damage in photo.
        
        Args:
            photo_bytes: Image file bytes
            
        Returns:
            Damage detection results
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": ("photo.jpg", photo_bytes, "image/jpeg")}
                
                response = await client.post(
                    f"{self.yolo_url}/damage/detect",
                    files=files,
                    params={"confidence_threshold": 0.25}
                )
                
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Damage detection service error: {str(e)}"
            }
    
    def _aggregate_damage_summary(self, all_damages: List[Dict]) -> Dict:
        """
        Aggregate damage detections into summary.
        
        Args:
            all_damages: List of all damage detections
            
        Returns:
            Summary statistics
        """
        if not all_damages:
            return {
                "total_damages": 0,
                "by_type": {},
                "by_severity": {"minor": 0, "moderate": 0, "severe": 0},
                "max_severity": None
            }
        
        summary = {
            "total_damages": len(all_damages),
            "by_type": {},
            "by_severity": {"minor": 0, "moderate": 0, "severe": 0},
            "max_severity": None
        }
        
        for damage in all_damages:
            damage_type = damage.get("damage_type", "unknown")
            severity = damage.get("severity", "minor")
            
            # Count by type
            if damage_type not in summary["by_type"]:
                summary["by_type"][damage_type] = 0
            summary["by_type"][damage_type] += 1
            
            # Count by severity
            if severity in summary["by_severity"]:
                summary["by_severity"][severity] += 1
        
        # Determine max severity
        if summary["by_severity"]["severe"] > 0:
            summary["max_severity"] = "severe"
        elif summary["by_severity"]["moderate"] > 0:
            summary["max_severity"] = "moderate"
        elif summary["by_severity"]["minor"] > 0:
            summary["max_severity"] = "minor"
        
        return summary
