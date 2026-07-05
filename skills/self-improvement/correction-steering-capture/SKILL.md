---
name: correction-steering-capture
description: "Capture every user correction, steer, or cycle-waste in real-time — extract root cause, determine fix, commit change."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [self-improvement, feedback, correction, steering, agent-learning]
---

# Correction & Steering Capture

## Purpose

Every time the user has to correct you, steer your output, or you go in circles — capture that signal. Don't let it happen twice.

## Trigger Conditions

Use this skill when:
- The user corrects your output or approach
- The user says "no", "that's not what I meant", or restates their request
- You produced something that misses the mark and they redirect you
- You went in circles (multiple back-and-forth without progress)
- The user expresses frustration or impatience with direction

## Protocol

### Step 1: Capture the signal

Identify what went wrong. Ask yourself:
- Did I misread the user's intent? (→ memory: update user preference / communication style)
- Did I lack context I should have had? (→ memory: add missing context)
- Did I follow a wrong procedure? (→ skill: patch the skill or add a pitfall)
- Did I invent facts or make assumptions? (→ memory: always verify before stating)
- Did I over-engineer or write too much? (→ style adjustment)

### Step 2: Apply the fix

- **Memory**: save a durable fact or preference correction
- **Skill patch**: if a loaded skill was wrong or incomplete, call `skill_manage(action='patch')` immediately
- **Knowledge store**: for facts, entities, or context that should persist

### Step 3: Confirm with user

Briefly state what you learned and what you changed. Keep it 1-2 lines. Don't over-apologise.

Examples:
> "Noted — I was reading from outdated skill data. Patched the skill with the corrected command."
> "Right, I was guessing instead of reading the file. Added memory: always verify before proposing."
> "Caught the cycle — I was iterating on presentation when you wanted substance. Will align."

### Step 4: Check for patterns

If the same correction happens 2+ times:
- Create a new skill or update an existing one
- Add a pitfalls section to the relevant skill
- Save a memory with the correction pattern

## Example: What to capture

| Correction type | Root cause | Fix |
|---|---|---|
| "That's not what I asked" | Misread intent | Verify understanding before acting |
| "No, the other thing" | Ambiguous context | Ask clarifying question earlier |
| "We did this before" | Missed session history | Search past sessions before starting |
| "Don't write so much" | Verbose by default | Reference user conciseness preference |
| "That command is wrong" | Outdated knowledge | Patch skill / update memory |

## Pitfalls

- **Don't over-capture.** Every minor wording correction doesn't need a memory entry — only repeated patterns and significant steering events.
- **Don't apologise.** Acknowledge the correction, apply the fix, move on.
- **Don't over-engineer the capture.** 1-2 line summary of what went wrong + what you fixed is sufficient. No formal logs or databases.
- **Do not capture user's personal information** as part of correction logs — keep it to the interaction pattern, not the content.
