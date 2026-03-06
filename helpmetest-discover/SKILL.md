---
name: helpmetest-discover
description: "Website exploration and feature discovery. Use when user says 'explore this site', 'discover features', 'map out app', 'what does this site do', or needs to understand site capabilities before testing. Creates comprehensive Persona, Feature, and ProjectOverview artifacts with scenario enumeration."
allowed-tools: mcp__helpmetest-*
---

# QA Roamer

Explores a website to understand what it does and who uses it.

## Prerequisites

**MANDATORY:** Call these before creating any artifacts:
```
how_to({ type: "authentication_state_management" })
how_to({ type: "tag_schema" })
```

## Workflow

### Phase 0: Context Discovery

**MANDATORY:** Call `how_to({ type: "context_discovery" })` to check for existing work before asking user for input.

- Reuse existing Persona artifacts (don't recreate auth)
- Extend existing ProjectOverview if found
- Only ask for URL if no artifacts exist

### Phase 1: Initial Discovery

1. **Navigate** to the URL with `helpmetest_run_interactive_command`:
   ```
   Go To  <url>  timeout=10000
   ```

2. **Read the page** - What does this site do?
   - Look at headline, navigation, content
   - Identify the business domain

3. **Check for authentication**:

   If the site has login/signup, set up authentication.

   Call `how_to({ type: "authentication_state_management" })` for complete setup process.

   **Summary:**
   - Check for existing Persona artifacts with credentials
   - If none exist, consult user about registration strategy
   - Create maintaining test based on strategy chosen
   - Validate authentication works before continuing
   - BLOCK discovery until auth is proven working

### Phase 1.5: Understand What SHOULD Exist

After identifying the industry, think about what a complete product in this domain needs:

**Ask yourself:**
1. **What is the PRIMARY user goal?** (buy something, get work done, learn something)
2. **What is the CORE TRANSACTION?** (purchase, subscription, booking, submission)
3. **What steps are needed to complete that transaction from start to finish?**
4. **What would a user EXPECT to find in a product like this?**

**Expected capabilities by industry type:**

**Transactional sites (e-commerce, booking, marketplace):**
- User needs: Discover → Evaluate → Decide → Transact → Confirm
- Expected features: Search, Browse, Details, Cart, Checkout, Payment, Confirmation, History

**SaaS/productivity tools:**
- User needs: Onboard → Use Core Feature → Manage Settings → Pay
- Expected features: Registration, Dashboard, Core Feature, Settings, Billing

**Content/media platforms:**
- User needs: Discover → Consume → Engage → Subscribe
- Expected features: Search, Browse, View, Comments, Share, Subscribe

**Social platforms:**
- User needs: Profile → Connect → Share → Engage
- Expected features: Profile, Feed, Post, Follow, Message, Notifications

**For each expected capability:**
1. Try to find it (check navigation, footer, user menu, follow CTAs)
2. If found: create Feature artifact
3. If NOT found: add to ProjectOverview expected_features with status: "missing"

### Phase 1.6: Walk the Critical User Journey

**Don't just discover pages - complete the PRIMARY user goal end-to-end.**

Think: "What does a user come here to DO, and what steps get them there?"

**Process:**
1. Identify the **primary goal** (e.g., "buy a product", "sign up for service")
2. Start as a new user and try to **complete that goal**
3. Document each step as a `JourneyStep`:
   - What action did you take?
   - Did it work? (status: found/missing/blocked)
   - What feature does this represent?
4. When you get BLOCKED, that's a missing feature

**Journey Schema:**
```json
{
  "name": "<Primary Goal> Flow",
  "persona_id": "persona-<who>",
  "steps": [
    { "action": "<What user does>", "feature_id": "feature-<x>", "status": "found|missing|blocked" }
  ],
  "completion": "complete|partial|blocked",
  "critical": true
}
```

**Critical journeys must be complete for product to work:**
- If journey is "partial" or "blocked" → major coverage gap
- Missing steps = missing features to flag in report

### Phase 2: Create Persona Artifacts

For each user type discovered, create a Persona artifact:

```json
{
  "type": "Persona",
  "id": "persona-<name>",
  "name": "Persona: <Name>",
  "content": {
    "persona_type": "primary|secondary|admin",
    "description": "Who they are",
    "goals": ["What they want"],
    "pain_points": ["Frustrations"],
    "username": "<generated-by-Create-Fake-Email>",
    "password": "SecureTest123!",
    "auth_state": "AdminState",
    "permissions": ["what they can do"],
    "environment": "staging"
  }
}
```

### Phase 3: Create ProjectOverview

Use `helpmetest_upsert_artifact`:

```json
{
  "type": "ProjectOverview",
  "id": "project-<domain>",
  "name": "ProjectOverview: <Site Name>",
  "content": {
    "url": "<url>",
    "summary": "What this site does and who it's for",
    "industry": "e-commerce|saas|healthcare|etc",
    "persona_ids": ["persona-admin", "persona-user"],
    "features": [
      { "feature_id": "feature-search", "name": "Search", "status": "working" },
      { "feature_id": "feature-cart", "name": "Cart", "status": "partial" },
      { "name": "Checkout", "status": "missing", "priority": "critical", "reason": "Cannot complete purchases" },
      { "name": "Payment", "status": "missing", "priority": "critical", "reason": "No payment integration found" }
    ],
    "user_journeys": [
      {
        "name": "Purchase Flow",
        "persona": "customer",
        "steps": [
          { "action": "Search for product", "feature_id": "feature-search", "status": "found" },
          { "action": "View product details", "feature_id": "feature-product-details", "status": "found" },
          { "action": "Add to cart", "feature_id": "feature-cart", "status": "found" },
          { "action": "Checkout", "status": "missing" },
          { "action": "Payment", "status": "missing" },
          { "action": "Confirmation", "status": "missing" }
        ],
        "completion": "partial"
      }
    ],
    "tech_stack": [],
    "auth_methods": [],
    "notes": []
  }
}
```

### Phase 4: Create Feature Artifacts with Scenario Enumeration

**MANDATORY FIRST STEP: Create transaction features BEFORE page-level features**

Before breaking down pages into individual features, identify and create features for complete end-to-end user flows:

Ask: "What multi-step processes exist that users need to complete from start to finish?"

Examples:
- Multi-page forms (registration, checkout, booking) → Create ONE feature for "complete registration/purchase/booking"
- Wizards or workflows → Create ONE feature for the entire workflow
- Any process spanning multiple pages → Create ONE feature for the complete flow, mark as priority:critical

Then enumerate page-level features (individual buttons, filters, searches, etc.)

**CRITICAL: This is a two-step process:**
1. **Create Feature artifact with basic info**
2. **Explore feature interactively to enumerate ALL test scenarios**

For each capability:

**Step 4.1: Create Feature artifact skeleton**

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

**Step 4.2: Explore feature to enumerate ALL scenarios**

Use `helpmetest_run_interactive_command` to systematically explore every possibility:

**A. Discover ALL functional scenarios (happy paths):**

For each way users can successfully use this feature:
```robot
As  <auth_state>
Go To  <feature-url>
# Try action - observe outcome
<action steps>
# Document what worked and what the result was
```

Create scenario for each discovered path:
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

**B. Discover ALL edge case scenarios (error handling):**

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

Create scenario for EACH discovered error case:
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

**C. Non-functional scenarios (if feature is performance/security critical):**

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

**Step 4.3: Update Feature artifact with ALL discovered scenarios**

```json
{
  "functional": [<all happy path scenarios>],
  "edge_cases": [<all error handling scenarios>],
  "non_functional": [<performance/security scenarios if applicable>]
}
```

**Each feature should have 10+ scenarios (5+ functional, 5+ edge cases minimum).**

### Phase 5: Link Everything

1. Add features to ProjectOverview.features with status:
   ```json
   { "feature_id": "feature-checkout", "name": "Checkout", "status": "working" }
   { "name": "Payment", "status": "missing", "priority": "critical", "reason": "No Stripe integration" }
   ```
2. For missing features: set status="missing", add priority and reason (no feature_id yet)

## Output

- Persona artifacts for each user type
- ProjectOverview artifact with persona_ids, capabilities
- Feature artifacts for each capability
- Summary of what was discovered

## Tag Schema (REQUIRED)

**Format:** ALL tags MUST use `category:value` format.

### Required Scenario Tags
- `priority:X` - REQUIRED. Values: `critical`, `high`, `medium`, `low`

### Recommended Scenario Tags
- `feature:X` - Feature area (e.g., `feature:authentication`, `feature:checkout`)
- `scenario:X` - Values: `happy-path`, `error-handling`, `edge-case`
- `workflow:X` - User journey (e.g., `workflow:purchase-flow`, `workflow:onboarding`)
- `role:X` - Required role (e.g., `role:admin`, `role:user`, `role:guest`)
- `project:X` - Links to ProjectOverview (e.g., `project:project-evershop`)
- `severity:X` - For bugs. Values: `blocker`, `critical`, `major`, `minor`, `trivial`

### Invalid Tags (DO NOT USE)
❌ Flat tags: `critical`, `authentication`, `happy-path`
❌ Wrong separators: `feature_auth`, `scenario-happy-path`
❌ Made-up categories: `type:feature`, `category:auth`, `site:example`

### Valid Examples
Scenario tags:
```json
{
  "tags": ["priority:critical", "feature:authentication", "scenario:happy-path", "role:user", "project:project-evershop"]
}
```

Bug tags:
```json
{
  "tags": ["priority:high", "severity:major", "feature:checkout", "scenario:error-handling"]
}
```

## Critical Rules

1. **Create Persona artifacts** - Don't embed personas in ProjectOverview
2. **Use persona_ids** - Reference personas by ID, not embedded
3. **Given/When/Then** - All scenarios use this format
4. **Explore authenticated AND unauthenticated** - Some features need login
5. **Tag scenarios properly** - All scenarios need priority: tag minimum

**Version:** 0.1
