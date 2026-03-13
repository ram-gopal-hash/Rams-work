"""
YouTube -> NotebookLM Pipeline
Run this locally after: notebooklm login

Usage: python claude-code-skills-notebooklm.py "your topic here"
Requires: export YOUTUBE_API_KEY="your_key_here"
"""
import subprocess
import json
import time
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

# Step 1: Search YouTube for trending videos on the given topic
print(f"Searching YouTube for '{topic}' videos...")
query = urllib.parse.urlencode({
    "part": "snippet",
    "q": f"{topic} tutorial {datetime.now().year}",
    "type": "video",
    "maxResults": 10,
    "order": "viewCount",
    "key": api_key,
})
url = f"https://www.googleapis.com/youtube/v3/search?{query}"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read())

video_ids = [item["id"]["videoId"] for item in data.get("items", []) if item["id"].get("videoId")]

# Fetch view counts
stats_query = urllib.parse.urlencode({
    "part": "statistics,contentDetails,snippet",
    "id": ",".join(video_ids),
    "key": api_key,
})
stats_url = f"https://www.googleapis.com/youtube/v3/videos?{stats_query}"
with urllib.request.urlopen(stats_url) as resp:
    stats_data = json.loads(resp.read())

videos = []
for item in stats_data.get("items", []):
    vid_id = item["id"]
    snippet = item["snippet"]
    stats = item.get("statistics", {})
    duration = item.get("contentDetails", {}).get("duration", "")
    videos.append({
        "title": snippet.get("title", ""),
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "views": int(stats.get("viewCount") or 0),
        "channel": snippet.get("channelTitle", ""),
        "duration": duration,
    })

# Sort by view count, take top 5
videos = sorted(videos, key=lambda x: x["views"] or 0, reverse=True)[:5]

if not videos:
    raise SystemExit(f"No videos found for topic: {topic}")

print(f"\nTop {len(videos)} videos found:")
for i, v in enumerate(videos, 1):
    print(f"  {i}. {v['title']} ({v['views']:,} views)")
    print(f"     {v['url']}")

# Step 2: Create a NotebookLM notebook and switch to it
print("\nCreating NotebookLM notebook...")
notebook_name = f"{topic.replace(chr(34), '').replace('/', '-')} Analysis"
create_result = subprocess.run(
    [sys.executable, "-m", "notebooklm", "create", notebook_name, "--json"],
    check=True, capture_output=True, text=True
)
notebook_id = json.loads(create_result.stdout).get("id", notebook_name)
time.sleep(3)
subprocess.run([sys.executable, "-m", "notebooklm", "use", notebook_id], check=True)
time.sleep(2)

# Step 3: Add each video as a source
print("\nAdding videos as sources...")
for v in videos:
    if v["url"]:
        print(f"  Adding: {v['title']}")
        result = subprocess.run([sys.executable, "-m", "notebooklm", "source", "add", v["url"]])
        if result.returncode != 0:
            print(f"  Skipping (failed to add): {v['url']}")
        time.sleep(1)

# Step 4: Ask for analysis
print("\nAsking NotebookLM to analyze top skills...")
result = subprocess.run(
    [sys.executable, "-m", "notebooklm", "ask",
     f"Based on all these videos, what are the top {topic} skills being taught? "
     "List them by frequency and importance, with a brief description of each skill."],
    capture_output=True, text=True
)
print("\n--- Analysis ---")
if result.returncode != 0:
    print(f"Warning: analysis command failed:\n{result.stderr}")
else:
    print(result.stdout)

# Step 5: Generate infographic
print("\nGenerating sketch-note style infographic...")
subprocess.run(
    [sys.executable, "-m", "notebooklm", "generate", "infographic",
     "--style", "sketch-note",
     "--wait"],
    check=True
)

# Step 6: Download the infographic
print("\nDownloading infographic...")
safe_topic = topic.replace(" ", "-").lower()
subprocess.run(
    [sys.executable, "-m", "notebooklm", "download", "infographic", f"./{safe_topic}-infographic"],
    check=True
)

print(f"\nDone! Infographic saved to ./{safe_topic}-infographic")
