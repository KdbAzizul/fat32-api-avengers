"""
Banking Service Database Models
"""
from sqlalchemy import Column, String, Numeric, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()

class BankAccount(Base):
    """Bank account model"""
    __tablename__ = "bank_accounts"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    account_number = Column(String, unique=True, nullable=False)
    balance = Column(Numeric(precision=10, scale=2), default=0, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Pydantic models
class BankAccountCreate(BaseModel):
    user_id: str
    initial_balance: Decimal = Decimal("1000.00")
    currency: str = "USD"

class BankAccountResponse(BaseModel):
    id: str
    user_id: str
    account_number: str
    balance: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DebitRequest(BaseModel):
    user_id: str
    amount: Decimal
    currency: str = "USD"

class DebitResponse(BaseModel):
    success: bool
    new_balance: Optional[Decimal] = None
    message: str
