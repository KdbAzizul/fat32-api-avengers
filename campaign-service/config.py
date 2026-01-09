"""
Configuration for Campaign Service
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""

    # Service
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "campaign-service")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8005"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Required env vars
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    OTEL_SERVICE_NAME: str = "campaign-service"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://campaign_user:campaign_pass@campaign-db:5434/campaign_db"
    )

    # Tracing (use OTLP because Jaeger does not expose 14268)
    TRACING_ENABLED: bool = os.getenv("TRACING_ENABLED", "true").lower() == "true"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://jaeger:4317"
    )

    OTEL_EXPORTER_OTLP_PROTOCOL: str = "grpc"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # important to avoid rejecting extra env vars

settings = Settings()
