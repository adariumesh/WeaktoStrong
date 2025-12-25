"""
FastAPI main application entry point for Weak-to-Strong platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Weak-to-Strong API",
    description="AI training platform backend",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Weak-to-Strong API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}