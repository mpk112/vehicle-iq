"""Application configuration."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "VehicleIQ"
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://vehicleiq:vehicleiq@localhost:5432/vehicleiq"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    
    # API Keys
    GROQ_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""
    
    # Services
    PADDLEOCR_URL: str = "http://localhost:8001"
    YOLO_URL: str = "http://localhost:8002"
    EMBEDDINGS_URL: str = "http://localhost:8003"
    
    # Storage
    STORAGE_TYPE: str = "local"  # local or supabase
    LOCAL_STORAGE_PATH: str = "./storage"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""


settings = Settings()
