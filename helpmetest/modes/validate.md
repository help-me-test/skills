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

Scoring against R1–R13. D/F grades get a concrete rewrite suggestion.
Output: Tasks artifact with one subtask per test, grade + failed rules + fix.

Starting with priority:critical tests first, then the rest.
```

Announce the plan, then immediately proceed — do not wait for a reply.

**Specific test or filter given:**

```
## Validate plan

Scope: [test-id | filter] — [N] tests

Scoring against R1–R13. Each FAIL gets a specific rewrite suggestion.
Output: Tasks artifact with grade + evidence per test.
```

Announce the plan, then immediately proceed — do not wait for a reply.

## Workflow

### 1. Orient

```bash
helpmetest status
```

Know the scope. Narrate how many tests you'll review before starting.

### 2. For each test in scope — fetch its content

```bash
helpmetest search "<test-id>"            # find the test and see its tags + name
helpmetest test run <test-id> --json     # get full content — `keywords` field is the RF body
```

Read:
- `keywords` — the RF body (from `--json` output)
- `tags` — project, feature, persona, priority, url (from search result)
- `name` — test name

**Do not use `helpmetest test run` to check pass/fail** — that runs the test. Use it only to extract content via `--json` for static analysis.

### 3. Score against the /tdd rulebook

For each test, check the rules below. Each rule is either PASS, FAIL, or N/A. Document the evidence (the specific line or the absence of a specific thing).

**R1 — Asserts an outcome, not presence.**
- FAIL if the test only clicks/navigates without a final assertion on data, state, or visible outcome.
- FAIL if the only assertion is `Should Be Visible` or `Wait For Element` on a selector — those prove presence, not function.
- PASS when there's at least one `Should Be Equal`, `Should Contain`, `Should Match`, data check, or state query.

**R2 — 5+ meaningful steps.**
- Count non-trivial keyword lines. `Go To`, `Fill Text`, `Click`, `Get Title`, assertions all count. `Sleep`, `Log`, comments don't.
- FAIL if <5 meaningful steps — the test is too shallow.

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

**R9 — Name follows the pattern — no vague/abd names.**
- Pattern: `<Feature> — <user-facing action>` or `User can <action>`.
- FAIL if name includes `test` in it (*"test login flow"*).
- FAIL if name is about implementation (*"clicks login-btn and checks div.dashboard"*).
- FAIL if name is vague/abd — does not say what the test actually verifies. A name like "login flow" or "checkout" or "user settings" tells nothing. The name must answer: "What specific user-facing behavior does this test verify?"
- Naming is the first line of defense against bad tests. A vague name means vague thinking = vague test.

**R10 — Has required tags.**
- FAIL if `priority:` or `feature:` tags missing.
- Tags come from metadata (parsed from `--tags` flag), not content.

---

## R11 — Mutation Resistance

**FAIL if the test could pass even when the code under test is broken.**

Ask: "If a developer introduced a realistic bug — removed the save handler, broke the validation, inverted the if condition — would this test fail?"

**Check:** Identify the specific behavior this test protects. Imagine removing or corrupting it. Would the test assertions still pass?

**Patterns that fail R11:**
- Test asserts element is visible but not that it works
- Test clicks submit but checks no data change
- Test reads from an input but doesn't verify the input was accepted
- Test checks "no error" instead of checking the positive outcome
- Test validates framework/library behavior, not our business logic

**Evidence:** "What specific bug would this miss if the code changed?"

---

## R12 — Tests Our Business Logic, Not Framework Behavior

**FAIL if the test validates:**
- Framework behavior (Express, Fastify, Koa route handlers)
- ORM/DB library behavior (Prisma findMany, Mongoose save)
- Crypto library behavior (bcrypt hash, JWT sign)
- HTTP client behavior (axios GET, fetch POST)
- React hook behavior (useState, useEffect — unless testing custom hook)

**Detection patterns (look for these in test keywords):**
- `(prisma|mongoose|sequelize).(find|create|update|delete)`
- `(bcrypt|argon2).(hash|compare)`
- `(jwt|jsonwebtoken).(sign|verify)`
- `(axios|fetch|got).(get|post|put|delete)`

**PASS if:** Test validates custom business logic that wraps or uses these libraries.

**Evidence:** "What line shows this tests OUR code vs the library?"

---

## R13 — Minimal Mocking

**FAIL if:**
- >3-4 mocks per test
- Mocking pure functions or business logic
- Complex mock setup that tests how mocks behave, not how code works

**PASS if:** Mocks only external I/O (APIs, databases, filesystem). Business logic uses real implementations.

**Evidence:** "What is mocked? Is it external I/O or internal logic?"

---

### 4. Grade each test

Score PASSes out of applicable rules (exclude N/A).

**R1-R10 (9 rules):**
- **A (8-9 PASS):** ship it
- **B (6-7):** solid, minor rewrites suggested
- **C (4-5):** needs real work
- **D (2-3):** probably better to rewrite than patch
- **F (<2):** delete or start over

**R11-R13 (3 rules — always applicable for functional tests):**
- Each FAIL on R11-R13 lowers the final grade by one tier (A→B, B→C, etc.)
- **Exception:** tests validating framework behavior (R12 FAIL) that aren't testing our code at all → automatic F regardless of R1-R10 score

**Evidence must cite:** the specific line or specific absence that triggered each FAIL.

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
Grade: C (6/8 applicable)

FAILS:
- R1 (asserts outcome): no assertion anywhere after Click submit — we prove the click happened, not that login succeeded
- R4 (FakeMail): hardcodes admin@test.com — second run fails because account already exists from first run

REWRITE SUGGESTION:
After `Click  button[type='submit']`, add:
  Wait For Elements State  role=heading[name="Dashboard"]  visible
  ${url}=  Get Url
  Should Contain  ${url}  /dashboard
```

## What NOT to do

- **Do not rewrite the tests.** That's `fix` or `tdd`. This mode critiques.
- **Do not run the tests to check pass/fail.** A test can be quality-bad AND currently green — both are true independently. You're judging the test content, not the outcome. Exception: `helpmetest test run <id> --json` is permitted *only* to extract the `keywords` field for static analysis — it will run the test as a side effect, but that's acceptable.
- **Do not score overly harshly.** If a rule is N/A (no email, no auth), don't count it against the test.
- **Do not skip the rewrite recommendation.** A failing rule without a concrete fix is useless. Every FAIL gets a "change X to Y" suggestion.

## Handoff

End the report with: *"N tests reviewed. The D/F grades are the queue for rewrite — run `/helpmetest tdd` or `/helpmetest fix` on them. B and C are smaller fixes the author can apply directly."*
