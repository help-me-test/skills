# Mode: report — project health diagnosis

Read-only, layered diagnosis of the current project's HelpMeTest state across 9 phases: triage, auth, tests (with 10-run history + aggregated errors), sync, coverage, code↔test linkage, bugs, artifacts, drift. Produces a tiered 🔴/🟠/🟡 report and ends by asking the user a single binary question that walks them from "what's broken" to "the highest-leverage fix is X — start there?"

This is the QA analogue of an SRE health check: layered phases, stop-the-line on critical findings, narrate every step, no side effects.

## When to use

User says "report", "health check", "is the project ok", "what's broken", "diagnose", "audit my tests", "are my tests actually green", "what state is the suite in", "/helpmetest report".

## What this mode does NOT do

- **No fixes.** Never deletes a test, modifies a Feature, re-auths a state, or runs a test.
- **No discovery.** If the project has no Features, this mode reports that — it doesn't try to fill the gap.
- **Output is recommendations only.** Fixes belong to `tdd` / `fix` / `discover` / etc.

---

## Inputs and dispatch

| Invocation | Behavior |
|------------|----------|
| `/helpmetest report` | Run every phase in order. |
| `/helpmetest report <phase>` | Run only that phase. Valid: `triage`, `auth`, `tests`, `sync`, `coverage`, `code`, `bugs`, `artifacts`, `drift`. |

Synonyms in user text: "linkage" → `sync`, "flaky" → `stability`, "annotations" → `code`, "hygiene" → `artifacts`.

## Announce

Bare `/helpmetest report`:

> "After this you'll know the health of your HelpMeTest project end to end — auth states, test stability over the last 10 runs with aggregated error analysis, Feature↔test sync, code annotation freshness, open bugs, artifact hygiene. I'll surface anything critical immediately, then walk through 9 phases. Read-only — nothing gets modified, no tests run.
>
> Full sweep, or just one phase (triage / auth / tests / sync / coverage / code / bugs / artifacts / drift)?"

Single phase: state what that phase will tell them, then proceed without asking.

---

## Phases — order matters (9 total)

Each phase: gather → classify findings into 🔴/🟠/🟡 → record into the in-memory rollup. Narrate before each phase ("running tests — analyzing last 10 runs with error aggregation") and after ("tests: 74 passing · 2 failing (both chronically broken) · flaky: 3 tests with mixed pass/fail pattern").

### Phase 1 — triage (always first, ≤30s)

Cheap checks that catch the worst states:

```bash
helpmetest status                        # any tests in FAIL right now?
helpmetest artifact list --type Feature  # any Feature with bugs[].severity=critical, unresolved?
```

**Stop-the-line:** if any of these are true, surface to the user *immediately* — one line, then offer to bail out:

- ≥1 test failing on its last run AND tagged `priority:critical`
- ≥1 Feature with a critical unresolved bug
- ≥1 auth state marked broken or last-tested >30 days ago

> "Found a fire: `[<test|feature|auth>]` — `[<one-line summary>]`. Continue with the full report, or stop here so you can address it first?"

If the user says continue, keep going. If they say stop, hand off to the recommended fix mode.

### Phase 2 — auth (early, because broken auth invalidates almost every other test result)

Auth has to be near the top: a broken `Helpmetest` saved state silently breaks every test that uses `As Helpmetest`, and the `tests` phase will report a wave of failures whose real cause is one upstream auth issue. Naming auth first stops that misdirection.

```
how_to({ type: "authentication_state_management" })
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

- **🔴 Chronically Broken** (pass rate <30%): Tests failing majority of time
  - Evidence: Error patterns, error count per type, min/max timestamps across runs

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

- **🟡 Flaky** (pass rate 30-70%): Unreliable signal, unpredictable behavior
  - Evidence: Mixed pass/fail pattern, error types vary per run
- **🟡 Recently Recovered** (last 1-2 pass, 3+ before failed): Dishonest green
  - Evidence: Last N runs show recent success but pattern shows prior failures
- **⚪ Stale** (last run >14 days ago): Test not exercised recently
  - Evidence: Timestamp of last run, current status
- **🟢 Stable** (pass rate ≥90%): Reliable, green
  - Evidence: Consistent passing trend, no failure streaks (pass rate <30%): Tests failing majority of time
  - Evidence: Error patterns, error count per type, min/max timestamps across runs
- **🟠 Flaky** (pass rate 30-70%): Unreliable signal, unpredictable behavior
  - Evidence: Mixed pass/fail pattern, error types vary per run
- **🟠 Recently Recovered** (last 1-2 pass, 3+ before failed): Dishonest green
  - Evidence: Last N runs show recent success but pattern shows prior failures
- **🟡 Stale** (last run >14 days ago): Test not exercised recently
  - Evidence: Timestamp of last run, current status
- **✅ Stable** (pass rate ≥90%): Reliable, green
  - Evidence: Consistent passing trend, no failure streaks

**Per failing test, summarize errors with flakiness score:**
```
❌ Test Name [flakiness: 0.67 — 🟠 FLAKY | 2/10 pass]
  - Timeout (4 runs): "TimeoutError: locator.evaluate: Timeout 10000ms exceeded" [weight 1.5]
  - Assertion (3 runs): "Should Contain: expected 'visible' found 'hidden'" [weight 2.0]
  - Selector (1 run): "locator.evaluate: Error: no matching selector" [weight 1.0]
  - Backend (1 run): "500 Server Error" [weight 1.5]
  - Other (1 run): "Javascript: locator.evaluate: Error: paused=false" [weight 1.0]
  - Score: weighted failures / total runs
```

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
helpmetest artifact list --type Feature   # every feature
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
helpmetest artifact list --type Feature
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

- Memory artifact present? Last updated within 30 days?
- ProjectOverview present?
- ≥1 Persona defined?
- Any Tasks artifacts >7 days old still `in_progress` (abandoned runs)?

Findings:
- 🟠 ProjectOverview missing
- 🟡 Memory artifact missing or >30 days stale, no Persona, abandoned Tasks

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
