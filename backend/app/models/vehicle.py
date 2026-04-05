"""Vehicle-related models."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

from app.core.database import Base


class VehicleRegistry(Base):
    """Vehicle registry model for base vehicle data."""

    __tablename__ = "vehicle_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    variant = Column(String(200), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    base_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_vehicle_lookup", "make", "model", "year", "variant"),
    )

    def __repr__(self) -> str:
        return f"<VehicleRegistry {self.make} {self.model} {self.year}>"


class ComparableVehicle(Base):
    """Comparable vehicle model for market listings."""

    __tablename__ = "comparable_vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vin = Column(String(17), nullable=True, index=True)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    variant = Column(String(200), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    mileage = Column(Integer, nullable=True)
    location = Column(String(200), nullable=True)
    listing_price = Column(Float, nullable=False)
    listing_date = Column(DateTime, nullable=True)
    listing_url = Column(String(500), nullable=True)
    embedding = Column(Vector(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "idx_comparable_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("idx_comparable_lookup", "make", "model", "year"),
    )

    def __repr__(self) -> str:
        return f"<ComparableVehicle {self.make} {self.model} {self.year} - ${self.listing_price}>"
