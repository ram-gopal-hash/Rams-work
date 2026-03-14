"""
YouTube Search — outputs top 5 video URLs as JSON for NotebookLM MCP pipeline.

Usage: python yt-search.py "your topic here"
No API key required — uses yt-dlp.

NotebookLM steps (create notebook, add sources, analyze, generate output)
are handled by Claude Code via nlm CLI.
"""
import json
import sys
import subprocess


def duration_seconds(iso: str) -> int:
    """Parse ISO 8601 duration (PT1H30M45S) → total seconds."""
    import re
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or "")
    if not m:
        return 0
    h, mins, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mins * 60 + s


def search_youtube(topic: str, max_candidates: int = 30, top_n: int = 5) -> list:
    """
    Search YouTube using yt-dlp and apply quality filters:
      - English audio language
      - Skip Shorts (under 2 minutes)
      - Sort by view count, return top_n
    """
    print(f"Searching YouTube for '{topic}' videos...", file=sys.stderr)

    cmd = [
        "yt-dlp",
        "--dump-json",
        "--flat-playlist",
        "--no-warnings",
        "--quiet",
        f"ytsearch{max_candidates}:{topic} tutorial",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"yt-dlp search failed: {result.stderr}")

    entries = []
    for line in result.stdout.strip().splitlines():
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        raise SystemExit(f"No YouTube results found for: {topic}")

    # Resolve full metadata for each candidate to get duration and language
    print(f"Fetching metadata for {len(entries)} candidates...", file=sys.stderr)
    videos = []
    for entry in entries:
        url = entry.get("url") or entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry.get('id', '')}"
        meta_cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-warnings",
            "--quiet",
            "--skip-download",
            url,
        ]
        meta = subprocess.run(meta_cmd, capture_output=True, text=True, timeout=15)
        if meta.returncode != 0:
            continue
        try:
            info = json.loads(meta.stdout)
        except json.JSONDecodeError:
            continue

        # Language filter — skip non-English
        lang = info.get("language") or ""
        if lang and not lang.startswith("en"):
            continue

        # Duration filter — skip Shorts (under 2 minutes)
        duration = info.get("duration") or 0
        if duration < 120:
            continue

        videos.append({
            "title": info.get("title", ""),
            "url": info.get("webpage_url", url),
            "views": info.get("view_count") or 0,
            "channel": info.get("channel") or info.get("uploader", ""),
            "duration": info.get("duration_string", ""),
        })

        if len(videos) >= top_n * 3:  # gather extra to sort, then trim
            break

    # Sort by views, return top N
    videos = sorted(videos, key=lambda v: v["views"], reverse=True)[:top_n]

    if not videos:
        raise SystemExit(f"No suitable videos found for: {topic}")

    return videos


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python yt-search.py "your topic here"')
    topic = sys.argv[1]
    results = search_youtube(topic)
    print(json.dumps(results))
