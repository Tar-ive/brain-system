#!/bin/bash

# Easy Gmail Setup Functions

# Function to set Gmail token
set_gmail_token() {
    if [ $# -eq 0 ]; then
        echo "Usage: set_gmail_token 'your_access_token'"
        echo ""
        echo "Get token from: https://developers.google.com/oauthplayground/"
        echo "1. Select Gmail API v1"
        echo "2. Check: gmail.modify scope"
        echo "3. Authorize and get access token"
        echo "4. Copy and paste here"
        return 1
    fi
    
    echo "$1" > /Users/tarive/brain-poc/gmail_token.txt
    echo "✅ Token saved!"
    
    # Test it
    python3 /Users/tarive/brain-poc/gmail_token_integration.py << EOF

EOF
}

# Function to analyze job emails
analyze_job_emails() {
    python3 -c "
from gmail_token_integration import analyze_jobs
analyze_jobs()
"
}

# Export functions
export -f set_gmail_token
export -f analyze_job_emails

echo "🎯 Easiest Gmail Setup - No OAuth Project Required!"
echo "==================================================="
echo ""
echo "Step 1: Get Access Token (1 minute)"
echo "------------------------------------"
echo "Open: https://developers.google.com/oauthplayground/"
echo ""
echo "1. In left panel, select 'Gmail API v1'"
echo "2. Check the box: https://www.googleapis.com/auth/gmail.modify"
echo "3. Click 'Authorize APIs' button"
echo "4. Sign in with your Google account"
echo "5. Click 'Exchange authorization code for tokens'"
echo "6. Copy the 'Access token' (starts with ya29...)"
echo ""
echo "Step 2: Set Token"
echo "-----------------"
echo "Run: set_gmail_token 'paste_your_token_here'"
echo ""
echo "Step 3: Use Gmail"
echo "-----------------"
echo "Run: analyze_job_emails"
echo ""
echo "That's it! No project setup, no credentials.json needed!"
echo ""
echo "Note: Token expires after 1 hour. For permanent access,"
echo "save the 'Refresh token' from OAuth Playground."