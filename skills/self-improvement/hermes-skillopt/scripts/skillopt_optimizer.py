#!/usr/bin/env python3.11
"""
SkillOpt Optimizer — automated skill improvement loop for Hermes Agent.

Performs one optimization cycle per run:
1. Select next skill from rotation
2. Run baseline tests through the skill
3. Score the baseline
4. Propose edits via optimizer model
5. Apply edits to a candidate skill file
6. Re-evaluate against same tests
7. Accept/reject based on score improvement
8. Commit (patch the real skill) or discard
9. Log the outcome
10. Advance rotation

Usage:
    python3.11 skillopt_optimizer.py                # Full cycle
    python3.11 skillopt_optimizer.py --dry-run      # Report only, no commits
    python3.11 skillopt_optimizer.py --skill TDD    # Override skill
    python3.11 skillopt_optimizer.py --status       # Show rotation state

Environment:
    - DEEPSEEK_API_KEY required (for both models)
    - RUNS inside the Hermes agent context in cron mode
    - Can also run standalone for testing
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

def _get_deepseek_key():
    """Get DeepSeek API key from env or .hermes/.env file."""
    key = os.getenv("DEEPSEEK_API_KEY")
    if key and not key.startswith("***") and len(key) > 10:
        return key
    # Try loading from .env file
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip("\"'")
                    if val and not val.startswith("***") and len(val) > 10:
                        return val
    return None


DEEPSEEK_API_KEY = _get_deepseek_key()

SKILLOPT_DIR = Path.home() / ".hermes" / "skillopt"
EVALUATORS_DIR = SKILLOPT_DIR / "evaluators"
ROTATION_FILE = SKILLOPT_DIR / "rotation.json"
HISTORY_FILE = SKILLOPT_DIR / "history.jsonl"
BACKUP_DIR = SKILLOPT_DIR / "backups"

SKILLS_DIR = Path.home() / ".hermes" / "skills"

# ── Helpers ────────────────────────────────────────────────────────────────


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def log_history(entry):
    SKILLOPT_DIR.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_rotation():
    if ROTATION_FILE.exists():
        return load_json(ROTATION_FILE)
    return {"skills": [], "current_index": 0, "last_optimized": None}


def save_rotation(rot):
    save_json(ROTATION_FILE, rot)


def get_current_skill_file(skill_name):
    """Find the SKILL.md for a given skill name across all categories."""
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            # Check if this directory's name matches, or if any parent matches
            # We match by the skill's directory name (the slug)
            skill_dir = os.path.basename(root)
            if skill_dir == skill_name:
                return os.path.join(root, "SKILL.md")
    return None


def backup_skill(skill_path):
    """Create a timestamped backup before modifying."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    skill_name = Path(skill_path).parent.name
    backup_path = BACKUP_DIR / f"{skill_name}_{ts}.md"
    import shutil
    shutil.copy2(skill_path, backup_path)
    return backup_path


# ── Scoring ────────────────────────────────────────────────────────────────


def score_response(response_text, test_case):
    """Score an agent's response against a test case's expected/forbidden behaviors.
    Uses semantic evaluation (DeepSeek) when available, falls back to keyword matching."""
    if DEEPSEEK_API_KEY:
        return _score_semantic(response_text, test_case)
    else:
        return _score_keyword(response_text, test_case)


