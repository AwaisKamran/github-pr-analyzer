"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserContribution(BaseModel):
    """Individual user contribution data"""
    username: str
    total_reviews: int
    approved_reviews: int
    changes_requested: int
    commented_reviews: int
    average_review_time_hours: Optional[float] = None
    repositories_reviewed: List[str] = []
    review_distribution: Dict[str, int] = {}  # Distribution by repository


class Summary(BaseModel):
    """Summary statistics"""
    total_prs_reviewed: int
    total_unique_reviewers: int
    average_reviews_per_pr: float
    most_active_reviewer: Optional[str] = None
    review_approval_rate: float
    average_time_to_review_hours: Optional[float] = None


class ReportResponse(BaseModel):
    """Complete report response"""
    organization: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    total_reviews: int
    total_contributors: int
    user_contributions: List[UserContribution]
    summary: Summary


class UserStats(BaseModel):
    """Detailed user statistics"""
    username: str
    total_reviews: int
    approved_reviews: int
    changes_requested: int
    commented_reviews: int
    average_review_time_hours: Optional[float] = None
    repositories_reviewed: List[str] = []
    review_timeline: List[Dict[str, Any]] = []  # Reviews over time
    review_types_distribution: Dict[str, int] = {}


class TopContributor(BaseModel):
    """Top contributor information"""
    username: str
    total_reviews: int
    percentage_of_total: float


class StatsResponse(BaseModel):
    """Organization statistics response"""
    organization: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    total_reviews: int
    total_unique_reviewers: int
    average_reviews_per_pr: float
    top_contributors: List[TopContributor]
    review_activity_over_time: Dict[str, int] = {}  # Reviews by date

