"""Utility functions for Gmail-Arcade MCP server."""

import re
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_email_content(content: str) -> str:
    """Sanitize email content to prevent injection attacks."""
    # Remove potential script tags and harmful content
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
    content = re.sub(r'on\w+\s*=', '', content, flags=re.IGNORECASE)
    return content.strip()


def validate_email_parameters(recipient: str, subject: str, body: str,
                             cc: Optional[List[str]] = None,
                             bcc: Optional[List[str]] = None) -> Dict[str, Any]:
    """Validate email parameters and return sanitized version."""
    errors = []

    # Validate recipient
    if not recipient:
        errors.append("Recipient is required")
    elif not validate_email_address(recipient):
        errors.append(f"Invalid recipient email format: {recipient}")

    # Validate subject
    if not subject:
        errors.append("Subject is required")
    elif len(subject) > 998:  # RFC 2822 limit
        errors.append("Subject too long (max 998 characters)")

    # Validate body
    if not body:
        errors.append("Body is required")

    # Validate CC recipients
    if cc:
        for email in cc:
            if not validate_email_address(email):
                errors.append(f"Invalid CC email format: {email}")

    # Validate BCC recipients
    if bcc:
        for email in bcc:
            if not validate_email_address(email):
                errors.append(f"Invalid BCC email format: {email}")

    if errors:
        raise ValueError(f"Email validation failed: {'; '.join(errors)}")

    # Return sanitized parameters
    return {
        'recipient': recipient.strip().lower(),
        'subject': sanitize_email_content(subject),
        'body': sanitize_email_content(body),
        'cc': [email.strip().lower() for email in (cc or [])],
        'bcc': [email.strip().lower() for email in (bcc or [])]
    }


def create_response(success: bool, data: Any = None,
                   error_message: str = None, tool_name: str = None) -> Dict[str, Any]:
    """Create standardized MCP response format."""
    response = {
        'success': success,
        'data': data,
        'metadata': {
            'tool': tool_name,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': str(uuid.uuid4())
        },
        'errors': []
    }

    if error_message:
        response['errors'].append(error_message)

    return response


async def retry_with_backoff(func, max_retries: int = 3,
                           initial_delay: float = 1.0,
                           backoff_factor: float = 2.0):
    """Retry function with exponential backoff."""
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt == max_retries:
                break

            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
            delay *= backoff_factor

    raise last_exception


def mask_sensitive_data(text: str, patterns: List[str] = None) -> str:
    """Mask sensitive data in text for logging."""
    if patterns is None:
        patterns = [
            r'(arc_[a-zA-Z0-9]+)',  # Arcade API keys
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email addresses
            r'(Bearer\s+[a-zA-Z0-9]+)',  # Bearer tokens
        ]

    masked_text = text
    for pattern in patterns:
        masked_text = re.sub(pattern, lambda m: m.group()[:4] + '*' * (len(m.group()) - 4), masked_text)

    return masked_text