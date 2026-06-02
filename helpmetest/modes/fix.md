> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

> ### 🔴 AFTER EVERY TEST UPSERT — RUN IT IMMEDIATELY.
> **Preferred:** Pass `run: true` to `helpmetest_upsert_test` — this updates AND runs in one atomic call.
> **Alternative:** Follow with `helpmetest_run_test({ id: "<same-id>" })` as a separate call.
> Upsert without run is **incomplete**. The test does not exist until it has a run record.
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

```
helpmetest_status()
helpmetest_search_artifacts({ query: "" })
helpmetest_search_artifacts({ query: "Memory" })
how_to({ type: "context_discovery" })
how_to({ type: "interactive_debugging" })
how_to({ type: "debugging_self_healing" })
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
```
helpmetest_status()             // failing tests, health checks
git log --oneline -10           // recent commits
git diff --stat HEAD            // uncommitted changes
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

1. `helpmetest_open_test` + `helpmetest_status({ id, testRunLimit: 10 })`
2. Read the error. Classify: selector? timing? assertion? state? API?
3. Check recent git changes — map changed files to likely failure causes
4. Load the Feature artifact the test belongs to

### Phase 2: Reproduce Interactively

Run steps one at a time via `helpmetest_run_interactive_command`:

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
2. Update via `helpmetest_upsert_test`
3. Run via `helpmetest_run_test` to confirm
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

1. Get all failing tests from `helpmetest_status`
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

1. Run all tests: `helpmetest_status` → get IDs → run each
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

### Anti-Patterns (Auto-Reject)

- Only navigation + element counting
- Click + wait for element that was already visible
- Form field presence check without filling + submitting
- Page load + title check only
- UI element visible without verifying it works

### Minimum Quality Requirements

- ≥ 5 meaningful steps
- ≥ 2 assertions (Get Text, Should Be, Wait For)
- Verifies state change (before/after OR API response OR persistence)
- Has `[Documentation]` with a `PROTECTS:` line naming the specific user complaint
- Uses stable selectors
- Tags: `priority:?` and `feature:?` required

### Mutation Resistance Check

Mentally introduce a realistic bug (e.g. "save button onClick removed") and ask: does this test catch it? If not → score 7+.

### Bullshit Score (1–10)

| Score | Meaning |
|-------|---------|
| 1–3 | Solid — behavioral assertions, mutation-resistant |
| 4–6 | Mediocre — some value but weak |
| 7–9 | Mostly bullshit — navigation only, no real behavior |
| 10 | Pure bullshit — single Go To, Sleep with no assertion |

**Score ≤ 4 → PASS. Score ≥ 5 → REJECT**

### Output: Single Test

```
[score]/10 — ✅ PASS / ❌ REJECT
Test ID: [id]
Reason: [one sentence]
[What to fix if rejected]
```

### Output: Batch

Table grouped by tier (Solid / Mediocre / Bullshit), then action menu:

```
Reply with numbers to act:

1. Delete [N] score-10 tests
2. Fix [N] misleading test names
3. Fix [N] vacuous assertions
4. Rewrite [N] mediocre tests
5. Investigate [N] failing tests
all — do everything
```

When user replies: execute without asking further. Delete score-10 tests immediately. For rewrites, show diff then call `helpmetest_upsert_test`.

---

## Key Principles

- **Reproduce before fixing** — never guess, always verify interactively
- **Code may not be deployed** — check `git diff HEAD` before calling something broken
- **Tests and code are both sources of truth** — neither wins automatically
- **Don't weaken assertions to make tests pass** — fix the root cause
- **All findings go into Feature artifacts** — a bug mentioned only in chat doesn't exist
- **Update Feature.status** after any change: "working" | "broken" | "partial"

**Version:** 0.1
