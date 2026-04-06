"""Health score calculation service - implements 6-component health scoring with persona-specific weights."""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession


class HealthScoreEngine:
    """
    Health score engine implementing 6-component scoring system.
    
    Components:
    1. Mechanical condition (engine, transmission, suspension)
    2. Exterior condition (paint, body, glass)
    3. Interior condition (seats, dashboard, electronics)
    4. Accident history (no accidents=100, major=0)
    5. Service history (regular service=100, none=50)
    6. Market appeal (popular model/color=100)
    
    Persona-specific weights:
    - Lender: Focus on mechanical (40%), exterior (30%), fraud (20%), service (10%)
    - Insurer: Focus on accident history (35%), mechanical (30%), fraud (25%), exterior (10%)
    - Broker: Focus on exterior (45%), mechanical (25%), market appeal (20%), fraud (10%)
    """
    
    # Persona-specific component weights
    PERSONA_WEIGHTS = {
        "Lender": {
            "mechanical_condition": 0.40,
            "exterior_condition": 0.30,
            "fraud_indicators": 0.20,
            "service_history": 0.10,
        },
        "Insurer": {
            "accident_history": 0.35,
            "mechanical_condition": 0.30,
            "fraud_indicators": 0.25,
            "exterior_condition": 0.10,
        },
        "Broker": {
            "exterior_condition": 0.45,
            "mechanical_condition": 0.25,
            "market_appeal": 0.20,
            "fraud_indicators": 0.10,
        }
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_health_score(
        self,
        persona: str,
        damage_detections: Dict,
        odometer_reading: int,
        service_records: Optional[List[Dict]] = None,
        accident_history: Optional[List[Dict]] = None,
        fraud_confidence: float = 0.0,
        make: str = "",
        model: str = "",
        color: Optional[str] = None,
        year: int = 0
    ) -> Dict:
        """
        Calculate vehicle health score with persona-specific weighting.
        
        Args:
            persona: Lender, Insurer, or Broker
            damage_detections: Damage detection results from YOLO
            odometer_reading: Vehicle mileage
            service_records: List of service records (optional)
            accident_history: List of accident records (optional)
            fraud_confidence: Fraud confidence score (0-100)
            make: Vehicle make
            model: Vehicle model
            color: Vehicle color
            year: Vehicle year
            
        Returns:
            Dict with health_score, component_breakdown, fraud_gate_triggered, 
            manual_review_required, and explanation
        """
        # Calculate individual components
        components = {}
        
        components["mechanical_condition"] = self._calculate_mechanical_condition(
            damage_detections, odometer_reading, service_records
        )
        
        components["exterior_condition"] = self._calculate_exterior_condition(
            damage_detections
        )
        
        components["interior_condition"] = self._calculate_interior_condition(
            damage_detections
        )
        
        components["accident_history"] = self._calculate_accident_history(
            accident_history
        )
        
        components["service_history"] = self._calculate_service_history(
            service_records
        )
        
        components["market_appeal"] = self._calculate_market_appeal(
            make, model, color, year
        )
        
        # Convert fraud confidence to fraud indicators score (inverse)
        components["fraud_indicators"] = 100.0 - fraud_confidence
        
        # Calculate weighted health score based on persona
        health_score = self._apply_persona_weights(persona, components)
        
        # Apply fraud gate logic
        fraud_gate_triggered = fraud_confidence > 60
        if fraud_gate_triggered:
            health_score = min(health_score, 30.0)
        
        # Check if manual review is required (low health score)
        manual_review_required = health_score < 40 or fraud_gate_triggered
        
        # Generate explanation
        explanation = self._generate_explanation(
            persona, components, health_score, fraud_gate_triggered
        )
        
        return {
            "health_score": round(health_score, 2),
            "component_breakdown": {k: round(v, 2) for k, v in components.items()},
            "fraud_gate_triggered": fraud_gate_triggered,
            "manual_review_required": manual_review_required,
            "manual_review_reason": self._get_review_reason(health_score, fraud_gate_triggered),
            "explanation": explanation
        }
    
    def _calculate_mechanical_condition(
        self,
        damage_detections: Dict,
        odometer_reading: int,
        service_records: Optional[List[Dict]]
    ) -> float:
        """
        Calculate mechanical condition score (0-100).
        
        Factors:
        - Engine/transmission damage from detections
        - High mileage penalty
        - Recent service bonus
        """
        base_score = 100.0
        
        # Deduct for mechanical damage
        if damage_detections and damage_detections.get("detections"):
            for damage in damage_detections["detections"]:
                damage_type = damage.get("damage_type", "").lower()
                severity = damage.get("severity", "minor")
                
                # Check for mechanical issues
                if any(keyword in damage_type for keyword in ["engine", "transmission", "suspension", "brake"]):
                    if severity == "severe":
                        base_score -= 30
                    elif severity == "moderate":
                        base_score -= 15
                    else:
                        base_score -= 5
        
        # Deduct for high mileage
        if odometer_reading > 150000:
            mileage_penalty = (odometer_reading - 150000) / 10000 * 2
            base_score -= min(mileage_penalty, 20)  # Cap at 20 points
        
        # Bonus for recent service
        if service_records:
            # Sort by date (most recent first)
            sorted_records = sorted(
                service_records,
                key=lambda x: x.get("date", datetime.min),
                reverse=True
            )
            
            if sorted_records:
                most_recent = sorted_records[0]
                service_date = most_recent.get("date")
                
                if isinstance(service_date, datetime):
                    days_since_service = (datetime.now() - service_date).days
                    if days_since_service < 180:  # Within 6 months
                        base_score += 5
        
        return max(0, min(100, base_score))
    
    def _calculate_exterior_condition(self, damage_detections: Dict) -> float:
        """
        Calculate exterior condition score (0-100).
        
        Factors:
        - Dents, scratches, rust, paint damage
        - Severity and count of damages
        """
        base_score = 100.0
        
        if not damage_detections or not damage_detections.get("detections"):
            return base_score
        
        for damage in damage_detections["detections"]:
            damage_type = damage.get("damage_type", "").lower()
            severity = damage.get("severity", "minor")
            
            # Check for exterior damage
            if any(keyword in damage_type for keyword in ["dent", "scratch", "rust", "paint", "panel", "bumper", "door"]):
                if severity == "severe":
                    base_score -= 20
                elif severity == "moderate":
                    base_score -= 10
                else:
                    base_score -= 3
        
        return max(0, min(100, base_score))
    
    def _calculate_interior_condition(self, damage_detections: Dict) -> float:
        """
        Calculate interior condition score (0-100).
        
        Factors:
        - Seat damage, dashboard issues, electronics
        """
        base_score = 100.0
        
        if not damage_detections or not damage_detections.get("detections"):
            return base_score
        
        for damage in damage_detections["detections"]:
            damage_type = damage.get("damage_type", "").lower()
            severity = damage.get("severity", "minor")
            
            # Check for interior damage
            if any(keyword in damage_type for keyword in ["seat", "dashboard", "interior", "upholstery", "console"]):
                if severity == "severe":
                    base_score -= 15
                elif severity == "moderate":
                    base_score -= 8
                else:
                    base_score -= 3
        
        return max(0, min(100, base_score))
    
    def _calculate_accident_history(self, accident_history: Optional[List[Dict]]) -> float:
        """
        Calculate accident history score (0-100).
        
        No accidents = 100
        Minor accidents = 70-90
        Major accidents = 0-50
        """
        if not accident_history:
            return 100.0  # No accidents
        
        base_score = 100.0
        
        for accident in accident_history:
            severity = accident.get("severity", "minor")
            
            if severity == "major":
                base_score -= 50
            elif severity == "moderate":
                base_score -= 25
            else:
                base_score -= 10
        
        return max(0, min(100, base_score))
    
    def _calculate_service_history(self, service_records: Optional[List[Dict]]) -> float:
        """
        Calculate service history score (0-100).
        
        Regular service = 100
        Some service = 70-90
        No service = 50
        """
        if not service_records:
            return 50.0  # No service records
        
        # Count service records
        service_count = len(service_records)
        
        if service_count >= 5:
            return 100.0  # Excellent service history
        elif service_count >= 3:
            return 85.0  # Good service history
        elif service_count >= 1:
            return 70.0  # Some service history
        else:
            return 50.0  # No service history
    
    def _calculate_market_appeal(
        self,
        make: str,
        model: str,
        color: Optional[str],
        year: int
    ) -> float:
        """
        Calculate market appeal score (0-100).
        
        Factors:
        - Popular make/model
        - Desirable color
        - Vehicle age
        """
        base_score = 70.0  # Neutral baseline
        
        # Popular Indian makes
        popular_makes = ["Maruti", "Hyundai", "Tata", "Honda", "Toyota", "Mahindra"]
        if make in popular_makes:
            base_score += 15
        
        # Popular models (simplified)
        popular_models = ["Swift", "i20", "Creta", "City", "Fortuner", "Nexon", "Seltos"]
        if model in popular_models:
            base_score += 10
        
        # Desirable colors
        if color:
            desirable_colors = ["white", "silver", "black", "grey", "gray"]
            if color.lower() in desirable_colors:
                base_score += 5
        
        # Age penalty
        current_year = datetime.now().year
        age = current_year - year
        
        if age <= 3:
            pass  # No penalty
        elif age <= 5:
            base_score -= 5
        elif age <= 10:
            base_score -= 10
        else:
            base_score -= 20
        
        return max(0, min(100, base_score))
    
    def _apply_persona_weights(self, persona: str, components: Dict[str, float]) -> float:
        """
        Apply persona-specific weights to calculate final health score.
        
        Args:
            persona: Lender, Insurer, or Broker
            components: Dict of component scores
            
        Returns:
            Weighted health score (0-100)
        """
        weights = self.PERSONA_WEIGHTS.get(persona, self.PERSONA_WEIGHTS["Lender"])
        
        weighted_score = 0.0
        for component, weight in weights.items():
            component_score = components.get(component, 0.0)
            weighted_score += component_score * weight
        
        return weighted_score
    
    def _get_review_reason(self, health_score: float, fraud_gate_triggered: bool) -> Optional[str]:
        """Get reason for manual review."""
        if fraud_gate_triggered:
            return "Fraud gate triggered (fraud confidence > 60)"
        elif health_score < 40:
            return f"Low health score ({health_score:.1f} < 40)"
        return None
    
    def _generate_explanation(
        self,
        persona: str,
        components: Dict[str, float],
        health_score: float,
        fraud_gate_triggered: bool
    ) -> List[str]:
        """
        Generate human-readable explanation of health score.
        
        Returns list of explanation strings.
        """
        explanation = []
        
        # Overall score
        if health_score >= 80:
            explanation.append(f"Excellent overall condition (score: {health_score:.1f}/100)")
        elif health_score >= 60:
            explanation.append(f"Good overall condition (score: {health_score:.1f}/100)")
        elif health_score >= 40:
            explanation.append(f"Fair overall condition (score: {health_score:.1f}/100)")
        else:
            explanation.append(f"Poor overall condition (score: {health_score:.1f}/100)")
        
        # Fraud gate
        if fraud_gate_triggered:
            explanation.append("⚠️ Fraud gate triggered - health score capped at 30")
        
        # Component highlights
        weights = self.PERSONA_WEIGHTS.get(persona, self.PERSONA_WEIGHTS["Lender"])
        
        # Sort components by weight (most important first)
        sorted_components = sorted(
            weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for component, weight in sorted_components[:3]:  # Top 3 components
            score = components.get(component, 0.0)
            component_name = component.replace("_", " ").title()
            
            if score >= 80:
                explanation.append(f"✓ {component_name}: Excellent ({score:.1f}/100, weight: {weight*100:.0f}%)")
            elif score >= 60:
                explanation.append(f"• {component_name}: Good ({score:.1f}/100, weight: {weight*100:.0f}%)")
            elif score >= 40:
                explanation.append(f"⚠ {component_name}: Fair ({score:.1f}/100, weight: {weight*100:.0f}%)")
            else:
                explanation.append(f"✗ {component_name}: Poor ({score:.1f}/100, weight: {weight*100:.0f}%)")
        
        return explanation
