# GitHub PR Review Analyzer

A FastAPI-based tool that provides comprehensive reports and statistics about each user's contribution to an organization's PR reviews. This tool can work with GitHub MCP (Model Context Protocol) or directly with the GitHub REST API.

## Features

- **Organization-wide Reports**: Analyze PR review contributions across all repositories in an organization
- **Repository-specific Reports**: Get detailed reports for individual repositories
- **User Statistics**: View detailed statistics for specific users
- **Time-based Filtering**: Filter reports by date range
- **Comprehensive Analytics**: 
  - Total reviews per user
  - Approval vs. changes requested vs. comments
  - Average review time
  - Repository distribution
  - Review activity over time

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AwaisKamran/github-pr-analyzer.git
cd github-pr-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
GITHUB_TOKEN=your_github_personal_access_token
USE_MCP=false
```

To get a GitHub token:
- Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate a new token with `repo` scope (for private repos) or `public_repo` scope (for public repos only)

## Usage

### Running the Server

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### 1. Organization Report
Get a comprehensive report for all repositories in an organization:
```
GET /api/v1/reports/organization/{org_name}
```

Query Parameters:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `repositories` (optional): Comma-separated list of repository names to filter

Example:
```bash
curl "http://localhost:8000/api/v1/reports/organization/myorg?start_date=2024-01-01&end_date=2024-12-31"
```

#### 2. Repository Report
Get a report for a specific repository:
```
GET /api/v1/reports/repository/{owner}/{repo}
```

Query Parameters:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

Example:
```bash
curl "http://localhost:8000/api/v1/reports/repository/myorg/myrepo?start_date=2024-01-01"
```

#### 3. User Statistics
Get detailed statistics for a specific user:
```
GET /api/v1/stats/user/{username}
```

Query Parameters:
- `org_name` (required): Organization name to filter
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

Example:
```bash
curl "http://localhost:8000/api/v1/stats/user/johndoe?org_name=myorg&start_date=2024-01-01"
```

#### 4. Organization Statistics
Get aggregated statistics for an organization:
```
GET /api/v1/stats/organization/{org_name}
```

Query Parameters:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `top_n` (optional, default: 10): Number of top contributors to return

Example:
```bash
curl "http://localhost:8000/api/v1/stats/organization/myorg?top_n=20"
```

## Using with GitHub MCP

To use this tool with GitHub MCP (Model Context Protocol):

1. Ensure you have a GitHub MCP server configured
2. Set `USE_MCP=true` in your `.env` file
3. The tool will attempt to use MCP tools first, falling back to the GitHub API if MCP is unavailable

Note: The MCP integration requires the MCP server to provide tools for:
- Listing organization repositories
- Listing pull requests
- Listing PR reviews

## Response Format

### Report Response
```json
{
  "organization": "myorg",
  "period_start": "2024-01-01",
  "period_end": "2024-12-31",
  "total_reviews": 150,
  "total_contributors": 10,
  "user_contributions": [
    {
      "username": "johndoe",
      "total_reviews": 45,
      "approved_reviews": 30,
      "changes_requested": 10,
      "commented_reviews": 5,
      "average_review_time_hours": 2.5,
      "repositories_reviewed": ["repo1", "repo2"],
      "review_distribution": {
        "repo1": 30,
        "repo2": 15
      }
    }
  ],
  "summary": {
    "total_prs_reviewed": 50,
    "total_unique_reviewers": 10,
    "average_reviews_per_pr": 3.0,
    "most_active_reviewer": "johndoe",
    "review_approval_rate": 60.0,
    "average_time_to_review_hours": 3.2
  }
}
```

## Project Structure

```
github-pr-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── mcp_client.py           # MCP client for GitHub integration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── reports.py          # Report endpoints
│   │   └── stats.py            # Statistics endpoints
│   └── services/
│       ├── __init__.py
│       ├── github_service.py   # GitHub data fetching
│       └── analytics.py        # Analytics calculations
├── requirements.txt
├── README.md
└── .env                        # Environment variables (create this)
```

## Development

### Running Tests
```bash
# Add tests as needed
pytest
```

### Code Style
The project follows PEP 8 style guidelines. Consider using:
- `black` for code formatting
- `flake8` or `ruff` for linting
- `mypy` for type checking

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

