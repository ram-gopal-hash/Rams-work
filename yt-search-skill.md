# yt-search-skill

**description:** Scrape YouTube metadata (titles, descriptions, durations, view counts, channels, thumbnails, upload dates, etc.) using yt-dlp — without downloading any media. Use this skill whenever the user wants to search YouTube, pull video info, extract playlist metadata, get channel stats, or build datasets from YouTube content. Trigger on mentions of "YouTube metadata", "video info", "yt-dlp", "YouTube search", "playlist scrape", "channel videos", or any request to gather structured data from YouTube URLs or search queries.

---

# YouTube Metadata Scraping with yt-dlp

Two approaches are available: CLI (quick, scriptable, great for one-off jobs) and Python API (programmatic, ideal for pipelines and post-processing). Both use the same underlying yt-dlp engine — pick whichever fits the task.

---

## 0 — Installation (one-time)

```bash
# Install from PyPI (covers both CLI and Python API)
pip install yt-dlp --break-system-packages

# Verify
yt-dlp --version
```

Repo reference: https://github.com/yt-dlp/yt-dlp.git

---

## Method 1 — CLI (yt-dlp command)

Best for: shell scripts, cron jobs, quick lookups, piping into jq.

### 1.1 Core flags for metadata-only mode

| Flag | Purpose |
|------|---------|
| `--dump-json` / `-j` | Print full metadata JSON for each video to stdout (no download) |
| `--dump-single-json` / `-J` | Same, but wraps playlist results in one JSON object |
| `--flat-playlist` | Don't resolve each video in a playlist — just list entries (fast) |
| `--skip-download` | Explicitly skip media download (useful with other post-processors) |
| `--print FIELD` | Print only specific fields, one per line |
| `--print-to-file FIELD FILE` | Append a field value to a file |
| `--no-warnings` | Suppress non-fatal warnings for cleaner piped output |

### 1.2 Single video metadata

```bash
# Full JSON blob
yt-dlp -j "https://www.youtube.com/watch?v=VIDEO_ID"

# Cherry-pick fields
yt-dlp --print "%(title)s | %(view_count)s views | %(upload_date)s" \
       "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 1.3 YouTube search (no URL needed)

```bash
# Search YouTube and dump metadata for the top 5 results
yt-dlp -j --flat-playlist "ytsearch5:machine learning 2025"

# Search and extract just titles + URLs
yt-dlp --print "%(title)s  %(webpage_url)s" "ytsearch10:lo-fi hip hop"
```

Search prefixes:

| Prefix | Behaviour |
|--------|-----------|
| `ytsearchN:` | Return top N results |
| `ytsearch_dateN:` | Return top N results, sorted by upload date |
| `ytsearchall:` | Return all results (use carefully — may be huge) |

### 1.4 Playlist / channel metadata

```bash
# Fast playlist listing (IDs + titles only, no per-video resolution)
yt-dlp -j --flat-playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Full metadata for every video in a playlist (slower, richer)
yt-dlp -j "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Channel — latest uploads tab
yt-dlp -j --flat-playlist "https://www.youtube.com/@CHANNEL_HANDLE/videos"

# Limit to N entries from a channel/playlist
yt-dlp -j --flat-playlist --playlist-items 1:20 \
       "https://www.youtube.com/@CHANNEL_HANDLE/videos"
```

### 1.5 Saving results to a file

```bash
# Dump search results to a JSONL file (one JSON object per line)
yt-dlp -j --flat-playlist "ytsearch20:python tutorial" > results.jsonl

# Or as a single JSON array
yt-dlp -J --flat-playlist "ytsearch20:python tutorial" > results.json
```

### 1.6 Useful field reference (template variables)

Common `%(field)s` names for `--print`:

```
id, title, description, upload_date, uploader, uploader_id,
channel, channel_id, channel_url, duration, duration_string,
view_count, like_count, comment_count, thumbnail, webpage_url,
categories, tags, live_status, availability, filesize_approx,
language, fps, resolution
```

Full list: `yt-dlp --print "%(field)s"` with any video, or check the output template docs.

---

## Method 2 — Python API (yt_dlp module)

Best for: applications, data pipelines, batch processing, custom filtering.

### 2.1 Basic single-video extraction

```python
import yt_dlp

