"""
Demo Service - Data Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid

# ============================================================================
# SQLAlchemy Model (Database)
# ============================================================================

class Item(Base):
    """Item database model - Demo entity"""
    __tablename__ = "items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False, default=0)  # Store price in cents
    quantity = Column(Integer, nullable=False, default=0)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# Pydantic Models (API)
# ============================================================================

class ItemBase(BaseModel):
    """Base item model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: int = Field(..., ge=0)  # Price in cents, must be >= 0
    quantity: int = Field(default=0, ge=0)
    is_available: bool = True

class ItemCreate(ItemBase):
    """Item creation model"""
    pass

class ItemUpdate(BaseModel):
    """Item update model - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None

class ItemResponse(BaseModel):
    """Item response model"""
    id: uuid.UUID
    name: str
    description: Optional[str]
    price: int
    quantity: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
