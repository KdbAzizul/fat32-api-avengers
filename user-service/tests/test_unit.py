"""
Unit Tests for User Service
Tests CRUD operations, endpoints, and utilities with mocking
"""
import sys
from pathlib import Path
# Add parent folder (project root) to sys.path so local modules can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
proj_root_str = str(PROJECT_ROOT)
if proj_root_str not in sys.path:
    sys.path.insert(0, proj_root_str)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import uuid
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Import models and functions to test
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
from main import app

# Test client
client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_user_id():
    """Generate a sample UUID"""
    return uuid.uuid4()


@pytest.fixture
def sample_user(sample_user_id):
    """Create a sample user object"""
    return User(
        id=sample_user_id,
        email="test@example.com",
        hashed_password="hashed_password_123",
        full_name="Test User",
        role="user",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=None
    )


@pytest.fixture
def sample_user_create():
    """Sample user creation data"""
    return UserCreate(
        email="newuser@example.com",
        password="securepassword123",
        full_name="New User",
        role="user"
    )


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    return session


# ============================================================================
# UTILITY TESTS
# ============================================================================

class TestUtils:
    """Test utility functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "mypassword123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_success(self):
        """Test password verification with correct password"""
        password = "mypassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Test password verification with incorrect password"""
        password = "mypassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


# ============================================================================
# CRUD TESTS
# ============================================================================

