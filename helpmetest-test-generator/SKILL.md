---
name: helpmetest-test-generator
description: "Generate validated tests from discovered scenarios. Use ONLY after feature discovery complete. Use when user says 'generate tests', 'create tests for X', 'write tests', or Feature artifacts have enumerated scenarios ready for test creation. Validates all tests, debugs failures, links to scenarios."
allowed-tools: mcp__helpmetest-*
---

# QA Test Generator

Generates tests for ONE feature at a time.

**Scope:** This skill works on a SINGLE FEATURE. Use `/helpmetest` for comprehensive site testing.

**CRITICAL: This skill is for PHASE 3 (Test Generation) ONLY.**

**DO NOT use this skill until:**
- ✅ ALL features have been discovered
- ✅ ALL scenarios have been enumerated (functional + edge_cases + non_functional)
- ✅ Features have been explored interactively to discover test scenarios
- ✅ Phase 2 (Feature Enumeration) is 100% complete

**If you're still discovering features or enumerating scenarios, use /helpmetest-discover instead.**

## Prerequisites

**MANDATORY:** Before generating ANY test, call:
```
how_to({ type: "test_quality_guardrails" })
how_to({ type: "tag_schema" })
how_to({ type: "interactive_debugging" })
```

## Input

- Feature artifact ID (e.g., "feature-checkout") - optional if can be inferred

## Workflow

### Phase 0: Context Discovery

**MANDATORY:** Call `how_to({ type: "context_discovery" })` to check for existing work before asking user for input.

- Prioritize features with `status: "untested"`
- Find scenarios with empty `test_ids` arrays
- **CRITICAL: Sort scenarios by priority** - `priority:critical` MUST be tested before `priority:high/medium/low`
- **Validate coverage** - Before claiming "all features tested", verify ALL `priority:critical` scenarios have test_ids
- If user says "continue"/"next" → auto-select first untested feature with critical scenarios

### Phase 1: Understand the Feature

1. **Read Feature artifact** using `helpmetest_get_artifact`
2. **Extract**:
   - goal - What must work?
   - persona_ids - Who can use this? (get auth_state from Persona)
   - functional - Main scenarios (Given/When/Then)
   - edge_cases - Boundary conditions
   - bugs - Known broken scenarios (skip these)

### Phase 2: Generate Tests for Scenarios

**NOTE: Scenarios were already explored interactively during discovery (Feature Enumeration phase). Now we generate tests based on those scenarios.**

**If scenarios in Feature artifact lack detail (missing selectors, unclear steps):**
- This means discovery phase wasn't thorough enough
- Go back and explore the feature interactively to document missing details
- Update Feature artifact scenarios with discovered information
- Then proceed with test generation

**MANDATORY TEST GENERATION ORDER:**
1. **Generate `priority:critical` scenarios FIRST** - These are end-to-end workflows that verify core business value
2. **Then generate `priority:high` scenarios** - Important but not mission-critical
3. **Finally generate `priority:medium/low` scenarios** - Nice-to-have coverage

**CRITICAL vs. PARTIAL test distinction:**
- ❌ **PARTIAL test** - "User can view form page" (just navigation, verifies form fields exist)
- ✅ **CRITICAL test** - "User completes the workflow" (full end-to-end transaction from start to confirmation)

**Before claiming feature is "tested":**
- ALL `priority:critical` scenarios MUST have `test_ids` populated
- If ANY critical scenario is untested, feature status is "untested"
- Don't generate 10 partial tests and skip the 1 critical end-to-end flow

For each functional scenario (starting with critical), create test using `helpmetest_upsert_test`:

```robot
*** Test Cases ***
<scenario.name>
    [Documentation]    Given: <given> | When: <when> | Then: <then>
    [Tags]    priority:high    feature:<feature_id>    project:<project_id>

    # Setup - authenticate if needed
    As  <auth_state>
    Go To  <scenario.url>

    # Given - establish precondition
    <steps to establish 'given' state>

    # When - perform action
    <steps for 'when' action>

    # Then - verify outcome
    <assertions for 'then' expected outcome>
```

**Test naming rules:**
- **NO project/site names** in test names (e.g., NOT "EverShop User Login")
- **Use feature descriptions** from scenario.name (e.g., "User can login with valid credentials")
- **Format:** `<Actor> can <action> <object>` OR `<Feature> <behavior>`
- **Examples:**
  - ✅ "User can update profile email"
  - ✅ "Cart total updates when quantity changes"
  - ✅ "Registration validates email format"
  - ❌ "EverShop Registration Test"
  - ❌ "QA Playground Login"
  - ❌ "SiteName Profile Update"

