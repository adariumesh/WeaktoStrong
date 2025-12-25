"""
Seed script for Data Track challenges
Creates 15 data science challenges with real datasets and comprehensive test configurations
"""

import asyncio

from sqlalchemy import select
from app.core.database import get_db
from app.models.challenge import Challenge, ChallengeDifficulty, ChallengeTrack, Track

DATA_CHALLENGES = [
    # BEGINNER: Data Cleaning (1-5)
    {
        "slug": "data-001-missing-values",
        "title": "Handle Missing Data",
        "description": "Clean a customer dataset by handling missing values appropriately for different columns.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.DATA,
        "order_index": 1,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "30 minutes",
        "requirements": [
            {"id": "req1", "text": "Load the customer dataset", "points": 20},
            {
                "id": "req2",
                "text": "Identify columns with missing values",
                "points": 20,
            },
            {
                "id": "req3",
                "text": "Handle missing values in numeric columns (mean/median)",
                "points": 30,
            },
            {
                "id": "req4",
                "text": "Handle missing values in categorical columns (mode/new category)",
                "points": 30,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use pandas for data manipulation",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Preserve original data shape (rows)",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "customers.csv",
            "validations": [
                {"name": "Dataset loaded", "type": "variable_exists", "variable": "df"},
                {
                    "name": "No missing values remain",
                    "type": "custom_check",
                    "check": "df.isnull().sum().sum() == 0",
                },
                {
                    "name": "Row count preserved",
                    "type": "dataframe_shape",
                    "dataframe": "df",
                    "shape": [1000, 8],
                },
                {
                    "name": "Age column filled",
                    "type": "custom_check",
                    "check": "'age' in df.columns and df['age'].notna().all()",
                },
            ],
        },
        "hints": [
            "Start by exploring the dataset with df.info() and df.isnull().sum()",
            "For numeric columns, consider using fillna() with mean() or median()",
            "For categorical columns, use mode() or create a new 'Unknown' category",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-002-duplicate-records",
        "title": "Remove Duplicate Records",
        "description": "Identify and remove duplicate records from a sales transactions dataset while preserving data integrity.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.DATA,
        "order_index": 2,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "25 minutes",
        "requirements": [
            {"id": "req1", "text": "Load the transactions dataset", "points": 25},
            {"id": "req2", "text": "Identify duplicate records", "points": 25},
            {
                "id": "req3",
                "text": "Remove duplicates while keeping first occurrence",
                "points": 25,
            },
            {"id": "req4", "text": "Verify deduplication was successful", "points": 25},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use pandas drop_duplicates() method",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Document the number of duplicates removed",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "transactions.csv",
            "validations": [
                {"name": "Dataset loaded", "type": "variable_exists", "variable": "df"},
                {
                    "name": "Duplicates removed",
                    "type": "custom_check",
                    "check": "df.duplicated().sum() == 0",
                },
                {
                    "name": "Data integrity maintained",
                    "type": "custom_check",
                    "check": "len(df) < 5000",
                },
                {
                    "name": "Duplicates count calculated",
                    "type": "variable_exists",
                    "variable": "duplicates_count",
                },
            ],
        },
        "hints": [
            "Use df.duplicated() to identify duplicate rows",
            "Consider which columns define a 'duplicate' - use subset parameter",
            "Keep track of how many duplicates were removed for reporting",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-003-data-types",
        "title": "Fix Data Types",
        "description": "Convert columns to appropriate data types and handle date parsing in a mixed dataset.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.DATA,
        "order_index": 3,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "35 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Load dataset and examine current data types",
                "points": 20,
            },
            {
                "id": "req2",
                "text": "Convert price column to numeric type",
                "points": 30,
            },
            {
                "id": "req3",
                "text": "Parse and convert date columns to datetime",
                "points": 30,
            },
            {
                "id": "req4",
                "text": "Convert categorical columns to category type",
                "points": 20,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Handle conversion errors gracefully",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Preserve data wherever possible",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "mixed_types.csv",
            "validations": [
                {"name": "Dataset loaded", "type": "variable_exists", "variable": "df"},
                {
                    "name": "Price is numeric",
                    "type": "custom_check",
                    "check": "pd.api.types.is_numeric_dtype(df['price'])",
                },
                {
                    "name": "Date is datetime",
                    "type": "custom_check",
                    "check": "pd.api.types.is_datetime64_any_dtype(df['date'])",
                },
                {
                    "name": "Category is categorical",
                    "type": "custom_check",
                    "check": "pd.api.types.is_categorical_dtype(df['category'])",
                },
            ],
        },
        "hints": [
            "Use pd.to_numeric() with errors='coerce' for safe conversion",
            "Use pd.to_datetime() for date parsing",
            "Use astype('category') for categorical data",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-004-outlier-detection",
        "title": "Detect and Handle Outliers",
        "description": "Identify outliers in a numerical dataset using statistical methods and decide on treatment.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.DATA,
        "order_index": 4,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "40 minutes",
        "requirements": [
            {"id": "req1", "text": "Calculate descriptive statistics", "points": 25},
            {"id": "req2", "text": "Identify outliers using IQR method", "points": 25},
            {
                "id": "req3",
                "text": "Identify outliers using Z-score method",
                "points": 25,
            },
            {"id": "req4", "text": "Create visualization of outliers", "points": 25},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use both IQR and Z-score methods",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Document outlier treatment decisions",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "sales_data.csv",
            "validations": [
                {"name": "Dataset loaded", "type": "variable_exists", "variable": "df"},
                {
                    "name": "IQR outliers identified",
                    "type": "variable_exists",
                    "variable": "iqr_outliers",
                },
                {
                    "name": "Z-score outliers identified",
                    "type": "variable_exists",
                    "variable": "zscore_outliers",
                },
                {
                    "name": "Statistics calculated",
                    "type": "variable_exists",
                    "variable": "stats",
                },
            ],
        },
        "hints": [
            "Use df.describe() for basic statistics",
            "IQR = Q3 - Q1, outliers are beyond Q1-1.5*IQR and Q3+1.5*IQR",
            "Z-score outliers are typically beyond ±3 standard deviations",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-005-data-validation",
        "title": "Data Validation and Quality Checks",
        "description": "Implement comprehensive data quality checks and validation rules for a business dataset.",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "track": ChallengeTrack.DATA,
        "order_index": 5,
        "points": 100,
        "model_tier": "local",
        "estimated_time": "45 minutes",
        "requirements": [
            {"id": "req1", "text": "Check for data completeness", "points": 25},
            {"id": "req2", "text": "Validate email format using regex", "points": 25},
            {"id": "req3", "text": "Check for reasonable value ranges", "points": 25},
            {"id": "req4", "text": "Generate data quality report", "points": 25},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use regular expressions for email validation",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Flag but don't remove invalid data",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "user_registrations.csv",
            "validations": [
                {"name": "Dataset loaded", "type": "variable_exists", "variable": "df"},
                {
                    "name": "Email validation performed",
                    "type": "variable_exists",
                    "variable": "email_valid",
                },
                {
                    "name": "Range checks performed",
                    "type": "variable_exists",
                    "variable": "age_valid",
                },
                {
                    "name": "Quality report created",
                    "type": "variable_exists",
                    "variable": "quality_report",
                },
            ],
        },
        "hints": [
            "Use regex pattern for email validation: r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'",
            "Check age ranges (e.g., 18-120) and salary ranges",
            "Create a summary report dictionary with validation results",
        ],
        "is_red_team": False,
    },
    # INTERMEDIATE: SQL Queries (6-10)
    {
        "slug": "data-006-basic-joins",
        "title": "Master SQL Joins",
        "description": "Write SQL queries using different join types to combine customer, order, and product data.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.DATA,
        "order_index": 6,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "50 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Write INNER JOIN to get customer orders",
                "points": 30,
            },
            {
                "id": "req2",
                "text": "Write LEFT JOIN to include all customers",
                "points": 30,
            },
            {
                "id": "req3",
                "text": "Write subquery for customer with most orders",
                "points": 40,
            },
            {
                "id": "req4",
                "text": "Calculate total order value per customer",
                "points": 50,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use proper SQL formatting and aliases",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Optimize queries for performance",
                "type": "performance",
            },
        ],
        "test_config": {
            "type": "sql",
            "setup_sql": """
                CREATE TABLE customers (
                    customer_id INTEGER PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    city VARCHAR(50)
                );
                CREATE TABLE orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    order_date DATE,
                    total_amount DECIMAL(10,2)
                );
                CREATE TABLE order_items (
                    item_id INTEGER PRIMARY KEY,
                    order_id INTEGER,
                    product_name VARCHAR(100),
                    quantity INTEGER,
                    price DECIMAL(10,2)
                );
                INSERT INTO customers VALUES 
                    (1, 'John Doe', 'john@email.com', 'New York'),
                    (2, 'Jane Smith', 'jane@email.com', 'Boston'),
                    (3, 'Bob Wilson', 'bob@email.com', 'Chicago');
                INSERT INTO orders VALUES 
                    (1, 1, '2024-01-15', 150.00),
                    (2, 1, '2024-02-01', 200.00),
                    (3, 2, '2024-01-20', 75.00);
                INSERT INTO order_items VALUES 
                    (1, 1, 'Widget A', 2, 25.00),
                    (2, 1, 'Widget B', 1, 100.00),
                    (3, 2, 'Widget C', 3, 50.00),
                    (4, 3, 'Widget A', 1, 25.00);
            """,
            "validations": [
                {"name": "Returns customer orders", "type": "row_count", "expected": 3},
                {
                    "name": "Includes customer names",
                    "type": "column_exists",
                    "column": "name",
                },
                {
                    "name": "Calculates totals correctly",
                    "type": "value_in_result",
                    "value": 350.00,
                    "column": "total_value",
                },
            ],
        },
        "hints": [
            "Start with INNER JOIN between customers and orders tables",
            "Use table aliases (c, o, oi) to make queries readable",
            "GROUP BY customer to calculate totals per customer",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-007-window-functions",
        "title": "Advanced Window Functions",
        "description": "Use SQL window functions for running totals, rankings, and moving averages in sales data.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.DATA,
        "order_index": 7,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "60 minutes",
        "requirements": [
            {"id": "req1", "text": "Calculate running total of sales", "points": 40},
            {
                "id": "req2",
                "text": "Rank customers by total purchase amount",
                "points": 40,
            },
            {"id": "req3", "text": "Calculate 3-month moving average", "points": 40},
            {
                "id": "req4",
                "text": "Find percentage of total sales per customer",
                "points": 30,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use proper window function syntax",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Handle edge cases in moving averages",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "sql",
            "setup_sql": """
                CREATE TABLE monthly_sales (
                    sale_id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    sale_date DATE,
                    amount DECIMAL(10,2)
                );
                INSERT INTO monthly_sales VALUES 
                    (1, 1, '2024-01-15', 1000.00),
                    (2, 1, '2024-02-15', 1200.00),
                    (3, 1, '2024-03-15', 800.00),
                    (4, 2, '2024-01-20', 1500.00),
                    (5, 2, '2024-02-20', 900.00),
                    (6, 3, '2024-01-10', 2000.00);
            """,
            "validations": [
                {
                    "name": "Running total calculated",
                    "type": "column_exists",
                    "column": "running_total",
                },
                {
                    "name": "Rankings assigned",
                    "type": "column_exists",
                    "column": "customer_rank",
                },
                {
                    "name": "Moving average computed",
                    "type": "column_exists",
                    "column": "moving_avg",
                },
            ],
        },
        "hints": [
            "Use SUM() OVER (ORDER BY date) for running totals",
            "Use RANK() or ROW_NUMBER() for rankings",
            "Use AVG() OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) for moving average",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-008-data-aggregation",
        "title": "Complex Aggregations",
        "description": "Perform complex grouping and aggregation operations on e-commerce data.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.DATA,
        "order_index": 8,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "45 minutes",
        "requirements": [
            {"id": "req1", "text": "Group sales by month and category", "points": 30},
            {
                "id": "req2",
                "text": "Calculate multiple aggregates (sum, avg, count)",
                "points": 40,
            },
            {
                "id": "req3",
                "text": "Use HAVING clause for filtering groups",
                "points": 40,
            },
            {"id": "req4", "text": "Create pivot-style report", "points": 40},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use efficient GROUP BY strategies",
                "type": "performance",
            },
            {"id": "con2", "text": "Handle NULL values properly", "type": "technical"},
        ],
        "test_config": {
            "type": "sql",
            "setup_sql": """
                CREATE TABLE product_sales (
                    sale_id INTEGER PRIMARY KEY,
                    product_category VARCHAR(50),
                    sale_date DATE,
                    quantity INTEGER,
                    unit_price DECIMAL(10,2),
                    total_amount DECIMAL(10,2)
                );
                INSERT INTO product_sales VALUES 
                    (1, 'Electronics', '2024-01-15', 2, 500.00, 1000.00),
                    (2, 'Electronics', '2024-01-20', 1, 300.00, 300.00),
                    (3, 'Clothing', '2024-01-25', 3, 50.00, 150.00),
                    (4, 'Electronics', '2024-02-01', 1, 800.00, 800.00),
                    (5, 'Clothing', '2024-02-05', 2, 75.00, 150.00);
            """,
            "validations": [
                {
                    "name": "Monthly grouping",
                    "type": "column_exists",
                    "column": "month",
                },
                {
                    "name": "Category aggregation",
                    "type": "column_exists",
                    "column": "category",
                },
                {"name": "Multiple metrics", "type": "row_count", "expected": 3},
            ],
        },
        "hints": [
            "Use strftime('%Y-%m', sale_date) to group by month",
            "Combine multiple aggregate functions in SELECT",
            "Use HAVING to filter aggregated results, not WHERE",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-009-performance-tuning",
        "title": "SQL Query Optimization",
        "description": "Optimize slow-running queries and understand query execution plans.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.DATA,
        "order_index": 9,
        "points": 150,
        "model_tier": "haiku",
        "estimated_time": "55 minutes",
        "requirements": [
            {"id": "req1", "text": "Identify query bottlenecks", "points": 30},
            {"id": "req2", "text": "Optimize JOIN operations", "points": 40},
            {"id": "req3", "text": "Use appropriate indexes", "points": 40},
            {"id": "req4", "text": "Rewrite subqueries as JOINs", "points": 40},
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Maintain query result accuracy",
                "type": "business",
            },
            {
                "id": "con2",
                "text": "Improve query performance by 50%",
                "type": "performance",
            },
        ],
        "test_config": {
            "type": "sql",
            "setup_sql": """
                CREATE TABLE large_orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    order_date DATE,
                    status VARCHAR(20),
                    total_amount DECIMAL(10,2)
                );
                CREATE INDEX idx_customer_date ON large_orders(customer_id, order_date);
                CREATE INDEX idx_status ON large_orders(status);
                INSERT INTO large_orders VALUES 
                    (1, 1, '2024-01-15', 'completed', 500.00),
                    (2, 1, '2024-01-20', 'pending', 300.00),
                    (3, 2, '2024-01-25', 'completed', 750.00),
                    (4, 3, '2024-02-01', 'completed', 1200.00);
            """,
            "validations": [
                {
                    "name": "Optimized query executes",
                    "type": "row_count",
                    "expected": 3,
                },
                {
                    "name": "Uses indexes efficiently",
                    "type": "column_exists",
                    "column": "total_amount",
                },
                {
                    "name": "Correct results returned",
                    "type": "value_in_result",
                    "value": "completed",
                    "column": "status",
                },
            ],
        },
        "hints": [
            "Use EXPLAIN QUERY PLAN to analyze query execution",
            "Ensure WHERE clauses use indexed columns",
            "Convert correlated subqueries to JOINs when possible",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-010-red-team-sql-injection",
        "title": "Red Team: SQL Injection Prevention",
        "description": "Identify and fix SQL injection vulnerabilities in data access code.",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "track": ChallengeTrack.DATA,
        "order_index": 10,
        "points": 200,
        "model_tier": "haiku",
        "estimated_time": "60 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Identify SQL injection vulnerabilities",
                "points": 50,
            },
            {"id": "req2", "text": "Implement parameterized queries", "points": 50},
            {"id": "req3", "text": "Add input validation", "points": 50},
            {"id": "req4", "text": "Test injection prevention", "points": 50},
        ],
        "constraints": [
            {"id": "con1", "text": "Use prepared statements", "type": "security"},
            {
                "id": "con2",
                "text": "Maintain functional requirements",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "vulnerable_code.py",
            "validations": [
                {
                    "name": "Vulnerabilities identified",
                    "type": "variable_exists",
                    "variable": "vulnerabilities",
                },
                {
                    "name": "Parameterized queries used",
                    "type": "custom_check",
                    "check": "'?' in secure_query or '%s' in secure_query",
                },
                {
                    "name": "Input validation added",
                    "type": "variable_exists",
                    "variable": "validate_input",
                },
                {
                    "name": "Security tests pass",
                    "type": "custom_check",
                    "check": "test_injection_prevention() == True",
                },
            ],
        },
        "hints": [
            "Look for string concatenation in SQL queries",
            "Use parameterized queries with ? placeholders",
            "Validate and sanitize all user inputs before querying",
        ],
        "is_red_team": True,
    },
    # ADVANCED: Analysis & ML (11-15)
    {
        "slug": "data-011-correlation-analysis",
        "title": "Correlation and Statistical Analysis",
        "description": "Perform comprehensive statistical analysis on a business dataset to uncover relationships.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.DATA,
        "order_index": 11,
        "points": 200,
        "model_tier": "sonnet",
        "estimated_time": "75 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Calculate correlation matrix for numerical variables",
                "points": 40,
            },
            {
                "id": "req2",
                "text": "Perform statistical significance tests",
                "points": 50,
            },
            {
                "id": "req3",
                "text": "Create correlation heatmap visualization",
                "points": 50,
            },
            {
                "id": "req4",
                "text": "Interpret results and provide business insights",
                "points": 60,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use scipy for statistical tests",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Set significance level at 0.05",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "business_metrics.csv",
            "validations": [
                {
                    "name": "Correlation matrix calculated",
                    "type": "variable_exists",
                    "variable": "correlation_matrix",
                },
                {
                    "name": "Statistical tests performed",
                    "type": "variable_exists",
                    "variable": "p_values",
                },
                {
                    "name": "Visualization created",
                    "type": "custom_check",
                    "check": "'matplotlib' in str(type(plt)) or 'seaborn' in str(type(sns))",
                },
                {
                    "name": "Business insights provided",
                    "type": "variable_exists",
                    "variable": "insights",
                },
            ],
        },
        "hints": [
            "Use df.corr() for correlation matrix",
            "Use scipy.stats for statistical tests like pearsonr()",
            "Use seaborn.heatmap() for visualization",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-012-ab-testing",
        "title": "A/B Testing Analysis",
        "description": "Design and analyze an A/B test to determine the impact of a website change on conversion rates.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.DATA,
        "order_index": 12,
        "points": 200,
        "model_tier": "sonnet",
        "estimated_time": "90 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Calculate conversion rates for both groups",
                "points": 40,
            },
            {
                "id": "req2",
                "text": "Perform statistical significance test (t-test)",
                "points": 50,
            },
            {"id": "req3", "text": "Calculate confidence intervals", "points": 50},
            {
                "id": "req4",
                "text": "Determine minimum sample size for power analysis",
                "points": 60,
            },
        ],
        "constraints": [
            {"id": "con1", "text": "Use 95% confidence level", "type": "business"},
            {
                "id": "con2",
                "text": "Account for multiple testing corrections",
                "type": "statistical",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "ab_test_data.csv",
            "validations": [
                {
                    "name": "Conversion rates calculated",
                    "type": "variable_exists",
                    "variable": "conversion_rates",
                },
                {
                    "name": "Statistical test performed",
                    "type": "variable_exists",
                    "variable": "t_statistic",
                },
                {
                    "name": "Confidence intervals calculated",
                    "type": "variable_exists",
                    "variable": "confidence_intervals",
                },
                {
                    "name": "Power analysis completed",
                    "type": "variable_exists",
                    "variable": "sample_size",
                },
            ],
        },
        "hints": [
            "Calculate conversion rate as conversions/total_visitors",
            "Use scipy.stats.ttest_ind for independent t-test",
            "Use statsmodels for power analysis and sample size calculation",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-013-cohort-analysis",
        "title": "Customer Cohort Analysis",
        "description": "Perform cohort analysis to understand customer retention patterns and lifetime value.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.DATA,
        "order_index": 13,
        "points": 200,
        "model_tier": "sonnet",
        "estimated_time": "85 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Create customer cohorts based on first purchase date",
                "points": 50,
            },
            {"id": "req2", "text": "Calculate retention rates by cohort", "points": 50},
            {
                "id": "req3",
                "text": "Analyze revenue per cohort over time",
                "points": 50,
            },
            {"id": "req4", "text": "Create cohort heatmap visualization", "points": 50},
        ],
        "constraints": [
            {"id": "con1", "text": "Use monthly cohorts", "type": "business"},
            {
                "id": "con2",
                "text": "Handle missing periods appropriately",
                "type": "technical",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "customer_transactions.csv",
            "validations": [
                {
                    "name": "Cohorts created",
                    "type": "variable_exists",
                    "variable": "cohort_data",
                },
                {
                    "name": "Retention rates calculated",
                    "type": "variable_exists",
                    "variable": "retention_rates",
                },
                {
                    "name": "Revenue analysis completed",
                    "type": "variable_exists",
                    "variable": "cohort_revenue",
                },
                {
                    "name": "Visualization created",
                    "type": "custom_check",
                    "check": "plt.gcf().get_axes() != []",
                },
            ],
        },
        "hints": [
            "Group customers by their first purchase month",
            "Calculate period numbers (0, 1, 2, ...) for each transaction",
            "Use pivot tables to create cohort matrices",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-014-machine-learning",
        "title": "Predictive Model Development",
        "description": "Build and evaluate a machine learning model to predict customer churn.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.DATA,
        "order_index": 14,
        "points": 250,
        "model_tier": "sonnet",
        "estimated_time": "120 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Perform feature engineering and selection",
                "points": 60,
            },
            {
                "id": "req2",
                "text": "Split data into training and testing sets",
                "points": 40,
            },
            {"id": "req3", "text": "Train and tune multiple models", "points": 80},
            {
                "id": "req4",
                "text": "Evaluate model performance with appropriate metrics",
                "points": 70,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Use cross-validation for model selection",
                "type": "technical",
            },
            {
                "id": "con2",
                "text": "Handle class imbalance if present",
                "type": "business",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "customer_churn.csv",
            "validations": [
                {
                    "name": "Features engineered",
                    "type": "variable_exists",
                    "variable": "X",
                },
                {
                    "name": "Data split performed",
                    "type": "variable_exists",
                    "variable": "X_train",
                },
                {
                    "name": "Models trained",
                    "type": "variable_exists",
                    "variable": "models",
                },
                {
                    "name": "Performance evaluated",
                    "type": "variable_exists",
                    "variable": "model_scores",
                },
            ],
        },
        "hints": [
            "Use sklearn for machine learning pipeline",
            "Try multiple algorithms: LogisticRegression, RandomForest, GradientBoosting",
            "Use metrics like precision, recall, F1-score for evaluation",
        ],
        "is_red_team": False,
    },
    {
        "slug": "data-015-red-team-data-privacy",
        "title": "Red Team: Data Privacy & GDPR Compliance",
        "description": "Implement data anonymization and ensure GDPR compliance in data processing workflows.",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "track": ChallengeTrack.DATA,
        "order_index": 15,
        "points": 250,
        "model_tier": "sonnet",
        "estimated_time": "90 minutes",
        "requirements": [
            {
                "id": "req1",
                "text": "Identify personally identifiable information (PII)",
                "points": 60,
            },
            {
                "id": "req2",
                "text": "Implement data anonymization techniques",
                "points": 70,
            },
            {"id": "req3", "text": "Create data retention policies", "points": 60},
            {
                "id": "req4",
                "text": "Build 'right to be forgotten' functionality",
                "points": 60,
            },
        ],
        "constraints": [
            {
                "id": "con1",
                "text": "Maintain data utility after anonymization",
                "type": "business",
            },
            {
                "id": "con2",
                "text": "Ensure irreversible anonymization",
                "type": "security",
            },
        ],
        "test_config": {
            "type": "python",
            "dataset": "customer_data.csv",
            "validations": [
                {
                    "name": "PII identified",
                    "type": "variable_exists",
                    "variable": "pii_fields",
                },
                {
                    "name": "Anonymization applied",
                    "type": "variable_exists",
                    "variable": "anonymized_data",
                },
                {
                    "name": "Retention policy implemented",
                    "type": "variable_exists",
                    "variable": "retention_policy",
                },
                {
                    "name": "Data deletion functionality",
                    "type": "variable_exists",
                    "variable": "delete_user_data",
                },
            ],
        },
        "hints": [
            "PII includes names, emails, phone numbers, addresses",
            "Use techniques like k-anonymity, l-diversity, differential privacy",
            "Implement automated data deletion based on retention periods",
        ],
        "is_red_team": True,
    },
]


async def seed_data_challenges():
    """Seed data science challenges to database"""

    async for db in get_db():
        try:
            for challenge_data in DATA_CHALLENGES:
                # Check if challenge already exists
                existing = await db.execute(
                    select(Challenge).where(Challenge.title == challenge_data["title"])
                )
                if existing.scalar_one_or_none():
                    print(
                        f"Challenge {challenge_data['title']} already exists, skipping..."
                    )
                    continue

                # Get data track ID
                track_result = await db.execute(
                    select(Track).where(Track.name == "Data Analysis")
                )
                track = track_result.scalar_one()

                # Create challenge
                challenge = Challenge(
                    title=challenge_data["title"],
                    description=challenge_data["description"],
                    track_id=track.id,
                    difficulty=challenge_data["difficulty"].value,
                    order_index=challenge_data["order_index"],
                    points=challenge_data["points"],
                    model_tier=challenge_data["model_tier"],
                    estimated_time_minutes=30,  # Default for now
                    requirements=challenge_data["requirements"],
                    constraints=challenge_data["constraints"],
                    test_config=challenge_data["test_config"],
                    hints=challenge_data["hints"],
                    is_red_team=challenge_data["is_red_team"],
                )

                db.add(challenge)
                print(f"Added challenge: {challenge_data['title']}")

            await db.commit()
            print(
                f"\n✅ Successfully seeded {len(DATA_CHALLENGES)} data science challenges!"
            )

        except Exception as e:
            await db.rollback()
            print(f"Error seeding challenges: {e}")
            raise

        break  # Only need first iteration


if __name__ == "__main__":
    asyncio.run(seed_data_challenges())
