#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""
import sys
import os
import asyncio
import uuid
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schemas.auth import UserCreate, UserLogin, TokenResponse
from app.core.auth import create_session_tokens, verify_password, get_password_hash


async def test_auth_utilities():
    """Test authentication utilities"""
    print("🧪 Testing authentication utilities...")

    # Test password hashing
    password = "test123456"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed), "Password hashing failed"
    assert not verify_password("wrong", hashed), "Wrong password should fail"
    print("✅ Password hashing works")

    # Test JWT token creation
    user_id = str(uuid.uuid4())
    tokens = create_session_tokens(user_id)

    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "token_type" in tokens
    assert "expires_in" in tokens
    print("✅ JWT token creation works")
    print(f"   Access token: {tokens['access_token'][:50]}...")
    print(f"   Refresh token: {tokens['refresh_token'][:50]}...")


async def test_schemas():
    """Test Pydantic schemas"""
    print("\n🧪 Testing Pydantic schemas...")

    # Test UserCreate schema
    user_data = {
        "email": "test@example.com",
        "password": "test123456",
        "name": "Test User",
    }

    user_create = UserCreate(**user_data)
    assert user_create.email == "test@example.com"
    assert user_create.name == "Test User"
    print("✅ UserCreate schema works")

    # Test UserLogin schema
    login_data = {"email": "test@example.com", "password": "test123456"}

    user_login = UserLogin(**login_data)
    assert user_login.email == "test@example.com"
    print("✅ UserLogin schema works")


async def main():
    """Main test function"""
    print("🚀 Starting authentication tests...\n")

    try:
        await test_auth_utilities()
        await test_schemas()

        print("\n🎉 All authentication tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
