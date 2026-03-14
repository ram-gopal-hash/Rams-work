# notebooklm-analysis-skill

**description:** Search YouTube for top videos on a topic, create a NotebookLM notebook,
add the videos as sources, analyze the content, and generate an output chosen by the user
(FAQ, study guide, infographic, podcast, or none). Trigger when the user asks to analyze
YouTube videos in NotebookLM, do a "YouTube to NotebookLM" pipeline, or any request
combining YouTube search with NotebookLM. Requires `YOUTUBE_API_KEY` in `.env`,
`notebooklm-mcp-cli` installed, and `nlm` authenticated.

---

## One-time `nlm` auth on Linux

`nlm login` needs a real browser — on Linux use **manual cookie export** instead:

1. Open `https://notebooklm.google.com` in your browser (already logged in)
2. Press **F12** → Network tab → reload the page
3. Right-click **any request** to `notebooklm.google.com` → **Copy as cURL**
4. Paste that cURL command in the Claude Code chat
5. Claude will write it to `/tmp/nlm-curl.txt` and run:

```bash
nlm login --manual --file /tmp/nlm-curl.txt
nlm notebook list   # verify it shows your notebooks
rm /tmp/nlm-curl.txt
```

Auth troubleshooting — if `nlm notebook list` says "Authentication expired":
```bash
nlm login --clear
# then repeat the cURL export steps above
```

---

## One-time YouTube API key setup

YouTube Data API v3 is required (free, 10,000 queries/day quota).

```bash
echo "YOUTUBE_API_KEY=your_key_here" >> /home/user/Rams-work/.env
```

Get a key: https://console.cloud.google.com/apis/library/youtube.googleapis.com

---

## Step 1 — Search YouTube

```bash
cd /home/user/Rams-work
python yt-search.py "<topic>"
```

Uses YouTube Data API v3 — returns top 5 videos by view count, English, no Shorts.
Output: JSON array with `title`, `url`, `views`, `channel`, `duration`.

---

## Step 2 — Create notebook

```bash
nlm notebook create "<topic> Analysis"
```

Output: `✓ Created notebook: ... ID: <notebook_id>`

Save the notebook ID — used in every step below.

---

## Step 3 — Add YouTube sources

Run one command per video URL (replace `<notebook_id>` and each `<url>`):

```bash
nlm source add <notebook_id> --youtube "<url1>"
nlm source add <notebook_id> --youtube "<url2>"
nlm source add <notebook_id> --youtube "<url3>"
nlm source add <notebook_id> --youtube "<url4>"
nlm source add <notebook_id> --youtube "<url5>"
```

Wait for all to succeed before continuing. If a source fails, skip it and continue.

---

## Step 4 — Analyze top skills

```bash
nlm query notebook <notebook_id> "Based on all these videos, what are the top <topic> skills being taught? List them by frequency and importance, with a brief description of each skill."
```

Parse and display only the `answer` field from the JSON response.

---

## Step 5 — Choose output

Ask the user:
> "What would you like to generate from this notebook?"
> 1. FAQ
> 2. Study guide
> 3. Infographic
> 4. Podcast (Audio Overview)
> 5. Nothing — leave notebook open for manual use

Then run the matching command below.

---

### Option 1 — FAQ

```bash
nlm query notebook <notebook_id> "Generate a comprehensive FAQ based on all the video sources. Format each entry as: Q: [question] / A: [answer]. Cover the most common beginner and intermediate questions about <topic>."
```

---

### Option 2 — Study guide

```bash
nlm query notebook <notebook_id> "Create a structured study guide for <topic> based on all video sources. Include: key concepts with definitions, common patterns and techniques, recommended learning order, and practical tips."
```

---

### Option 3 — Infographic

```bash
nlm infographic create <notebook_id> --style sketch-note --wait
nlm download <notebook_id> --type infographic --output "<topic>-infographic.png"
```

---

### Option 4 — Podcast (Audio Overview)

```bash
nlm audio create <notebook_id> --wait
nlm download <notebook_id> --type audio --output "<topic>-podcast.mp3"
```

---

### Option 5 — Nothing

Report: "Notebook '<topic> Analysis' is ready. Open it at https://notebooklm.google.com"
Notebook ID: `<notebook_id>`

---

## Notes

- Always verify `nlm notebook list` works before starting — confirms auth is valid
- The `nlm query notebook` response is JSON; extract only the `answer` field to show the user
- `yt-search.py` prints status to stderr and JSON to stdout — only stdout is the data
- Sources take 30–60 seconds to index after adding; if query returns thin results, wait and retry
- If all Invidious instances fail, check https://api.invidious.io/instances.json for a live one
