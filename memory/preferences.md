# Preferences

How Ram likes to work and communicate.

---

## Communication style
- Concise answers, no filler
- Prefers options presented as a table or bullet list before acting
- Asks clarifying questions before Claude charges ahead

## Workflow
- Everything runs from Claude Code chat — no separate terminal, no PowerShell
- Avoids sharing secrets in the conversation; prefers config files or settings
- Prefers Python scripts over shell one-liners for anything reusable

## Tools & environment
- Python 3.11 available at `/usr/bin/python3`
- `nlm` (notebooklm-tools) installed but needs auth
- Network: HTTP proxy active; direct yt-dlp scraping is blocked (403)
- YouTube Data API v3 endpoint IS reachable from this server
- Branch naming convention: `claude/<description>-<sessionId>`
