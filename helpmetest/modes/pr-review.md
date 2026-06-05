# Mode: pr-review

Gap analysis for a branch before merge. Reads the diff, maps changed files to test coverage via `@helpmetest` annotations, and flags files with no coverage as gaps. **Does NOT run tests** — this is analysis only.

## Orient First

```bash
helpmetest status
helpmetest artifact list
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

```json
{
  "type": "CoverageReport",
  "id": "pr-review-<short-timestamp>",
  "content": {
    "scope": "files changed on branch vs main",
    "features_scanned": N,
    "tests_total": N,
    "scenarios_total": N,
    "scenarios_covered": N,
    "coverage_percent": 0-100,
    "by_feature": [
      {
        "feature_id": "<id>",
        "feature_name": "<name>",
        "scenarios_total": N,
        "scenarios_covered": N,
        "scenarios_gap": N
      }
    ],
    "critical_gaps": [
      {
        "feature_id": "gap",
        "scenario_name": "<filename> — no @helpmetest annotation",
        "priority": "high|medium|low",
        "suggested_mode": "tdd"
      }
    ],
    "dead_links": [],
    "orphan_tests": [],
    "next_actions": [
      {
        "priority": 1,
        "action": "/helpmetest tdd — add coverage for <file>",
        "mode": "tdd"
      }
    ]
  }
}
```

Map unannotated files into `critical_gaps[]` — each gap file becomes one entry with `feature_id: "gap"` and a description containing the filename.

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
