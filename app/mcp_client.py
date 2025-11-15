"""
MCP Client for interacting with GitHub MCP tools
Supports both MCP protocol and direct GitHub API calls
"""
from typing import Dict, Any, Optional
import os
import httpx
from app.config import settings


class MCPClient:
    """Client for calling GitHub MCP tools"""
    
    def __init__(self, use_mcp: bool = None):
        """
        Initialize MCP client
        
        Args:
            use_mcp: Whether to use MCP (if available) or GitHub API directly.
                     If None, will try MCP first, then fall back to API.
        """
        self.server_name = "github"  # Default GitHub MCP server name
        self.use_mcp = use_mcp if use_mcp is not None else settings.USE_MCP
        self.github_token = settings.GITHUB_TOKEN
        self.github_api_base = "https://api.github.com"
        
        # Create HTTP client for GitHub API
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        headers["Accept"] = "application/vnd.github.v3+json"
        
        self.http_client = httpx.AsyncClient(
            base_url=self.github_api_base,
            headers=headers,
            timeout=30.0
        )
    
    async def call_github_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a GitHub MCP tool or use GitHub API directly
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Result from the MCP tool or GitHub API
        """
        # Try MCP first if enabled
        if self.use_mcp:
            try:
                return await self._call_mcp_tool(tool_name, arguments)
            except Exception as e:
                # Fall back to GitHub API if MCP fails
                print(f"MCP call failed, falling back to GitHub API: {str(e)}")
        
        # Use GitHub API directly
        return await self._call_github_api(tool_name, arguments)
    
    async def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call GitHub MCP tool (requires MCP server to be available)
        This would be implemented to use the MCP protocol
        """
        # Note: This would need to be implemented to actually call MCP
        # For now, we'll raise an error to indicate MCP is not available
        raise NotImplementedError(
            "MCP integration requires MCP server to be configured. "
            "Set USE_MCP=false to use GitHub API directly."
        )
    
    async def _call_github_api(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call GitHub REST API directly
        Maps MCP tool names to GitHub API endpoints
        """
        if tool_name == "list_repositories" or tool_name == "get_repos":
            org = arguments.get("organization") or arguments.get("org")
            return await self._get_org_repositories(org)
        
        elif tool_name == "list_pull_requests":
            owner = arguments["owner"]
            repo = arguments["repo"]
            state = arguments.get("state", "all")
            since = arguments.get("since")
            return await self._get_pull_requests(owner, repo, state, since)
        
        elif tool_name == "list_pr_reviews":
            owner = arguments["owner"]
            repo = arguments["repo"]
            pull_number = arguments["pull_number"]
            return await self._get_pr_reviews(owner, repo, pull_number)
        
        else:
            raise ValueError(f"Unknown tool name: {tool_name}")
    
    async def _get_org_repositories(self, org: str) -> Dict[str, Any]:
        """Get repositories for an organization"""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            response = await self.http_client.get(
                f"/orgs/{org}/repos",
                params={"page": page, "per_page": per_page, "type": "all"}
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            repos.extend(data)
            
            # Check if there are more pages
            if len(data) < per_page:
                break
            
            page += 1
        
        return {"repositories": repos, "data": repos}
    
    async def _get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        since: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get pull requests for a repository"""
        prs = []
        page = 1
        per_page = 100
        
        params = {"state": state, "page": page, "per_page": per_page, "sort": "created", "direction": "desc"}
        if since:
            params["since"] = since
        
        while True:
            response = await self.http_client.get(
                f"/repos/{owner}/{repo}/pulls",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            prs.extend(data)
            
            if len(data) < per_page:
                break
            
            page += 1
            params["page"] = page
        
        return {"pull_requests": prs, "data": prs}
    
    async def _get_pr_reviews(
        self,
        owner: str,
        repo: str,
        pull_number: int
    ) -> Dict[str, Any]:
        """Get reviews for a pull request"""
        response = await self.http_client.get(
            f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        )
        response.raise_for_status()
        reviews = response.json()
        
        return {"reviews": reviews, "data": reviews}
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

