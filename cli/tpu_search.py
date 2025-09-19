#!/usr/bin/env python3
"""
Specific TPU Credit Expiration Search
"""

import sys
import os
import requests
import re
from datetime import datetime, timedelta
from pathlib import Path

# Add brain system to path
BRAIN_ROOT = Path(__file__).parent
sys.path.insert(0, str(BRAIN_ROOT / "integrations"))

from gmail.gmail_hybrid import GmailHybridAnalyzer

def search_tpu_expiration():
    """Search specifically for TPU credit expiration information"""
    gmail = GmailHybridAnalyzer()
    
    if not gmail.access_token:
        print("❌ No Gmail access token")
        return
    
    headers = {"Authorization": f"Bearer {gmail.access_token}"}
    
    # Very specific TPU credit expiration searches
    specific_queries = [
        'from:google-cloud-support TPU',
        'from:google.com TPU credit',
        'from:googlecloudplatform.com credit',
        '"research credit" expir',
        '"academic credit" deadline',
        'colab TPU quota',
        '"Cloud Credits" expir',
        '"expires on" TPU'
    ]
    
    print("🔍 Searching for TPU credit expiration...")
    
    all_findings = []
    
    for query in specific_queries:
        print(f"   Searching: {query}")
        
        try:
            response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers=headers,
                params={'q': query, 'maxResults': 10}
            )
            response.raise_for_status()
            
            messages = response.json().get('messages', [])
            print(f"   Found {len(messages)} messages")
            
            for msg in messages:
                # Get full message
                msg_response = requests.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}",
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
                
                # Look for expiration info
                full_text = f"{subject} {body}".lower()
                
                # Date extraction patterns
                date_patterns = [
                    r'expir[es]*.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'valid until.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'deadline.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'end[s]? on.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}.*expir',
                    r'expir.*?(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}'
                ]
                
                found_dates = []
                for pattern in date_patterns:
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    found_dates.extend(matches)
                
                # Credit amount patterns
                credit_patterns = [
                    r'\$([0-9,]+(?:\.[0-9]{2})?)',
                    r'([0-9,]+)\s*credit',
                    r'([0-9,]+)\s*dollar'
                ]
                
                found_credits = []
                for pattern in credit_patterns:
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    found_credits.extend(matches)
                
                if found_dates or found_credits or 'tpu' in full_text or 'quota' in full_text:
                    finding = {
                        'id': msg['id'],
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'found_dates': found_dates,
                        'found_credits': found_credits,
                        'body_snippet': body[:300] + "..." if len(body) > 300 else body
                    }
                    all_findings.append(finding)
                    
        except Exception as e:
            print(f"   Error with query '{query}': {e}")
            continue
    
    # Print findings
    print(f"\n📊 TPU Credit Search Results:")
    print("=" * 50)
    
    if not all_findings:
        print("❌ No specific TPU credit expiration information found")
        print("\n💡 Recommendations:")
        print("   • Check Google Cloud Console directly")
        print("   • Look for emails from google-cloud-support@google.com")
        print("   • Search for 'billing' or 'quota' emails manually")
        return
    
    # Remove duplicates and sort by relevance
    unique_findings = []
    seen_ids = set()
    
    for finding in all_findings:
        if finding['id'] not in seen_ids:
            unique_findings.append(finding)
            seen_ids.add(finding['id'])
    
    print(f"Found {len(unique_findings)} unique relevant emails:")
    print()
    
    for i, finding in enumerate(unique_findings[:5], 1):
        print(f"{i}. 📧 {finding['subject']}")
        print(f"   From: {finding['sender']}")
        print(f"   Date: {finding['date']}")
        
        if finding['found_dates']:
            print(f"   🗓️  Dates found: {', '.join(finding['found_dates'])}")
        
        if finding['found_credits']:
            print(f"   💰 Credits found: {', '.join(finding['found_credits'])}")
        
        # Show relevant snippet
        snippet = finding['body_snippet'].replace('\n', ' ')
        if 'expir' in snippet.lower() or 'deadline' in snippet.lower():
            print(f"   📄 Snippet: {snippet}")
        
        print()
    
    return unique_findings

if __name__ == "__main__":
    findings = search_tpu_expiration()