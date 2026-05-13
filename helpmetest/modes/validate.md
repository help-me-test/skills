# Mode: validate — test quality review

**What this mode does:** read one or more tests and score them against the `/tdd` quality rules. Produce a specific, actionable critique — which rules each test breaks, which rewrites would fix them. This is the "should this test exist?" review, not the "is this test green?" check.

**When to use:** user says "is this test any good", "validate these tests", "review the test I just wrote", "score our tests", "audit the suite", "what would you rewrite".

---

## Inputs

- A specific test id: *"validate broken-example-title"*
- A filter: *"validate all priority:critical tests"*, *"validate tests for feature-auth"*
- Default (no filter): validate every test in the project (cap at 20 and report which you scored).

## Announce

After orient, present the plan before scoring:

**No filter given:**

```
## Validate plan

Scope: [N] tests total in the project

I will score each test against 10 quality rules (R1–R10):
  R1 asserts outcome  R2 5+ steps     R3 PM-readable docs
  R4 FakeMail         R5 As <State>   R6 no blocked patterns
  R7 stable selectors R8 complete tags R9 good name  R10 linked to Feature

Each test gets a grade A–F. D/F grades get a concrete rewrite suggestion.
Output: Tasks artifact with one subtask per test, grade + failed rules + fix.

Recommended: start with priority:critical — if those are weak, everything else is moot.

Critical tests first, or full suite?
```

Wait for scope answer.

**Specific test or filter given:**

```
## Validate plan

Scope: [test-id | filter] — [N] tests

Scoring against R1–R10. Each FAIL gets a specific rewrite suggestion.
Output: Tasks artifact with grade + evidence per test.

Ready to start?
```

Wait for confirmation, then proceed.

## Workflow

### 1. Orient

```
helpmetest_status({ testsOnly: true })
```

Know the scope. Narrate how many tests you'll review before starting.

### 2. For each test in scope — fetch its content

```
helpmetest_status({ id: "<test-id>" })  // includes the test body in `content`
```

Read:
- `content` — the RF keywords
- `description` — the [Documentation] Given/When/Then/Risk
- `tags` — project, feature, persona, priority, url
- Name

### 3. Score against the /tdd rulebook

For each test, check the rules below. Each rule is either PASS, FAIL, or N/A. Document the evidence (the specific line or the absence of a specific thing).

**R1 — Asserts an outcome, not presence.**
- FAIL if the test only clicks/navigates without a final assertion on data, state, or visible outcome.
- FAIL if the only assertion is `Should Be Visible` or `Wait For Element` on a selector — those prove presence, not function.
- PASS when there's at least one `Should Be Equal`, `Should Contain`, `Should Match`, data check, or state query.

**R2 — 5+ meaningful steps.**
- Count non-trivial keyword lines. `Go To`, `Fill Text`, `Click`, `Get Title`, assertions all count. `Sleep`, `Log`, comments don't.
- FAIL if <5 meaningful steps — the test is too shallow.

**R3 — Documentation has Given/When/Then/Risk, PM-readable.**
- FAIL if any of the four lines is missing from `[Documentation]`.
- FAIL if any line contains CSS selectors (`.btn`, `#id`), DOM attribute paths (`div[data-id]`), JS internals (`window.*`, variable names), or RF keyword names. The description must read for a product manager, not a developer.
- FAIL if Given is vague (*"user is logged in"* without stating precondition detail) — no better than no description.
- PASS when each line is concrete and the Risk names a specific user complaint.

**R4 — Uses FakeMail for emails.**
- N/A if no email field involved.
- FAIL if test hardcodes `test@example.com` or similar — these fail on second run (account already exists).
- FAIL if test constructs emails like `user_${timestamp}@example.com` instead of using `Create Fake Email` / `Create Email And Fill`.
- PASS when `Create Fake Email` or `Create Email And Fill` is used AND `Delete Email` is in teardown or explicit cleanup.

**R5 — Uses `As <StateName>` for auth, not re-login.**
- N/A if feature doesn't require auth.
- FAIL if the test fills login form, clicks login, waits for dashboard — that's re-auth per run. Use `Save As` once, `As <State>` in every test.
- PASS when `As <StateName>` is the first meaningful line after `Go To`.