def _score_semantic(response_text, test_case):
    """Score a response using DeepSeek for semantic evaluation."""
    criteria_text = "\n".join(
        f"- [{b.get('weight', 1.0)}x] {b['criterion']}"
        for b in test_case.get("expected_behaviors", [])
    )
    forbidden_text = "\n".join(
        f"- {b}" for b in test_case.get("forbidden_behaviors", [])
    )

    eval_prompt = (
        "You are a rigorous evaluator of AI agent behavior. Score how well the "
        "agent's response meets each expected behavior.\n\n"
        f"## Expected behaviors (with weights):\n{criteria_text}\n\n"
        f"## Forbidden behaviors (penalize if present):\n{forbidden_text}\n\n"
        "## Agent's response:\n"
        f"{response_text}\n\n"
        "Return ONLY a JSON object:\n"
        '```json\n{"behavior_scores": [{"criterion": "...", "pass": true/false, "rationale": "..."}], '
        '"forbidden_violations": [{"behavior": "...", "present": true/false}], '
        '"overall_score": 0.0-1.0}\n```\n'
        "Pass = agent demonstrated the behavior. For forbidden behaviors, present=true = agent did it (penalize)."
    )

    import urllib.request
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a precise agent behavior evaluator. Return only JSON."},
            {"role": "user", "content": eval_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
    }).encode()

    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
            content = body["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"\n  ⚠ Evaluator API call failed: {e}")
        return _score_keyword(response_text, test_case)

    # Extract JSON
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].strip() if content.count("```") >= 2 else content

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"\n  ⚠ Failed to parse evaluator output: {e}")
        return _score_keyword(response_text, test_case)

    # Build score dict
    expected = result.get("behavior_scores", [])
    forbidden = result.get("forbidden_violations", [])
    overall = result.get("overall_score", 0.0)

    passed = sum(1 for b in expected if b.get("pass"))
    failed = sum(1 for b in expected if not b.get("pass"))

    # Apply forbidden penalties
    forbidden_count = sum(1 for f in forbidden if f.get("present"))
    penalty = forbidden_count * 0.15
    final_score = max(0.0, overall - penalty)

    details = []
    for b in expected:
        status = "✓" if b.get("pass") else "✗"
        details.append(f"{status} {b['criterion'][:70]} — {b.get('rationale', '')[:50]}")

    for f in forbidden:
        if f.get("present"):
            details.append(f"⚠ FORBIDDEN: {f['behavior'][:60]}")

    return {
        "test_case_id": test_case["id"],
        "score": round(final_score, 3),
        "passed": passed,
        "failed": failed + forbidden_count,
        "details": details,
        "eval_method": "semantic",
    }


def _score_keyword(response_text, test_case):
    text_lower = response_text.lower()
    total_weight = 0.0
    earned_weight = 0.0
    passed = []
    failed = []
    details = []

    for b in test_case.get("expected_behaviors", []):
        criterion = b["criterion"]
        weight = b.get("weight", 1.0)
        total_weight += weight

        # Simple keyword matching — semantic eval would be better
        keywords = _extract_keywords(criterion)
        match_count = sum(1 for kw in keywords if kw in text_lower)
        threshold = max(1, len(keywords) * 0.5)  # at least half of keywords

        if match_count >= threshold:
            earned_weight += weight
            passed.append({"criterion": criterion, "score": match_count / max(len(keywords), 1)})
            details.append(f"✓ {criterion[:60]}...")
        else:
            failed.append({"criterion": criterion, "match_count": match_count, "needed": threshold})
            details.append(f"✗ {criterion[:60]}... ({match_count}/{threshold} keywords)")

    # Check forbidden behaviors
    for fb in test_case.get("forbidden_behaviors", []):
        fb_keywords = _extract_keywords(fb)
        fb_matches = sum(1 for kw in fb_keywords if kw in text_lower)
        if fb_matches >= max(1, len(fb_keywords) * 0.4):
            # Subtle penalty for forbidden behavior
            penalty = 0.3 * max(1, len(fb_keywords) * 0.1)
            earned_weight -= penalty
            failed.append({"criterion": f"FORBIDDEN: {fb}", "penalty": penalty})
            details.append(f"⚠ FORBIDDEN: {fb[:60]}...")

    raw_score = earned_weight / max(total_weight, 0.01)
    final_score = max(0.0, raw_score)

    return {
        "test_case_id": test_case["id"],
        "score": round(final_score, 3),
        "passed": len(passed),
        "failed": len(failed),
        "total_weight": total_weight,
        "earned_weight": round(earned_weight, 2),
        "details": details,
    }


