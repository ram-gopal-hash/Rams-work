# notebooklm-analysis-skill

**description:** Search YouTube for top videos on a topic, create a NotebookLM notebook,
add the videos as sources, analyze the content, and generate an output chosen by the user
(FAQ, study guide, infographic, podcast, or none). Trigger when the user asks to analyze
YouTube videos in NotebookLM, do a "YouTube to NotebookLM" pipeline, or any request
combining YouTube search with NotebookLM. Requires `YOUTUBE_API_KEY` in `.env` and
`notebooklm-mcp-cli` installed.

---

## One-time setup (Windows PowerShell)

```powershell
# 1. Install
pip install notebooklm-mcp-cli

# 2. Add nlm to PATH for this session (replace username if different)
$env:PATH += ";C:\Users\tarar\AppData\Local\Python\pythoncore-3.14-64\Scripts"

# 3. Authenticate
nlm login

# 4. Create .env with YouTube API key
'YOUTUBE_API_KEY=your_key_here' | Out-File -FilePath 'C:\Users\tarar\Rams-work\.env' -Encoding utf8
```

To make PATH permanent (so you never need step 2 again):
```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Users\tarar\AppData\Local\Python\pythoncore-3.14-64\Scripts", "User")
```

---

## Auth troubleshooting

If `nlm notebook list` says "Authentication expired" even after `nlm login`:
```powershell
nlm login --clear
nlm login
nlm notebook list   # verify it shows your notebooks before proceeding
```

---

## Step 1 — Search YouTube

```powershell
cd C:\Users\tarar\Rams-work
python yt-search.py "<topic>"
```

Output: JSON array of top 5 videos. Note the `url` values — needed for step 3.

---

## Step 2 — Create notebook

```powershell
nlm notebook create "<topic> Analysis"
```

Output: `✓ Created notebook: ... ID: <notebook_id>`

Save the notebook ID — used in every step below.

---

## Step 3 — Add YouTube sources

Run one command per video URL (replace `<notebook_id>` and each `<url>`):

```powershell
nlm source add <notebook_id> --youtube "<url1>"
nlm source add <notebook_id> --youtube "<url2>"
nlm source add <notebook_id> --youtube "<url3>"
nlm source add <notebook_id> --youtube "<url4>"
nlm source add <notebook_id> --youtube "<url5>"
```

Wait for all to succeed before continuing. If a source fails, skip it and continue.

---

## Step 4 — Analyze top skills

```powershell
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

```powershell
nlm query notebook <notebook_id> "Generate a comprehensive FAQ based on all the video sources. Format each entry as: Q: [question] / A: [answer]. Cover the most common beginner and intermediate questions about <topic>."
```

Save the answer to a file:
```powershell
# After running the query, save manually or pipe output
nlm query notebook <notebook_id> "Generate a FAQ..." | Out-File "<topic>-faq.md" -Encoding utf8
```

---

### Option 2 — Study guide

```powershell
nlm query notebook <notebook_id> "Create a structured study guide for <topic> based on all video sources. Include: key concepts with definitions, common patterns and techniques, recommended learning order, and practical tips."
```

---

### Option 3 — Infographic

```powershell
nlm infographic create <notebook_id> --style sketch-note --wait
```

Then download:
```powershell
nlm download <notebook_id> --type infographic --output "<topic>-infographic.png"
```

---

### Option 4 — Podcast (Audio Overview)

```powershell
nlm audio create <notebook_id> --wait
```

Then download:
```powershell
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
