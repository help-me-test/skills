# Mode: coverage — gap analysis

**What this mode does:** read every Feature artifact and every test, produce the coverage matrix, flag the gaps. No test runs, no browser automation — this is pure analysis that answers "what isn't tested?"

**When to use:** user says "what's not tested", "coverage gaps", "missing tests", "audit coverage", "which priority:critical scenarios have no tests".

**Output artifact:** this mode produces a `CoverageReport` artifact — that is the deliverable. The enclosing Tasks artifact (from modes/agent.md lifecycle) is the lifecycle receipt; the CoverageReport is the substantive result. Both get created per run. Get the authoritative schema with `helpmetest_get_artifact_schema({ type: "CoverageReport" })` before building.

---

## Inputs

- Optional filter: a Feature artifact id, a tag (`project:X`, `priority:critical`), or a feature area.
- Default (no filter): all Feature artifacts in the project.

If the user's task names a feature or priority, filter to that. Otherwise scan everything.

## Announce

After orient, present the plan before scanning:

**No filter given:**

```
## Coverage plan

Scope: all [N] Feature artifacts, [M] tests total

I will:
1. Build a scenario → test map across all features
2. Classify each scenario: Covered / Gap / Dead link / Under-covered
3. Find orphan tests (tests not linked to any scenario)
4. Produce a CoverageReport artifact with critical_gaps[] ranked by priority

Recommended: start with priority:critical and priority:high gaps — those are
the flows that hurt most when they break silently.

Full scope, or critical/high only?
```

Wait for scope answer.

**Filter given (feature area or priority):**

```
## Coverage plan

Scope: [filter — e.g. priority:critical | feature-auth | project:checkout]
Artifacts in scope: [N] features, [M] tests

I will:
1. Map scenarios → tests for the filtered set
2. Classify: Covered / Gap / Dead link / Under-covered
3. Produce a CoverageReport for the scoped area

Ready to start?
```

Wait for confirmation, then proceed.

## Workflow

### 1. Orient

```
helpmetest_search_artifacts({ type: "Feature" })
helpmetest_status({ testsOnly: true })
```

Count what you're working with: N features, M tests. Narrate the numbers before you dig in.

### 2. Build the scenario → test map

For each Feature artifact, fetch full content:
```
helpmetest_get_artifact({ id: "<feature-id>" })
```

Extract each scenario (`content.functional[]`, `content.edge_cases[]`) — capture:
- Scenario `name`
- Scenario `tags` (especially `priority:<level>`)
- Scenario `test_ids` (the link back to tests)

For each entry, classify:
- **Covered** — `test_ids` is non-empty AND every id in it corresponds to an existing test (check against the test list from step 1).
- **Gap** — `test_ids` is empty.
- **Dead link** — `test_ids` contains an id that doesn't exist as a test.
- **Under-covered** — scenario has 1 test but you'd expect 2+ (e.g. `priority:critical` scenario with only a happy-path test, no error path).

### 3. Find orphan tests

Cross-check the test list against all `scenario.test_ids` references. Any test id not referenced by any scenario is an orphan.

### 4. Produce the CoverageReport artifact

This is the deliverable. Create it with `helpmetest_upsert_artifact` using `type: "CoverageReport"`. Required fields per the schema (fetch with `helpmetest_get_artifact_schema({ type: "CoverageReport" })`):

```json
{
  "id": "coverage-<ISO-date>-<short-hash-of-scope>",
  "type": "CoverageReport",
  "name": "Coverage gap scan — <scope>",
  "content": {
    "name": "<same>",
    "description": "<one paragraph: scope, what was scanned, overall verdict>",
    "scope": "<'all features' | 'features tagged X' | 'feature <id>'>",
    "features_scanned": <int>,
    "tests_total": <int>,
    "scenarios_total": <int>,
    "scenarios_covered": <int>,
    "coverage_percent": <float 0-100>,
    "by_feature": [
      { "feature_id": "...", "priority": "critical|high|medium|low|null",
        "scenarios_total": <int>, "scenarios_covered": <int>,
        "scenarios_gap": <int>, "scenarios_dead_link": <int>,
        "notes": "optional one-line" }
    ],
    "critical_gaps": [
      { "feature_id": "...", "scenario_name": "...", "priority": "critical|high|medium|low",
        "user_impact": "<one sentence of what gets missed if this silently breaks>" }
    ],
    "dead_links": [
      { "feature_id": "...", "scenario_name": "...", "missing_test_id": "..." }
    ],
    "orphan_tests": [
      { "test_id": "...", "name": "...", "tagged_feature": "feature-id-or-null",
        "status": "PASS|FAIL|UNKNOWN",
        "suggestion": "link to <feature>.<scenario> | remove | rewrite" }
    ],
    "next_actions": [
      { "mode": "fix-tests|tdd|discover|manual|other",
        "description": "<what to do, scoped to which items>" }
    ]
  }
}
```

Don't include scenarios that are fully covered in `critical_gaps` — only list gaps. Don't truncate the arrays; list every row. If the scope is huge (>50 features), shrink the scope with a filter rather than summarizing — partial data in a full-structured artifact is more useful than complete data in prose.

### 5. Populate links on the CoverageReport

When you create the CoverageReport, set its `content.links` to **every related artifact id**: the enclosing Tasks artifact and every Feature you scanned. That's the only place the links need to live — the server computes reverse edges, so the Tasks detail page will automatically show the CoverageReport as a linked chip. Don't double-upsert the Tasks artifact just to add the CoverageReport id.

```
content.links = ["<tasks-artifact-id>", "feature-a", "feature-b", ...]
```

### 6. Close out the Tasks artifact

Mark subtasks `done` with notes pointing at the CoverageReport id: *"Coverage report produced: `<coverage-report-id>`."* Don't duplicate the report contents in the Tasks artifact — the report IS the report, the Tasks artifact just tracks lifecycle.

### 6. Evidence

The evidence is the CoverageReport artifact itself — structured, queryable, complete. Every claim in it maps to a concrete field. No screenshots needed; no test runs.

## What NOT to do

- **Do not run tests.** This mode is read-only.
- **Do not create new Feature artifacts.** Use `discover` for that.
- **Do not write tests to fill gaps.** Produce the report; the user decides what to do next (probably invoking `/helpmetest tdd` per gap).
- **Do not modify Feature artifacts.** You're a reporter, not an editor.

## Handoff

The final report should end with: *"Next action: run `/helpmetest tdd` against the N `priority:critical` gaps above. Dead links need decisions from you."*

## Report quality — what counts as useful

The CoverageReport's `critical_gaps[]` and `next_actions[]` arrays are what a reviewer reads first. Make them specific:

❌ `user_impact: "test is missing"` — useless
❌ `user_impact: "coverage gap"` — useless
✅ `user_impact: "users whose card is declined silently see a blank page instead of an error — they become support tickets"`

❌ `next_actions[0].description: "write more tests"` — useless
✅ `next_actions[0].description: "run /helpmetest tdd on the 3 priority:critical gaps above (payment-declined, session-expired, empty-results)"`

The CoverageReport is machine-queryable and human-readable at the same time. Make both uses work.
