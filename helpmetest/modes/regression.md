# Mode: regression — change-targeted testing

**What this mode does:** given a list of changed source files, find tests that cover those files (via `@helpmetest` annotations or explicit Feature artifact links), run them, report pass/fail. Bounded by the blast radius of the change — faster than a full run, focused on what actually could have broken.

**When to use:** user says "test what I changed", "regression check", "ran after this commit", "fix this and confirm nothing else broke", "I just refactored X — is anything red?"

---

## Inputs

The user must tell you **which files changed** (you don't have shell access, so you can't git diff). Accept any of these shapes:

- A list of paths: *"regression: `app/src/components/Login.jsx`, `app/server/auth.js`"*
- A diff pasted into the task
- A feature area: *"regression on the auth flow"* (then treat all files under `app/**/*auth*` as changed)

## Announce

After orient, present the plan:

**No files provided — ask first:**
> "Which files changed? Give me a list of paths, paste the diff, or name the feature area (e.g. 'auth flow'). I'll find the affected tests from there."

Wait for the answer.

**Files or feature area provided:**

```
## Regression plan

Changed: [file list or feature area]

I will:
1. Grep each changed file for @helpmetest annotations → affected test IDs (method a)
2. Check Feature artifacts for relevant_files matches → additional test IDs (method b)
3. Deduplicate → run the set, priority:critical first
4. Classify each result: green / regressed / pre-existing / flaky
5. Report via Tasks artifact — run URLs included for every test

Estimated: [N] tests. Any suspected regressions will be called out prominently.

Ready to start?
```

Wait for confirmation, then proceed.

## Workflow

### 1. Orient

```bash
helpmetest status
```

Catalog what tests exist before digging.

### 2. Resolve the set of affected tests

Three ways a test can be relevant to a changed file — check in this order:

**(a) `@helpmetest` annotation in the file itself.** Read each changed file and grep-equivalent for `// @helpmetest` or `# @helpmetest`. Annotation format:
```
// @helpmetest feature:<id> tests:<name1>,<name2>,...
```
Collect every test name from every annotation.

**(b) Feature artifact that mentions the file in `relevant_files`.** Search artifacts:
```bash
helpmetest artifact list --type Feature
```
Fetch each feature, check its `relevant_files[].path` against the changed set. For matches, pull the `scenario.test_ids` — those tests are affected.

**(c) Convention-based fallback.** If a changed file's path matches a feature area (e.g. `app/auth/*` → `feature:*auth*`), include tests tagged with that feature. Document this as a fallback — it's noisier than (a) or (b).

Deduplicate. That's your run set.

### 3. Filter by priority

If the run set is huge (>20 tests), prioritize:
- `priority:critical` — always include
- `priority:high` — include
- `priority:medium` — include if not too many
- `priority:low` — include only if the set is small otherwise

Narrate what you're running and what you're skipping.

### 4. Run

For each test in the set, run sequentially or all at once:
```bash
helpmetest test run test-1 test-2 test-3 ...
```

Parallel is faster for ≥3 tests. Sequential makes narration cleaner.

Capture every run URL from the response.

### 5. Classify results

Group by outcome:

- **Green** — passed, nothing to do.
- **Red (suspected regression)** — failed, and the last known state was green. Likely caused by the change. **Document these prominently — they're the signal this mode exists for.**
- **Red (pre-existing)** — failed, and was already red before this change (check run history if available). Flag but de-emphasize.
- **Flaky** — failed but history shows intermittent pass/fail. Re-run once to confirm.

### 6. Report via Tasks artifact

The Tasks artifact (per modes/agent.md lifecycle rules) captures the run. Structure:

- `links` → every Feature whose tests were included
- `relevant_files` → the changed files the user named (copy them verbatim)
- Top-level `notes` → the trigger (which files, which feature area) and the run-set size + priority filter applied
- One subtask per test run outcome group:
  - Subtask: "Ran N tests — M green, K red-suspected-regression, L pre-existing, J flaky"
  - Each red-suspected-regression test gets its own subtask in `notes` with: test id, failure message, the file it's annotated from, and the run URL.

### 7. Evidence

Every test that ran → its run URL must appear in the notes. Don't summarize "all passed" — paste the URLs the tool gave you. Reviewer should be able to click through to any of them.

## What NOT to do

- **Do not re-run everything.** If you run the full suite, you missed the point of this mode. Limit the set based on annotations + feature links.
- **Do not fix red tests.** If one fails, **do not route to `fix`** unless the user said so. Regression's job is to report, not repair.
- **Do not create new tests for uncovered code.** That's `tdd` or `coverage`.

## Handoff

End with a specific next action depending on results:

- Any red-suspected-regression: *"N tests regressed after your change — run `/helpmetest fix` on them, or inspect manually."*
- All green: *"All N affected tests passed. Change is safe to ship from a test perspective."*
- Mostly pre-existing failures: *"Your change didn't break new tests. N tests were already red — unrelated to this work."*

## If the user's change doesn't map to any known tests

This is a coverage signal. Report: *"No tests are annotated against the files you changed. Coverage gap — run `/helpmetest coverage` on the affected feature area to see if anything is scheduled but unwritten."*
