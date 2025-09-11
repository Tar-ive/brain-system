#!/usr/bin/env python3
"""
Enhanced XML Brain System with Natural Language Processing
Supports <remind>, intelligent Gmail analysis, and automatic date/time parsing
"""

import re
import json
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
# Use built-in datetime instead of external dependencies
# import dateutil.parser
# import pytz

# Import the existing unified brain system
from unified_xml_brain import UnifiedXMLBrain, BrainEntry

class EnhancedXMLBrain(UnifiedXMLBrain):
    """Enhanced brain system with natural language processing"""
    
    def __init__(self, brain_dir: str = "/Users/tarive/brain-poc"):
        super().__init__(brain_dir)
        # Use timezone offset for CST (-6) and CDT (-5)
        self.cst_offset = timedelta(hours=-6)  # CST timezone offset
        
        # Enhanced XML tag configuration
        self.enhanced_tags = {
            "remind": {
                "description": "Natural language reminders with auto date/time parsing", 
                "examples": ["<remind>wake baby up at 14:45 CST</remind>", "<remind>call mom tomorrow at 2pm</remind>"],
                "auto_parse": True,
                "integrations": ["apple_reminders"]
            },
            "gmail": {
                "description": "Gmail analysis and automation requests",
                "examples": ["<gmail>check how many job application replies I got</gmail>", "<gmail>find emails from founders this week</gmail>"],
                "auto_parse": True,
                "integrations": ["gmail_mcp"]
            }
        }

    def parse_enhanced_xml_input(self, input_text: str) -> BrainEntry:
        """Parse XML input with enhanced natural language processing"""
        # Extract all XML tags with enhanced processing
        xml_pattern = r'<(\w+)>(.*?)</\1>'
        xml_matches = re.findall(xml_pattern, input_text, re.DOTALL)
        
        xml_tags = []
        processed_content = []
        integrations_needed = []
        
        for tag, content in xml_matches:
            xml_tags.append(tag)
            clean_content = content.strip()
            
            # Enhanced processing for specific tags
            if tag == "remind":
                reminder_data = self._parse_reminder_content(clean_content)
                processed_content.append(f"reminder: {reminder_data['task']} at {reminder_data['datetime_str']}")
                integrations_needed.append(("apple_reminders", reminder_data))
                
            elif tag == "gmail":
                gmail_data = self._parse_gmail_request(clean_content)
                processed_content.append(f"gmail: {gmail_data['request_type']} - {clean_content}")
                integrations_needed.append(("gmail_mcp", gmail_data))
                
            else:
                processed_content.append(f"{tag}: {clean_content}")
        
        # Remove XML tags from original text for clean content
        clean_content = re.sub(xml_pattern, '', input_text).strip()
        if processed_content:
            clean_content += "\n\n" + "\n".join(processed_content)
        
        # Create enhanced brain entry
        entry = super().parse_xml_input(input_text)
        
        # Add integration metadata
        if integrations_needed:
            entry.metadata = getattr(entry, 'metadata', {})
            entry.metadata['integrations'] = integrations_needed
            
        return entry

    def _parse_reminder_content(self, content: str) -> Dict:
        """Parse natural language reminder content and extract datetime"""
        # Common time patterns
        time_patterns = [
            r'at (\d{1,2}):(\d{2})\s*(pm|am)\s*(CST|CDT|EST|PST)?',  # at 2:30pm CST or at 14:45 pm CST
            r'at (\d{1,2}):(\d{2})\s*(CST|CDT|EST|PST)?',           # at 14:45 CST
            r'at (\d{1,2})\s*(pm|am)',                               # at 2pm
            r'(\d{1,2}):(\d{2})\s*(pm|am)\s*(CST|CDT|EST|PST)?',    # 2:30pm CST or 14:45 pm CST
            r'(\d{1,2}):(\d{2})\s*(CST|CDT|EST|PST)?',              # 14:45 CST
        ]
        
        # Date patterns
        date_patterns = [
            r'tomorrow',
            r'today',
            r'(\d{1,2})/(\d{1,2})',                        # 12/25
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',
        ]
        
        # Extract time
        time_info = None
        timezone_info = None
        
        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                # Handle different pattern formats
                if pattern == time_patterns[2]:  # at 2pm pattern (hour only)
                    hour = int(groups[0])
                    minute = 0  # Default minute for hour-only patterns
                    timezone_or_ampm = groups[1].upper() if len(groups) > 1 else None
                    timezone_info = None
                else:
                    # Hour:minute patterns
                    hour = int(groups[0])
                    minute = int(groups[1]) if len(groups) > 1 else 0
                    
                    # Look for AM/PM and timezone in the groups
                    timezone_or_ampm = None
                    timezone_info = None
                    
                    for group in groups[2:]:  # Check groups after hour and minute
                        if group and group.upper() in ['PM', 'AM']:
                            timezone_or_ampm = group.upper()
                        elif group and group.upper() in ['CST', 'CDT', 'EST', 'PST']:
                            timezone_info = group.upper()
                
                # Handle AM/PM conversion, be smart about 24-hour format
                if timezone_or_ampm and timezone_or_ampm in ['PM', 'AM']:
                    if hour > 12:  # 24-hour format like 14:45, convert to 12-hour equivalent
                        hour_12 = hour - 12
                        # If they said PM and it's afternoon (13-23), keep as PM
                        # If they said AM and it's afternoon, it's probably a mistake, use PM
                        if timezone_or_ampm == 'PM':
                            hour = hour  # Keep 24-hour format (14:45 PM = 14:45)
                        else:  # AM with 24-hour is confusing, assume they meant the 12-hour equivalent
                            hour = hour_12 if hour_12 > 0 else 12
                    else:  # Standard 12-hour format
                        if timezone_or_ampm == 'PM' and hour < 12:
                            hour += 12
                        elif timezone_or_ampm == 'AM' and hour == 12:
                            hour = 0
                
                time_info = (hour, minute)
                break
        
        # Extract date (default to today)
        target_date = datetime.now().date()
        
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if match.group(0).lower() == 'tomorrow':
                    target_date = target_date + timedelta(days=1)
                elif match.group(0).lower() == 'today':
                    pass  # already set to today
                # Add more date parsing as needed
                break
        
        # Combine date and time
        if time_info:
            target_datetime = datetime.combine(
                target_date, 
                datetime.min.time().replace(hour=time_info[0], minute=time_info[1])
            )
            # Apply CST timezone offset
            target_datetime = target_datetime.replace(tzinfo=timezone(self.cst_offset))
        else:
            # Default to current time if no time specified
            target_datetime = datetime.now(timezone(self.cst_offset))
        
        # Extract the task (remove time/date references)
        task = content
        for pattern in time_patterns + date_patterns:
            task = re.sub(pattern, '', task, flags=re.IGNORECASE)
        
        task = re.sub(r'\s+', ' ', task).strip()  # Clean up whitespace
        
        return {
            'task': task,
            'datetime': target_datetime,
            'datetime_str': target_datetime.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'timezone': str(target_datetime.tzinfo)
        }

    def _parse_gmail_request(self, content: str) -> Dict:
        """Parse Gmail analysis requests"""
        request_type = "general"
        search_terms = []
        
        # Job application patterns
        if re.search(r'job\s+application|application\s+repl|interview|hiring|recruiter', content, re.IGNORECASE):
            request_type = "job_applications"
            search_terms = ["job", "application", "interview", "position", "role", "hiring", "recruiter"]
        
        # Founder/startup patterns  
        elif re.search(r'founder|startup|partnership|collaboration|business|entrepreneur', content, re.IGNORECASE):
            request_type = "founders"
            search_terms = ["founder", "startup", "partnership", "collaboration", "CEO", "entrepreneur"]
        
        # Reply analysis
        if re.search(r'repl|response|got back|heard back', content, re.IGNORECASE):
            request_type += "_replies"
        
        return {
            'request_type': request_type,
            'search_terms': search_terms,
            'original_request': content,
            'action': self._determine_gmail_action(request_type)
        }

    def _determine_gmail_action(self, request_type: str) -> str:
        """Determine the Gmail action needed"""
        if "job_applications" in request_type:
            if "replies" in request_type:
                return "analyze_job_replies"
            return "search_job_emails"
        elif "founders" in request_type:
            return "search_founder_emails"
        return "general_search"

    def store_enhanced_entry(self, entry: BrainEntry, execute_integrations: bool = True) -> int:
        """Store entry and execute integrations"""
        entry_id = self.store_entry(entry, sync_to_legacy=True)
        
        if execute_integrations and hasattr(entry, 'metadata') and 'integrations' in entry.metadata:
            for integration_type, integration_data in entry.metadata['integrations']:
                if integration_type == "apple_reminders":
                    self._execute_reminder_integration(integration_data, entry_id)
                elif integration_type == "gmail_mcp":
                    self._execute_gmail_integration(integration_data, entry_id)
        
        return entry_id

    def _execute_reminder_integration(self, reminder_data: Dict, entry_id: int):
        """Execute Apple Reminders integration using MCP format"""
        try:
            # Format the datetime as expected by Apple Reminders MCP: YYYY-MM-DD HH:mm:ss
            target_datetime = reminder_data['datetime']
            mcp_datetime_format = target_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
            # Use the proper MCP format for AppleScript date - this mimics what the MCP server does
            applescript_date = target_datetime.strftime('%B %d, %Y %I:%M:%S %p')  # December 11, 2025 2:45:00 PM
            
            # Create AppleScript for adding reminder (following MCP server patterns)
            applescript = f'''
            tell application "Reminders"
                set targetList to list "Reminders"
                set newReminder to make new reminder in targetList
                set name of newReminder to "{reminder_data['task']}"
                set due date of newReminder to (date "{applescript_date}")
                set completed of newReminder to false
            end tell
            '''
            
            # Execute AppleScript using osascript
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Reminder set: {reminder_data['task']} at {mcp_datetime_format}")
                # Store success in brain
                self.store_entry(BrainEntry(
                    content=f"Successfully set Apple reminder: {reminder_data['task']} at {mcp_datetime_format}",
                    xml_tags=['b'],
                    dimensions=['personal'],
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    importance=0.6,
                    connections=[str(entry_id)]
                ), sync_to_legacy=False)
            else:
                print(f"⚠️ Reminder setup failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Reminder integration error: {e}")

    def _execute_gmail_integration(self, gmail_data: Dict, entry_id: int):
        """Execute Gmail MCP integration"""
        try:
            action = gmail_data['action']
            
            if action == "analyze_job_replies":
                result = self._analyze_job_application_replies()
            elif action == "search_job_emails":
                result = self._search_job_emails(gmail_data['search_terms'])
            elif action == "search_founder_emails":
                result = self._search_founder_emails(gmail_data['search_terms'])
            else:
                result = self._general_gmail_search(gmail_data['search_terms'])
            
            # Store Gmail analysis results
            self.store_entry(BrainEntry(
                content=f"Gmail analysis: {result}",
                xml_tags=['gmail'],
                dimensions=['work'],
                timestamp=datetime.now(timezone.utc).isoformat(),
                importance=0.8,
                connections=[str(entry_id)]
            ), sync_to_legacy=False)
            
            print(f"📧 Gmail analysis: {result}")
            
        except Exception as e:
            print(f"❌ Gmail integration error: {e}")

    def _analyze_job_application_replies(self) -> str:
        """Analyze inbox for job application replies"""
        try:
            # Try to use actual Gmail integration
            try:
                from gmail_integration import get_gmail_analyzer
                analyzer = get_gmail_analyzer()
                
                if analyzer.service:
                    # Use actual Gmail API
                    analysis = analyzer.analyze_job_applications()
                    return analyzer.format_job_analysis(analysis)
            except ImportError:
                pass
            
            # Fallback to template if Gmail not available
            analysis = {
                'total_job_emails': 0,
                'replies_received': 0,
                'interviews_scheduled': 0,
                'rejections': 0,
                'pending_responses': 0,
                'time_period': 'last 30 days',
                'gmail_configured': False
            }
            
            result = f"""📊 Job Application Analysis:
            
⚠️ Gmail not configured. Please complete OAuth setup:
   1. Go to https://console.cloud.google.com/
   2. Create OAuth credentials  
   3. Save as /Users/tarive/brain-poc/mcp-gmail/credentials.json
   4. Test with: python3 /Users/tarive/brain-poc/mcp-gmail/scripts/test_gmail_setup.py

📧 Total job-related emails: {analysis['total_job_emails']}
✅ Replies received: {analysis['replies_received']}  
📅 Interviews scheduled: {analysis['interviews_scheduled']}
❌ Rejections: {analysis['rejections']}
⏳ Pending responses: {analysis['pending_responses']}
📈 Time period: {analysis['time_period']}"""
            
            return result
            
        except Exception as e:
            return f"Gmail analysis failed: {str(e)}"

    def _search_job_emails(self, search_terms: List[str]) -> str:
        """Search for job-related emails"""
        return f"Searching for job emails with terms: {', '.join(search_terms)}"

    def _search_founder_emails(self, search_terms: List[str]) -> str:
        """Search for founder-related emails"""
        try:
            # Try to use actual Gmail integration
            try:
                from gmail_integration import get_gmail_analyzer
                analyzer = get_gmail_analyzer()
                
                if analyzer.service:
                    # Use actual Gmail API
                    founder_data = analyzer.search_founder_emails()
                    result = f"🤝 Founder Communications Analysis:\n\n"
                    result += f"📧 Total founder emails: {founder_data['total_founder_emails']}\n"
                    result += f"📈 Time period: {founder_data['time_period']}\n\n"
                    
                    if founder_data['founders']:
                        result += "Recent founder contacts:\n"
                        for founder in founder_data['founders'][:5]:
                            result += f"• From: {founder['from'][:60]}\n"
                            result += f"  Subject: {founder['subject'][:80]}\n\n"
                    
                    return result
            except ImportError:
                pass
            
            return f"Searching for founder emails with terms: {', '.join(search_terms)}"
        except Exception as e:
            return f"Founder email search failed: {str(e)}"

    def _general_gmail_search(self, search_terms: List[str]) -> str:
        """General Gmail search"""
        return f"General Gmail search for: {', '.join(search_terms)}"


