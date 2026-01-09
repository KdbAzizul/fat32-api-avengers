"""
User Service - Handles all user-related business logic
No JWT handling - that's done by the API Gateway
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
import logging

from database import get_db, init_db
from models import User, UserCreate, UserUpdate, UserResponse
from crud import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_all_users,
    update_user,
    delete_user,
    validate_user_credentials
)
from utils import hash_password, verify_password
from prometheus_fastapi_instrumentator import Instrumentator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Service",
    description="User management microservice",
    version="1.0.0"
)

# Initialize tracing after app creation
try:
    from middleware.tracing import init_tracing
    init_tracing(app)
    logger.info("Tracing initialized successfully")
except Exception as e:
    logger.warning(f"Tracing initialization failed: {e}")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    logger.info("Initializing User Service...")
    await init_db()
    logger.info("User Service started successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user-service"}

# ============================================================================
# HELPER: Extract user from gateway headers
# ============================================================================

def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from gateway header"""
    return x_user_id

def get_current_user_role(x_user_role: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user role from gateway header"""
    return x_user_role

def require_admin(x_user_role: Optional[str] = Header(None)):
    """Require admin role"""
    if x_user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

# ============================================================================
# AUTH ENDPOINTS - Called by Gateway
# ============================================================================

@app.post("/api/v1/auth/register", status_code=201)
async def register(user_data: UserCreate, db = Depends(get_db)):
    """
    Register new user
    Gateway will call this and handle token generation
    """
    # Check if user exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = await create_user(db, user_data)
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "created_at": user.created_at.isoformat()
    }

@app.post("/api/v1/auth/validate-credentials")
async def validate_credentials(credentials: dict, db = Depends(get_db)):
    """
    Validate user credentials
    Called by gateway during login
    Returns user data if valid, raises exception if not
    """
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Validate credentials
    user = await validate_user_credentials(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.get("/users/me")
async def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Get current user's profile"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)

@app.put("/users/me")
async def update_my_profile(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Update current user's profile"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await update_user(db, user_id, user_update)
    return UserResponse.from_orm(updated_user)

@app.delete("/users/me")
async def delete_my_account(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Delete current user's account"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await delete_user(db, user_id)
    return {"message": "Account deleted successfully"}

# ============================================================================
# ADMIN ENDPOINTS - User Management
# ============================================================================

@app.get("/users", dependencies=[Depends(require_admin)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db)
) -> List[UserResponse]:
    """List all users (admin only)"""
    users = await get_all_users(db, skip=skip, limit=limit)
    return [UserResponse.from_orm(user) for user in users]

@app.get("/users/{user_id}", dependencies=[Depends(require_admin)])
async def get_user(user_id: str, db = Depends(get_db)):
    """Get user by ID (admin only)"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)

@app.put("/users/{user_id}", dependencies=[Depends(require_admin)])
async def admin_update_user(
    user_id: str,
    user_update: UserUpdate,
    db = Depends(get_db)
):
    """Update any user (admin only)"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await update_user(db, user_id, user_update)
    return UserResponse.from_orm(updated_user)

@app.delete("/users/{user_id}", dependencies=[Depends(require_admin)])
async def admin_delete_user(user_id: str, db = Depends(get_db)):
    """Delete any user (admin only)"""
    await delete_user(db, user_id)
    return {"message": "User deleted successfully"}

@app.post("/users", dependencies=[Depends(require_admin)])
async def admin_create_user(user_data: UserCreate, db = Depends(get_db)):
    """Create user (admin only)"""
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await create_user(db, user_data)
    return UserResponse.from_orm(user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)