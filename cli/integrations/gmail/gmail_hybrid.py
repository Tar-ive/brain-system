#!/usr/bin/env python3
"""
Gmail Hybrid Integration - Uses OAuth Playground with your credentials
Bypasses Google verification requirements
"""

import json
import requests
import base64
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import re

class GmailHybridAnalyzer:
    """Gmail integration using OAuth Playground tokens with credentials"""
    
    def __init__(self, credentials_path: str = None):
        self.brain_root = Path("/Users/tarive/brain")
        self.config_dir = self.brain_root / "config" / "tokens"
        
        # Find credentials file
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            self.credentials_path = self._find_credentials_file()
        
        self.token_path = self.config_dir / "gmail_playground_token.txt"
        
        self.credentials = self._load_credentials()
        self.access_token = self._load_token()
        
        print(f"📧 Gmail Hybrid initialized")
        print(f"   Credentials: {self.credentials_path.name if self.credentials_path.exists() else 'Not found'}")
        print(f"   Token: {'✅ Found' if self.access_token else '❌ Not found'}")
    
    def _find_credentials_file(self) -> Path:
        """Find the credentials JSON file"""
        for file_path in self.config_dir.glob("*.json"):
            if "client_secret" in file_path.name or "credentials" in file_path.name:
                return file_path
        
        # If not found, look for any JSON file with OAuth credentials
        for json_file in self.config_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'installed' in data or 'web' in data or 'client_id' in data:
                        return json_file
            except:
                continue
        
        return self.config_dir / "credentials.json"
    
    def _load_credentials(self) -> Optional[Dict]:
        """Load OAuth credentials from JSON file"""
        if not self.credentials_path.exists():
            return None
        
        try:
            with open(self.credentials_path, 'r') as f:
                creds = json.load(f)
            
            # Handle both formats: {"installed": {...}} or direct {...}
            if "installed" in creds:
                return creds["installed"]
            elif "web" in creds:
                return creds["web"]
            else:
                return creds
        except Exception as e:
            print(f"⚠️ Error loading credentials: {e}")
            return None
    
    def _load_token(self) -> Optional[str]:
        """Load existing access token"""
        if self.token_path.exists():
            try:
                return self.token_path.read_text().strip()
            except Exception as e:
                print(f"⚠️ Error loading token: {e}")
                return None
        return None
    
    def save_token(self, token: str):
        """Save access token from OAuth Playground"""
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.write_text(token)
        self.access_token = token
        print(f"✅ Token saved to: {self.token_path}")
        return self.test_connection()
    
    def get_playground_instructions(self) -> str:
        """Get instructions for OAuth Playground setup"""
        if not self.credentials:
            return """❌ No credentials found. Please save your OAuth credentials JSON file in:
   /Users/tarive/brain/config/tokens/"""
        
        client_id = self.credentials.get('client_id', 'YOUR_CLIENT_ID')
        
        instructions = f"""
🔐 Gmail OAuth Playground Setup
===============================

Since your app isn't verified by Google, use OAuth Playground:

1. Go to: https://developers.google.com/oauthplayground/

2. Click the Settings gear (⚙️) in top right

3. Check "Use your own OAuth credentials"

4. Enter your credentials:
   Client ID: {client_id}
   Client Secret: {self.credentials.get('client_secret', 'YOUR_CLIENT_SECRET')}

5. In the left panel, find "Gmail API v1"

6. Select: https://www.googleapis.com/auth/gmail.modify

7. Click "Authorize APIs" and sign in with your Gmail account

8. Click "Exchange authorization code for tokens"

9. Copy the "Access token" (starts with ya29...)

10. Save it:
    brain gmail-token 'YOUR_ACCESS_TOKEN'

This bypasses the Google verification requirement!
"""
        return instructions
    
    def authenticate(self):
        """Show OAuth Playground authentication instructions"""
        print(self.get_playground_instructions())
        
        token = input("\nPaste your OAuth Playground access token: ").strip()
        if token:
            return self.save_token(token)
        else:
            print("No token provided")
            return False
    
    def test_connection(self) -> bool:
        """Test Gmail API connection"""
        if not self.access_token:
            print("❌ No access token. Run authentication first.")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers=headers
            )
            response.raise_for_status()
            
            profile = response.json()
            print(f"✅ Gmail connection successful!")
            print(f"   Email: {profile.get('emailAddress')}")
            print(f"   Messages: {profile.get('messagesTotal'):,}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail connection failed: {e}")
            if "401" in str(e):
                print("   Token expired. Get new one from OAuth Playground")
            elif "403" in str(e):
                print("   Access denied. Check token permissions")
            return False
    
    def analyze_job_applications(self, days_back: int = 30) -> Dict:
        """Analyze job application emails"""
        if not self.access_token:
            return self._mock_analysis("No access token configured")
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Calculate date filter
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            
            # Search for job-related emails
            query = f'after:{after_date} (subject:(application OR interview OR position OR role OR hiring OR opportunity) OR from:(recruiting OR hr OR talent OR careers OR noreply))'
            
            response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers=headers,
                params={'q': query, 'maxResults': 50}
            )
            response.raise_for_status()
            
            messages = response.json().get('messages', [])
            
            analysis = {
                'total_messages': len(messages),
                'companies': set(),
                'message_types': {'applications': 0, 'interviews': 0, 'rejections': 0, 'replies': 0, 'other': 0},
                'messages': [],
                'time_period': f'last {days_back} days'
            }
            
            for msg in messages[:20]:  # Analyze first 20 messages
                # Get message details
                msg_response = requests.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}",
                    headers=headers
                )
                msg_response.raise_for_status()
                msg_data = msg_response.json()
                
                # Extract headers
                headers_data = {h['name']: h['value'] for h in msg_data['payload'].get('headers', [])}
                subject = headers_data.get('Subject', '')
                sender = headers_data.get('From', '')
                date = headers_data.get('Date', '')
                
                # Get message body for better categorization
                body = self._get_message_body(msg_data)
                
                # Categorize message
                msg_type = self._categorize_message(subject, sender, body)
                analysis['message_types'][msg_type] += 1
                
                # Extract company name
                company = self._extract_company(sender, subject)
                if company:
                    analysis['companies'].add(company)
                
                analysis['messages'].append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'type': msg_type,
                    'company': company
                })
            
            analysis['companies'] = list(analysis['companies'])
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing job emails: {e}")
            return self._mock_analysis(f"Error: {e}")
    
    def _get_message_body(self, msg_data: Dict) -> str:
        """Extract body text from Gmail message"""
        try:
            payload = msg_data['payload']
            body = ''
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif payload['body'].get('data'):
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            
            return body[:1000]  # Limit to first 1000 chars
        except:
            return ''
    
    def _categorize_message(self, subject: str, sender: str, body: str) -> str:
        """Categorize email message type"""
        text = (subject + ' ' + sender + ' ' + body).lower()
        
        # Interview patterns
        if any(word in text for word in ['interview', 'call', 'meeting', 'schedule', 'calendar', 'zoom', 'phone screen']):
            return 'interviews'
        
        # Rejection patterns
        elif any(phrase in text for phrase in ['unfortunately', 'not moving forward', 'other candidate', 'declined', 'regret']):
            return 'rejections'
        
        # Reply patterns (automated acknowledgments)
        elif any(phrase in text for phrase in ['thank you for your', 'received your application', 'reviewing your', 'noreply', 'no-reply']):
            return 'replies'
        
        # Application patterns
        elif any(word in text for word in ['application', 'apply', 'position', 'role', 'opportunity', 'opening']):
            return 'applications'
        
        else:
            return 'other'
    
    def _extract_company(self, sender: str, subject: str) -> Optional[str]:
        """Extract company name from sender or subject"""
        # Extract from sender email domain
        email_match = re.search(r'@([^.]+)\.', sender)
        if email_match:
            domain = email_match.group(1)
            # Skip common email providers
            if domain not in ['gmail', 'yahoo', 'outlook', 'hotmail', 'icloud', 'noreply', 'mail']:
                # Clean up common prefixes
                domain = domain.replace('careers', '').replace('jobs', '').replace('mail', '')
                if len(domain) > 2:
                    return domain.title()
        
        # Extract from sender name
        name_match = re.search(r'^([^<@]+)', sender)
        if name_match:
            name = name_match.group(1).strip()
            # Skip generic recruiting terms
            if not any(word in name.lower() for word in ['recruiting', 'talent', 'hr', 'careers', 'jobs', 'team']):
                # Extract company name from formats like "John at CompanyName"
                at_match = re.search(r'\bat\s+([A-Z][a-zA-Z]+)', name)
                if at_match:
                    return at_match.group(1)
                
                # Use first part if it looks like a company
                words = name.split()
                if words and len(words[0]) > 3 and words[0][0].isupper():
                    return words[0]
        
        return None
    
    def _mock_analysis(self, message: str) -> Dict:
        """Return mock data when Gmail is not available"""
        return {
            'total_messages': 0,
            'companies': [],
            'message_types': {'applications': 0, 'interviews': 0, 'rejections': 0, 'replies': 0, 'other': 0},
            'messages': [],
            'time_period': 'last 30 days',
            'error': message
        }
    
    def format_job_analysis(self, analysis: Dict) -> str:
        """Format job analysis for display"""
        if 'error' in analysis:
            error_msg = analysis['error']
            if 'No access token' in error_msg:
                return f"""📊 Job Application Analysis
{"="*50}

❌ {error_msg}

To set up Gmail:
{self.get_playground_instructions()}"""
            else:
                return f"❌ Analysis failed: {error_msg}"
        
        result = f"""📊 Job Application Analysis
{"="*50}

📧 Total Messages: {analysis['total_messages']}
📅 Time Period: {analysis['time_period']}

📈 Message Breakdown:
   Applications: {analysis['message_types']['applications']}
   Interviews: {analysis['message_types']['interviews']} 
   Replies: {analysis['message_types']['replies']}
   Rejections: {analysis['message_types']['rejections']}
   Other: {analysis['message_types']['other']}"""
        
        if analysis.get('companies'):
            companies_list = ', '.join(analysis['companies'][:8])
            if len(analysis['companies']) > 8:
                companies_list += f" (+{len(analysis['companies']) - 8} more)"
            result += f"\n\n🏢 Companies: {companies_list}"
        
        if analysis['message_types']['interviews'] > 0:
            result += f"\n\n🎯 Next Steps: Prepare for {analysis['message_types']['interviews']} interviews!"
        elif analysis['message_types']['applications'] > 0:
            result += f"\n\n📬 Follow up on {analysis['message_types']['applications']} applications"
        
        return result
    
    def send_email(self, to_email: str, subject: str, body: str, from_name: str = "Saksham's Brain") -> bool:
        """Send an email using Gmail API"""
        if not self.access_token:
            print("❌ No access token. Cannot send email.")
            return False
        
        try:
            import email
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_name
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Convert to raw format
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            headers = {"Authorization": f"Bearer {self.access_token}"}
            data = {"raw": raw_message}
            
            response = requests.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Email sent successfully!")
            print(f"   To: {to_email}")
            print(f"   Subject: {subject}")
            print(f"   Message ID: {result.get('id')}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            if "401" in str(e):
                print("   Token expired. Get new one from OAuth Playground")
            elif "403" in str(e):
                print("   Permission denied. Check token scopes")
            return False


def main():
    """Test Gmail Hybrid integration"""
    gmail = GmailHybridAnalyzer()
    
    if not gmail.access_token:
        print("No token found. Starting authentication...")
        gmail.authenticate()
    else:
        gmail.test_connection()


if __name__ == "__main__":
    main()