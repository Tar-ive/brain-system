#!/usr/bin/env python3
"""
Comprehensive Email Analyzer for TPU Credits and Job Applications
Uses existing Gmail integration to extract specific information
"""

import sys
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path

# Add brain system to path
BRAIN_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BRAIN_ROOT))
sys.path.insert(0, str(BRAIN_ROOT / "integrations"))

from gmail_hybrid import GmailHybridAnalyzer

class ComprehensiveEmailAnalyzer:
    """Analyzes emails for specific information like TPU credits and job applications"""
    
    def __init__(self):
        self.gmail = GmailHybridAnalyzer()
        
    def search_tpu_credits(self, days_back: int = 180) -> Dict:
        """Search for TPU quota and credit related emails"""
        print("🔍 Searching for TPU credit information...")
        
        if not self.gmail.access_token:
            return {"error": "No Gmail access token available"}
        
        try:
            headers = {"Authorization": f"Bearer {self.gmail.access_token}"}
            
            # Search for TPU, quota, credit related emails
            tpu_queries = [
                'tpu OR "tensor processing unit"',
                'quota OR credit OR billing',
                'google cloud OR gcp',
                '"research credit" OR "academic credit"',
                'colab OR "colaboratory"',
                'expir OR deadline OR "valid until"'
            ]
            
            all_tpu_messages = []
            
            for query in tpu_queries:
                # Calculate date filter
                after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
                full_query = f'after:{after_date} ({query})'
                
                import requests
                response = requests.get(
                    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                    headers=headers,
                    params={'q': full_query, 'maxResults': 20}
                )
                response.raise_for_status()
                
                messages = response.json().get('messages', [])
                all_tpu_messages.extend(messages)
            
            # Remove duplicates
            unique_messages = []
            seen_ids = set()
            for msg in all_tpu_messages:
                if msg['id'] not in seen_ids:
                    unique_messages.append(msg)
                    seen_ids.add(msg['id'])
            
            print(f"Found {len(unique_messages)} potentially relevant emails")
            
            # Analyze messages for TPU credit info
            tpu_findings = {
                'total_messages': len(unique_messages),
                'credit_info': [],
                'expiration_dates': [],
                'quota_info': [],
                'recommendations': []
            }
            
            for msg in unique_messages[:15]:  # Analyze first 15 messages
                msg_response = requests.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}",
                    headers=headers
                )
                msg_response.raise_for_status()
                msg_data = msg_response.json()
                
                # Extract email details
                headers_data = {h['name']: h['value'] for h in msg_data['payload'].get('headers', [])}
                subject = headers_data.get('Subject', '')
                sender = headers_data.get('From', '')
                date = headers_data.get('Date', '')
                body = self.gmail._get_message_body(msg_data)
                
                # Look for credit/quota information
                credit_info = self._extract_tpu_info(subject, body, sender, date)
                if credit_info:
                    tpu_findings['credit_info'].append(credit_info)
                
                # Look for expiration dates
                expiry = self._extract_expiration_dates(subject, body)
                if expiry:
                    tpu_findings['expiration_dates'].extend(expiry)
                
                # Look for quota information
                quota = self._extract_quota_info(subject, body)
                if quota:
                    tpu_findings['quota_info'].append(quota)
            
            # Generate recommendations
            tpu_findings['recommendations'] = self._generate_tpu_recommendations(tpu_findings)
            
            return tpu_findings
            
        except Exception as e:
            print(f"❌ Error searching TPU emails: {e}")
            return {"error": str(e)}
    
    def analyze_job_responses(self, days_back: int = 90) -> Dict:
        """Enhanced job application response analysis"""
        print("📊 Analyzing job application responses...")
        
        if not self.gmail.access_token:
            return {"error": "No Gmail access token available"}
        
        try:
            headers = {"Authorization": f"Bearer {self.gmail.access_token}"}
            
            # More comprehensive job search queries
            job_queries = [
                'application OR applied OR "thank you for applying"',
                'interview OR "phone screen" OR "technical interview"',
                'position OR role OR opportunity OR opening',
                'recruiting OR recruiter OR "talent acquisition"',
                'unfortunately OR "not moving forward" OR declined',
                'offer OR "next steps" OR "move forward"',
                'feedback OR "interview feedback" OR assessment'
            ]
            
            all_job_messages = []
            
            for query in job_queries:
                after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
                full_query = f'after:{after_date} ({query})'
                
                import requests
                response = requests.get(
                    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                    headers=headers,
                    params={'q': full_query, 'maxResults': 25}
                )
                response.raise_for_status()
                
                messages = response.json().get('messages', [])
                all_job_messages.extend(messages)
            
            # Remove duplicates
            unique_messages = []
            seen_ids = set()
            for msg in all_job_messages:
                if msg['id'] not in seen_ids:
                    unique_messages.append(msg)
                    seen_ids.add(msg['id'])
            
            print(f"Found {len(unique_messages)} job-related emails")
            
            # Enhanced analysis
            job_stats = {
                'total_job_emails': len(unique_messages),
                'time_period': f'last {days_back} days',
                'companies': set(),
                'detailed_breakdown': {
                    'applications_sent': 0,
                    'acknowledgments': 0,
                    'interviews_scheduled': 0,
                    'rejections': 0,
                    'offers': 0,
                    'pending': 0,
                    'follow_ups': 0
                },
                'company_responses': {},
                'timeline': [],
                'next_actions': []
            }
            
            for msg in unique_messages[:30]:  # Analyze more messages
                msg_response = requests.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg['id']}",
                    headers=headers
                )
                msg_response.raise_for_status()
                msg_data = msg_response.json()
                
                headers_data = {h['name']: h['value'] for h in msg_data['payload'].get('headers', [])}
                subject = headers_data.get('Subject', '')
                sender = headers_data.get('From', '')
                date = headers_data.get('Date', '')
                body = self.gmail._get_message_body(msg_data)
                
                # Enhanced categorization
                category = self._categorize_job_email(subject, body, sender)
                job_stats['detailed_breakdown'][category] += 1
                
                # Extract company info
                company = self.gmail._extract_company(sender, subject)
                if company:
                    job_stats['companies'].add(company)
                    if company not in job_stats['company_responses']:
                        job_stats['company_responses'][company] = []
                    job_stats['company_responses'][company].append({
                        'type': category,
                        'date': date,
                        'subject': subject[:100]
                    })
                
                # Timeline entry
                job_stats['timeline'].append({
                    'date': date,
                    'company': company or 'Unknown',
                    'type': category,
                    'subject': subject[:80]
                })
            
            # Convert sets to lists for JSON serialization
            job_stats['companies'] = list(job_stats['companies'])
            
            # Sort timeline by date
            try:
                job_stats['timeline'].sort(key=lambda x: self._parse_email_date(x['date']), reverse=True)
            except:
                pass  # Keep original order if date parsing fails
            
            # Generate next actions
            job_stats['next_actions'] = self._generate_job_recommendations(job_stats)
            
            return job_stats
            
        except Exception as e:
            print(f"❌ Error analyzing job emails: {e}")
            return {"error": str(e)}
    
    def _extract_tpu_info(self, subject: str, body: str, sender: str, date: str) -> Optional[Dict]:
        """Extract TPU credit and quota information from email"""
        text = (subject + ' ' + body).lower()
        
        credit_keywords = ['credit', 'quota', 'tpu', 'research grant', 'academic credit']
        if not any(keyword in text for keyword in credit_keywords):
            return None
        
        info = {
            'sender': sender,
            'date': date,
            'subject': subject,
            'type': 'unknown'
        }
        
        # Determine type of TPU info
        if any(word in text for word in ['expir', 'deadline', 'valid until', 'ends on']):
            info['type'] = 'expiration'
        elif any(word in text for word in ['quota', 'limit', 'allocation']):
            info['type'] = 'quota'
        elif any(word in text for word in ['credit', 'grant', 'awarded']):
            info['type'] = 'credit_info'
        
        # Try to extract specific amounts or dates
        amount_match = re.search(r'\$([0-9,]+(?:\.[0-9]{2})?)', body)
        if amount_match:
            info['amount'] = amount_match.group(1)
        
        return info
    
    def _extract_expiration_dates(self, subject: str, body: str) -> List[str]:
        """Extract expiration dates from email content"""
        text = subject + ' ' + body
        
        # Look for various date patterns
        date_patterns = [
            r'expir.*?(\d{1,2}/\d{1,2}/\d{2,4})',
            r'valid until.*?(\d{1,2}/\d{1,2}/\d{2,4})',
            r'deadline.*?(\d{1,2}/\d{1,2}/\d{2,4})',
            r'ends on.*?(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{1,2}/\d{1,2}/\d{2,4}).*?expir',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return dates
    
    def _extract_quota_info(self, subject: str, body: str) -> Optional[Dict]:
        """Extract quota/usage information"""
        text = subject + ' ' + body
        
        quota_patterns = [
            r'quota.*?(\d+)',
            r'limit.*?(\d+)',
            r'usage.*?(\d+)',
            r'remaining.*?(\d+)',
            r'(\d+).*?tpu.*?hours?'
        ]
        
        for pattern in quota_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'value': match.group(1),
                    'context': match.group(0)
                }
        
        return None
    
    def _categorize_job_email(self, subject: str, body: str, sender: str) -> str:
        """Enhanced job email categorization"""
        text = (subject + ' ' + body + ' ' + sender).lower()
        
        # More specific categorization
        if any(phrase in text for phrase in ['offer', 'congratulations', 'pleased to offer', 'job offer']):
            return 'offers'
        elif any(phrase in text for phrase in ['interview', 'call', 'meeting', 'schedule', 'phone screen', 'technical interview', 'onsite']):
            return 'interviews_scheduled'
        elif any(phrase in text for phrase in ['unfortunately', 'not moving forward', 'other candidate', 'declined', 'regret', 'not selected']):
            return 'rejections'
        elif any(phrase in text for phrase in ['thank you for your application', 'received your application', 'reviewing your', 'under consideration']):
            return 'acknowledgments'
        elif any(phrase in text for phrase in ['follow up', 'checking in', 'status update', 'any updates']):
            return 'follow_ups'
        elif any(phrase in text for phrase in ['next steps', 'move forward', 'proceed', 'continue']):
            return 'pending'
        elif any(word in text for word in ['application', 'apply', 'position', 'role', 'opportunity']):
            return 'applications_sent'
        else:
            return 'pending'
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime object"""
        try:
            # Handle various email date formats
            import email.utils
            return datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date_str)))
        except:
            return datetime.now()  # Fallback
    
    def _generate_tpu_recommendations(self, findings: Dict) -> List[str]:
        """Generate recommendations based on TPU findings"""
        recommendations = []
        
        if findings['expiration_dates']:
            recommendations.append("⚠️ Found expiration dates - check if TPU credits need renewal")
        
        if findings['quota_info']:
            recommendations.append("📊 Quota information found - monitor usage to avoid overruns")
        
        if findings['credit_info']:
            recommendations.append("💰 Credit information available - review terms and usage guidelines")
        
        if not findings['credit_info'] and not findings['expiration_dates']:
            recommendations.append("🔍 No specific credit expiration found - consider reaching out to Google Cloud support")
        
        return recommendations
    
    def _generate_job_recommendations(self, stats: Dict) -> List[str]:
        """Generate job search recommendations"""
        recommendations = []
        
        total_apps = stats['detailed_breakdown']['applications_sent']
        responses = stats['detailed_breakdown']['acknowledgments'] + stats['detailed_breakdown']['interviews_scheduled']
        
        if total_apps > 0:
            response_rate = (responses / total_apps) * 100
            recommendations.append(f"📈 Response rate: {response_rate:.1f}% ({responses}/{total_apps})")
        
        if stats['detailed_breakdown']['interviews_scheduled'] > 0:
            recommendations.append(f"🎯 {stats['detailed_breakdown']['interviews_scheduled']} interviews scheduled - prepare and follow up")
        
        if stats['detailed_breakdown']['follow_ups'] > 0:
            recommendations.append(f"📞 {stats['detailed_breakdown']['follow_ups']} follow-ups sent - track responses")
        
        pending_count = stats['detailed_breakdown']['pending'] + stats['detailed_breakdown']['acknowledgments']
        if pending_count > 5:
            recommendations.append(f"⏳ {pending_count} applications pending - consider following up after 1-2 weeks")
        
        if len(stats['companies']) < 5:
            recommendations.append("🎯 Consider expanding target companies - diversify applications")
        
        return recommendations


def main():
    """Run comprehensive email analysis"""
    analyzer = ComprehensiveEmailAnalyzer()
    
    print("🧠 Comprehensive Email Analysis Starting...")
    print("=" * 60)
    
    # Search for TPU credit information
    tpu_info = analyzer.search_tpu_credits()
    
    print("\n🔍 TPU Credit Analysis:")
    print("-" * 30)
    if 'error' in tpu_info:
        print(f"❌ Error: {tpu_info['error']}")
    else:
        print(f"📧 Total messages analyzed: {tpu_info['total_messages']}")
        print(f"💰 Credit info found: {len(tpu_info['credit_info'])}")
        print(f"📅 Expiration dates found: {len(tpu_info['expiration_dates'])}")
        
        if tpu_info['expiration_dates']:
            print("⚠️ Expiration dates found:")
            for date in tpu_info['expiration_dates'][:3]:
                print(f"   • {date}")
        
        for rec in tpu_info['recommendations']:
            print(f"   {rec}")
    
    # Analyze job applications
    job_stats = analyzer.analyze_job_responses()
    
    print("\n📊 Job Application Analysis:")
    print("-" * 30)
    if 'error' in job_stats:
        print(f"❌ Error: {job_stats['error']}")
    else:
        print(f"📧 Total job emails: {job_stats['total_job_emails']}")
        print(f"🏢 Companies: {len(job_stats['companies'])}")
        print(f"📅 Time period: {job_stats['time_period']}")
        
        print("\n📈 Breakdown:")
        breakdown = job_stats['detailed_breakdown']
        for category, count in breakdown.items():
            if count > 0:
                print(f"   {category.replace('_', ' ').title()}: {count}")
        
        print("\n🎯 Next Actions:")
        for action in job_stats['next_actions']:
            print(f"   {action}")
    
    return tpu_info, job_stats


if __name__ == "__main__":
    tpu_results, job_results = main()