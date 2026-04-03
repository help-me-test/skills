---
name: tdd
description: "Everything to do with tests on HelpMeTest. Use when: writing tests for a new feature, generating tests for an existing feature, fixing a broken test, debugging a failing test, tests broke after a UI change, tests are out of date after a refactor. Triggers on: 'write tests', 'generate tests', 'test is failing', 'fix tests', 'tests broke', 'implement X', 'add feature', 'fix bug', 'why does this test fail', 'tests are out of date'. If it involves HelpMeTest tests in any way, this is the skill."
allowed-tools: mcp__helpmetest-*
---

> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

> **No MCP?** Use `helpmetest <command>` instead of MCP tools.

# Tests — Write, Generate, Fix

## Orient First (Always)

Before doing anything, check what already exists:

```
helpmetest_status()
helpmetest_search_artifacts({ query: "" })
helpmetest_search_artifacts({ type: "Tasks" })
```

- Tests already failing? → that's the priority, not creating new ones
- Tasks artifact in progress? → resume it, don't start over
- Feature artifacts exist? → use them, don't re-discover

---

## Use Cases

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

**3. Write ALL tests** — happy paths, edge cases, errors — before implementing anything. Failing tests are your spec.

**4. Implement incrementally** — pick the highest-priority failing test, make it pass, move to the next.

**5. Done when** all tests are green and you've reviewed for missing edge cases.

---

### "Write tests for an existing feature"

Feature exists (or was just built by someone else). Your job is tests only.

**1. Read the Feature artifact** — `helpmetest_get_artifact({ id: "feature-X" })`. If none exists, create one first based on what you know.

**2. Explore interactively before writing** — run the scenario step by step using `helpmetest_run_interactive_command`. A test written after seeing real behavior uses real selectors and reflects actual timing. A test written from a description is a guess.

```
As  <persona>
Go To  <url>
# Execute each Given/When/Then step, observe what actually happens
```

**3. Before writing each test, answer this out loud:**
> "If this test passes but the feature is actually broken, what user complaint would we miss until a customer reports it?"

Write that answer as the `PROTECTS:` line in `[Documentation]`. This is the contract the test makes with the user — not optional boilerplate. If you can't answer it in one sentence, the scenario needs more thought, not a test.

**4. Write tests** for `priority:critical` scenarios first, then high, then medium. For each:
- 5+ meaningful steps
- Verify business outcomes (data saved, state changed) — not just that an element is visible
- Use `Create Fake Email` for any registration/email fields — never hardcode
- `[Documentation]` must start with `PROTECTS: <what user complaint this catches>`

**5. Validate** each test with `validate-tests` **before** linking it to the scenario. A test that passes when the feature is broken must be rewritten — it is not done until the validator says PASS.

**6. Link tests back** — add each test ID to `scenario.test_ids` in the Feature artifact **only after** it passes validation.

**7. Run and fix** — see "Fix broken tests" below if a newly-written test fails.

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

Then get test history: `helpmetest_status({ id: "test-id", testRunLimit: 10 })`

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

1. Get test list: `helpmetest_status()`
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

### Documentation format

Every test must have `[Documentation]` with two parts:

```robot
[Documentation]    PROTECTS: <one sentence — what user complaint this catches if the feature breaks>
...                Given: <given> | When: <when> | Then: <then>
```

**PROTECTS: good examples:**
- ✅ `PROTECTS: Users who complete checkout don't get charged without receiving an order confirmation`
- ✅ `PROTECTS: Users typing wrong passwords aren't silently logged in or shown a blank error`
- ✅ `PROTECTS: Profile email changes don't silently fail — user would see stale email still showing`
- ❌ `PROTECTS: The login form works` — too vague, what breaks? who notices?
- ❌ `PROTECTS: Tests that the form submits` — that's what the test does, not what it protects

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

If testing a local server, set up the proxy first:
```
helpmetest_proxy({ action: "start", domain: "dev.local", sourcePort: 3000 })
```
Verify it works before writing any tests. See the `proxy` skill for details.

---

## Tags

- `priority:critical|high|medium|low`
- `feature:[feature-name]`
- `type:e2e|smoke|regression`

---

## Done means

- ✅ All tests passing
- ✅ All `priority:critical` scenarios have `test_ids`
- ✅ Every test has a `PROTECTS:` line in `[Documentation]`
- ✅ Every test passed `/validate-tests` before being linked
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