def get_video_info(url: str) -> dict:
    """Extract metadata for a single video without downloading."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        # Don't fetch unnecessary stuff
        "extract_flat": False,
        "writesubtitles": False,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info  # full metadata dict


info = get_video_info("https://www.youtube.com/watch?v=VIDEO_ID")
print(info["title"], "|", info["view_count"], "views")
```

### 2.2 YouTube search via Python

```python
import yt_dlp
import json

def youtube_search(query: str, max_results: int = 10) -> list[dict]:
    """Search YouTube and return metadata for top results."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,       # fast — no per-video resolution
        "playlist_items": f"1:{max_results}",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
    return result.get("entries", [])


videos = youtube_search("rust programming tutorial", max_results=5)
for v in videos:
    print(f"{v.get('title')}  —  {v.get('url')}")
```

### 2.3 Full metadata search (resolve each result)

```python
def youtube_search_full(query: str, max_results: int = 5) -> list[dict]:
    """Search YouTube and fully resolve each result's metadata."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,  # resolve every entry
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
    return result.get("entries", [])


videos = youtube_search_full("quantum computing explained", max_results=3)
for v in videos:
    print(json.dumps({
        "title":       v.get("title"),
        "channel":     v.get("channel"),
        "views":       v.get("view_count"),
        "duration":    v.get("duration_string"),
        "upload_date": v.get("upload_date"),
        "url":         v.get("webpage_url"),
        "description": v.get("description", "")[:200],
    }, indent=2))
```

### 2.4 Playlist / channel scraping

```python
def get_playlist_entries(playlist_url: str, limit: int = 50) -> list[dict]:
    """Get metadata entries from a playlist or channel page."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "playlist_items": f"1:{limit}",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
    return result.get("entries", [])
