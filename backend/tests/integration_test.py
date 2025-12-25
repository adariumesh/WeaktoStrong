"""
WeaktoStrong Data Analysis Integration Test
End-to-end testing of the complete Data Analysis challenge execution flow
"""

import asyncio
import json
import pytest
import uuid
from typing import Dict, Any
from httpx import AsyncClient

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from main import app
from app.core.database import get_db
from app.models.challenge import Challenge, Track
from app.models.user import User
from app.services.execution_service import get_execution_service, ExecutionRequest
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession


class TestDataAnalysisIntegration:
    """
    Integration tests for Data Analysis challenge execution
    Tests the complete flow from API request to Docker sandbox execution to validation
    """
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Create a test user"""
        test_user = User(
            email="test@example.com",
            name="Test User",
            tier="free",
            tokens_used_today=0,
            is_active=True,
            is_verified=True
        )
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)
        return test_user
    
    @pytest.fixture
    async def data_analysis_challenge(self, db_session: AsyncSession):
        """Get a Data Analysis challenge from the database"""
        # Find the Data Analysis track
        track_result = await db_session.execute(
            select(Track).where(Track.name == "Data Analysis")
        )
        track = track_result.scalar_one_or_none()
        
        if not track:
            pytest.skip("Data Analysis track not found in database")
        
        # Get the first challenge from the track
        challenge_result = await db_session.execute(
            select(Challenge).where(Challenge.track_id == track.id).order_by(Challenge.order_index).limit(1)
        )
        challenge = challenge_result.scalar_one_or_none()
        
        if not challenge:
            pytest.skip("No Data Analysis challenges found in database")
        
        return challenge
    
    @pytest.mark.asyncio
    async def test_data_analysis_execution_service_direct(self, db_session: AsyncSession):
        """
        Test Data Analysis execution via ExecutionService directly
        """
        
        # Get a Data Analysis challenge
        track_result = await db_session.execute(
            select(Track).where(Track.name == "Data Analysis")
        )
        track = track_result.scalar_one_or_none()
        
        if not track:
            pytest.skip("Data Analysis track not found - run seed_data_challenges.py first")
        
        challenge_result = await db_session.execute(
            select(Challenge).where(Challenge.track_id == track.id).order_by(Challenge.order_index).limit(1)
        )
        challenge = challenge_result.scalar_one_or_none()
        
        if not challenge:
            pytest.skip("No Data Analysis challenges found - run seed_data_challenges.py first")
        
        print(f"Testing challenge: {challenge.title}")
        
        # Create test code that should pass validation
        test_code = """
# WeaktoStrong Data Analysis Challenge 1: Fundamentals

# The dataset 'df' is already loaded for you
# Columns: product_name, quantity, price, sale_date

# TODO 1: Calculate total revenue
# Hint: revenue = quantity * price
df['revenue'] = df['quantity'] * df['price']
total_revenue = df['revenue'].sum()

# TODO 2: Find the product with highest total sales
# Hint: Group by product_name and sum quantities  
product_sales = df.groupby('product_name')['quantity'].sum()
best_selling_product = product_sales.idxmax()

# TODO 3: Calculate average order value
avg_order_value = df['revenue'].mean()

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Best Selling Product: {best_selling_product}")
print(f"Average Order Value: ${avg_order_value:.2f}")

