"""Configuration management for Gmail-Arcade MCP server."""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class GmailArcadeConfig(BaseModel):
    """Configuration for Gmail-Arcade MCP server."""

    arcade_api_key: str = Field(..., description="Arcade API key for authentication")
    user_id: str = Field(default="tarive22@gmail.com", description="Gmail user ID")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=3600, description="Rate limit window in seconds")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Initial retry delay in seconds")

    @validator('arcade_api_key')
    def validate_api_key(cls, v):
        """Validate API key format."""
        if not v or not v.startswith('arc_'):
            raise ValueError("Invalid Arcade API key format")
        return v

    @validator('user_id')
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if not v or '@' not in v:
            raise ValueError("Invalid user ID format")
        return v

    class Config:
        """Pydantic configuration."""
        env_prefix = "GMAIL_ARCADE_"
        case_sensitive = False


def load_config(env_file_path: Optional[str] = None) -> GmailArcadeConfig:
    """Load configuration from environment variables and .env file."""

    # Default env file path
    if env_file_path is None:
        env_file_path = "/Users/tarive/.env.mcp-brain-system"

    # Load environment variables from file
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)

    # Get required values from environment
    arcade_api_key = os.getenv('ARCADE_API_KEY')
    if not arcade_api_key:
        raise ValueError("ARCADE_API_KEY not found in environment")

    # Create configuration
    config_data = {
        'arcade_api_key': arcade_api_key,
        'user_id': os.getenv('GMAIL_USER_ID', 'tarive22@gmail.com'),
        'rate_limit_requests': int(os.getenv('GMAIL_RATE_LIMIT_REQUESTS', '100')),
        'rate_limit_window': int(os.getenv('GMAIL_RATE_LIMIT_WINDOW', '3600')),
        'timeout_seconds': int(os.getenv('GMAIL_TIMEOUT_SECONDS', '30')),
        'max_retries': int(os.getenv('GMAIL_MAX_RETRIES', '3')),
        'retry_delay': float(os.getenv('GMAIL_RETRY_DELAY', '1.0')),
    }

    return GmailArcadeConfig(**config_data)