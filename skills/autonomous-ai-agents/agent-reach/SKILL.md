---
name: agent-reach
description: "Use when the user needs internet platform access for an agent — reading tweets, searching Reddit, watching YouTube/Bilibili, browsing XiaoHongShu/Facebook/Instagram, reading RSS, searching GitHub, or transcribing podcasts."
version: 1.0.0
author: Hermes Agent (adapted from Panniantong/Agent-Reach)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, social-media, scraping, agents, tools]
    related_skills: [scrapling, github-workflow]
---

# Agent Reach

**Give your AI Agent one-click access to the entire internet.**

Agent Reach is a capability layer that handles **selection, installation, health checks, and routing** for each platform's most reliable access path. Backends come and go; you won't notice.

- Repo: https://github.com/Panniantong/Agent-Reach
- Docs: https://github.com/Panniantong/Agent-Reach/blob/main/docs/README_en.md

## When to Use

- User asks agent to read a tweet / Twitter/X profile
- User asks agent to search Reddit or read a subreddit
- User wants YouTube video subtitles or search
- User needs Bilibili search / video detail
- User wants to read RSS/Atom feeds
- User needs GitHub repo info / search
- User wants to browse XiaoHongShu, Facebook, Instagram
- User needs web page content as clean Markdown
- User wants podcast audio transcribed
- User needs web search (semantic search via Exa)

## Installation

Copy this to the agent (Claude Code, Hermes, Cursor, etc.):

```
Install Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

Or manually:

```bash
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```

Update:

```
Update Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
```

## Capabilities

| Platform | What you can do | Setup needed |
|---|---|---|
| **Web pages** | Read any URL → clean Markdown | Zero config |
| **Twitter/X** | Read tweets, search, timeline | Cookie export |
| **Reddit** | Search, read posts & comments | OpenCLI / cookie |
| **YouTube** | Subtitles, search across 1800+ video sites | Zero config |
| **Bilibili** | Search, video detail, subtitles | Zero config |
| **GitHub** | Read repos, search code/repos | Zero config |
| **RSS/Atom** | Parse any feed | Zero config |
| **XiaoHongShu** | Read notes, search, comments | OpenCLI / MCP |
| **Facebook** | Search, profiles, feed, groups | OpenCLI |
| **Instagram** | User search, profiles, posts, explore | OpenCLI |
| **LinkedIn** | Public profiles, companies, jobs | Jina Reader |
| **V2EX** | Hot topics, node topics, user profiles | Zero config |
| **Xueqiu (雪球)** | Stock quotes, search, hot posts | Cookie |
| **Xiaoyuzhou Podcast** | Transcription | Free Groq API key |
| **Web Search** | Semantic web search | Auto-configured (Exa) |

## Diagnostics

```bash
agent-reach doctor
```

Shows what's ready, what's configurable, and how to fix it.

## Common Pitfalls

1. **Hermes agents need `exec` permission** — if using `messaging` tool profile, the agent can't run `pip install` / `agent-reach`. Ensure `coding` or equivalent profile is active.
2. **Some platforms need a logged-in session** — Reddit, Facebook, Instagram, XiaoHongShu, and LinkedIn (full profiles) require either OpenCLI or cookie export.
3. **Jina Reader rate limits** — free tier has usage limits; for heavy scraping, pair with Scrapling skill instead.
4. **Cookies stay local** — Agent Reach never uploads them. Fully open source, can be audited.
5. **Exa search needs signup** — `exa.ai` free key is auto-configured during install; if it fails, sign up manually.

## Verification Checklist

- [ ] `agent-reach doctor` shows expected channels as ✅ ready
- [ ] Twitter read works (if cookie configured)
- [ ] Web page → Markdown via Jina Reader works
- [ ] YouTube subtitles via yt-dlp work
- [ ] GitHub repo view via `gh` works
- [ ] Bilibili search works via bili-cli
- [ ] RSS feed parsing works via feedparser
- [ ] Agent has `exec`/terminal tool permission if running shell commands
