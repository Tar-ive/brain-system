#!/usr/bin/env python3
"""
MCP Validation Script
Tests individual MCP servers for basic functionality and configuration correctness.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def validate_node_mcp(name, build_path):
    """Validate a Node.js-based MCP server"""
    print(f"Validating {name}...")

    if not os.path.exists(build_path):
        print(f"  ❌ Build file not found: {build_path}")
        return False

    try:
        # Check if the built file is valid JavaScript
        result = subprocess.run(['node', '-c', build_path],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  ✅ {name} build validation passed")
            return True
        else:
            print(f"  ❌ {name} build validation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ❌ {name} validation timed out")
        return False
    except Exception as e:
        print(f"  ❌ {name} validation error: {e}")
        return False

def validate_python_mcp(name, directory):
    """Validate a Python-based MCP server"""
    print(f"Validating {name}...")

    server_py = os.path.join(directory, 'server.py')
    if not os.path.exists(server_py):
        print(f"  ❌ Server file not found: {server_py}")
        return False

    try:
        # Check if uv can validate the project
        result = subprocess.run(['uv', 'run', '--directory', directory, 'python', '-c', 'import server'],
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"  ✅ {name} Python validation passed")
            return True
        else:
            print(f"  ❌ {name} Python validation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ❌ {name} validation timed out")
        return False
    except Exception as e:
        print(f"  ❌ {name} validation error: {e}")
        return False

def validate_configuration():
    """Validate the MCP configuration file"""
    config_path = '/Users/tarive/mcp-brain-system.json'
    print(f"Validating configuration: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        if 'mcpServers' not in config:
            print("  ❌ Missing 'mcpServers' key in configuration")
            return False

        expected_services = ['reddit', 'hackernews', 'discord', 'firecrawl',
                           'basic-memory', 'imessage', 'gmail', 'memory-fallback',
                           'splitwise', 'whatsapp']

        missing_services = []
        for service in expected_services:
            if service not in config['mcpServers']:
                missing_services.append(service)

        if missing_services:
            print(f"  ❌ Missing services in configuration: {missing_services}")
            return False

        print(f"  ✅ Configuration validation passed ({len(config['mcpServers'])} services)")
        return True

    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in configuration: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Configuration validation error: {e}")
        return False

def main():
    """Main validation routine"""
    print("🔍 MCP Brain System Validation")
    print("=" * 40)

    base_path = '/Users/tarive/brain-mcp-servers'

    validations = [
        # Configuration validation
        ("Configuration", validate_configuration, []),

        # Node.js MCPs
        ("Hacker News MCP", validate_node_mcp,
         ['hackernews', f'{base_path}/mcp-claude-hackernews/build/index.js']),
        ("Discord MCP", validate_node_mcp,
         ['discord', f'{base_path}/discordmcp/build/index.js']),

        # Python MCPs
        ("Reddit MCP", validate_python_mcp,
         ['reddit', f'{base_path}/reddit-mcp']),
    ]

    results = []
    for name, validator, args in validations:
        if args:
            result = validator(*args)
        else:
            result = validator()
        results.append((name, result))

    print("\n" + "=" * 40)
    print("📊 Validation Summary")
    print("=" * 40)

    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {name}")
        if result:
            passed += 1

    print(f"\nResult: {passed}/{len(results)} validations passed")

    if passed == len(results):
        print("🎉 All validations passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("⚠️  Some validations failed. Please fix issues before deployment.")
        sys.exit(1)

if __name__ == '__main__':
    main()