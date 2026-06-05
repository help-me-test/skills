> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

> ### 🔴 AFTER EVERY TEST CREATE/UPDATE — RUN IT IMMEDIATELY.
> Follow with `helpmetest test run <id>` as a separate call.
> Create/update without run is **incomplete**. The test does not exist until it has a run record.
> No exceptions. Not even "the server isn't running." A FAIL result is valid — it documents current state.

---

## Narrate Your Actions

**Never create a test, artifact, or run a test silently.** Always tell the user:
- **Before:** what you are about to do and why (what scenario it covers, what risk it guards against)
- **After:** what happened — result, what the artifact contains, why a test failed
- **Next:** what you will do next and what decision point is coming

Silence means the user has no idea what you did or why.

# Fix Tests

One skill for everything wrong with your test suite. Reads the situation, picks the right mode.

## Prerequisites — Always Do This First

```bash
helpmetest status
helpmetest artifact list
helpmetest search Memory
```

Check git state:
```bash
git log --oneline -10
git diff --stat HEAD
```

## Announce

After orient, present before classifying or acting.

**Specific failing tests found:**
> "After diagnosis you'll know whether `[test-id]` is a broken selector, a timing issue, or an actual bug in the feature. [If bug: I'll document it in the Feature artifact so it doesn't get lost.] I'd start with `[highest-priority failing test]`. That, or is there a different test you need green urgently?"

**Multiple failing tests:**
> "After this you'll know which of the [N] failures are fixable today (selector, timing) and which are real bugs in the app. I'd work through them highest-priority first. Want me to go in that order, or is there one specific test you need fixed first?"

**No failing tests, but user reported something broken:**
> "Nothing is showing as failed in the last run, but something's clearly wrong. After this you'll know whether it's a test issue, a code issue, or an environment problem. I'll check git history and dig in — give me a minute."

**Rule:** Always say what the user will know after this, not what you will do. Recommend one starting point.

## Read the Situation → Pick the Mode

After orient, classify:

| Signal | Mode |
|--------|------|
| "Something broke" / "it stopped working" / vague signal | **Triage first** (see below) |
| One specific test named by user, or one test failing | **Debug** |
| Multiple tests failing after a deploy or UI change | **Heal** |
| Tests passing but code changed — drift suspected | **Sync** |
| "Is this test any good?" / reviewing test quality | **Validate** |
| Mixed (failures + drift + quality issues) | **All modes, in order** |

### Triage (when you don't know what's wrong)

Gather fast, diagnose specifically, then switch to the right mode.

Collect everything in parallel:
```bash
helpmetest status              # failing tests, health checks
git log --oneline -10          # recent commits
git diff --stat HEAD           # uncommitted changes
```

Map what you find to a root cause:

- **Test issue** — test fails but feature works. Selector changed, timing off, stale after refactor → **Debug or Heal mode**
- **App bug** — feature itself is broken. 500 errors, missing data, broken flow → document in Feature.bugs[], tell user
- **Regression** — worked before a specific commit. Identify the commit, scope blast radius → **Debug mode** + recommend rollback or hotfix
- **Environment** — auth state expired, proxy down, env var missing → fix setup, re-run auth test
- **Coverage gap** — "it's broken" but no test exists → create Feature artifact, run `/tdd`

State the diagnosis once before acting: **"Based on [evidence], the problem is [specific cause]. The fix is [action]."** Then switch to the right mode.

---

## Mode: Debug — One Test, Root Cause

**Golden Rule: Always reproduce interactively before fixing. Never guess.**

### Tasks Artifact

Create before starting:

```json
{
  "type": "Tasks",
  "name": "Tasks: Debug [test name]",
  "content": {
    "overview": "Debug failing test [test-id]. Root cause → fix or document bug.",
    "tasks": [
      { "id": "1.0", "title": "Understand the failure", "status": "pending", "priority": "critical" },
      { "id": "2.0", "title": "Reproduce interactively", "status": "pending", "priority": "critical" },
      { "id": "3.0", "title": "Determine root cause", "status": "pending", "priority": "critical" },
      { "id": "4.0", "title": "Fix test OR document bug", "status": "pending", "priority": "critical" }
    ]
  }
}
```

### Phase 1: Understand

1. `helpmetest open test <id>` + `helpmetest status --id <id> --history 10`
2. Read the error. Classify: selector? timing? assertion? state? API?
3. Check recent git changes — map changed files to likely failure causes
4. Load the Feature artifact the test belongs to

### Phase 2: Reproduce Interactively

Run steps one at a time via `helpmetest interactive "<keyword>"`:

```robot
As  <auth_state>
Go To  <url>
# → observe after each step
```

Stop at the failing step. Investigate based on error type:

