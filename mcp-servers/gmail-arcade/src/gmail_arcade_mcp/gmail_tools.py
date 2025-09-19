"""Gmail tool implementations using Arcade API."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from arcade_gmail.tools import (
    send_email as arcade_send_email,
    list_emails as arcade_list_emails,
    who_am_i as arcade_who_am_i,
    write_draft_email as arcade_write_draft_email,
    send_draft_email as arcade_send_draft_email
)
from arcade_core.schema import ToolContext
from .config import GmailArcadeConfig
from .utils import validate_email_parameters, create_response, retry_with_backoff, mask_sensitive_data


logger = logging.getLogger(__name__)


class GmailTools:
    """Gmail tools implementation using Arcade Gmail API."""

    def __init__(self, config: GmailArcadeConfig):
        """Initialize Gmail tools with configuration."""
        self.config = config
        self._authenticated = False

    async def initialize(self):
        """Initialize Gmail tools with API key."""
        try:
            # Set the API key in environment for arcade-gmail
            os.environ['ARCADE_API_KEY'] = self.config.arcade_api_key
            self._authenticated = True
            logger.info("Gmail Arcade tools initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gmail tools: {e}")
            raise

    def _create_context(self) -> ToolContext:
        """Create a ToolContext for arcade functions."""
        return ToolContext(
            authorization=None,  # API key is set via environment variable
            secrets=None,
            metadata=None,
            user_id=self.config.user_id
        )

    def _ensure_authenticated(self):
        """Check if Gmail tools are authenticated."""
        if not self._authenticated:
            raise ValueError("Gmail tools not initialized - call initialize() first")
        return True

    async def send_email(self, recipient: str, subject: str, body: str,
                        cc: Optional[List[str]] = None,
                        bcc: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send an email using arcade-gmail send_email function."""
        try:
            self._ensure_authenticated()

            # Validate and sanitize parameters
            params = validate_email_parameters(recipient, subject, body, cc, bcc)

            logger.info(f"Sending email to {mask_sensitive_data(recipient)} with subject: {subject[:50]}...")

            # Call arcade-gmail send_email function directly
            context = self._create_context()
            result = await arcade_send_email(
                context=context,
                recipient=params['recipient'],
                subject=params['subject'],
                body=params['body'],
                cc=params.get('cc'),
                bcc=params.get('bcc')
            )

            return create_response(
                success=True,
                data=result,
                tool_name='gmail_send_email'
            )

        except Exception as e:
            logger.error(f"Failed to send email: {mask_sensitive_data(str(e))}")
            return create_response(
                success=False,
                error_message=str(e),
                tool_name='gmail_send_email'
            )

    async def list_emails(self, n_emails: int = 5) -> Dict[str, Any]:
        """List emails using arcade-gmail list_emails function."""
        try:
            self._ensure_authenticated()

            n_emails = min(max(n_emails, 1), 50)  # Clamp between 1-50
            logger.info(f"Listing {n_emails} emails")

            context = self._create_context()
            result = await arcade_list_emails(context=context, n_emails=n_emails)

            return create_response(
                success=True,
                data=result,
                tool_name='gmail_list_emails'
            )

        except Exception as e:
            logger.error(f"Failed to list emails: {mask_sensitive_data(str(e))}")
            return create_response(
                success=False,
                error_message=str(e),
                tool_name='gmail_list_emails'
            )

    async def who_am_i(self) -> Dict[str, Any]:
        """Get user profile information using arcade-gmail who_am_i function."""
        try:
            self._ensure_authenticated()

            logger.info("Getting user profile information")

            context = self._create_context()
            result = await arcade_who_am_i(context=context)

            return create_response(
                success=True,
                data=result,
                tool_name='gmail_who_am_i'
            )

        except Exception as e:
            logger.error(f"Failed to get user profile: {mask_sensitive_data(str(e))}")
            return create_response(
                success=False,
                error_message=str(e),
                tool_name='gmail_who_am_i'
            )

    async def search_emails(self, sender: Optional[str] = None,
                          recipient: Optional[str] = None,
                          subject: Optional[str] = None,
                          body: Optional[str] = None,
                          limit: int = 25) -> Dict[str, Any]:
        """Search emails - simplified implementation using list_emails."""
        try:
            self._ensure_authenticated()

            # Validate that at least one search parameter is provided
            search_params = [sender, recipient, subject, body]
            if not any(search_params):
                raise ValueError("At least one search parameter must be provided")

            limit = min(max(limit, 1), 100)  # Clamp between 1-100

            logger.info(f"Searching emails with filters (simplified implementation)")

            # For now, use list_emails as a simplified search
            context = self._create_context()
            result = await arcade_list_emails(context=context, n_emails=limit)

            return create_response(
                success=True,
                data={
                    "message": "Search functionality simplified - showing recent emails",
                    "search_filters": {
                        "sender": sender,
                        "recipient": recipient,
                        "subject": subject,
                        "body": body
                    },
                    "emails": result
                },
                tool_name='gmail_search_emails'
            )

        except Exception as e:
            logger.error(f"Failed to search emails: {mask_sensitive_data(str(e))}")
            return create_response(
                success=False,
                error_message=str(e),
                tool_name='gmail_search_emails'
            )

    async def write_draft_email(self, recipient: str, subject: str, body: str,
                              cc: Optional[List[str]] = None,
                              bcc: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a draft email using arcade-gmail write_draft_email function."""
        try:
            self._ensure_authenticated()

            # Validate and sanitize parameters
            params = validate_email_parameters(recipient, subject, body, cc, bcc)

            logger.info(f"Creating draft email to {mask_sensitive_data(recipient)}")

            context = self._create_context()
            result = await arcade_write_draft_email(
                context=context,
                recipient=params['recipient'],
                subject=params['subject'],
                body=params['body'],
                cc=params.get('cc'),
                bcc=params.get('bcc')
            )

            return create_response(
                success=True,
                data=result,
                tool_name='gmail_write_draft_email'
            )

        except Exception as e:
            logger.error(f"Failed to create draft email: {mask_sensitive_data(str(e))}")
            return create_response(
                success=False,
                error_message=str(e),
                tool_name='gmail_write_draft_email'
            )

    async def send_draft_email(self, email_id: str) -> Dict[str, Any]:
        """Send a draft email using arcade-gmail send_draft_email function."""
        try:
            self._ensure_authenticated()

            if not email_id:
                raise ValueError("Email ID is required")

            logger.info(f"Sending draft email with ID: {email_id}")

            context = self._create_context()
            result = await arcade_send_draft_email(context=context, email_id=email_id)

            return create_response(
                success=True,
                data=result,
                tool_name='gmail_send_draft_email'
            )

        except Exception as e:
            logger.error(f"Failed to send draft email: {mask_sensitive_data(str(e))}")
            return create_response(
                success=False,
                error_message=str(e),
                tool_name='gmail_send_draft_email'
            )