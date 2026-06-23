> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

> ### 🔴 AFTER EVERY TEST CREATE/UPDATE — TWO MORE STEPS ARE MANDATORY.
> 1. Run the test — call `helpmetest test run <test-id>` after creating or updating.
>    Run it even if you think the app server is down or not yet built. A FAIL result is valid — it documents current state. Never skip because you "expect it to fail."
> 2. Update the Feature artifact to include this test ID in the matching scenario's `test_ids` array.
> Create-only is **incomplete**. Both steps are required. No exceptions.

---

---

## The Iron Law

> **NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**

If you write code before the test → delete it, start over. Don't keep it as "reference", don't "adapt" it while writing tests, don't look at it. Implement fresh from tests. Period.

**Exceptions:** Throwaway prototypes, generated code, configuration files. Ask your human partner.

---

## Red-Green-Refactor Verification Steps

Every TDD cycle follows these three phases. Each has a mandatory gate.

### RED — Write Failing Test

1. Write the test
2. Run it — it **MUST** fail for the expected reason
3. If it passes → you're testing existing behavior, fix the test so it fails on the intended behavior
4. If it errors → fix the error, re-run until it fails correctly

**Gate:** Test fails with the right error message before proceeding.

### GREEN — Minimal Code

1. Write the simplest code to pass the test
2. Run the test — it **MUST** pass
3. If it fails → fix the code, not the test
4. Don't add features, don't refactor beyond what the test requires

**Gate:** Test passes. No other tests break.

### REFACTOR — Clean Up

1. After green, remove duplication, improve names, extract helpers
2. Keep tests green — don't add behavior in refactor
3. Re-run tests after refactor

**Gate:** All tests pass, code is cleaner than before.

---

## Common Rationalizations — Stop These

| Excuse | Reality |
|--------|---------|
| "I'll test after" | Tests passing immediately prove nothing |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt |
| "This is different because..." | It's not. Delete and start over. |
| "The test is too hard to write" | The test is telling you the design is wrong |
| "I know this works" | You don't. Prove it. |

---

## Narrate Your Actions

**Never create a test, artifact, or run a test silently.** Always tell the user:
- **Before:** what you are about to do and why (what scenario it covers, what risk it guards against)
- **After:** what happened — result, what the artifact contains, why a test failed
- **Next:** what you will do next and what decision point is coming

Silence means the user has no idea what you did or why.

# Tests — Write, Generate, Fix

## Orient First (Always)

Before doing anything, check what already exists:

```bash
helpmetest status
helpmetest artifact list
helpmetest artifact list --type Tasks
```

---

## Announce (always — before any test is written or fixed)

After orient, present the TDD landscape in user-value terms. Never start work silently.

**If invoked with a specific task** (feature name, test id, file to change): skip to the relevant use case below, but still open with one sentence stating what the user will have after this work.

**If invoked bare (no task given)**, present based on what orient found:

**Failing tests exist:**
> "After diagnosis you'll know whether `[test-id]` is a broken selector, a timing issue, or an actual bug in the feature — so you can either fix the test or file the bug with confidence. I'd start there; it's already written, just needs fixing. That, or is there a specific feature you want to build test-first?"

**No failing tests, uncovered scenarios exist:**
> "Suite is green but [N] scenarios have no tests — if any of those flows broke today, nothing would catch it. I'd start with `[highest-priority scenario]` in `[feature-id]`. Want to cover that, or do you have a specific feature in mind?"

**Both failing tests and uncovered scenarios:**
> "There's [N] failing test[s] and [M] uncovered scenarios. I'd fix the failing test first — it's already written — then cover the critical gaps. That order, or is there something specific you want to build?"

**All green and covered:**
> "Suite is green and covered. Tell me the feature you want to build test-first and I'll enumerate scenarios before writing a single line of code."

**Rules:**
- Always recommend an order with a reason. Never present a menu of options with no recommendation.
- The binary choice is "my recommended path vs. redirect to something specific" — not a list of 3+ options.
- One question, not two.

---

## Use Cases

### "Change this" / "Fix this bug" / "Refactor this" — Existing Code

**This is the highest-risk scenario for silent test breakage. Code changes must never lead — tests must.**

Before touching any file, do this in full:

**Step 1: Find the blast radius**
```bash
grep -rn "@helpmetest" <files-to-change>
helpmetest status
git diff --stat HEAD
```
If no annotations exist: still check `helpmetest status`. Tests may exist without annotations — treat them as if they were annotated. If no tests exist at all, tell the user before coding: "No tests cover this code. Should I write them first?"

**Step 2: Classify each affected test**

For every test in the annotations:
- **Still valid** — you're not changing the behavior this test covers → leave it alone
- **Needs update** — you're intentionally changing what this test asserts → show the diff
- **Delete** — the feature/behavior being removed → flag for explicit user decision
- **New test needed** — your change adds new behavior with no coverage → propose it

**Step 3: Present the test impact plan — STOP and wait for explicit approval**

