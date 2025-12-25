#!/usr/bin/env python3
"""
Test the Data Analysis Docker sandbox directly
"""

import json
import docker
import sys


def test_data_sandbox():
    """Test the data sandbox with a simple data analysis challenge"""
    
    print("🧪 Testing WeaktoStrong Data Analysis Sandbox...")
    
    try:
        # Initialize Docker client
        docker_client = docker.from_env()
        image_name = "weak-to-strong/data-sandbox:latest"
        
        print(f"✅ Docker client initialized, using image: {image_name}")
        
        # Test configuration for a simple data analysis challenge
        test_config = {
            "type": "python",
            "code": '''
# Analyze the sales data
import pandas as pd
import numpy as np

# The dataset should be loaded automatically
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Calculate total revenue (quantity * price)
df['revenue'] = df['quantity'] * df['price']
total_revenue = df['revenue'].sum()

# Find best selling product by total quantity
product_sales = df.groupby('product_name')['quantity'].sum()
best_selling_product = product_sales.idxmax()
best_selling_quantity = product_sales.max()

# Calculate some basic stats
avg_order_value = df['revenue'].mean()
total_orders = len(df)

print(f"\\n=== SALES ANALYSIS ===")
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Best Selling Product: {best_selling_product} ({best_selling_quantity:,} units)")
print(f"Average Order Value: ${avg_order_value:.2f}")
print(f"Total Orders: {total_orders:,}")

# Results for validation
result_summary = {
    'total_revenue': total_revenue,
    'best_product': best_selling_product,
    'avg_order': avg_order_value
}
''',
            "dataset": "sales_data.csv",
            "validations": [
                {
                    "name": "Revenue Calculation",
                    "type": "variable_exists",
                    "variable": "total_revenue"
                },
                {
                    "name": "Product Analysis",
                    "type": "variable_exists", 
                    "variable": "best_selling_product"
                },
                {
                    "name": "Summary Created",
                    "type": "variable_exists",
                    "variable": "result_summary"
                }
            ]
        }
        
        print("🚀 Executing data analysis in sandbox...")
        
        # Container configuration
        container_config = {
            "image": image_name,
            "command": ["python", "data-test-runner.py", json.dumps(test_config)],
            "mem_limit": "512m",
            "cpu_period": 100000,
            "cpu_quota": 50000,  # 0.5 CPU
            "network_mode": "none",
            "user": "sandbox",
            "security_opt": ["no-new-privileges:true"],
            "cap_drop": ["ALL"],
            "read_only": True,
            "tmpfs": {
                "/tmp": "noexec,nosuid,size=100m",
                "/workspace/temp": "noexec,nosuid,size=50m"
            },
            "remove": True,
            "stdout": True,
            "stderr": True
        }
        
        # Run container
        container = docker_client.containers.run(**container_config)
        
        # Get output
        logs = container.logs(stdout=True, stderr=True).decode('utf-8')
        
        print("\\n📋 SANDBOX OUTPUT:")
        print("=" * 50)
        print(logs)
        print("=" * 50)
        
        # Try to parse JSON result
        try:
            json_start = logs.rfind('{')
            if json_start != -1:
                json_content = logs[json_start:]
                result = json.loads(json_content)
                
                print("\\n📊 PARSED RESULTS:")
                print(f"✅ Success: {result.get('passed', False)}")
                print(f"🎯 Score: {result.get('score', 0)}/100")
                print(f"🔍 Validations: {len(result.get('validations', []))}")
                
                for validation in result.get('validations', []):
                    status = "✅" if validation.get('passed', False) else "❌"
                    print(f"  {status} {validation.get('name', 'Unknown')}: {validation.get('message', 'No message')}")
                
                if result.get('passed', False):
                    print("\\n🎉 DATA ANALYSIS SANDBOX TEST PASSED!")
                    print("\\n🧠 WeaktoStrong 'Vibe Coder' Philosophy Demonstrated:")
                    print("  • Code executed successfully in secure sandbox")
                    print("  • Output-based validation (not code style)")
                    print("  • Real data science insights extracted")
                    print("  • Ready for production data challenges!")
                else:
                    print("\\n❌ Validation failed, but sandbox is working")
                    
            else:
                print("\\n⚠️  No JSON result found, but execution completed")
                
        except json.JSONDecodeError as e:
            print(f"\\n⚠️  Could not parse JSON result: {e}")
            print("But the sandbox executed successfully!")
        
        return True
        
    except docker.errors.ImageNotFound:
        print(f"❌ Docker image not found: {image_name}")
        print("💡 Run: docker build -t weak-to-strong/data-sandbox:latest .")
        return False
        
    except docker.errors.ContainerError as e:
        print(f"❌ Container execution failed: {e}")
        if e.stderr:
            print(f"Container stderr: {e.stderr.decode()}")
        return False
        
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_data_sandbox()
    sys.exit(0 if success else 1)