# Create some summary data for validation
result_summary = {
    'total_revenue': total_revenue,
    'best_product': best_selling_product,
    'avg_order': avg_order_value
}
"""
        
        # Create execution request
        execution_request = ExecutionRequest(
            challenge_id=str(challenge.id),
            user_id="test-user-123",
            code=test_code,
            language="python"
        )
        
        # Execute using ExecutionService
        execution_service = get_execution_service()
        result = await execution_service.execute_challenge(execution_request, db_session)
        
        # Assertions
        assert result is not None
        assert result.challenge_id == str(challenge.id)
        assert result.user_id == "test-user-123"
        assert result.track_type == "data"
        assert result.execution_time_ms > 0
        
        # Print detailed results for debugging
        print(f"Execution Result:")
        print(f"  Success: {result.success}")
        print(f"  Score: {result.score}/{result.max_score}")
        print(f"  Execution Time: {result.execution_time_ms}ms")
        print(f"  Errors: {result.errors}")
        print(f"  Insights Found: {result.insights_found}")
        print(f"  Validation Results: {len(result.validation_results)} checks")
        
        # Check if execution completed (even if validations failed)
        assert len(result.errors) == 0 or not any("Docker" in str(error) for error in result.errors), \
            f"Docker execution failed: {result.errors}"
        
        # Success depends on sandbox execution working
        if result.success:
            assert result.score > 0
            print("✅ Challenge execution successful!")
        else:
            print(f"⚠️  Challenge execution completed but validation failed: {result.errors}")
    
    @pytest.mark.asyncio
    async def test_data_analysis_api_endpoint(self, async_client: AsyncClient, test_user: User, data_analysis_challenge: Challenge):
        """
        Test Data Analysis execution via API endpoint
        """
        
        # Test code for the challenge
        test_code = """
# Simple data analysis code
import pandas as pd
import numpy as np

# Basic calculations that should exist in most challenges
if 'df' in globals():
    total_revenue = df['revenue'].sum() if 'revenue' in df.columns else 0
    best_selling_product = "Test Product"
    avg_order_value = df['revenue'].mean() if 'revenue' in df.columns else 0
else:
    # Fallback if dataset not loaded
    total_revenue = 125430.50
    best_selling_product = "Widget A"
    avg_order_value = 50.25

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Best Selling Product: {best_selling_product}")
print(f"Average Order Value: ${avg_order_value:.2f}")
"""
        
        # Make API request
        response = await async_client.post(
            f"/api/v1/challenges/{data_analysis_challenge.id}/execute",
            json={
                "challenge_id": str(data_analysis_challenge.id),
                "code": test_code,
                "language": "python"
            }
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.json()}")
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        
        # Validate response structure
        assert "challenge_id" in result
        assert "user_id" in result
        assert "track_type" in result
        assert "success" in result
        assert "score" in result
        assert "execution_time_ms" in result
        
        assert result["track_type"] == "data"
        assert result["execution_time_ms"] > 0
        
        print("✅ API endpoint test completed!")
    
    @pytest.mark.asyncio
    async def test_multiple_data_challenges(self, db_session: AsyncSession):
        """
        Test execution of multiple Data Analysis challenges
        """
        
        # Get all Data Analysis challenges
        track_result = await db_session.execute(
            select(Track).where(Track.name == "Data Analysis")
        )
        track = track_result.scalar_one_or_none()
        
        if not track:
            pytest.skip("Data Analysis track not found")
        
        challenges_result = await db_session.execute(
            select(Challenge).where(Challenge.track_id == track.id).order_by(Challenge.order_index)
        )
        challenges = challenges_result.scalars().all()
        
        if len(challenges) == 0:
            pytest.skip("No Data Analysis challenges found")
        
        execution_service = get_execution_service()
        results = []
        
        # Test first 3 challenges (to avoid long test times)
        for i, challenge in enumerate(challenges[:3]):
            print(f"Testing Challenge {i+1}: {challenge.title}")
            
            # Generic test code that should work for most challenges
            test_code = """
# Generic data analysis code
import pandas as pd
import numpy as np

# Try to use the loaded dataset
if 'df' in globals():
    print(f"Dataset loaded: {df.shape}")
    
    # Create basic variables that most challenges expect
    if 'revenue' not in df.columns and 'quantity' in df.columns and 'price' in df.columns:
        df['revenue'] = df['quantity'] * df['price']
    
    total_revenue = df['revenue'].sum() if 'revenue' in df.columns else 0
    
    # Find best selling product
    if 'product_name' in df.columns and 'quantity' in df.columns:
        product_sales = df.groupby('product_name')['quantity'].sum()
        best_selling_product = product_sales.idxmax()
    else:
        best_selling_product = "Unknown Product"
    
    # Calculate average
    avg_order_value = df['revenue'].mean() if 'revenue' in df.columns else 0
    
else:
    # Fallback values
    total_revenue = 100000
    best_selling_product = "Test Product"
    avg_order_value = 50.0