Write this out to the user before any code edit:

```
I'm about to change [what]. Here's the test impact:

`test-name` → NEEDS UPDATE
  currently asserts: [what the test checks now]
  will change to:    [what it should check after]

`test-name-2` → STILL VALID (no change needed)

`test-name-3` → NEW TEST NEEDED
  will cover: [new behavior being added]

Approve this plan before I write any code?

**Mutation Resistance check (R11):** For each NEEDS UPDATE test, also verify: if the behavior changes, does this test still verify the correct outcome? If the test would still pass after the code change, it needs updating too.
```

**Step 4: After approval — update the tests first**

Tests will fail immediately. That is correct — failing tests are now the spec for your implementation.

**Step 5: Change the code**

The failing tests tell you exactly what to implement. No more, no less.

**Step 6: Run all listed tests — prove they're green**

Done means green tests, not "this should work." Run them. Show the output.

---

### "I want to build an app" / "I want to develop X" / "Refactor X" — use `dev` mode

For any full code work (greenfield, new feature, change, refactor), use `dev` mode — it orchestrates the correct sequence including onboard, tdd, interactive, discover, validate, and coverage. See `modes/dev.md`.

`tdd` is a sub-step of `dev`, not the entry point for code work.

### "I need to build something" (TDD)

New feature, bug fix, or refactor. Tests come first — they define what "done" means.

**1. Create a Tasks artifact** to track the work:
```json
{
  "id": "tasks-[feature-name]",
  "type": "Tasks",
  "content": {
    "overview": "What this implements and why",
    "tasks": [
      { "id": "1.0", "title": "Write all tests first", "status": "pending", "priority": "critical" },
      { "id": "2.0", "title": "Implement to make tests pass", "status": "pending" },
      { "id": "3.0", "title": "All green — review for gaps", "status": "pending" }
    ]
  }
}
```

**2. Create a Feature artifact** with all scenarios before writing a single test:
```json
{
  "id": "feature-[name]",
  "type": "Feature",
  "content": {
    "goal": "What this feature does",
    "functional": [
      { "name": "User can do X", "given": "...", "when": "...", "then": "...", "tags": ["priority:critical"], "test_ids": [] }
    ],
    "edge_cases": [],
    "bugs": []
  }
}
```

**3. Plan coverage before writing a single test.** For every feature, enumerate scenarios across four types:

| Type | Always? | Question to ask |
|------|---------|-----------------|
| Critical path | ✅ always | What does a real user do when everything works? |
| Error paths | ✅ always | What are the 3 most likely ways this breaks in prod? |
| Boundary conditions | if data/logic | Where does behavior change based on a threshold? |
| Edge cases | selectively | What would a QA engineer test that a dev wouldn't? |

Mark each scenario: **write immediately** (critical/high) / **write before launch** (medium) / **skip** (cosmetic, already covered, unreliable). Don't test everything — test what would hurt if it broke.

**4. Write ALL tests** — happy paths, edge cases, errors — before implementing anything. Failing tests are your spec. After each test, run the red-team loop (`shared.md §3a`) before writing the next one.

**5. Implement incrementally** — pick the highest-priority failing test, make it pass, move to the next.

**6. Done when** all tests are green and you've reviewed for missing edge cases.

---

### "Write tests for an existing feature"

Feature exists (or was just built by someone else). Your job is tests only.

**1. Read the Feature artifact** — `helpmetest artifact get feature-X`. If none exists, create one first based on what you know.

**2. Explore interactively before writing** — use `interactive` mode to run the scenario step by step against the live app. A test written from real observation uses real selectors and reflects actual timing. A test written from a description is a guess. See `modes/interactive.md`.

**3. Before writing each test, answer this out loud:**
> "If this test passes but the feature is actually broken, what user complaint would we miss until a customer reports it?"



**4. Write tests** for `priority:critical` scenarios first, then high, then medium. For each:
- 5+ meaningful steps
- Verify business outcomes (data saved, state changed) — not just that an element is visible
- Use `Create Fake Email` for any registration/email fields — never hardcode
- Test name must answer: `<Feature> — <user-facing action>` or `User can <action>`. No implementation details, no "test" in name.
- Tags must include: `priority:<level>`, `feature:<name>`. Use `--tags` flag, not `[Tags]` in content.

**5. Red-team loop** — see `shared.md §3a`. Run it after every test create/update. Only move to the next test when all four questions come up clean.

**6. Validate** the finished test with `/helpmetest validate` as a formal gate. A test that passes when the feature is broken must be rewritten — it is not done until the validator says PASS.

**7. Link tests back** — add each test ID to `scenario.test_ids` in the Feature artifact **only after** it passes the red-team loop and validation.

**8. Run and fix** — see "Fix broken tests" below if a newly-written test fails.

---

### "Fix broken tests" / "Tests are failing"

**First: understand the failure pattern**

