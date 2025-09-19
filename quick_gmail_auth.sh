#!/bin/bash

# Quick Gmail Authentication using gcloud
# This uses Application Default Credentials (ADC) approach

echo "🚀 Quick Gmail Setup with gcloud"
echo "================================"

# Step 1: Set up application default credentials with Gmail scope
echo ""
echo "📧 Setting up Gmail authentication..."
echo "This will open a browser for authentication."
echo ""

# Create application default credentials with Gmail scope
gcloud auth application-default login \
    --scopes="https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.readonly" \
    --no-launch-browser 2>/dev/null || \
gcloud auth application-default login \
    --scopes="https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.readonly"

echo ""
echo "✅ Authentication complete!"

# Step 2: Create a wrapper credentials file for the mcp-gmail
echo ""
echo "📝 Creating credentials wrapper..."

# Get the ADC path
ADC_PATH="$HOME/.config/gcloud/application_default_credentials.json"

if [ -f "$ADC_PATH" ]; then
    # Create a Python script to use ADC with Gmail
    cat > /Users/tarive/brain-poc/test_gmail_with_adc.py << 'EOF'
#!/usr/bin/env python3
"""
Test Gmail access using Application Default Credentials
"""

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')

from google.auth import default
from googleapiclient.discovery import build

def test_gmail_with_adc():
    """Test Gmail API using ADC"""
    try:
        # Get default credentials with Gmail scope
        credentials, project = default(
            scopes=['https://www.googleapis.com/auth/gmail.modify']
        )
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Test by getting user profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Successfully connected to Gmail!")
        print(f"   Email: {profile.get('emailAddress', 'Unknown')}")
        print(f"   Total messages: {profile.get('messagesTotal', 0)}")
        print(f"   Total threads: {profile.get('threadsTotal', 0)}")
        
        # Search for job-related emails
        print("\n🔍 Searching for job-related emails...")
        query = 'subject:(application OR interview OR position OR role) OR from:(recruiting OR hr)'
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=5
        ).execute()
        
        messages = results.get('messages', [])
        print(f"   Found {len(messages)} job-related emails (showing max 5)")
        
        if messages:
            print("\n📧 Recent job-related emails:")
            for i, msg in enumerate(messages, 1):
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg_data['payload'].get('headers', [])}
                print(f"   {i}. {headers.get('Subject', 'No subject')[:80]}")
        
        print("\n✅ Gmail integration is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you authenticated with: gcloud auth application-default login")
        print("2. Include Gmail scopes when authenticating")
        return False

if __name__ == "__main__":
    test_gmail_with_adc()
EOF

    chmod +x /Users/tarive/brain-poc/test_gmail_with_adc.py
    
    echo "✅ Test script created!"
    echo ""
    echo "📧 Testing Gmail access..."
    python3 /Users/tarive/brain-poc/test_gmail_with_adc.py
    
else
    echo "❌ Application default credentials not found at $ADC_PATH"
    echo "   Please run: gcloud auth application-default login"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. If the test above worked, Gmail integration is ready!"
echo "2. Use commands like:"
echo "   gmail_analyze \"check job application replies\""
echo "   check_job_replies"
echo ""
echo "Note: For the mcp-gmail server, you still need OAuth2 desktop credentials."
echo "But the brain system can now use ADC for Gmail access!"