"""Enhanced seed script with comprehensive test data for VehicleIQ."""

import asyncio
import sys
from pathlib import Path
import random
from datetime import datetime, timedelta
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.vehicle import VehicleRegistry, ComparableVehicle


# Indian vehicle market data
INDIAN_MAKES_MODELS = {
    "Maruti": ["Swift", "Baleno", "Dzire", "Alto", "WagonR", "Ertiga", "Vitara Brezza", "S-Cross", "Ciaz", "XL6"],
    "Hyundai": ["i20", "Creta", "Verna", "Grand i10", "Venue", "Aura", "Alcazar", "Tucson", "Elantra", "Kona"],
    "Tata": ["Nexon", "Harrier", "Altroz", "Tiago", "Punch", "Safari", "Tigor", "Hexa", "Zest", "Bolt"],
    "Honda": ["City", "Amaze", "Jazz", "WR-V", "Civic", "CR-V", "Accord", "Brio", "Mobilio", "BR-V"],
    "Toyota": ["Innova", "Fortuner", "Glanza", "Urban Cruiser", "Camry", "Yaris", "Etios", "Corolla", "Land Cruiser", "Vellfire"],
    "Mahindra": ["Scorpio", "XUV700", "Thar", "Bolero", "XUV300", "Marazzo", "KUV100", "TUV300", "Alturas", "XUV500"],
    "Kia": ["Seltos", "Sonet", "Carens", "Carnival", "EV6"],
    "MG": ["Hector", "Astor", "ZS EV", "Gloster", "Hector Plus"],
    "Renault": ["Kwid", "Triber", "Kiger", "Duster", "Captur"],
    "Nissan": ["Magnite", "Kicks", "GT-R", "Terrano", "Sunny"],
}

VARIANTS = ["Base", "Mid", "Top", "Premium"]
FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric"]
TRANSMISSIONS = ["Manual", "Automatic", "AMT", "CVT"]
INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
    "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara"
]


def generate_vin():
    """Generate a realistic VIN (17 characters)."""
    # VIN format: WMI (3) + VDS (6) + VIS (8)
    chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"  # Excluding I, O, Q
    return ''.join(random.choice(chars) for _ in range(17))


def generate_indian_registration():
    """Generate Indian registration number (e.g., DL01AB1234)."""
    state_codes = ["DL", "MH", "KA", "TN", "UP", "GJ", "RJ", "HR", "PB", "WB"]
    state = random.choice(state_codes)
    district = random.randint(1, 99)
    series = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(2))
    number = random.randint(1000, 9999)
    return f"{state}{district:02d}{series}{number}"


