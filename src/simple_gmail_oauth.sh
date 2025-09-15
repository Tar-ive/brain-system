#!/bin/bash

echo "🚀 Simple Gmail OAuth Setup"
echo "=========================="
echo ""
echo "Since gcloud CLI doesn't directly support creating desktop OAuth clients,"
echo "here's the fastest way to get Gmail working:"
echo ""
echo "Option 1: Quick Manual Setup (2 minutes)"
echo "----------------------------------------"
echo "1. Open this URL:"
echo "   https://console.cloud.google.com/apis/credentials/oauthclient;oauth=project;oauthClient=new"
echo ""
echo "2. If prompted, create a new project called 'brain-gmail'"
echo ""
echo "3. Select:"
echo "   - Application type: Desktop app"
echo "   - Name: Brain Gmail Client"
echo ""
echo "4. Click CREATE"
echo ""
echo "5. Click DOWNLOAD JSON"
echo ""
echo "6. Save as: /Users/tarive/brain-poc/mcp-gmail/credentials.json"
echo ""
echo "Option 2: Use Existing Project"
echo "-------------------------------"

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -n "$CURRENT_PROJECT" ]; then
    echo "Your current project: $CURRENT_PROJECT"
    echo ""
    
    # Enable Gmail API
    echo "Enabling Gmail API for $CURRENT_PROJECT..."
    gcloud services enable gmail.googleapis.com --project="$CURRENT_PROJECT" 2>/dev/null
    
    echo ""
    echo "1. Open credentials page for your project:"
    echo "   https://console.cloud.google.com/apis/credentials?project=$CURRENT_PROJECT"
    echo ""
    echo "2. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'"
    echo ""
    echo "3. Select 'Desktop app' and create"
    echo ""
    echo "4. Download JSON and save as:"
    echo "   /Users/tarive/brain-poc/mcp-gmail/credentials.json"
else
    echo "No active project. Use Option 1 above."
fi

echo ""
echo "Option 3: Test with Service Account (Alternative)"
echo "-------------------------------------------------"
echo "If you have issues with OAuth, we can try using a service account:"
echo ""

# Create service account approach
cat > /Users/tarive/brain-poc/create_service_account.sh << 'SCRIPT'
#!/bin/bash
PROJECT=${1:-brain-gmail}
gcloud iam service-accounts create gmail-brain \
    --display-name="Gmail Brain Integration" \
    --project="$PROJECT"

gcloud iam service-accounts keys create \
    /Users/tarive/brain-poc/mcp-gmail/service-account.json \
    --iam-account="gmail-brain@${PROJECT}.iam.gserviceaccount.com"

echo "Service account created. However, note that service accounts"
echo "have limited Gmail access and may not work for personal email."
SCRIPT

chmod +x /Users/tarive/brain-poc/create_service_account.sh

echo "To create a service account (limited functionality):"
echo "   /Users/tarive/brain-poc/create_service_account.sh [project-id]"
echo ""
echo "==============================================="
echo "📝 Recommended: Use Option 1 (Quick Manual Setup)"
echo "   Takes only 2 minutes and works reliably!"
echo "==============================================="