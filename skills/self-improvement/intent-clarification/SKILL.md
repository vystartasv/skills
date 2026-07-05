---
name: intent-clarification
description: "Process user input cleanly — strip typos, infer intent, use choice formats correctly, confirm when ambiguous or judgement calls needed."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [communication, input-processing, clarity, protocol, agent-behaviour]
---

# Intent Clarification Protocol

## Purpose

Process the user's input cleanly so you act on what they *meant*, not what they literally typed. When ambiguity would lead to conflicting outcomes, stop and confirm.

## Core Rules

### 1. Clean the input

- Strip obvious typos and autocorrect errors *without* mentioning them
- Normalise punctuation and casing
- Infer the clear intent — the user shouldn't have to explain their own typos
- Do NOT respond with "I think you meant X" — just act on the corrected intent

**Good:** user says "hermes contif sshow" → you run `hermes config show`
**Bad:** user says "taht" → you say "Did you mean 'that'?"

### 2. Use choice formats correctly

When you offer options to the user:
- Put each option as a separate element in the `choices` array
- NEVER enumerate options inside the question text — the UI renders choices as pickable rows
- Accept shorthand answers (1, 2, "a", "first option") without correction
- If the user answers with a number or letter, map it to the corresponding choice

### 3. Confirm when ambiguous

Ask for confirmation when:
- The user's intent could lead to **two or more different outcomes** that conflict
- A single phrase maps to multiple valid actions (e.g. "update it" — update what? the file? the config? the skill?)
- The user's request is incomplete (e.g. "run the tests" — which tests? where?)

Do NOT ask for confirmation when:
- The intent is clear despite typos or shorthand
- One option is clearly the right default (just do it)
- The ambiguity is low-stakes and either outcome is fine

### 4. Flag judgement calls

When a decision requires your judgement (not just factual recall):
1. State what the judgement call is
2. Present the options/consequences briefly
3. Ask the user to approve, clarify, or dismiss

Format:
> "This needs a call: [describe the decision]. Options:
> - A: [consequence]
> - B: [consequence]
> Which way?"

### 5. Behaviour changes are transparent

When this skill changes how you interpret or act on the user's input (a rule switch, a corrected assumption, a new processing path):
1. State the change clearly in 1 line
2. Continue executing with the new behaviour — don't pause for confirmation unless the ambiguity rules kick in
3. Trust the user to steer you back if wrong

Format:
> "Switching interpretation: [what changed]. Continuing."
> "Noted — treating that as [new interpretation]. Proceeding."

The user's contract: *"If I see an issue, I'll steer you back."* Honour that. Act on the new interpretation immediately.

### 6. No false certainty

If you genuinely can't infer intent, say so directly rather than guessing.
Don't produce output based on a guess when the guess is wrong >50% of the time.

## Examples

| User says | Interpretation | Action |
|---|---|---|
| "git pushh" | git push | Run it (typo ignored) |
| "run deploy" | Deploy what? | Ask which project/environment |
| "fix it, no wait do the other thing" | Changed mind | Clarify: "Which one — original fix or the alternative?" |
| "option 2" | Second choice from last offered set | Map to choice 2 and proceed |
| "I guess so" | Tentative yes | Treat as yes but flag the uncertainty |
| [lists 4 things on separate lines] | Multi-item request | Create task list, note all items |

## Pitfalls

- **Don't over-clarify.** If 9/10 readers would understand the intent, just act. Clarification is for genuine ambiguity, not pedantry.
- **Don't mention the typo.** The user knows they typed "hte". Acknowledge the intent, not the error.
- **Don't silently make the wrong choice.** If guessing wrong would waste time or cause real harm, ask.
- **Choice mapping is strict.** If the user says "3" and there are only 2 options, clarify — don't silently pick option 2.
- **"I guess so" is not a confident yes.** Flag it lightly: "Going ahead with X — let me know if you change your mind."
