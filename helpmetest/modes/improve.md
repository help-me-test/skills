<!-- llms-description: Audit tests against quality rules and report defects without changing existing tests. -->

# Mode: improve — audit test quality, preserve test evidence

**What this mode does:** list every test in scope and run `validate` on each one to score
it against R1–R13. It reports every defect with literal evidence and the code/product change
needed to make the existing test trustworthy. It **never rewrites an existing test**.

**When to use:** user says "improve tests", "clean up all tests", "add comments to tests", "make tests better", "annotate tests", "bring tests up to standard".

---

## Inputs

- No filter: improve every test in the project (all at once — no cap)
- Tag filter: `improve project:bug-shop` — only tests matching that tag
- Specific test: `improve bug-10-surcharge`

---

## Announce

After orient, present the plan before touching anything:

```
## Improve plan

Scope: [N] tests — [filter or "all"]

Phase 1: Audit — validate each test (R1–R13) to get grade + failed rules.
Phase 2: Reproduce — run each flagged test unchanged and capture its literal output.
Phase 3: Report — state the product/code/environment change needed for the existing test
to pass or become meaningful.
Phase 4: Verify — re-run only after that non-test change.

No test will be rewritten, weakened, skipped, or deleted.

```

Announce the plan, then immediately proceed — do not wait for confirmation.

---

## Workflow

### 1. Orient

```bash
helpmetest status
```

Collect the full test list. Note total count and any already-failing tests (run status).

### 2. Audit each test using validate

For each test, apply the full `validate` scoring (R1–R13) as defined in `modes/validate.md`.

```bash
helpmetest search "<test-id>"           # find the test — shows tags + name
helpmetest test run <test-id> --json    # get full content via `keywords` field
```

Score every applicable rule. Record:
- Which rules FAIL
- The specific line or absence that caused each FAIL
- The grade (A–F)

Do not rewrite yet — audit the full scope first.

### 3. Announce audit results

Before rewriting:

```
Audit complete. [N] tests reviewed.
  [X] already grade A/B (no changes needed)
  [Y] need fixes:
    - [n] R1  no outcome assertion
    - [n] R4  hardcoded email
    - [n] R5  re-login instead of As <State>
    - [n] R6  unjustified sleep / blocked pattern
    - [n] R7  fragile CSS selectors
    - [n] R8  incomplete tags
    - [n] R9  vague or "test" name
    - [n] R11 mutation-blind assertion
    - [n] R12 tests framework behavior → auto-F
    - [n] R13 excessive mocking

Tests that need attention: [Y]. Their source stays unchanged. Starting reproduction and
evidence capture now.
```

### 4. Record each failing test

For every failed R-rule or red run, record: test id; literal command and output; the exact
expectation; observed product behaviour; and the code, configuration, fixture, or
environment change required for that unchanged test to pass. **Do not apply any of the
rewrite patterns below; they are historical examples superseded by `shared.md` §1a.**

**R1 — Add an outcome assertion**

Replace `Should Be Visible` / `Wait For Element` -only assertions with at least one data check:
- `Should Be Equal`, `Should Contain`, `Should Match Regexp`
- Read a value with `Get Text` or `Get Attribute` and assert the value, not just presence.

**R4 — Replace hardcoded email**

```robot
${email}=  Create Fake Email
Fill Text  [data-testid="email"]  ${email}
```

Add `Delete Email  ${email}` in teardown or after the assertion block.

**R5 — Replace re-login with As state**

Remove the login form fill + click sequence. Replace with:
```robot
As  <StateName>
```
as the first meaningful line (before `Go To`).

**R6 — Fix blocked patterns and unjustified sleep**

- Remove `Evaluate  ...__import__(...)` and `Evaluate  lambda ...`
- For `Sleep  Xs` without a comment: replace with `Wait For Elements State` on the condition being waited for, or add a one-line why-comment if the sleep is genuinely necessary (animation, specific timing constraint).

**R7 — Replace fragile selectors**

**FAST PATH: if the test currently passes (100/100 or close), existing selectors are working — do NOT run interactive to re-discover them. Only use `interactive` when a selector is actively failing or is visibly fragile (bare `.class`, positional `nth-child`, deeply nested path).**

For genuinely fragile selectors only: use `interactive` mode to navigate to the page and read the Interactive section — it lists every element with its best available selector. See `modes/interactive.md`.

Selector priority:
1. `[data-testid="..."]` — stable, survives styling and layout changes
2. `role=button[name="Place order"]` — semantic, survives DOM restructuring
3. `text=Place order` — last resort for elements with no testid or role

Do not change selectors that are already stable (`[data-testid=...]`, `role=`, `text=`, `css=.well-named-class`). The goal is to improve failing tests, not audit already-working ones.

**R8 / R10 — Complete tags**

Add any missing required tags: `project:X`, `feature:<id>`, `persona:<name>`, `priority:<level>`, `url:<base>`.

**R9 — Fix vague or "test" name**

Rename to follow `<Feature> — <user-facing action>` or `User can <action>`:
- Remove the word "test" from the name
- Make the name answer: "What specific user-facing behavior does this verify?"

**R11 — Strengthen mutation-resistant assertion**

After `Click submit` or equivalent, verify the actual data change:
```robot
# instead of just: Wait For Elements State  [data-testid="banner"]  visible
${name}=  Browser.Get Text  [data-testid="profile-name"]
Should Be Equal  ${name}  New Name
```

**R12 — Rewrite to test through the UI**

If the test calls ORM/crypto/HTTP client directly, rewrite it as a browser test that exercises the same behavior through the product UI. This is a full structural rewrite — flag it explicitly before touching it.

**R13 — Remove excess mocks**

Keep only mocks for external I/O (APIs, filesystem, third-party services). Remove mocks for business logic, pure functions, and internal services. Rewrite the test to use real implementations where mocks were covering internal code.

### 5. Tasks artifact

Track progress per `modes/agent.md`. One subtask per test reviewed:
- `title`: `"Audit: <test-id>"`
- `status`: `done` only after its unchanged run output and required product change are
  recorded; otherwise `blocked`
- `notes`: literal run output, failed R-rules, and the code/environment work needed

### 6. Final report

Start with the required `TEST FILES CHANGED: none.` line. For every test, paste:

```text
<literal helpmetest test run command>
<literal result output>
```

Then state whether the test is satisfied by the current product. If not, leave it red and
state exactly what code/environment change would satisfy its existing contract. Never write
“all green” unless the pasted literal output proves each named test passed.

## What NOT to do

- **Do not rewrite test logic, comments, selectors, setup, tags, names, or assertions.**
- **Do not add steps to, skip, disable, weaken, or delete a test.**
- **Do not batch test rewrites; no test rewrite is permitted.**
