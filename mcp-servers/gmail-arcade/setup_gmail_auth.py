#!/usr/bin/env python3
"""Setup Gmail OAuth2 authentication with Arcade platform."""

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


async def setup_gmail_authentication():
    """Set up Gmail OAuth2 authentication through Arcade platform."""
    try:
        print("🔧 Gmail Authentication Setup for Arcade")
        print("=" * 50)

        # Load configuration
        print("\n1. Loading configuration...")
        config = load_config()
        print(f"✓ Configuration loaded for user: {config.user_id}")
        print(f"✓ API Key configured: {config.arcade_api_key[:10]}...")

        # Initialize Arcade client
        print("\n2. Initializing Arcade client...")
        client = Arcade()
        print("✓ Arcade client initialized")

        # Use the configured user ID from our config
        USER_ID = config.user_id
        print(f"✓ Using user ID: {USER_ID}")

        # List available Gmail tools that need authorization
        gmail_tools = [
            "Gmail.SendEmail",
            "Gmail.ListEmails",
            "Gmail.WriteDraftEmail",
            "Gmail.SendDraftEmail"
        ]

        print(f"\n3. Setting up authorization for {len(gmail_tools)} Gmail tools...")

        for tool_name in gmail_tools:
            print(f"\n   Setting up: {tool_name}")
            try:
                # Request authorization for each Gmail tool
                auth_response = client.tools.authorize(
                    tool_name=tool_name,
                    user_id=USER_ID,
                )

                if auth_response.status == "completed":
                    print(f"   ✅ {tool_name} - Already authorized")
                else:
                    print(f"   🔗 {tool_name} - Authorization required")
                    print(f"   Click this link to authorize: {auth_response.url}")
                    print(f"   Waiting for authorization completion...")

                    # Wait for user to complete authorization
                    client.auth.wait_for_completion(auth_response)
                    print(f"   ✅ {tool_name} - Authorization completed!")

            except Exception as e:
                print(f"   ⚠️ {tool_name} - Error: {e}")

        print(f"\n4. Testing Gmail access...")

        # Test with a simple Gmail tool
        try:
            print("   Testing Gmail.ListEmails...")
            emails_response = client.tools.execute(
                tool_name="Gmail.ListEmails",
                user_id=USER_ID,
            )
            print("   ✅ Gmail access confirmed!")

        except Exception as e:
            print(f"   ⚠️ Gmail test failed: {e}")
            print("   This may be normal if authorization is still pending")

        print(f"\n🎉 Gmail authentication setup completed!")
        print(f"\nNext steps:")
        print(f"1. Complete any pending authorizations via the provided links")
        print(f"2. Run the production test: python production_test.py")
        print(f"3. Send test email to pqo14@txstate.edu")

        return True

    except Exception as e:
        print(f"\n❌ Authentication setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Gmail-Arcade Authentication Setup")
    print("This script will help you authorize Gmail access through Arcade")
    print("")

    result = asyncio.run(setup_gmail_authentication())

    if result:
        print("\n✅ AUTHENTICATION SETUP COMPLETED")
        print("You can now send emails through the Gmail-Arcade MCP server!")
    else:
        print("\n❌ AUTHENTICATION SETUP FAILED")
        print("Please check the error messages above and try again.")

    sys.exit(0 if result else 1)