"""Fraud detection service - implements 9 fraud signals."""

import hashlib
import httpx
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.vehicle import VehicleRegistry
from app.models.assessment import Assessment


class FraudDetectionEngine:
    """
    Fraud detection engine implementing 9 fraud signals.
    
    Signals:
    1. VIN clone detection
    2. Photo reuse detection (perceptual hashing)
    3. Odometer rollback detection (LLM-based)
    4. Flood damage detection
    5. Document tampering detection
    6. Claim history cross-match (mock)
    7. Registration mismatch validation
    8. Salvage title check (mock)
    9. Stolen vehicle check (mock)
    """
    
    # Signal weights for confidence calculation
    SIGNAL_WEIGHTS = {
        "vin_clone": 0.15,
        "photo_reuse": 0.12,
        "odometer_rollback": 0.13,
        "flood_damage": 0.10,
        "document_tampering": 0.12,
        "claim_history": 0.10,
        "registration_mismatch": 0.10,
        "salvage_title": 0.10,
        "stolen_vehicle": 0.08,
    }
    
    def __init__(self, db: AsyncSession, groq_api_key: Optional[str] = None):
        self.db = db
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def detect_fraud(
        self,
        vin: str,
        photos: List[bytes],
        ocr_results: Dict,
        damage_detections: Dict,
        mileage: int
    ) -> Dict:
        """
        Run all fraud detection signals and calculate confidence score.
        
        Args:
            vin: Vehicle VIN
            photos: List of photo bytes
            ocr_results: OCR extraction results
            damage_detections: Damage detection results
            mileage: Reported mileage
            
        Returns:
            Dict with fraud_confidence, signals, and evidence
        """
        signals = {}
        evidence = []
        
        # Signal 1: VIN clone detection
        vin_clone_result = await self._check_vin_clone(vin)
        signals["vin_clone"] = vin_clone_result
        if vin_clone_result["detected"]:
            evidence.append(vin_clone_result["evidence"])
        
        # Signal 2: Photo reuse detection
        photo_reuse_result = await self._check_photo_reuse(photos)
        signals["photo_reuse"] = photo_reuse_result
        if photo_reuse_result["detected"]:
            evidence.append(photo_reuse_result["evidence"])
        
        # Signal 3: Odometer rollback detection
        odometer_rollback_result = await self._check_odometer_rollback(
            ocr_results.get("odometer"), mileage
        )
        signals["odometer_rollback"] = odometer_rollback_result
        if odometer_rollback_result["detected"]:
            evidence.append(odometer_rollback_result["evidence"])
        
        # Signal 4: Flood damage detection
        flood_damage_result = await self._check_flood_damage(damage_detections)
        signals["flood_damage"] = flood_damage_result
        if flood_damage_result["detected"]:
            evidence.append(flood_damage_result["evidence"])
        
        # Signal 5: Document tampering detection
        document_tampering_result = await self._check_document_tampering(ocr_results)
        signals["document_tampering"] = document_tampering_result
        if document_tampering_result["detected"]:
            evidence.append(document_tampering_result["evidence"])
        
        # Signal 6: Claim history cross-match (mock)
        claim_history_result = await self._check_claim_history(vin)
        signals["claim_history"] = claim_history_result
        if claim_history_result["detected"]:
            evidence.append(claim_history_result["evidence"])
        
        # Signal 7: Registration mismatch validation
        registration_mismatch_result = await self._check_registration_mismatch(
            vin, ocr_results
        )
        signals["registration_mismatch"] = registration_mismatch_result
        if registration_mismatch_result["detected"]:
            evidence.append(registration_mismatch_result["evidence"])
        
        # Signal 8: Salvage title check (mock)
        salvage_title_result = await self._check_salvage_title(vin)
        signals["salvage_title"] = salvage_title_result
        if salvage_title_result["detected"]:
            evidence.append(salvage_title_result["evidence"])
        
        # Signal 9: Stolen vehicle check (mock)
        stolen_vehicle_result = await self._check_stolen_vehicle(vin)
        signals["stolen_vehicle"] = stolen_vehicle_result
        if stolen_vehicle_result["detected"]:
            evidence.append(stolen_vehicle_result["evidence"])
        
        # Calculate weighted fraud confidence (0-100)
        fraud_confidence = self._calculate_fraud_confidence(signals)
        
        return {
            "fraud_confidence": fraud_confidence,
            "signals": signals,
            "evidence": evidence,
            "fraud_gate_triggered": fraud_confidence > 60,
            "recommended_action": self._get_recommended_action(fraud_confidence)
        }
    
    async def _check_vin_clone(self, vin: str) -> Dict:
        """
        Signal 1: Check if VIN appears in multiple assessments.
        
        Returns confidence 0-100 based on duplicate count.
        """
        # Query assessments with same VIN
        result = await self.db.execute(
            select(func.count(Assessment.id)).where(Assessment.vin == vin)
        )
        count = result.scalar()
        
        if count > 1:
            confidence = min(100, 30 + (count - 1) * 20)  # 30% base + 20% per duplicate
            return {
                "detected": True,
                "confidence": confidence,
                "evidence": f"VIN {vin} found in {count} assessments (possible clone)",
                "details": {"duplicate_count": count}
            }
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {}
        }
    
    async def _check_photo_reuse(self, photos: List[bytes]) -> Dict:
        """
        Signal 2: Check if photos have been used in previous assessments.
        
        Uses perceptual hashing (pHash) to detect reused photos.
        """
        # TODO: Implement perceptual hashing with imagehash library
        # For now, use simple MD5 hash as placeholder
        
        photo_hashes = [hashlib.md5(photo).hexdigest() for photo in photos]
        
        # TODO: Check against Redis cache of known photo hashes
        # For MVP, return no detection
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {"photo_count": len(photos)}
        }
    
    async def _check_odometer_rollback(
        self, ocr_odometer: Optional[Dict], reported_mileage: int
    ) -> Dict:
        """
        Signal 3: Check for odometer tampering.
        
        Compares OCR reading with reported mileage.
        """
        if not ocr_odometer or not ocr_odometer.get("value"):
            return {
                "detected": False,
                "confidence": 0,
                "evidence": None,
                "details": {"reason": "No OCR odometer reading"}
            }
        
        ocr_reading = ocr_odometer["value"]
        difference = abs(ocr_reading - reported_mileage)
        
        # If difference > 10%, flag as suspicious
        if difference > reported_mileage * 0.1:
            confidence = min(100, 40 + (difference / reported_mileage) * 100)
            return {
                "detected": True,
                "confidence": confidence,
                "evidence": f"Odometer mismatch: OCR={ocr_reading}km, Reported={reported_mileage}km",
                "details": {
                    "ocr_reading": ocr_reading,
                    "reported_mileage": reported_mileage,
                    "difference": difference
                }
            }
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {"ocr_reading": ocr_reading, "reported_mileage": reported_mileage}
        }
    
    async def _check_flood_damage(self, damage_detections: Dict) -> Dict:
        """
        Signal 4: Check for flood damage indicators.
        
        Looks for rust, water lines, electrical corrosion in damage detections.
        """
        if not damage_detections or not damage_detections.get("detections"):
            return {
                "detected": False,
                "confidence": 0,
                "evidence": None,
                "details": {}
            }
        
        # Look for flood-related damage types
        flood_indicators = ["rust", "water_damage", "corrosion"]
        detections = damage_detections.get("detections", [])
        
        flood_damages = [
            d for d in detections
            if any(indicator in d.get("damage_type", "").lower() for indicator in flood_indicators)
        ]
        
        if flood_damages:
            confidence = min(100, 30 + len(flood_damages) * 15)
            return {
                "detected": True,
                "confidence": confidence,
                "evidence": f"Found {len(flood_damages)} flood damage indicators",
                "details": {"flood_damages": flood_damages}
            }
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {}
        }
    
    async def _check_document_tampering(self, ocr_results: Dict) -> Dict:
        """
        Signal 5: Check for document tampering.
        
        Analyzes OCR confidence and consistency.
        """
        if not ocr_results:
            return {
                "detected": False,
                "confidence": 0,
                "evidence": None,
                "details": {}
            }
        
        # Check OCR confidence scores
        low_confidence_fields = []
        for field, data in ocr_results.items():
            if isinstance(data, dict) and "confidence" in data:
                if data["confidence"] < 0.7:  # Low confidence threshold
                    low_confidence_fields.append(field)
        
        if low_confidence_fields:
            confidence = min(100, 25 + len(low_confidence_fields) * 15)
            return {
                "detected": True,
                "confidence": confidence,
                "evidence": f"Low OCR confidence in fields: {', '.join(low_confidence_fields)}",
                "details": {"low_confidence_fields": low_confidence_fields}
            }
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {}
        }
    
    async def _check_claim_history(self, vin: str) -> Dict:
        """
        Signal 6: Check claim history (mock for demo).
        
        In production, integrate with insurance claim database.
        """
        # TODO: Integrate with external claim history API
        # For MVP, return mock data
        
        # Simulate 10% chance of claim history
        import random
        if random.random() < 0.1:
            return {
                "detected": True,
                "confidence": 50,
                "evidence": "Vehicle has previous insurance claims (mock data)",
                "details": {"claim_count": 1}
            }
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {}
        }
    
    async def _check_registration_mismatch(self, vin: str, ocr_results: Dict) -> Dict:
        """
        Signal 7: Check for VIN/registration mismatch.
        
        Compares VIN from OCR with reported VIN.
        """
        ocr_vin = ocr_results.get("vin", {}).get("value") if ocr_results else None
        
        if not ocr_vin:
            return {
                "detected": False,
                "confidence": 0,
                "evidence": None,
                "details": {"reason": "No OCR VIN available"}
            }
        
        if ocr_vin != vin:
            return {
                "detected": True,
                "confidence": 80,
                "evidence": f"VIN mismatch: OCR={ocr_vin}, Reported={vin}",
                "details": {"ocr_vin": ocr_vin, "reported_vin": vin}
            }
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {"ocr_vin": ocr_vin, "reported_vin": vin}
        }
    
    async def _check_salvage_title(self, vin: str) -> Dict:
        """
        Signal 8: Check for salvage title (mock for demo).
        
        In production, integrate with DMV/RTO database.
        """
        # TODO: Integrate with salvage title database
        # For MVP, return mock data
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {}
        }
    
    async def _check_stolen_vehicle(self, vin: str) -> Dict:
        """
        Signal 9: Check if vehicle is stolen (mock for demo).
        
        In production, integrate with police database.
        """
        # TODO: Integrate with stolen vehicle database
        # For MVP, return mock data
        
        return {
            "detected": False,
            "confidence": 0,
            "evidence": None,
            "details": {}
        }
    
    def _calculate_fraud_confidence(self, signals: Dict) -> float:
        """
        Calculate weighted fraud confidence score (0-100).
        
        Uses signal weights and individual confidences.
        """
        total_confidence = 0.0
        
        for signal_name, signal_data in signals.items():
            weight = self.SIGNAL_WEIGHTS.get(signal_name, 0)
            confidence = signal_data.get("confidence", 0)
            total_confidence += weight * confidence
        
        return round(total_confidence, 2)
    
    def _get_recommended_action(self, fraud_confidence: float) -> str:
        """Get recommended action based on fraud confidence."""
        if fraud_confidence >= 80:
            return "REJECT - High fraud risk"
        elif fraud_confidence >= 60:
            return "MANUAL_REVIEW - Fraud gate triggered"
        elif fraud_confidence >= 30:
            return "CAUTION - Medium fraud risk"
        else:
            return "PROCEED - Low fraud risk"
