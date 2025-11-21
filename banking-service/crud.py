"""
Banking Service CRUD Operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import BankAccount, BankAccountCreate
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)

async def create_account(db: AsyncSession, account_data: BankAccountCreate) -> BankAccount:
    """Create a new bank account"""
    account_id = str(uuid.uuid4())
    account_number = f"ACC{uuid.uuid4().hex[:10].upper()}"
    
    account = BankAccount(
        id=account_id,
        user_id=account_data.user_id,
        account_number=account_number,
        balance=account_data.initial_balance,
        currency=account_data.currency,
        is_active=True
    )
    
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    logger.info(f"Created bank account {account_number} for user {account_data.user_id}")
    return account

async def get_account_by_user_id(db: AsyncSession, user_id: str) -> BankAccount:
    """Get bank account by user ID"""
    result = await db.execute(
        select(BankAccount).where(BankAccount.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def get_account_by_id(db: AsyncSession, account_id: str) -> BankAccount:
    """Get bank account by ID"""
    result = await db.execute(
        select(BankAccount).where(BankAccount.id == account_id)
    )
    return result.scalar_one_or_none()

async def check_balance(db: AsyncSession, user_id: str, amount: Decimal) -> tuple[bool, str]:
    """Check if user has sufficient balance"""
    account = await get_account_by_user_id(db, user_id)
    
    if not account:
        return False, "Account not found"
    
    if not account.is_active:
        return False, "Account is inactive"
    
    if account.balance < amount:
        return False, f"Insufficient balance. Available: {account.balance}, Required: {amount}"
    
    return True, "Sufficient balance"

async def debit_account(db: AsyncSession, user_id: str, amount: Decimal) -> tuple[bool, str, Decimal]:
    """Debit amount from user account"""
    account = await get_account_by_user_id(db, user_id)
    
    if not account:
        return False, "Account not found", Decimal("0")
    
    if not account.is_active:
        return False, "Account is inactive", account.balance
    
    if account.balance < amount:
        return False, f"Insufficient balance. Available: {account.balance}, Required: {amount}", account.balance
    
    # Deduct the amount
    account.balance -= amount
    await db.commit()
    await db.refresh(account)
    
    logger.info(f"Debited {amount} from account {account.account_number}. New balance: {account.balance}")
    return True, "Transaction successful", account.balance

async def credit_account(db: AsyncSession, user_id: str, amount: Decimal) -> tuple[bool, str, Decimal]:
    """Credit amount to user account"""
    account = await get_account_by_user_id(db, user_id)
    
    if not account:
        return False, "Account not found", Decimal("0")
    
    if not account.is_active:
        return False, "Account is inactive", account.balance
    
    # Add the amount
    account.balance += amount
    await db.commit()
    await db.refresh(account)
    
    logger.info(f"Credited {amount} to account {account.account_number}. New balance: {account.balance}")
    return True, "Transaction successful", account.balance