class DataGenerator:
    """Generate realistic test data for VehicleIQ."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = []
        self.vehicles = []
        self.comparables = []
    
    async def generate_users(self, count: int = 20):
        """Generate test users across all roles."""
        print(f"Generating {count} users...")
        
        # Predefined test users
        test_users = [
            ("admin@vehicleiq.com", "Admin@123456", "Admin User", UserRole.ADMIN, "VehicleIQ"),
            ("lender@example.com", "Lender@123456", "Lender User", UserRole.LENDER, "Example Bank"),
            ("insurer@example.com", "Insurer@123456", "Insurer User", UserRole.INSURER, "Example Insurance"),
            ("broker@example.com", "Broker@123456", "Broker User", UserRole.BROKER, "Example Dealership"),
            ("assessor@example.com", "Assessor@123456", "Assessor User", UserRole.ASSESSOR, "VehicleIQ"),
        ]
        
        for email, password, name, role, org in test_users:
            user = User(
                id=uuid.uuid4(),
                email=email,
                hashed_password=get_password_hash(password),
                full_name=name,
                role=role,
                organization=org,
                is_active="true",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.users.append(user)
            self.session.add(user)
        
        # Generate additional users
        roles = [UserRole.ASSESSOR, UserRole.LENDER, UserRole.INSURER, UserRole.BROKER]
        for i in range(count - len(test_users)):
            role = random.choice(roles)
            user = User(
                id=uuid.uuid4(),
                email=f"user{i+1}@example.com",
                hashed_password=get_password_hash("Password@123"),
                full_name=f"Test User {i+1}",
                role=role,
                organization=f"Organization {i+1}",
                is_active="true" if random.random() > 0.1 else "false",  # 10% inactive
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                updated_at=datetime.utcnow(),
            )
            self.users.append(user)
            self.session.add(user)
        
        await self.session.commit()
        print(f"✅ Created {len(self.users)} users")
    
    async def generate_vehicle_registry(self, count: int = 1000):
        """Generate vehicle registry with realistic Indian market data."""
        print(f"Generating {count} vehicle registry entries...")
        
        generated = 0
        for make, models in INDIAN_MAKES_MODELS.items():
            for model in models:
                for year in range(2015, 2025):  # 10 years
                    for variant in VARIANTS:
                        if generated >= count:
                            break
                        
                        # Base price varies by make, model, year, variant
                        base_multiplier = {
                            "Maruti": 0.6, "Hyundai": 0.7, "Tata": 0.65,
                            "Honda": 0.8, "Toyota": 1.0, "Mahindra": 0.75,
                            "Kia": 0.85, "MG": 0.9, "Renault": 0.6, "Nissan": 0.65
                        }
                        
                        variant_multiplier = {
                            "Base": 1.0, "Mid": 1.15, "Top": 1.3, "Premium": 1.5
                        }
                        
                        year_multiplier = 1.0 + (year - 2015) * 0.05  # 5% increase per year
                        
                        base_price = int(
                            500000 *  # Base ₹5L
                            base_multiplier.get(make, 0.7) *
                            variant_multiplier[variant] *
                            year_multiplier
                        )
                        
                        vehicle = VehicleRegistry(
                            id=uuid.uuid4(),
                            make=make,
                            model=model,
                            year=year,
                            variant=variant,
                            fuel_type=random.choice(FUEL_TYPES),
                            transmission=random.choice(TRANSMISSIONS),
                            base_price=base_price,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow(),
                        )
                        self.vehicles.append(vehicle)
                        self.session.add(vehicle)
                        generated += 1
                    
                    if generated >= count:
                        break
                if generated >= count:
                    break
            if generated >= count:
                break
        
        await self.session.commit()
        print(f"✅ Created {len(self.vehicles)} vehicle registry entries")
    
    async def generate_comparable_vehicles(self, count: int = 2000):
        """Generate comparable vehicle listings."""
        print(f"Generating {count} comparable vehicles...")
        
        for i in range(count):
            # Pick random vehicle from registry
            if self.vehicles:
                base_vehicle = random.choice(self.vehicles)
                make = base_vehicle.make
                model = base_vehicle.model
                year = base_vehicle.year + random.randint(-2, 2)  # ±2 years
                year = max(2015, min(2024, year))  # Clamp to valid range
                variant = base_vehicle.variant
                fuel_type = base_vehicle.fuel_type
                transmission = base_vehicle.transmission
                base_price = base_vehicle.base_price
            else:
                # Fallback if no vehicles in registry
                make = random.choice(list(INDIAN_MAKES_MODELS.keys()))
                model = random.choice(INDIAN_MAKES_MODELS[make])
                year = random.randint(2015, 2024)
                variant = random.choice(VARIANTS)
                fuel_type = random.choice(FUEL_TYPES)
                transmission = random.choice(TRANSMISSIONS)
                base_price = random.randint(400000, 2000000)
            
            # Mileage increases with age
            age = 2024 - year
            mileage = random.randint(5000, 15000) * age + random.randint(0, 10000)
            mileage = min(mileage, 200000)  # Cap at 200k km
            
            # Listing price based on base price, age, and mileage
            depreciation = 0.85 ** age  # 15% per year
            mileage_factor = 1.0 - (mileage / 200000) * 0.3  # Up to 30% reduction for high mileage
            listing_price = int(base_price * depreciation * mileage_factor * random.uniform(0.9, 1.1))
            
            comparable = ComparableVehicle(
                id=uuid.uuid4(),
                vin=generate_vin(),
                make=make,
                model=model,
                year=year,
                variant=variant,
                fuel_type=fuel_type,
                transmission=transmission,
                mileage=mileage,
                location=random.choice(INDIAN_CITIES),
                listing_price=listing_price,
                listing_date=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                listing_url=f"https://example.com/listing/{uuid.uuid4()}",
                condition_summary=random.choice([
                    "Excellent condition, single owner",
                    "Good condition, well maintained",
                    "Fair condition, minor scratches",
                    "Average condition, normal wear and tear"
                ]),
                # embedding will be generated separately
                created_at=datetime.utcnow(),
            )
            self.comparables.append(comparable)
            self.session.add(comparable)
            
            # Commit in batches
            if (i + 1) % 100 == 0:
                await self.session.commit()
                print(f"  Progress: {i+1}/{count}")
        
        await self.session.commit()
        print(f"✅ Created {len(self.comparables)} comparable vehicles")


async def seed_database_enhanced():
    """Run enhanced database seeding."""
    print("🌱 Starting enhanced database seeding...")
    print("=" * 60)
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        generator = DataGenerator(session)
        
        # Generate data
        await generator.generate_users(count=20)
        await generator.generate_vehicle_registry(count=1000)
        await generator.generate_comparable_vehicles(count=2000)
        
        print("=" * 60)
        print("✅ Enhanced database seeding completed!")
        print("\n📊 Summary:")
        print(f"  Users: {len(generator.users)}")
        print(f"  Vehicle Registry: {len(generator.vehicles)}")
        print(f"  Comparable Vehicles: {len(generator.comparables)}")
        print("\n🔑 Test Credentials:")
        print("  Admin: admin@vehicleiq.com / Admin@123456")
        print("  Lender: lender@example.com / Lender@123456")
        print("  Insurer: insurer@example.com / Insurer@123456")
        print("  Broker: broker@example.com / Broker@123456")
        print("  Assessor: assessor@example.com / Assessor@123456")
        print("\n⚠️  Note: Embeddings need to be generated separately")
        print("  Run: python scripts/generate_embeddings.py")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database_enhanced())
