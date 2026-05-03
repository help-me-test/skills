# Mode: nightly

Scheduled health check. Does two things: (1) runs tests for all existing Features and marks broken ones, (2) discovers new URLs in test tags that have no Feature artifact yet and creates stub Features for them. Run on a schedule or manually to keep the artifact library fresh.

## Orient First

```
helpmetest_status()
helpmetest_search_artifacts({ query: "" })
helpmetest_search_artifacts({ type: "Tasks" })
```

Check auth state before anything:
```
how_to({ type: "authentication_state_management" })
```

You need a valid auth state (`As <StateName>`) for the discovery sub-flow. If none exists, skip Step 3 and note it in the summary.

---

## Step 1 — Health check: run each Feature's tests

1. From `helpmetest_search_artifacts({ query: "" })`, collect all Feature artifact IDs
2. For each Feature, call `helpmetest_get_artifact({ id: "<feature-id>" })` to read its scenarios
3. Collect all test IDs from `scenarios[].test_ids` across all features
4. For each test ID, call `helpmetest_run_test({ id: "<test-id>" })` to get a fresh result

Classify each Feature after running its tests:
- **All tests green** → status: `working`
- **Some tests failing** → status: `partial`
- **All tests failing** → status: `broken`

---

## Step 2 — Update degraded Features

For each Feature whose status changed to `broken` or `partial`:

Call `helpmetest_upsert_artifact` with the Feature's updated `status` field:
```json
{
  "id": "<feature-id>",
  "type": "Feature",
  "content": {
    "...": "all existing fields unchanged",
    "status": "broken"
  }
}
```

**Important:** preserve all existing fields — only update `status`. Fetch the current artifact first to avoid overwriting scenarios or bugs.

---

## Step 3 — Discover new URLs

From all tests returned by `helpmetest_status()`, extract every `url:` tag value.

For each URL found:
1. Check if any existing Feature artifact covers that URL (look at Feature `functional[].given` for the URL, or Feature tags)
2. If NO Feature covers the URL → it's a new page to document

For each uncovered URL:
- Run a lightweight interactive check:
  ```
  As <StateName>
  Go To <url>
  Get Title
  ```
- Create a stub Feature artifact:
  ```json
  {
    "type": "Feature",
    "id": "feature-stub-<slug>",
    "name": "<Page Title> (stub)",
    "content": {
      "goal": "Discovered via nightly — needs full discovery pass",
      "source": "nightly",
      "status": "untested",
      "functional": [],
      "edge_cases": [],
      "gaps": ["Full discovery needed — run /helpmetest discover on this URL"],
      "bugs": []
    }
  }
  ```

---

## Step 4 — Summary

Produce a `Tasks` artifact as the run receipt (use `helpmetest_get_artifact_schema({ type: "Tasks" })` first):

```json
{
  "type": "Tasks",
  "id": "nightly-<date>",
  "content": {
    "overview": "Nightly audit — <date>",
    "tasks": [
      { "id": "1.0", "title": "Health check", "status": "done",
        "description": "N features checked: X healthy, Y partial, Z broken" },
      { "id": "2.0", "title": "New stubs created", "status": "done",
        "description": "N new stub features for uncovered URLs" }
    ]
  }
}
```

Narrate the summary:

```
Nightly audit complete:

Health:
  ✓  N features healthy
  ⚠  Y features degraded (marked partial/broken):
     - feature-checkout: all 3 tests failing
  
New URLs discovered:
  + /settings/billing  → stub feature-stub-billing created
  + /help/getting-started → no auth state available, skipped

→ /helpmetest fix-tests for broken features
→ /helpmetest discover on new stubs for full coverage
```

---

## Done when

- [ ] All Feature artifacts checked and their tests run
- [ ] Degraded Features updated with new status
- [ ] Stub Features created for uncovered URLs
- [ ] Tasks artifact created as run receipt
- [ ] Nothing was deleted — marks only, human decides
