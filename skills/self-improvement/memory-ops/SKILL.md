---
name: memory-ops
description: "Interactive memory search and management — list all instances of a category, confirm correctness, edit, or delete entries."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, search, management, interactive]
---

# memory-ops: Interactive Memory Search & Management

## When to load

When the user wants to:
- Search their memory and **interact with results** (not just read)
- See **all instances** of a category
- **Confirm** a memory entry is correct
- **Edit** or **Delete** specific entries
- Review what's stored about a topic

## Three memory stores

Before searching, identify WHICH store the user wants:

### 1. Active memory (context)
**Injected into your system prompt every turn.** Parse directly from context.

- **List all entries**: Read the MEMORY and USER PROFILE sections visible in your system prompt. Present each as a numbered item.
- **View a specific entry**: The full text is already in context — just quote it.
- **Edit**: Use `memory(action='replace', target=..., old_text='unique substring', content='new text')`
- **Delete**: Use `memory(action='remove', target=..., old_text='unique substring')`

### 2. Knowledge base
Persistent semantic store.

- **List categories**: Use the knowledge tool's browse/list functions to see the hierarchy
- **Search**: Use semantic search
- **Read details**: Retrieve at overview level, then offer full if needed
- **Edit**: Read full content → present → delete old + store corrected version
- **Delete**: Browse to find URI → delete

### 3. Session history
Past conversations. Use `session_search`.

- **Search**: `session_search(query)` → shows matching sessions with bookends
- **Scroll**: `session_search(session_id=..., around_message_id=...)` to dive deeper
- No edit/delete — sessions are immutable logs.

## Interactive workflows

### Workflow A: List all instances of a type

Present as numbered choice list:

```
User: "show all my project memories"
Agent: *determines store → reads/parses → presents numbered list*
       [1] Project Alpha v0.1.0
       [2] Project Beta config
       [3] ...
       Reply with number to view, d<N> to delete
```

### Workflow B: Confirm an entry is correct

```
User: "check if my project info is right"
Agent: *reads entry, presents it*
       "Your entry says: ...
       Reply ✅ to confirm correct, or type correction."
User: "✅"
Agent: "Confirmed ✓"
```

### Workflow C: Edit an entry

```
Agent: "Current entry: [text]. What should it say instead?"
User: provides new text
Agent: *memory(action='replace', ...)*
       "Updated ✓"
```

### Workflow D: Delete an entry

```
Agent: shows entry → "Reply 'y' to delete, anything else to cancel."
User: "y"
Agent: *deletes*
       "Deleted ✓"
```

## Safety rules

1. **Always confirm before delete** — show the content, ask for explicit confirmation.
2. **Show before edit** — always show the current text before replacing it.
3. **Use unique identifiers** for replacements.
4. **Knowledge base deletes are permanent** — warn the user.
5. **Never delete session history** — sessions are immutable.
