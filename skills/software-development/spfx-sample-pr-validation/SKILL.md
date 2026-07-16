---
name: spfx-sample-pr-validation
description: >-
  Validation checklist for SPFx sample PRs submitted to
  pnp/sp-dev-fx-webparts (and similar PnP sample repos). 
  Covers the 10 automated validation criteria the GitHub Actions bot
  checks, plus the lesser-known formatting requirements.
version: 1.0.0
tags: [spfx, pnp, samples, pr, validation, contribute]
---

# SPFx Sample PR Validation

When submitting a new SPFx sample to `pnp/sp-dev-fx-webparts`, the repo's
automated validation bot checks 10 criteria. Any ⚠️ warning must be fixed
before the sample maintainer will merge.

## The 10 validation criteria

| # | Check | Requirement |
|---|-------|-------------|
| 1 | Affects only one folder | PR must change files in exactly one `samples/<name>/` folder |
| 2 | Folder naming convention | `react-<descriptive-name>` or `angular-<name>`, lowercase with hyphens |
| 3 | README.md contains visitor stat image | **Must use `<img>` HTML tag**, NOT Markdown `![alt](url)` syntax |
| 4 | .nvmrc file exists | Pin Node.js version (e.g. `v22.14.0`) |
| 5 | README.md exists | Complete, not the default scaffold template |
| 6 | screenshot.png in assets/ folder | `assets/screenshot.png` must exist (even if placeholder) |
| 7 | No .sppkg file | Source code only — no packages |
| 8 | No node_modules/ folder | Already excluded by .gitignore, but validate |
| 9 | No lib/ folder | Already excluded by .gitignore, but validate |
| 10 | No upgrade reports | No `upgrade-report.md` or similar |

## Critical formatting details

### ❌ Will fail: Markdown image syntax

```markdown
![Visitor count](https://m365-visitor-stats.azurewebsites.net/sp-dev-fx-webparts/samples/react-mcp-client)
```

### ✅ Will pass: HTML `<img>` tag

```html
<img src="https://m365-visitor-stats.azurewebsites.net/sp-dev-fx-webparts/samples/react-mcp-client" />
```

The validation regex looks for `<img` tags specifically. Do NOT use Markdown
image syntax for the visitor stats badge.

### .nvmrc format

```
v22.14.0
```

Just the version string with `v` prefix, newline at end.

### README must not be the default template

The SPFx scaffolder generates a README with placeholder text like
`[picture of the solution in action, if possible]` and
`CopilotAgent description`. This template **will not pass validation**.

Minimum required sections:
- Title (H1)
- Summary paragraph
- Prerequisites
- This sample illustrates... / Features
- Compatibility table (SPFx version, Node.js, SharePoint)
- Contributors
- Version history
- Disclaimer
- Minimal Path to Awesome (clone, install, serve)

## Screenshot

The validation requires `assets/screenshot.png` to exist. A real screenshot
of the web part in action is preferred, but a placeholder PNG will pass
validation. Create a real screenshot before the PR is reviewed.

## After fixing

The validation bot re-runs automatically. Push new commits, or comment on
the PR to trigger re-validation.

```bash
# Comment on PR to kick re-validation
gh pr comment <N> --repo pnp/sp-dev-fx-webparts --body "Addressed validation warnings"

# Or push a new commit, which also triggers re-validation
```

Wait for the second bot comment. If it says ✅ success instead of ⚠️ warnings,
the PR is ready for maintainer review.

## Related skills

- `open-source-pr-submission` — general OSS PR process
- `github-workflow` — gh CLI operations
- `sharepoint-ecosystem` — navigating SharePoint/PnP repos