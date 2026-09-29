<!-- llms-description: Diagnose a failing test, reproduce it, and fix the product or environment without changing the test. -->

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

# Diagnose failing tests

Existing tests are immutable evidence under `shared.md` §1a. This mode diagnoses whether
the product, configuration, fixture, or environment violates that evidence; it never
repairs, skips, or deletes a test.

## Workflow

1. **Create or resume the Tasks artifact** (per `modes/agent.md` Preflight — this is not optional). One artifact, id `tasks-fix-$(date +%Y%m%d)-<test-id-or-session>`, 3 subtasks from the start: `Understand the failure`, `Reproduce interactively`, `Fix code/environment or document blocker`. Created exactly once here — the submodes below (Debug/Heal/Sync) update this same artifact's subtasks, they never create a second one.
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
         {"id": "3", "title": "Fix code, environment, or document blocker", "status": "pending", "priority": "critical"}
       ]
     }'
   ```
2. **Orient**:
   ```bash
   helpmetest status
   helpmetest artifact list --tags "project:<slug>"
   helpmetest artifact list --type Memory --tags "project:<slug>"
   git log --oneline -10
   git diff --stat HEAD
   ```
   Look the `Memory` artifact up **by type**, not with `helpmetest search Memory` — that
   is a full-text search and returned two unrelated `ProjectHealthReport` artifacts when
   measured 2026-09-25. And read `status` as a **workspace** view: it has no project filter
   (see `modes/shared.md` §1), so filter its rows on `#project:<slug>` yourself before
   concluding anything about this project's health.
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

1. `helpmetest test view <id>` to read the test body, then `helpmetest test run <id>` to see it fail **now**, then `helpmetest test view <id> --errors` for the pass/fail ratio and the error *body*. A single green re-run is one sample: `playground-forms` was 1-pass/499-fail on 2026-09-26 and the one pass was a manual re-run. The `--errors` body is also where the real cause appears — `status` showed `Invalid keyword Get Text`, the body said `Multiple keywords with name 'Get Text' found`, which is a collision, not a missing keyword. Add `--json` for the structured result.
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

- `element_not_found` → restore or correctly expose the product element
- `timing` → fix the product or test environment timing cause
- `auth_or_state` → verify auth state restoration
- `api_or_backend` → repair or document the product failure
- `test_isolation` (alternating PASS/FAIL, shared state) → make the product fixture or
  environment idempotent

### Phase 4A: Fix code, configuration, fixtures, or environment

**HARD RULES — no test mutation:**
1. Validate the required product behaviour interactively first — run the complete existing
   test flow via `helpmetest interactive`.
2. Change only code, configuration, fixtures, or the test environment until it satisfies
   the existing test contract.
3. Run `helpmetest test run <id>`. Preserve the literal command and result output in the
   report. If it remains red, leave it red and state what code still needs to do.
4. **MUST update the Tasks artifact created in `## Workflow` step 1**: mark the subtask
   done only with the run URL as evidence; otherwise mark it blocked with the raw failure.

If the test appears stale or wrong, do not use `test update`. Stop and report its exact
expectation, the observed product behaviour, and the code change required for the test to
pass.

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
  "name": "Heal session [date]",
  "content": {
    "name": "Heal session [date]",
    "description": "[what was failing and what healing it should achieve]",
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
2. **Re-run each one, then check its history before classifying.** `status` shows the last
   result; a re-run shows one more sample. Neither is the picture. `helpmetest test view
   <id> --errors` gives the ratio and the error body — measured 2026-09-26,
   `playground-forms` was **1 passed, 499 failed** since 2026-09-19, and the single pass
   was a manual re-run that would have cleared it. Drop only what the history shows
   healthy, and say how many you dropped.
3. For each test still failing:
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

**Rewritten 2026-09-26 — the previous template could not be submitted.** It modelled a
single bulk log (`{fixed: [...], not_fixed: [...], summary: {...}}`) with an id of
`self-healing-log`. None of those three fields exists, all four required fields were
missing, and the name `"SelfHealing: Test Maintenance Log"` is itself rejected for
containing the type. The real artifact is **one per test**, not one per run:

```json
{
  "type": "SelfHealing",
  "id": "healing-<test-id>",
  "name": "<test name> — healing log",
  "content": {
    "name": "<test name> — healing log",
    "description": "<what keeps breaking and what was done about it>",
    "test_id": "<test-id>",
    "test_name": "<test name>",
    "total_fixes": 1,
    "successful_fixes": 1,
    "failed_fixes": 0,
    "current_status": "healthy",
    "attempts": [
      { "timestamp": "<ISO>",
        "error_message": "<the real failure text>",
        "error_type": "selector",
        "fix_applied": "Updated selector to [data-testid='submit-btn']",
        "selectors_tried": ["..."],
        "test_content_before": "...", "test_content_after": "...",
        "success": true,
        "notes": "<optional>" }
    ],
    "last_error": null,
    "last_fix_timestamp": "<ISO>"
  }
}
```

Required: `name`, `description`, `test_id`, `test_name`. Two closed enums, both measured:
`current_status` is `healthy | flaky | broken`, and `attempts[].error_type` is
`selector | syntax | timing | proxy | other` — **not** the `selector_change` /
`server_error` strings the old template used. `SelfHealingAttempt` requires
`error_message`, `error_type`, `fix_applied`, `success`.

A test you could not fix does not go in a `not_fixed` array — it gets its own artifact with
`success: false` on the attempt and `current_status: "broken"`, plus the bug written to the
Feature per Phase 4B. Verified: the shape above saved; the old one did not.

---

## Mode: Sync — Drift Audit After Refactor

**Tests may be passing but wrong — stale assertions, removed features, changed behavior.**

### Discrepancy Types

1. **Code Broke It** — test was passing, code change caused regression → fix code
2. **Test conflicts with intended behaviour** — stop, preserve the red result, and ask for
   a new explicit decision; never fix, skip, or delete the test
3. **Not Deployed** — fix in local code, not shipped yet → tag pending-deploy
4. **Removed Feature** — leave the test failing; report the removed contract and the code
   or product decision needed to resolve it

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

### Resolution record (per discrepancy)

```
#3 of 12 · TEST / PRODUCT CONFLICT
📋 <test name>
   expects   <what test asserts>
   product now  <what code does> · <file> · <commit>

   Result: test left unchanged and red.
   Needed: <code or product change required for the existing test to pass>
```

Do not offer to fix, skip, disable, or delete the test. The only allowed resolution in this
skill is to make code or its real environment satisfy the existing contract.

Never apply a category-wide test rewrite. Repair the shared code/environment cause, then
re-run the untouched tests.

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
