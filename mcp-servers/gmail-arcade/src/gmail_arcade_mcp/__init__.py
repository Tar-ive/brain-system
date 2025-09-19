"""Gmail-Arcade MCP Server for Brain System Integration."""

__version__ = "1.0.0"
__author__ = "Brain System"
__description__ = "MCP server providing Gmail functionality via Arcade API"

from .server import GmailArcadeMCPServer
from .config import GmailArcadeConfig

__all__ = ["GmailArcadeMCPServer", "GmailArcadeConfig"]