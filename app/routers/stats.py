"""
API endpoints for PR review statistics
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.services.github_service import GitHubService
from app.services.analytics import AnalyticsService
from app.models.schemas import UserStats, StatsResponse

router = APIRouter()


@router.get("/stats/user/{username}", response_model=UserStats)
async def get_user_stats(
    username: str,
    org_name: Optional[str] = Query(None, description="Filter by organization"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get detailed statistics for a specific user's PR review contributions
    """
    try:
        github_service = GitHubService()
        analytics_service = AnalyticsService()
        
        # Parse dates if provided (YYYY-MM-DD format)
        start = None
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format. Use YYYY-MM-DD")
        
        end = None
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format. Use YYYY-MM-DD")
        
        # Fetch reviews
        if org_name:
            all_reviews = await github_service.get_organization_pr_reviews(
                org_name=org_name,
                start_date=start,
                end_date=end
            )
        else:
            # If no org specified, we'd need to search across all repos
            # For now, require org_name
            raise HTTPException(
                status_code=400,
                detail="org_name parameter is required"
            )
        
        # Filter reviews for this user
        user_reviews = [r for r in all_reviews if r.get("user", {}).get("login") == username]
        
        # Calculate user-specific stats
        stats = analytics_service.calculate_user_statistics(username, user_reviews)
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/organization/{org_name}", response_model=StatsResponse)
async def get_organization_stats(
    org_name: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    top_n: int = Query(10, description="Number of top contributors to return")
):
    """
    Get aggregated statistics for an organization's PR review activity
    """
    try:
        github_service = GitHubService()
        analytics_service = AnalyticsService()
        
        # Parse dates if provided (YYYY-MM-DD format)
        start = None
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format. Use YYYY-MM-DD")
        
        end = None
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format. Use YYYY-MM-DD")
        
        # Fetch PR reviews
        all_reviews = await github_service.get_organization_pr_reviews(
            org_name=org_name,
            start_date=start,
            end_date=end
        )
        
        # Calculate organization-wide stats
        contributions = analytics_service.calculate_user_contributions(all_reviews)
        org_stats = analytics_service.calculate_organization_statistics(
            contributions, all_reviews, top_n
        )
        
        # Set organization and date fields
        org_stats.organization = org_name
        org_stats.period_start = start_date
        org_stats.period_end = end_date
        
        return org_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