```

### 2.5 Filtering with match_filter

```python
def search_long_videos(query: str, min_duration_sec: int = 600) -> list[dict]:
    """Search YouTube but only keep videos longer than min_duration_sec."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "match_filter": yt_dlp.utils.match_filter_func(
            f"duration >= {min_duration_sec}"
        ),
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(f"ytsearch20:{query}", download=False)
    return [e for e in result.get("entries", []) if e is not None]
```

### 2.6 Error handling pattern

```python
import yt_dlp

def safe_extract(url: str) -> dict | None:
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        print(f"[yt-dlp] Extraction failed for {url}: {e}")
        return None
    except yt_dlp.utils.ExtractorError as e:
        print(f"[yt-dlp] Extractor error for {url}: {e}")
        return None
```

---

## 3 — Key metadata fields returned

Both methods return the same underlying dict. Here are the most useful keys:

| Field | Type | Example |
|-------|------|---------|
| `id` | str | `"dQw4w9WgXcQ"` |
| `title` | str | `"Never Gonna Give You Up"` |
| `description` | str | Full description text |
| `upload_date` | str | `"20091025"` (YYYYMMDD) |
| `uploader` / `channel` | str | Channel display name |
| `channel_id` | str | `"UCuAXFkgsw1L7xaCfnd5JJOw"` |
| `duration` | int | Seconds (e.g., `212`) |
| `duration_string` | str | `"3:32"` |
| `view_count` | int | `1500000000` |
| `like_count` | int | `15000000` |
| `comment_count` | int | `3000000` |
| `categories` | list | `["Music"]` |
| `tags` | list | `["rick astley", "pop"]` |
| `thumbnail` | str | Best thumbnail URL |
| `thumbnails` | list | All thumbnail URLs + sizes |
| `webpage_url` | str | Full watch URL |
| `live_status` | str | `"not_live"`, `"is_live"`, `"was_live"` |
| `availability` | str | `"public"`, `"unlisted"`, `"needs_auth"` |

> **`extract_flat=True` caveat:** When using flat extraction (fast mode), only a subset of fields is available — typically `id`, `title`, `url`, `duration`, `view_count`, and `uploader`. Set `extract_flat=False` for the full field set (at the cost of one extra request per video).

---

## 3.5 — Quality Filtering (language, Shorts, view count)

Use these patterns when you need only substantive, English-language, non-Shorts content —
the same checks used in `yt-search.py`.

### CLI — filter during search

```bash
# English-language results only (API hint; not a guarantee — always post-filter)
yt-dlp --print "%(title)s  %(webpage_url)s  %(language)s  %(duration)s" \
       "ytsearch20:python tutorial 2025"

# Skip Shorts (duration < 120 s) using match_filter
yt-dlp -j --match-filter "duration >= 120" "ytsearch20:python tutorial 2025"

# Combine: min duration 2 min + English language tag
yt-dlp -j \
  --match-filter "duration >= 120 & language = 'en'" \
  "ytsearch20:python tutorial 2025"
```

> **Note:** `language` is often `null` on search results. Use `defaultAudioLanguage` via
> the YouTube Data API (see Python section below) for reliable language filtering.

### Python API — YouTube Data API v3 (reliable language + duration)

```python
import re, json, urllib.request, urllib.parse, os
from datetime import datetime

def duration_seconds(iso: str) -> int:
    """Parse ISO 8601 duration (PT1H30M45S) → total seconds."""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not m:
        return 0
    h, mins, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mins * 60 + s

def youtube_search_filtered(topic: str, api_key: str, max_candidates: int = 20,
                            top_n: int = 5, min_duration_sec: int = 120) -> list[dict]:
    """
    Search YouTube via Data API v3 and apply quality filters:
      - English audio language (defaultAudioLanguage / defaultLanguage starts with 'en')
      - Skip Shorts (duration < min_duration_sec, default 2 min)
      - Sort by view count, return top_n results
    """
    # 1. Search for candidate video IDs
    search_params = urllib.parse.urlencode({
        "part": "snippet",
        "q": f"{topic} tutorial {datetime.now().year}",
        "type": "video",
        "maxResults": max_candidates,
        "order": "viewCount",
        "relevanceLanguage": "en",   # hint to API — not a hard filter
        "key": api_key,
    })
    with urllib.request.urlopen(
        f"https://www.googleapis.com/youtube/v3/search?{search_params}"
    ) as r:
        ids = [i["id"]["videoId"] for i in json.load(r).get("items", [])
               if i["id"].get("videoId")]

    if not ids:
        return []

    # 2. Fetch statistics + duration + snippet in one call
    stats_params = urllib.parse.urlencode({
        "part": "statistics,contentDetails,snippet",
        "id": ",".join(ids),
        "key": api_key,
    })
    with urllib.request.urlopen(
        f"https://www.googleapis.com/youtube/v3/videos?{stats_params}"
    ) as r:
        items = json.load(r).get("items", [])

    videos = []
    for item in items:
        snippet  = item["snippet"]
        stats    = item.get("statistics", {})
        duration = item.get("contentDetails", {}).get("duration", "")

        # Language filter — prefer defaultAudioLanguage, fall back to defaultLanguage
        lang = snippet.get("defaultAudioLanguage") or snippet.get("defaultLanguage") or "en"
        if not lang.startswith("en"):
            continue

        # Shorts filter
        if duration_seconds(duration) < min_duration_sec:
            continue

        videos.append({
            "title":    snippet.get("title", ""),
            "url":      f"https://www.youtube.com/watch?v={item['id']}",
            "views":    int(stats.get("viewCount") or 0),
            "channel":  snippet.get("channelTitle", ""),
            "duration": duration,
        })

    # Sort by views, return top N
    return sorted(videos, key=lambda v: v["views"], reverse=True)[:top_n]


# Example usage
api_key = os.environ["YOUTUBE_API_KEY"]
results = youtube_search_filtered("machine learning", api_key)
for v in results:
    print(f"{v['title']}  ({v['views']:,} views)  {v['url']}")
```

**Filters applied:**

| Filter | How |
|--------|-----|
| English language | `defaultAudioLanguage` or `defaultLanguage` starts with `"en"` |
| No Shorts | `duration_seconds(duration) >= 120` (skip videos under 2 min) |
| Most viewed | `sorted(..., key=views, reverse=True)[:top_n]` |
| Year-relevant | `"tutorial {current_year}"` appended to query |

---

## 4 — Tips & Gotchas

1. **Rate limiting.** YouTube may throttle or block rapid-fire requests. Add small delays between calls in batch jobs (`time.sleep(1-3)`).
2. **Cookies for age-restricted content.** Pass `--cookies-from-browser chrome` (CLI) or `"cookiesfrombrowser": ("chrome",)` (Python) to access restricted videos.
3. **Geo-restricted videos.** Use `--geo-bypass` or set `"geo_bypass": True`.
4. **Keep yt-dlp updated.** YouTube changes its internals frequently. Run `pip install -U yt-dlp --break-system-packages` regularly.
5. **`extract_flat` is your friend.** For large playlists/channels, always start with flat extraction. Resolve individual videos only when you need full metadata.
6. **JSONL over JSON for large datasets.** One JSON object per line is easier to stream-process than one massive array.
