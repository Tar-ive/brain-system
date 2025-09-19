"""Gmail-Arcade MCP Server implementation."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ServerCapabilities,
    Tool,
    TextContent,
)

from .config import load_config, GmailArcadeConfig
from .gmail_tools import GmailTools
from .utils import mask_sensitive_data


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/gmail-arcade-mcp.log')
    ]
)
logger = logging.getLogger(__name__)


class GmailArcadeMCPServer:
    """Gmail-Arcade MCP Server."""

    def __init__(self, config: GmailArcadeConfig):
        """Initialize the server with configuration."""
        self.config = config
        self.gmail_tools = GmailTools(config)
        self.server = Server("gmail-arcade-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers."""

        # Define available tools
        self.server.list_tools = self._list_tools
        self.server.call_tool = self._call_tool

    async def initialize(self):
        """Initialize the server and Gmail tools."""
        try:
            await self.gmail_tools.initialize()
            logger.info("Gmail-Arcade MCP Server initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize server: {mask_sensitive_data(str(e))}")
            raise

    async def _list_tools(self) -> List[Tool]:
        """Return list of available tools."""
        return [
            Tool(
                name="gmail_send_email",
                description="Send an email using Gmail via Arcade API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Email address of the recipient"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Subject line of the email"
                        },
                        "body": {
                            "type": "string",
                            "description": "Body content of the email"
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "CC recipients (optional)"
                        },
                        "bcc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "BCC recipients (optional)"
                        }
                    },
                    "required": ["recipient", "subject", "body"]
                }
            ),
            Tool(
                name="gmail_list_emails",
                description="List recent emails from Gmail via Arcade API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "n_emails": {
                            "type": "integer",
                            "description": "Number of emails to retrieve (1-50)",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 5
                        }
                    }
                }
            ),
            Tool(
                name="gmail_who_am_i",
                description="Get current user's Gmail profile information",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="gmail_search_emails",
                description="Search emails by various criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sender": {
                            "type": "string",
                            "description": "Filter by sender email address"
                        },
                        "recipient": {
                            "type": "string",
                            "description": "Filter by recipient email address"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Filter by subject content"
                        },
                        "body": {
                            "type": "string",
                            "description": "Filter by body content"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (1-100)",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 25
                        }
                    }
                }
            ),
            Tool(
                name="gmail_write_draft_email",
                description="Create a draft email in Gmail",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Email address of the recipient"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Subject line of the email"
                        },
                        "body": {
                            "type": "string",
                            "description": "Body content of the email"
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "CC recipients (optional)"
                        },
                        "bcc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "BCC recipients (optional)"
                        }
                    },
                    "required": ["recipient", "subject", "body"]
                }
            ),
            Tool(
                name="gmail_send_draft_email",
                description="Send a previously created draft email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "ID of the draft email to send"
                        }
                    },
                    "required": ["email_id"]
                }
            )
        ]

    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Call a tool with the given arguments."""
        try:
            logger.info(f"Calling tool: {name} with args: {mask_sensitive_data(str(arguments))}")

            # Route to appropriate tool handler
            if name == "gmail_send_email":
                result = await self.gmail_tools.send_email(
                    recipient=arguments["recipient"],
                    subject=arguments["subject"],
                    body=arguments["body"],
                    cc=arguments.get("cc"),
                    bcc=arguments.get("bcc")
                )
            elif name == "gmail_list_emails":
                result = await self.gmail_tools.list_emails(
                    n_emails=arguments.get("n_emails", 5)
                )
            elif name == "gmail_who_am_i":
                result = await self.gmail_tools.who_am_i()
            elif name == "gmail_search_emails":
                result = await self.gmail_tools.search_emails(
                    sender=arguments.get("sender"),
                    recipient=arguments.get("recipient"),
                    subject=arguments.get("subject"),
                    body=arguments.get("body"),
                    limit=arguments.get("limit", 25)
                )
            elif name == "gmail_write_draft_email":
                result = await self.gmail_tools.write_draft_email(
                    recipient=arguments["recipient"],
                    subject=arguments["subject"],
                    body=arguments["body"],
                    cc=arguments.get("cc"),
                    bcc=arguments.get("bcc")
                )
            elif name == "gmail_send_draft_email":
                result = await self.gmail_tools.send_draft_email(
                    email_id=arguments["email_id"]
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

            # Return result as TextContent
            return [TextContent(type="text", text=str(result))]

        except Exception as e:
            logger.error(f"Tool call failed: {mask_sensitive_data(str(e))}")
            error_result = {
                "success": False,
                "error": str(e),
                "tool": name
            }
            return [TextContent(type="text", text=str(error_result))]


async def run_server():
    """Run the Gmail-Arcade MCP server."""
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")

        # Create and initialize server
        mcp_server = GmailArcadeMCPServer(config)
        await mcp_server.initialize()

        # Run the server using stdio
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="gmail-arcade-mcp",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={},
                    ),
                ),
            )

    except Exception as e:
        logger.error(f"Server failed to start: {mask_sensitive_data(str(e))}")
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error: {mask_sensitive_data(str(e))}")
        sys.exit(1)


if __name__ == "__main__":
    main()