# 🧠 Brain System - Centralized Command Center

All brain functionality organized in one place!

## Directory Structure

```
/Users/tarive/brain/
├── core/               # Core brain processing
│   └── brain.py       # Main XML brain processor
├── integrations/       # External integrations
│   ├── gmail/         # Gmail integration
│   │   ├── gmail_token.py    # Token-based access
│   │   └── gmail_oauth.py    # OAuth access
│   ├── reminders/     # Apple Reminders
│   └── mcp/           # MCP servers
├── config/            # Configuration files
│   ├── tokens/        # API tokens
│   │   └── gmail_token.txt   # Gmail access token
│   └── credentials/   # OAuth credentials
├── data/              # Runtime data
│   ├── cache/         # Cached data
│   └── sessions/      # Session data
├── commands/          # Command-line tools
│   └── brain          # Main CLI command
├── docs/              # Documentation
├── templates/         # Templates and examples
├── logs/              # System logs
├── brain.py           # Main entry point
├── setup_gmail.sh     # Gmail setup helper
└── README.md          # This file
```

## Quick Start

### 1. Save Your Gmail Token

Get a token from [OAuth Playground](https://developers.google.com/oauthplayground/):
1. Select "Gmail API v1" → Check `gmail.modify`
2. Authorize and get access token
3. Save it:

```bash
# Method 1: Direct save
echo 'YOUR_TOKEN' > /Users/tarive/brain/config/tokens/gmail_token.txt

# Method 2: Using brain command
brain gmail-token 'YOUR_TOKEN'

# Method 3: Interactive
brain interactive
# Then type: gmail token
```

### 2. Test Gmail Connection

```bash
brain gmail-test
```

### 3. Analyze Job Emails

```bash
brain analyze-jobs
```

## Available Commands

```bash
brain status         # Show system status
brain gmail-token    # Set Gmail token
brain gmail-test     # Test Gmail connection
brain analyze-jobs   # Analyze job emails
brain process        # Process text
brain interactive    # Interactive mode
brain setup-gmail    # Setup instructions
```

## Features

### Gmail Integration
- ✅ OAuth Playground tokens (easiest, no project setup)
- ✅ Job application email analysis
- ✅ Email categorization and tracking
- ✅ Company extraction

### Apple Reminders
- ✅ Natural language processing
- ✅ `<remind>` tag support
- ✅ Time zone handling

### Brain Processing
- ✅ XML tag processing
- ✅ Reminder integration
- ✅ Context management

## Token Management

Tokens are stored in `/Users/tarive/brain/config/tokens/`

- `gmail_token.txt` - Gmail access token

Tokens expire after 1 hour. For permanent access, save the refresh token.

## Interactive Mode

```bash
brain interactive
# or
python3 /Users/tarive/brain/brain.py
```

Commands in interactive mode:
- `status` - System status
- `gmail token` - Set Gmail token
- `gmail test` - Test connection
- `analyze jobs` - Analyze emails
- `process <text>` - Process text
- `quit` - Exit

## Troubleshooting

### Gmail Token Expired
Get a new token from [OAuth Playground](https://developers.google.com/oauthplayground/)

### Command Not Found
Add to PATH:
```bash
echo 'export PATH="/Users/tarive/brain/commands:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Missing Files
The system will create directories as needed. Run:
```bash
brain status
```

## Development

Main entry points:
- `/Users/tarive/brain/brain.py` - Central command center
- `/Users/tarive/brain/core/brain.py` - Core processor
- `/Users/tarive/brain/integrations/gmail/gmail_token.py` - Gmail integration

## Next Steps

1. Set up Gmail token
2. Test the connection
3. Analyze your job emails
4. Explore other features

---
*Brain System v1.0 - All your brain files in one place!*