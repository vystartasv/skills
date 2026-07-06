---
name: test-driven-development
description: "TDD: enforce RED-GREEN-REFACTOR, tests before code."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, tdd, development, quality, red-green-refactor]
    related_skills: [systematic-debugging, writing-plans, subagent-driven-development]
---

# Test-Driven Development (TDD)

## Overview

Write the test first. Watch it fail. Write minimal code to pass.

**Immediate Action Required:**
1. Create the test file NOW using the file tool
2. Write ONE failing test
3. Run the test using the terminal tool to confirm it fails
4. Only then may you read or create any implementation files

Do NOT proceed to step 2 until step 1 is complete. Do NOT proceed to step 3 until step 2 is complete. Do NOT proceed to implementation until step 3 confirms failure.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions (ask the user first):**
- Throwaway prototypes
- Generated code
- Configuration files

Thinking "skip TDD just this once"? Stop. That's rationalization.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

## Red-Green-Refactor Cycle

### RED — Write Failing Test

Write one minimal test showing what should happen.

**Good test:**
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception('fail')
        return 'success'

    result = retry_operation(operation)

    assert result == 'success'
    assert attempts == 3
```
Clear name, tests real behavior, one thing.

**Bad test:**
```python
def test_retry_works():
    mock = MagicMock()
    mock.side_effect = [Exception(), Exception(), 'success']
    result = retry_operation(mock)
    assert result == 'success'  # What about retry count? Timing?
```
Vague name, tests mock not real code.

**Requirements:**
- One behavior per test
- Clear descriptive name ("and" in name? Split it)
- Real code, not mocks (unless truly unavoidable)
- Name describes behavior, not implementation

### Verify RED — Watch It Fail

**MANDATORY. Never skip.**

```bash
# Use terminal tool to run the specific test
pytest tests/test_feature.py::test_specific_behavior -v
```

Confirm:
- Test fails (not errors from typos)
- Failure message is expected
- Fails because the feature is missing

**Test passes immediately?** You're testing existing behavior. Fix the test.

**Test errors?** Fix the error, re-run until it fails correctly.

### GREEN — Minimal Code

Write the simplest code to pass the test. Nothing more.

**Good:**
```python
def add(a, b):
    return a + b  # Nothing extra
```

**Bad:**
```python
def add(a, b):
    result = a + b
    logging.info(f"Adding {a} + {b} = {result}")  # Extra!
    return result
```

Don't add features, refactor other code, or "improve" beyond the test.

**Cheating is OK in GREEN:**
- Hardcode return values
- Copy-paste
- Duplicate code
- Skip edge cases

We'll fix it in REFACTOR.

### Verify GREEN — Watch It Pass

**MANDATORY.**

```bash
# Run the specific test
pytest tests/test_feature.py::test_specific_behavior -v

# Then run ALL tests to check for regressions
pytest tests/ -q
```

Confirm:
- Test passes
- Other tests still pass
- Output pristine (no errors, warnings)

**Test fails?** Fix the code, not the test.

**Other tests fail?** Fix regressions now.

### REFACTOR — Clean Up

After green only:
- Remove duplication
- Improve names
- Extract helpers
- Simplify expressions

Keep tests green throughout. Don't add behavior.

**If tests fail during refactor:** Undo immediately. Take smaller steps.

### Repeat

Next failing test for next behavior. One cycle at a time.

## Why Order Matters

**"I'll write tests after to verify it works"**

Tests written after code pass immediately. Passing immediately proves nothing:
- Might test the wrong thing
- Might test implementation, not behavior
- Might miss edge cases you forgot
- You never saw it catch the bug

Test-first forces you to see the test fail, proving it actually tests something.

**"I already manually tested all the edge cases"**

Manual testing is ad-hoc. You think you tested everything but:
- No record of what you tested
- Can't re-run when code changes
- Easy to forget cases under pressure
- "It worked when I tried it" ≠ comprehensive

Automated tests are systematic. They run the same way every time.

**"Deleting X hours of work is wasteful"**

Sunk cost fallacy. The time is already gone. Your choice now:
- Delete and rewrite with TDD (high confidence)
- Keep it and add tests after (low confidence, likely bugs)

The "waste" is keeping code you can't trust.

**"TDD is dogmatic, being pragmatic means adapting"**

TDD IS pragmatic:
- Finds bugs before commit (faster than debugging after)
- Prevents regressions (tests catch breaks immediately)
- Documents behavior (tests show how to use code)
- Enables refactoring (change freely, tests catch breaks)

"Pragmatic" shortcuts = debugging in production = slower.

**"Tests after achieve the same goals — it's spirit not ritual"**

No. Tests-after answer "What does this do?" Tests-first answer "What should this do?"

Tests-after are biased by your implementation. You test what you built, not what's required. Tests-first force edge case discovery before implementing.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |
| "Test hard = design unclear" | Listen to the test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD faster than debugging. Pragmatic = test-first. |
| "Manual test faster" | Manual doesn't prove edge cases. You'll re-test every change. |
| "Existing code has no tests" | You're improving it. Add tests for the code you touch. |

## Red Flags — STOP and Start Over

If you catch yourself doing any of these, delete the code and restart with TDD:

- Code before test
- Test after implementation
- Test passes immediately on first run
- Can't explain why test failed
- Tests added "later"
- Rationalizing "just this once"
- "I already manually tested it"
- "Tests after achieve the same purpose"
- "Keep as reference" or "adapt existing code"
- "Already spent X hours, deleting is wasteful"
- "TDD is dogmatic, I'm being pragmatic"
- "This is different because..."

**All of these mean: Delete code. Start over with TDD.**

## Mandatory First Action

Before ANY other action (reading files, checking structure, etc.), you MUST write a failing test. This is not optional. The test file must be created and the test executed to confirm failure before any implementation code is written.

**Enforcement:**
- Do NOT read implementation files before writing the test
- Do NOT check project structure before writing the test
- Do NOT plan implementation before writing the test
- The first file operation MUST be creating the test file
- The first terminal command MUST be running the test to confirm failure

If you catch yourself doing anything else first, STOP. Delete any work done. Start with the test.

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

Can't check all boxes? You skipped TDD. Start over.

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write the wished-for API. Write the assertion first. Ask the user. |
| Test too complicated | Design too complicated. Simplify the interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify the design. |

## Hermes Agent Integration

### Running Tests

Use the `terminal` tool to run tests at each step:

```python
# RED — verify failure
terminal("pytest tests/test_feature.py::test_name -v")

