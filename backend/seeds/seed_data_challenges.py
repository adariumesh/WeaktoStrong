#!/usr/bin/env python3
"""
WeaktoStrong Data Analysis Challenge Seeder
Seeds the database with 6 progressive data science challenges
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import get_db
from app.models.challenge import Challenge, Track, ChallengeTrack, ChallengeDifficulty
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def seed_data_challenges():
    """Seed database with WeaktoStrong Data Analysis track challenges"""
    
    print("🌱 Seeding Data Analysis Challenges...")
    
    challenges = [
        {
            "id": "data-analysis-intro",
            "title": "Data Analysis Fundamentals",
            "description": """
Welcome to WeaktoStrong Data Analysis! 

Your mission: Analyze a simple sales dataset and extract basic insights.

**WeaktoStrong Philosophy**: Start with simple analysis before complex modeling.
Perfect for those who want to build confidence with data basics.

**Dataset**: sales_data.csv (100 rows of product sales)
**Goal**: Calculate total revenue and find the best-selling product.
            """.strip(),
            "difficulty": ChallengeDifficulty.BEGINNER.value,
            "track": ChallengeTrack.DATA.value,
            "points": 100,
            "estimated_time_minutes": 30,
            "initial_code": '''# WeaktoStrong Data Analysis Challenge 1: Fundamentals

# The dataset 'df' is already loaded for you
# Columns: product_name, quantity, price, sale_date

# TODO 1: Calculate total revenue
# Hint: revenue = quantity * price
total_revenue = None

# TODO 2: Find the product with highest total sales
# Hint: Group by product_name and sum quantities  
best_selling_product = None

# TODO 3: Calculate average order value
avg_order_value = None

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Best Selling Product: {best_selling_product}")
print(f"Average Order Value: ${avg_order_value:.2f}")
''',
            "validation_code": {
                "type": "python",
                "dataset": "sales_data.csv",
                "validations": [
                    {
                        "name": "Total Revenue Calculated",
                        "type": "variable_exists", 
                        "variable": "total_revenue"
                    },
                    {
                        "name": "Best Selling Product Found",
                        "type": "variable_exists",
                        "variable": "best_selling_product"
                    },
                    {
                        "name": "Revenue Value Check",
                        "type": "value_check",
                        "variable": "total_revenue",
                        "expected": 125430.50
                    }
                ]
            }
        },
        
        {
            "id": "data-cleaning-essentials",
            "title": "Data Cleaning & Preprocessing",
            "description": """
Real data is messy! Time to clean it up.

**Challenge**: Clean a customer dataset with missing values and outliers.

**WeaktoStrong Approach**: Build confidence with systematic cleaning
before attempting advanced preprocessing techniques.

**Dataset**: customer_data_messy.csv (500 rows with various issues)
**Goal**: Create a clean dataset ready for analysis.
            """.strip(),
            "difficulty": ChallengeDifficulty.BEGINNER.value,
            "track": ChallengeTrack.DATA.value,
            "points": 120,
            "estimated_time_minutes": 45,
            "initial_code": '''# WeaktoStrong Data Analysis Challenge 2: Data Cleaning

# The messy dataset 'df' is loaded
# Issues: missing ages, invalid emails, duplicate customers, outlier ages

# TODO 1: Handle missing values in 'age' column
# Fill with median age or remove rows with missing age
cleaned_df = df.copy()

# TODO 2: Remove duplicate customers based on email
# Keep the first occurrence

# TODO 3: Filter out unrealistic ages (< 18 or > 100)

# TODO 4: Clean email format (remove invalid emails)

# TODO 5: Create summary statistics
clean_rows = len(cleaned_df)
original_rows = len(df)
cleaning_summary = {
    'original_rows': original_rows,
    'clean_rows': clean_rows,
    'rows_removed': original_rows - clean_rows,
    'data_quality_score': (clean_rows / original_rows) * 100
}

print(f"Data Cleaning Complete:")
print(f"Original: {original_rows} rows")
print(f"Cleaned: {clean_rows} rows") 
print(f"Quality Score: {cleaning_summary['data_quality_score']:.1f}%")
''',
            "validation_code": {
                "type": "python",
                "dataset": "customer_data_messy.csv",
                "validations": [
                    {
                        "name": "Cleaned DataFrame Created",
                        "type": "variable_exists",
                        "variable": "cleaned_df"
                    },
                    {
                        "name": "Data Size Reduced",
                        "type": "custom_check",
                        "check_code": "len(cleaned_df) < len(df)"
                    },
                    {
                        "name": "No Missing Ages",
                        "type": "custom_check", 
                        "check_code": "cleaned_df['age'].isnull().sum() == 0"
                    }
                ]
            }
        },
        
        {
            "id": "exploratory-data-analysis",
            "title": "Exploratory Data Analysis",
            "description": """
