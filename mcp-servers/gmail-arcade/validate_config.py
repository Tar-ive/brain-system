#!/usr/bin/env python3
"""Validate the Gmail-Arcade MCP server configuration."""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from gmail_arcade_mcp.config import load_config
from gmail_arcade_mcp.server import GmailArcadeMCPServer


async def validate_configuration():
    """Validate that the server can be initialized with the current configuration."""
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print(f"✓ Configuration loaded successfully")
        print(f"  - User ID: {config.user_id}")
        print(f"  - API Key: {config.arcade_api_key[:10]}...")
        print(f"  - Rate limit: {config.rate_limit_requests} requests per {config.rate_limit_window}s")

        # Create server instance
        print("\nCreating server instance...")
        server = GmailArcadeMCPServer(config)
        print("✓ Server instance created")

        # Initialize server
        print("\nInitializing server...")
        await server.initialize()
        print("✓ Server initialized successfully")

        # Test tool listing
        print("\nListing available tools...")
        tools = await server._list_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        print("\n🎉 Gmail-Arcade MCP server configuration is valid!")
        return True

    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(validate_configuration())
    sys.exit(0 if result else 1)