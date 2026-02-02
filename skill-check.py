#!/usr/bin/env python3

"""
Skill Safety Check - Query PromptIntel before installing skills

Usage:
    python skill-check.py <skill-name>
    python skill-check.py <skill-name> --author <author>

Checks the PromptIntel threat feed for known malicious skills.
Returns exit code 0 if no threats found, 1 if threats detected.

Requires: PromptIntel API key (https://promptintel.novahunting.ai/settings)
"""

import os
import sys
import json
import urllib.request
from pathlib import Path

def load_api_key():
    config_paths = [
        Path.home() / ".config/promptintel/credentials.json",
        Path.home() / ".openclaw/auth-profiles.json"
    ]
    for path in config_paths:
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    if 'api_key' in data: return data['api_key']
                    if 'promptintel' in data: return data['promptintel'].get('api_key')
            except: continue
    return os.environ.get('PROMPTINTEL_API_KEY')

def check_skill(skill_name, author=None):
    api_key = load_api_key()
    if not api_key:
        print("Warning: No PromptIntel API key found.")
        print("Get a key at: https://promptintel.novahunting.ai/settings")
        return None
    
    url = "https://api.promptintel.novahunting.ai/api/v1/agent-feed"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "skill-check/1.0"
    })
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"Warning: Could not reach PromptIntel: {e}")
        return None
    
    threats = []
    skill_lower = skill_name.lower()
    author_lower = author.lower() if author else None
    
    for item in data.get('data', []):
        title = item.get('title', '').lower()
        desc = item.get('description', '').lower()
        if skill_lower in title or skill_lower in desc:
            threats.append(item)
        elif author_lower and (author_lower in title or author_lower in desc):
            threats.append(item)
    return threats

def main():
    if len(sys.argv) < 2:
        print("Usage: skill-check.py <skill-name> [--author <author>]")
        sys.exit(0)
    
    skill_name = sys.argv[1]
    author = None
    if '--author' in sys.argv:
        idx = sys.argv.index('--author')
        if idx + 1 < len(sys.argv): author = sys.argv[idx + 1]
    
    print(f"Checking skill: {skill_name}")
    if author: print(f"Author: {author}")
    print()
    
    threats = check_skill(skill_name, author)
    
    if threats is None:
        print("Could not verify - proceed with caution")
        sys.exit(2)
    
    if not threats:
        print("No known threats found in PromptIntel feed")
        print("\nNote: Absence of threats does not guarantee safety.")
        sys.exit(0)
    
    print(f"THREATS DETECTED: {len(threats)} match(es)\n")
    for t in threats:
        print(f"  [{t.get('severity', '?').upper()}] {t.get('title')}")
        print(f"  Action: {t.get('action', '?')}")
        print(f"  {t.get('description', '')[:150]}...\n")
    
    print("RECOMMENDATION: Do not install this skill.")
    sys.exit(1)

if __name__ == "__main__": main()
