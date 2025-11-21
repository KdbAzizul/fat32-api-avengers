from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application configuration settings"""
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://demo:password@localhost:5432/demodb"
    )
    
    # Service configuration for tracing
    service_name: str = "demo-service"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Jaeger tracing
    jaeger_endpoint: str = os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268/api/traces")
    tracing_enabled: bool = os.getenv("TRACING_ENABLED", "true").lower() == "true"
    
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
