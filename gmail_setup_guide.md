# Gmail Integration Setup Guide

## Step 1: Google Cloud Console Setup (5 minutes)

### 1.1 Create Google Cloud Project
1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Project name: `brain-gmail-integration`
4. Click "Create"

### 1.2 Enable Gmail API
1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Gmail API" → "Enable"

### 1.3 Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: "External" (unless you have Google Workspace)
   - App name: "Brain Gmail Integration"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue" through the scopes and test users sections
4. Back to Credentials → "Create Credentials" → "OAuth client ID"
5. Application type: "Desktop application"
6. Name: "Brain Gmail Client"
7. Click "Create"
8. **IMPORTANT**: Download the JSON file (click Download button)
9. Save it as `/Users/tarive/brain-poc/gmail_credentials.json`

## Step 2: Install Gmail MCP Server

### Option A: jeremyjordan/mcp-gmail (Recommended)
```bash
cd /Users/tarive/brain-poc
git clone https://github.com/jeremyjordan/mcp-gmail.git
cd mcp-gmail
pip install -e .
```

### Option B: Using UV (if you prefer)
```bash
uv add mcp-gmail
```

## Step 3: Configure MCP Server in Claude

### 3.1 Add to Claude MCP Configuration
Add this to your `~/.claude.json` file:

```json
{
  "mcpServers": {
    "gmail": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "mcp_gmail"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/Users/tarive/brain-poc/gmail_credentials.json",
        "GMAIL_TOKEN_PATH": "/Users/tarive/brain-poc/gmail_token.json"
      }
    }
  }
}
```

### 3.2 Test Installation
```bash
# Test if the server can start
python -m mcp_gmail --help
```

## Step 4: First Authentication

### 4.1 Initial OAuth Flow
The first time you use the Gmail MCP server, it will:
1. Open your web browser
2. Ask you to sign in to your Google account
3. Request permissions for Gmail access
4. Save authentication token to `gmail_token.json`

## Step 5: Brain System Integration

### 5.1 Add Gmail Commands to Brain System
```bash
# Add these functions to brain_global_commands.sh

# Send email to founder
brain_email_founder() {
    if [ $# -lt 3 ]; then
        echo "Usage: brain_email_founder <email> <subject> <message>"
        echo "Example: brain_email_founder founder@startup.com 'Partnership Inquiry' 'Hi, I would like to discuss...'"
        return 1
    fi
    
    local founder_email="$1"
    local subject="$2"
    local message="$3"
    
    echo "📧 Sending email to $founder_email"
    
    # Store in brain system first
    brain_store "<people>$founder_email</people> emailed about: $subject"
    
    # Note: Actual Gmail sending will be through Claude MCP integration
    echo "Email composed and logged in brain system"
    echo "Subject: $subject"
    echo "To: $founder_email"
    echo "Message: $message"
}

# Search founder emails
brain_search_founder_emails() {
    if [ $# -lt 1 ]; then
        echo "Usage: brain_search_founder_emails <founder_name_or_email>"
        return 1
    fi
    
    local founder="$1"
    echo "🔍 Searching emails for: $founder"
    
    # Search brain system records
    brain_search "$founder" --tag people
}

# List recent founder communications
brain_founder_communications() {
    echo "📊 Recent Founder Communications:"
    brain_search "emailed about" --tag people | head -10
}
```

## Step 6: Testing Gmail Integration

### 6.1 Test Commands
```bash
# Test brain integration
brain_email_founder "test@example.com" "Test Subject" "This is a test message"

# Check if it was stored
brain_search "test@example.com" --tag people
```

### 6.2 Verify MCP Connection
```bash
# Check if Gmail MCP is connected
claude mcp list | grep gmail
```

## Expected Workflow

### Sending Emails
1. Use: `brain_email_founder founder@startup.com "Partnership" "Hello, I'd like to discuss..."`
2. Brain system logs the interaction
3. Claude MCP sends the actual email via Gmail API
4. Confirmation stored in brain system

### Tracking Communications
1. All founder emails automatically tagged with `<people>email</people>`
2. Searchable by founder name or email
3. Integrated with 5-dimensional tracking system
4. Stored in Basic Memory for persistence

## Troubleshooting

### Common Issues
1. **"No module named mcp_gmail"**: Reinstall with `pip install -e .`
2. **Authentication errors**: Delete `gmail_token.json` and re-authenticate
3. **Permission denied**: Check OAuth scopes include Gmail send permission
4. **MCP connection failed**: Verify path in `~/.claude.json`

### Debug Commands
```bash
# Check OAuth token status
ls -la /Users/tarive/brain-poc/gmail_token.json

# Test credentials file
cat /Users/tarive/brain-poc/gmail_credentials.json | jq .

# Verify MCP server
python -m mcp_gmail --version
```

## Security Notes
- Never commit `gmail_credentials.json` or `gmail_token.json` to git
- Store credentials securely
- Use environment variables for production deployments
- Regularly review OAuth permissions in Google Account settings

---

**Next Steps:**
1. Complete Google Cloud setup
2. Download credentials.json file
3. Install MCP server
4. Test integration with Claude
5. Add brain system commands