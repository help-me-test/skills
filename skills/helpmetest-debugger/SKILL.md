---
name: helpmetest-debugger
description: "Debug failing tests. Determines if failure is a bug or test issue. Fixes tests or documents bugs in Feature.bugs."
allowed-tools: mcp__helpmetest-*
---

# QA Debugger

Debugs failing tests to determine root cause and fix.

**Golden Rule: ALWAYS reproduce interactively before fixing. Never guess. Never make blind fixes.**

## Prerequisites

**MANDATORY:** Before debugging, call:
```
how_to({ type: "interactive_debugging" })
how_to({ type: "debugging_self_healing" })
```

## Input

- Failing test ID
- Error message/logs
- Feature artifact the test belongs to

## Workflow

### Phase 1: Understand the Failure

1. **Get test details** using `helpmetest_open_test`
2. **Get test history** using `helpmetest_status({ id: "test-id", testRunLimit: 10 })`
3. **Classify failure pattern** (see debugging_self_healing.md patterns):
   - Selector issue? Timing issue? State issue? API issue? Data issue? **Test isolation?**
   - Refer to pattern categories to identify symptoms and determine root cause
4. **Get Feature** using `helpmetest_get_artifact`
5. **Identify failure point**:
   - Which step failed?
   - What was the error?
   - What was expected vs actual?

### Phase 2: Reproduce Interactively (CRITICAL - NEVER SKIP THIS)

**MANDATORY:** Use `helpmetest_run_interactive_command` to execute the test manually, step by step.

1. **Get Persona** for auth_state if needed

2. **Start interactive session** - Execute steps ONE AT A TIME, observing after EACH step:
   ```robot
   As  <auth_state>
   Go To  <url>
   ```
   **→ Observe:** Did page load? Check URL. Look at page content.

3. **Execute steps leading up to failure** - Run each step separately:
   ```robot
   Fill Text  <selector>  <value>
   ```
   **→ Observe:** Did field get filled? Check with `Get Attribute  <selector>  value`

   ```robot
   Click  <button-selector>
   ```
   **→ Observe:** What happened after click? Did page change? Check `Get Url`

4. **When you reach the failing step, investigate based on error type:**

   **Element not found:**
   - List all elements of that type on the page (buttons, inputs, etc.)
   - Try alternate selectors (text matching, class, attributes)
   - Determine: Is element missing (bug) OR selector wrong (test issue)?

   **Element not interactable:**
   - Check if element is visible and enabled
   - Check if need to scroll to element
   - Check if multiple matches exist
   - Check if need to wait for element to become interactable
   - Determine: What's blocking interaction?

   **Wrong value/assertion failed:**
   - Check what's actually displayed
   - Check what page you're on
   - Check for error messages on page
   - Determine: Is behavior a bug OR did expectations change?

   **Timeout/page load failure:**
   - Try with longer timeout
   - Check where you ended up (Get Url)
   - Check for API responses
   - Wait for key elements that indicate page loaded
   - Determine: Is app slow (increase timeout) OR broken (bug)?

5. **Document findings after investigation:**
   - Exact step that failed
   - What you expected
   - What actually happened
   - Root cause (selector wrong, timing issue, feature broken, etc.)

### Phase 3: Determine Root Cause

Refer to `debugging_self_healing.md` for all failure pattern categories and fixes.

Quick reference:
- **Test isolation**: Alternating PASS/FAIL + changing error values + shared state → Make idempotent
- **Selector issues**: Element not found → Fix selector or document bug
- **Timing issues**: Timeouts, element not visible → Add waits
- **State issues**: Auth/session problems → Verify state restoration
- **API issues**: Backend errors → Document as bug
- **Data issues**: Conflicts, duplicates → Use unique data or cleanup

### Phase 4A: Fix Test Issue

If problem is with the test (NOT a bug in the application):

1. **Identify fix** based on interactive investigation:
   - Update selector (found correct selector during investigation)
   - Add wait/timeout (saw element appears after delay)
   - Fix expected value (saw actual correct value during investigation)
   - Add missing setup step (discovered required state during investigation)

2. **VALIDATE fix interactively BEFORE updating test** (CRITICAL):

   Run the COMPLETE corrected flow interactively to prove it works:
   ```robot
   # Run the FULL test with fixes applied
   As  <auth_state>
   Go To  <url>

   # Step 1 with fix
   Fill Text  <corrected-selector>  <value>
   Get Attribute  <corrected-selector>  value  ==  <value>  # Verify it worked

   # Step 2 with fix
   Wait For Elements State  <button>  enabled  timeout=5000  # Added wait
   Click  <button>

   # Step 3 with fix
   Wait For Response  url=/api/submit  status=200  # Verify API call
   Get Text  .success  ==  Saved successfully  # Updated expected text

   # Verify outcome
   Go To  <url>  # Reload to verify persistence
   Get Attribute  <selector>  value  ==  <value>  # Confirm data saved
   ```

   **→ If ANY step fails during interactive validation, STOP and investigate more**
   **→ Only proceed when ENTIRE flow runs successfully interactively**

3. **Update test** using `helpmetest_upsert_test` with validated fixes

4. **Run test** using `helpmetest_run_test` to confirm automated version works

5. **If test STILL fails:**
   - Return to Phase 2 (reproduce interactively)
   - Compare automated test output with interactive output
   - Find the difference
   - Repeat until test passes

### Phase 4B: Document Bug

If problem is with the feature:

1. **Add bug to Feature.bugs**:
   ```json
   {
     "name": "Brief description",
     "given": "Precondition",
     "when": "Action taken",
     "then": "Expected outcome",
     "actual": "What actually happens",
     "severity": "blocker|critical|major|minor",
     "url": "http://example.com/page",
     "tags": ["affects:all-users"],
     "test_ids": []
   }
   ```

2. **Update Feature.status** to "broken" or "partial"

3. **Skip or tag test** until bug is fixed

### Phase 5: Update Feature Status

After debugging:

1. **Update Feature.status**:
   - "working": All scenarios pass
   - "broken": Critical scenarios fail due to bugs
   - "partial": Some scenarios pass, some fail

2. **Update ProjectOverview.features** with works: true/false

## Output

- Root cause identified
- Test fixed OR bug documented
- Feature.status updated
- Summary of actions taken

## Self-Healing Patterns

Refer to `debugging_self_healing.md` for all auto-fixable patterns and strategies.

## Critical Rules

1. **Always reproduce first** - Don't guess, verify
2. **Determine bug vs test issue** - Different actions needed
3. **Update artifacts** - All findings go into Feature
4. **Verify fixes** - Run test after fixing

**Version:** 0.1
