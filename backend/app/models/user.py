"""User model."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid

from app.core.database import Base


class UserRole(str, Enum):
    """User role enum."""

    ASSESSOR = "Assessor"
    LENDER = "Lender"
    INSURER = "Insurer"
    BROKER = "Broker"
    ADMIN = "Admin"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(ENUM('Assessor', 'Lender', 'Insurer', 'Broker', 'Admin', name='user_role', create_type=False), nullable=False)
    organization = Column(String(255), nullable=True)
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
