# Mode: improve — audit and rewrite all tests to quality standard

**What this mode does:** list every test in scope, run `validate` on each one to score it against R1–R13, then immediately fix every failing rule in-place. Unlike `validate` which only critiques, `improve` does the work. It also applies two additional style passes (comment structure and inline comments) that validate does not cover.

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
Phase 2: Rewrite — fix every FAIL, one test at a time.
Phase 3: Style — apply comment structure (I2) and inline comment (I3) passes.
Phase 4: Verify — re-run each rewritten test to confirm it still passes.

Each failing rule gets a concrete fix applied immediately.

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

Starting rewrites now — [Y] tests to fix.
```

### 4. Fix each failing test

For each test with at least one FAIL, apply the fixes below. All fixes in one pass — don't make separate passes per rule.

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

Do not guess or invent selectors. Use `interactive` mode to navigate to the page and read the Interactive section — it lists every element with its best available selector. See `modes/interactive.md`.

Selector priority:
1. `[data-testid="..."]` — stable, survives styling and layout changes
2. `role=button[name="Place order"]` — semantic, survives DOM restructuring
3. `text=Place order` — last resort for elements with no testid or role

Do not change selectors that are already stable (`[data-testid=...]`, `role=`, `text=`).

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
${name}=  Get Text  [data-testid="profile-name"]
Should Be Equal  ${name}  New Name
```

**R12 — Rewrite to test through the UI**

If the test calls ORM/crypto/HTTP client directly, rewrite it as a browser test that exercises the same behavior through the product UI. This is a full structural rewrite — flag it explicitly before touching it.

**R13 — Remove excess mocks**

Keep only mocks for external I/O (APIs, filesystem, third-party services). Remove mocks for business logic, pure functions, and internal services. Rewrite the test to use real implementations where mocks were covering internal code.

### 5. Apply style passes (I2 and I3)

After R-rule fixes, apply two additional passes that validate does not cover:

**I2 — Section comments**

The test body must be divided into intent-based section comments. Rules:
- One comment covers exactly 2 keywords (for ~13-keyword tests) — this satisfies the validator's even-distribution check
- No numbering, no decorations, no "verify/check/assert" as first word
- Written in product context: names the phase from the user's perspective
- Comments must NOT describe what the keyword does — they name the intent

**Working example — 13 keywords → 7 sections of 2 each:**
```robot
# Open todo app
  Go To  https://todo.playground.helpmetest.com

# Clear previous state and reload
  Javascript  window.localStorage.clear()
  Reload

# Verify list is empty
  ${items_before}=  Get Text  css=.todo-count
  Should Contain  ${items_before}  0

# Add todo with valid text
  Fill Text  input.new-todo  Buy milk
  Press Keys  input.new-todo  Enter

# Todo appears in list
  ${todo_text}=  Get Text  css=.todo-list li label
  Should Contain  ${todo_text}  Buy milk

# Counter shows correct item count
  ${counter}=  Get Text  css=.todo-count
  Should Contain  ${counter}  1 item left

# Input clears and is ready for next todo
  ${cleared}=  Javascript  document.querySelector("input.new-todo").value === ""
  Should Be True  ${cleared}
```

**Section size formula:** count keywords → target `ceil(total / 2)` sections so each has ~2 keywords. For 13 keywords → 7 sections. If validator rejects due to "Uneven comment distribution", adjust by 1 section at a time. See `modes/comment.md` for full spec.

**I3 — Inline comments**

Add a one-line why-comment only for:
- A `Javascript` call whose purpose is not obvious from its shape
- `Wait Until Keyword Succeeds` explaining the specific race condition

One line max, written for a product manager. Explains WHY, not WHAT.

### 6. Apply the fix

```bash
helpmetest test update <id> --file /tmp/<id>-improved.robot --no-run
```

### 7. Verify it still passes

```bash
helpmetest test run <id>
```

Wait for result. If it fails:
- Check if the content change broke a selector or timing assumption
- Fix and re-run — do not move on until the test is green

### 8. Tasks artifact

Track progress per `modes/agent.md`. One subtask per test that needed fixes:
- `title`: `"Improve: <test-id>"`
- `status`: `done` when test is green after rewrite
- `notes`: which R-rules were fixed + run URL as evidence

### 9. Final report

```
## Improve complete

[N] tests reviewed. [X] already grade A/B. [Y] rewritten.

Rules fixed:
  R1  [n] tests   R4  [n] tests
  R5  [n] tests   R6  [n] tests   R7  [n] tests
  R8  [n] tests   R9  [n] tests   R11 [n] tests
  R12 [n] tests   R13 [n] tests
  I2  [n] tests   I3  [n] tests

All [Y] rewritten tests are green. ✅
```

---

## What NOT to do

- **Do not rewrite test logic** — only improve clarity, structure, and documentation (except R11/R12/R13 which require logic changes)
- **Do not add steps** beyond what fixes the failing rule
- **Do not skip the re-run** — "should work" is not evidence
- **Do not batch rewrites** without verifying each one passes
- **Do not invent selectors** — always discover via `helpmetest interactive`