Time to explore! Uncover patterns and insights through visualization.

**Mission**: Conduct comprehensive EDA on e-commerce transaction data.

**WeaktoStrong Method**: Start with simple plots, progress to complex insights.
Perfect for building analytical intuition.

**Dataset**: ecommerce_transactions.csv (1000+ transactions)
**Goal**: Generate actionable business insights through data exploration.
            """.strip(),
            "difficulty": ChallengeDifficulty.INTERMEDIATE.value,
            "track": ChallengeTrack.DATA.value, 
            "points": 150,
            "estimated_time_minutes": 50,
            "initial_code": '''# WeaktoStrong Data Analysis Challenge 3: Exploratory Data Analysis

import matplotlib.pyplot as plt
import seaborn as sns

# Dataset 'df' contains: transaction_id, customer_id, product_category, 
# amount, transaction_date, customer_segment, region

# TODO 1: Basic statistics and data overview
data_summary = {
    'total_transactions': len(df),
    'total_revenue': df['amount'].sum(),
    'avg_transaction_value': df['amount'].mean(),
    'unique_customers': df['customer_id'].nunique()
}

# TODO 2: Revenue by product category
revenue_by_category = df.groupby('product_category')['amount'].sum().sort_values(ascending=False)

# TODO 3: Customer segment analysis
segment_analysis = df.groupby('customer_segment').agg({
    'amount': ['count', 'sum', 'mean'],
    'customer_id': 'nunique'
}).round(2)

# TODO 4: Monthly revenue trend (if date parsing works)
# Convert transaction_date to datetime and extract month

# TODO 5: Key insights summary
key_insights = [
    f"Top revenue category: {revenue_by_category.index[0]}",
    f"Most valuable segment: {segment_analysis.loc[segment_analysis[('amount', 'mean')].idxmax()].name}",
    f"Average customer value: ${data_summary['avg_transaction_value']:.2f}"
]

print("=== EDA INSIGHTS ===")
for insight in key_insights:
    print(f"• {insight}")
    
print(f"\\nTotal Revenue: ${data_summary['total_revenue']:,.2f}")
print(f"Total Customers: {data_summary['unique_customers']:,}")
''',
            "validation_code": {
                "type": "python",
                "dataset": "ecommerce_transactions.csv",
                "validations": [
                    {
                        "name": "Data Summary Created",
                        "type": "variable_exists",
                        "variable": "data_summary"
                    },
                    {
                        "name": "Revenue Analysis Done",
                        "type": "variable_exists",
                        "variable": "revenue_by_category"
                    },
                    {
                        "name": "Insights Generated",
                        "type": "variable_exists",
                        "variable": "key_insights"
                    },
                    {
                        "name": "Multiple Insights Found",
                        "type": "custom_check",
                        "check_code": "len(key_insights) >= 3"
                    }
                ]
            }
        },
        
        {
            "id": "statistical-analysis",
            "title": "Statistical Analysis with Python",
            "description": """
Move beyond descriptive stats to inferential analysis!

**Challenge**: Perform statistical tests to validate business hypotheses.

**WeaktoStrong Progression**: Use simple t-tests before complex modeling.
Build statistical intuition through practical application.

