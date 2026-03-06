# Interactive Debugging Investigation

**Philosophy: NEVER GUESS. Always investigate interactively to understand the actual problem.**

## Core Approach

1. **Reproduce the failure** - Run test steps interactively one by one
2. **Find the exact failure point** - Which step fails?
3. **Investigate why** - What's the actual page state when it fails?
4. **Determine root cause** - Bug vs test issue?
5. **Fix correctly** - Update test OR document bug (never both)

## Investigation Techniques

### Finding What's Actually On The Page

```robot
# See all elements of a type
Get Elements  button
Get Elements  input
Get Elements  [data-testid]

# Try variations of failing selector
Get Elements  button >> "Submit"
Get Elements  button.primary
Get Elements  [type="submit"]
```

### Checking Element State

```robot
# Is it visible? Enabled?
Get Element State  <selector>  visible
Get Element State  <selector>  enabled

# Try making it interactable
Scroll To Element  <selector>
Wait For Elements State  <selector>  enabled  timeout=5000
```

### Inspecting Values

```robot
# What's actually displayed?
Get Text  <selector>

# What's the actual attribute value?
Get Attribute  <selector>  value

# Where am I?
Get Url

# Any errors shown?
Get Elements  .error
Get Text  .error
```

### Checking API Calls

```robot
# Wait longer to see if it's just slow
Wait For Response  url=<expected>  timeout=30000

# Check page state after action
Get Url  # Did navigation happen?
Get Elements  .success  # Did success message appear?
Get Elements  .error  # Did error occur?
```

## Decision Framework

After investigation, determine:

### Test Issue

**Indicators:**
- Selector wrong (element exists but different selector)
- Timing issue (element appears later, need wait)
- Wrong expectation (test expects wrong value, but app behavior is correct)

**Action:** Fix test, validate interactively, confirm entire flow works

### Application Bug

**Indicators:**
- Feature doesn't work as expected
- API returns error
- Data doesn't persist
- Element missing/broken

**Action:** Document in feature.bugs[], keep test as specification of expected behavior

## Critical Rule

**NEVER fix a test without first proving the corrected version works interactively!**

Run the COMPLETE corrected flow interactively before updating the test. If any step fails, the fix is wrong.
