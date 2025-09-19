#!/usr/bin/env python3
"""
Gmail Integration for Brain System
Provides actual Gmail API functionality for job application tracking
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("⚠️ Gmail API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

class GmailAnalyzer:
    """Gmail analyzer for brain system integration"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials_path: str = None):
        # Find credentials file in brain system
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            self.credentials_path = self._find_credentials_file()
        
        self.token_path = self.credentials_path.parent / "gmail_token.json"
        self.service = None
        
        if GMAIL_AVAILABLE and self.credentials_path.exists():
            self.authenticate()
    
    def _find_credentials_file(self) -> Path:
        """Find the credentials JSON file in brain config"""
        config_dir = Path("/Users/tarive/brain/config/tokens")
        
        # Look for any JSON file that contains client credentials
        for json_file in config_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'installed' in data or 'web' in data or 'client_id' in data:
                        return json_file
            except:
                continue
        
        # Default fallback
        return config_dir / "credentials.json"
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    print(f"❌ Credentials not found at {self.credentials_path}")
                    print("   Please follow Gmail OAuth setup guide")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def analyze_job_applications(self, days_back: int = 30) -> Dict:
        """Analyze job application emails"""
        if not self.service:
            return self._mock_job_analysis()
        
        try:
            # Calculate date range
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            
            # Search query for job-related emails
            query = f'after:{after_date} (subject:(application OR interview OR position OR role OR hiring OR opportunity OR opening) OR from:(recruiting OR hr OR talent OR careers OR jobs))'
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            
            # Analyze messages
            analysis = {
                'total_job_emails': len(messages),
                'replies_received': 0,
                'interviews_scheduled': 0,
                'rejections': 0,
                'pending_responses': 0,
                'time_period': f'last {days_back} days',
                'companies': set(),
                'next_interviews': []
            }
            
            # Patterns for categorization
            interview_patterns = [
                r'schedule.*interview', r'interview.*scheduled', r'interview.*time',
                r'phone screen', r'technical interview', r'onsite', r'zoom call'
            ]
            rejection_patterns = [
                r'unfortunately', r'not.*moving forward', r'other candidate',
                r'decided not to', r'not.*selected', r'regret to inform'
            ]
            reply_patterns = [
                r'thank you for.*application', r'received your.*application',
                r'reviewing your.*application', r'next steps', r'we.*ll be in touch'
            ]
            
            for msg_id in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_id['id'],
                    format='full'
                ).execute()
                
                # Extract email content
                headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
                subject = headers.get('Subject', '').lower()
                from_email = headers.get('From', '').lower()
                body = self._get_message_body(msg).lower()
                
                # Extract company name
                company = self._extract_company_name(from_email, subject)
                if company:
                    analysis['companies'].add(company)
                
                # Categorize email
                if any(re.search(pattern, body) or re.search(pattern, subject) 
                       for pattern in interview_patterns):
                    analysis['interviews_scheduled'] += 1
                    # Try to extract interview date/time
                    interview_info = self._extract_interview_info(body, subject, headers)
                    if interview_info:
                        analysis['next_interviews'].append(interview_info)
                        
                elif any(re.search(pattern, body) or re.search(pattern, subject) 
                         for pattern in rejection_patterns):
                    analysis['rejections'] += 1
                    
                elif any(re.search(pattern, body) or re.search(pattern, subject) 
                         for pattern in reply_patterns):
                    analysis['replies_received'] += 1
                else:
                    analysis['pending_responses'] += 1
            
            # Convert set to list for JSON serialization
            analysis['companies'] = list(analysis['companies'])
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing emails: {e}")
            return self._mock_job_analysis()
    
    def search_founder_emails(self, days_back: int = 30) -> Dict:
        """Search for founder and startup communications"""
        if not self.service:
            return {'total_founder_emails': 0, 'founders': [], 'time_period': f'last {days_back} days'}
        
        try:
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            
            query = f'after:{after_date} (from:(founder OR ceo OR cofounder OR startup) OR subject:(partnership OR collaboration OR startup OR venture))'
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            
            founder_data = {
                'total_founder_emails': len(messages),
                'founders': [],
                'time_period': f'last {days_back} days'
            }
            
            for msg_id in messages[:10]:  # Analyze top 10
                msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_id['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
                founder_data['founders'].append({
                    'from': headers.get('From', 'Unknown'),
                    'subject': headers.get('Subject', 'No subject'),
                    'date': headers.get('Date', 'Unknown date')
                })
            
            return founder_data
            
        except Exception as e:
            print(f"❌ Error searching founder emails: {e}")
            return {'total_founder_emails': 0, 'founders': [], 'time_period': f'last {days_back} days'}
    
    def _get_message_body(self, msg) -> str:
        """Extract body from Gmail message"""
        try:
            payload = msg['payload']
            body = ''
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body += self._decode_base64(data)
            elif payload['body'].get('data'):
                body = self._decode_base64(payload['body']['data'])
                
            return body[:2000]  # Limit to first 2000 chars
        except:
            return ''
    
    def _decode_base64(self, data) -> str:
        """Decode base64 email data"""
        import base64
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    def _extract_company_name(self, from_email: str, subject: str) -> Optional[str]:
        """Extract company name from email"""
        # Try to extract from domain
        domain_match = re.search(r'@([a-zA-Z0-9-]+)\.(com|io|co|org)', from_email)
        if domain_match:
            company = domain_match.group(1)
            # Clean up common email prefixes
            company = company.replace('mail', '').replace('careers', '').replace('jobs', '')
            if len(company) > 2:
                return company.title()
        
        # Try to extract from subject
        if 'at ' in subject:
            at_match = re.search(r'at ([A-Z][a-zA-Z]+)', subject)
            if at_match:
                return at_match.group(1)
        
        return None
    
    def _extract_interview_info(self, body: str, subject: str, headers: Dict) -> Optional[Dict]:
        """Extract interview date and time if possible"""
        # Look for date patterns
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(monday|tuesday|wednesday|thursday|friday)\s+\d{1,2}',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, body.lower())
            if match:
                return {
                    'company': self._extract_company_name(headers.get('From', ''), subject),
                    'date_mention': match.group(0),
                    'subject': subject[:100]
                }
        
        return None
    
    def _mock_job_analysis(self) -> Dict:
        """Return mock data when Gmail is not available"""
        return {
            'total_job_emails': 0,
            'replies_received': 0,
            'interviews_scheduled': 0,
            'rejections': 0,
            'pending_responses': 0,
            'time_period': 'last 30 days',
            'companies': [],
            'next_interviews': [],
            'gmail_configured': False,
            'message': 'Gmail not configured. Please complete OAuth setup.'
        }
    
    def format_job_analysis(self, analysis: Dict) -> str:
        """Format job analysis for display"""
        if not analysis.get('gmail_configured', True):
            return f"""📊 Job Application Analysis:
            
⚠️ Gmail not configured. Please complete OAuth setup:
   1. Go to https://console.cloud.google.com/
   2. Create OAuth credentials
   3. Save as /Users/tarive/brain-poc/mcp-gmail/credentials.json
   4. Run: gmail_analyze "test"
"""
        
        result = f"""📊 Job Application Analysis:
        
📧 Total job-related emails: {analysis['total_job_emails']}
✅ Replies received: {analysis['replies_received']}  
📅 Interviews scheduled: {analysis['interviews_scheduled']}
❌ Rejections: {analysis['rejections']}
⏳ Pending responses: {analysis['pending_responses']}
📈 Time period: {analysis['time_period']}"""
        
        if analysis.get('companies'):
            result += f"\n\n🏢 Companies: {', '.join(analysis['companies'][:5])}"
            if len(analysis['companies']) > 5:
                result += f" (+{len(analysis['companies']) - 5} more)"
        
        if analysis.get('next_interviews'):
            result += "\n\n📅 Upcoming Interviews:"
            for interview in analysis['next_interviews'][:3]:
                result += f"\n   • {interview.get('company', 'Unknown')} - {interview.get('date_mention', 'TBD')}"
        
        result += "\n\nNext steps: Follow up on pending applications, prepare for scheduled interviews."
        
        return result


# Global instance for easy access
gmail_analyzer = None

def get_gmail_analyzer():
    """Get or create Gmail analyzer instance"""
    global gmail_analyzer
    if gmail_analyzer is None:
        gmail_analyzer = GmailAnalyzer()
    return gmail_analyzer


if __name__ == "__main__":
    # Test the Gmail analyzer
    analyzer = get_gmail_analyzer()
    
    if analyzer.service:
        print("✅ Gmail connected successfully!")
        
        # Test job application analysis
        print("\n📊 Analyzing job applications...")
        job_analysis = analyzer.analyze_job_applications()
        print(analyzer.format_job_analysis(job_analysis))
        
        # Test founder email search
        print("\n🤝 Searching founder emails...")
        founder_data = analyzer.search_founder_emails()
        print(f"Found {founder_data['total_founder_emails']} founder-related emails")
        for founder in founder_data['founders'][:3]:
            print(f"  • {founder['from'][:50]}")
    else:
        print("❌ Gmail not configured. Please set up OAuth credentials first.")
        print(analyzer.format_job_analysis(analyzer._mock_job_analysis()))