**Dataset**: ab_test_results.csv (A/B test conversion data)
**Goal**: Determine statistical significance and business impact.
            """.strip(),
            "difficulty": ChallengeDifficulty.INTERMEDIATE.value,
            "track": ChallengeTrack.DATA.value,
            "points": 200,
            "estimated_time_minutes": 60,
            "initial_code": '''# WeaktoStrong Data Analysis Challenge 4: Statistical Analysis

from scipy import stats
import numpy as np

# Dataset 'df' contains A/B test results: user_id, variant, converted, revenue

# TODO 1: Basic conversion rates
conversion_rates = df.groupby('variant')['converted'].agg(['count', 'sum', 'mean'])
control_rate = conversion_rates.loc['control', 'mean']
treatment_rate = conversion_rates.loc['treatment', 'mean']

# TODO 2: Statistical significance test
control_conversions = df[df['variant'] == 'control']['converted']
treatment_conversions = df[df['variant'] == 'treatment']['converted']

# Perform two-sample t-test
t_stat, p_value = stats.ttest_ind(treatment_conversions, control_conversions)

# TODO 3: Effect size calculation
effect_size = treatment_rate - control_rate
relative_improvement = (effect_size / control_rate) * 100

# TODO 4: Confidence interval for difference
pooled_std = np.sqrt(((len(control_conversions)-1)*control_conversions.var() + 
                     (len(treatment_conversions)-1)*treatment_conversions.var()) / 
                     (len(control_conversions)+len(treatment_conversions)-2))

margin_error = 1.96 * pooled_std * np.sqrt(1/len(control_conversions) + 1/len(treatment_conversions))
ci_lower = effect_size - margin_error  
ci_upper = effect_size + margin_error

# TODO 5: Statistical summary
statistical_summary = {
    'control_rate': control_rate,
    'treatment_rate': treatment_rate, 
    'effect_size': effect_size,
    'relative_improvement_pct': relative_improvement,
    'p_value': p_value,
    'is_significant': p_value < 0.05,
    'confidence_interval': (ci_lower, ci_upper)
}

print("=== STATISTICAL ANALYSIS RESULTS ===")
print(f"Control Conversion Rate: {control_rate:.3f}")
print(f"Treatment Conversion Rate: {treatment_rate:.3f}")
print(f"Effect Size: {effect_size:.3f}")
print(f"Relative Improvement: {relative_improvement:.1f}%")
print(f"P-value: {p_value:.4f}")
print(f"Statistically Significant: {p_value < 0.05}")
''',
            "validation_code": {
                "type": "python", 
                "dataset": "ab_test_results.csv",
                "validations": [
                    {
                        "name": "Conversion Rates Calculated",
                        "type": "variable_exists",
                        "variable": "conversion_rates"
                    },
                    {
                        "name": "Statistical Test Performed",
                        "type": "variable_exists",
                        "variable": "p_value"
                    },
                    {
                        "name": "Effect Size Calculated", 
                        "type": "variable_exists",
                        "variable": "effect_size"
                    },
                    {
                        "name": "Statistical Summary Created",
                        "type": "variable_exists",
                        "variable": "statistical_summary"
                    }
                ]
            }
        },
        
        {
            "id": "machine-learning-intro",
            "title": "Introduction to Machine Learning",
            "description": """
Your first ML model! Predict customer behavior using scikit-learn.

**Mission**: Build a regression model to predict customer lifetime value.

**WeaktoStrong Philosophy**: Start with linear regression before complex algorithms.
Focus on understanding predictions over perfect accuracy.

