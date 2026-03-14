# notebooklm Installation

## Recommended: notebooklm-mcp-cli (unified package)

Installs both the CLI (`nlm`) and the MCP server (`notebooklm-mcp`) in one step.
Enables Claude Code to control NotebookLM directly via 35 MCP tools — no subprocess calls needed.

```bash
pip install notebooklm-mcp-cli

# One-time MCP registration with Claude Code
nlm setup add claude-code

# Authenticate (opens browser)
nlm login
```

Reference: https://github.com/jacob-bd/notebooklm-mcp-cli

---

## Legacy: notebooklm-py (standalone Python library)

Use this if you need the Python library directly without MCP integration.

## Basic installation

```bash
pip install notebooklm-py
```

## With browser login support (required for first-time setup)

```bash
pip install "notebooklm-py[browser]"
playwright install chromium
```

## Development install (latest from GitHub)

```bash
pip install git+https://github.com/teng-lin/notebooklm-py@main
```

## Authentication

```bash
notebooklm login

# For organizations requiring Microsoft Edge:
notebooklm login --browser msedge
```
