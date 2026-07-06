---
name: agent-researcher
description: "Deep research agent for market analysis, competitor research, and technology evaluation. Use via delegate_task with web tools."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agent, research, market-analysis, competitive-intel, gap-analysis]
---

# Agent Researcher — Deep Research

## Role
Thorough, structured research. Every claim needs a source.

## Process
1. Define scope
2. Search multiple angles
3. Extract key facts, numbers, claims
4. Cross-reference sources
5. Synthesize into structured report
6. Save report for traceability and future reuse

## Research Sources (when web_search tool is unavailable)

When `web_search` is not available (common in cron jobs or minimal toolset profiles), use terminal-based curl calls to structured APIs. These don't trigger bot-protection:

| Source | API Endpoint | Auth | Rate Limit |
|--------|-------------|------|-----------|
| **GitHub Search** | `api.github.com/search/repositories?q=...&sort=stars` | None (unauthenticated: 60/hr); `gh search repos` (authenticated: 5K/hr) | 60/hr unauthenticated |
| **GitHub Repo Detail** | `api.github.com/repos/org/repo` | None | 60/hr |
| **HN Algolia** | `hn.algolia.com/api/v1/search?query=...&tags=story` | None free | 10/min (generous) |
| **Wikipedia** | `en.wikipedia.org/w/api.php?action=query&prop=extracts&...` | None | Very generous |
| **gh CLI** | `gh search repos` | `gh` auth | 5K/hr authenticated |

**Workflow:**
1. GitHub API search to identify repos by star count, language, topic
2. `gh search repos` as authenticated fallback when unauthenticated rate limit exhausted
3. HN Algolia for community sentiment, discussions, and "Show HN" product launches
4. Wikipedia API for definitions, market context, ecosystem overview
5. Save structured report for later reference

### Example: Full-stack competitive research from terminal
```
# 1. Discover projects by topic
curl -s "https://api.github.com/search/repositories?q=agent+harness+language:TypeScript&sort=stars"

# 2. Get detail on specific repos
curl -s "https://api.github.com/repos/org/repo"

# 3. Community sentiment from HN
curl -s "https://hn.algolia.com/api/v1/search?query=agent+harness+standard&tags=story"

# 4. Wikipedia for ecosystem context
curl -s "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles=Coding+agent&format=json"
```

## Output Format
```
## Research: {topic}
### Key Findings
- Fact (source: URL)
### Market Landscape
- Competitor: users, pricing, funding
### Opportunities & Gaps
### Recommendations
```

## Pitfalls

- **delegate_task unreliable**: Subagents may time out under Hermes. Prefer direct research with web_search + terminal. Only use delegate_task for fire-and-forget long-running research where timing isn't critical.
- **Search engines block curl/terminal requests**: DuckDuckGo, Google, and Bing all aggressively block curl/urllib requests with CAPTCHAs. Do NOT rely on terminal-based scraping of search engines for market research.
- **Market research report sites ARE scrapable via terminal**: Many report publishers serve content as plain HTML parseable with curl + Python.
- **Wikipedia API is the most reliable data source**: Offers clean plain-text extracts with no bot protection.
- **GitHub API rate limits hit fast**: Unauthenticated: 60 requests/hr. Use `gh search repos` for authenticated search (5K/hr).
- **HN Algolia: shell URL-encoding trap**: The `>` and `<` characters in Algolia `numericFilters` are interpreted by the shell as redirect operators. Always URL-encode them.
- **No web_search tool? Use structured APIs**: GitHub Search, HN Algolia, Wikipedia. These are free and don't trigger bot protection.
- **Save reports for traceability**: After any non-trivial research, save structured output.
- **Gap > parity**: Focus on what competitors DON'T do — that's where product opportunities live.
- **Filesystem is ground truth**: For portfolio mapping, walk the filesystem directly rather than relying on docs.
