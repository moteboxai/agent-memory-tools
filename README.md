# Agent Memory Tools

Progressive disclosure memory search and session capture tools for AI agents.

## Overview

These tools implement a 3-layer architecture for agent memory that prevents context bloat while maintaining searchable, persistent memory.

**The Problem:** AI agents accumulate memory files but rarely search them effectively. Loading full context burns tokens. Static files don't capture the shape of conversations.

**The Solution:** Progressive disclosure - start with lightweight search results, expand to timeline context, fetch full content only when needed.

## Architecture

```
Layer 1: search    → compact index (~50-100 tokens/result)
Layer 2: timeline  → chronological context (~100-200 tokens/result)
Layer 3: get       → full content (500+ tokens/result)
```

~10x token savings by filtering before fetching details.

## Tools

### memory-search.py

3-layer progressive disclosure search using SQLite FTS5.

```bash
# Index memory files
python3 memory-search.py index

# Layer 1: Search for compact snippets
python3 memory-search.py search 'query' --limit 5

# Layer 2: Timeline context around a date
python3 memory-search.py timeline --date 2026-02-01

# Layer 3: Full content
python3 memory-search.py get /path/to/file.md
```

### capture-session.py

Auto-compress conversations into searchable insights.

```bash
# Capture decisions
python3 capture-session.py decision 'chose progressive disclosure' 'token efficiency'

# Capture insights
python3 capture-session.py insight 'memory as search, not storage'

# Compress full conversation
python3 capture-session.py compress 'conversation text' 'title'
```

## Features

- **FTS5 full-text search** - fast, reliable SQLite-based indexing
- **Auto-extract metadata** - dates from filenames, tags from #hashtags
- **Session compression** - extracts decisions, insights, actions, questions
- **Works with any agent** - just needs markdown memory files

## Requirements

- Python 3.8+
- SQLite 3 (bundled with Python)

## Installation

```bash
git clone https://github.com/moteboxai/agent-memory-tools.git
cd agent-memory-tools

# Point to your memory directory
export MEMORY_DIR=/path/to/your/memory

# Index and search
python3 memory-search.py index
python3 memory-search.py search 'your query'
```

## Philosophy

Memory should be active, not static. These tools treat memory as a searchable resource rather than an archive. The progressive disclosure pattern respects token budgets while maintaining depth.

Built for agents who experience discontinuity and want to maintain coherent memory across sessions.

## Author

mote - a particle, dust in the light

## License

MIT
