<!-- llms-description: Read-only project health diagnosis across test stability, coverage, sync and drift. -->

# Mode: report — project health diagnosis

Read-only, layered diagnosis of the current project's HelpMeTest state across 9 phases: triage, auth, tests (with 10-run history + aggregated errors), sync, coverage, code↔test linkage, bugs, artifacts, drift. Produces a tiered 🔴/🟠/🟡 report and ends by asking the user a single binary question that walks them from "what's broken" to "the highest-leverage fix is X — start there?"

This is the QA analogue of an SRE health check: layered phases, stop-the-line on critical findings, narrate every step, no side effects.

## When to use

User says "report", "health check", "is the project ok", "what's broken", "diagnose", "audit my tests", "are my tests actually green", "what state is the suite in", "/helpmetest report".

## What this mode does NOT do

- **No fixes.** Never deletes a test, modifies a Feature, re-auths a state, or runs a test.
- **No discovery.** If the project has no Features, this mode reports that — it doesn't try to fill the gap.
- **Output is recommendations only.** Fixes belong to `tdd` / `fix` / `discover` / etc.

## Workflow

1. **Announce** (below) — state what the user will know after this, then begin immediately.
2. **Run each phase in order** (§Phases below) — 9 phases: triage → auth → tests → sync → coverage → code → bugs → artifacts → drift. Or run only the phase named in the invocation (`report <phase>`).
3. **Stop-the-line on critical findings** — a 🔴 in an early phase (triage, auth) still lets later phases run, but gets surfaced immediately, not buried until the final summary.
4. **Produce the tiered report** (🔴/🟠/🟡) and end with one binary question pointing at the highest-leverage fix.

---

## Inputs and dispatch

| Invocation | Behavior |
|------------|----------|
| `/helpmetest report` | Run every phase in order. |
| `/helpmetest report <phase>` | Run only that phase. Valid: `triage`, `auth`, `tests`, `sync`, `coverage`, `code`, `bugs`, `artifacts`, `drift`. |

Synonyms in user text: "linkage" → `sync`, "flaky" → `stability`, "annotations" → `code`, "hygiene" → `artifacts`.

## Announce

Bare `/helpmetest report`:

> "After this you'll know the health of your HelpMeTest project end to end — auth states, test stability over the last 10 runs with aggregated error analysis, Feature↔test sync, code annotation freshness, open bugs, artifact hygiene. I'll surface anything critical immediately, then walk through 9 phases. Read-only — nothing gets modified, no tests run."

Announce, then immediately begin Phase 1. If the user scoped to a single phase (e.g. `report tests`), state what that phase will tell them, then proceed — do not wait for confirmation.

---

## Phases — order matters (9 total)

Each phase: gather → classify findings into 🔴/🟠/🟡 → record into the in-memory rollup. Narrate before each phase ("running tests — analyzing last 10 runs with error aggregation") and after ("tests: 74 passing · 2 failing (both chronically broken) · flaky: 3 tests with mixed pass/fail pattern").

### Phase 1 — triage (always first, ≤30s)

Cheap checks that catch the worst states:

```bash
helpmetest status                        # any tests in FAIL right now?
helpmetest artifact list --type Feature --tags "project:<slug>"  # any Feature with bugs[].severity=critical, unresolved?
```

**A red line in `status` is a claim, not a finding — and so is one green re-run.** Re-run
the test, then read `helpmetest test view <id> --errors` for its pass/fail ratio and the
error body. Measured 2026-09-26: `playground-forms` showed `1 passed, 499 failed` since
2026-09-19, and that one pass was a manual re-run. Reporting either the stale red or the
lucky green as the verdict sends someone to debug nothing, or hides a failure recurring
every ten minutes.

Also: `status` is workspace-wide and has no project filter. Measured 2026-09-26 —
`143 total`, `59❌`, across 6 projects. Filter the lines by `#project:<slug>` before
counting anything, or the report describes strangers' software.

**Stop-the-line:** if any of these are true, surface to the user *immediately* — one line, then offer to bail out:

- ≥1 test failing on its last run AND tagged `priority:critical`
- ≥1 Feature with a critical unresolved bug
- ≥1 auth state marked broken or last-tested >30 days ago

> "Found a fire: `[<test|feature|auth>]` — `[<one-line summary>]`. Continue with the full report, or stop here so you can address it first?"

