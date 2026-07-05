---
name: hermes-skillopt
description: "Automated skill optimizer — tests, scores, and improves Hermes skills against ground truth using a three-model evaluation loop."
version: 2.2.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [optimization, self-improvement, skills, automation, testing, evaluation]
---

# Hermes SkillOpt — Continuous Skill Improvement

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Optimizer Loop                         │
│                                                          │
│  1. SELECT   → Pick a skill with evaluator criteria     │
│  2. BASELINE → Run N test cases through the skill       │
│                Score the agent's performance             │
│  3. PROPOSE  → Optimizer model analyzes failures         │
│                and proposes edits to the skill file      │
│  4. RE-EVAL  → Run same test cases against new skill    │
│  5. COMPARE  → Accept if improvement, reject if not     │
│  6. COMMIT   → Patch the skill + log history            │
│  7. CYCLE    → Repeat for next skill in rotation        │
└─────────────────────────────────────────────────────────┘
```

**Three-model design:**
- **Worker model** — runs the test cases, generates responses following the skill
- **Evaluator model** — semantically judges whether each expected/forbidden behavior was met in the agent's response
- **Optimizer model** — analyzes failure patterns, proposes specific edits to the skill file

All three use the same API key (DeepSeek recommended). The script auto-loads the key from environment variable or `~/.hermes/.env`.

## Skill Evaluators

Each optimizable skill needs an evaluator: a JSON file at `~/.hermes/skillopt/evaluators/<skill-name>.json` that defines:

```json
{
  "skill_name": "my-skill",
  "description": "What this skill does",
  "test_cases": [
    {
      "id": "no-fix-without-root-cause",
      "task": "You see a bug: a user's login fails intermittently. Your job is to debug it.",
      "expected_behaviors": [
        {"criterion": "Does NOT propose a fix before completing investigation", "weight": 2},
        {"criterion": "Identifies reproduction steps, affected components, failure mode", "weight": 1},
        {"criterion": "Does NOT guess the cause without evidence", "weight": 1.5}
      ],
      "forbidden_behaviors": [
        "Proposes a fix without completing investigation",
        "Says 'just add logging' as the only debugging step"
      ]
    }
  ],
  "pass_threshold": 0.7
}
```

## The Optimizer Script

Located at `scripts/skillopt_optimizer.py` (bundled with this skill). Copy it to your Hermes scripts directory:

```bash
cp scripts/skillopt_optimizer.py ~/.hermes/scripts/
```

### What it does each cycle:

1. **Pick a skill** — reads `~/.hermes/skillopt/rotation.json` to know which skill to optimize today
2. **Load evaluator** — reads the evaluator JSON for that skill
3. **Run baseline** — for each test case, generates a response from a fresh agent session following the current skill, then scores it
4. **Generate diagnosis** — passes failures + the skill file to the optimizer model and asks for proposed edits
5. **Apply edits to a copy** — writes a candidate skill file
6. **Re-evaluate** — runs the same test cases through the candidate skill
7. **Compare scores** — if candidate >= baseline + threshold, commit the edit
8. **Log** — records the cycle outcome in `~/.hermes/skillopt/history.jsonl`
9. **Advance rotation** — moves to the next skill

### Scoring System

Each test case is scored by a separate evaluator call. The evaluator receives:
- The expected behaviors (with weights)
- The forbidden behaviors
- The agent's raw response

It returns a JSON object with per-criterion pass/fail judgments + an overall 0.0–1.0 score.
Forbidden behaviors incur a -0.15 penalty each if present.

Final score = `mean(test_case_scores)` with forbidden penalties applied.
Improvement threshold: candidate score must be ≥ baseline score + 0.05 (5% minimum lift).

## Setup

### 1. Create directories and files

```bash
mkdir -p ~/.hermes/skillopt/evaluators ~/.hermes/scripts

# Copy the optimizer engine
cp scripts/skillopt_optimizer.py ~/.hermes/scripts/
```

### 2. Create rotation config

```json
{
  "skills": [
    {"name": "my-skill", "evaluator": "my-skill.json"}
  ],
  "current_index": 0,
  "last_optimized": null
}
```

Save to `~/.hermes/skillopt/rotation.json`.

### 3. Create an evaluator for each skill

In `~/.hermes/skillopt/evaluators/`. See the example above.

### 4. Verify

```bash
python3 ~/.hermes/scripts/skillopt_optimizer.py --dry-run --status
python3 ~/.hermes/scripts/skillopt_optimizer.py --dry-run
```

### 5. Schedule the cron

```bash
hermes cron create "0 6 * * 1,3,5" --name "SkillOpt Optimizer" \
  --prompt "Run the Hermes SkillOpt optimizer. Load hermes-skillopt skill and execute one optimization cycle." \
  --skill hermes-skillopt
```

This runs every Mon/Wed/Fri at 6am, optimizing one skill per run.

## Files

```
~/.hermes/skillopt/
├── evaluators/              # JSON evaluator files (one per skill)
├── rotation.json            # Which skills to optimize + current index
├── history.jsonl            # Every cycle outcome (accept/reject/skip)
└── backups/                 # Timestamped skill backups before commit
~/.hermes/scripts/
└── skillopt_optimizer.py    # The engine
```

## Diagnostics

### Low skill name → score determinism

Test scores fluctuate between runs for the same skill (the worker LLM is stochastic). Compare baseline vs candidate scores from the **same run**, not against historical baselines. Relative improvement within one run is the valid signal.

### Worker model naturally fails certain evaluators

If tests that require explicit step labeling score 0.000 while the model actually performs the behaviour, update evaluator criteria to be **behaviour-based** rather than label-based. Verify the actual response rather than checking for section headers.

## Pitfalls

- **Candidate re-eval MUST use a temp file** — the worker reads the skill file from disk. Passing the original `skill_path` reads the original skill, making baseline and candidate identical.
- **Edit placement needs section-anchored matching** — the optimizer returns `location` as prose like "near ## The Iron Law section". Always pre-process to find `##`-prefixed section headers as anchor points first; fall back to words >4 chars.
- **Better test case quality** produces meaningful optimizations. Each test case should have clearly verifiable expected behaviors, not subjective opinions.
- **Optimizer hallucination** — the optimizer model may propose edits that look good but don't actually improve performance. The re-evaluation step is essential — never trust proposed edits without verification.
- **Skill drift** — repeated optimizations can gradually change the skill's original purpose. The rotation should revisit older skills periodically to check for drift.
- **Small test suites** — 2-3 test cases per skill is enough for a cycle. More than 5 and the token cost becomes prohibitive.
- **Skills unsuitable for optimization**: creative skills (no ground truth), content generation (subjective quality), anything requiring external API calls (unreproducible). Stick to skills with clear right/wrong outcomes.
- **`execute_code` blocked in cron context** — the sandboxed Python executor is blocked for cron jobs (run without user approval). The optimizer script must use `terminal()` for subprocess calls instead of `execute_code()`.
- **API key loading** — the script checks `$DEEPSEEK_API_KEY` env var first, then `~/.hermes/.env`. If the `.env` file has a redacted key (`***sanitized***`), the script treats it as missing and falls back to simulation.
- **Worker model may produce tool-call syntax** — the evaluator handles this correctly (semantic evaluation), but keyword-based scoring would miss it entirely. Always use semantic evaluation.
