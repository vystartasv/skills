---
name: git-housekeeping
description: "Clean, shrink, and maintain git repos — identify bloat, strip large files from history with filter-repo, manage .gitignore for backup repos."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, filter-repo, repo-maintenance, cleanup, bloat]
---

# Git Housekeeping

Cleans bloated git repos — especially backup/disaster-recovery repos that accumulate large files through periodic syncs.

## When to use

- User asks "why is my git repo so large?" or "can we shrink git history?"
- A backup/sync repo keeps growing
- User wants to add excludes to keep future syncs lean
- A database or sessions DB is being accidentally synced to git

## Investigation

```bash
# Check overall repo size
du -sh .

# Check git history size
du -sh .git/objects

# List largest blobs in git history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objectname) %(objecttype) %(objectsize) %(rest)' | \
  awk '/^[^ ]+ blob [0-9]/ {print $3, $4}' | \
  sort -rn | head -30

# Check what's tracked in working tree
git ls-files '*.tar.gz' '*.tgz' '*.zip' '*.pdf'
```

## Shrinking history with git-filter-repo

**Prerequisite:** `brew install git-filter-repo`

### 1. Backup the mirror first

```bash
cd /path/to/repo
git clone --mirror . /tmp/repo-backup
```

### 2. Strip files/directories from ALL history

```bash
git filter-repo \
  --path path/to/bloated/dir/ \
  --path path/to/large/file.pdf \
  --invert-paths \
  --force
```

### 3. Re-add the remote (filter-repo removes it)

```bash
git remote add origin git@github.com:user/repo.git
```

### 4. Force push

```bash
git push origin main --force
```

## Security scrubbing with replace-text

### Create patterns file

Format: `<OLD_TEXT==>NEW_TEXT>` — one per line.

```bash
cat > /tmp/scrub-patterns.txt << 'EOF'
192.168.1.1==>INTERNAL_IP
user@example.com==>agent@example.com
/Users/username/projects==>PROJECT_ROOT
internal.domain.com==>EXAMPLE.COM
EOF
```

### Remove files AND replace text in one run

```bash
git filter-repo \
  --path secrets.md --invert-paths \
  --replace-text /tmp/scrub-patterns.txt \
  --force
```

## Preventing future bloat

### Update .gitignore

```gitignore
# Large bloat from syncs
*.tar.gz
*.zip
*.db
```

### Update sync scripts

Wire rsync excludes:

```bash
BLOAT_EXCLUDES="--exclude=*.tar.gz --exclude=*.zip --exclude=*.db"
rsync -a --delete $BLOAT_EXCLUDES "$SRC/" "$REPO/"
```

## Pitfalls

- **git-filter-repo removes the `origin` remote** — must re-add before pushing.
- **--force push required** after filter-repo since history is rewritten. Notify collaborators.
- **filter-repo rewrites ALL commits** — even a single-file removal touches every commit that referenced it.
- **Do not use `git filter-branch`** — it's deprecated. Use `git-filter-repo`.
- **Backup mirror is essential** — if filter-repo deletes something you wanted, restore from backup.
- **Never commit SQLite DBs or session dumps** to git repos. Add them to .gitignore.
