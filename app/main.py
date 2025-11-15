"""
FastAPI application for GitHub PR Review Analytics
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import reports, stats

app = FastAPI(
    title="GitHub PR Review Analyzer",
    description="API for analyzing PR review contributions across an organization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(stats.router, prefix="/api/v1", tags=["statistics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GitHub PR Review Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

