"""
FastAPI main application
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1 import api_router
from app.core.database import get_db
from app.schemas.auth import UserCreate, UserLogin, TokenResponse
from app.services.auth import AuthService
from sqlalchemy import text
from pydantic import BaseModel

app = FastAPI(
    title="Weak-to-Strong API",
    description="AI training platform backend",
    version="0.1.0",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Weak-to-Strong API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Temporary direct auth endpoints for MVP
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user - temporary MVP endpoint"""
    auth_service = AuthService(db)
    return await auth_service.register_user(user_data)


@app.post("/auth/login", response_model=TokenResponse) 
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login user - temporary MVP endpoint"""
    auth_service = AuthService(db)
    return await auth_service.login_user(login_data)


# Temporary challenge endpoints for MVP
@app.get("/challenges")
async def get_challenges(db: AsyncSession = Depends(get_db)):
    """Get all challenges - temporary MVP endpoint using direct SQL"""
    result = await db.execute(text("""
        SELECT id, title, description, difficulty, points, estimated_time_minutes 
        FROM challenges 
        ORDER BY order_index
    """))
    
    challenges = []
    for row in result:
        challenges.append({
            "id": str(row.id),
            "title": row.title,
            "description": row.description,
            "difficulty": row.difficulty,
            "points": row.points,
            "estimated_time_minutes": row.estimated_time_minutes,
        })
    
    return challenges


class ChallengeSubmission(BaseModel):
    challenge_id: str
    code: str


@app.post("/submit")
async def submit_challenge(
    submission: ChallengeSubmission,
    db: AsyncSession = Depends(get_db)
):
    """Submit solution for a challenge - temporary MVP endpoint"""
    
    # Simple validation - check if code contains required elements
    code = submission.code.lower()
    
    if "h1" in code and "hello" in code:
        result = {
            "success": True,
            "message": "Challenge completed successfully!",
            "score": 100,
            "feedback": "Great job! Your HTML contains the required h1 tag with Hello World."
        }
    else:
        result = {
            "success": False,
            "message": "Challenge not completed",
            "score": 0,
            "feedback": "Make sure to include an h1 tag with 'Hello, World' text."
        }
    
    return result


# Get available challenges
@app.get("/challenges", response_model=list)
async def get_challenges():
    """Get all available challenges for Data Analysis track"""
    
    # Return Data Analysis track challenges for WeaktoStrong pivot
    return [
        {
            "id": "data-analysis-intro",
            "title": "Data Analysis Fundamentals",
            "description": "Learn to analyze datasets using pandas. Extract insights from CSV data, perform basic statistics, and create visualizations. Practice WeaktoStrong methodology by starting with simple analysis before complex modeling.",
            "difficulty": "beginner",
            "points": 100,
            "estimated_time_minutes": 30
        },
        {
            "id": "data-cleaning-essentials", 
            "title": "Data Cleaning & Preprocessing",
            "description": "Master data preprocessing techniques. Handle missing values, detect outliers, and prepare data for analysis. Build confidence with basic cleaning before advanced transformations.",
            "difficulty": "beginner",
            "points": 120,
            "estimated_time_minutes": 45
        },
        {
            "id": "exploratory-data-analysis",
            "title": "Exploratory Data Analysis",
            "description": "Conduct comprehensive EDA using matplotlib and seaborn. Create compelling visualizations, identify patterns, and generate data-driven insights.",
            "difficulty": "intermediate",
            "points": 150,
            "estimated_time_minutes": 50
        },
        {
            "id": "statistical-analysis",
            "title": "Statistical Analysis with Python",
            "description": "Perform statistical tests, calculate confidence intervals, and interpret statistical significance using scipy and statsmodels.",
            "difficulty": "intermediate", 
            "points": 200,
            "estimated_time_minutes": 60
        },
        {
            "id": "machine-learning-intro",
            "title": "Introduction to Machine Learning",
            "description": "Build your first ML models using scikit-learn. Start with simple linear regression before progressing to complex algorithms.",
            "difficulty": "intermediate",
            "points": 250,
            "estimated_time_minutes": 75
        },
        {
            "id": "advanced-ml-techniques",
            "title": "Advanced ML Techniques", 
            "description": "Master feature engineering, hyperparameter tuning, and model evaluation. Apply WeaktoStrong principles to model selection.",
            "difficulty": "advanced",
            "points": 300,
            "estimated_time_minutes": 90
        }
    ]


# Temporary mock progress endpoints for dashboard (no auth for now)
@app.get("/progress/")
async def get_user_progress_mock():
    """Get user progress - temporary mock for dashboard"""
    return {
        "user_id": "34b555e3-a77e-4ea7-b8c6-f68c031a214e",
        "total_points": 420,
        "challenges_completed": 2,
        "challenges_attempted": 3,
        "completion_rate": 66.7,
        "current_streak": 5,
        "longest_streak": 12,
        "ai_tier_unlocked": "haiku",
        "web_track_completed": 0,
        "data_track_completed": 2,
        "cloud_track_completed": 0,
        "last_activity": "2024-12-24T14:30:00Z",
        "achievements_count": 8,
        "badges_count": 5
    }

@app.get("/progress/streaks")
async def get_user_streaks_mock():
    """Get user streaks - temporary mock for dashboard"""
    return {
        "current_streak": 5,
        "longest_streak": 12,
        "streak_active": True,
        "days_until_reset": 2
    }

@app.get("/progress/leaderboard")
async def get_leaderboard_mock():
    """Get leaderboard - temporary mock for dashboard"""
    return [
        {
            "rank": 1,
            "user_id": "demo-user",
            "name": "Demo User",
            "avatar_url": None,
            "points": 420,
            "completed": 2,
            "streak": 5,
            "tier": "free"
        }
    ]

@app.post("/progress/refresh")
async def refresh_progress_mock():
    """Refresh progress - temporary mock for dashboard"""
    return {
        "message": "Progress refreshed successfully",
        "progress": {
            "total_points": 420,
            "challenges_completed": 2,
            "current_streak": 5,
            "ai_tier": "haiku"
        }
    }

# Basic progress endpoint for dashboard
@app.get("/api/v1/progress/stats")
async def get_progress_stats():
    """Get user progress statistics for dashboard"""
    
    # Mock progress data for MVP demonstration
    return {
        "overview": {
            "total_points": 420,
            "challenges_completed": 2,
            "challenges_attempted": 3,
            "completion_rate": 66.7,
            "ai_tier": "haiku"
        },
        "streaks": {
            "current_streak": 5,
            "longest_streak": 12,
            "streak_active": True,
            "days_until_reset": 2
        },
        "achievements": {
            "earned": 8,
            "total": 24,
            "recent": [
                {"title": "First Steps", "earned_at": "2024-12-24"},
                {"title": "Data Detective", "earned_at": "2024-12-23"}
            ]
        },
        "tracks": {
            "web": {"completed": 0, "total": 6, "points": 0},
            "data": {"completed": 2, "total": 6, "points": 220},
            "cloud": {"completed": 0, "total": 6, "points": 0}
        },
        "activity": {
            "last_activity": "2024-12-24T14:30:00Z",
            "ai_requests_total": 47
        }
    }