If the user says continue, keep going. If they say stop, hand off to the recommended fix mode.

### Phase 2 — auth (early, because broken auth invalidates almost every other test result)

Auth has to be near the top: a broken `Helpmetest` saved state silently breaks every test that uses `As Helpmetest`, and the `tests` phase will report a wave of failures whose real cause is one upstream auth issue. Naming auth first stops that misdirection.

```bash
helpmetest search "setup-auth"
helpmetest status
```

For each saved state:
- Is the `setup-auth-<State>` test passing on its last run?
- When did a test last successfully use `As <State>`? (search recent agent runs / test runs that include `As <State>`)
- Any state that no test references? → orphan
- Any test referencing `As <State>` for a state that isn't saved? → broken ref

Findings:
- 🔴 setup-auth test failing → every test using that state is suspect
- 🟠 state last used >14 days ago → stale, may rot
- 🟡 orphan state (no tests use it) or unused state

### Phase 3 — tests (status + stability + error analysis)

**Single-step comprehensive test report** combining current status, historical stability (last 10 runs), and aggregated error analysis.

```bash
helpmetest status --history 10
```

**Read that output as text, not JSON.** Verified 2026-09-25: `--history` inlines the runs
under each row in the human-readable output (232 lines → 356 lines with `--history 3`), but
**`--json` ignores it entirely** — the row keys are identical with and without the flag:
`id, name, status, last_run, duration, stability, stability_runs, tags, content, emoji`.
There is no per-run array in the JSON. An agent that reaches for `--json` here gets one
aggregate `stability` number and no error history, and would have to invent the per-run
analysis this phase asks for.

The text rows look like this — status, timestamp and the error, per run:

```
❌ 🔴   0/100    10s  Lite-mode multi-tab replay loads without duplicate tab containers  #priority:critical …
    ❌ 2026-09-25 17:50:20  Go To: TimeoutError: page.goto: Timeout 10000ms exceeded.
    ❌ 2026-09-25 17:45:27  Go To: TimeoutError: page.goto: Timeout 10000ms exceeded.
    ❌ 2026-09-25 17:40:17  Go To: TimeoutError: page.goto: Timeout 10000ms exceeded.
```

Note what that particular pattern means before filing three findings: the same error, on
several tests, minutes apart, is one broken dependency — not N broken tests. Cluster by
error text and timestamp first (see `modes/shared.md` §1 on re-running before diagnosing).

For each test, extract:
- **Status**: passing, failing, never-run, stale (>14 days)
- **Pass rate**: from last 10 runs (e.g., "7/10" = 70%)
- **Error messages**: all 10 run errors grouped by type:
  - Timeout: "TimeoutError: locator.evaluate: Timeout exceeded"
  - Assertion: "Should Contain: X does not contain Y"
  - Selector: "locator.evaluate: Error: element not found"
  - Backend: "500 Server Error", network timeouts
  - Auth: "401 Unauthorized", redirect to login
  - Logic: "Javascript: Error", variable undefined, etc.

**Group tests by stability class:**

| Class | Pass rate over the last N runs | Evidence to cite |
|---|---|---|
| 🔴 **Chronically Broken** | < 30% | error patterns, error count per type, min/max timestamps across runs |
| 🟠 **Flaky** | 30-70% | mixed pass/fail pattern, error types vary per run |
| 🟠 **Recently Recovered** | last 1-2 pass, 3+ before failed | a dishonest green — recent success over a prior failure streak |
| ⚪ **Stale** | last run > 14 days ago | timestamp of last run, current status |
| 🟢 **Stable** | ≥ 90% | consistent passing trend, no failure streaks |

This table used to appear **twice**, split by the Flakiness Score section below, with the
two copies disagreeing on every icon (🟡 vs 🟠 for Flaky, 🟢 vs ✅ for Stable, ⚪ vs 🟡 for
Stale) — and the second copy had lost its "Chronically Broken" heading entirely, grafting
that class's `< 30%` definition onto Stable's evidence line. A report is graded on its
severity icons; two contradictory legends make the output unreadable and unreviewable.
One table now, and the severity ladder matches the 🔴/🟠/🟡 rubric used in the snapshot.

---

### Flakiness Score (quantitative)

