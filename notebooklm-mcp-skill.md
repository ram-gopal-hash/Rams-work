# notebooklm-analysis-skill

**description:** Search YouTube for top videos on a topic, create a NotebookLM notebook, add the videos as sources, ask for a skills analysis, and optionally generate an output (infographic, podcast, FAQ, study guide, or none). Use this skill when the user asks to analyze YouTube videos in NotebookLM, do a "YouTube to NotebookLM" pipeline, generate a NotebookLM skill analysis, or any request combining YouTube search with NotebookLM. Requires `YOUTUBE_API_KEY` env var and `notebooklm-mcp-cli` MCP server registered in Claude Code.

---

## Prerequisites (one-time setup)

```bash
# YouTube API key
export YOUTUBE_API_KEY="your_key_here"

# Install MCP CLI and register with Claude Code
pip install notebooklm-mcp-cli
nlm setup add claude-code

# Authenticate NotebookLM (opens browser)
nlm login
```

---

## Steps (execute in order, using MCP tools for steps 2–6)

### Step 1 — Search YouTube

Run the search script and parse the JSON output:

```bash
python yt-search.py "<topic>"
```

The script prints a JSON array of objects with these fields:
`title`, `url`, `views`, `channel`, `duration`

Extract the list of `url` values for the next steps.

---

### Step 2 — Create NotebookLM notebook

Use MCP tool to create a new notebook named `"<topic> Analysis"`.
Save the returned notebook ID for subsequent steps.

---

### Step 3 — Add YouTube sources

For each of the 5 video URLs from Step 1, use the MCP tool to add it as a YouTube source to the notebook.

Wait for all sources to be fully indexed before proceeding to Step 4.

---

### Step 4 — Analyze top skills

Use the MCP query tool to ask the notebook:

> "Based on all these videos, what are the top `<topic>` skills being taught?
> List them by frequency and importance, with a brief description of each skill."

Print the full response for the user.

---

### Step 5 — Choose output (ask the user if not already specified)

If the user has not stated what they want as output, ask:

> "What would you like NotebookLM to generate from these videos?"
> 1. **Infographic** — sketch-note style visual summary (PNG file)
> 2. **Podcast** — Audio Overview (MP3 conversational summary)
> 3. **FAQ** — Frequently Asked Questions document
> 4. **Study guide** — structured notes with key concepts and definitions
> 5. **None** — just leave the notebook with sources loaded for manual exploration

Then proceed based on their choice:

#### Option 1 — Infographic

Use the MCP tool to generate a sketch-note style infographic.
Use `--wait` / wait-for-completion mode and retry up to 3 times if rate limited.
Download with the MCP tool and save as `./<topic-slug>-infographic.png`.

#### Option 2 — Podcast (Audio Overview)

Use the MCP tool to trigger Audio Overview generation on the notebook.
Poll for completion, then download the MP3 as `./<topic-slug>-podcast.mp3`.

#### Option 3 — FAQ

Use the MCP query tool with the prompt:
> "Generate a comprehensive FAQ based on all the video sources.
> Format as: Q: [question] / A: [answer]. Cover the most common beginner and intermediate questions about `<topic>`."

Print the FAQ and optionally save to `./<topic-slug>-faq.md`.

#### Option 4 — Study guide

Use the MCP query tool with the prompt:
> "Create a structured study guide for `<topic>` based on all video sources.
> Include: key concepts with definitions, common patterns/techniques, recommended learning order, and practical tips."

Print the study guide and optionally save to `./<topic-slug>-study-guide.md`.

#### Option 5 — None

Skip generation. Report the notebook name and ID so the user can open it in NotebookLM directly.

---

## Notes

- The MCP server exposes 35 NotebookLM tools. Disable `@notebooklm-mcp` when not in use to preserve context.
- If infographic generation fails (rate limited), the notebook ID was already created — re-run just steps 5–6 later using the saved notebook ID.
- MCP reference: https://github.com/jacob-bd/notebooklm-mcp-cli
