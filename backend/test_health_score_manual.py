"""Manual test script for health score calculation."""

import asyncio
from datetime import datetime, timedelta

from app.services.health_score import HealthScoreEngine


async def test_health_score():
    """Test health score calculation manually."""
    
    engine = HealthScoreEngine(db=None)
    
    print("=" * 80)
    print("Testing Health Score Calculation")
    print("=" * 80)
    
    # Test 1: Lender persona with good condition
    print("\n1. Lender Persona - Good Condition")
    print("-" * 80)
    
    damage_detections = {
        "detections": [
            {
                "damage_type": "scratch",
                "severity": "minor",
                "confidence": 0.8,
                "bbox": [0, 0, 100, 100]
            }
        ]
    }
    
    service_records = [
        {
            "date": datetime.now() - timedelta(days=30),
            "service_type": "oil_change",
            "mileage": 50000,
            "cost": 3000.0
        }
    ]
    
    result = await engine.calculate_health_score(
        persona="Lender",
        damage_detections=damage_detections,
        odometer_reading=50000,
        service_records=service_records,
        accident_history=None,
        fraud_confidence=15.0,
        make="Maruti",
        model="Swift",
        color="white",
        year=2020
    )
    
    print(f"Health Score: {result['health_score']}")
    print(f"Fraud Gate Triggered: {result['fraud_gate_triggered']}")
    print(f"Manual Review Required: {result['manual_review_required']}")
    print("\nComponent Breakdown:")
    for component, score in result['component_breakdown'].items():
        print(f"  {component}: {score:.2f}")
    print("\nExplanation:")
    for item in result['explanation']:
        print(f"  {item}")
    
    # Test 2: Fraud gate triggered
    print("\n\n2. Fraud Gate Triggered (fraud_confidence > 60)")
    print("-" * 80)
    
    result = await engine.calculate_health_score(
        persona="Lender",
        damage_detections={"detections": []},
        odometer_reading=50000,
        service_records=None,
        accident_history=None,
        fraud_confidence=75.0,  # Above threshold
        make="Maruti",
        model="Swift",
        color="white",
        year=2020
    )
    
    print(f"Health Score: {result['health_score']} (should be <= 30)")
    print(f"Fraud Gate Triggered: {result['fraud_gate_triggered']}")
    print(f"Manual Review Required: {result['manual_review_required']}")
    print(f"Review Reason: {result['manual_review_reason']}")
    
    # Test 3: Insurer persona with accident history
    print("\n\n3. Insurer Persona - Major Accident")
    print("-" * 80)
    
    accident_history = [
        {
            "date": datetime.now() - timedelta(days=180),
            "severity": "major",
            "description": "Front collision",
            "repair_cost": 150000.0,
            "airbag_deployed": True
        }
    ]
    
    result = await engine.calculate_health_score(
        persona="Insurer",
        damage_detections={"detections": []},
        odometer_reading=50000,
        service_records=None,
        accident_history=accident_history,
        fraud_confidence=10.0,
        make="Hyundai",
        model="Creta",
        color="white",
        year=2021
    )
    
    print(f"Health Score: {result['health_score']}")
    print(f"Accident History Score: {result['component_breakdown']['accident_history']}")
    print("\nExplanation:")
    for item in result['explanation']:
        print(f"  {item}")
    
    # Test 4: Broker persona with exterior damage
    print("\n\n4. Broker Persona - Severe Exterior Damage")
    print("-" * 80)
    
    damage_detections = {
        "detections": [
            {"damage_type": "dent", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 200, 200]},
            {"damage_type": "rust", "severity": "moderate", "confidence": 0.8, "bbox": [0, 0, 150, 150]},
            {"damage_type": "paint", "severity": "moderate", "confidence": 0.85, "bbox": [0, 0, 180, 180]},
        ]
    }
    
    result = await engine.calculate_health_score(
        persona="Broker",
        damage_detections=damage_detections,
        odometer_reading=80000,
        service_records=None,
        accident_history=None,
        fraud_confidence=5.0,
        make="Toyota",
        model="Fortuner",
        color="white",
        year=2019
    )
    
    print(f"Health Score: {result['health_score']}")
    print(f"Exterior Condition Score: {result['component_breakdown']['exterior_condition']}")
    print("\nExplanation:")
    for item in result['explanation']:
        print(f"  {item}")
    
    # Test 5: Low health score triggering manual review
    print("\n\n5. Low Health Score - Manual Review Required")
    print("-" * 80)
    
    damage_detections = {
        "detections": [
            {"damage_type": "engine", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
            {"damage_type": "transmission", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
            {"damage_type": "rust", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
            {"damage_type": "dent", "severity": "severe", "confidence": 0.9, "bbox": [0, 0, 100, 100]},
        ]
    }
    
    accident_history = [
        {"date": datetime.now(), "severity": "major", "description": "Major accident"}
    ]
    
    result = await engine.calculate_health_score(
        persona="Lender",
        damage_detections=damage_detections,
        odometer_reading=250000,  # High mileage
        service_records=None,
        accident_history=accident_history,
        fraud_confidence=0.0,
        make="Unknown",
        model="Unknown",
        color="brown",
        year=2005
    )
    
    print(f"Health Score: {result['health_score']} (should be < 40)")
    print(f"Manual Review Required: {result['manual_review_required']}")
    print(f"Review Reason: {result['manual_review_reason']}")
    print("\nComponent Breakdown:")
    for component, score in result['component_breakdown'].items():
        print(f"  {component}: {score:.2f}")
    
    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_health_score())
