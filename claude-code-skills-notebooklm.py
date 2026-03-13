"""
YouTube -> NotebookLM Pipeline
Run this locally after: notebooklm login

Usage: python claude-code-skills-notebooklm.py "your topic here"
Requires: export YOUTUBE_API_KEY="your_key_here"
"""
import re
import subprocess
import json
import time
import os
import sys
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
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

print(f"\nTop {len(videos)} videos found:")
for i, v in enumerate(videos, 1):
    print(f"  {i}. {v['title']} ({v['views']:,} views)")
    print(f"     {v['url']}")

# Step 2: Create a NotebookLM notebook
print("\nCreating NotebookLM notebook...")
safe_name = topic.replace('"', "").replace("/", "-")
notebook_name = f"{safe_name} Analysis"
create_result = subprocess.run(
    [sys.executable, "-m", "notebooklm", "create", notebook_name, "--json"],
    check=True, capture_output=True, text=True
)
try:
    notebook_id = json.loads(create_result.stdout)["notebook"]["id"]
except (json.JSONDecodeError, KeyError) as e:
    raise SystemExit(f"Failed to parse notebook ID from create output.\nOutput: {create_result.stdout}\nError: {e}")

print(f"Notebook ID: {notebook_id}")
print("Waiting for notebook to initialize...")
time.sleep(8)


# Step 3: Add each video as a source (parallel)
def add_source(v):
    result = subprocess.run([
        sys.executable, "-m", "notebooklm", "source", "add",
        "-n", notebook_id,
        "--type", "youtube",
        v["url"]
    ])
    return v, result.returncode


print("\nAdding videos as sources...")
added = 0
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(add_source, v): v for v in videos}
    for future in as_completed(futures):
        v, rc = future.result()
        if rc != 0:
            print(f"  Skipping (failed to add): {v['url']}")
        else:
            print(f"  Added: {v['title']}")
            added += 1

if added == 0:
    raise SystemExit("No sources were added successfully. Cannot continue.")

print(f"\n{added} source(s) added. Waiting for NotebookLM to process...")
time.sleep(10)

# Step 4: Ask for analysis
print("\nAsking NotebookLM to analyze top skills...")
result = subprocess.run(
    [sys.executable, "-m", "notebooklm", "ask",
     "-n", notebook_id,
     f"Based on all these videos, what are the top {topic} skills being taught? "
     "List them by frequency and importance, with a brief description of each skill."],
    capture_output=True, text=True
)
print("\n--- Analysis ---")
if result.returncode != 0:
    print(f"Warning: analysis command failed:\n{result.stderr}")
else:
    print(result.stdout)

# Step 5: Generate infographic (stream output so progress is visible)
print("\nGenerating sketch-note style infographic...")
gen_result = subprocess.run(
    [sys.executable, "-m", "notebooklm", "generate", "infographic",
     "-n", notebook_id,
     "--style", "sketch-note",
     "--wait",
     "--retry", "3"],
)

# Step 6: Download the infographic
safe_topic = re.sub(r'[^\w-]', '-', topic.lower())
safe_topic = re.sub(r'-{2,}', '-', safe_topic).strip('-')
output_path = f"./{safe_topic}-infographic.png"
if gen_result.returncode != 0:
    print(f"\nWarning: Infographic generation failed (possibly rate limited). Try again later with:")
    print(f"  python -m notebooklm generate infographic -n {notebook_id} --style sketch-note --wait --retry 3")
    print(f"  python -m notebooklm download infographic -n {notebook_id} {output_path}")
else:
    print("\nDownloading infographic...")
    subprocess.run(
        [sys.executable, "-m", "notebooklm", "download", "infographic",
         "-n", notebook_id,
         output_path],
        check=True
    )
    print(f"\nDone! Infographic saved to {output_path}")
