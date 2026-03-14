# notebooklm Installation

## Recommended: notebooklm-mcp-cli (unified package)

Installs both the CLI (`nlm`) and the MCP server (`notebooklm-mcp`) in one step.

```powershell
pip install notebooklm-mcp-cli
```

Reference: https://github.com/jacob-bd/notebooklm-mcp-cli

### Fix PATH on Windows (required after install)

The `nlm` command is installed but not on PATH by default. Fix for current session:

```powershell
$env:PATH += ";C:\Users\tarar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
```

Fix permanently (run once, then restart PowerShell):

```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Users\tarar\AppData\Local\Python\pythoncore-3.14-64\Scripts", "User")
```

### Authenticate

```powershell
nlm login
```

Opens Google Chrome to sign in. Credentials saved to `~\.notebooklm-mcp-cli\profiles\default`.

### Auth troubleshooting

If commands fail with "Authentication expired" immediately after login:

```powershell
nlm login --clear
nlm login
nlm notebook list   # verify this shows notebooks before proceeding
```

### MCP setup (optional — only if Claude Code CLI is installed)

```powershell
nlm setup add claude-code
```

If Claude Code CLI is not installed, manually create `C:\Users\tarar\.claude\settings.json`:

```json
{"mcpServers": {"notebooklm-mcp": {"command": "notebooklm-mcp"}}}
```

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
