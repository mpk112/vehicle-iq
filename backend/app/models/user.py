"""User model."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
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
    role = Column(SQLEnum(UserRole), nullable=False)
    organization = Column(String(255), nullable=True)
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
