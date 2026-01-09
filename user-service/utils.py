"""
User Service - Utility Functions
"""
from passlib.context import CryptContext
from pwdlib import PasswordHash

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
passlib_context = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Hash a password"""
    # return pwd_context.hash(password)
    return passlib_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    # return pwd_context.verify(plain_password, hashed_password)
    return passlib_context.verify(plain_password, hashed_password)