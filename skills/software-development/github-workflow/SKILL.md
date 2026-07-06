---
name: github-workflow
description: "Complete GitHub operations — authentication setup, issues management, pull request lifecycle, code review, and repository management. Covers both gh CLI and git+curl fallbacks."
version: 1.1.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, git, pull-request, issues, ci]
---

# GitHub Workflow

Class-level umbrella for all GitHub operations. Each section has subsections.

## Auth Detection

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\\n\\r')
    fi
  fi
fi
```

## Section A: Issues Management

### Common Actions

| Action | gh | curl |
|--------|-----|------|
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| View issue | `gh issue view N` | `GET /repos/{o}/{r}/issues/N` |
| Create issue | `gh issue create --title "..." --body "..."` | `POST /repos/{o}/{r}/issues` |
| Add labels | `gh issue edit N --add-label "bug"` | `POST /repos/{o}/{r}/issues/N/labels` |
| Comment | `gh issue comment N --body "..."` | `POST /repos/{o}/{r}/issues/N/comments` |
| Close | `gh issue close N` | `PATCH /repos/{o}/{r}/issues/N` |

### Bulk File-from-Disk Pattern

1. Write each issue as `.github/issues/NN-description.md` with `# Title` as first line
2. Commit and push
3. Create issues from them

```bash
for f in .github/issues/*.md; do
  title=$(head -1 "$f" | sed 's/^# //')
  gh issue create --title "$title" --body-file "$f"
done
```

## Section B: Pull Request Workflow

### Branch Naming

`feat/description`, `fix/description`, `refactor/description`, `docs/description`, `ci/description`

### Conventional Commits

```
type(scope): short description
```
Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

### Create PR

| With gh | `gh pr create --title "feat: ..." --body "..."` |
|---------|-----|
| With curl | `curl POST /repos/{o}/{r}/pulls -d '{"head":"branch","base":"main"}'` |

### CI Monitoring & Auto-Fix

```bash
gh pr checks                # Quick status
gh pr checks --watch        # Poll until done
```

Auto-fix loop: check CI → read logs → fix → commit → push → re-check (max 3 attempts).

### Merge

Basic: `gh pr merge --squash --delete-branch`

**Pitfall — PRs with `.github/workflows/` changes:** If the PR modifies workflow files, `gh pr merge` may fail without `workflow` scope. Use local squash-merge + SSH push instead:

```bash
gh pr checkout N
git checkout main
git merge --squash <pr-branch>
git commit -m "feat: description (#N)"
git remote set-url origin git@github.com:owner/repo.git
git push origin main
```

## Section C: Code Review

```bash
git diff main...HEAD --stat          # Scope
git diff main...HEAD                 # Full diff
git diff main...HEAD -- src/file.py  # File-by-file

# Check for issues
git diff main...HEAD | grep -n "print(\\|TODO\\|FIXME\\|debugger"
git diff main...HEAD | grep -in "password\\|secret\\|api_key"
```

### PR Review

```bash
gh pr view N && gh pr diff N
gh pr checkout N
gh pr review N --approve --body "LGTM!"
```

### Review Checklist

- Correctness: edge cases, error paths, data flow
- Security: secrets, injection, input validation
- Code Quality: naming, DRY, single responsibility
- Testing: happy path + error cases covered
- Performance: no N+1 queries, no blocking in async

## Section D: Repository Management

| Action | gh | curl |
|--------|-----|------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create (user) | `gh repo create name --public --clone` | `POST /user/repos` |
| Create (org) | `gh repo create org/repo --public` | `POST /orgs/org/repos` |
| Fork | `gh repo fork o/r --clone` | `POST /repos/o/r/forks` |
| Edit settings | `gh repo edit --description "..."` | `PATCH /repos/o/r` |
| Create release | `gh release create v1.0 --generate-notes` | `POST /repos/o/r/releases` |
| Set secret | `gh secret set KEY --body "val"` | `PUT /repos/o/r/actions/secrets/KEY` |

## Section E: External Contributor Onboarding

When a first-time external contributor submits a PR:
1. Review the change
2. Decide: merge, request changes, or close with explanation
3. Thank the contributor
4. Point to next steps or related issues

## Pitfalls

- **PR comment shell escape**: Always use `--body-file` for complex markdown content.
- **Fork PR head format**: `your-username:your-branch` for `--head`.
- **Labels must exist before `gh issue create --label`**.
- **Workflow scope** needed for `gh pr merge` on PRs with workflow changes.
- **`gh pr merge` on workflow PRs** — use local squash-merge instead.
