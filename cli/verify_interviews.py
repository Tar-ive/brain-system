#!/usr/bin/env python3
"""
Verify Interview Claims - Show Actual Email Details
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add brain system to path
BRAIN_ROOT = Path(__file__).parent
sys.path.insert(0, str(BRAIN_ROOT / "integrations"))

from gmail.gmail_hybrid import GmailHybridAnalyzer

def verify_interview_emails():
    """Get actual details of emails categorized as interviews"""
    gmail = GmailHybridAnalyzer()
    
    if not gmail.access_token:
        print("❌ No Gmail access token")
        return
    
    headers = {"Authorization": f"Bearer {gmail.access_token}"}
    
    # Search for interview-related emails in last 90 days
    interview_queries = [
        'interview',
        '"phone screen"',
        '"technical interview"',
        'schedule AND (call OR meeting)',
        '"zoom interview"',
        '"teams meeting"'
    ]
    
    print("🔍 Verifying Interview Email Claims...")
    print("=" * 60)
    
    all_interview_emails = []
    
    for query in interview_queries:
        after_date = (datetime.now() - timedelta(days=90)).strftime('%Y/%m/%d')
        full_query = f'after:{after_date} {query}'
        
        try:
            response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers=headers,
                params={'q': full_query, 'maxResults': 10}
            )
            response.raise_for_status()
            
            messages = response.json().get('messages', [])
            all_interview_emails.extend(messages)
            
        except Exception as e:
            print(f"Error with query '{query}': {e}")
            continue
    
    # Remove duplicates
    unique_emails = []
    seen_ids = set()
    for email in all_interview_emails:
        if email['id'] not in seen_ids:
            unique_emails.append(email)
            seen_ids.add(email['id'])
    
    print(f"Found {len(unique_emails)} unique potential interview emails")
    print()
    
    verified_interviews = []
    spam_or_promotional = []
    unclear_emails = []
    
    for i, email in enumerate(unique_emails[:15], 1):  # Check first 15
        try:
            # Get full email details
            msg_response = requests.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{email['id']}",
                headers=headers
            )
            msg_response.raise_for_status()
            msg_data = msg_response.json()
            
            # Extract details
            headers_data = {h['name']: h['value'] for h in msg_data['payload'].get('headers', [])}
            subject = headers_data.get('Subject', '')
            sender = headers_data.get('From', '')
            date = headers_data.get('Date', '')
            body = gmail._get_message_body(msg_data)
            
            print(f"{i}. 📧 ANALYZING EMAIL:")
            print(f"   Subject: {subject}")
            print(f"   From: {sender}")
            print(f"   Date: {date}")
            print()
            
            # Determine if this is a real interview
            email_analysis = analyze_email_legitimacy(subject, sender, body)
            
            email_details = {
                'subject': subject,
                'sender': sender,
                'date': date,
                'analysis': email_analysis,
                'body_snippet': body[:200] + "..." if len(body) > 200 else body
            }
            
            if email_analysis['is_real_interview']:
                verified_interviews.append(email_details)
                print("   ✅ REAL INTERVIEW EMAIL")
                if email_analysis['company']:
                    print(f"   🏢 Company: {email_analysis['company']}")
                if email_analysis['interview_type']:
                    print(f"   📞 Type: {email_analysis['interview_type']}")
            
            elif email_analysis['is_spam_or_promotional']:
                spam_or_promotional.append(email_details)
                print("   ❌ SPAM/PROMOTIONAL EMAIL")
                print(f"   🚨 Reason: {email_analysis['spam_reason']}")
            
            else:
                unclear_emails.append(email_details)
                print("   ⚠️  UNCLEAR - needs manual review")
            
            print("   📄 Email snippet:", email_details['body_snippet'][:100] + "...")
            print("-" * 60)
            
        except Exception as e:
            print(f"   ❌ Error analyzing email {i}: {e}")
            print("-" * 60)
            continue
    
    # Summary
    print("\n📊 VERIFICATION SUMMARY:")
    print("=" * 60)
    print(f"✅ Real interviews found: {len(verified_interviews)}")
    print(f"❌ Spam/promotional: {len(spam_or_promotional)}")
    print(f"⚠️  Unclear emails: {len(unclear_emails)}")
    
    if verified_interviews:
        print("\n🎯 CONFIRMED INTERVIEW DETAILS:")
        print("-" * 40)
        for i, interview in enumerate(verified_interviews, 1):
            print(f"{i}. {interview['subject']}")
            print(f"   From: {interview['sender']}")
            print(f"   Date: {interview['date']}")
            if interview['analysis']['company']:
                print(f"   Company: {interview['analysis']['company']}")
            print()
    
    if spam_or_promotional:
        print("\n🚨 SPAM/PROMOTIONAL EMAILS FOUND:")
        print("-" * 40)
        for i, spam in enumerate(spam_or_promotional, 1):
            print(f"{i}. {spam['subject']}")
            print(f"   From: {spam['sender']}")
            print(f"   Spam reason: {spam['analysis']['spam_reason']}")
            print()
    
    return {
        'verified_interviews': verified_interviews,
        'spam_promotional': spam_or_promotional,
        'unclear': unclear_emails
    }

def analyze_email_legitimacy(subject: str, sender: str, body: str) -> dict:
    """Analyze if an email is a real interview or spam"""
    
    analysis = {
        'is_real_interview': False,
        'is_spam_or_promotional': False,
        'company': None,
        'interview_type': None,
        'spam_reason': None
    }
    
    text = (subject + ' ' + sender + ' ' + body).lower()
    
    # Spam/promotional indicators
    spam_indicators = [
        'unsubscribe',
        'marketing',
        'newsletter',
        'promotion',
        'discount',
        'free trial',
        'limited time',
        'click here',
        'noreply',
        'no-reply',
        'automated',
        'do not reply'
    ]
    
    # Check for spam
    for indicator in spam_indicators:
        if indicator in text:
            analysis['is_spam_or_promotional'] = True
            analysis['spam_reason'] = f"Contains '{indicator}'"
            return analysis
    
    # Real interview indicators
    real_interview_patterns = [
        'schedule.*interview',
        'interview.*schedule',
        'phone screen',
        'technical interview',
        'onsite interview',
        'zoom.*interview',
        'teams.*meeting',
        'interview.*time',
        'available.*interview',
        'hr.*interview',
        'hiring manager',
        'recruiter.*call',
        'interview.*invitation'
    ]
    
    # Check for real interview patterns
    import re
    for pattern in real_interview_patterns:
        if re.search(pattern, text):
            analysis['is_real_interview'] = True
            break
    
    # Extract company name
    if analysis['is_real_interview']:
        # Try to get company from email domain
        import re
        email_match = re.search(r'@([^.]+)\.', sender)
        if email_match:
            domain = email_match.group(1)
            if domain not in ['gmail', 'yahoo', 'outlook', 'hotmail']:
                analysis['company'] = domain.title()
        
        # Determine interview type
        if 'phone' in text or 'call' in text:
            analysis['interview_type'] = 'Phone Screen'
        elif 'technical' in text:
            analysis['interview_type'] = 'Technical Interview'
        elif 'onsite' in text:
            analysis['interview_type'] = 'Onsite Interview'
        elif 'zoom' in text or 'video' in text:
            analysis['interview_type'] = 'Video Interview'
        else:
            analysis['interview_type'] = 'Interview'
    
    return analysis

if __name__ == "__main__":
    results = verify_interview_emails()