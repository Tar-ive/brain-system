#!/usr/bin/env python3
"""
Gmail Integration using OAuth Playground Token
Easiest way to get Gmail working without complex OAuth setup
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import base64
import re

class GmailTokenAnalyzer:
    """Gmail analyzer using Bearer token from OAuth Playground"""
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or self.load_token()
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
        self.headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
    
    def load_token(self):
        """Load token from file if exists"""
        try:
            with open("/Users/tarive/brain-poc/gmail_token.txt", "r") as f:
                return f.read().strip()
        except:
            return None
    
    def save_token(self, token: str):
        """Save token to file"""
        with open("/Users/tarive/brain-poc/gmail_token.txt", "w") as f:
            f.write(token)
        self.access_token = token
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def test_connection(self) -> bool:
        """Test if token works"""
        if not self.access_token:
            print("❌ No token found. Please set token first.")
            print("   Get token from: https://developers.google.com/oauthplayground/")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/users/me/profile",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Connected to Gmail!")
                print(f"   Email: {data.get('emailAddress', 'Unknown')}")
                print(f"   Total messages: {data.get('messagesTotal', 0)}")
                return True
            else:
                print(f"❌ Token invalid or expired. Status: {response.status_code}")
                print("   Get new token from: https://developers.google.com/oauthplayground/")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def analyze_job_applications(self, days_back: int = 30) -> Dict:
        """Analyze job application emails"""
        if not self.access_token:
            return self._mock_analysis()
        
        try:
            # Build query
            after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f'after:{after_date} (subject:(application OR interview OR position OR role OR hiring) OR from:(recruiting OR hr OR talent))'
            
            # Search messages
            response = requests.get(
                f"{self.base_url}/users/me/messages",
                headers=self.headers,
                params={"q": query, "maxResults": 50}
            )
            
            if response.status_code != 200:
                print(f"⚠️ Gmail API error: {response.status_code}")
                return self._mock_analysis()
            
            data = response.json()
            messages = data.get('messages', [])
            
            analysis = {
                'total_job_emails': len(messages),
                'replies_received': 0,
                'interviews_scheduled': 0,
                'rejections': 0,
                'pending_responses': 0,
                'time_period': f'last {days_back} days',
                'companies': set(),
                'sample_subjects': []
            }
            
            # Analyze first 10 messages for details
            for msg_data in messages[:10]:
                msg_response = requests.get(
                    f"{self.base_url}/users/me/messages/{msg_data['id']}",
                    headers=self.headers,
                    params={"format": "metadata", "metadataHeaders": "Subject,From"}
                )
                
                if msg_response.status_code == 200:
                    msg = msg_response.json()
                    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
                    subject = headers.get('Subject', '')
                    from_email = headers.get('From', '')
                    
                    analysis['sample_subjects'].append(subject[:80])
                    
                    # Extract company
                    company = self._extract_company(from_email, subject)
                    if company:
                        analysis['companies'].add(company)
                    
                    # Categorize
                    subject_lower = subject.lower()
                    if any(word in subject_lower for word in ['interview', 'schedule', 'call', 'meet']):
                        analysis['interviews_scheduled'] += 1
                    elif any(word in subject_lower for word in ['unfortunately', 'regret', 'not selected']):
                        analysis['rejections'] += 1
                    elif any(word in subject_lower for word in ['received', 'thank you', 'application']):
                        analysis['replies_received'] += 1
            
            analysis['companies'] = list(analysis['companies'])
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing emails: {e}")
            return self._mock_analysis()
    
    def _extract_company(self, from_email: str, subject: str) -> str:
        """Extract company name"""
        # From email domain
        match = re.search(r'@([a-zA-Z0-9-]+)\.', from_email)
        if match:
            company = match.group(1).replace('mail', '').replace('careers', '')
            if len(company) > 2:
                return company.title()
        
        # From subject
        if ' at ' in subject:
            match = re.search(r' at ([A-Z][a-zA-Z]+)', subject)
            if match:
                return match.group(1)
        
        return None
    
    def _mock_analysis(self) -> Dict:
        """Return mock data when no token"""
        return {
            'total_job_emails': 0,
            'replies_received': 0,
            'interviews_scheduled': 0,
            'rejections': 0,
            'pending_responses': 0,
            'time_period': 'last 30 days',
            'companies': [],
            'sample_subjects': [],
            'error': 'No token configured'
        }
    
    def format_analysis(self, analysis: Dict) -> str:
        """Format analysis for display"""
        if analysis.get('error'):
            return f"""📊 Job Application Analysis:

⚠️ Gmail not configured. Please get token from:
   https://developers.google.com/oauthplayground/
   
1. Select Gmail API v1 → gmail.modify scope
2. Authorize and get access token
3. Run: set_gmail_token "your_token_here"
"""
        
        result = f"""📊 Job Application Analysis:

📧 Total job-related emails: {analysis['total_job_emails']}
✅ Replies received: {analysis['replies_received']}
📅 Interviews scheduled: {analysis['interviews_scheduled']}
❌ Rejections: {analysis['rejections']}
⏳ Pending responses: {analysis['pending_responses']}
📈 Time period: {analysis['time_period']}"""
        
        if analysis['companies']:
            result += f"\n\n🏢 Companies: {', '.join(analysis['companies'][:5])}"
        
        if analysis['sample_subjects']:
            result += "\n\n📋 Recent job emails:"
            for i, subject in enumerate(analysis['sample_subjects'][:5], 1):
                result += f"\n   {i}. {subject}"
        
        return result


# Global instance
analyzer = GmailTokenAnalyzer()


def set_gmail_token(token: str):
    """Set Gmail access token"""
    analyzer.save_token(token)
    if analyzer.test_connection():
        print("\n✅ Token saved and verified!")
        return True
    return False


def test_gmail():
    """Test Gmail connection"""
    return analyzer.test_connection()


def analyze_jobs():
    """Analyze job applications"""
    analysis = analyzer.analyze_job_applications()
    print(analyzer.format_analysis(analysis))
    return analysis


if __name__ == "__main__":
    print("🔐 Gmail Token Integration")
    print("==========================")
    print("")
    print("Get your token from: https://developers.google.com/oauthplayground/")
    print("1. Select Gmail API v1")
    print("2. Check: https://www.googleapis.com/auth/gmail.modify")
    print("3. Click 'Authorize APIs' and sign in")
    print("4. Click 'Exchange authorization code for tokens'")
    print("5. Copy the 'Access token'")
    print("")
    
    token = input("Paste your access token (or press Enter to test existing): ").strip()
    
    if token:
        set_gmail_token(token)
    else:
        test_gmail()
    
    if analyzer.access_token:
        print("\n" + "="*50)
        analyze_jobs()