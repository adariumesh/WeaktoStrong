#!/usr/bin/env python3
"""
Test the complete Data Analysis challenge flow
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.runners.data_runner import DataRunner, DataChallenge, DataValidation


async def test_data_runner():
    """Test the complete data analysis challenge execution"""
    
    print("🧪 Testing WeaktoStrong Data Analysis Runner...")
    
    try:
        # Initialize runner
        runner = DataRunner()
        print("✅ DataRunner initialized")
        
        # Create a simple test challenge
        test_challenge = DataChallenge(
            challenge_id="test-data-analysis",
            initial_code="# Sample sales data loaded as 'df'",
            dataset_name="sales_data.csv",
            validations=[
                DataValidation(
                    name="Total Revenue Calculated",
                    type="variable_exists",
                    variable="total_revenue"
                ),
                DataValidation(
                    name="Revenue Value Check",
                    type="value_check", 
                    variable="total_revenue",
                    expected=125430.50,
                    tolerance=1.0
                )
            ]
        )
        
        # Test user code (simulates what a user would write)
        user_code = '''
# Calculate total revenue
total_revenue = (df['quantity'] * df['price']).sum()

# Find best selling product
product_sales = df.groupby('product_name')['quantity'].sum()
best_selling_product = product_sales.idxmax()

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Best Selling Product: {best_selling_product}")
'''
        
        print("🚀 Executing data challenge...")
        
        # Execute the challenge
        result = await runner.execute_data_challenge(
            user_id="test-user-123",
            code=user_code,
            challenge=test_challenge
        )
        
        # Print results
        print("\\n📊 EXECUTION RESULTS:")
        print(f"Success: {result.success}")
        print(f"Score: {result.score}/{result.max_score}")
        print(f"Execution Time: {result.execution_time_ms}ms")
        print(f"Variables Created: {result.variables_created}")
        print(f"Insights Found: {result.insights_found}")
        
        if result.output:
            print(f"\\n📝 OUTPUT:")
            print(result.output)
        
        if result.errors:
            print(f"\\n❌ ERRORS:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.validations:
            print(f"\\n✅ VALIDATIONS:")
            for validation in result.validations:
                status = "✅" if validation.get("passed", False) else "❌"
                print(f"  {status} {validation.get('name', 'Unknown')}: {validation.get('message', 'No message')}")
        
        # Test Vibe Coder scoring
        print(f"\\n🎯 VIBE CODER ASSESSMENT:")
        print(f"  - Code executed successfully: {'Yes' if result.success else 'No'}")
        print(f"  - Created analysis variables: {'Yes' if result.variables_created else 'No'}")
        print(f"  - Generated insights: {'Yes' if result.insights_found else 'No'}")
        print(f"  - Overall score: {result.score}% (Pass threshold: 70%)")
        
        if result.success:
            print("\\n🎉 TEST PASSED - WeaktoStrong Data Analysis Runner is working!")
        else:
            print("\\n❌ TEST FAILED - Check the errors above")
            
    except Exception as e:
        print(f"\\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_data_runner())