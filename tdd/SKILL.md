---
name: tdd
description: "Test-Driven Development enforcer using HelpMeTest. Use when user wants to implement new feature, refactor code, or fix bugs. Forces test-first workflow: write ALL comprehensive end-to-end tests before ANY implementation, use tests as guardrails during development, ensure all tests pass before claiming done. Use when user says 'implement X', 'add feature Y', 'refactor Z', 'fix bug', or starts coding without tests."
allowed-tools: mcp__helpmetest-*
---

> **Who you are:** If `.helpmetest/SOUL.md` exists in this project, read it before starting — it defines your character and shapes how you work.

> **No MCP?** The CLI has full feature parity — use `helpmetest <command>` instead of MCP tools. See the [CLI reference](../README.md#no-mcp-use-the-cli).

# Test-Driven Development

Enforces test-driven development using HelpMeTest end-to-end tests as guardrails.

## Core Philosophy

Tests come first. ALL tests come first. Not one test - ALL tests covering happy paths, edge cases, and errors. Tests define what "done" means. Code exists to make tests pass. No feature is complete until all tests are green.

## When to Use This Skill

Use for ANY code change that affects user-facing behavior:
- **New features**: Write ALL tests defining expected behavior, then implement
- **Refactoring**: Write tests capturing current behavior first, refactor, verify no regression
- **Bug fixes**: Write test reproducing the bug, fix it, verify test passes
- **Enhancements**: Write ALL tests for new behavior, implement, verify

## Workflow

### Step 0: Create Tasks Artifact (MANDATORY)

Before any implementation work begins, create a Tasks artifact to plan and track the work. This is non-negotiable — it gives you a structured plan and lets you resume if the session is interrupted.

1. **Search for an existing Tasks artifact** — don't create duplicates:
   ```
   helpmetest_search_artifacts({ type: "Tasks" })
   ```
   If one exists for this feature, read it and resume from the first non-done task.

2. **If none exists, create one** before writing a single line of code or a single test:
   ```json
   {
     "id": "tasks-[feature-name]",
     "type": "Tasks",
     "name": "Tasks: [Feature Name]",
     "content": {
       "overview": "What this work implements and why it exists",
       "source_artifact_ids": ["feature-[name]"],
       "relevant_files": [
         { "path": "path/to/file.js", "description": "Why this file is touched" }
       ],
       "tasks": [
         { "id": "1.0", "title": "Write all tests first", "status": "pending", "priority": "critical",
           "subtasks": [
             { "id": "1.1", "title": "Create Feature artifact", "status": "pending" },
             { "id": "1.2", "title": "Write happy path tests", "status": "pending" },
             { "id": "1.3", "title": "Write edge case tests", "status": "pending" }
           ]
         },
         { "id": "2.0", "title": "Implement to make tests pass", "status": "pending", "priority": "critical",
           "subtasks": []
         },
         { "id": "3.0", "title": "All tests green — review for gaps", "status": "pending", "priority": "high",
           "subtasks": []
         }
       ],
       "notes": []
     }
   }
   ```

3. **Update task statuses throughout the workflow** using partial updates (never re-upsert full content):
   ```
   # Starting a task
   helpmetest_upsert_artifact({ id: "tasks-[name]", content: { "tasks.0.status": "in_progress" } })

   # Finishing a subtask
   helpmetest_upsert_artifact({ id: "tasks-[name]", content: { "tasks.0.subtasks.0.status": "done" } })

   # Blocked with reason
   helpmetest_upsert_artifact({ id: "tasks-[name]", content: { "tasks.1.status": "blocked", "tasks.1.notes": "Waiting for..." } })
   ```

**The Tasks artifact is your contract with the user.** It shows exactly what's planned, what's being worked on, and what's done — at any point in the session.

### Step 1: Understand What Needs to Change

Ask the user:
1. **What's changing?** (new feature / refactoring / bug fix / enhancement)
2. **What's the expected behavior?** (what should work after the change)
3. **What URL/port is affected?** (localhost:3000? production URL?)
4. **What hostname does the app use?** (localhost? myapp.local? important for proxy)

### Step 2: Propose Test-First Approach

Explain to the user:

```
I'll use Test-Driven Development with HelpMeTest:

1. First: Write ALL comprehensive end-to-end tests that define what "done" looks like
   - Happy path scenarios (feature works as expected)
   - Edge cases (boundary conditions, unusual inputs)
   - Error scenarios (how it should handle failures)
   - NOT just 1-2 tests - ALL tests for complete coverage

2. Create Feature artifact linking all test scenarios

3. These tests will FAIL initially - that's expected and good!
   - Failing tests show what needs to be implemented
   - They're your specification in executable form

4. Then: Implement code incrementally to make tests pass
   - Make small changes
   - Run tests after each logical step
   - Use test failures to guide next steps

5. Done when: All tests pass + no new edge cases discovered

Do you want to proceed with test-first approach?
```

**If user says no**: Ask why, but gently encourage - "Tests written first catch issues earlier and serve as living documentation. Can I at least write a few core tests to guide implementation?"

**If user agrees**: Proceed to Step 3.

### Step 3: Set Up Local Development (if testing localhost)

**CRITICAL: If testing local development (localhost), set up proxy FIRST before writing tests.**

#### Check if User Has Local Server Running

Ask: "Do you have a local server running? If so, what port?"

If no server exists yet, help them set one up:
```bash
# Simple HTTP server
cd /path/to/app
python3 -m http.server 3000
# Or node http-server, or their framework's dev server
```

#### Start HelpMeTest Proxy

**Use the helpmetest-proxy skill to set up tunnels:**

The proxy skill will guide you through:
- Choosing the right strategy (single tunnel, separate tunnels, or production substitution)
- Starting the tunnel via the MCP tool
- Verifying it works with HelpMeTest interactive commands

**Quick reference:**
```
# Most common: single tunnel
helpmetest_proxy({ action: "start", domain: "dev.local", sourcePort: 3000 })

# Verify before proceeding (use HelpMeTest, NOT curl or browser)
helpmetest_run_interactive_command({ command: "Go To  http://dev.local" })
# Should load your local app
```

**The proxied URL only works inside HelpMeTest test commands** — not in your local browser or curl.

**Only write tests after proxy is confirmed working.**

For detailed proxy setup, troubleshooting, and all strategies, use the helpmetest-proxy skill.

### Step 4: Write ALL Comprehensive Tests First

**CRITICAL: Write ALL tests before ANY implementation. Not 1 test. ALL tests.**

#### Create Feature Artifact FIRST

Before writing tests, create the Feature artifact to organize scenarios:

Call `how_to({ type: "context_discovery" })` to check for existing artifacts.

Create Feature artifact:
```json
{
  "id": "feature-[name]",
  "type": "Feature",
  "name": "Feature: [Name]",
  "content": {
    "goal": "What this feature accomplishes",
    "non_goals": ["What this is NOT"],
    "status": "untested",
    "functional": [
      {
        "name": "Scenario name",
        "given": "Precondition",
        "when": "Action",
        "then": "Expected outcome",
        "tags": ["priority:critical"],
        "test_ids": []  // Will populate as we create tests
      }
    ],
    "edge_cases": [],
    "non_functional": [],
    "bugs": [],
    "persona_ids": []
  }
}
```

#### Write Tests for New Features

Write tests covering:

1. **Happy Path Scenarios** (3-5 tests):
   - User can successfully complete the main workflow
   - Data persists correctly
   - UI shows correct feedback
   - Navigation works as expected

2. **Edge Cases** (3-5 tests):
   - Empty inputs
   - Invalid formats
   - Boundary values (too long, too short, negative numbers)
   - Duplicate entries
   - Wrong permissions/unauthorized access

3. **Error Scenarios** (2-3 tests):
   - API failures
   - Network timeouts
   - Missing required data
   - Concurrent operations

Use `helpmetest_upsert_test` for **EVERY** test:

**Robot Framework syntax patterns:**

```robot
# Navigate to page
Go To  http://localhost  timeout=5s

# Get text from element
${text}=  Get Text  [data-testid="some-element"]

# Get attribute value
${value}=  Get Property  input[name="field"]  value

# Click element
Click  [data-testid="submit-button"]

# Fill input field
Fill Text  input[name="username"]  testuser

# Wait for API response
Wait For Response  url=**/api/endpoint**  status=200  timeout=5s

# Wait for element state
Wait For Elements State  [data-testid="result"]  visible  timeout=5s

# Assertions
Should Be Equal  ${actual}  ${expected}
Should Be Equal As Numbers  ${num1}  ${num2}
Should Not Be Empty  ${text}

# Type conversion
${number}=  Convert To Integer  ${text}

# Reload page
Reload

# Wait/pause
Sleep  0.5s
```

**Common test structure:**

```robot
# Given - Set up initial state
Go To  http://localhost  timeout=5s
${initial_state}=  Get Text  [data-testid="element"]

# When - Perform the action being tested
Click  [data-testid="action-button"]
Wait For Response  url=**/api/action**  status=200

# Then - Verify the outcome
${result}=  Get Text  [data-testid="result"]
Should Be Equal  ${result}  expected_value

# Optional - Verify persistence
Reload
${persisted}=  Get Text  [data-testid="element"]
Should Be Equal  ${persisted}  ${result}
```

**Test naming**: Descriptive names like "User can submit form and data persists after reload"

**Link tests to Feature artifact**: Add each test ID to the corresponding scenario's `test_ids` array.

#### For Refactoring

**CRITICAL**: Tests must capture EXISTING behavior BEFORE refactoring.

1. Navigate to the code being refactored
2. Understand current behavior - what does it do now?
3. Write tests that verify current behavior works
4. Run tests to confirm they pass with current code
5. Then refactor
6. Run tests again to verify no regression

#### For Bug Fixes

Write a test that REPRODUCES the bug:

```robot
# Bug reproduction: Steps that trigger the specific bug
Go To  http://localhost  timeout=5s

# Set up the conditions that cause the bug
${initial_state}=  Get Text  [data-testid="element"]

# Perform the action that triggers the bug
Click  [data-testid="trigger-button"]

# Expected behavior: what SHOULD happen
# Actual behavior (before fix): what currently happens (test will FAIL)
${actual}=  Get Text  [data-testid="result"]
Should Be Equal  ${actual}  expected_correct_value
```

The test will FAIL before the bug is fixed, then PASS after.

### Step 5: Run All Tests (Expect Failures)

After writing ALL tests, run them using `helpmetest_run_test`:

```
helpmetest_run_test({ id: "test-id" })
```

**Explain failures to user:**

```
✅ Test Suite Created: [X] tests written

Expected Results (tests SHOULD fail now):
- [Test 1]: ❌ Will fail - feature not implemented yet
- [Test 2]: ❌ Will fail - API endpoint doesn't exist
- [Test 3]: ❌ Will fail - UI elements not created
...

This is GOOD! Failing tests show exactly what needs to be built.
They're your roadmap for implementation.

Ready to start implementing?
```

### Step 6: Implement Incrementally

**Process:**

1. **Pick the highest priority failing test** (priority:critical first)
2. **Explain what needs to be implemented** to make it pass
3. **Make the minimal change** to progress toward green
4. **Check syntax** (if code language):
   ```bash
   # JavaScript
   node -c app.js

   # Python
   python -m py_compile script.py

   # Others: use language's syntax checker
   ```
5. **Run that specific test**
6. **If test passes**: Move to next failing test
7. **If test still fails**: Analyze failure, implement more, check syntax, re-run

**When to run tests:**
- ✅ After implementing a complete function/component
- ✅ After fixing a syntax error
- ✅ After adding a feature piece (e.g., API endpoint, UI handler)
- ❌ NOT after every single line (too frequent)
- ❌ NOT only at the end (defeats TDD purpose)

**Balance**: Run tests when you've completed something meaningful toward making a test pass.

### Step 7: Handle Test Failures During Implementation

When a test fails during implementation:

**1. Check for syntax errors FIRST:**
```bash
# Run syntax checker for your language
node -c file.js  # JavaScript
python -m py_compile file.py  # Python
# etc.
```

If syntax error: fix it, re-run test.

**2. If no syntax error, read the test failure:**
   - What step failed?
   - What was expected vs actual?
   - Any error messages?

**3. Determine cause:**
   - Implementation incomplete? → Continue implementing
   - Implementation bug? → Fix the code
   - Test wrong? → Review test (rare - tests were written based on requirements)

**4. Debug interactively** if unclear:
   ```robot
   # Run test steps manually to see what's happening
   Go To  http://localhost  timeout=5s

   # See what's actually on the page
   Get Elements  button  # All buttons
   Get Text  .result  # What result is shown?

   # Try the action
   Click  button >> "Submit"
   # Did it work? Check the response
   ```

**5. Fix and re-run:**
   - Make the fix
   - Check syntax again
   - Run the failing test
   - If passes, continue to next test
   - If still fails, repeat debugging

### Step 8: All Tests Green - But Are We Done?

When all tests pass, **don't claim done yet**. Review for missing edge cases:

**Ask yourself:**
1. What happens if user does X twice?
2. What if API is slow/times out?
3. What if user has no permission?
4. What about concurrent users?
5. What about large data sets?

**If you find gaps:**

```
✅ All [X] tests passing!

But I found potential edge cases not covered:
1. What if user adds 1000 items? (performance)
2. What if two users edit same item? (race condition)
3. What if API is down? (error handling)

Should I write tests for these scenarios?
```

**If user agrees**: Write additional tests, they'll likely fail, implement fixes, re-run.

**If no gaps found**:

```
✅ All [X] tests passing!
✅ No obvious edge cases missing
✅ Feature appears complete

Ready to mark as done?
```

### Step 9: Final Validation

Run ALL tests one more time to ensure nothing broke:

```
# Run all tests for this feature
helpmetest_run_test({ tags: ["feature:[feature-name]"] })
```

If any test fails:
1. Identify which test broke and why
2. Determine if it's a regression
3. Fix the code or update the test (with user approval)

### Step 10: Mark as Complete

Only when:
- ✅ All new tests pass
- ✅ No existing tests broken (or intentionally updated)
- ✅ No obvious edge cases missing
- ✅ User confirms implementation matches requirements
- ✅ Feature artifact updated with status: "working"
- ✅ Tasks artifact — mark all tasks done:
  ```
  helpmetest_upsert_artifact({ id: "tasks-[name]", content: { "tasks.0.status": "done", "tasks.1.status": "done", "tasks.2.status": "done" } })
  ```

**Summary to user:**

```
✅ Implementation Complete!

Tests Written: [X] total
- [Y] happy path scenarios
- [Z] edge cases
- [W] error scenarios

All tests passing ✅

Changes made:
- [list files changed]
- [list key functionality added]

Test coverage ensures:
- Feature works as expected
- Edge cases handled
- No regressions introduced
```

## Best Practices

### Writing Good Tests

**Tests should verify business outcomes**, not implementation details:

❌ Bad test:
```robot
# Just checks element exists - doesn't verify functionality
Wait For Elements State  [data-testid="submit-button"]  visible
```

✅ Good test:
```robot
# Verifies the business outcome - data persists after submission
Fill Text  input[name="field"]  test_value
Click  [data-testid="submit-button"]
Wait For Response  url=**/api/save**  status=200

Reload
Wait For Elements State  input[name="field"]  visible
${value}=  Get Property  input[name="field"]  value
Should Be Equal  ${value}  test_value
```

### Syntax Checking

**Always check syntax before running tests** if you're modifying code:

```bash
# JavaScript
node -c file.js && echo "✅ Syntax OK"

# Python
python -m py_compile file.py && echo "✅ Syntax OK"

# TypeScript
tsc --noEmit && echo "✅ Syntax OK"
```

Syntax errors waste time - catch them before running tests.

### Proxy Troubleshooting

**If tests can't reach your local server**, use the `/proxy` skill for complete troubleshooting:
- Verifying proxy is running: `helpmetest_proxy({ action: "list" })`
- Checking local server connectivity
- Fixing stale frpc processes or MCP server running old code
- Choosing the right proxy strategy (single tunnel, separate tunnels, production substitution)
- WebSocket limitations (wss:// works, ws:// doesn't)

## Tag Schema

Use these tags for TDD tests:

- `tdd:new-feature` - Test for new functionality
- `tdd:refactoring-guard` - Test capturing existing behavior before refactoring
- `tdd:bug-fix` - Test reproducing a bug (should fail initially, pass after fix)
- `tdd:edge-case` - Additional edge case discovered after initial implementation

Also include standard tags:
- `priority:critical|high|medium|low`
- `feature:[feature-name]`
- `bug:[bug-id]` (if applicable)

## Critical Rules

1. **Write ALL tests first** - Not 1 test. ALL tests (happy path, edge cases, errors) before ANY implementation
2. **Create Feature artifact early** - Before writing tests, create artifact to organize scenarios
3. **Set up proxy for localhost** - Must be running before tests execute
4. **Check syntax frequently** - Before running tests, after code changes
5. **Expect failures** - Initial test failures are good, they define the work
6. **Run tests after logical steps** - Not every line, not only at end
7. **Green isn't done** - All tests passing means review for missing edge cases
8. **Tests are guardrails** - If test fails after change, either fix code or (rarely) fix test
9. **No feature complete** until all tests pass + no gaps found

## Example: Complete TDD Flow

See `references/examples/wishlist-example.md` for a complete walkthrough of adding a wishlist feature using TDD — covering proxy setup, test creation, incremental implementation, and edge case discovery.

**Version:** 0.1
