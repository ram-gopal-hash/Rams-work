# User Context

Running notes about the current state of the project and what Ram is working on.

---

## Active project
YouTube → NotebookLM research pipeline from Claude Code chat.

**Goal:** Type a topic in chat → Claude finds top YouTube videos → adds them to a new NotebookLM notebook → returns analysis.

## Current status (2026-03-14)
- `yt-search.py` exists but uses YouTube Data API v3 (key not yet set in `~/.claude/settings.json`)
- Plan written: rewrite `yt-search.py` to use Invidious public API (no key needed)
- `nlm` not yet authenticated on this server
- `~/.claude/settings.json` ready to receive `YOUTUBE_API_KEY` under `"env"` block

## Blockers
- User needs to provide their real YouTube API key (or we proceed with Invidious rewrite)
- `nlm login --manual --file` step not yet done (needs user to copy cURL from browser)

## Files
| File | Purpose |
|------|---------|
| `yt-search.py` | YouTube search (currently YouTube Data API, planned: Invidious) |
| `yt-search-skill.md` | Docs for yt-search skill |
| `notebooklm-mcp-skill.md` | Full pipeline docs |
| `notebooklm-py-install.md` | Install notes for nlm |
| `memory/` | This persistent memory system |
