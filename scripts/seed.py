"""Seed database with test data."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.vehicle import VehicleRegistry, ComparableVehicle
import uuid
from datetime import datetime, timedelta
import random


async def seed_database():
    """Seed database with test data."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🌱 Seeding database...")
        
        # Create test users
        print("Creating users...")
        users = [
            User(
                id=uuid.uuid4(),
                email="admin@vehicleiq.com",
                hashed_password=get_password_hash("Admin@123456"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                organization="VehicleIQ",
                is_active="true",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            User(
                id=uuid.uuid4(),
                email="lender@example.com",
                hashed_password=get_password_hash("Lender@123456"),
                full_name="Lender User",
                role=UserRole.LENDER,
                organization="Example Bank",
                is_active="true",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            User(
                id=uuid.uuid4(),
                email="assessor@example.com",
                hashed_password=get_password_hash("Assessor@123456"),
                full_name="Assessor User",
                role=UserRole.ASSESSOR,
                organization="VehicleIQ",
                is_active="true",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
        
        for user in users:
            session.add(user)
        
        # Create vehicle registry
        print("Creating vehicle registry...")
        makes_models = [
            ("Maruti", ["Swift", "Baleno", "Dzire", "Alto", "WagonR"]),
            ("Hyundai", ["i20", "Creta", "Verna", "Grand i10", "Venue"]),
            ("Tata", ["Nexon", "Harrier", "Altroz", "Tiago", "Punch"]),
            ("Honda", ["City", "Amaze", "Jazz", "WR-V", "Civic"]),
            ("Toyota", ["Innova", "Fortuner", "Glanza", "Urban Cruiser", "Camry"]),
        ]
        
        vehicles = []
        for make, models in makes_models:
            for model in models:
                for year in range(2018, 2025):
                    base_price = random.randint(500000, 2000000)
                    vehicles.append(
                        VehicleRegistry(
                            id=uuid.uuid4(),
                            make=make,
                            model=model,
                            year=year,
                            variant="Standard",
                            fuel_type=random.choice(["Petrol", "Diesel", "CNG"]),
                            transmission=random.choice(["Manual", "Automatic"]),
                            base_price=base_price,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                    )
        
        for vehicle in vehicles[:100]:  # Add first 100
            session.add(vehicle)
        
        # Create comparable vehicles
        print("Creating comparable vehicles...")
        comparables = []
        for i in range(50):
            make, models = random.choice(makes_models)
            model = random.choice(models)
            year = random.randint(2018, 2024)
            mileage = random.randint(10000, 100000)
            listing_price = random.randint(400000, 1800000)
            
            comparables.append(
                ComparableVehicle(
                    id=uuid.uuid4(),
                    make=make,
                    model=model,
                    year=year,
                    variant="Standard",
                    fuel_type=random.choice(["Petrol", "Diesel", "CNG"]),
                    transmission=random.choice(["Manual", "Automatic"]),
                    mileage=mileage,
                    location=random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"]),
                    listing_price=listing_price,
                    listing_date=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    listing_url=f"https://example.com/listing/{i}",
                    created_at=datetime.utcnow(),
                )
            )
        
        for comparable in comparables:
            session.add(comparable)
        
        await session.commit()
        print("✅ Database seeded successfully!")
        print("\nTest Users:")
        print("  Admin: admin@vehicleiq.com / Admin@123456")
        print("  Lender: lender@example.com / Lender@123456")
        print("  Assessor: assessor@example.com / Assessor@123456")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
