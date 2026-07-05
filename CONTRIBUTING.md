# Contributing

This repo publishes skills for [Hermes Agent](https://github.com/NousResearch/hermes-agent). Anyone can propose skills, improvements, or fixes.

## Repo structure

```
skills/
├── <category>/
│   ├── DESCRIPTION.md          # Category description (YAML frontmatter)
│   ├── <skill-name>/
│   │   ├── SKILL.md            # Main skill file (required)
│   │   ├── scripts/            # Executable scripts the skill references
│   │   ├── references/         # Supporting docs
│   │   └── templates/          # Templates the skill uses
```

## Adding a skill

### 1. Choose or create a category

Categories group related skills. Existing ones: `self-improvement`, `software-development`, `research`, `devops`, etc. If none fits, add a new one with a `DESCRIPTION.md`:

```yaml
---
description: What this category contains.
---
```

### 2. Write SKILL.md

Format:

```yaml
---
name: your-skill-name
description: "One-line what this skill does."
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [relevant, tags, here]
---

# Skill Title

## Purpose

What this skill helps the agent do. 2-3 sentences.

## Trigger Conditions

When should the agent load or use this skill?

## Protocol

Step-by-step instructions. Be specific enough that an LLM agent can follow them without guessing.

## Pitfalls

Common mistakes, edge cases, and anti-patterns.
```

Requirements:
- `name` must match the directory name (lowercase, hyphens)
- `description` must be meaningful (one line, not empty)
- `author` — your name or handle

### 3. Bundle dependencies

If the skill references scripts, include them under `scripts/`. Reference them in SKILL.md with instructions to copy or symlink.

### 4. Make it universal

Skills should work for **any Hermes user**, not just you:
- Use `~/.hermes/` paths (Hermes convention)
- No personal cron job IDs, file paths, or account references
- Examples use generic placeholders, not project-specific names
- Avoid hardcoded API keys or tokens
- If a setup step is OS-specific, note it in the Pitfalls section

## Review checklist

Before submitting a PR:

- [ ] `SKILL.md` exists with valid YAML frontmatter
- [ ] `description` is meaningful
- [ ] No personal/private references in examples or paths
- [ ] No hardcoded secrets, tokens, or API keys
- [ ] Script dependencies are bundled or have clear install instructions
- [ ] Category `DESCRIPTION.md` exists if using a new category
- [ ] Pitfalls section covers known edge cases

## PR process

1. Fork this repo
2. Add or update skills in your fork
3. Open a PR with a summary of what changed and why
4. A maintainer will review within a few days