**Test requirements:**
- 5+ meaningful steps
- Verify actual business outcomes
- Use stable selectors
- Include relevant assertions
- Use `Create Fake Email` for registration/email tests (never hardcode emails)

### Phase 3: Generate Edge Case Tests

For critical edge_cases:

```robot
*** Test Cases ***
Edge Case: <scenario.name>
    [Documentation]    Given: <given> | When: <when> | Then: <then>
    [Tags]    priority:medium    feature:<feature_id>    project:<project_id>

    # Setup and execute edge case scenario
    ...
```

### Phase 4: Validate Test Quality

**MANDATORY:** After creating each test, validate it using `/helpmetest-validator`:

1. Pass test ID and feature ID to validator
2. Validator checks:
   - Business value (would test fail if feature broken?)
   - No bullshit patterns (element counting, click without verification)
   - Proper assertions and state verification
3. **If REJECTED:**
   - Read validator feedback
   - Fix test based on specific issues
   - Validate again
   - Repeat until PASSED
4. **If PASSED:**
   - Continue to Phase 6

**DO NOT SKIP THIS STEP** - all tests must pass validation before running.

### Phase 5: Link Tests to Scenarios

Update Feature artifact - add test_id to each scenario's test_ids:

```json
{
  "functional": [
    {
      "name": "Create new item",
      "given": "...",
      "when": "...",
      "then": "...",
      "test_ids": ["test-create-new-item"]
    }
  ]
}
```

### Phase 6: Run and Debug Tests

1. **Run test** using `helpmetest_run_test`

2. **If test PASSES:**
   - ✅ Move to next scenario
   - Update scenario status

3. **If test FAILS - Debug interactively (MANDATORY):**

   **DO NOT guess or make blind fixes. Use interactive debugging.**

   **Step 6.1: Reproduce failure interactively**
   ```robot
   # Run the exact test steps interactively
   As  <auth_state>
   Go To  <scenario.url>

   # Execute each step from the test ONE AT A TIME
   <step 1>
   # Observe: Did it work? Check the result.

   <step 2>
   # Observe: Did it work? Check the result.

   <failing step>
   # Observe: What error? What's the page state?
   ```

   **Step 6.2: Investigate the exact failure point**

   **If "Element not found":**
   ```robot
   # Find what's actually on the page
   Get Elements  button  # All buttons
   Get Elements  input  # All inputs
   Get Elements  [data-testid]  # Test IDs
   Get Elements  <failing-selector>  # Exact failing selector

   # Try alternate selectors
   Get Elements  button >> "Submit"
   Get Elements  button.primary
   Get Elements  [type="submit"]

   # Document: What selector SHOULD we use?
   ```

   **If "Click failed" / "Not interactable":**
   ```robot
   # Check element state
   Get Element State  <selector>  visible
   Get Element State  <selector>  enabled

   # Check if overlapped or need scroll
   Scroll To Element  <selector>
   Wait For Elements State  <selector>  enabled  timeout=5000

   # Document: What's needed before click?
   ```

   **If "Assertion failed" / "Wrong value":**
   ```robot
   # Check actual values
   Get Text  <selector>  # What's actually displayed?
   Get Attribute  <selector>  value  # What's the actual value?

   # Check page state
   Get Url  # Right page?
   Get Elements  .error  # Any errors?

   # Document: Is actual value a bug or did test expect wrong thing?
   ```

   **If "Timeout" / "No response":**
   ```robot
   # Try with longer timeout
   Wait For Response  url=<expected>  timeout=30000

   # Check if API call happens at all
   # Check current URL
   Get Url

   # Check if page is in error state
   Get Elements  .error
   Get Text  .error

   # Document: Is app slow or is request failing?
   ```

   **Step 6.3: Determine root cause**

   Based on interactive investigation:
   - **Test issue:** Selector wrong, timing issue, wrong expectation → Fix test
   - **Application bug:** Feature broken, returns error, doesn't save → Document bug

   **Step 6.4A: If TEST issue - Fix and validate interactively**
   ```robot
   # Run COMPLETE corrected flow to prove it works
   As  <auth_state>
   Go To  <url>

   # All steps with corrections applied
   Fill Text  <CORRECTED-selector>  <value>
   Wait For Elements State  <button>  enabled  # ADDED wait
   Click  <button>
   Wait For Response  url=/api/save  status=200  # ADDED verification
   Get Text  .success  ==  Data saved  # CORRECTED expected value

   # Verify persistence
   Reload
   Get Attribute  <selector>  value  ==  <value>
   ```

   **→ Only update test when ENTIRE flow works interactively**

   **Step 6.4B: If APPLICATION bug - Document in Feature.bugs**
   ```json
   {
     "name": "Brief bug description",
     "given": "Precondition from scenario",
     "when": "Action from scenario",
     "then": "Expected from scenario",
     "actual": "What actually happens (from interactive investigation)",
     "severity": "blocker|critical|major|minor",
     "test_ids": ["test-id"],
     "tags": ["priority:high", "severity:critical"]
   }
   ```

   **Step 6.5: Update test with fixes (if test issue)**
   - Use `helpmetest_upsert_test` with validated corrections
   - Re-run test to confirm it passes
   - If still fails, return to Step 7.1

   **Step 6.6: Verify fix**
   - Run test again
   - Confirm it passes
   - If fails, repeat debugging process