class TestCRUD:
    """Test CRUD operations"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, mock_db_session, sample_user_create):
        """Test user creation"""
        with patch('crud.hash_password', return_value="hashed_password"):
            user = await create_user(mock_db_session, sample_user_create)
            
            # Verify user object was created
            assert mock_db_session.add.called
            assert mock_db_session.commit.called
            assert mock_db_session.refresh.called
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, mock_db_session, sample_user, sample_user_id):
        """Test get user by ID"""
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        user = await get_user_by_id(mock_db_session, str(sample_user_id))
        
        assert user == sample_user
        assert mock_db_session.execute.called
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_db_session):
        """Test get user by ID when user doesn't exist"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        user = await get_user_by_id(mock_db_session, str(uuid.uuid4()))
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, mock_db_session, sample_user):
        """Test get user by email"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        user = await get_user_by_email(mock_db_session, "test@example.com")
        
        assert user == sample_user
        assert mock_db_session.execute.called
    
    @pytest.mark.asyncio
    async def test_get_all_users(self, mock_db_session, sample_user):
        """Test get all users with pagination"""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_user]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        users = await get_all_users(mock_db_session, skip=0, limit=10)
        
        assert len(users) == 1
        assert users[0] == sample_user
    
    @pytest.mark.asyncio
    async def test_update_user(self, mock_db_session, sample_user, sample_user_id):
        """Test user update"""
        update_data = UserUpdate(full_name="Updated Name")
        
        with patch('crud.get_user_by_id', return_value=sample_user):
            updated_user = await update_user(
                mock_db_session,
                str(sample_user_id),
                update_data
            )
            
            assert mock_db_session.commit.called
            assert mock_db_session.refresh.called
            assert updated_user.full_name == "Updated Name"
    
    @pytest.mark.asyncio
    async def test_update_user_with_password(self, mock_db_session, sample_user, sample_user_id):
        """Test user update with password change"""
        update_data = UserUpdate(password="newpassword123")
        
        with patch('crud.get_user_by_id', return_value=sample_user):
            with patch('crud.hash_password', return_value="new_hashed_password") as mock_hash:
                updated_user = await update_user(
                    mock_db_session,
                    str(sample_user_id),
                    update_data
                )
                
                mock_hash.assert_called_once_with("newpassword123")
                assert updated_user.hashed_password == "new_hashed_password"
    
    @pytest.mark.asyncio
    async def test_delete_user(self, mock_db_session, sample_user, sample_user_id):
        """Test user deletion"""
        with patch('crud.get_user_by_id', return_value=sample_user):
            result = await delete_user(mock_db_session, str(sample_user_id))
            
            assert result is True
            assert mock_db_session.delete.called
            assert mock_db_session.commit.called
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, mock_db_session):
        """Test delete user when user doesn't exist"""
        with patch('crud.get_user_by_id', return_value=None):
            result = await delete_user(mock_db_session, str(uuid.uuid4()))
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_user_credentials_success(self, mock_db_session, sample_user):
        """Test credential validation with correct credentials"""
        with patch('crud.get_user_by_email', return_value=sample_user):
            with patch('crud.verify_password', return_value=True):
                user = await validate_user_credentials(
                    mock_db_session,
                    "test@example.com",
                    "correctpassword"
                )
                
                assert user == sample_user
    
    @pytest.mark.asyncio
    async def test_validate_user_credentials_wrong_password(self, mock_db_session, sample_user):
        """Test credential validation with wrong password"""
        with patch('crud.get_user_by_email', return_value=sample_user):
            with patch('crud.verify_password', return_value=False):
                user = await validate_user_credentials(
                    mock_db_session,
                    "test@example.com",
                    "wrongpassword"
                )
                
                assert user is None
    
    @pytest.mark.asyncio
    async def test_validate_user_credentials_user_not_found(self, mock_db_session):
        """Test credential validation with non-existent user"""
        with patch('crud.get_user_by_email', return_value=None):
            user = await validate_user_credentials(
                mock_db_session,
                "nonexistent@example.com",
                "anypassword"
            )
            
            assert user is None


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestEndpoints:
    """Test API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "service": "user-service"
        }
    
    @patch('main.get_db')
    @patch('main.get_user_by_email')
    @patch('main.create_user')
    def test_register_success(self, mock_create_user, mock_get_by_email, mock_get_db):
        """Test user registration"""
        # Mock no existing user
        mock_get_by_email.return_value = None
        
        # Mock created user
        new_user = MagicMock()
        new_user.id = uuid.uuid4()
        new_user.email = "newuser@example.com"
        new_user.full_name = "New User"
        new_user.role = "user"
        new_user.created_at = datetime.utcnow()
        mock_create_user.return_value = new_user
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "New User",
                "role": "user"
            }
        )
        
        assert response.status_code == 201
        assert "email" in response.json()
    
    @patch('main.get_db')
    @patch('main.get_user_by_email')
    def test_register_duplicate_email(self, mock_get_by_email, mock_get_db):
        """Test registration with existing email"""
        # Mock existing user
        existing_user = MagicMock()
        mock_get_by_email.return_value = existing_user
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "password123",
                "full_name": "Existing User"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    @patch('main.get_db')
    @patch('main.validate_user_credentials')
    def test_validate_credentials_success(self, mock_validate, mock_get_db):
        """Test credential validation endpoint"""
        # Mock valid user
        valid_user = MagicMock()
        valid_user.id = uuid.uuid4()
        valid_user.email = "user@example.com"
        valid_user.full_name = "Test User"
        valid_user.role = "user"
        valid_user.is_active = True
        mock_validate.return_value = valid_user
        
        response = client.post(
            "/api/v1/auth/validate-credentials",
            json={
                "email": "user@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        assert "email" in response.json()
    
    @patch('main.get_db')
    @patch('main.validate_user_credentials')
    def test_validate_credentials_invalid(self, mock_validate, mock_get_db):
        """Test credential validation with invalid credentials"""
        mock_validate.return_value = None
        
        response = client.post(
            "/api/v1/auth/validate-credentials",
            json={
                "email": "user@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    @patch('main.get_db')
    @patch('main.get_user_by_id')
    def test_get_my_profile(self, mock_get_by_id, mock_get_db):
        """Test get current user profile"""
        # Mock user
        user = MagicMock()
        user.id = uuid.uuid4()
        user.email = "user@example.com"
        user.full_name = "Test User"
        user.role = "user"
        user.is_active = True
        user.created_at = datetime.utcnow()
        user.updated_at = None
        user.last_login = None
        mock_get_by_id.return_value = user
        
        response = client.get(
            "/users/me",
            headers={"x-user-id": str(user.id)}
        )
        
        assert response.status_code == 200
    
    def test_get_my_profile_unauthorized(self):
        """Test get profile without authentication"""
        response = client.get("/users/me")
        
        assert response.status_code == 401
    
    @patch('main.get_db')
    @patch('main.get_all_users')
    def test_list_users_admin(self, mock_get_all, mock_get_db):
        """Test list users as admin"""
        # Mock users list
        mock_get_all.return_value = []
        
        response = client.get(
            "/users",
            headers={"x-user-role": "admin"}
        )
        
        assert response.status_code == 200
    
    def test_list_users_non_admin(self):
        """Test list users without admin role"""
        response = client.get(
            "/users",
            headers={"x-user-role": "user"}
        )
        
        assert response.status_code == 403


# ============================================================================
# MODEL TESTS
# ============================================================================

class TestModels:
    """Test Pydantic models"""
    
    def test_user_create_validation(self):
        """Test UserCreate model validation"""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        assert user_data.email == "test@example.com"
        assert user_data.password == "password123"
        assert user_data.full_name == "Test User"
        assert user_data.role == "user"
    
    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email"""
        with pytest.raises(Exception):  # Pydantic validation error
            UserCreate(
                email="invalid-email",
                password="password123",
                full_name="Test User"
            )

    def test_user_create_short_password(self):
        """Test UserCreate with short password"""
        with pytest.raises(Exception):  # Pydantic validation error
            UserCreate(
                email="test@example.com",
                password="short",
                full_name="Test User"
            )
        
    
    def test_user_update_partial(self):
        """Test UserUpdate with partial data"""
        update_data = UserUpdate(full_name="Updated Name")
        
        assert update_data.full_name == "Updated Name"
        assert update_data.email is None
        assert update_data.password is None
    
    def test_user_response_from_orm(self, sample_user):
        """Test UserResponse from ORM model"""
        response = UserResponse.from_orm(sample_user)
        
        assert response.email == sample_user.email
        assert response.full_name == sample_user.full_name
        assert response.role == sample_user.role
        assert response.is_active == sample_user.is_active