# GREEN — verify pass
terminal("pytest tests/test_feature.py::test_name -v")

# Full suite — verify no regressions
terminal("pytest tests/ -q")
```

### With delegate_task

When dispatching subagents for implementation, enforce TDD in the goal:

```python
delegate_task(
    goal="Implement [feature] using strict TDD",
    context="""
    Follow test-driven-development skill:
    1. Write failing test FIRST
    2. Run test to verify it fails
    3. Write minimal code to pass
    4. Run test to verify it passes
    5. Refactor if needed
    6. Commit

    Project test command: pytest tests/ -q
    Project structure: [describe relevant files]
    """,
    toolsets=['terminal', 'file']
)
```

### With systematic-debugging

Bug found? Write failing test reproducing it. Follow TDD cycle. The test proves the fix and prevents regression.

Never fix bugs without a test.

## Test-Driven Migration & Modernization

When migrating a codebase (old language → new language, old framework → new framework, or even a complete rewrite), TDD becomes even more critical. The tests are your **parity guarantee** — they prove the new system behaves identically to the old one.

### The Migration Principle

```
Old codebase → add tests → measure coverage → migrate in chunks → verify parity → repeat
```

The tests come **first**, always. The old codebase might have no tests — that's your starting point, not an excuse to skip them.

### Step 1: Mature the Old Codebase First

Before migrating anything, build a safety net:

1. **Identify behavior boundaries** — what are the key entry points, APIs, and data flows?
2. **Write characterization tests** — tests that capture *current* behavior, regardless of whether it's correct. These freeze the system's existing behavior.
3. **Measure coverage** — the more coverage you have, the more accurate your parity checking will be
4. **Document structure** — document the project layout, key modules, data models, and dependencies so the migration agent has context

### Step 2: Build a Parity Checker

A parity checker is tooling that verifies the old and new systems produce identical outputs for identical inputs:

```
Old system → run with input X → record output Y
New system → run with input X → verify output = Y
```

**Implementation approach:**
1. Identify all input/output boundaries of the system (APIs, functions, data transformations)
2. For composable systems, write a simulator that exercises both old and new code paths
3. For API migrations, write a tool that calls both old and new endpoints with parameter combinations and asserts identical responses
4. For data migrations, compare pre- and post-migration datasets field-by-field

```python
# Example: API parity checker pattern
def test_api_parity():
    # Old API
    old_result = call_old_api("/users/42", method="GET")
    # New API
    new_result = call_new_api("/v2/users/42", method="GET")

    assert old_result.status_code == new_result.status_code
    assert old_result.json() == new_result.json(), \
        f"Parity failure: old={old_result.json()}, new={new_result.json()}"
```

### Step 3: Incremental Migration in Small Chunks

Do not attempt a "finger snap" migration (convert entire codebase at once). Instead:

1. **Define scoped user stories** — each story covers one piece of functionality
2. **Create an executable plan** — a checkbox list of specific files, interfaces, and behaviors to migrate
3. **Migrate one chunk at a time** — use AI agents to convert, but validate parity after each chunk
4. **Archive documentation after each chunk** — record what was migrated and how
5. **Run regression tests continuously** — verify new changes don't break previously migrated chunks

```yaml
# Example migration plan structure
stories:
  - id: MIG-001
    scope: "User authentication module"
    files_old:
      - src/auth/login.py
      - src/auth/session.py
    files_new:
      - src/v2/auth/login.js
      - src/v2/auth/session.js
    parity_tests:
      - test_login_accepts_valid_credentials
      - test_login_rejects_invalid_credentials
      - test_session_expiry
    status: pending
```

### Step 4: Use the Tests as Guardrails for AI Agents

When using AI agents for migration code generation:

1. The parity tests are your **objective pass/fail criteria** — the agent knows when it's succeeded
2. Give the agent the parity tooling as context: "Your output must pass these checks"
3. After each migration chunk, the agent runs parity tests and iterates until they pass
4. The safety net allows you to refactor and improve without fear of breaking behavior

### Step 5: Full SDLC Integration

After migration, the same test suite transitions to your normal development workflow:

- Parity tests become regression tests
- Characterization tests become your acceptance test suite
- The migration scaffolding becomes your CI pipeline
- Your tests document what the new system should do

## Testing Anti-Patterns

- **Testing mock behavior instead of real behavior** — mocks should verify interactions, not replace the system under test
- **Testing implementation details** — test behavior/results, not internal method calls
- **Happy path only** — always test edge cases, errors, and boundaries
- **Brittle tests** — tests should verify behavior, not structure; refactoring shouldn't break them

## Final Rule

```
Production code → test exists and failed first
Otherwise → not TDD
```

No exceptions without the user's explicit permission.
