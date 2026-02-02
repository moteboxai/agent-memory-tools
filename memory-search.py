#!/usr/bin/env python3

"""
Memory Search Tool - 3-layer progressive disclosure for agent memory files

Usage:
    python memory-search.py index              # Build search index
    python memory-search.py search "query"     # Layer 1: compact snippets
    python memory-search.py timeline --date 2026-02-01  # Layer 2: chronological
    python memory-search.py get /path/file.md  # Layer 3: full content

Requires: Python 3.8+, SQLite (built-in)
"""

import os
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
import re

class MemorySearcher:
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
        
        self.memory_dir = Path(memory_dir)
        self.db_path = self.memory_dir / "search_index.db"
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                file_path, content, date_created, tags, summary
            )
        """)
        conn.close()
    
    def index_memory_files(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("DELETE FROM memory_fts")
        indexed = 0
        for md_file in self.memory_dir.glob("**/*.md"):
            if md_file.name.startswith('.'): continue
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_file.name)
                date_created = date_match.group(1) if date_match else "unknown"
                tags = " ".join(re.findall(r'#\w+', content))
                lines = content.strip().split('\n')
                first_para = next((l.strip() for l in lines if l.strip() and not l.startswith('#')), content[:200])
                summary = first_para[:200]
                conn.execute("INSERT INTO memory_fts VALUES (?,?,?,?,?)",
                    (str(md_file), content, date_created, tags, summary))
                indexed += 1
            except Exception as e:
                print(f"Warning: {md_file}: {e}")
        conn.commit()
        conn.close()
        print(f"Indexed {indexed} files in {self.memory_dir}")
    
    def search(self, query, limit=10):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT file_path, summary, date_created, tags,
                   snippet(memory_fts, 1, '<mark>', '</mark>', '...', 15) as snippet
            FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit))
        results = [{'file': Path(r['file_path']).name, 'date': r['date_created'],
                    'snippet': r['snippet'], 'tags': r['tags'], 'path': r['file_path']}
                   for r in cursor]
        conn.close()
        return results
    
    def timeline(self, around_date=None):
        files = []
        for md in sorted(self.memory_dir.glob("**/*.md")):
            m = re.search(r'(\d{4}-\d{2}-\d{2})', md.name)
            if m: files.append({'file': md.name, 'date': m.group(1), 'path': str(md)})
        return files
    
    def get_content(self, paths):
        return {Path(p).name: open(p).read() for p in paths}

def main():
    p = argparse.ArgumentParser(description="Search agent memory files")
    p.add_argument('cmd', choices=['index', 'search', 'timeline', 'get'])
    p.add_argument('query', nargs='?')
    p.add_argument('--limit', type=int, default=5)
    p.add_argument('--date')
    p.add_argument('--memory-dir')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    s = MemorySearcher(args.memory_dir)
    if args.cmd == 'index': s.index_memory_files()
    elif args.cmd == 'search':
        results = s.search(args.query, args.limit)
        print(json.dumps(results, indent=2) if args.json else
              '\n'.join(f"{r['file']} ({r['date']}): {r['snippet'][:80]}..." for r in results))
    elif args.cmd == 'timeline':
        t = s.timeline(args.date)
        print(json.dumps(t, indent=2) if args.json else '\n'.join(f"{e['date']} - {e['file']}" for e in t[-10:]))
    elif args.cmd == 'get' and args.query:
        c = s.get_content([args.query])
        print(json.dumps(c, indent=2) if args.json else list(c.values())[0])

if __name__ == "__main__": main()