- **Element not found**: Try alternate selectors — is element gone (bug) or selector changed (test issue)?
- **Not interactable**: Check visibility, scroll, multiple matches, disabled state
- **Assertion failed**: What's actually displayed? Behavior changed intentionally?
- **Timeout**: App slow or broken?

### Phase 3: Root Cause

- **Selector changed** → fix selector
- **Timing** → add wait
- **State/auth** → verify auth state restoration
- **API error** → document bug
- **Test isolation** (alternating PASS/FAIL, shared state) → make idempotent

### Phase 4A: Fix Test

1. Validate fix interactively first — run the complete corrected flow
2. Update via `helpmetest test update <id> ...`
3. Run via `helpmetest test run <id>` to confirm
4. Update Feature artifact

### Phase 4B: Document Bug

Add to Feature.bugs[]:
```json
{
  "name": "Brief description",
  "given": "Precondition",
  "when": "Action taken",
  "then": "Expected outcome",
  "actual": "What actually happens",
  "severity": "blocker|critical|major|minor",
  "url": "http://example.com/page",
  "tags": []
}
```

Update Feature.status → "broken" or "partial".

---

## Mode: Heal — Bulk Failures After Deploy

**Don't fix blindly — classify first, then fix fast.**

### Tasks Artifact

```json
{
  "type": "Tasks",
  "name": "Tasks: Heal Session [date]",
  "content": {
    "overview": "Healing [N] failing tests.",
    "tasks": [
      { "id": "1.0", "title": "[test-id]: [test name]", "status": "pending", "priority": "critical",
        "notes": "[error summary from last run]" }
    ],
    "notes": ["SelfHealing artifact: self-healing-log"]
  }
}
```

### Startup: Fix All Existing Failures

1. Get all failing tests from `helpmetest status`
2. For each failing test:
   - Classify failure type
   - **Fixable** (selector change, timing, form structure): investigate → fix → verify → document in SelfHealing artifact
   - **Not fixable** (auth broken, 500 errors, missing pages): document as bug in Feature artifact
3. After processing all failures, enter monitoring mode

**Fixable vs Not:**
- Fixable: selector changed, timing issue, form added/removed, button moved, test isolation
- Not fixable: auth broken, server errors, missing features, API endpoints removed

### Monitoring Mode

```
listen_to_events({ type: "test_run_completed" })
```

When a test fails: classify → fix if fixable → document if not → resume listening.

### SelfHealing Artifact

```json
{
  "type": "SelfHealing",
  "id": "self-healing-log",
  "name": "SelfHealing: Test Maintenance Log",
  "content": {
    "fixed": [
      { "test_id": "test-login", "pattern_detected": "selector_change",
        "fix_applied": "Updated selector to [data-testid='submit-btn']",
        "verification_result": "Test passed on re-run", "timestamp": "..." }
    ],
    "not_fixed": [
      { "test_id": "test-checkout", "issue_type": "server_error",
        "error_message": "500 on POST /api/checkout",
        "why_not_fixable": "Application bug, not a test issue",
        "recommendation": "Investigate checkout API endpoint" }
    ],
    "summary": { "total_processed": 5, "fixed": 3, "not_fixable": 2, "last_run": "..." }
  }
}
```

---

## Mode: Sync — Drift Audit After Refactor

**Tests may be passing but wrong — stale assertions, removed features, changed behavior.**

### Discrepancy Types

**Failure-based:**
1. **Code Broke It** — test was passing, code change caused regression → fix code
2. **Test Is Stale** — code intentionally changed, test hasn't caught up → fix test
3. **Not Deployed** — fix in local code, not shipped yet → tag pending-deploy
4. **Removed Feature** — test exercises what no longer exists → delete test

**Passing but suspicious:**
5. **False Positive** — passes but assertions too weak to verify anything
6. **Flaky** — passes sometimes, fails sometimes with no code change
7. **Duplicate Coverage** — two tests cover the exact same scenario

**Coverage gaps:**
8. **Missing Test** — feature exists, no test coverage
9. **Scenario Gap** — Feature artifact has scenario but `test_ids` is empty
10. **Scenario Drift** — tests and code agree but Feature artifact documents old behavior
11. **Selector / Schema Drift** — test's selectors or API shape no longer matches code

### Workflow

1. Run all tests: `helpmetest status` → get IDs → run each
2. For each test + each Feature artifact, check for discrepancy types above
3. Record: type, test, Feature, what test expects vs what code does, git evidence

### Sync Report (present before resolving)

```
🔄 Sync Report · <project> · <date>
<N> failing · <N> flaky · <N> gaps · <N> passing

💥 Failures
   Code Broke It · <N> tests
   <test name>
   issue: <one line>

🕳 Gaps
   Missing Test · <N>
   <feature name> — <what it does>
```

