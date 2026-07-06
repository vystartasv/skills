---
name: repo-docs
description: "Standard open-source repo documentation templates — README, CONTRIBUTING, CHANGELOG, CODE_OF_CONDUCT, SECURITY, LICENSE. Apply to any new or existing project repo."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentation, open-source, templates, repo-setup, onboarding]
---

# Repo Documentation Templates

Creates and maintains the standard set of documentation files every open-source repo should have.
Load this skill, then apply the templates to the target repo.

## Files to Create

1. **README.md** — Project overview, Summary, Who it's for/NOT, Quick Start, License
2. **CONTRIBUTING.md** — Dev setup, PR workflow, code style, testing requirements
3. **CHANGELOG.md** — Keep a Changelog format, linked to GitHub releases
4. **CODE_OF_CONDUCT.md** — Contributor Covenant 2.1
5. **SECURITY.md** — How to report vulnerabilities, supported versions
6. **LICENSE** — MIT (default, unless user specifies otherwise)

## README Structure

The standard README follows this structure:

```
# Project Name
One-line tagline.

## Summary (2-3 paragraphs, plain English, no code)

## Who it's for (4 bullet scenarios)

## Who it's NOT for (4 bullet anti-scenarios)

## Install

## Quick Start

## [Optional: Architecture / Security / FAQ sections]

## License
```

Rules:
- **No ELI5 sections** in production READMEs. Write for adults who aren't technical.
- Summary answers "what problem does this solve?" without mentioning code, APIs, or implementation.
- Who it's for / Who it's NOT for are equally important — prevents wasted time.
- Quick Start must work with copy-paste. Include actual commands that run.

## CHANGELOG Structure

- Keep a Changelog format (https://keepachangelog.com)
- Sections: Added, Changed, Fixed, Removed
- Linked to git tags / GitHub releases

## Workflow

1. Check which files already exist in the repo (`ls *.md`)
2. Create missing files from templates
3. Populate project-specific details: name, install command, quick start, repo URL
4. Commit all new files in a single commit: `docs: add standard repo documentation`
5. Push

## Pitfalls

- Don't add ELI5 sections. They're patronizing for production repos.
- Don't copy-paste template verbatim without filling in project-specific details.
- Don't add AUTHORS file unless there are multiple contributors. Use `git shortlog -sn` instead.
- If the repo already has some files, only add missing ones — don't replace without asking.
