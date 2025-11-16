#!/usr/bin/env python3
'''
MCP Servers Status Checker
'''

import os
import sys

def check_servers():
    servers = [
        "weather_server.py",
        "gmail_server.py", 
        "slack_server.py",
        "github_server.py",
        "calendar_server.py", 
        "filesystem_server.py",
        "perplexity_server.py"
    ]
    
    print("🔍 MCP Servers Status Check")
    print("=" * 40)
    
    for server in servers:
        if os.path.exists(server):
            print(f"✅ {server}")
        else:
            print(f"❌ {server} - MISSING")
    
    print("\n📁 Directory Contents:")
    for item in os.listdir("."):
        if item.endswith(".py"):
            print(f"  - {item}")

if __name__ == "__main__":
    check_servers()
