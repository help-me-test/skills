# Debugging Failing Tests

**DO NOT guess or make blind fixes. Use interactive debugging.**

## Step 1: Reproduce Failure Interactively

Run the exact test steps interactively, one at a time:

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

## Step 2: Investigate the Exact Failure Point

### If "Element not found"

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

### If "Click failed" / "Not interactable"

```robot
# Check element state
Get Element State  <selector>  visible
Get Element State  <selector>  enabled

# Check if overlapped or need scroll
Scroll To Element  <selector>
Wait For Elements State  <selector>  enabled  timeout=5000

# Document: What's needed before click?
```

### If "Assertion failed" / "Wrong value"

```robot
# Check actual values
Get Text  <selector>  # What's actually displayed?
Get Attribute  <selector>  value  # What's the actual value?

# Check page state
Get Url  # Right page?
Get Elements  .error  # Any errors?

# Document: Is actual value a bug or did test expect wrong thing?
```

### If "Timeout" / "No response"

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

## Step 3: Determine Root Cause

Based on interactive investigation:
- **Test issue:** Selector wrong, timing issue, wrong expectation → Fix test
- **Application bug:** Feature broken, returns error, doesn't save → Document bug

## Step 4A: If TEST Issue - Fix and Validate Interactively

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

## Step 4B: If APPLICATION Bug - Document in Feature.bugs

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

## Step 5: Update Test with Fixes (if test issue)

- Use `helpmetest_upsert_test` with validated corrections
- Re-run test to confirm it passes
- If still fails, return to Step 1

## Step 6: Verify Fix

- Run test again
- Confirm it passes
- If fails, repeat debugging process