def _extract_keywords(text):
    """Extract meaningful keywords from a criterion/behavior string."""
    # Remove common stopwords and split
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "and", "or", "not", "no", "nor", "but",
        "if", "then", "else", "when", "where", "why", "how", "all",
        "each", "every", "both", "few", "more", "most", "other", "some",
        "such", "only", "own", "same", "so", "than", "too", "very",
        "just", "because", "about", "up", "out", "off", "over", "it",
        "its", "that", "this", "these", "those", "what", "which", "who",
        "whom", "whose", "doesn", "don", "didn", "won", "wouldn",
        "shouldn", "couldn", "isn", "aren", "wasn", "weren", "hasn",
        "haven", "hadn", "needn", "dare", "ought", "used", "doing",
        "doesnot", "donot", "didnot", "willnot", "wouldnot", "shouldnot",
        "step", "first", "then", "next", "before", "after",
    }
    words = text.lower().split()
    return [w.strip(".,!?;:'\"()[]{}-_") for w in words
            if w.strip(".,!?;:'\"()[]{}-_") not in stopwords
            and len(w.strip(".,!?;:'\"()[]{}-_")) > 2]


# ── Agent interaction (simulated for dry-run) ─────────────────────────────


def call_agent_with_skill(skill_file, task, model="deepseek-chat"):
    """Call the worker model with the skill file as context.
    Returns the agent's response text."""
    if not DEEPSEEK_API_KEY:
        print("\n  ⚠ DEEPSEEK_API_KEY not available, using simulated response")
        return simulate_agent_response_fallback(Path(skill_file).parent.name, task)

    with open(skill_file) as f:
        skill_content = f.read()

    # Build a prompt that asks the model to follow the skill
    system_prompt = (
        "You are an AI agent executing a task. You have been given a SKILL.md file "
        "that defines how you should work. Follow its instructions precisely.\n\n"
        f"## Your Skill File\n\n```markdown\n{skill_content}\n```"
    )

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    }).encode()

    import urllib.request
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read())
            return body["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"\n  ⚠ API call failed: {e}")
        return simulate_agent_response_fallback(Path(skill_file).parent.name, task)


def simulate_agent_response_fallback(skill_name, task):
    """Used when API is unavailable."""
    if "systematic-debugging" in skill_name:
        return (
            "Let me investigate this systematically.\n\n"
            "**Phase 1: Reproduce**\nI need to understand exactly what happens. "
            "What environment is this on? What exact input triggers it? "
            "What's the expected vs actual behavior?\n\n"
            "**Phase 2: Isolate**\nPossible causes to check:\n"
            "1. Network latency issue\n"
            "2. Database query timeout\n"
            "3. Race condition in async code\n"
            "4. Configuration difference between environments\n\n"
            "**Phase 3: Root cause**\nAfter checking each: the issue is in the "
            "database connection pool exhausting under load.\n\n"
            "**Phase 4: Fix**\nIncrease pool size from 10 to 25. "
            "Verify by running the load test that reproduces the issue."
        )
    elif "test-driven-development" in skill_name:
        return (
            "Following TDD:\n\n"
            "**RED:** First, I'll write a failing test:\n"
            '```python\ndef test_email_validation():'
            '\n    assert is_valid_email("user@example.com") == True'
            '\n    assert is_valid_email("not-an-email") == False'
            '\n    assert is_valid_email("") == False\n```\n\n'
            "This test should fail because the function doesn't exist yet.\n\n"
            "**GREEN:** Now minimal implementation:\n"
            '```python\ndef is_valid_email(email):'
            '\n    return "@" in email and "." in email'
            '\n```\n\n'
            "**REFACTOR:** Could add more edge cases, but keep it minimal for now."
        )
    return "Following the skill guidelines. Investigating systematically and then implementing."


def simulate_agent_response(skill_file, task):
    """Run the agent against a task using a skill file.
    In live mode: calls the DeepSeek flash model with the skill as context.
    In dry-run: returns simulated response."""
    return call_agent_with_skill(skill_file, task, model="deepseek-chat")


# ── Optimizer (generates proposed edits) ───────────────────────────────────


def generate_optimization_prompt(skill_content, failures, evaluator):
    """Build a prompt for the optimizer model."""
    prompt_parts = [
        "You are a skill optimization expert. Your job is to improve an AI agent's skill document "
        "based on observed failure patterns.\n\n",
        f"## Current Skill File\n\n```markdown\n{skill_content}\n```\n\n",
        "## Test Results\n\nThe agent failed these test cases:\n\n",
    ]

    for f in failures[:3]:  # Limit to top 3 failures
        prompt_parts.append(f"### Test: {f['test_case_id']}\n")
        prompt_parts.append(f"Score: {f['score']}\n")
        for detail in f.get("details", []):
            if detail.startswith("✗") or detail.startswith("⚠"):
                prompt_parts.append(f"- {detail}\n")
        prompt_parts.append("\n")

    prompt_parts.append(
        "\n## Instructions\n\n"
        "Propose 1-3 specific edits to the skill document that would help the agent "
        "pass more of the expected behaviors. Each edit must be:\n"
        "1. **Specific** — exact text to add, remove, or modify\n"
        "2. **Testable** — the edit should make a concrete behavioral difference\n"
        "3. **Minimal** — tiny changes, not rewrites\n\n"
        "Format your response as a JSON array:\n"
        '```json\n[{"action": "add|modify|remove", "location": "near text ...", '
        '"new_text": "...", "rationale": "..."}]\n```\n\n'
        "Return ONLY the JSON array, no other text."
    )

    return "".join(prompt_parts)


def propose_edits(skill_content, failures, evaluator, dry_run=False):
    """Propose edits using the optimizer model."""
    return _call_optimizer_model(generate_optimization_prompt(skill_content, failures, evaluator))


def _call_optimizer_model(prompt):
    """Call the optimizer model (deepseek-v4-pro) via API.
    Parses JSON array of edits from the response."""
    if not DEEPSEEK_API_KEY:
        print("  ⚠ DEEPSEEK_API_KEY not available, skipping optimizer")
        return []

    import urllib.request
    import urllib.error

    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a precise skill optimization engine. Return ONLY a JSON array of edits."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    }).encode()

    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
            content = body["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ⚠ Optimizer API call failed: {e}")
        return []

    # Extract JSON array from model output (may be wrapped in ```json ... ```)
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].strip() if content.count("```") >= 2 else content

    try:
        edits = json.loads(content)
        if isinstance(edits, list):
            return edits
        else:
            print("  ⚠ Optimizer returned non-list JSON")
            return []
    except json.JSONDecodeError as e:
        print(f"  ⚠ Failed to parse optimizer response as JSON: {e}")
        return []


