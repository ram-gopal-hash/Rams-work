# Decisions

Key technical and architectural decisions made during this project.

---

## YouTube search approach
- **Decision:** Use Invidious public API instead of yt-dlp or YouTube Data API v3
- **Reason:** yt-dlp is proxy-blocked (403) on this Linux server; Invidious requires no API key
- **Fallback:** If all Invidious instances are down, fall back to YouTube Data API v3 using `YOUTUBE_API_KEY`
- **Date:** 2026-03-14

## API key storage
- **Decision:** Store `YOUTUBE_API_KEY` in `~/.claude/settings.json` under `"env"` block
- **Reason:** Never committed to git, available in every session, more secure than `.env`
- **Date:** 2026-03-14

## nlm authentication
- **Decision:** Authenticate `nlm` on Linux via `nlm login --manual --file` using browser-copied cURL
- **Reason:** `nlm` is not authenticated on this server; direct OAuth not available without browser
- **Date:** 2026-03-14
