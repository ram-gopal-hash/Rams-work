"""
YouTube Search — outputs top 5 video URLs as JSON for NotebookLM MCP pipeline.

Usage: python yt-search.py "your topic here"
Requires YOUTUBE_API_KEY in .env or environment.

NotebookLM steps (create notebook, add sources, analyze, generate output)
are handled by Claude Code via nlm CLI.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def duration_to_seconds(iso: str) -> int:
    """Parse ISO 8601 duration (PT1H30M45S) → total seconds."""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mins, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mins * 60 + s


def yt_api(endpoint: str, params: dict, api_key: str) -> dict:
    params["key"] = api_key
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def search_youtube(topic: str, api_key: str, top_n: int = 5) -> list:
    print(f"Searching YouTube for '{topic}' ...", file=sys.stderr)

    # Step 1: search for video IDs
    search_data = yt_api("search", {
        "part": "snippet",
        "q": topic,
        "type": "video",
        "maxResults": 50,
        "relevanceLanguage": "en",
        "order": "relevance",
    }, api_key)

    video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
    if not video_ids:
        raise SystemExit(f"No YouTube results found for: {topic}")

    # Step 2: get duration + view count for all IDs in one request
    details_data = yt_api("videos", {
        "part": "contentDetails,statistics,snippet",
        "id": ",".join(video_ids),
    }, api_key)

    videos = []
    for item in details_data.get("items", []):
        duration = duration_to_seconds(item["contentDetails"].get("duration", ""))
        if duration < 120:  # skip Shorts
            continue
        views = int(item["statistics"].get("viewCount", 0))
        snippet = item["snippet"]

        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        dur_str = (
            f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"
        )

        videos.append({
            "title": snippet.get("title", ""),
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "views": views,
            "channel": snippet.get("channelTitle", ""),
            "duration": dur_str,
        })

    if not videos:
        raise SystemExit(f"No suitable videos found for: {topic}")

    return sorted(videos, key=lambda v: v["views"], reverse=True)[:top_n]


if __name__ == "__main__":
    load_env()
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python yt-search.py "your topic here"')
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise SystemExit(
            "YOUTUBE_API_KEY not set. Add it to .env or set the environment variable.\n"
            "Get a free key at: https://console.cloud.google.com/apis/library/youtube.googleapis.com"
        )
    topic = sys.argv[1]
    results = search_youtube(topic, api_key)
    print(json.dumps(results, indent=2))