**R6 — No blocked patterns.**
- FAIL if test uses `Evaluate  ...__import__(...)` — sandbox blocks it.
- FAIL if test uses `Evaluate  lambda ...` — likely blocked.
- FAIL if test uses `Sleep  X` without a one-line comment explaining *why* (animation, network delay). Unjustified sleep is a flaky-test generator.
- PASS when no blocked patterns and no unjustified sleep.

**R7 — Selectors prefer role/text/testid, not CSS fragility.**
- PREFER: `text=<visible text>`, `role=<role>`, `[data-testid='...']`, `[aria-label='...']`.
- AVOID: chained class selectors (`.a.b.c`), nth-child, deep descendants (`> div > span`).
- FAIL if >50% of selectors are the fragile kind.
- PASS when robust selectors dominate.

**R8 — Tags are complete.**
- Required: `project:X`, `feature:<feature-id>`, `persona:<persona>`, `priority:<level>`, `url:<base-url>`.
- FAIL if any required tag is missing.
- FAIL if the feature tag references a non-existent Feature artifact (it should match a real artifact id).

**R9 — Name follows the pattern.**
- Pattern: `<Feature> — <user-facing action>` or `User can <action>`.
- FAIL if name includes `test` in it (*"test login flow"*).
- FAIL if name is about implementation (*"clicks login-btn and checks div.dashboard"*).

**R10 — Linked to a Feature.scenario.**
- FAIL if the test is an orphan (no scenario references its id in `test_ids`).
- Note: this is coverage-side; the test itself doesn't know about its scenarios. Cross-check against Feature artifacts.

### 4. Grade each test

Score the PASSes out of applicable rules (exclude N/A).

- **A (9-10 of applicable rules PASS):** ship it.
- **B (7-8):** solid, minor rewrites suggested.
- **C (5-6):** needs real work.
- **D (3-4):** probably better to rewrite than patch.
- **F (<3):** delete or start over.

### 5. Produce the report via Tasks artifact

Per modes/agent.md lifecycle lifecycle — the Tasks artifact IS the deliverable. Structure:

- `links` → every Feature artifact whose tests you reviewed
- `relevant_files` → empty (no source files touched)
- Top-level `notes` → scope (N tests, filter applied) and the overall grade distribution (e.g. 2 A, 5 B, 1 C, 1 F).
- One subtask per reviewed test:
  - `title`: `"Validate: <test-id>"`
  - `status`: `done`
  - `priority`: map the grade to priority (F → critical to fix, C-D → high, B → medium, A → low)
  - `notes`: the test's grade, the failed rule IDs with one-line evidence each, and the specific rewrite recommendation.

### 6. Evidence

The report **is** the evidence — no run URLs, no screenshots. But every FAIL claim must cite the specific line or the specific absence ("no `Should Be Equal` anywhere in the content", "Documentation line 2 contains `.login-btn`").

## Example subtask note (good)

```
Grade: C (6/9 applicable)

FAILS:
- R1 (asserts outcome): no assertion anywhere after Click submit — we prove the click happened, not that login succeeded
- R3 (PM-readable docs): Given line says "user visits .login-page" — contains CSS selector; should say "user on the login screen"
- R4 (FakeMail): hardcodes admin@test.com — second run fails because account already exists from first run

REWRITE SUGGESTION:
After `Click  button[type='submit']`, add:
  Wait For Elements State  role=heading[name="Dashboard"]  visible
  ${url}=  Get Url
  Should Contain  ${url}  /dashboard

Rewrite docs first two lines:
  Given: registered user with valid account
  When: user submits the login form with valid credentials
```

## What NOT to do

- **Do not rewrite the tests.** That's `fix` or `tdd`. This mode critiques.
- **Do not run the tests.** A test can be quality-bad AND currently green — both are true independently. You're judging the test content, not the outcome.
- **Do not score overly harshly.** If a rule is N/A (no email, no auth), don't count it against the test.
- **Do not skip the rewrite recommendation.** A failing rule without a concrete fix is useless. Every FAIL gets a "change X to Y" suggestion.

## Handoff

End the report with: *"N tests reviewed. The D/F grades are the queue for rewrite — run `/helpmetest tdd` or `/helpmetest fix` on them. B and C are smaller fixes the author can apply directly."*
