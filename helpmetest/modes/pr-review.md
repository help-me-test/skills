<!-- llms-description: Branch diff to annotation map to coverage gap report. No test runs. -->

# Mode: pr-review

Gap analysis for a branch before merge. Reads the diff, maps changed files to test coverage via `@helpmetest` annotations, and flags files with no coverage as gaps. **Does NOT run tests** — this is analysis only.

## Orient First

```bash
helpmetest status
helpmetest artifact list --tags "project:<slug>"   # scoped — a bare list spans every project
```

## Announce

After orient, present the plan before reading any diff:

```
## PR review plan

Branch: [current branch vs main]

I will:
1. Read the diff (git diff main...HEAD --name-only)
2. For each changed file: grep for @helpmetest annotations → map to test IDs + status
3. Files with no annotation → flagged as coverage gaps with severity (high/medium/low by path)
4. Produce a CoverageReport artifact with gaps and next actions

No tests will be run — this is analysis only.

Ready to start?
```

Wait for confirmation, then proceed.

**On a codebase without annotations, step 3 flags everything — which is correct, but say so
up front.** Measured 2026-09-25 on this repo: exactly one `@helpmetest` annotation exists
(`app/server/launch.js:1`), and it is stale — its `feature:launch-flow` artifact 404s and
neither of the two test ids it names is among the 143 live tests.

So a CoverageReport that lists every changed file as a gap is an honest reading of an
unannotated codebase, not a bug in this mode. Lead with that fact rather than producing a
wall of identical high-severity gaps: *"this repo has no annotations, so coverage cannot be
inferred from the diff — here is what the tests actually cover instead"* is more use than
twenty rows saying the same thing.

And when an annotation does exist, check its targets resolve before trusting it. It is a
hand-maintained comment with nothing keeping it honest.

---

## Step 1 — Read the branch diff

```bash
git diff main...HEAD --name-only
```

If `main` doesn't exist, try `master`, then fall back to `HEAD~1`:
```bash
git diff master...HEAD --name-only 2>/dev/null || git diff HEAD~1 HEAD --name-only
```

---

## Step 2 — Classify each changed file

For each changed file:

**Has `@helpmetest` annotation:**
1. Parse the annotation to get `feature:<id>` and `tests:<ids>`
2. Call `helpmetest status --id <test-id>` for each test to get current status
3. Record: file → annotation → test IDs → current status (passing/failing/never run)

**No `@helpmetest` annotation:**
1. Record as a **coverage gap**
2. Assign severity based on path:
   - `components/`, `pages/`, `routes/` → `high`
   - `utils/`, `hooks/`, `lib/` → `medium`
   - `config/`, `types/`, `constants/` → `low`

---

## Step 3 — Produce CoverageReport artifact

Fetch the schema first:
```bash
helpmetest artifact schema CoverageReport
```

Create a `CoverageReport` artifact:

**Corrected 2026-09-26 against `artifact schema CoverageReport --json`.** The previous
shape used `scope`, `scenarios_total`, `scenarios_covered`, `coverage_percent`,
`next_actions` and `by_feature[].feature_name`/`scenarios_gap` — none of which exist — and
omitted six required fields. See `modes/coverage.md` for the same template with every
nested shape spelled out.

```json
{
  "type": "CoverageReport",
  "id": "pr-review-<short-timestamp>",
  "content": {
    "name": "PR review — <branch>",
    "description": "Annotation coverage for files changed on <branch> vs main",
    "verdict": "<one sentence: is this branch safe to review, and why>",
    "verdict_status": "ready|at_risk|not_ready",
    "scope_audited": ["files changed on branch vs main"],
    "scope_not_audited": ["everything not touched by this branch"],
    "features_scanned": 0,
    "tests_total": 0,
    "total": { "total": 0, "covered": 0, "skipped": 0, "pct": 0.0 },
    "by_feature": [
      { "feature_id": "<id>", "priority": "high",
        "scenarios": { "total": 0, "covered": 0, "skipped": 0, "pct": 0.0 } }
    ],
    "critical_gaps": [
      { "feature_id": "<id>", "scenario_name": "<scenario>", "priority": "high",
        "risk": "core_journey",
        "implication": "<what ships unguarded if this is wrong>" }
    ],
    "code_gaps": [
      { "path": "<changed file with no annotation>", "surface_name": "<what it does>",
        "risk": "core_journey", "implication": "<what is unprotected>" }
    ],
    "dead_links": [],
    "orphan_tests": [],
    "recommendations": [
      { "title": "Add coverage for <file>", "command": "/helpmetest tdd <file>" }
    ]
  }
}
```

Note `code_gaps` is the right home for "changed file with no `@helpmetest` annotation" —
the old template forced those into `critical_gaps` with a fake `feature_id` of `"gap"`.

Map unannotated changed files into `code_gaps[]` — one entry per file, with `path`, a short `surface_name`, its `risk`, and the `implication` if it ships unguarded. (This line used to say `critical_gaps[]` with `feature_id: "gap"`; `critical_gaps` entries are scenarios belonging to a real Feature, and `code_gaps` exists precisely for code with no Feature behind it.)

---

## Step 4 — Narrate findings

```
PR coverage summary:

Covered (annotation found):
  ✓ src/components/Login.jsx → tests: login-happy-path (passing), login-error (passing)
  ✗ src/utils/auth.js → tests: auth-token-refresh (FAILING — needs attention)

Gaps (no annotation):
  ⚠ src/utils/helpers.js [medium] — no tests
  ⚠ src/pages/Settings.jsx [high]  — no tests

→ /helpmetest tdd to fill the gaps before merging
```

---

## Done when

- [ ] `CoverageReport` artifact created with `critical_gaps[]` populated for each unannotated changed file
- [ ] `by_feature[]` populated for annotated files
- [ ] `next_actions[]` suggests `/helpmetest tdd` for each gap
- [ ] **No tests were run** — this is analysis only
