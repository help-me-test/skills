# Phase 2: Comprehensive Feature Enumeration & Scenario Discovery

**GOAL: Create Feature artifacts with ALL test scenarios enumerated through interactive exploration.**

**CRITICAL: This is enumeration phase - DO NOT generate tests yet!**

## MANDATORY FIRST STEP: Think About Complete User Journeys

Before breaking down pages into features, identify what complete end-to-end flows exist.

Ask: **"What does a user come here to DO from start to finish?"**

When you find a multi-step process (forms with submit, wizards, transaction flows), create a Feature for the COMPLETE flow with priority:critical, not separate features for each step.

### Common Mistake

- You see pages for step 1, step 2, step 3 of a process
- You create features: "View step 1", "Fill step 2", "Submit step 3"
- You never created: "Complete the full process from start to confirmation"

### Correct Approach

- Recognize the pages form a complete transaction
- Create ONE Feature: "User completes [the goal]" with priority:critical
- Explore the ENTIRE flow interactively
- Then create supporting features for individual steps if needed

## Process for Each Page

After identifying core transaction features, enumerate page-level capabilities:

1. Look at what users can DO on this page
2. Skip capabilities already covered by transaction features
3. For each new capability found:

### a. Create Feature Artifact Skeleton

```json
{
  "type": "Feature",
  "id": "feature-<name>",
  "name": "Feature: <Name>",
  "content": {
    "goal": "What business outcome",
    "non_goals": ["What this is NOT"],
    "status": "untested",
    "persona_ids": ["persona-user"],
    "functional": [],
    "non_functional": [],
    "edge_cases": [],
    "bugs": [],
    "notes": []
  }
}
```

### b. Explore Feature to Discover ALL Scenarios

Use `helpmetest_run_interactive_command` to systematically try everything:

#### Happy Paths Discovery

- Try EVERY way to successfully use this feature
- For each successful path: run it interactively, observe outcome, create functional scenario

#### Error Scenarios Discovery

Try EVERY way the feature should fail gracefully:

**Empty inputs:**
```robot
As  <auth_state>
Go To  <feature-url>
# Try submitting with empty required fields
Fill Text  <selector>  ${EMPTY}
Click  <submit-button>
# Document: What error? Input preserved? State corrupted?
```

**Invalid formats:**
```robot
# Try invalid email format
Fill Text  input[type=email]  notanemail
# Try non-numeric in number field
Fill Text  input[type=number]  abc
# Document error handling
```

**Boundary values:**
```robot
# Try too long
Fill Text  <selector>  ${'x' * 1000}
# Try too short (if min length exists)
Fill Text  <selector>  a
# Try negative numbers (if applicable)
Fill Text  <selector>  -1
# Document validation errors
```

**Duplicate entries:**
```robot
# Try duplicate username/email/identifier
Fill Text  <selector>  <existing-value>
# Document conflict handling
```

**Permission errors:**
```robot
# Try accessing without proper role
As  <lower-privilege-state>
Go To  <restricted-page>
# Document access denial
```

For each error case discovered, create an edge_case scenario.

#### Non-functional Discovery (if critical)

- Performance-sensitive features (search, load)
- Security-critical features (auth, payment, permissions)

### c. Update Feature Artifact with ALL Discovered Scenarios

Add scenarios to functional, edge_cases, and non_functional arrays. Each scenario has empty test_ids array.

## Report Progress

After each feature:
- Feature name
- How many scenarios discovered (functional, edge_cases, non_functional)
- Features enumerated so far (X of Y total)
- Total scenarios discovered across all features

## Feature Completeness Checklist

For EACH Feature, ensure interactive exploration covered:
- ✅ ALL functional paths (every way users can successfully use it)
- ✅ ALL edge cases:
  - ✅ Empty inputs
  - ✅ Invalid formats
  - ✅ Boundary values
  - ✅ Duplicate entries
  - ✅ Permission denied
- ✅ Critical non-functional (performance, security if applicable)

## Example

Profile Update Feature (After Interactive Exploration):

```json
{
  "functional": [
    { "name": "User can update first name", "given": "User on profile page", "when": "Change first name and click save", "then": "Name updated, success message shown, change persists after reload", "priority": "high", "test_ids": [] },
    { "name": "User can update email", "given": "User on profile page", "when": "Change email and click save", "then": "Email updated, verification sent, change persists", "priority": "high", "test_ids": [] },
    { "name": "User can upload avatar", "given": "User on profile page", "when": "Upload image file and click save", "then": "Avatar updated, displayed on profile, persists after reload", "priority": "medium", "test_ids": [] }
  ],
  "edge_cases": [
    { "name": "Empty name rejected", "given": "User on profile page", "when": "Clear first name field and click save", "then": "Error: 'Name required', name not cleared, page state unchanged", "priority": "high", "test_ids": [] },
    { "name": "Invalid email format rejected", "given": "User on profile page", "when": "Enter 'notanemail' and click save", "then": "Error: 'Invalid email format', email unchanged, input preserved", "priority": "high", "test_ids": [] },
    { "name": "Duplicate email rejected", "given": "User on profile page", "when": "Enter email of existing user and click save", "then": "Error: 'Email already in use', email unchanged", "priority": "high", "test_ids": [] },
    { "name": "Avatar file too large rejected", "given": "User on profile page", "when": "Upload 10MB image file", "then": "Error: 'File too large (max 2MB)', avatar unchanged", "priority": "medium", "test_ids": [] },
    { "name": "Invalid avatar format rejected", "given": "User on profile page", "when": "Upload .txt file as avatar", "then": "Error: 'Invalid format (jpg/png only)', avatar unchanged", "priority": "medium", "test_ids": [] }
  ]
}
```

**Each scenario = one future test. One Feature should have 10+ scenarios!**

## Validation Before Exiting Phase 2

Review all Feature artifacts you created. Check:

1. **Do you have at least ONE feature with priority:critical that represents a complete end-to-end user flow?**
   - If site has transactions/forms/wizards → you should have a "complete [transaction]" feature
   - If you only have features like "view form", "fill field", "click button" → you missed the main flow

2. **Did you break down a multi-step process into separate features without creating the complete flow feature?**
   - Warning sign: Multiple features for same process area but no end-to-end feature
   - Fix: Create a critical feature for the complete flow

If you cannot identify any core transaction features, the discovery was incomplete.

## Exit Criteria

- ✅ Core transaction features identified (if site has transactions)
- ✅ ALL pages have been analyzed for capabilities
- ✅ ALL features have been created as artifacts
- ✅ ALL features have been explored interactively
- ✅ ALL scenarios (functional + edge cases + non-functional) have been enumerated
- ✅ NO tests have been generated yet (that's Phase 3)
