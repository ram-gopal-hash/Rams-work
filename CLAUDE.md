# Claude Instructions for Rams-work

## Memory — read at session start

At the start of every session, read all four memory files before responding:

```
memory/decisions.md   — key technical decisions and their rationale
memory/people.md      — who Ram is and relevant context
memory/preferences.md — how Ram likes to work
memory/user.md        — current project state, status, blockers
```

These give you the context needed to continue work without repeating prior discussions.

## Memory — update at session end

Before finishing a session (when the user is done or says goodbye), update the memory files with anything new:

- **decisions.md** — any new technical decisions or reversals
- **people.md** — new context about Ram or collaborators
- **preferences.md** — newly observed workflow preferences
- **user.md** — update current status, tick off completed items, add new blockers or files

Keep entries dated (`YYYY-MM-DD`). Append new entries; don't delete old ones unless they're superseded.

## Project context

- Repo: `/home/user/Rams-work`
- Platform: Linux server, Python 3.11, HTTP proxy active
- Active branch: `claude/add-markdown-upload-z1ZUy`
- Push with: `git push -u origin claude/add-markdown-upload-z1ZUy`

## Behavior

- Be concise. No filler.
- Present options before acting on ambiguous requests.
- Never commit secrets or API keys to git.
- Run everything from Bash tool — no separate terminal assumed.
