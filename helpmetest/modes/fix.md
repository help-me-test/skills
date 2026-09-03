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

One skill for everything wrong with your test suite. Reads the situation, picks the right submode.

## Workflow

1. **Create or resume the Tasks artifact** (per `modes/agent.md` Preflight — this is not optional). One artifact, id `tasks-fix-$(date +%Y%m%d)-<test-id-or-session>`, 3 subtasks from the start: `Understand the failure`, `Reproduce interactively`, `Fix test or document bug`. Created exactly once here — the submodes below (Debug/Heal/Sync) update this same artifact's subtasks, they never create a second one.
   ```bash
   helpmetest artifact upsert \
     --id "tasks-fix-$(date +%Y%m%d)-<test-id>" \
     --type Tasks \
     --name "Tasks: Fix <test-id>" \
     --content '{
       "overview": "Debug failing test <test-id>. Root cause \u2192 fix or document bug.",
       "tasks": [
         {"id": "1", "title": "Understand the failure", "status": "in_progress", "priority": "critical"},
         {"id": "2", "title": "Reproduce interactively", "status": "pending", "priority": "critical"},
         {"id": "3", "title": "Fix test or document bug", "status": "pending", "priority": "critical"}
       ]
     }'
   ```
2. **Orient**:
   ```bash
   helpmetest status
   helpmetest artifact list
   helpmetest search Memory
   git log --oneline -10
   git diff --stat HEAD
   ```
3. **Announce** — present before classifying or acting (see templates below). Always say what the user will know after this, not what you will do. Recommend one starting point.
4. **Classify the signal and route to a submode** using the table below. If the signal itself is vague ("something broke"), run Triage first (below the table) to get to a specific classification before routing.
5. **Execute the routed submode** (`Mode: Debug` / `Mode: Heal` / `Mode: Sync` / `Mode: Validate` below) — each ends in either a fix, a documented bug, or a report. Use `references/failure-categories.md` for the actual error category once you have a specific failing test, and `references/evidence-rules.md` for how to record findings — don't invent evidence.
6. **Verify green** — `helpmetest test run <id>` after any fix; a "should work" claim without a run is not done.
7. **Close out** per `modes/agent.md` Postflight — every Tasks subtask terminal with evidence, Feature.status updated if a bug was found or fixed.

### Announce templates

**Specific failing tests found:**
> "After diagnosis you'll know whether `[test-id]` is a broken selector, a timing issue, or an actual bug in the feature. [If bug: I'll document it in the Feature artifact so it doesn't get lost.] I'd start with `[highest-priority failing test]`. That, or is there a different test you need green urgently?"

**Multiple failing tests:**
> "After this you'll know which of the [N] failures are fixable today (selector, timing) and which are real bugs in the app. I'd work through them highest-priority first. Want me to go in that order, or is there one specific test you need fixed first?"

**No failing tests, but user reported something broken:**
> "Nothing is showing as failed in the last run, but something's clearly wrong. After this you'll know whether it's a test issue, a code issue, or an environment problem. I'll check git history and dig in — give me a minute."

### Classify and route

| Signal | Submode |
|--------|------|
| "Something broke" / "it stopped working" / vague signal | **Triage first** (below), then re-route |
| One named test, or one test failing, whether or not a deploy just happened | **Debug** |
| Multiple tests failing together, especially right after a deploy or UI change | **Heal** |
| Tests passing but code changed — drift suspected | **Sync** |
| "Is this test any good?" / reviewing test quality | **Validate** |
| Mixed (failures + drift + quality issues) | **All submodes, in order** |

Disambiguating Debug vs Heal: route on **how many tests are failing**, not on whether a deploy happened — a deploy that breaks a single named test is still Debug; only route to Heal when multiple tests failed together.

### Triage (when the signal is vague)

Gather fast, diagnose specifically, then re-route using the table above.

Collect everything in parallel:
```bash
helpmetest status              # failing tests, health checks
git log --oneline -10          # recent commits
git diff --stat HEAD           # uncommitted changes
```

Map what you find to a root cause:

- **Test issue** — test fails but feature works. Selector changed, timing off, stale after refactor → **Debug or Heal**
- **App bug** — feature itself is broken. 500 errors, missing data, broken flow → document in Feature.bugs[], tell user
- **Regression** — worked before a specific commit. Identify the commit, scope blast radius → **Debug** + recommend rollback or hotfix
- **Environment** — auth state expired, proxy down, env var missing → fix setup, re-run auth test
- **Coverage gap** — "it's broken" but no test exists → create Feature artifact, run `/tdd`

State the diagnosis once before acting: **"Based on [evidence], the problem is [specific cause]. The fix is [action]."** Then re-route using the table above.

---

## Mode: Debug — One Test, Root Cause

**Golden Rule: Always reproduce interactively before fixing. Never guess.**

The Tasks artifact was already created in `## Workflow` step 1 — update its subtasks as you move through the phases below, don't create a second one.

### Phase 1: Understand

1. `helpmetest test view <id>` to read the test body; `helpmetest test run <id> --json` to get last run details
2. Read the error. Classify using `references/failure-categories.md` — pick exactly one category (`element_not_found`, `timing`, `assertion_failure`, `auth_or_state`, `api_or_backend`, `environment`, `test_isolation`, `unknown`), grounded in the run's evidence (`references/evidence-rules.md`).
3. Check recent git changes — map changed files to likely failure causes
4. Load the Feature artifact the test belongs to

### Phase 2: Reproduce Interactively

Run the failing steps one at a time using `interactive` mode (see `modes/interactive.md`). Stop at the failing step and investigate based on error type:


- **Element not found**: Try alternate selectors — is element gone (bug) or selector changed (test issue)?
- **Not interactable**: Check visibility, scroll, multiple matches, disabled state
- **Assertion failed**: What's actually displayed? Behavior changed intentionally?
- **Timeout**: App slow or broken?

### Phase 3: Root Cause

Map to the category chosen in Phase 1 (`references/failure-categories.md`):

- `element_not_found` → fix selector
- `timing` → add wait
- `auth_or_state` → verify auth state restoration
- `api_or_backend` → document bug
- `test_isolation` (alternating PASS/FAIL, shared state) → make idempotent

### Phase 4A: Fix Test

**HARD RULES — no skipping:**
1. Validate fix interactively first — run the complete corrected flow via `helpmetest interactive`
2. Update: `helpmetest test update <id> --file /tmp/<id>-fixed.robot --no-run`
3. **MUST run**: `helpmetest test run <id>` — wait for green. "Should work" is not evidence.
4. **MUST update the Tasks artifact created in `## Workflow` step 1**: mark the subtask done, set `notes` to the run URL as evidence (per `modes/agent.md` §Evidence). Don't create a second artifact here.

### Phase 4B: Document Bug

Add to `Feature.bugs[]` — shape in `references/cli-contracts.md`. Update `Feature.status` → `"broken"` or `"partial"`.

---

## Mode: Heal — Bulk Failures After Deploy

**Don't fix blindly — classify first, then fix fast.**

### Tasks Artifact — replace the generic shape from Workflow step 1

Heal handles bulk failures, so its Tasks artifact needs one subtask per failing test, not the 3-phase Debug shape created by default in `## Workflow` step 1. Overwrite the `tasks` array on that same artifact id (don't create a second artifact):

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

### Recording discrepancies

1. Run all tests: `helpmetest status` → get IDs → run each
2. For each test + each Feature artifact, check for discrepancy types above
3. Record: type, test, Feature, what test expects vs what code does, git evidence — per `references/evidence-rules.md`, don't record a discrepancy type you're inferring without the actual diff/error text backing it.

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

Present the Sync Report, then immediately begin resolving — present one discrepancy at a time using the Resolution Options format below.

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

See `modes/validate.md` for the full R1–R13 rules, scoring, and output format. Apply it exactly as defined there.

---

## Key Principles

- **Reproduce before fixing** — never guess, always verify interactively
- **Code may not be deployed** — check `git diff HEAD` before calling something broken
- **Tests and code are both sources of truth** — neither wins automatically
- **Don't weaken assertions to make tests pass** — fix the root cause
- **All findings go into Feature artifacts** — a bug mentioned only in chat doesn't exist
- **Update Feature.status** after any change: "working" | "broken" | "partial"

**Version:** 0.2 — restructured into a canonical `## Workflow`, fixed duplicate Tasks-artifact creation, wired `references/failure-categories.md` and `references/evidence-rules.md`.