**Dataset**: customer_features.csv (customer demographics + CLV)
**Goal**: Create a working predictive model with interpretable results.
            """.strip(),
            "difficulty": ChallengeDifficulty.INTERMEDIATE.value,
            "track": ChallengeTrack.DATA.value,
            "points": 250, 
            "estimated_time_minutes": 75,
            "initial_code": '''# WeaktoStrong Data Analysis Challenge 5: Machine Learning Intro

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Dataset 'df': age, income, tenure_months, num_purchases, customer_lifetime_value

# TODO 1: Prepare features and target
features = ['age', 'income', 'tenure_months', 'num_purchases']
X = df[features] 
y = df['customer_lifetime_value']

# TODO 2: Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# TODO 3: Scale features for better performance
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# TODO 4: Train linear regression model
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# TODO 5: Make predictions and evaluate
y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# TODO 6: Feature importance analysis
feature_importance = dict(zip(features, model.coef_))
most_important_feature = max(feature_importance, key=feature_importance.get)

# TODO 7: Model summary
model_summary = {
    'mse': mse,
    'r2_score': r2,
    'feature_importance': feature_importance,
    'most_important_feature': most_important_feature,
    'model_performance': 'good' if r2 > 0.5 else 'needs_improvement'
}

print("=== MACHINE LEARNING MODEL RESULTS ===")
print(f"R² Score: {r2:.3f}")
print(f"Mean Squared Error: {mse:,.2f}")
print(f"Most Important Feature: {most_important_feature}")
print(f"Model Performance: {model_summary['model_performance']}")

# Example prediction
sample_prediction = model.predict(scaler.transform([[35, 50000, 24, 12]]))[0]
print(f"\\nSample CLV Prediction: ${sample_prediction:,.2f}")
''',
            "validation_code": {
                "type": "python",
                "dataset": "customer_features.csv", 
                "validations": [
                    {
                        "name": "Model Created",
                        "type": "variable_exists",
                        "variable": "model"
                    },
                    {
                        "name": "Predictions Generated",
                        "type": "variable_exists", 
                        "variable": "y_pred"
                    },
                    {
                        "name": "R² Score Calculated",
                        "type": "variable_exists",
                        "variable": "r2"
                    },
                    {
                        "name": "Feature Importance Analyzed",
                        "type": "variable_exists",
                        "variable": "feature_importance"
                    },
                    {
                        "name": "Decent Model Performance",
                        "type": "custom_check",
                        "check_code": "r2 > 0.3"  # Reasonable baseline
                    }
                ]
            }
        },
        
        {
            "id": "advanced-ml-techniques", 
            "title": "Advanced ML Techniques",
            "description": """
Master advanced techniques! Feature engineering, hyperparameter tuning, and model evaluation.

**Final Challenge**: Build an optimized ML pipeline for customer churn prediction.

**WeaktoStrong Mastery**: Apply all learned concepts to create production-ready model.
Demonstrate analytical maturity through systematic approach.

