#!/usr/bin/env python3
"""
Global Brain Help System
Provides /brain_help command available across all Claude instances
Integrates with unified XML brain system
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

class GlobalBrainHelp:
    def __init__(self):
        self.brain_poc_dir = Path("/Users/tarive/brain-poc")
        self.unified_brain = self.brain_poc_dir / "unified_xml_brain.py"
        self.global_config = Path.home() / ".brain_global_config.json"
        self.setup_global_config()
        
    def setup_global_config(self):
        """Setup global configuration for brain help system"""
        default_config = {
            "version": "1.0.0",
            "xml_tags": {
                "people": {
                    "description": "Person references and relationships",
                    "examples": ["<people>baby</people>", "<people>harshal</people>", "<people>dr_ekren</people>"],
                    "dimensions": ["personal", "work"],
                    "importance_weight": 0.7
                },
                "project": {
                    "description": "Project-related information and updates",
                    "examples": ["<project>ybrowser</project>", "<project>brain-system</project>", "<project>obviusai</project>"],
                    "dimensions": ["work", "startup", "research"],
                    "importance_weight": 0.8
                },
                "b": {
                    "description": "Brain system functionalities, updates, and maintenance",
                    "examples": ["<b>add indexing docs</b>", "<b>fix search bug</b>", "<b>improve sync</b>"],
                    "dimensions": ["work", "research"],
                    "importance_weight": 0.6
                },
                "bfeatures": {
                    "description": "Brain system feature requests and enhancements",
                    "examples": ["<bfeatures>integrate with imessage</bfeatures>", "<bfeatures>add voice notes</bfeatures>", "<bfeatures>mobile access</bfeatures>"],
                    "dimensions": ["work", "research"],
                    "importance_weight": 0.9
                },
                "research": {
                    "description": "Research insights, findings, and academic work",
                    "examples": ["<research>Newton's philosophy of time</research>", "<research>quantum computing applications</research>", "<research>evolutionary computation insights</research>"],
                    "dimensions": ["research", "uni"],
                    "importance_weight": 1.0
                },
                "goals": {
                    "description": "Personal and professional goals and aspirations",
                    "examples": ["<goals>get O1 visa</goals>", "<goals>complete PhD</goals>", "<goals>launch startup</goals>"],
                    "dimensions": ["personal", "work", "uni", "startup"],
                    "importance_weight": 0.95
                },
                "chores": {
                    "description": "Daily tasks, chores, and routine activities",
                    "examples": ["<chores>make baby chutney</chores>", "<chores>grocery shopping</chores>", "<chores>clean workspace</chores>"],
                    "dimensions": ["personal"],
                    "importance_weight": 0.3
                }
            },
            "dimensions": {
                "personal": {
                    "description": "Personal life, relationships, health, family",
                    "color": "🟢",
                    "priority": 1.0,
                    "common_tags": ["people", "goals", "chores"]
                },
                "work": {
                    "description": "Professional work, job applications, career",
                    "color": "🔵", 
                    "priority": 1.1,
                    "common_tags": ["project", "goals", "people"]
                },
                "research": {
                    "description": "Academic research, papers, insights, discoveries",
                    "color": "🟡",
                    "priority": 1.2,
                    "common_tags": ["research", "project", "bfeatures"]
                },
                "uni": {
                    "description": "University activities, courses, deadlines, academics",
                    "color": "🟣",
                    "priority": 1.0,
                    "common_tags": ["research", "goals", "chores"]
                },
                "startup": {
                    "description": "Entrepreneurial activities, business ideas, products",
                    "color": "🔴",
                    "priority": 1.15,
                    "common_tags": ["project", "goals", "bfeatures"]
                }
            },
            "quick_commands": {
                "brain_store": "Store information with XML tags",
                "brain_search": "Search across all dimensions",
                "brain_help": "Show this help system",
                "brain_status": "Show brain system status",
                "brain_dimension": "View entries for specific dimension",
                "brain_export": "Export dimension as XML"
            },
            "integration_systems": [
                "simple_brain (append-only log)",
                "goal_keeper (JSON goal tracking)",
                "working_memory (7-item cognitive limit)",
                "basic_memory (MCP long-term storage)",
                "obsidian_sync (markdown backup)",
                "auto_commit (git version control)"
            ]
        }
        
        if not self.global_config.exists():
            with open(self.global_config, 'w') as f:
                json.dump(default_config, f, indent=2)

    def show_help(self, detailed: bool = False):
        """Show brain help with XML tag hierarchy"""
        with open(self.global_config) as f:
            config = json.load(f)
        
        help_text = self._generate_help_text(config, detailed)
        print(help_text)
        return help_text
        
    def _generate_help_text(self, config: dict, detailed: bool) -> str:
        """Generate comprehensive help text"""
        help_lines = [
            "🧠 UNIFIED BRAIN SYSTEM - Global Help",
            "=" * 50,
            "",
            "## XML TAG HIERARCHY FOR INFORMATION STORAGE",
            ""
        ]
        
        # Core XML tags
        for tag, info in config["xml_tags"].items():
            help_lines.append(f"### <{tag}>content</{tag}>")
            help_lines.append(f"   📝 {info['description']}")
            help_lines.append(f"   🎯 Dimensions: {', '.join(info.get('dimensions', []))}")
            help_lines.append(f"   ⭐ Importance: {info['importance_weight']}")
            help_lines.append("   💡 Examples:")
            for example in info['examples'][:3]:
                help_lines.append(f"      {example}")
            help_lines.append("")
        
        # 5-Dimensional tracking
        help_lines.extend([
            "## 5-DIMENSIONAL TRACKING SYSTEM",
            "All information is automatically categorized across:",
            ""
        ])
        
        for dim, info in config["dimensions"].items():
            help_lines.append(f"{info['color']} **{dim}** - {info['description']}")
            if detailed:
                help_lines.append(f"   Priority: {info['priority']}, Common tags: {', '.join(info['common_tags'])}")
        
        help_lines.extend([
            "",
            "## USAGE EXAMPLES",
            ""
        ])
        
        # Usage examples
        examples = [
            ("Store person info:", "brain_store \"<people>baby</people> loves homemade chutney, especially spicy varieties\""),
            ("Log project work:", "brain_store \"<project>ybrowser</project> integration with <project>bu-nicehack</project> shows promise\""),
            ("Brain system improvement:", "brain_store \"<b>add indexing docs</b> to improve discoverability of brain functions\""),
            ("Feature requests:", "brain_store \"<bfeatures>integrate with imessage and reminders app</bfeatures> for seamless capture\""),
            ("Research insights:", "brain_store \"<research>Newton's philosophy: time is absolute, space is relative container</research>\""),
            ("Set goals:", "brain_store \"<goals>get O1 visa</goals> requires demonstrating extraordinary ability in AI research\""),
            ("Daily chores:", "brain_store \"<chores>make baby chutney</chores> using tomatoes from garden\"")
        ]
        
        for desc, cmd in examples:
            help_lines.append(f"{desc}")
            help_lines.append(f"  {cmd}")
            help_lines.append("")
        
        # Commands section
        help_lines.extend([
            "## AVAILABLE COMMANDS",
            ""
        ])
        
        commands = [
            ("brain_store \"<tag>content</tag>\"", "Store information with XML tags"),
            ("brain_search \"query\"", "Search across all dimensions"),
            ("brain_search \"query\" --dim personal", "Search specific dimension"),
            ("brain_search \"query\" --tag people", "Search by XML tag"),
            ("brain_dimension personal", "View all entries for dimension"),
            ("brain_export research", "Export dimension as XML"),
            ("brain_status", "Show system health and stats"),
            ("brain_help", "Show this help (add --detailed for more)")
        ]
        
        for cmd, desc in commands:
            help_lines.append(f"**{cmd}**")
            help_lines.append(f"   {desc}")
            help_lines.append("")
        
        # Integration info
        help_lines.extend([
            "## INTEGRATED SYSTEMS",
            "This unified system connects:",
            ""
        ])
        
        for system in config["integration_systems"]:
            help_lines.append(f"✅ {system}")
        
        help_lines.extend([
            "",
            "## GLOBAL AVAILABILITY",
            "• Run '/brain_help' or 'brain_help' in any Claude session",
            "• All XML-tagged entries searchable across sessions",
            "• Automatic sync to all connected storage systems",
            "• 5-dimensional categorization happens automatically",
            "",
            f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"🔧 Config: {self.global_config}",
            f"💾 Brain location: {self.brain_poc_dir}"
        ])
        
        return "\n".join(help_lines)

    def brain_store(self, content: str):
        """Store content using unified XML brain system"""
        try:
            if not self.unified_brain.exists():
                return "❌ Unified brain system not found. Run setup first."
            
            result = subprocess.run([
                "python3", str(self.unified_brain), "store", content
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"❌ Storage failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "❌ Storage timed out"
        except Exception as e:
            return f"❌ Error: {e}"

    def brain_search(self, query: str, dimension: str = None, tag: str = None):
        """Search using unified brain system"""
        try:
            cmd = ["python3", str(self.unified_brain), "search", query]
            
            if dimension:
                cmd.extend(["--dim", dimension])
            if tag:
                cmd.extend(["--tag", tag])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"❌ Search failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "❌ Search timed out"
        except Exception as e:
            return f"❌ Error: {e}"

    def brain_status(self):
        """Show brain system status across all components"""
        status_lines = [
            "🧠 BRAIN SYSTEM STATUS",
            "=" * 30,
            ""
        ]
        
        # Check unified brain
        if self.unified_brain.exists():
            status_lines.append("✅ Unified XML Brain: Available")
        else:
            status_lines.append("❌ Unified XML Brain: Missing")
        
        # Check legacy systems
        legacy_systems = [
            ("simple_brain.py", self.brain_poc_dir / "simple_brain.py"),
            ("goal_keeper.py", self.brain_poc_dir / "goal_keeper.py"),
            ("Working Memory", self.brain_poc_dir / "working-memory"),
            ("Basic Memory", None)  # External system
        ]
        
        for name, path in legacy_systems:
            if path is None:  # Basic Memory check
                try:
                    result = subprocess.run(["basic-memory", "status"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        status_lines.append(f"✅ {name}: Connected")
                    else:
                        status_lines.append(f"❌ {name}: Not connected")
                except:
                    status_lines.append(f"❌ {name}: Not available")
            elif path and path.exists():
                status_lines.append(f"✅ {name}: Available")
            else:
                status_lines.append(f"❌ {name}: Missing")
        
        # Show dimension stats
        try:
            with open(self.global_config) as f:
                config = json.load(f)
            
            status_lines.append("\n📊 DIMENSIONAL TRACKING:")
            for dim, info in config["dimensions"].items():
                status_lines.append(f"{info['color']} {dim}: {info['description']}")
        except:
            status_lines.append("\n❌ Could not load dimension config")
        
        status_text = "\n".join(status_lines)
        print(status_text)
        return status_text


def main():
    """Main entry point for global brain help"""
    brain_help = GlobalBrainHelp()
    
    if len(sys.argv) < 2:
        brain_help.show_help()
        return
    
    command = sys.argv[1]
    
    if command == "help" or command == "/brain_help" or command == "brain_help":
        detailed = "--detailed" in sys.argv
        brain_help.show_help(detailed)
    elif command == "store" and len(sys.argv) > 2:
        content = " ".join(sys.argv[2:])
        result = brain_help.brain_store(content)
        print(result)
    elif command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        # Parse optional flags
        dimension = None
        tag = None
        if "--dim" in sys.argv:
            dim_idx = sys.argv.index("--dim")
            if dim_idx + 1 < len(sys.argv):
                dimension = sys.argv[dim_idx + 1]
        if "--tag" in sys.argv:
            tag_idx = sys.argv.index("--tag")
            if tag_idx + 1 < len(sys.argv):
                tag = sys.argv[tag_idx + 1]
        
        result = brain_help.brain_search(query, dimension, tag)
        print(result)
    elif command == "status":
        brain_help.brain_status()
    else:
        print("Usage: brain_help_global.py [help|store|search|status] [args...]")
        print("Run 'brain_help_global.py help' for detailed usage information")


if __name__ == "__main__":
    main()