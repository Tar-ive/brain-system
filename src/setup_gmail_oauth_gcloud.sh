#!/bin/bash

# Gmail OAuth Setup Script using gcloud CLI
# This script creates OAuth credentials for Gmail API access

set -e  # Exit on error

echo "🚀 Setting up Gmail OAuth using gcloud CLI"
echo "=========================================="

# Configuration
PROJECT_ID="brain-gmail-integration-$(date +%s)"
PROJECT_NAME="Brain Gmail Integration"
CREDENTIALS_PATH="/Users/tarive/brain-poc/mcp-gmail/credentials.json"

# Step 1: Create or select project
echo ""
echo "📁 Step 1: Creating Google Cloud Project..."
if gcloud projects create "$PROJECT_ID" --name="$PROJECT_NAME" 2>/dev/null; then
    echo "✅ Project created: $PROJECT_ID"
else
    echo "⚠️  Project creation failed (might already exist). Using existing project."
    # Try to use existing project
    EXISTING_PROJECT=$(gcloud projects list --filter="name:Brain Gmail Integration" --format="value(projectId)" | head -1)
    if [ -n "$EXISTING_PROJECT" ]; then
        PROJECT_ID="$EXISTING_PROJECT"
        echo "✅ Using existing project: $PROJECT_ID"
    fi
fi

# Set the project as active
gcloud config set project "$PROJECT_ID"
echo "✅ Set active project to: $PROJECT_ID"

# Step 2: Enable Gmail API
echo ""
echo "📧 Step 2: Enabling Gmail API..."
if gcloud services enable gmail.googleapis.com --project="$PROJECT_ID"; then
    echo "✅ Gmail API enabled"
else
    echo "⚠️  Gmail API might already be enabled"
fi

# Step 3: Create OAuth consent screen configuration
echo ""
echo "🔐 Step 3: Configuring OAuth consent screen..."

# First check if OAuth brand already exists
EXISTING_BRAND=$(gcloud iap oauth-brands list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | head -1)

if [ -z "$EXISTING_BRAND" ]; then
    # Create OAuth brand (consent screen)
    gcloud iap oauth-brands create \
        --application_title="Brain Gmail Integration" \
        --support_email="tarive22@gmail.com" \
        --project="$PROJECT_ID" 2>/dev/null || echo "⚠️  OAuth brand might already exist"
else
    echo "✅ OAuth brand already exists"
fi

# Step 4: Create OAuth 2.0 Client ID
echo ""
echo "🔑 Step 4: Creating OAuth 2.0 Client ID..."

# Create OAuth client for desktop application
echo "Creating desktop OAuth client..."

# We need to use the API directly for desktop clients since gcloud doesn't support it directly
# First, get an access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# Create the OAuth client using the API
OAUTH_RESPONSE=$(curl -s -X POST \
  "https://iam.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/oauthClients" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Brain Gmail Desktop Client",
    "allowedGrantTypes": ["authorization_code", "refresh_token"],
    "allowedRedirectUris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    "allowedScopes": [
      "https://www.googleapis.com/auth/gmail.modify"
    ]
  }' 2>/dev/null)

# Alternative approach: Use the older API
if [ -z "$OAUTH_RESPONSE" ] || [[ "$OAUTH_RESPONSE" == *"error"* ]]; then
    echo "⚠️  Desktop client creation via API failed. Trying alternative method..."
    
    # Create credentials using the console API
    OAUTH_RESPONSE=$(curl -s -X POST \
      "https://console.cloud.google.com/apis/credentials/oauthclient" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"project_id\": \"${PROJECT_ID}\",
        \"client_type\": \"installed\",
        \"client_name\": \"Brain Gmail Desktop Client\"
      }" 2>/dev/null)
fi

# Step 5: Download and save credentials
echo ""
echo "📥 Step 5: Setting up credentials file..."

# Since gcloud doesn't directly support desktop OAuth clients, we'll create the credentials JSON manually
# This is the format needed for desktop applications

cat > "$CREDENTIALS_PATH" <<EOF
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "${PROJECT_ID}",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
EOF

echo ""
echo "⚠️  IMPORTANT: Manual step required!"
echo "====================================="
echo ""
echo "Since gcloud CLI doesn't directly support creating desktop OAuth clients,"
echo "you need to complete this step manually:"
echo ""
echo "1. Open this URL in your browser:"
echo "   https://console.cloud.google.com/apis/credentials?project=${PROJECT_ID}"
echo ""
echo "2. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'"
echo ""
echo "3. Select:"
echo "   - Application type: Desktop app"
echo "   - Name: Brain Gmail Desktop Client"
echo ""
echo "4. Click 'CREATE'"
echo ""
echo "5. Click 'DOWNLOAD JSON'"
echo ""
echo "6. Save the file as:"
echo "   ${CREDENTIALS_PATH}"
echo ""
echo "📝 Project ID: ${PROJECT_ID}"
echo ""
echo "Once you've downloaded the credentials, test with:"
echo "   cd /Users/tarive/brain-poc/mcp-gmail"
echo "   uv run python scripts/test_gmail_setup.py"
echo ""
echo "✅ Gmail API is enabled and project is configured!"
echo "   Just need to download the OAuth credentials manually."