Wait for user to confirm, then resolve one by one.

### Resolution Options (per discrepancy)

```
#3 of 12 · TEST IS STALE
📋 <test name>
   expects   <what test asserts>
   code now  <what code does> · <file> · <commit>

   1 · Fix the test    [code leads]
   2 · Fix the code    [test leads]
   3 · Skip
   4 · Delete test
   5 · Document bug
   6 · Not deployed
```

If user says "fix all selector drifts" — apply across the category without asking per item.

---

## Mode: Validate — Test Quality Review

**The core question: would this test fail if the feature broke? If not → reject.**

### The Business Value Test (MOST IMPORTANT)

1. "What business capability does this test verify?"
2. "If this test passes but the feature is broken, is that possible?"

**If answer to #2 is YES → IMMEDIATE REJECTION**

---

### Validation Rules (R1–R13)

Apply all rules. Each rule is a gate.

**R1 — Meaningful steps**
- FAIL if < 5 meaningful steps (each step must change state, not just navigation)
- FAIL if test is only navigation + element counting

**R2 — Behavioral assertions**
- FAIL if < 2 assertions (Get Text, Should Be, Wait For ≠ element present)
- FAIL if only asserts element visibility without behavior

**R3 — State verification**
- FAIL if test doesn't verify state change (before/after OR API response OR persistence)

**R4 — Description has Given/When/Then/Risk**
- FAIL if `--description` missing Given/When/Then/Risk format
- FAIL if uses `[Documentation]` Robot syntax instead of `--description` CLI flag

**R5 — Stable selectors**
- FAIL if uses fragile selectors (index-based, dynamic text without stable anchor)

**R6 — Required tags**
- FAIL if missing `priority:?` or `feature:?`

**R7 — Actionable assertions**
- FAIL if only checks "no error" instead of positive outcome
- FAIL if vacuous assertion (always passes)

**R8 — Tags are complete and consistent**
- FAIL if tags contradict each other or contradict test body

**R9 — Auth state used correctly**
- FAIL if test re-authenticates instead of reusing established auth state

**R10 — Linked to a Feature.scenario**
- FAIL if the test is an orphan (no scenario references its id in `test_ids`)

**R11 — Mutation Resistance**
- FAIL if the test could pass even when the code under test is broken
- Check: remove the save handler, break the validation — would this test fail?
- Patterns that fail R11: asserts visible but not functional, clicks but checks no data change

**R12 — Tests Our Business Logic, Not Framework Behavior**
- FAIL if test validates: Express/Fastify routes, Prisma/Mongoose ops, bcrypt/JWT sign, axios/fetch calls
- PASS if test validates custom business logic wrapping these libraries

**R13 — Minimal Mocking**
- FAIL if >3-4 mocks per test
- FAIL if mocking pure functions or business logic (only mock external I/O)

---

### Scoring

Score PASSes out of applicable rules.

**R1-R10:**
- **A (9-10 PASS):** ship it
- **B (7-8):** solid, minor rewrites suggested
- **C (5-6):** needs real work
- **D (3-4):** probably better to rewrite than patch
- **F (<3):** delete or start over

**R11-R13 (always applicable for functional tests):**
- Each FAIL on R11-R13 lowers the final grade by one tier (A→B, B→C, etc.)
- FAIL on R12 + test only validates framework behavior → automatic F

---

### Bullshit Score Translation

| Bullshit Score | Grade | Action |
|----------------|-------|--------|
| 1–3 | A-B | ship it |
| 4–6 | C | minor rewrites |
| 7–9 | D | rewrite or delete |
| 10 | F | delete immediately |

---

### Output: Single Test

```
[Grade] — [PASS/REJECT] (R11-R13: X/3)
Test ID: [id]
Rule failures: R11, R12
Evidence: [specific line or absence]
[What to fix]
```

### Output: Batch

Table grouped by grade (A / B / C / D / F), then action menu:

```
Reply with numbers to act:

1. Delete [N] F-grade tests
2. Fix [N] D-grade tests
3. Rewrite [N] C-grade tests
4. Keep [N] A/B-grade tests
all — do everything
```

When user replies: execute without asking further.

---

## Key Principles

- **Reproduce before fixing** — never guess, always verify interactively
- **Code may not be deployed** — check `git diff HEAD` before calling something broken
- **Tests and code are both sources of truth** — neither wins automatically
- **Don't weaken assertions to make tests pass** — fix the root cause
- **All findings go into Feature artifacts** — a bug mentioned only in chat doesn't exist
- **Update Feature.status** after any change: "working" | "broken" | "partial"

**Version:** 0.1
