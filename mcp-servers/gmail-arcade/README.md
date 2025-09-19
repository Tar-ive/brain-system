# Gmail-Arcade MCP Server

A Model Context Protocol (MCP) server that provides Gmail functionality via the Arcade API, designed for integration with the Brain System.

## Overview

This MCP server enables Claude Code to interact with Gmail through the Arcade platform, providing secure and reliable email management capabilities.

## Features

- **Send Emails**: Send emails with subject, body, CC, and BCC recipients
- **List Emails**: Retrieve recent emails from Gmail
- **User Profile**: Get current user's Gmail profile information
- **Search Emails**: Search emails by sender, recipient, subject, or body content
- **Draft Management**: Create and send draft emails
- **Security**: Input validation, content sanitization, and API key protection
- **Error Handling**: Graceful error handling with retry logic

## Installation

1. Install dependencies:
```bash
cd /Users/tarive/brain-mcp-servers/gmail-arcade
pip install -r requirements.txt
```

2. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

The server requires configuration via environment variables in `/Users/tarive/.env.mcp-brain-system`:

```bash
# Required
ARCADE_API_KEY=arc_your_api_key_here

# Optional (defaults shown)
GMAIL_USER_ID=tarive22@gmail.com
GMAIL_RATE_LIMIT_REQUESTS=100
GMAIL_RATE_LIMIT_WINDOW=3600
GMAIL_TIMEOUT_SECONDS=30
GMAIL_MAX_RETRIES=3
GMAIL_RETRY_DELAY=1.0
```

## Brain System Integration

Add to `/Users/tarive/mcp-brain-system.json`:

```json
{
  "gmail-arcade": {
    "command": "python",
    "args": ["-m", "gmail_arcade_mcp.server"],
    "cwd": "/Users/tarive/brain-mcp-servers/gmail-arcade",
    "env": {
      "PYTHONPATH": "/Users/tarive/brain-mcp-servers/gmail-arcade/src"
    }
  }
}
```

## Available Tools

### gmail_send_email
Send an email using Gmail via Arcade API.

**Parameters:**
- `recipient` (string, required): Email address of the recipient
- `subject` (string, required): Subject line of the email
- `body` (string, required): Body content of the email
- `cc` (array, optional): CC recipients
- `bcc` (array, optional): BCC recipients

**Example:**
```json
{
  "recipient": "user@example.com",
  "subject": "Hello from Gmail-Arcade",
  "body": "This is a test email sent via the Gmail-Arcade MCP server."
}
```

### gmail_list_emails
List recent emails from Gmail.

**Parameters:**
- `n_emails` (integer, optional): Number of emails to retrieve (1-50, default: 5)

### gmail_who_am_i
Get current user's Gmail profile information.

**Parameters:** None

### gmail_search_emails
Search emails by various criteria.

**Parameters:**
- `sender` (string, optional): Filter by sender email address
- `recipient` (string, optional): Filter by recipient email address
- `subject` (string, optional): Filter by subject content
- `body` (string, optional): Filter by body content
- `limit` (integer, optional): Maximum number of results (1-100, default: 25)

### gmail_write_draft_email
Create a draft email in Gmail.

**Parameters:**
- `recipient` (string, required): Email address of the recipient
- `subject` (string, required): Subject line of the email
- `body` (string, required): Body content of the email
- `cc` (array, optional): CC recipients
- `bcc` (array, optional): BCC recipients

### gmail_send_draft_email
Send a previously created draft email.

**Parameters:**
- `email_id` (string, required): ID of the draft email to send

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gmail_arcade_mcp

# Run specific test
pytest tests/test_integration.py::TestEmailIntegration::test_send_email_to_target_recipient_end_to_end
```

### Key Test Cases

The primary test case validates sending an email to `pqo14@txstate.edu` with subject `test`:

```python
# Integration test for the required functionality
async def test_send_email_to_target_recipient_end_to_end():
    result = await server._call_tool(
        name="gmail_send_email",
        arguments={
            "recipient": "pqo14@txstate.edu",
            "subject": "test",
            "body": "Integration test email from Gmail-Arcade MCP server"
        }
    )
    assert "success" in result[0].text.lower()
```

## Security Features

- **API Key Protection**: Arcade API keys are masked in logs and error messages
- **Input Validation**: Email addresses and content are validated before processing
- **Content Sanitization**: Email content is sanitized to prevent injection attacks
- **Rate Limiting**: Configurable rate limiting to respect API quotas
- **Error Handling**: Secure error messages that don't leak sensitive information

## Development

### Project Structure

```
src/gmail_arcade_mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server implementation
├── gmail_tools.py       # Gmail tool implementations
├── config.py            # Configuration management
└── utils.py             # Utility functions

tests/
├── test_server.py       # Server functionality tests
├── test_gmail_tools.py  # Gmail tool tests
└── test_integration.py  # End-to-end integration tests
```

### Code Quality

- **Type Hints**: Full type annotations using Python type hints
- **Pydantic Models**: Configuration validation using Pydantic
- **Async/Await**: Proper async programming patterns
- **Error Handling**: Comprehensive error handling with logging
- **Testing**: 100% test coverage following TDD principles

## Troubleshooting

### Common Issues

1. **Authentication Required**: If tools return authentication errors, ensure the Arcade API key is valid and the user has authorized the Gmail tools.

2. **Rate Limiting**: If you encounter rate limit errors, adjust the `GMAIL_RATE_LIMIT_*` configuration values.

3. **Network Timeouts**: Increase `GMAIL_TIMEOUT_SECONDS` for slow network conditions.

### Logs

Logs are written to `/tmp/gmail-arcade-mcp.log` and include:
- Tool execution attempts
- Authentication status
- Error details (with sensitive data masked)
- Performance metrics

### Health Check

The server automatically logs initialization status and tool execution results for monitoring.

## License

This project is part of the Brain System MCP integration suite.

## Contributing

Follow the Brain System development patterns:
1. Test-driven development (TDD)
2. Security-first design
3. Comprehensive error handling
4. Clear documentation
5. Type safety