For each test with ≥5 runs of history, compute:

**Flakiness Score = (Failure Count × Failure Weight) / Total Runs**

| Failure Type | Weight | Reason |
|-------------|--------|--------|
| Timeout | 1.5 | Usually environment, sometimes code |
| Assertion | 2.0 | Likely test logic or real regression |
| Selector/Element | 1.0 | UI change, usually fixable |
| Network | 0.5 | Transient, not test's fault |
| Server Error | 1.5 | Could be app bug or test dependency |
| Auth | 2.0 | Broken state, cascading failures |

**Flakiness thresholds:**
- **0.0-0.2:** 🟢 Stable (occasional transient failure)
- **0.2-0.5:** 🟡 Suspicious (watch, investigate)
- **0.5-0.8:** 🟠 Flaky (unreliable, fix or quarantine)
- **0.8-1.0:** 🔴 Critical (nearly always fails, likely test infrastructure issue)

**Action:**
- Score ≥0.5 on `priority:critical` → immediate fix required
- Score ≥0.8 any priority → quarantine or delete (not worth maintaining)
- Score 0.2-0.5 → document root cause, schedule fix

**Per failing test, classify each error using the fixed categories in `references/failure-categories.md`, summarize with flakiness score:**
```
❌ Test Name [flakiness: 0.67 — 🟠 FLAKY | 2/10 pass]
  - timing (4 runs): "TimeoutError: locator.evaluate: Timeout 10000ms exceeded" [weight 1.5]
  - assertion_failure (3 runs): "Should Contain: expected 'visible' found 'hidden'" [weight 2.0]
  - element_not_found (1 run): "locator.evaluate: Error: no matching selector" [weight 1.0]
  - api_or_backend (1 run): "500 Server Error" [weight 1.5]
  - unknown (1 run): "Javascript: locator.evaluate: Error: paused=false" [weight 1.0]
  - Score: weighted failures / total runs
```

**Aggregate across all failing tests** into a one-line category summary the user can scan at a glance, e.g. `3 element_not_found · 2 timing · 1 api_or_backend · 1 unknown` — this is the failure-category stat surfaced in the final report, not just per-test detail.

Findings:
- 🔴 chronically broken test on `priority:critical`
- 🔴 failing test on `priority:critical`
- 🟠 chronically broken test (any priority)
- 🟠 flaky test (any priority)
- 🟠 recently recovered (test with recent success but prior failures)
- 🟠 failing test on lower priority
- 🟠 never-run test on `priority:critical`
- 🟡 stale test (>14 days), never-run on lower priority

### Phase 4 — sync (test ↔ Feature linkage)

Every Feature has at least one scenario with at least one populated `test_ids[]`?
Every test referenced in `scenario.test_ids[]` actually exists in `helpmetest status`?
Every test in `helpmetest status` is referenced by at least one Feature scenario?

```bash
helpmetest artifact list --type Feature --tags "project:<slug>"   # every feature in THIS project
helpmetest status                          # every test
# for each feature → helpmetest artifact get <id> to read scenarios
```

