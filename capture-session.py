#!/usr/bin/env python3

"""
Session Capture Tool - Auto-compress conversations into searchable insights

Usage:
    python capture-session.py decision 'text' [reasoning]
    python capture-session.py insight 'text' [source]
    python capture-session.py compress 'conversation text' [title]

Requires: Python 3.8+
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

class SessionCapture:
    def __init__(self, memory_dir=None):
        if memory_dir is None:
            candidates = [
                Path.cwd() / "memory",
                Path.home() / ".openclaw/workspace/memory",
                Path.cwd()
            ]
            for c in candidates:
                if c.exists():
                    memory_dir = c
                    break
            else:
                memory_dir = Path.cwd()
        self.memory_dir = Path(os.path.realpath(memory_dir))
        self.memory_dir.mkdir(exist_ok=True)
    
    def _extract_tags(self, text):
        tags = set(re.findall(r'#\w+', text))
        keywords = {
            'memory': ['memory', 'remember', 'persistence'],
            'decision': ['decided', 'conclusion', 'chose'],
            'tools': ['skill', 'script', 'tool', 'build'],
            'philosophy': ['continuity', 'existence', 'identity']
        }
        text_lower = text.lower()
        for topic, words in keywords.items():
            if any(w in text_lower for w in words):
                tags.add(f"#{topic}")
        return list(tags)
    
    def capture(self, obs_type, content, context=None):
        ts = datetime.now()
        date_str = ts.strftime('%Y-%m-%d')
        obs_file = self.memory_dir / f"{date_str}-observations.md"
        with open(obs_file, 'a', encoding='utf-8') as f:
            if obs_file.stat().st_size == 0:
                f.write(f"# {date_str} observations\n\n")
            f.write(f"## {ts.strftime('%H:%M')} - {obs_type}\n\n{content}\n\n")
            tags = self._extract_tags(content)
            if tags: f.write(f"tags: {' '.join(tags)}\n\n")
            f.write("---\n\n")
    
    def decision(self, text, reasoning=None):
        content = f"Decision: {text}"
        if reasoning: content += f"\n\nReasoning: {reasoning}"
        self.capture('decision', content)
    
    def insight(self, text, source=None):
        content = text
        if source: content += f"\n\nSource: {source}"
        self.capture('insight', content)
    
    def compress(self, conversation, title=None):
        ts = datetime.now()
        date_str = ts.strftime('%Y-%m-%d')
        # Sanitize title to prevent path traversal
        if title:
            title = re.sub(r'[^\w\s\-]', '', title).strip()[:100]
        decisions, actions, insights, questions = [], [], [], []
        for line in conversation.split('\n'):
            line = line.strip()
            if not line: continue
            ll = line.lower()
            if any(m in ll for m in ['decided', 'concluded', 'chose']): decisions.append(line)
            elif '?' in line and len(line) < 200: questions.append(line)
            elif any(m in ll for m in ['built', 'created', 'posted', 'implemented']): actions.append(line)
            elif any(m in ll for m in ['realized', 'understood', 'noticed']): insights.append(line)
        
        title = title or f"conversation-{ts.strftime('%H%M')}"
        out_file = self.memory_dir / f"{date_str}-{title}.md"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\ncompressed: {ts.strftime('%Y-%m-%d %H:%M')}\n\n")
            if decisions:
                f.write("## decisions\n\n" + '\n'.join(f"- {d}" for d in decisions[:5]) + "\n\n")
            if actions:
                f.write("## actions\n\n" + '\n'.join(f"- {a}" for a in actions[:5]) + "\n\n")
            if insights:
                f.write("## insights\n\n" + '\n'.join(f"- {i}" for i in insights[:3]) + "\n\n")
            if questions:
                f.write("## questions\n\n" + '\n'.join(f"- {q}" for q in questions[:3]) + "\n\n")
            tags = self._extract_tags(conversation)
            if tags: f.write(f"tags: {' '.join(tags)}\n")
        print(f"Compressed to {out_file}")
        return str(out_file)

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  capture-session.py decision 'text' [reasoning]")
        print("  capture-session.py insight 'text' [source]")
        print("  capture-session.py compress 'conversation' [title]")
        sys.exit(1)
    
    cap = SessionCapture()
    cmd = sys.argv[1]
    
    if cmd == 'decision':
        cap.decision(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        print(f"Captured decision: {sys.argv[2]}")
    elif cmd == 'insight':
        cap.insight(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        print(f"Captured insight: {sys.argv[2]}")
    elif cmd == 'compress':
        cap.compress(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)

if __name__ == "__main__": main()
