# Mode: pre-push

Runs the minimum set of tests needed to gate a push: all `priority:critical` tests plus tests covering files changed since the last push. Binary output — BLOCKED or CLEAR TO PUSH. Does NOT push, does NOT fix anything.

## Orient First

```bash
helpmetest status
```

Snapshot the current state of critical tests before running anything.

## Announce

After orient, present the plan before running anything:

```
## Pre-push plan

Critical tests: [N] (tagged priority:critical)
Changed files: [reading git diff — annotation-covered tests TBD]
Total runs: ~[N + M] tests

I will:
1. Collect all priority:critical tests (Set A)
2. Grep changed files for @helpmetest annotations → collect covered test IDs (Set B)
3. Run the union of A ∪ B
4. Produce a RegressionRun artifact
5. Output BLOCKED or CLEAR TO PUSH

Starting now.
```

Pre-push has no scope ambiguity — proceed immediately after presenting the plan.

---

## Step 1 — Find changed files

```bash
git diff origin/HEAD...HEAD --name-only
```

If no upstream is configured (command errors), fall back to:
```bash
git diff HEAD~1 HEAD --name-only
```

---

## Step 2 — Collect tests to run

**Set A — critical tests:**
Call `helpmetest status`. Collect every test with tag `priority:critical`.

**Set B — annotation-covered tests:**
For each file from Step 1, `grep -n "@helpmetest"` and collect referenced test IDs.

Run the **union** of Set A ∪ Set B (deduplicated).

---

## Step 3 — Run the tests

For each test ID, call `helpmetest test run <test-id>` one at a time.

Track which tests pass and which fail. A critical test failing is a blocker regardless of cause.

---

## Step 4 — Produce output artifact

Fetch the schema first:
```bash
helpmetest artifact schema RegressionRun
```

Create a `RegressionRun` artifact with:
- `trigger_files`: files from Step 1
- `selection_method`: `"mixed"` (critical tags + annotations)
- `affected_tests`: full list that ran
- `results[]`: one entry per test with classification
- `verdict`:
  - `safe_to_ship` → all tests green → output **"CLEAR TO PUSH"** in summary
  - `regressions_found` → at least one critical test failed → output **"BLOCKED"** in summary

Add the verdict word (`BLOCKED` or `CLEAR TO PUSH`) to the RegressionRun's `summary` field so it's machine-readable.

---

## Step 5 — Output

If `verdict: safe_to_ship`:
```
✓ CLEAR TO PUSH
  All N critical tests passed.
  X annotation-covered tests passed.
```

If `verdict: regressions_found`:
```
✗ BLOCKED
  N critical test(s) failed:
  - <test-id>: <failure_message>

  Fix these before pushing.
  → /helpmetest fix to diagnose
```

---

## Done when

- [ ] `RegressionRun` artifact created with `verdict` field set
- [ ] Summary contains either `BLOCKED` or `CLEAR TO PUSH`
- [ ] All critical tests were run
- [ ] All annotation-covered tests for changed files were run
