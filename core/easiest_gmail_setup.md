# Easiest Gmail Setup Options

## ❌ Why API Keys Don't Work
Gmail API requires OAuth because:
- API keys only work for public data (like YouTube videos, Maps)
- Gmail contains private user data
- Google enforces OAuth for all personal data access

## ✅ Option 1: Use Existing OAuth Token (Easiest)
If you have any existing Google OAuth app (from another project), you can reuse those credentials:

```bash
# Copy existing credentials from another project
cp ~/path/to/existing/credentials.json /Users/tarive/brain-poc/mcp-gmail/credentials.json

# Test it
cd /Users/tarive/brain-poc/mcp-gmail
uv run python scripts/test_gmail_setup.py
```

## ✅ Option 2: Gmail API via Personal Access Token (Quick Hack)
Use Google's OAuth 2.0 Playground to generate a token quickly:

1. Go to: https://developers.google.com/oauthplayground/
2. In the left panel, find "Gmail API v1"
3. Select: `https://www.googleapis.com/auth/gmail.modify`
4. Click "Authorize APIs"
5. Sign in with your Google account
6. Click "Exchange authorization code for tokens"
7. Copy the "Access token"

Then use this token directly:

```python
# Save as /Users/tarive/brain-poc/test_with_token.py
import requests

ACCESS_TOKEN = "paste_your_token_here"

# Test Gmail access
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
response = requests.get(
    "https://gmail.googleapis.com/gmail/v1/users/me/profile",
    headers=headers
)
print(response.json())

# Search emails
params = {"q": "subject:job application"}
response = requests.get(
    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
    headers=headers,
    params=params
)
print(f"Found {response.json().get('resultSizeEstimate', 0)} job emails")
```

## ✅ Option 3: Use Google Colab (No Setup Required)
Run Gmail commands in Google Colab which has built-in auth:

```python
# In Google Colab
from google.colab import auth
auth.authenticate_user()

import google.auth
from googleapiclient.discovery import build

creds, _ = google.auth.default()
service = build('gmail', 'v1', credentials=creds)

# Now use Gmail API
profile = service.users().getProfile(userId='me').execute()
print(profile)
```

## ✅ Option 4: Use an Email Client Library (No OAuth)
Use IMAP with app-specific password (less secure but simpler):

```python
import imaplib
import email

# Enable 2FA on your Google account
# Generate app password: https://myaccount.google.com/apppasswords
# Use that password below

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('your_email@gmail.com', 'your_app_password')
mail.select('inbox')

# Search for job emails
status, messages = mail.search(None, 'SUBJECT "job application"')
print(f"Found {len(messages[0].split())} job-related emails")
```

## ✅ Option 5: Use Pre-configured OAuth Service
Services that provide OAuth as a service:

1. **Pipedream**: https://pipedream.com/
   - Sign up free
   - Connect Gmail
   - Get API endpoint to access your Gmail

2. **Zapier/Make/IFTTT**: 
   - Connect Gmail
   - Create webhook triggers
   - Access email data via their APIs

## 🎯 Recommended: OAuth Playground Method
The OAuth Playground (Option 2) is fastest for testing:
1. Takes 1 minute
2. No project setup needed
3. Token lasts 1 hour (enough for testing)
4. Can refresh token programmatically

Would you like me to implement any of these methods?