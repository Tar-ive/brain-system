#!/bin/bash

echo "🧠 Brain System - Gmail Setup"
echo "============================"
echo ""
echo "Your Gmail token should be saved here:"
echo "  📁 /Users/tarive/brain/config/tokens/gmail_token.txt"
echo ""
echo "To get a Gmail token:"
echo "------------------------"
echo "1. Go to: https://developers.google.com/oauthplayground/"
echo "2. Select 'Gmail API v1' from the left panel"
echo "3. Check: https://www.googleapis.com/auth/gmail.modify"
echo "4. Click 'Authorize APIs' and sign in"
echo "5. Click 'Exchange authorization code for tokens'"
echo "6. Copy the 'Access token' (starts with ya29...)"
echo ""
echo "Then save it using one of these methods:"
echo ""
echo "Method 1: Direct save"
echo "---------------------"
echo "echo 'YOUR_TOKEN_HERE' > /Users/tarive/brain/config/tokens/gmail_token.txt"
echo ""
echo "Method 2: Interactive"
echo "---------------------"
echo "python3 /Users/tarive/brain/brain.py"
echo "# Then use: gmail token"
echo ""
echo "Method 3: From any directory"
echo "-----------------------------"
echo "export BRAIN_GMAIL_TOKEN='YOUR_TOKEN_HERE'"
echo "python3 -c 'from pathlib import Path; import os; Path(\"/Users/tarive/brain/config/tokens/gmail_token.txt\").write_text(os.environ[\"BRAIN_GMAIL_TOKEN\"])'"
echo ""

# Create token directory if it doesn't exist
mkdir -p /Users/tarive/brain/config/tokens

echo "Token directory ready: /Users/tarive/brain/config/tokens/"
echo ""

# Check if token exists
if [ -f "/Users/tarive/brain/config/tokens/gmail_token.txt" ]; then
    echo "✅ Gmail token already exists!"
    echo "   Testing connection..."
    python3 -c "
import sys
sys.path.insert(0, '/Users/tarive/brain')
from brain import brain
brain.gmail.test_connection()
"
else
    echo "⚠️ No Gmail token found. Please set one up using the instructions above."
fi