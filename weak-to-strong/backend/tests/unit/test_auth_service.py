"""
Unit tests for authentication service
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.auth import AuthService
from app.schemas.auth import UserCreate, UserLogin
from app.models.user import User, UserTier
from app.core.auth import create_session_tokens, verify_password, get_password_hash


class TestAuthService:
    """Test cases for AuthService"""

    @pytest_asyncio.fixture
    async def auth_service(self, test_db_session):
        """Create an AuthService instance with test database"""
        return AuthService(test_db_session)

    @pytest_asyncio.fixture
    async def test_user(self, test_db_session) -> User:
        """Create a test user in the database"""
        user_data = {
            "id": uuid4(),
            "email": "test@example.com",
            "hashed_password": get_password_hash("testpassword123"),
            "full_name": "Test User",
            "is_active": True,
            "tier": UserTier.FREE,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        user = User(**user_data)
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        return user

    @pytest.mark.unit
    async def test_create_user_success(self, auth_service, test_user_data):
        """Test successful user creation"""
        user_create = UserCreate(**test_user_data)

        user = await auth_service.create_user(user_create)

        assert user.email == test_user_data["email"]
        assert user.full_name == test_user_data["full_name"]
        assert user.is_active == test_user_data["is_active"]
        assert user.tier == UserTier.FREE
        assert user.id is not None
        assert verify_password(test_user_data["password"], user.hashed_password)

    @pytest.mark.unit
    async def test_create_user_duplicate_email(
        self, auth_service, test_user, test_user_data
    ):
        """Test user creation with duplicate email fails"""
        user_create = UserCreate(**test_user_data)

        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.create_user(user_create)

    @pytest.mark.unit
    async def test_authenticate_user_success(self, auth_service, test_user):
        """Test successful user authentication"""
        login_data = UserLogin(email="test@example.com", password="testpassword123")

        user = await auth_service.authenticate_user(
            login_data.email, login_data.password
        )

        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    @pytest.mark.unit
    async def test_authenticate_user_invalid_email(self, auth_service):
        """Test authentication with invalid email"""
        user = await auth_service.authenticate_user(
            "nonexistent@example.com", "password"
        )
        assert user is None

    @pytest.mark.unit
    async def test_authenticate_user_invalid_password(self, auth_service, test_user):
        """Test authentication with invalid password"""
        user = await auth_service.authenticate_user("test@example.com", "wrongpassword")
        assert user is None

    @pytest.mark.unit
    async def test_login_user_success(self, auth_service, test_user):
        """Test successful user login returns tokens"""
        login_data = UserLogin(email="test@example.com", password="testpassword123")

        token_response = await auth_service.login_user(login_data)

        assert token_response.access_token is not None
        assert token_response.refresh_token is not None
        assert token_response.token_type == "bearer"
        assert token_response.expires_in > 0

    @pytest.mark.unit
    async def test_login_user_invalid_credentials(self, auth_service, test_user):
        """Test login with invalid credentials raises exception"""
        login_data = UserLogin(email="test@example.com", password="wrongpassword")

        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.login_user(login_data)

    @pytest.mark.unit
    async def test_get_user_by_email_success(self, auth_service, test_user):
        """Test getting user by email"""
        user = await auth_service.get_user_by_email("test@example.com")

        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    @pytest.mark.unit
    async def test_get_user_by_email_not_found(self, auth_service):
        """Test getting non-existent user by email"""
        user = await auth_service.get_user_by_email("nonexistent@example.com")
        assert user is None

    @pytest.mark.unit
    async def test_get_user_by_id_success(self, auth_service, test_user):
        """Test getting user by ID"""
        user = await auth_service.get_user_by_id(str(test_user.id))

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.unit
    async def test_get_user_by_id_not_found(self, auth_service):
        """Test getting non-existent user by ID"""
        fake_id = str(uuid4())
        user = await auth_service.get_user_by_id(fake_id)
        assert user is None

    @pytest.mark.unit
    async def test_refresh_token_success(self, auth_service, test_user):
        """Test successful token refresh"""
        # Create initial tokens
        tokens = create_session_tokens(str(test_user.id))

        # Refresh tokens
        new_token_response = await auth_service.refresh_token(tokens["refresh_token"])

        assert new_token_response.access_token != tokens["access_token"]
        assert new_token_response.refresh_token != tokens["refresh_token"]
        assert new_token_response.token_type == "bearer"

    @pytest.mark.unit
    async def test_refresh_token_invalid(self, auth_service):
        """Test token refresh with invalid token"""
        with pytest.raises(ValueError, match="Invalid refresh token"):
            await auth_service.refresh_token("invalid-refresh-token")

    @pytest.mark.unit
    async def test_update_user_tier(self, auth_service, test_user):
        """Test updating user tier"""
        await auth_service.update_user_tier(str(test_user.id), UserTier.PRO)

        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.tier == UserTier.PRO

    @pytest.mark.unit
    async def test_deactivate_user(self, auth_service, test_user):
        """Test deactivating user account"""
        await auth_service.deactivate_user(str(test_user.id))

        updated_user = await auth_service.get_user_by_id(str(test_user.id))
        assert updated_user.is_active == False

    @pytest.mark.unit
    async def test_password_validation(self):
        """Test password hashing and verification"""
        password = "testsecurepassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) == True
        assert verify_password("wrongpassword", hashed) == False
        assert hashed != password  # Ensure password is actually hashed
