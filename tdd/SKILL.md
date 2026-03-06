---
name: tdd
description: "Test-Driven Development enforcer using HelpMeTest. Use when user wants to implement new feature, refactor code, or fix bugs. Forces test-first workflow: write ALL comprehensive end-to-end tests before ANY implementation, use tests as guardrails during development, ensure all tests pass before claiming done. Use when user says 'implement X', 'add feature Y', 'refactor Z', 'fix bug', or starts coding without tests."
allowed-tools: mcp__helpmetest-*
---

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

**Why proxy is needed:** HelpMeTest tests run against URLs. For local development, the proxy tunnels `http://localhost` (or custom hostname) to your local port.

**Proxy command format:**
```bash
# If app works with localhost hostname:
helpmetest proxy start localhost:3000

# If app needs specific hostname (for cookies/config/APIs):
helpmetest proxy start myapp.local:3000
```

**How it works:**
- Tests use: `Go To  http://localhost` (or `http://myapp.local`)
- Proxy routes that to your local port (e.g., 3000)
- App runs locally, tests access it through proxy

**Verify proxy is running:**
```
✓ Proxying localhost -> localhost:3000
```

**Important:** Proxy must stay running. Start it in background before writing tests.

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

```robot
*** Test Cases ***
User can [accomplish goal]
    [Documentation]    Given: [precondition] | When: [action] | Then: [expected outcome]
    [Tags]    priority:critical    feature:[feature-name]    tdd:new-feature

    # Setup
    As  [auth-state]
    Go To  http://localhost  timeout=5000  # or http://[custom-hostname]

    # Given - establish precondition
    [setup steps]

    # When - perform action
    [action steps]

    # Then - verify outcome
    [assertions that would FAIL if feature broken]
    Wait For Response  url=[expected-api-call]  status=200
    Get Text  [success-indicator]  ==  [expected-message]

    # Verify persistence
    Reload
    [verify data persisted]
```

**Test naming**: Descriptive names like "User can add item to cart and quantity persists after reload"

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
*** Test Cases ***
Bug: [Description of bug]
    [Documentation]    Reproduces bug #123 - [what's broken]
    [Tags]    priority:critical    feature:[feature]    tdd:bug-fix    bug:123

    # Steps that trigger the bug
    # Expected: [what should happen]
    # Actual (before fix): [what actually happens - test will fail]
```

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
   Go To  http://localhost  timeout=5000

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
Get Element Count  input[name=quantity]  ==  1  # Just checks element exists
```

✅ Good test:
```robot
Fill Text  input[name=quantity]  5
Click  button >> "Update"
Wait For Response  url=/api/cart/update  status=200
Reload
Get Property  input[name=quantity]  value  ==  5  # Verifies persistence
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

**If tests can't reach localhost:**

1. Check proxy is running: `ps aux | grep "helpmetest proxy"`
2. Check local server is running: `curl http://localhost:3000`
3. Verify proxy output shows: `✓ Proxying localhost -> localhost:3000`
4. Try restarting proxy: kill the process, run `helpmetest proxy start localhost:3000` again

**If app needs specific hostname:**

Some apps require a specific hostname (not localhost) for:
- Cookies (set to specific domain)
- API configuration (hardcoded domain)
- Authentication callbacks

Solution: Use hostname in proxy command:
```bash
helpmetest proxy start myapp.local:3000
```

Then tests use: `Go To  http://myapp.local`

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

**User**: "Add a wishlist feature where users can save items for later"

**TDD Agent**:

```
Step 1: Understanding requirements
- Add items to wishlist
- View wishlist
- Remove from wishlist
- Persist across sessions

Step 2: Setting up local development
Is your app running on localhost? What port?

Step 3: Starting proxy
$ helpmetest proxy start localhost:3000
✓ Proxying localhost -> localhost:3000

Step 4: Creating Feature artifact...
[creates feature-wishlist artifact]

Step 5: Writing ALL tests (not implementing yet!)

Tests to write:
1. ✅ Add item to wishlist (priority:critical)
2. ✅ View wishlist items (priority:critical)
3. ✅ Remove from wishlist (priority:critical)
4. ✅ Empty wishlist shows message (priority:medium)
5. ✅ Cannot add duplicate items (priority:high)
6. ✅ Wishlist persists after reload (priority:critical)
7. ✅ Add fails gracefully if API error (priority:medium)
8. ✅ Wishlist has max 100 items (priority:low)

Writing all 8 tests now...
[creates all 8 tests with helpmetest_upsert_test]

✅ 8 tests written. Running them...
[runs all tests]

Expected results:
❌ All 8 tests failing (feature not implemented)

This is GOOD! Tests show exactly what to build.

Step 6: Starting implementation...

Next: Make "Add item to wishlist" pass

Checking syntax...
✅ Syntax OK

Implementing add functionality...
[writes code]

Running test...
✅ Test passes!

Next: Make "View wishlist items" pass
[implements]
[checks syntax]
[runs test]
✅ Test passes!

[continues until all 8 tests pass]

✅ All 8 tests passing!

Reviewing for missing edge cases...
Found gap: What if user adds item while offline?

Writing test for offline scenario...
[writes test]
❌ Test fails as expected
[implements offline handling]
[checks syntax]
✅ Test passes!

✅ All 9 tests passing!
✅ No other edge cases found
✅ Feature complete!

Summary:
- 9 tests written (4 critical, 3 high, 2 medium)
- All tests passing ✅
- Covers happy paths, edge cases, and persistence
- Offline handling implemented
```

**Version:** 0.1
