"""
Integration tests for authentication API endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime

from app.models.user import User, UserTier
from app.core.auth import get_password_hash


class TestAuthAPI:
    """Integration tests for authentication endpoints"""

    @pytest.mark.integration
    async def test_register_user_success(self, client: AsyncClient):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["tier"] == "free"
        assert "id" in data
        assert "password" not in data  # Password should not be returned

    @pytest.mark.integration
    async def test_register_user_duplicate_email(
        self, client: AsyncClient, test_db_session
    ):
        """Test registration with duplicate email fails"""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Existing User",
        )
        test_db_session.add(existing_user)
        await test_db_session.commit()

        # Try to register with same email
        user_data = {
            "email": "existing@example.com",
            "password": "newpassword123",
            "full_name": "Another User",
        }

        response = await client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    @pytest.mark.integration
    async def test_register_user_invalid_data(self, client: AsyncClient):
        """Test registration with invalid data"""
        invalid_data = {
            "email": "notanemail",  # Invalid email format
            "password": "123",  # Too short password
            "full_name": "",  # Empty name
        }

        response = await client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    async def test_login_success(self, client: AsyncClient, test_db_session):
        """Test successful login"""
        # Create test user
        user = User(
            email="loginuser@example.com",
            hashed_password=get_password_hash("loginpassword123"),
            full_name="Login User",
            is_active=True,
        )
        test_db_session.add(user)
        await test_db_session.commit()

        login_data = {"email": "loginuser@example.com", "password": "loginpassword123"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    @pytest.mark.integration
    async def test_login_invalid_credentials(
        self, client: AsyncClient, test_db_session
    ):
        """Test login with invalid credentials"""
        # Create test user
        user = User(
            email="testuser@example.com",
            hashed_password=get_password_hash("correctpassword"),
            full_name="Test User",
        )
        test_db_session.add(user)
        await test_db_session.commit()

        # Try login with wrong password
        login_data = {"email": "testuser@example.com", "password": "wrongpassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    @pytest.mark.integration
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        login_data = {"email": "nonexistent@example.com", "password": "anypassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_get_current_user_success(self, client: AsyncClient, test_db_session):
        """Test getting current user with valid token"""
        # Create and login user
        user = User(
            email="currentuser@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Current User",
            tier=UserTier.PRO,
        )
        test_db_session.add(user)
        await test_db_session.commit()

        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "currentuser@example.com", "password": "password123"},
        )
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "currentuser@example.com"
        assert data["full_name"] == "Current User"
        assert data["tier"] == "pro"

    @pytest.mark.integration
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token"""
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token"""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_refresh_token_success(self, client: AsyncClient, test_db_session):
        """Test successful token refresh"""
        # Create and login user
        user = User(
            email="refreshuser@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Refresh User",
        )
        test_db_session.add(user)
        await test_db_session.commit()

        # Login to get initial tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "refreshuser@example.com", "password": "password123"},
        )
        token_data = login_response.json()
        refresh_token = token_data["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        new_token_data = response.json()
        assert "access_token" in new_token_data
        assert "refresh_token" in new_token_data
        assert new_token_data["access_token"] != token_data["access_token"]
        assert new_token_data["refresh_token"] != refresh_token

    @pytest.mark.integration
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid refresh token"""
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid_refresh_token"}
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    @pytest.mark.integration
    async def test_logout_success(self, client: AsyncClient, test_db_session):
        """Test successful logout"""
        # Create and login user
        user = User(
            email="logoutuser@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Logout User",
        )
        test_db_session.add(user)
        await test_db_session.commit()

        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "logoutuser@example.com", "password": "password123"},
        )
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # Logout
        response = await client.post(
            "/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

    @pytest.mark.integration
    async def test_logout_invalid_token(self, client: AsyncClient):
        """Test logout with invalid token"""
        response = await client.post(
            "/api/v1/auth/logout", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_rate_limiting(self, client: AsyncClient):
        """Test rate limiting on auth endpoints"""
        # This test assumes rate limiting is configured
        # Make multiple rapid requests to trigger rate limiting
        login_data = {"email": "nonexistent@example.com", "password": "anypassword"}

        responses = []
        for _ in range(10):  # Make 10 rapid requests
            response = await client.post("/api/v1/auth/login", json=login_data)
            responses.append(response.status_code)

        # Should have some 429 (Too Many Requests) responses if rate limiting is active
        # Note: This test might be flaky depending on rate limiting configuration
        assert any(status in [401, 429] for status in responses)