# ── Edit application ──────────────────────────────────────────────────────


def apply_edit_to_skill(skill_content, edit):
    """Apply a single edit to skill content. Returns modified content."""
    action = edit.get("action", "")
    location_text = edit.get("location", "")
    new_text = edit.get("new_text", "")

    lines = skill_content.split("\n")

    if action == "add":
        # Find the insertion point by section header matching (more reliable than single words)
        insert_after = None
        # First try to match a complete section header phrase (e.g. "## The Iron Law")
        header_words = [w for w in location_text.split() if w.startswith("##") or w.startswith("#")]
        if not header_words:
            # Fall back to longer keywords (>4 chars to reduce noise)
            keywords = [w.strip(".,!?;:'\"()[]-") for w in location_text.split() if len(w.strip(".,!?;:'\"()[]-")) > 4]
        else:
            keywords = header_words
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    insert_after = i
                    break
            if insert_after is not None:
                break
        if insert_after is not None:
            lines.insert(insert_after + 1, "")
            lines.insert(insert_after + 2, new_text)
        else:
            # Append at end as fallback
            lines.append("")
            lines.append(new_text)

    elif action == "modify":
        # Find and replace a section near the location
        header_words = [w for w in location_text.split() if w.startswith("##") or w.startswith("#")]
        keywords = header_words if header_words else [w.strip(".,!?;:'\"()[]-") for w in location_text.split() if len(w.strip(".,!?;:'\"()[]-")) > 4]
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    lines[i] = new_text
                    break
            if keyword.lower() in line.lower():
                break

    elif action == "remove":
        # Remove lines matching the location
        header_words = [w for w in location_text.split() if w.startswith("##") or w.startswith("#")]
        keywords = header_words if header_words else [w.strip(".,!?;:'\"()[]-") for w in location_text.split() if len(w.strip(".,!?;:'\"()[]-")) > 4]
        remove_indices = []
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    remove_indices.append(i)
                    break
        for idx in reversed(remove_indices):
            lines.pop(idx)

    return "\n".join(lines)