Check recent code changes:
```bash
git diff --stat HEAD
git log --oneline -5
```
Map changed files to likely causes:
- `components/`, `pages/` → selector changes
- `auth/`, `session/` → auth state issues
- `api/`, `routes/` → backend errors or changed response shapes

Then get test history: `helpmetest status --id <test-id> --history 10`

**Classify:**
- Consistent failure after a code change → selector/behavior changed
- Intermittent PASS/FAIL with changing errors → isolation issue (shared state, test order dependency)
- Timeout / element not visible → timing issue
- Auth/session error → state not restored correctly
- Backend error in test output → real bug, not a test issue

**Reproduce interactively — always do this before fixing**

Run the failing steps one at a time:
```
As  <persona>
Go To  <url>
# Execute each step, observe what actually happens at the point of failure
```

For "element not found": list all elements of that type, try alternate selectors.
For "wrong value": check what's actually displayed vs what the test expected.
For timeouts: try longer waits, check whether the element ever appears.

**Decide: test issue or app bug?**

- **Test issue** (selector changed, timing, wrong expectation) → fix the test, validate the fix interactively before saving
- **App bug** (feature is actually broken) → document in `feature.bugs[]`, update Feature.status to "broken" or "partial"

**Many tests broke after a UI change?**

Work through them systematically one by one. For each:
1. Classify the failure (usually selector or timing)
2. Reproduce interactively
3. Fix
4. Run to confirm

Don't shotgun-fix by guessing — one wrong fix creates two broken tests.

**Tests are out of date after a refactor?**

1. Get test list: `helpmetest status`
2. For each failing test, check whether the Feature artifact scenario still matches intended behavior
3. If the code is the source of truth → update the test
4. If the test was right and the refactor broke behavior → document the regression

---

## Writing Tests

### Structure

```
As  <persona>          # auth state — always first
Go To  <url>

# Given — establish precondition
<steps>

# When — perform the action
<steps>

# Then — verify the outcome
<assertions>

# Persistence check (if relevant)
Reload
<re-assert that state survived>
```

### Inline comments

**Every non-obvious step must have a `# comment` above it written for a product manager, not an engineer.**

Comments explain *why* a step exists, what the user is experiencing, or what the test is checking — not what the keyword does.

```robot
# User opens an existing test replay — this is the entry point for debugging failed tests
Go To  https://helpmetest.example.com/test/some-test

# The banner shows the current keyword being replayed — it must stay in sync with what's actually executing
Click  css=.banner-next

# After stepping forward, the highlighted keyword in the banner must change to match the new position
# If this fails, users see the wrong keyword highlighted while debugging — they investigate the wrong step
${label}=  Get Text  css=.keyword-line.current .keyword-text
Should Contain  ${label}  ${expected_keyword}
```

Comments are **mandatory** for:
- Any `Javascript` call — explain what user-visible state it reads or changes
- Any `Hover` or `Sleep` — explain why the UI requires this (hover to reveal hidden elements, sleep for animation)
- Any multi-step assertion group — explain what the group collectively verifies
- Any setup step that isn't obvious navigation

### What makes a good test

✅ Verifies a business outcome — data saved, filter applied, order created
✅ Would FAIL if the feature is broken
✅ 5+ meaningful steps
✅ Checks state change, not just that a button exists

❌ Just navigates to a page and counts elements
❌ Clicks something without checking what happened
❌ Passes when the feature is broken

### Test naming

Format: `User can <action>` or `<Feature> <behavior>`
- ✅ `User can update profile email`
- ✅ `Cart total updates when quantity changes`
- ❌ `MyApp Login Test`
- ❌ `SiteName Checkout`

### Auth

Use `Save As <StateName>` once to capture auth state. Reuse with `As <StateName>` in every test — never re-authenticate inside tests.

### Emails

Use `Create Fake Email` — never hardcode `test@example.com`. Hardcoded emails break on second run.
```
${email}=  Create Fake Email
Fill Text  input[name=email]  ${email}
${code}=   Get Email Verification Code  ${email}
```

### Localhost

If testing a local server, set up a proxy tunnel first — see the `proxy` skill. Use the domain the proxy gives you in all test URLs, not `localhost`.

---

## Tags

- `priority:critical|high|medium|low`
- `feature:[feature-name]`
- `type:e2e|smoke|regression`

---

## Done means

- ✅ All tests passing
- ✅ All `priority:critical` scenarios have `test_ids`
- ✅ Every test passed `/fix` before being linked
- ✅ Bugs documented in `feature.bugs[]`
- ✅ Feature.status updated (`working` / `broken` / `partial`)
- ✅ Tasks artifact all done

## Final summary format

Never end with "N tests created, M passing." End with this:

```
## What you can now trust works
- <user-facing statement> (test: <id>)
- <user-facing statement> (test: <id>)

## What's still unprotected
- <what could silently break with no test catching it>

## Bugs found
- <bug description> — documented in feature.bugs[]
```

If you can't write the first section in user-facing language, your tests are not done.
