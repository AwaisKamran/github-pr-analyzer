"""
Analytics service for calculating PR review statistics
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from app.models.schemas import (
    UserContribution, Summary, UserStats, TopContributor, StatsResponse
)


class AnalyticsService:
    """Service for analyzing PR review data"""
    
    def calculate_user_contributions(
        self,
        reviews: List[Dict[str, Any]]
    ) -> List[UserContribution]:
        """
        Calculate contribution statistics for each user
        
        Args:
            reviews: List of PR review dictionaries
            
        Returns:
            List of UserContribution objects
        """
        user_data = defaultdict(lambda: {
            "total_reviews": 0,
            "approved_reviews": 0,
            "changes_requested": 0,
            "commented_reviews": 0,
            "review_times": [],
            "repositories": set(),
            "review_distribution": defaultdict(int)
        })
        
        # Aggregate data by user
        for review in reviews:
            user = review.get("user", {})
            username = user.get("login")
            if not username:
                continue
            
            state = review.get("state", "").lower()
            repo = review.get("repository", "unknown")
            
            user_data[username]["total_reviews"] += 1
            user_data[username]["repositories"].add(repo)
            user_data[username]["review_distribution"][repo] += 1
            
            if state == "approved":
                user_data[username]["approved_reviews"] += 1
            elif state == "changes_requested":
                user_data[username]["changes_requested"] += 1
            elif state == "commented":
                user_data[username]["commented_reviews"] += 1
            
            # Calculate review time (time between PR creation and review)
            pr_created = review.get("pr_created_at")
            review_submitted = review.get("submitted_at")
            
            if pr_created and review_submitted:
                try:
                    pr_time = self._parse_datetime(pr_created)
                    review_time = self._parse_datetime(review_submitted)
                    if pr_time and review_time:
                        hours = (review_time - pr_time).total_seconds() / 3600
                        if hours >= 0:  # Only count positive times
                            user_data[username]["review_times"].append(hours)
                except Exception:
                    pass
        
        # Convert to UserContribution objects
        contributions = []
        for username, data in user_data.items():
            avg_time = (
                sum(data["review_times"]) / len(data["review_times"])
                if data["review_times"] else None
            )
            
            contributions.append(UserContribution(
                username=username,
                total_reviews=data["total_reviews"],
                approved_reviews=data["approved_reviews"],
                changes_requested=data["changes_requested"],
                commented_reviews=data["commented_reviews"],
                average_review_time_hours=avg_time,
                repositories_reviewed=sorted(list(data["repositories"])),
                review_distribution=dict(data["review_distribution"])
            ))
        
        # Sort by total reviews (descending)
        contributions.sort(key=lambda x: x.total_reviews, reverse=True)
        
        return contributions
    
    def generate_summary(
        self,
        contributions: List[UserContribution],
        reviews: List[Dict[str, Any]]
    ) -> Summary:
        """Generate summary statistics"""
        if not reviews:
            return Summary(
                total_prs_reviewed=0,
                total_unique_reviewers=0,
                average_reviews_per_pr=0.0,
                review_approval_rate=0.0
            )
        
        # Count unique PRs
        unique_prs = set()
        for review in reviews:
            repo = review.get("repository")
            pr_num = review.get("pr_number")
            if repo and pr_num:
                unique_prs.add(f"{repo}#{pr_num}")
        
        # Calculate average reviews per PR
        avg_reviews = len(reviews) / len(unique_prs) if unique_prs else 0.0
        
        # Find most active reviewer
        most_active = contributions[0].username if contributions else None
        
        # Calculate approval rate
        total_approved = sum(c.approved_reviews for c in contributions)
        approval_rate = (total_approved / len(reviews) * 100) if reviews else 0.0
        
        # Calculate average time to review
        all_review_times = []
        for review in reviews:
            pr_created = review.get("pr_created_at")
            review_submitted = review.get("submitted_at")
            if pr_created and review_submitted:
                try:
                    pr_time = self._parse_datetime(pr_created)
                    review_time = self._parse_datetime(review_submitted)
                    if pr_time and review_time:
                        hours = (review_time - pr_time).total_seconds() / 3600
                        if hours >= 0:
                            all_review_times.append(hours)
                except Exception:
                    pass
        
        avg_time = (
            sum(all_review_times) / len(all_review_times)
            if all_review_times else None
        )
        
        return Summary(
            total_prs_reviewed=len(unique_prs),
            total_unique_reviewers=len(contributions),
            average_reviews_per_pr=round(avg_reviews, 2),
            most_active_reviewer=most_active,
            review_approval_rate=round(approval_rate, 2),
            average_time_to_review_hours=round(avg_time, 2) if avg_time else None
        )
    
    def calculate_user_statistics(
        self,
        username: str,
        reviews: List[Dict[str, Any]]
    ) -> UserStats:
        """Calculate detailed statistics for a specific user"""
        if not reviews:
            return UserStats(
                username=username,
                total_reviews=0,
                approved_reviews=0,
                changes_requested=0,
                commented_reviews=0
            )
        
        approved = sum(1 for r in reviews if r.get("state", "").lower() == "approved")
        changes_requested = sum(1 for r in reviews if r.get("state", "").lower() == "changes_requested")
        commented = sum(1 for r in reviews if r.get("state", "").lower() == "commented")
        
        # Calculate review times
        review_times = []
        for review in reviews:
            pr_created = review.get("pr_created_at")
            review_submitted = review.get("submitted_at")
            if pr_created and review_submitted:
                try:
                    pr_time = self._parse_datetime(pr_created)
                    review_time = self._parse_datetime(review_submitted)
                    if pr_time and review_time:
                        hours = (review_time - pr_time).total_seconds() / 3600
                        if hours >= 0:
                            review_times.append(hours)
                except Exception:
                    pass
        
        avg_time = sum(review_times) / len(review_times) if review_times else None
        
        # Get repositories
        repositories = sorted(list(set(r.get("repository", "unknown") for r in reviews)))
        
        # Review timeline
        timeline = []
        for review in reviews:
            submitted = review.get("submitted_at")
            if submitted:
                try:
                    date = self._parse_datetime(submitted)
                    if date:
                        timeline.append({
                            "date": date.isoformat(),
                            "state": review.get("state", "").lower(),
                            "repository": review.get("repository"),
                            "pr_number": review.get("pr_number")
                        })
                except Exception:
                    pass
        
        # Review types distribution
        review_types = defaultdict(int)
        for review in reviews:
            state = review.get("state", "").lower()
            review_types[state] += 1
        
        return UserStats(
            username=username,
            total_reviews=len(reviews),
            approved_reviews=approved,
            changes_requested=changes_requested,
            commented_reviews=commented,
            average_review_time_hours=round(avg_time, 2) if avg_time else None,
            repositories_reviewed=repositories,
            review_timeline=sorted(timeline, key=lambda x: x["date"]),
            review_types_distribution=dict(review_types)
        )
    
    def calculate_organization_statistics(
        self,
        contributions: List[UserContribution],
        reviews: List[Dict[str, Any]],
        top_n: int = 10
    ) -> StatsResponse:
        """Calculate organization-wide statistics"""
        summary = self.generate_summary(contributions, reviews)
        
        # Get top contributors
        top_contributors = []
        total_reviews = sum(c.total_reviews for c in contributions)
        
        for contrib in contributions[:top_n]:
            percentage = (contrib.total_reviews / total_reviews * 100) if total_reviews > 0 else 0
            top_contributors.append(TopContributor(
                username=contrib.username,
                total_reviews=contrib.total_reviews,
                percentage_of_total=round(percentage, 2)
            ))
        
        # Review activity over time
        activity_by_date = defaultdict(int)
        for review in reviews:
            submitted = review.get("submitted_at")
            if submitted:
                try:
                    date = self._parse_datetime(submitted)
                    if date:
                        date_str = date.date().isoformat()
                        activity_by_date[date_str] += 1
                except Exception:
                    pass
        
        return StatsResponse(
            organization="",  # Will be set by the router
            period_start=None,  # Will be set by the router
            period_end=None,  # Will be set by the router
            total_reviews=len(reviews),
            total_unique_reviewers=len(contributions),
            average_reviews_per_pr=summary.average_reviews_per_pr,
            top_contributors=top_contributors,
            review_activity_over_time=dict(sorted(activity_by_date.items()))
        )
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """Parse datetime string in various formats"""
        if not date_str:
            return None
        
        # Remove timezone info for parsing
        date_str = date_str.replace("Z", "+00:00")
        
        try:
            # Try ISO format
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                # Try common GitHub date format
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                return None

