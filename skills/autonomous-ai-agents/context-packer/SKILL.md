---
name: context-packer
description: "Repo pruner for local model agents — 2,521 files become 8 that matter. Stops agents drowning in node_modules. Token-budgeted, priority-scored, noise-filtered."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [context, local-model, token-optimization, pre-cron, pruning]
---

# Context Packer — Compact Repo Context for Local Models

## When to use
- As a pre-cron script for any job using a local model
- When local agents with 40K token windows drown in full repo dumps
- Before delegating a coding task to a local agent

## Usage

### As pre-cron script (stdout → injected into prompt)
```
# In cron job config:
script: context_packer.py /path/to/project
```

### CLI
```
python3 ~/.hermes/scripts/context_packer.py /path/to/project
python3 ~/.hermes/scripts/context_packer.py /path/to/project --max-chars 80000
python3 ~/.hermes/scripts/context_packer.py /path/to/project --stats
python3 ~/.hermes/scripts/context_packer.py /path/to/project --json
```

## What it does
1. Collects all signal files (`.md`, `.py`, `.ts`, `.tsx`, `.json`, `.yaml`, `.toml`, etc.)
2. Prunes ONLY specific noise dirs: `node_modules`, `__pycache__`, `dist`, `lib`, `build`, `.foundry`, `.pytest_cache`, `.venv`, `venv`, `.cache`, `.tox`, `.mypy_cache`, `.ruff_cache`, `coverage` — NOT all dot-directories (`.github/`, `.vscode/` etc. are preserved since they carry CI config and settings)
3. Excludes: `.git` (via dir prune), `package-lock.json`, `*.map`, `*.d.ts`, huge files (>500KB)
4. Prioritizes: AGENTS.md, ARCHITECTURE.md, CLAUDE.md, README.md (score 0)
5. Sorts by priority + recency
6. Outputs markdown with full priority files + previews of key sources + file listing

## Pitfalls
- Budget is soft — output may slightly exceed max_chars. Budget is checked per-section, not globally. For strict budgets, add a global counter that stops adding sections entirely when exceeded.
- Test files in test/ dirs are deprioritized but not excluded
- Priority scoring weights MD/docs heavily; adjust `get_file_priority()` for project-specific needs
- Previously pruned ALL dot-directories (including `.github/`, `.vscode/`). Fixed to only prune NOISE_DIRS.
- `.git` directory is pruned but `.github/`, `.vscode/`, etc. are NOT — these contain CI workflows, settings, and config that agents may need
