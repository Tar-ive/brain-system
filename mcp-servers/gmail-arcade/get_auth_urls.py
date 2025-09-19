#!/usr/bin/env python3
"""Get Gmail OAuth2 authorization URLs from Arcade platform."""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from gmail_arcade_mcp.config import load_config

try:
    from arcadepy import Arcade
except ImportError:
    print("❌ Error: 'arcadepy' package not installed.")
    print("Install it with: pip install arcadepy")
    sys.exit(1)


async def get_authorization_urls():
    """Get authorization URLs for Gmail tools without waiting."""
    try:
        print("🔧 Gmail Authorization URLs")
        print("=" * 40)

        # Load configuration
        config = load_config()
        print(f"✓ User: {config.user_id}")

        # Initialize Arcade client
        client = Arcade()
        USER_ID = config.user_id

        # Gmail tools that need authorization
        gmail_tools = [
            "Gmail.SendEmail",
            "Gmail.ListEmails",
            "Gmail.WriteDraftEmail",
            "Gmail.SendDraftEmail"
        ]

        print(f"\n📧 Authorization Required for {len(gmail_tools)} Gmail Tools:")
        print("-" * 60)

        auth_urls = []

        for tool_name in gmail_tools:
            try:
                print(f"\n🔗 {tool_name}")

                # Get authorization URL without waiting
                auth_response = client.tools.authorize(
                    tool_name=tool_name,
                    user_id=USER_ID,
                )

                if auth_response.status == "completed":
                    print(f"   ✅ Already authorized")
                else:
                    print(f"   🌐 Authorization URL:")
                    print(f"   {auth_response.url}")
                    auth_urls.append((tool_name, auth_response.url))

            except Exception as e:
                print(f"   ❌ Error: {e}")

        print(f"\n" + "=" * 60)
        print("📋 NEXT STEPS:")
        print("=" * 60)

        if auth_urls:
            print("1. Open each authorization URL in your browser")
            print("2. Grant Gmail permissions to Arcade")
            print("3. Complete the OAuth2 flow for each tool")
            print()
            print("Authorization URLs:")
            for tool_name, url in auth_urls:
                print(f"   • {tool_name}: {url}")
            print()
            print("4. After authorization, test with:")
            print("   python production_test.py")
        else:
            print("✅ All Gmail tools are already authorized!")
            print("You can now send emails through the MCP server.")

        return len(auth_urls) == 0  # True if all authorized

    except Exception as e:
        print(f"\n❌ Failed to get authorization URLs: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(get_authorization_urls())

    if result:
        print("\n✅ All tools authorized - ready to send emails!")
    else:
        print("\n⏳ Authorization required - follow the URLs above")

    sys.exit(0)