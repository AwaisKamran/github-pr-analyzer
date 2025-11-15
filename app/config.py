"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # GitHub configuration
    GITHUB_TOKEN: Optional[str] = None
    USE_MCP: bool = False  # Set to True if MCP server is available
    
    # API configuration
    API_TITLE: str = "GitHub PR Review Analyzer"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

