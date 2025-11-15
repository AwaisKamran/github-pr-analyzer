"""
GitHub MCP service for fetching PR review data
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.mcp_client import MCPClient


class GitHubService:
    """Service for interacting with GitHub via MCP or GitHub API"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
    
    async def close(self):
        """Close MCP client connections"""
        await self.mcp_client.close()
    
    async def get_organization_pr_reviews(
        self,
        org_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        repositories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all PR reviews from repositories in an organization
        
        Args:
            org_name: Name of the GitHub organization
            start_date: Optional start date filter
            end_date: Optional end date filter
            repositories: Optional list of repository names to filter
            
        Returns:
            List of PR review dictionaries
        """
        all_reviews = []
        
        # Get list of repositories in the organization
        repos = await self._get_organization_repositories(org_name)
        
        # Filter repositories if specified
        if repositories:
            repos = [r for r in repos if r.get("name") in repositories]
        
        # Fetch PR reviews from each repository
        for repo in repos:
            repo_name = repo.get("name")
            owner = repo.get("owner", {}).get("login", org_name)
            
            reviews = await self.get_repository_pr_reviews(
                owner=owner,
                repo=repo_name,
                start_date=start_date,
                end_date=end_date
            )
            all_reviews.extend(reviews)
        
        return all_reviews
    
    async def get_repository_pr_reviews(
        self,
        owner: str,
        repo: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all PR reviews from a specific repository
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of PR review dictionaries
        """
        all_reviews = []
        
        # Get all pull requests
        pull_requests = await self._get_pull_requests(owner, repo, start_date, end_date)
        
        # Get reviews for each PR
        for pr in pull_requests:
            pr_number = pr.get("number")
            reviews = await self._get_pr_reviews(owner, repo, pr_number)
            
            # Add repository context to each review
            for review in reviews:
                review["repository"] = f"{owner}/{repo}"
                review["pr_number"] = pr_number
                review["pr_title"] = pr.get("title")
                review["pr_created_at"] = pr.get("created_at")
            
            all_reviews.extend(reviews)
        
        return all_reviews
    
    async def _get_organization_repositories(self, org_name: str) -> List[Dict[str, Any]]:
        """Get list of repositories in an organization using MCP"""
        try:
            # Try to use GitHub MCP tool to list repositories
            result = await self.mcp_client.call_github_tool(
                tool_name="list_repositories",
                arguments={"organization": org_name}
            )
            return result.get("repositories", [])
        except Exception as e:
            # Fallback: try alternative MCP tool names
            try:
                result = await self.mcp_client.call_github_tool(
                    tool_name="get_repos",
                    arguments={"org": org_name}
                )
                return result.get("data", [])
            except Exception:
                # If MCP tools are not available, raise informative error
                raise Exception(
                    f"Could not fetch repositories. Please ensure GitHub MCP is configured. "
                    f"Error: {str(e)}"
                )
    
    async def _get_pull_requests(
        self,
        owner: str,
        repo: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get pull requests for a repository using MCP"""
        try:
            args = {
                "owner": owner,
                "repo": repo,
                "state": "all"  # Get all PRs (open, closed, merged)
            }
            
            # Add date filters if provided
            if start_date:
                args["since"] = start_date.isoformat()
            
            result = await self.mcp_client.call_github_tool(
                tool_name="list_pull_requests",
                arguments=args
            )
            
            prs = result.get("pull_requests", result.get("data", []))
            
            # Filter by end_date if provided
            if end_date:
                prs = [
                    pr for pr in prs
                    if pr.get("created_at") and 
                    datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")) <= end_date
                ]
            
            return prs
        except Exception as e:
            raise Exception(
                f"Could not fetch pull requests for {owner}/{repo}. "
                f"Please ensure GitHub MCP is configured. Error: {str(e)}"
            )
    
    async def _get_pr_reviews(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get reviews for a specific pull request using MCP"""
        try:
            result = await self.mcp_client.call_github_tool(
                tool_name="list_pr_reviews",
                arguments={
                    "owner": owner,
                    "repo": repo,
                    "pull_number": pr_number
                }
            )
            return result.get("reviews", result.get("data", []))
        except Exception as e:
            # If reviews endpoint fails, return empty list (some PRs may not have reviews)
            print(f"Warning: Could not fetch reviews for PR #{pr_number}: {str(e)}")
            return []

