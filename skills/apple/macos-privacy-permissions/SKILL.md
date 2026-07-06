---
name: macos-privacy-permissions
description: "Grant macOS Privacy & Security permissions (Full Disk Access, Files & Folders, Accessibility, etc.) to Python binaries, Homebrew tools, and other command-line programs via System Settings or TCC."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [macos, permissions, tcc, privacy, security]
---

# macOS Privacy & Security Permissions

On macOS, command-line tools (Python, rsync, ffmpeg, etc.) can't access protected paths like `~/Desktop`, `~/Documents`, `~/Downloads`, `~/Library/Application Support`, or external volumes without being explicitly granted permission via System Settings → Privacy & Security.

## When to load

- User says "grant disk access", "needs permission", "operation not permitted"
- A Python or CLI tool gets `Permission denied` accessing `~/Desktop`, `~/Documents`, `~/Library`, `/Volumes/`
- User just installed a new Python version and it has no TCC permissions
- User wants to check which Python binaries have what permissions

## Quick check: current TCC state

```bash
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client, service, auth_value FROM access WHERE client LIKE '%python%'" 2>&1
```

`auth_value = 2` = allowed, `auth_value = 0` = denied, `auth_value = 5` = limited.

## Types of permissions

| Permission | Covers | Use case |
|---|---|---|
| **Full Disk Access** | Desktop, Documents, Downloads, ~/Library, external volumes | Scripts that back up files, index media, manage photos |
| **Files & Folders** | Desktop, Documents, Downloads individually | Scoped access |
| **Accessibility** | Control other apps via CGEvent/CoreGraphics | Automation scripts |
| **Automation** | Control other specific apps | AppleScript workflows |

## Granting Full Disk Access (most common)

### 1. Open the settings pane

```bash
open 'x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles'
```

### 2. Guide the user

1. Click the **+** (padlock to unlock if greyed out)
2. Navigate to the actual Python/CLI **binary** (not a symlink)
3. Select it → **Open**

### Finding the real binary path

Homebrew Python:
```bash
REAL=$(realpath /opt/homebrew/bin/python3)
echo $REAL
# Example: /opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/bin/python3.14
```

uv-managed Python:
```bash
which python3 && realpath $(which python3)
# Example: ~/.local/share/uv/python/cpython-3.14.X-macos-aarch64-none/bin/python3.14
```

**Key**: Always use the realpath, not the symlink. TCC records the real binary path.

### 3. Verify it worked

```bash
python3 -c "
import os
desktop = os.path.expanduser('~/Desktop')
print(f'Desktop: {len(os.listdir(desktop))} items')
print('Full Disk Access confirmed')
"
```

## Multiple Python binaries

Each Python version needs its own TCC entry. Add them one at a time.

## Pitfalls

- **Symlinks don't work**: TCC records the realpath. Always navigate to the real binary.
- **No programmatic grant**: macOS does not allow programmatic TCC grant. The user MUST interact with System Settings GUI.
- **Each version is separate**: Python 3.11 permissions do NOT carry over to 3.12, 3.13, etc.
- **TCC is process-based**: Reinstalling Python means re-granting.
- **`tccutil reset`**: Resets ALL permissions for ALL apps. Use only as last resort.
- **macOS Sonoma+** has stricter TCC enforcement — may need to restart processes after granting.
