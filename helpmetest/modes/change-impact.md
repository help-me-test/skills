# Mode: change-impact

Maps a git diff to the tests that cover the changed code. Runs only those tests. Reports coverage gaps for changed files with no `@helpmetest` annotation. Read-and-run — does NOT modify code, tests, or artifacts.

## Orient First

```
helpmetest_status()
helpmetest_search_artifacts({ type: "Tasks" })
```

If a Tasks artifact is in progress for this run, resume it.

## Announce

After orient, present the plan before reading any diff:

**Nothing specified (no files or commit given):**
> "What changed? Give me a commit hash, a file list, or say 'last commit' and I'll run `git diff HEAD~1`."

Wait for the answer.

**Files or commit specified — present the plan:**

```
## Change-impact plan

Source: [git diff HEAD~1 | files: X, Y, Z | commit: abc123]

I will:
1. Read the diff and collect changed files
2. Grep each file for @helpmetest annotations → find affected test IDs
3. Run each affected test and classify: green / regressed / pre-existing
4. Produce a RegressionRun artifact with verdict
5. List any changed files with no annotation as coverage gaps

Estimated: [N annotation tests + critical tests if any]. Ready to start?
```

Wait for confirmation, then proceed.

---

## Step 1 — Read the diff

```bash
git log -1 --stat
git diff HEAD~1 HEAD --name-only
```

Collect the list of changed files. If the user specified a commit range or a list of files directly, use those instead.

---

## Step 2 — Collect affected tests

For each changed file:

1. `grep -n "@helpmetest" <file>` — extract all annotations
2. Parse each annotation: `feature:<id> tests:<t1>,<t2>,...`
3. Collect the union of all test IDs across all annotated changed files
4. For files with NO `@helpmetest` annotation: record them as **coverage gaps** (label with severity: `high` for `components/` or `pages/`, `medium` for `utils/`, `low` for `config/` or `types/`)

---

## Step 3 — Run affected tests

For each test ID collected in Step 2, call `helpmetest_run_test({ id: "<test-id>" })`.

Run them one at a time — **not in parallel** — so results are readable.

After each run, classify the result:
- `green` — passed
- `regressed` — failed now, was passing before the change
- `pre_existing_fail` — failed before AND after (not caused by this change)

Check "was passing before" by looking at `last_run` status from `helpmetest_status` **before** you ran the test in this session.

---

## Step 4 — Produce output artifact

Fetch the schema first:
```
helpmetest_get_artifact_schema({ type: "RegressionRun" })
```

Create a `RegressionRun` artifact:

```json
{
  "type": "RegressionRun",
  "id": "regression-<short-timestamp>",
  "content": {
    "trigger_files": ["<list of changed files>"],
    "selection_method": "annotations",
    "affected_tests": ["<test ids that ran>"],
    "skipped_tests": [],
    "results": [
      {
        "test_id": "<id>",
        "classification": "green|regressed|pre_existing_fail",
        "run_url": "<url from run result>",
        "failure_message": "<one-line summary if failed>",
        "annotation_source": "<file path where annotation was found>"
      }
    ],
    "verdict": "safe_to_ship|regressions_found|pre_existing_only|inconclusive"
  }
}
```

**Verdict rules:**
- `safe_to_ship` — all tests green
- `regressions_found` — at least one `regressed` classification
- `pre_existing_only` — failures exist but all were already failing before
- `inconclusive` — flaky results, no clear pattern

---

## Step 5 — Report coverage gaps

After the artifact, narrate any coverage gaps:

```
Coverage gaps (changed files with no @helpmetest annotation):
- src/utils/formatDate.js [medium] — no tests cover this file
- src/pages/Settings.jsx  [high]   — no tests cover this file
```

Suggest: `→ /helpmetest tdd — write tests for these files`

---

## Done when

- [ ] `RegressionRun` artifact created with all fields populated
- [ ] Every annotated changed file's tests were run
- [ ] Coverage gaps listed for unannotated changed files
- [ ] Verdict reflects actual results
