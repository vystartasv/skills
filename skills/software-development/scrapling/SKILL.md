---
name: scrapling
description: "Scrape any website using Scrapling — a Python library with anti-bot bypass (Cloudflare Turnstile), stealth headless browsing, adaptive parser, spiders framework, CLI, and MCP server."
version: "0.4.9"
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [scraping, web, anti-bot, cloudflare-bypass, mcp]
---

# Scrapling Hermes Skill

Scrapling is installed via `uv tool install "scrapling[all]"`. The CLI binary `scrapling` is at `~/.local/bin/scrapling`.

## Architecture — three tiers of fetching

| Tier | Tool | Use when | Speed |
|---|---|---|---|
| HTTP | `Fetcher.get()` / `scrapling extract get` | Static pages, APIs, no bot protection | Fastest |
| Browser | `DynamicFetcher.fetch()` / `scrapling extract fetch` | SPAs, JS-rendered content, dynamic pages | Medium |
| Stealth | `StealthyFetcher.fetch()` / `scrapling extract stealthy-fetch` | Cloudflare Turnstile, anti-bot, WAF | Same as browser |

**Rule:** Start with `get`. If blocked/empty → `fetch`. If still blocked → `stealthy-fetch`.

## CLI Usage (no Python code needed)

```bash
# Static page → Markdown (best for docs, articles)
scrapling extract get "https://example.com" /tmp/page.md

# JS-rendered page
scrapling extract fetch "https://example.com" /tmp/page.md

# Anti-bot protected page
scrapling extract stealthy-fetch "https://example.com" /tmp/page.md

# Extract only a specific section with CSS selector (saves tokens)
scrapling extract get "https://example.com" /tmp/page.md -s "article.main-content"

# POST request
scrapling extract post "https://api.example.com" /tmp/result.md \
  --data '{"query":"test"}' --headers '{"Content-Type":"application/json"}'
```

Key CLI flags:
- `-s, --css-selector` — narrow to specific elements (huge token savings)
- `--headless` / `--no-headless` — visible browser mode for debugging
- `--real-chrome` — use your Chrome install instead of bundled Chromium
- `--solve-cloudflare` — auto-solve Turnstile/interstitial (stealthy-fetch only)
- `--network-idle` — wait for all network requests to settle
- `--proxy "http://user:pass@host:port"` — proxy support
- `--ai-targeted` — add prompt injection protection + ad blocking

## MCP Server — universal (any language client)

Scrapling ships a native MCP server. Start it and any MCP client (Claude Desktop, VS Code, etc.) can use it:

```bash
scrapling mcp                         # stdio transport (default)
scrapling mcp --http --port 8000      # Streamable HTTP transport
```

The server exposes **10 tools**: `get`, `bulk_get`, `fetch`, `bulk_fetch`, `stealthy_fetch`, `bulk_stealthy_fetch`, `open_session`, `close_session`, `list_sessions`, `screenshot`.

To configure it as a Hermes MCP server, add to your `.hermes/config.yaml`:

```yaml
mcp_servers:
  scrapling:
    command: scrapling
    args: [mcp]
```

## Decision Tree

```
Site has anti-bot (Cloudflare Turnstile)?
  → StealthyFetcher / stealthy-fetch CLI / MCP stealthy_fetch

Site is SPA / JS-rendered?
  → DynamicFetcher / fetch CLI / MCP fetch

Static page, no protection?
  → Fetcher.get() / get CLI / MCP get

Need multiple pages from same site?
  → session-based fetcher or spider

Need data from any language (Rust, JS, Go, etc.)?
  → Start the MCP server and connect from that language's MCP client
```

## Pitfalls

1. **uv tool vs uv run mismatch**: `scrapling` installed via `uv tool install` uses a specific Python. If you `uv run` it with a different Python, dependencies may be missing. Always use `scrapling` CLI directly.
2. **No Python code in this skill**: This skill uses the CLI and MCP server only. For Python scripting, use `execute_code` with `uv tool run --from scrapling python3`.
3. **Adaptive mode**: Must set `StealthyFetcher.adaptive = True` before fetching. The `auto_save=True` flag is silently ignored otherwise.
4. **Resource heavy**: Browser-based fetchers launch a Chromium instance. For light scraping, always start with `get`.
5. **Proxy auth**: Use dict format for browser fetchers; string URL format for HTTP fetchers.
