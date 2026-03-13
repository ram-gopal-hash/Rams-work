"""
Claude Code Skills -> NotebookLM Pipeline
Run this locally after: notebooklm login
"""
import subprocess
import json
import time

# Step 1: Search YouTube for trending Claude Code Skills videos
print("Searching YouTube for Claude Code Skills videos...")
result = subprocess.run(
    ["yt-dlp", "-j", "--flat-playlist", "ytsearch10:Claude Code skills tutorial 2025",
     "--no-warnings"],
    capture_output=True, text=True
)

videos = []
for line in result.stdout.splitlines():
    try:
        v = json.loads(line)
        videos.append({
            "title": v.get("title", ""),
            "url": v.get("url") or v.get("webpage_url", ""),
            "views": v.get("view_count", 0),
            "channel": v.get("uploader", ""),
            "duration": v.get("duration_string", ""),
        })
    except json.JSONDecodeError:
        pass

# Sort by view count, take top 5
videos = sorted(videos, key=lambda x: x["views"] or 0, reverse=True)[:5]

print(f"\nTop {len(videos)} videos found:")
for i, v in enumerate(videos, 1):
    print(f"  {i}. {v['title']} ({v['views']:,} views)")
    print(f"     {v['url']}")

# Step 2: Create a NotebookLM notebook
print("\nCreating NotebookLM notebook...")
subprocess.run(["notebooklm", "create", "Claude Code Skills Analysis"], check=True)
time.sleep(2)

# Step 3: Add each video as a source
print("\nAdding videos as sources...")
for v in videos:
    if v["url"]:
        print(f"  Adding: {v['title']}")
        subprocess.run(["notebooklm", "source", "add", v["url"]], check=True)
        time.sleep(1)

# Step 4: Ask for analysis
print("\nAsking NotebookLM to analyze top skills...")
result = subprocess.run(
    ["notebooklm", "ask",
     "Based on all these videos, what are the top Claude Code skills being taught? "
     "List them by frequency and importance, with a brief description of each skill."],
    capture_output=True, text=True
)
print("\n--- Analysis ---")
print(result.stdout)

# Step 5: Generate infographic
print("\nGenerating handwritten blueprint style infographic...")
subprocess.run(
    ["notebooklm", "generate", "infographic",
     "--style", "handwritten blueprint",
     "--wait"],
    check=True
)

# Step 6: Download the infographic
print("\nDownloading infographic...")
subprocess.run(
    ["notebooklm", "download", "infographic", "./claude-code-skills-infographic"],
    check=True
)

print("\nDone! Infographic saved to ./claude-code-skills-infographic")
