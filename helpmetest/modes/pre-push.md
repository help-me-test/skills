# Mode: pre-push

Runs the minimum set of tests needed to gate a push: all `priority:critical` tests plus tests covering files changed since the last push. Binary output — BLOCKED or CLEAR TO PUSH. Does NOT push, does NOT fix anything.

## Orient First

```
helpmetest_status()
```

Snapshot the current state of critical tests before running anything.

## Announce

After orient, before running anything:

> "After this you'll get a binary verdict — BLOCKED or CLEAR TO PUSH — based on all priority:critical tests plus tests covering your changed files. Takes [N critical tests + M annotation-covered] runs. Starting now."

Then proceed immediately — this mode has no scope ambiguity.

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
Call `helpmetest_status()`. Collect every test with tag `priority:critical`.

**Set B — annotation-covered tests:**
For each file from Step 1, `grep -n "@helpmetest"` and collect referenced test IDs.

Run the **union** of Set A ∪ Set B (deduplicated).

---

## Step 3 — Run the tests

For each test ID, call `helpmetest_run_test({ id: "<test-id>" })` one at a time.

Track which tests pass and which fail. A critical test failing is a blocker regardless of cause.

---

## Step 4 — Produce output artifact

Fetch the schema first:
```
helpmetest_get_artifact_schema({ type: "RegressionRun" })
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
  → /helpmetest fix-tests to diagnose
```

---

## Done when

- [ ] `RegressionRun` artifact created with `verdict` field set
- [ ] Summary contains either `BLOCKED` or `CLEAR TO PUSH`
- [ ] All critical tests were run
- [ ] All annotation-covered tests for changed files were run