4. **Update Feature.status** based on results:
   - All tests pass → "working"
   - All tests fail due to bugs → "broken"
   - Mixed → "partial"

## Output

- Test files created via `helpmetest_upsert_test`
- All tests debugged and fixed OR bugs documented
- Feature artifact updated with test_ids on scenarios
- Feature.bugs[] populated for application bugs
- Feature.status updated
- Summary of tests generated, pass rates, bugs found

## Test Quality Requirements

**MANDATORY:** Before creating any test, review anti-patterns and quality standards:

```
how_to({ type: "test_quality_guardrails" })
```

This includes:
- ❌ Bullshit test anti-patterns (element counting, click without verification, etc.)
- ✅ Real test patterns (complete workflows with outcome verification)
- Quality checklist (5+ steps, business outcomes, state verification)
- Red flags to avoid

## Quality Checklist

**Before creating ANY test, answer:**
1. "What business capability does this test verify?"
2. "If this test passes but the feature is broken, is that possible?"
   - If YES → Test is bullshit, rewrite it
   - If NO → Test is valid

**Test MUST have:**
- [ ] 5+ meaningful steps (not just navigation + counting)
- [ ] Verifies business outcome (data saved, filter applied, order created)
- [ ] Includes state change verification (before/after comparison OR API response check)
- [ ] Uses stable selectors (data-testid preferred)
- [ ] Has proper assertions that would FAIL if feature broken
- [ ] Was validated interactively first

**Test MUST NOT have:**
- [ ] Only navigation + element counting
- [ ] Click without verifying result of click
- [ ] Form display without testing form submission
- [ ] Success message verification without checking data persisted

## FakeMail Keywords

For registration and email verification tests, use FakeMail:

```robot
# Generate unique test email
${email}=  Create Fake Email
# Returns: adventure.acme@fakemail.helpmetest.com

# Use in registration
Fill Text  input[name=email]  ${email}
Click  button >> "Register"

# Get verification code from email
${code}=  Get Email Verification Code  ${email}
Fill Text  input[name=code]  ${code}

# Cleanup after test
Delete Email  ${email}
```

**NEVER hardcode emails** - always use `Create Fake Email`.

## Tag Schema (REQUIRED)

**Format:** ALL tags MUST use `category:value` format.

### Required Test Tags
- `priority:X` - REQUIRED. Values: `critical`, `high`, `medium`, `low`

### Allowed Test Tags
- `project:X` - ProjectOverview ID (e.g., `project:evershop`, `project:qa-playground-hub`)
- `feature:X` - Feature area (e.g., `feature:login`, `feature:cart`, `feature:checkout`)
- `role:X` - Persona type (e.g., `role:customer`, `role:admin`, `role:qa-engineer`)
- `url:X` - Associated URL (e.g., `url:playground.helpmetest.com`)

### Invalid Tags (DO NOT USE)
❌ Flat tags: `critical`, `e2e`, `login`
❌ Wrong separators: `feature_login`, `priority-high`
❌ Wrong case: `Priority:Critical`, `FEATURE:LOGIN`
❌ Invalid categories: `type:`, `platform:`, `browser:`, `scenario:`, `status:`

### Valid Example
```robot
[Tags]    priority:critical    feature:login    project:evershop
```

## Critical Rules

1. **No bullshit tests** - "Click button, verify page" is NOT a test
2. **Test interactively first** - Never create blind tests
3. **Given/When/Then** - Map scenario to test steps
4. **Link to scenario** - Add test_id to scenario.test_ids
5. **Use FakeMail** - Never hardcode test emails
6. **Tag properly** - All tests need `priority:` tag minimum

**Version:** 0.1
