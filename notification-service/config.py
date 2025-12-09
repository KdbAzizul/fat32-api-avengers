"""
Configuration for Notification Service
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(extra='ignore', env_file=".env", case_sensitive=True)
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://notification_user:notification_pass@localhost:5432/notification_db"
    )
    
    # Service
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "notification-service")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8005"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    # Tracing
    TRACING_ENABLED: bool = os.getenv("TRACING_ENABLED", "true").lower() == "true"
    JAEGER_ENDPOINT: str = os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268/api/traces")
    

settings = Settings()