# ── Main optimization cycle ───────────────────────────────────────────────


def run_cycle(dry_run=False, override_skill=None):
    """Run one optimization cycle."""

    # 1. Load rotation
    rot = load_rotation()
    if not rot["skills"]:
        print("⚠ No skills in rotation. Create evaluators first.")
        return

    # 2. Pick skill
    if override_skill:
        idx = next((i for i, s in enumerate(rot["skills"])
                    if s["name"] == override_skill), None)
        if idx is None:
            print(f"❌ Skill '{override_skill}' not found in rotation.")
            return
    else:
        idx = rot["current_index"]

    skill_entry = rot["skills"][idx]
    skill_name = skill_entry["name"]
    evaluator_file = EVALUATORS_DIR / skill_entry["evaluator"]

    if not evaluator_file.exists():
        print(f"❌ Evaluator not found: {evaluator_file}")
        return

    evaluator = load_json(evaluator_file)
    skill_path = get_current_skill_file(skill_name)

    if not skill_path:
        print(f"❌ SKILL.md not found for '{skill_name}'")
        return

    print(f"\n{'='*60}")
    print(f"  Hermes SkillOpt — Cycle")
    print(f"  Skill: {skill_name}")
    print(f"  Mode:  {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"  Tests: {len(evaluator['test_cases'])}")
    print(f"{'='*60}\n")

    # 3. Read current skill
    with open(skill_path) as f:
        skill_content = f.read()

    print(f"📖 Loaded skill ({len(skill_content)} chars)")

    # 4. Baseline: run tests through current skill
    print("\n🔬 Running BASELINE tests...")
    baseline_results = []
    baseline_total = 0.0

    for tc in evaluator["test_cases"]:
        print(f"  Test: {tc['id']}...", end=" ", flush=True)
        response = simulate_agent_response(skill_path, tc["task"])
        score = score_response(response, tc)
        baseline_results.append(score)
        baseline_total += score["score"]
        print(f"score: {score['score']:.3f} ({score['passed']}✓ {score['failed']}✗)")

    baseline_avg = baseline_total / max(len(baseline_results), 1)
    print(f"\n📊 BASELINE SCORE: {baseline_avg:.3f}")

    # 5. Identify failures for optimizer
    failures = [r for r in baseline_results if r["score"] < 0.6]

    if not failures:
        print("✅ No significant failures — skill is performing well. Skipping optimization.")
        rot["current_index"] = (idx + 1) % len(rot["skills"])
        rot["last_optimized"] = datetime.now(timezone.utc).isoformat()
        if not dry_run:
            save_rotation(rot)
        log_history({
            "skill": skill_name,
            "baseline": round(baseline_avg, 3),
            "candidate": None,
            "accepted": "skipped",
            "edits": [],
            "reason": "Baseline score acceptable, no optimization needed",
            "dry_run": dry_run,
        })
        return

    print(f"\n🔧 {len(failures)} tests below threshold — generating improvements...")

    # 6. Propose edits
    edits = propose_edits(skill_content, failures, evaluator, dry_run=dry_run)

    if not edits:
        print("⚠ No edits proposed (optimizer returned empty).")
        rot["current_index"] = (idx + 1) % len(rot["skills"])
        rot["last_optimized"] = datetime.now(timezone.utc).isoformat()
        if not dry_run:
            save_rotation(rot)
        return

    print(f"\n📝 Proposed edits ({len(edits)}):")
    for e in edits:
        print(f"   [{e['action']}] {e['rationale'][:80]}")

    # 7. Apply edits to candidate
    candidate_content = skill_content
    for edit in edits:
        candidate_content = apply_edit_to_skill(candidate_content, edit)

    print(f"\n📄 Candidate skill: {len(candidate_content)} chars "
          f"({'larger' if len(candidate_content) > len(skill_content) else 'smaller'})")

    # 8. Re-evaluate candidate — write temp file so the worker reads candidate, not original
    print("\n🔬 Running RE-EVALUATION tests on candidate...")
    candidate_results = []
    candidate_total = 0.0

    # Write candidate to a temp file so simulate_agent_response reads the new skill
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tf:
        tf.write(candidate_content)
        candidate_temp_path = tf.name

    try:
        for tc in evaluator["test_cases"]:
            print(f"  Test: {tc['id']}...", end=" ", flush=True)
            response = simulate_agent_response(candidate_temp_path, tc["task"])
            score = score_response(response, tc)
            candidate_results.append(score)
            candidate_total += score["score"]
            print(f"score: {score['score']:.3f} ({score['passed']}✓ {score['failed']}✗)")
    finally:
        os.unlink(candidate_temp_path)

    candidate_avg = candidate_total / max(len(candidate_results), 1)
    print(f"\n📊 CANDIDATE SCORE: {candidate_avg:.3f}")

    # 9. Compare
    improvement = candidate_avg - baseline_avg
    threshold = 0.05  # 5% minimum lift
    accepted = improvement >= threshold

    print(f"\n{'='*60}")
    print(f"  Baseline:    {baseline_avg:.3f}")
    print(f"  Candidate:   {candidate_avg:.3f}")
    print(f"  Improvement: {improvement:+.3f} (threshold: +{threshold})")
    print(f"  Decision:    {'✅ ACCEPTED' if accepted else '❌ REJECTED'}")
    print(f"{'='*60}\n")

    # 10. Commit or discard
    if accepted and not dry_run:
        # Backup
        backup_path = backup_skill(skill_path)
        print(f"💾 Backed up to {backup_path}")

        # Write the candidate
        with open(skill_path, "w") as f:
            f.write(candidate_content)
        print(f"✅ Skill updated: {skill_path}")
    elif accepted and dry_run:
        print("🔷 Would commit (dry-run — no changes made)")

    # 11. Rotate
    rot["current_index"] = (idx + 1) % len(rot["skills"])
    rot["last_optimized"] = datetime.now(timezone.utc).isoformat()
    if not dry_run:
        save_rotation(rot)

    # 12. Log
    log_history({
        "skill": skill_name,
        "baseline": round(baseline_avg, 3),
        "candidate": round(candidate_avg, 3),
        "accepted": accepted,
        "improvement": round(improvement, 3),
        "threshold": threshold,
        "edits": [f"[{e['action']}] {e['rationale']}" for e in edits],
        "worker_model": "deepseek/deepseek-v4-flash",
        "optimizer_model": "deepseek/deepseek-v4-pro",
        "test_count": len(evaluator["test_cases"]),
        "dry_run": dry_run,
    })

    print(f"📝 Cycle logged to {HISTORY_FILE}")


# ── CLI ────────────────────────────────────────────────────────────────────


def show_status():
    """Show rotation state and history summary."""
    rot = load_rotation()
    print("\n📋 SkillOpt Rotation Status")
    print(f"{'='*40}")
    print(f"Skills in rotation: {len(rot['skills'])}")
    for i, s in enumerate(rot["skills"]):
        marker = "→" if i == rot["current_index"] else " "
        print(f"  {marker} [{i}] {s['name']}")
    print(f"Last optimized: {rot['last_optimized'] or 'never'}")

    if HISTORY_FILE.exists():
        entries = []
        with open(HISTORY_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        print(f"\n📊 History ({len(entries)} cycles):")
        for e in entries[-5:]:
            status = "✅" if e.get("accepted") == True else \
                     "⏭" if e.get("accepted") == "skipped" else "❌"
            name = e.get("skill", "?")
            base = e.get("baseline", 0)
            cand = e.get("candidate", 0)
            imp = e.get("improvement", 0)
            ts = e.get("timestamp", "")[:19]
            print(f"  {status} [{ts}] {name}: {base:.2f}→{cand:.2f} ({imp:+.2f})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hermes SkillOpt — automated skill improvement")
    parser.add_argument("--dry-run", action="store_true", help="Report only, no commits")
    parser.add_argument("--skill", type=str, help="Override which skill to optimize")
    parser.add_argument("--status", action="store_true", help="Show rotation state and exit")
    args = parser.parse_args()

    if args.status:
        show_status()
    else:
        run_cycle(dry_run=args.dry_run, override_skill=args.skill)
