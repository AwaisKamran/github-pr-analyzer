"""
API endpoints for generating PR review reports
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.services.github_service import GitHubService
from app.services.analytics import AnalyticsService
from app.models.schemas import ReportResponse, UserContribution

router = APIRouter()


@router.get("/reports/organization/{org_name}", response_model=ReportResponse)
async def get_organization_report(
    org_name: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    repositories: Optional[str] = Query(None, description="Comma-separated list of repository names to filter")
):
    """
    Generate a comprehensive report of PR review contributions for an organization
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
        
        # Parse repository filter
        repo_list = [r.strip() for r in repositories.split(",")] if repositories else None
        
        # Fetch PR reviews from all repositories in the organization
        all_reviews = await github_service.get_organization_pr_reviews(
            org_name=org_name,
            start_date=start,
            end_date=end,
            repositories=repo_list
        )
        
        # Generate analytics
        contributions = analytics_service.calculate_user_contributions(all_reviews)
        summary = analytics_service.generate_summary(contributions, all_reviews)
        
        return ReportResponse(
            organization=org_name,
            period_start=start_date,
            period_end=end_date,
            total_reviews=len(all_reviews),
            total_contributors=len(contributions),
            user_contributions=contributions,
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/repository/{owner}/{repo}", response_model=ReportResponse)
async def get_repository_report(
    owner: str,
    repo: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Generate a report of PR review contributions for a specific repository
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
        
        # Fetch PR reviews from the repository
        all_reviews = await github_service.get_repository_pr_reviews(
            owner=owner,
            repo=repo,
            start_date=start,
            end_date=end
        )
        
        # Generate analytics
        contributions = analytics_service.calculate_user_contributions(all_reviews)
        summary = analytics_service.generate_summary(contributions, all_reviews)
        
        return ReportResponse(
            organization=f"{owner}/{repo}",
            period_start=start_date,
            period_end=end_date,
            total_reviews=len(all_reviews),
            total_contributors=len(contributions),
            user_contributions=contributions,
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

