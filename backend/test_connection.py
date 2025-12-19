"""
Simple connection test for backend services
"""

import os
import sys
from urllib.parse import urlparse


def test_imports():
    """Test that required packages can be imported"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import redis

        print("✅ All required packages can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def test_environment():
    """Test environment variables are loadable"""
    required_vars = ["DATABASE_URL", "REDIS_URL", "JWT_SECRET", "NEXTAUTH_SECRET"]

    # Try to load .env file
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env loading")

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("Please create .env file with required variables")
        return False
    else:
        print("✅ Environment variables are available")
        return True


def test_database_config():
    """Test database URL format"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return False

    try:
        parsed = urlparse(db_url)
        if parsed.scheme not in ["postgresql", "postgres"]:
            print(f"❌ Unsupported database scheme: {parsed.scheme}")
            return False
        print(
            f"✅ Database URL format valid: {parsed.scheme}://{parsed.hostname}:{parsed.port}"
        )
        return True
    except Exception as e:
        print(f"❌ Invalid DATABASE_URL: {e}")
        return False


def test_redis_config():
    """Test Redis URL format"""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL not set")
        return False

    try:
        parsed = urlparse(redis_url)
        if not parsed.scheme.startswith("redis"):
            print(f"❌ Invalid Redis scheme: {parsed.scheme}")
            return False
        print(
            f"✅ Redis URL format valid: {parsed.scheme}://{parsed.hostname}:{parsed.port}"
        )
        return True
    except Exception as e:
        print(f"❌ Invalid REDIS_URL: {e}")
        return False


def main():
    """Run all tests"""
    print("🔍 Testing backend configuration...\n")

    tests = [
        ("Package imports", test_imports),
        ("Environment variables", test_environment),
        ("Database configuration", test_database_config),
        ("Redis configuration", test_redis_config),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"Testing {name}...")
        if test_func():
            passed += 1
        print()

    print(f"🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Backend configuration test complete!")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
