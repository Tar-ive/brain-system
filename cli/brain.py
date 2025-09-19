#!/usr/bin/env python3
"""
Brain System - Centralized Command Center
All brain functionality in one organized place
"""

import os
import sys
from pathlib import Path

# Add brain directories to path
BRAIN_ROOT = Path(__file__).parent
sys.path.insert(0, str(BRAIN_ROOT / "core"))
sys.path.insert(0, str(BRAIN_ROOT / "integrations"))

from core.brain import EnhancedXMLBrain
from integrations.gmail.gmail_hybrid import GmailHybridAnalyzer

class BrainSystem:
    """Centralized brain system with all integrations"""
    
    def __init__(self):
        self.root = BRAIN_ROOT
        self.config_dir = self.root / "config"
        self.data_dir = self.root / "data"
        
        # Initialize core brain
        self.brain = EnhancedXMLBrain()
        
        # Initialize Gmail with hybrid approach
        self.gmail = GmailHybridAnalyzer()
        
        print(f"🧠 Brain System Initialized")
        print(f"   Root: {self.root}")
        print(f"   Config: {self.config_dir}")
        print(f"   Data: {self.data_dir}")
    
    def _load_gmail_token(self):
        """Load Gmail token from config"""
        token_file = self.config_dir / "tokens" / "gmail_token.txt"
        if token_file.exists():
            return token_file.read_text().strip()
        return None
    
    def save_gmail_token(self, token: str):
        """Save Gmail token to config"""
        token_file = self.config_dir / "tokens" / "gmail_token.txt"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(token)
        self.gmail.access_token = token
        self.gmail.headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Gmail token saved to: {token_file}")
        return self.gmail.test_connection()
    
    def process(self, text: str):
        """Process text through brain system"""
        return self.brain.process(text)
    
    def analyze_job_emails(self):
        """Analyze job application emails"""
        analysis = self.gmail.analyze_job_applications()
        print(self.gmail.format_job_analysis(analysis))
        return analysis
    
    def send_email(self, to_email: str, subject: str, body: str):
        """Send an email via Gmail"""
        return self.gmail.send_email(to_email, subject, body)
    
    def status(self):
        """Show brain system status"""
        print("\n🧠 Brain System Status")
        print("=" * 50)
        
        # Check Gmail
        print("\n📧 Gmail Integration:")
        if hasattr(self.gmail, 'access_token') and self.gmail.access_token:
            if self.gmail.test_connection():
                print("   Status: ✅ Connected via OAuth Playground")
            else:
                print("   Status: ❌ Token expired")
        elif hasattr(self.gmail, 'credentials') and self.gmail.credentials:
            print("   Status: ⚠️ Credentials found, needs token")
        else:
            print("   Status: ❌ No credentials configured")
        
        # Check directories
        print("\n📁 Directory Structure:")
        for dir_name in ["core", "config", "integrations", "data"]:
            dir_path = self.root / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*")))
                print(f"   {dir_name}: ✅ ({file_count} files)")
            else:
                print(f"   {dir_name}: ❌ Missing")
        
        # Check reminders
        print("\n⏰ Apple Reminders:")
        print("   Status: ✅ Available via <remind> tags")
        
        return True


# Global instance
brain = BrainSystem()


def main():
    """Interactive brain system"""
    print("\n🧠 Brain System - Interactive Mode")
    print("=" * 50)
    print("\nCommands:")
    print("  status           - Show system status")
    print("  gmail auth       - Authenticate Gmail OAuth")
    print("  gmail test       - Test Gmail connection")
    print("  analyze jobs     - Analyze job emails")
    print("  process <text>   - Process text with brain")
    print("  quit            - Exit")
    print()
    
    while True:
        try:
            cmd = input("brain> ").strip()
            
            if not cmd:
                continue
            
            if cmd == "quit":
                break
            
            elif cmd == "status":
                brain.status()
            
            elif cmd == "gmail auth":
                if hasattr(brain.gmail, 'authenticate'):
                    brain.gmail.authenticate()
                else:
                    print("Gmail OAuth not available")
            
            elif cmd == "gmail test":
                if hasattr(brain.gmail, 'service') and brain.gmail.service:
                    analysis = brain.gmail.analyze_job_applications(days_back=1)
                    print("✅ Gmail connection test successful!")
                else:
                    print("❌ Gmail not connected. Run 'gmail auth' first.")
            
            elif cmd == "analyze jobs":
                brain.analyze_job_emails()
            
            elif cmd.startswith("process "):
                text = cmd[8:]
                result = brain.process(text)
                print(f"Result: {result}")
            
            else:
                print(f"Unknown command: {cmd}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()