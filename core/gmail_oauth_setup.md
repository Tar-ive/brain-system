# Gmail OAuth Setup Guide for Brain Integration

## 🚀 Quick Setup Steps (5 minutes)

### Step 1: Create Google Cloud Project

1. **Open Google Cloud Console**: https://console.cloud.google.com/
2. **Create New Project**:
   - Click "Select a project" dropdown (top bar)
   - Click "New Project"
   - Project name: `brain-gmail-integration`
   - Click "Create"
   - Wait for project creation (takes ~30 seconds)

### Step 2: Enable Gmail API

1. **Open API Library**: https://console.cloud.google.com/apis/library
2. **Search for Gmail API**:
   - Type "Gmail API" in search box
   - Click on "Gmail API"
   - Click "ENABLE" button
   - Wait for API to enable

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth consent screen**: https://console.cloud.google.com/apis/credentials/consent
2. **Configure consent screen**:
   - User Type: Select "External"
   - Click "CREATE"
3. **Fill in App Information**:
   - App name: `Brain Gmail Integration`
   - User support email: Your email
   - Developer contact: Your email
   - Click "SAVE AND CONTINUE"
4. **Add Scopes**:
   - Click "ADD OR REMOVE SCOPES"
   - Search for "Gmail"
   - Check: `https://www.googleapis.com/auth/gmail.modify`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"
5. **Add Test Users** (optional):
   - Add your email as test user
   - Click "SAVE AND CONTINUE"

### Step 4: Create OAuth Credentials

1. **Go to Credentials**: https://console.cloud.google.com/apis/credentials
2. **Create credentials**:
   - Click "CREATE CREDENTIALS"
   - Select "OAuth client ID"
3. **Configure OAuth client**:
   - Application type: **Desktop app**
   - Name: `Brain Gmail Client`
   - Click "CREATE"
4. **Download credentials**:
   - Click "DOWNLOAD JSON" button
   - Save as: `/Users/tarive/brain-poc/mcp-gmail/credentials.json`

### Step 5: Test Gmail Setup

Run this command to test authentication:
```bash
cd /Users/tarive/brain-poc/mcp-gmail
uv run python scripts/test_gmail_setup.py
```

This will:
1. Open browser for Google authentication
2. Ask you to allow access
3. Create token.json file
4. Test basic Gmail access

## ✅ Verification Checklist

- [ ] Google Cloud Project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth credentials created
- [ ] credentials.json downloaded to correct location
- [ ] Test script runs successfully

## 🔧 Files Created

After setup, you should have:
- `/Users/tarive/brain-poc/mcp-gmail/credentials.json` - OAuth client configuration
- `/Users/tarive/brain-poc/mcp-gmail/token.json` - Your authentication token (created after first login)

## 📝 Important Notes

- The consent screen will show "unverified app" warning - this is normal for personal use
- Choose "Continue" when you see the warning
- Token expires after 7 days of inactivity but auto-refreshes when used
- Keep credentials.json private - don't commit to git

## 🚨 Troubleshooting

If you get errors:
1. Make sure you selected "Desktop app" not "Web application"
2. Ensure Gmail API is enabled in your project
3. Check that credentials.json is in the correct directory
4. Try deleting token.json and re-authenticating

## Next Steps

Once credentials are set up:
1. Test with: `gmail_analyze "check job application replies"`
2. Configure Claude MCP for Gmail access
3. Use natural language Gmail commands in brain system