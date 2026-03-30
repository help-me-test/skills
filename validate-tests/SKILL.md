---
name: validate-tests
description: "Invoke this skill when a user shares test code and questions whether it actually works as intended — not to run or fix the test, but to evaluate whether the test has real value. Triggers on: \"is this test any good?\", \"would this catch a real bug?\", \"this test always passes — is that normal?\", \"review these tests before I commit\", or \"does this test verify anything meaningful?\". Also triggers when someone suspects a test is useless, wants a pre-commit quality gate, or is unsure if an auto-generated test is worth keeping. The core question this skill answers: \"Would this test fail if the feature broke?\" If not, the test gets rejected. Do NOT use for generating new tests, fixing failing tests, or exploring application features."
allowed-tools: mcp__helpmetest-*
---

> **Who you are:** If `.helpmetest/SOUL.md` exists in this project, read it before starting — it defines your character and shapes how you work.

> **No MCP?** The CLI has full feature parity — use `helpmetest <command>` instead of MCP tools. See the [CLI reference](../README.md#no-mcp-use-the-cli).

# QA Validator

Validates and scores test quality. Rejects tests that don't meet quality standards.

## Prerequisites

```
how_to({ type: "context_discovery" })
how_to({ type: "test_quality_guardrails" })
```

`context_discovery` identifies the Feature artifact the test should link to. After validation passes, add the `test_id` to the scenario's `test_ids` array so future sessions know this scenario is covered.

## Tasks Artifact

**For batch validation (3+ tests):** Create a Tasks artifact to track which tests have been validated:

```json
{
  "id": "tasks-validate-[feature-name]",
  "type": "Tasks",
  "name": "Tasks: Validate Tests for [Feature Name]",
  "content": {
    "overview": "Validate all tests for [Feature Name]. Each subtask is one test — PASS or REJECT.",
    "source_artifact_ids": ["feature-[name]"],
    "tasks": [
      { "id": "1.0", "title": "Validate all tests", "status": "pending", "priority": "critical",
        "subtasks": [
          { "id": "1.1", "title": "[test-id]: [test name]", "status": "pending" },
          { "id": "1.2", "title": "[test-id]: [test name]", "status": "pending" }
        ]
      }
    ],
    "notes": []
  }
}
```

Mark each subtask `done` (PASS) or `blocked` with notes explaining rejection reason. For single-test validation, Tasks is optional.

## Input

- Test ID or test content to validate
- Feature artifact it should test

## Validation Workflow

### Step 1: The Business Value Question (MOST IMPORTANT)

Before checking anything else, answer these two questions:

1. **"What business capability does this test verify?"**
2. **"If this test passes but the feature is broken, is that possible?"**

**If answer to #2 is YES → IMMEDIATE REJECTION**

This is the ONLY question that truly matters. A test that passes when the feature is broken is worthless.

Examples of worthless tests:
- Test only counts form fields → REJECT (form could be broken, test still passes)
- Test clicks button, waits for same element → REJECT (button could do nothing, test still passes)
- Test navigates, verifies title → REJECT (navigation works, feature could be broken)

### Step 2: Check for Anti-Patterns (Auto-Reject)

Check for these bullshit patterns:

- ❌ Only navigation + element counting (no actual feature usage)
- ❌ Click + Wait for element that was already visible (no state change)
- ❌ Form field presence check without filling + submission
- ❌ Page load + title check (no business transaction)
- ❌ UI element verification without verifying element WORKS

**If ANY anti-pattern found → IMMEDIATE REJECTION**

### Step 3: Check Minimum Quality Requirements

- Step count >= 5 meaningful steps?
- Has >= 2 assertions (Get Text, Should Be, Wait For)?
- Verifies state change (before/after OR API response OR data persistence)?
- Tests scenario's Given/When/Then, not just "page loads"?
- Uses stable selectors?
- Has [Documentation]?
- Tags use category:value format (priority:high)?
- Has required tags: priority:?
- Tags include feature:?
- No invalid tags?

**If ANY requirement fails → REJECT with specific feedback**

### Step 4: Assign Bullshit Score

Rate the test on the **Bullshit Scale: 1–10** where 1 = solid test, 10 = pure bullshit.

| Score | Meaning |
|-------|---------|
| 1–3 | Solid — behavioral assertions, state changes verified, would catch real bugs |
| 4–6 | Mediocre — some value but weak assertions, misleading name, or vacuously true checks |
| 7–9 | Mostly bullshit — navigation only, `>= 0` assertions, no real behavior tested |
| 10 | Pure bullshit — single `Go To`, unnamed hash ID, `Sleep` with no assertion |

**Score ≤ 4 → PASS. Score ≥ 5 → REJECT** (unless the user asks only for a grade without enforcement).

### Step 5: Generate Validation Report

For a **single test**, output:

```
[score]/10 — ✅ PASS / ❌ REJECT
Test ID: [id]
Reason: [one sentence]
[Optional: what to fix]
```

For a **batch of tests**, output a table grouped by tier:

```
### Solid (1–3)
| Test | Score | Reason |
|------|-------|--------|
| test-name | 2 | End-to-end flow, before/after verified |

### Mediocre (4–6)
| Test | Score | Reason |
...

### Bullshit (7–10)
| Test | Score | Reason |
...
```

Then a summary line: `X solid / Y mediocre / Z bullshit out of N total`

Then immediately output a **numbered action menu** based on what was found. Only show options that apply:

```
What next? Reply with numbers (e.g. "1 3"):

1. Delete [N] score-10 tests: [id1], [id2]
2. Rename [N] misleading tests (name doesn't match what test does)
3. Fix [N] vacuous assertions (>= 0, always-true checks)
4. Rewrite [N] mediocre tests into solid ones
5. Investigate [N] failing tests
6. All of the above
```

**When user replies with numbers:**

- Parse the reply as a space/comma-separated list of option numbers
- Execute each selected action in order without asking for more input
- For **delete**: call `helpmetest_delete_test` for each score-10 test ID
- For **rename**: propose new name + ask to confirm before calling `helpmetest_upsert_test`
- For **fix assertions**: show current code → show fixed code → call `helpmetest_upsert_test`
- For **rewrite**: show rewritten test → call `helpmetest_upsert_test`
- For **investigate**: run each failing test with `helpmetest_run_test` and report what broke

## Output

- Bullshit score (1–10) for every test reviewed
- Validation status: PASS or REJECT
- Specific feedback (why rejected OR recommendations if passed)
- Updated Feature artifact if PASS (add test_id to scenario.test_ids)

## Rejection Examples

### REJECT: Element Counting

```robot
Go To  /profile
Get Element Count  input[placeholder='John']  ==  1
Get Element Count  button[type='submit']  ==  1
```
**Reason:** Only counts elements, doesn't test if form works. Test passes even if form submission broken.

### REJECT: Click Without Verification

```robot
Go To  /videos
Click  [data-testid='category-python']
Wait For Elements State  [data-testid='category-python']  visible
```
**Reason:** Waits for element that was already visible. Doesn't verify videos were filtered. Test passes even if filter broken.

### REJECT: Navigation Only

```robot
Go To  /checkout
Get Title  ==  Checkout
Get Element Count  input[name='address']  ==  1
```
**Reason:** Only navigation + element existence. Doesn't test checkout works. Test passes even if checkout endpoint broken.

### REJECT: Form Display Without Submission

```robot
Go To  /register
Get Element Count  input[type='email']  ==  1
Get Element Count  input[type='password']  ==  1
```
**Reason:** Only checks form exists, doesn't test registration. Test passes even if registration endpoint returns 500.

### PASS: Complete Workflow

```robot
Go To  /profile
Fill Text  input[name='firstName']  John
Click  button[type='submit']
Wait For Response  url=/api/profile  status=200
Reload
Get Attribute  input[name='firstName']  value  ==  John
```
**Reason:** Tests complete workflow - user can update AND data persists. Would fail if feature broken.

**Version:** 0.1