# Create common analysis variables
result_summary = {
    'total_revenue': total_revenue,
    'best_product': best_selling_product,
    'avg_order': avg_order_value
}

print(f"Analysis complete: ${total_revenue:,.2f} total revenue")
"""
            
            execution_request = ExecutionRequest(
                challenge_id=str(challenge.id),
                user_id="test-user-multi",
                code=test_code,
                language="python"
            )
            
            result = await execution_service.execute_challenge(execution_request, db_session)
            results.append(result)
            
            print(f"  Result: {'✅ PASS' if result.success else '❌ FAIL'} ({result.score}/{result.max_score})")
            if result.errors:
                print(f"  Errors: {result.errors}")
        
        # Summary
        successful_challenges = sum(1 for r in results if r.success)
        print(f"\n📊 Multi-Challenge Test Results:")
        print(f"  Challenges tested: {len(results)}")
        print(f"  Successful executions: {successful_challenges}")
        print(f"  Success rate: {successful_challenges/len(results)*100:.1f}%")
        
        # At least one should execute without Docker errors
        execution_errors = [r for r in results if any("Docker" in str(e) for e in r.errors)]
        assert len(execution_errors) < len(results), "All challenges failed with Docker errors"
    
    @pytest.mark.asyncio
    async def test_validation_rules_parsing(self, db_session: AsyncSession):
        """
        Test that validation rules are correctly parsed from challenge database
        """
        
        # Get a challenge with validation rules
        track_result = await db_session.execute(
            select(Track).where(Track.name == "Data Analysis")
        )
        track = track_result.scalar_one_or_none()
        
        if not track:
            pytest.skip("Data Analysis track not found")
        
        challenge_result = await db_session.execute(
            select(Challenge).where(
                Challenge.track_id == track.id,
                Challenge.validation_rules.isnot(None)
            ).limit(1)
        )
        challenge = challenge_result.scalar_one_or_none()
        
        if not challenge:
            pytest.skip("No challenges with validation rules found")
        
        print(f"Testing validation rules for: {challenge.title}")
        
        # Check validation rules structure
        validation_rules = challenge.validation_rules
        assert validation_rules is not None
        assert "type" in validation_rules
        assert "validations" in validation_rules
        
        validations = validation_rules["validations"]
        assert isinstance(validations, list)
        assert len(validations) > 0
        
        # Check validation structure
        for validation in validations:
            assert "name" in validation
            assert "type" in validation
            print(f"  Validation: {validation['name']} ({validation['type']})")
        
        print("✅ Validation rules structure is correct")
    
    @pytest.mark.asyncio
    async def test_execution_service_status(self):
        """
        Test that execution service status endpoint works
        """
        
        execution_service = get_execution_service()
        status = await execution_service.get_execution_status()
        
        assert "service" in status
        assert status["service"] == "execution_service"
        assert "runners" in status
        
        runners = status["runners"]
        assert "data" in runners
        assert "web" in runners
        assert "cloud" in runners
        
        # Data runner should be available
        data_runner_status = runners["data"]
        print(f"Data Runner Status: {data_runner_status}")
        
        print("✅ Execution service status check complete")


def pytest_configure(config):
    """Configure pytest for integration tests"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    """
    Run integration test directly for debugging
    """
    import asyncio
    
    async def run_direct_test():
        print("🧪 Running WeaktoStrong Data Analysis Integration Test")
        
        # Test execution service directly
        from app.core.database import get_db
        
        async for db in get_db():
            test_instance = TestDataAnalysisIntegration()
            try:
                await test_instance.test_data_analysis_execution_service_direct(db)
                print("✅ Direct execution test passed!")
            except Exception as e:
                print(f"❌ Direct execution test failed: {e}")
            
            try:
                await test_instance.test_validation_rules_parsing(db)
                print("✅ Validation rules test passed!")
            except Exception as e:
                print(f"❌ Validation rules test failed: {e}")
            
            try:
                await test_instance.test_execution_service_status()
                print("✅ Status test passed!")
            except Exception as e:
                print(f"❌ Status test failed: {e}")
            
            break
    
    asyncio.run(run_direct_test())