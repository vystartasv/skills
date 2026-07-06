---
name: macos-python-homebrew
description: "Manage Python installations on macOS via Homebrew — check versions, remove old ones, migrate dependents, fix PATH priority."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [python, homebrew, macos, development, environment]
---

# macOS Python via Homebrew

Manage Python versions installed via Homebrew on macOS. Covers version inventory, safe removal of old versions, migrating formula/cask dependents to the current Python, and ensuring the Homebrew Python is the default on the shell PATH.

## When to use

- User asks "can we remove old Python versions?"
- Upgrading python@3.x and cleaning up the previous major version
- `python3 --version` shows Apple's system Python (3.9.x) instead of Homebrew's modern Python
- A formula or cask needs its Python dependency updated to the current version

## Steps

### 1. Inventory installed Python versions

```sh
brew list --versions | grep python
```

### 2. Check dependents before removing

```sh
brew uses --installed python@3.X
```

- **No output** = nothing depends on it → safe to remove.
- **List of formulas/casks** = those depend on that Python version.

### 3. Removing a Python version

**No dependents** — straight removal:
```sh
brew remove python@3.X
```

**Has dependents** — two approaches:

#### A. Reinstall the dependent against the current Python (preferred)

For **formulae**, patch the formula's `depends_on 'python@3.X'` line to the current version, then reinstall.

For **casks**, create a local tap override with the modified dependency.

#### B. Keep both versions (fallback)

If the formula/cask hardcodes the Python version, accept the old Python stays.

### 4. Remove the old Python

```sh
brew remove python@3.X
```

### 5. Fix PATH so Homebrew Python is default

On Apple Silicon Macs, prepend `/opt/homebrew/bin` to PATH in `~/.zshrc`:

```sh
export PATH="/opt/homebrew/bin:$PATH"
```

**Verification:**
```sh
echo 'export PATH="/opt/homebrew/bin:$PATH"; which python3; python3 --version' | zsh
```

Expected: `/opt/homebrew/bin/python3` with a recent Python version.

### 6. Verify migrated tools work

- **CLI tools**: run `--version` or `--help`
- **gcloud**: `gcloud --version`
- **Scripts using `#!/usr/bin/env python3`**: check they resolve to the right binary

## Pitfalls

- **Cask override maintenance**: A local cask override must be manually updated when the cask's version changes.
- **Homebrew auto-removes python@3.X when its last dependent is removed.** Removing a formula may also remove Python.
- **TCC permissions don't survive upgrades**: Granting permissions to `/opt/homebrew/bin/python3.X` doesn't carry over to `python3.Y`. Grant to the opt path instead.
- **`brew uses --installed` shows direct deps only**: A formula depending on `python@3` (not `python@3.X`) may not show up. Use `brew deps --tree <formula>` for the full picture.
- **System Python is needed by macOS**: Never remove `/usr/bin/python3` — it breaks system tools.