# Command-line interface
def main():
    import sys
    brain = EnhancedXMLBrain()
    
    if len(sys.argv) < 2:
        print("Usage: enhanced_xml_brain.py [store|search|help] [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "help":
        print("""
🧠 ENHANCED XML BRAIN SYSTEM

## New XML Tags:

### <remind>natural language reminder</remind>
Examples:
  <remind>wake baby up at 14:45 CST</remind>
  <remind>call mom tomorrow at 2pm</remind>
  <remind>dentist appointment next Friday at 10:30am</remind>

### <gmail>analysis request</gmail>  
Examples:
  <gmail>check how many job application replies I got</gmail>
  <gmail>find emails from founders this week</gmail>
  <gmail>analyze my recruiting emails</gmail>

## Usage:
  enhanced_xml_brain.py store "<remind>wake baby up at 14:45 CST</remind>"
  enhanced_xml_brain.py store "<gmail>check job application replies</gmail>"
        """)
        
    elif command == "store" and len(sys.argv) > 2:
        input_text = " ".join(sys.argv[2:])
        entry = brain.parse_enhanced_xml_input(input_text)
        entry_id = brain.store_enhanced_entry(entry)
        print(f"✅ Enhanced entry stored: {entry_id}")
        print(f"   Tags: {entry.xml_tags}")
        print(f"   Dimensions: {entry.dimensions}")
        if hasattr(entry, 'metadata') and 'integrations' in entry.metadata:
            print(f"   Integrations: {[i[0] for i in entry.metadata['integrations']]}")
            
    elif command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = brain.search_unified(query)
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. [{result['importance']:.2f}] {result['content'][:100]}...")
    
    else:
        print("Invalid command. Use 'help' for usage information.")


if __name__ == "__main__":
    main()