# Comprehensive Scenario Enumeration

**CRITICAL: Enumerate ALL scenarios interactively before writing ANY tests.**

## Happy Paths Discovery

Try EVERY way to successfully use the feature:

```robot
As  <auth_state>
Go To  <feature-url>

# Try action - observe outcome
<action steps>
# Document what worked and what the result was
```

For each successful path, create a functional scenario:

```json
{
  "name": "User can <accomplish goal>",
  "given": "User on <page> with <precondition>",
  "when": "User <performs action>",
  "then": "<Expected successful outcome>",
  "url": "<feature-url>",
  "auth": ["<auth_state>"],
  "priority": "critical|high|medium|low",
  "test_ids": []
}
```

## Error Scenarios Discovery

Try EVERY way the feature should fail gracefully:

### Empty Inputs

```robot
As  <auth_state>
Go To  <feature-url>

# Try submitting with empty required fields
Fill Text  <selector>  ${EMPTY}
Click  <submit-button>
# Document: What error? Input preserved? State corrupted?
```

### Invalid Formats

```robot
# Try invalid email format
Fill Text  input[type=email]  notanemail

# Try non-numeric in number field
Fill Text  input[type=number]  abc

# Document error handling
```

### Boundary Values

```robot
# Try too long
Fill Text  <selector>  ${'x' * 1000}

# Try too short (if min length exists)
Fill Text  <selector>  a

# Try negative numbers (if applicable)
Fill Text  <selector>  -1

# Document validation errors
```

### Duplicate Entries

```robot
# Try duplicate username/email/identifier
Fill Text  <selector>  <existing-value>
# Document conflict handling
```

### Permission Errors

```robot
# Try accessing without proper role
As  <lower-privilege-state>
Go To  <restricted-page>
# Document access denial
```

For each error case, create an edge_case scenario:

```json
{
  "name": "<Error scenario name>",
  "given": "User on <page> with <state>",
  "when": "User <performs invalid action>",
  "then": "Error shown: <expected message>, input preserved, state unchanged",
  "url": "<feature-url>",
  "auth": ["<auth_state>"],
  "priority": "high|medium|low",
  "test_ids": []
}
```

## Non-Functional Scenarios

For performance/security critical features:

```json
{
  "name": "Search responds within 2 seconds",
  "given": "User on search page",
  "when": "User searches for common term",
  "then": "Results displayed within 2000ms",
  "url": "<search-url>",
  "auth": ["<auth_state>"],
  "priority": "medium",
  "test_ids": []
}
```

## Completeness Checklist

For EACH Feature, ensure interactive exploration covered:
- ✅ ALL functional paths (every way users can successfully use it)
- ✅ ALL edge cases:
  - ✅ Empty inputs
  - ✅ Invalid formats
  - ✅ Boundary values
  - ✅ Duplicate entries
  - ✅ Permission denied
- ✅ Critical non-functional (performance, security if applicable)

**Each scenario = one future test. One Feature should have 10+ scenarios!**