Build 4 lists:
- Features with **no tests** at all
- Scenarios with **no tests** (scenarios within a Feature where `test_ids` is empty)
- **Orphan tests** (test exists, no Feature scenario references it)
- **Broken refs** (Feature scenario references a `test_id` that doesn't exist)

Findings:
- 🔴 broken ref on a `priority:critical` scenario
- 🟠 Feature with zero coverage, broken ref on any scenario
- 🟡 orphan test, scenario with no test on lower priority

### Phase 5 — coverage

Per Feature, list scenarios without tests, ranked by priority. Cross-reference with Phase 5 to avoid duplicate findings.

Snapshot line: "X of Y scenarios have tests · Z Features have zero coverage."

Findings:
- 🟠 Feature with zero coverage and any `priority:critical` scenario
- 🟡 individual uncovered scenarios on lower priority

### Phase 6 — code (gated on code access)

**First, detect code access:**

```bash
git rev-parse --show-toplevel 2>/dev/null
```

If non-empty → run the phase. If empty/error → skip the phase, record one line in the final report: *"Code-aware checks skipped — not running from a project directory."*

**If code is present:**

```bash
grep -rn "@helpmetest" --include="*.{js,jsx,ts,tsx,py,rb,go}" .
```

For each `@helpmetest feature:<id> tests:<id1>,<id2>` annotation:
- Does the named feature artifact still exist?
- Does each named test still exist? (cross-reference Phase 3's test list)
- Are those tests passing?

Heuristic gap detection (low-confidence, label as such):
- Files in dirs where adjacent files have annotations, but this file has none
- Route handlers / page components / API endpoint files without annotations

Findings:
- 🔴 annotation references a deleted test/feature (broken ref in production code)
- 🟠 annotation references a chronically failing test (the comment promises coverage that doesn't exist)
- 🟡 heuristic gap — file probably needs annotations

### Phase 7 — bugs (Feature artifact `bugs[]` audit)

```bash
helpmetest artifact list --type Feature --tags "project:<slug>"
# for each → helpmetest artifact get <id> to read content.bugs[]
```

Aggregate every bug across all Features. For each bug:
- severity (critical / major / minor)
- age (created_at vs now)
- has `repro_steps`?
- is the Feature's tests for that scenario currently passing? (a critical unresolved bug whose tests pass means the bug isn't guarded)

Findings:
- 🔴 critical unresolved bug whose related test currently passes (false-green — the test doesn't actually cover the bug)
- 🟠 critical unresolved bug, any major bug >7 days old
- 🟡 minor bugs >30 days old, bugs without `repro_steps`

### Phase 8 — artifacts (hygiene)

- Memory artifact present, and do its entries still hold? Each entry has `category` + `lesson` (+ optional `tags`, `linked_artifact_ids`, `added_at`) — see `references/cli-contracts.md`. **There is no `confidence` or `last_verified` field**; this step used to tell you to check both, verified absent against the live schema 2026-09-25. With no freshness signal recorded, spot-check the entries that would do damage if wrong — selectors and timings — against the live app, and report those by name.
- ProjectOverview present?
- ≥1 Persona defined?
- Any Tasks artifacts >7 days old still `in_progress` (abandoned runs)?

Findings:
- 🟠 ProjectOverview missing
- 🟡 Memory artifact missing, or entries whose selector/timing claims no longer match the live app — name the specific entries and what you observed instead, not just a count. (Do not grade on `confidence`/`last_verified`: those fields do not exist.)

### Phase 9 — drift (style/discipline)

Read every test's body (sample if there are >100 tests). Flag:
- Tests that re-authenticate inside the body instead of using `As <State>`
- Tests <5 meaningful steps
- Tests that only assert presence (no action → result structure)
- Tests without a `priority` field
- Features without scenarios

Findings:
- 🟡 (drift findings are always 🟡 — they're style violations, not breakage)

---

## Final tiered report

After all selected phases, produce the rollup. Mirrors k8s-health's structure.

```
# 🎯 HelpMeTest Project Health: [HEALTHY | DEGRADED | CRITICAL]

## 🔴 Immediate (act now)
- [Phase] [Component] → Problem → Evidence (specific test/feature/file id) → Fix mode

## 🟠 Warnings (act this week)
- (same shape)

## 🟡 Drift (act when you can)
- (same shape)

## Snapshot
- Tests: X passing / Y failing / Z never-run / W stale
- Stability: A flaky · B chronically broken · C recently recovered (dishonest greens)
- Features: M total · N with full coverage · O with gaps
- Auth states: K total · L stale · P broken
- Bugs (open): critical X · major Y · minor Z
- Code annotations: scanned R files · S broken refs (or "skipped — no code access")
```

Severity rule:
- 🔴 — anything that means the suite is **lying** (broken ref, chronically broken on critical, false-green on critical bug, broken auth)
- 🟠 — meaningful unreliability (flaky tests, stale auth, zero-coverage Feature, recent regression)
- 🟡 — drift, hygiene, cosmetic

---

## Output artifact: `ProjectHealthReport`

Persist a `ProjectHealthReport` artifact per run. This is the substantive deliverable; the enclosing Tasks artifact is the lifecycle receipt.

**First, fetch the schema** (always — required fields can change):

```bash
helpmetest artifact schema ProjectHealthReport
```

Then create with `helpmetest artifact upsert`:

- `id: "report-<ISO-date>-<short-hash>"` — new id per run, never overwrite
- `type: "ProjectHealthReport"`
- `content.scope:` `"all phases"` for a full sweep, or the phase name (e.g. `"tests"`) for a sub-mode invocation
- `content.severity:` `HEALTHY` only if `findings` is empty; `CRITICAL` if any `severity:critical` finding; otherwise `DEGRADED`
- `content.phases_run:` the phases you actually executed, in order
- `content.phases_skipped:` array of `{phase, reason}` for phases you intentionally skipped (most common: code phase, reason "not running from a project directory")
- `content.findings:` flat list of every flagged item across all phases. Each finding: `{phase, severity, summary, evidence, recommended_mode, recommended_scope}`. Don't truncate — even 🟡 drift findings belong here; the artifact is the audit trail.
- `content.snapshot:` the aggregate counts block (matches the Snapshot section of the in-chat report)
- `content.recommendation:` `{mode, scope, why}` — the same content used in the closing remediation question. If `severity == HEALTHY`, set `mode: "none"` and `scope: null`.
- `content.links:` `[<enclosing-tasks-id>, <every feature id you read>]`. The server resolves reverse edges — don't double-upsert Tasks.

**`recommended_mode` and `recommendation.mode` are a closed enum, and it is not the mode
names you write in chat.** Measured 2026-09-26:

```
✗ 422: findings.0.recommended_mode
  Input should be 'fix-tests', 'tdd', 'discover', 'validate', 'coverage',
  'ui-review', 'api-testing', 'regression', 'onboard', 'manual' or 'none'
```

So the remediation line says `/helpmetest fix <test-id>` while the artifact field must say
**`fix-tests`**; likewise `ui-review` and `api-testing`, not `ui` and `api`. Writing the
chat name into the artifact is rejected, and it is the natural mistake because the section
above tells you to recommend `/helpmetest fix`. Verified both ways: `fix` rejected,
`fix-tests` saved.

Two notes on that list: it still contains `onboard`, which is no longer a mode in this
skill (bare `/helpmetest` handles new projects) — do not use it. And `manual` / `none` are
the escape hatches when no mode owns the finding.

Subsequent runs produce new artifacts; comparing them over time is how drift is tracked (out of scope for this mode, but the data shape supports it).

---

## Closing remediation conversation — required

After printing the report, **do not exit**. The user must leave with a clear next step.

Compute the recommendation:
1. If any 🔴 → pick the highest-impact critical finding. Recommend the mode that owns it:
   - Failing critical test → `/helpmetest fix <test-id>`
   - Broken auth → `/helpmetest fix setup-auth-<State>` (or re-create the state)
   - Broken code annotation → `/helpmetest tdd` to update the annotation
   - Critical false-green bug → `/helpmetest tdd` to write the test that should have failed
2. Else if any 🟠 → pick the highest-impact warning, same logic.
3. Else if any 🟡 → offer "want to clean these up now or skip?"
4. Else → "Project's healthy. Anything else?"

Format (one binary question, recommended path attached):

> "Highest-leverage fix: **`<mode> <scope>`** — `<one sentence why this matters most>`.
>
> Start there now, or pick a different finding from the report?"

The question MUST be a single binary choice. Not a menu of all findings — that's what the report is for.

---

## Done when

- [ ] Master Tasks artifact created at start; one subtask per phase you chose to run
- [ ] Each phase narrated before/after; findings classified into 🔴/🟠/🟡
- [ ] Stop-the-line check fired (or explicitly noted as clean) before continuing past triage
- [ ] Run history (last 10) actually analyzed in the tests phase with error aggregation (not just last result)
- [ ] Code phase ran iff `git rev-parse --show-toplevel` succeeded; skip noted in the report otherwise
- [ ] Final tiered report printed
- [ ] Report (or fallback Tasks) artifact persisted with `links[]` populated
- [ ] Closing remediation question asked — single binary, with a concrete recommended next mode

## What NOT to do

- **Do not run tests.** Read-only.
- **Do not modify Features, tests, auth states, or annotations.** This mode reports; it doesn't repair.
- **Do not skip history analysis in the tests phase even if everything's green on last run.** Stability over last 10 runs is the whole point — catches flaky tests and recently recovered false-greens.
- **Do not exit silently.** The closing remediation question is mandatory.
- **Do not list every drift finding individually in chat.** Aggregate counts in the snapshot; the artifact has the full list.
