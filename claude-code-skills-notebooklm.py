"""
YouTube Search — outputs top 5 video URLs as JSON for NotebookLM MCP pipeline.

Usage: python claude-code-skills-notebooklm.py "your topic here"
Requires: export YOUTUBE_API_KEY="your_key_here"

NotebookLM steps (create notebook, add sources, analyze, generate infographic)
are handled by Claude Code via the notebooklm-mcp-cli MCP server.
Install: pip install notebooklm-mcp-cli && nlm setup add claude-code
"""
import re
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    raise SystemExit("Usage: python claude-code-skills-notebooklm.py \"your topic here\"")
topic = sys.argv[1]

api_key = os.environ.get("YOUTUBE_API_KEY")
if not api_key:
    raise SystemExit("ERROR: YOUTUBE_API_KEY environment variable not set.\n"
                     "Run: export YOUTUBE_API_KEY='your_key_here'")


def duration_seconds(d: str) -> int:
    """Parse ISO 8601 duration string (e.g. PT1H30M45S) to total seconds."""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d)
    if not m:
        return 0
    h, mins, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mins * 60 + s


# Step 1: Search YouTube for trending videos on the given topic
print(f"Searching YouTube for '{topic}' videos...")
query = urllib.parse.urlencode({
    "part": "snippet",
    "q": f"{topic} tutorial {datetime.now().year}",
    "type": "video",
    "maxResults": 20,
    "order": "viewCount",
    "relevanceLanguage": "en",
    "key": api_key,
})
url = f"https://www.googleapis.com/youtube/v3/search?{query}"
with urllib.request.urlopen(url) as resp:
    data = json.load(resp)

video_ids = [item["id"]["videoId"] for item in data.get("items", []) if item["id"].get("videoId")]

if not video_ids:
    raise SystemExit(f"YouTube search returned no video results for topic: {topic}")

# Fetch view counts, duration, and snippet in one call
stats_query = urllib.parse.urlencode({
    "part": "statistics,contentDetails,snippet",
    "id": ",".join(video_ids),
    "key": api_key,
})
stats_url = f"https://www.googleapis.com/youtube/v3/videos?{stats_query}"
with urllib.request.urlopen(stats_url) as resp:
    stats_data = json.load(resp)

videos = []
for item in stats_data.get("items", []):
    vid_id = item["id"]
    snippet = item["snippet"]
    stats = item.get("statistics", {})
    duration = item.get("contentDetails", {}).get("duration", "")
    lang = snippet.get("defaultAudioLanguage", snippet.get("defaultLanguage", "en"))
    if lang and not lang.startswith("en"):
        continue
    # Skip YouTube Shorts (under 2 minutes)
    if duration_seconds(duration) < 120:
        continue
    videos.append({
        "title": snippet.get("title", ""),
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "views": int(stats.get("viewCount") or 0),
        "channel": snippet.get("channelTitle", ""),
        "duration": duration,
    })

# Sort by view count, take top 5
videos = sorted(videos, key=lambda x: x["views"], reverse=True)[:5]

if not videos:
    raise SystemExit(f"No videos found for topic: {topic}")

print(json.dumps(videos))