**Dataset**: customer_churn.csv (comprehensive customer data + churn labels)
**Goal**: Deploy a complete ML solution with documented insights.
            """.strip(),
            "difficulty": ChallengeDifficulty.ADVANCED.value,
            "track": ChallengeTrack.DATA.value,
            "points": 300,
            "estimated_time_minutes": 90,
            "initial_code": '''# WeaktoStrong Data Analysis Challenge 6: Advanced ML Techniques

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pandas as pd

# Dataset 'df': comprehensive customer data with 'churn' target variable

# TODO 1: Advanced feature engineering
# Create new features from existing ones
df['tenure_years'] = df['tenure_months'] / 12
df['avg_monthly_spend'] = df['total_charges'] / df['tenure_months']
df['calls_per_month'] = df['customer_service_calls'] / df['tenure_months']

# TODO 2: Encode categorical variables
categorical_features = df.select_dtypes(include=['object']).columns
for col in categorical_features:
    if col != 'churn':
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

# TODO 3: Feature selection and preparation  
feature_cols = [col for col in df.columns if col != 'churn']
X = df[feature_cols]
y = df['churn']

# TODO 4: Train/validation split with stratification
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# TODO 5: Hyperparameter tuning with GridSearch
param_grid = {
    'n_estimators': [50, 100], 
    'max_depth': [5, 10, None],
    'min_samples_split': [2, 5]
}

rf_model = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(rf_model, param_grid, cv=3, scoring='roc_auc')
grid_search.fit(X_train, y_train)

# TODO 6: Best model evaluation
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)
y_pred_proba = best_model.predict_proba(X_test)[:, 1]

# TODO 7: Comprehensive model evaluation
auc_score = roc_auc_score(y_test, y_pred_proba)
cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='roc_auc')

# TODO 8: Feature importance for interpretability
feature_importance = dict(zip(feature_cols, best_model.feature_importances_))
top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]

# TODO 9: Final model summary
final_model_summary = {
    'auc_score': auc_score,
    'cv_mean': cv_scores.mean(),
    'cv_std': cv_scores.std(), 
    'best_params': grid_search.best_params_,
    'top_features': top_features,
    'model_quality': 'excellent' if auc_score > 0.8 else 'good' if auc_score > 0.7 else 'fair'
}

print("=== ADVANCED ML MODEL RESULTS ===")
print(f"AUC Score: {auc_score:.3f}")
print(f"Cross-validation: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
print(f"Model Quality: {final_model_summary['model_quality']}")
print(f"Best Parameters: {grid_search.best_params_}")
print("\\nTop 5 Features:")
for feature, importance in top_features:
    print(f"  {feature}: {importance:.3f}")
''',
            "validation_code": {
                "type": "python",
                "dataset": "customer_churn.csv",
                "validations": [
                    {
                        "name": "Advanced Model Created",
                        "type": "variable_exists",
                        "variable": "best_model"
                    },
                    {
                        "name": "Hyperparameter Tuning Done",
                        "type": "variable_exists",
                        "variable": "grid_search"
                    },
                    {
                        "name": "AUC Score Calculated",
                        "type": "variable_exists",
                        "variable": "auc_score"
                    },
                    {
                        "name": "Feature Engineering Applied", 
                        "type": "custom_check",
                        "check_code": "'tenure_years' in df.columns"
                    },
                    {
                        "name": "Model Performance Evaluation",
                        "type": "variable_exists",
                        "variable": "final_model_summary"
                    },
                    {
                        "name": "Good Model Performance",
                        "type": "custom_check",
                        "check_code": "auc_score > 0.6"  # Reasonable performance
                    }
                ]
            }
        }
    ]
    
    async for db in get_db():
        try:
            # Get data track ID
            track_result = await db.execute(
                text("SELECT id FROM tracks WHERE name = 'Data Analysis'")
            )
            track_id = track_result.scalar_one()
            print(f"📍 Found Data Analysis track: {track_id}")
            
            # Clear existing data analysis challenges
            await db.execute(
                text("DELETE FROM challenges WHERE track_id = :track_id"),
                {"track_id": track_id}
            )
            
            # Insert new challenges using raw SQL to match database schema exactly
            for i, challenge_data in enumerate(challenges):
                # Build the SQL with proper casting
                insert_sql = text(f"""
                    INSERT INTO challenges (
                        track_id, title, description, difficulty, order_index, 
                        requirements, constraints, test_config, hints, 
                        is_red_team, points, estimated_time_minutes, model_tier,
                        validation_rules, created_at
                    ) VALUES (
                        '{track_id}',
                        '{challenge_data["title"].replace("'", "''")}',
                        '{challenge_data["description"].replace("'", "''")}',
                        '{challenge_data["difficulty"]}'::challenge_difficulty,
                        {i + 1},
                        '[]'::jsonb,
                        '[]'::jsonb,
                        '{{}}'::jsonb,
                        '[]'::jsonb,
                        {str(False).lower()},
                        {challenge_data["points"]},
                        {challenge_data["estimated_time_minutes"]},
                        'local'::model_tier,
                        '{json.dumps(challenge_data["validation_code"]).replace("'", "''")}' ::json,
                        CURRENT_TIMESTAMP
                    )
                """)
                
                await db.execute(insert_sql)
                print(f"✅ Added challenge: {challenge_data['title']}")
            
            await db.commit()
            print(f"\\n🎉 Successfully seeded {len(challenges)} Data Analysis challenges!")
            print("\\n📊 Challenge Progression:")
            print("1. Data Analysis Fundamentals (100 pts) - Basic calculations")
            print("2. Data Cleaning & Preprocessing (120 pts) - Handle messy data")  
            print("3. Exploratory Data Analysis (150 pts) - Visual insights")
            print("4. Statistical Analysis (200 pts) - Hypothesis testing")
            print("5. Machine Learning Intro (250 pts) - First ML model")
            print("6. Advanced ML Techniques (300 pts) - Production pipeline")
            print("\\nTotal Track Value: 1,120 points")
            
        except Exception as e:
            print(f"❌ Error seeding challenges: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_data_challenges())