---
name: fact-checking
description: "Verify factual claims from forwarded messages, social media posts, articles, or user assertions by cross-referencing against primary sources via web investigation."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [fact-checking, verification, research, source-triangulation]
---

# Fact-Checking Protocol

## Why this exists
When the user shares claims from forwarded messages, quotes, article excerpts, or social media posts, a systematic verification approach is needed — especially when `web_search` tool is unavailable and you must rely on direct HTTP scraping and source triangulation.

## Workflow

### 1. Extract all verifiable claims

Parse every factual assertion from the source text:
- **Names** (people, companies, products) — note them exactly as written, then probe for spelling variation
- **Numbers** (users, revenue, dates, percentages, view counts)
- **Background claims** (education, military service, employment history, affiliation)
- **Core theses / arguments** attributed to the source
- **Client/customer claims** (case studies, testimonials)

### 2. Primary source triangulation

For each claim, find the closest primary source:

| Source type | Method |
|---|---|
| **YouTube video** | Scrape video page for `shortDescription` and `ownerChannelName` |
| **Company website** | Scrape `/about`, homepage, footer (legal entity name) |
| **Personal site / portfolio** | Bio pages, education/experience sections |
| **LinkedIn** | Google-cached profile (direct scrape usually blocked by authwall) |
| **Twitter/X** | Profile bio for quick background check |

### 3. Cross-reference each claim

| Verdict | Criteria |
|---|---|
| ✅ Confirmed | Found verbatim or equivalent in primary source |
| ❌ Minor error | Spelling variation, close but not exact |
| ⚠️ Partially confirmed | Gist is right but details differ |
| ❓ Unverifiable | No primary source accessible |
| ❌ False | Contradicted by primary source |

### 4. Write the report

Structure as a clear verdict list with:
1. **Each claim** quoted from the original
2. **Verdict emoji** (✅ ❌ ⚠️ ❓)
3. **Primary source quote** showing evidence
4. **URL citation** so the user can verify independently
5. **Distinguish substance errors from transcription/typo errors**

## Pitfalls

- **Spelling errors in the original claim are the #1 blocker.** Try phonetic variants, common misspellings, and partial matches.
- **Company brand names ≠ legal entity names.** Check the footer for the official registered name.
- **Video descriptions contain the full context** — the `shortDescription` field in YouTube HTML has the complete description.
- **macOS uses BSD grep, not GNU grep.** `grep -P` does NOT work. Use `python3 -c` with `re` module.
- **`execute_code` blocks network calls.** Do NOT use it for web scraping — use `terminal()` with curl.
- **Search engines are aggressively blocked.** After 1-2 failed searches, switch to direct source scraping.
- **Source self-reporting is not independent verification.** Label self-claims as self-reported.
- **Distinguish between the user's framing and the source's actual claims.**
