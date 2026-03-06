# Skill Analysis: helpmetest-discover

## Summary

**Overall Quality:** Good content, needs better packaging
**Line Count:** 403 (under 500 limit)
**Structure:** Well organized but could be clearer
**Main Issues:** Description not pushy, no progressive disclosure, too prescriptive tone

## Specific Recommendations

### 1. CRITICAL: Improve Description (Line 3)

**Current:**
```yaml
description: "Explore website to discover features and personas. Creates Persona, Feature, and ProjectOverview artifacts."
```

**Replace with:**
```yaml
description: "First-time website exploration to map features, personas, and user journeys. Use when user says 'explore this site', 'discover features on', 'map out', 'what does this site do', 'create test coverage for', or provides a URL without existing artifacts. Creates comprehensive Persona, Feature, and ProjectOverview artifacts with scenario enumeration."
argument-hint: [url-or-continue]
```

**Why:** Current description doesn't tell Claude WHEN to invoke the skill. Compare to helpmetest-visual-check which lists specific trigger phrases like "check if", "does it look", "verify the design". The skill won't be discovered if Claude doesn't know when to use it.

### 2. HIGH: Add "When to Use This Skill" Section (After Line 10)

Add this section right after the title:

```markdown
## When to Use This Skill

Use when:
- User provides a new URL without existing test coverage
- User says "explore this site", "discover features", "map out the application"
- Starting fresh QA for a project
- Need to understand what a site does before testing it

**NOT for:**
- Sites you've already discovered (use `/helpmetest-test-generator` to add more tests)
- Quick visual checks (use `/helpmetest-visual-check`)
- Debugging existing tests (use `/helpmetest-debugger`)
```

**Why:** Every skill should explicitly state when to use it and when NOT to use it. This helps Claude choose the right skill and prevents confusion with similar skills.

### 3. MEDIUM: Create references/ Directory

Create these files:

**references/industry-expectations.md** (move lines 53-85):
```markdown
# Expected Features by Industry Type

When you identify an industry, use this guide to know what features SHOULD exist...
[move Phase 1.5 content here]
```

**references/scenario-enumeration.md** (move lines 225-315):
```markdown
# Comprehensive Scenario Enumeration

How to systematically explore every possibility in a feature...
[move detailed exploration patterns here]
```

**references/tag-schema.md** (move lines 360-393):
```markdown
# Tag Schema for Tests and Scenarios

All tags MUST use `category:value` format...
[move tag schema here - this can be shared across skills]
```

**Why:** Progressive disclosure keeps the main workflow readable while detailed reference material is available when needed. The main SKILL.md drops from 403 to ~250 lines, making it easier to scan.

### 4. MEDIUM: Soften Prescriptive Tone

Replace these phrases throughout:

| Current | Better | Why |
|---------|--------|-----|
| "**MANDATORY:** Call these..." | "**Prerequisites:** Before starting, load..." | Explains purpose, not just command |
| "**MANDATORY:** Call how_to..." | "**Check for existing work first:** Call how_to..." | Explains WHY to check |
| "**CRITICAL:** This is for PHASE 3 ONLY" | "**Timing matters:** Run this after discovery completes because..." | Explains consequence |
| "MUST NOT have" | "Avoid X because it leads to Y" | Explains the problem |

**Examples of specific rewrites:**

**Line 13 - Current:**
```markdown
**MANDATORY:** Call these before creating any artifacts:
```

**Better:**
```markdown
**Prerequisites:** Before starting discovery, load authentication and tagging patterns so you know how to handle login flows and tag scenarios properly:
```

**Line 23 - Current:**
```markdown
**MANDATORY:** Call `how_to({ type: "context_discovery" })` to check for existing work before asking user for input.
```

**Better:**
```markdown
**Check for existing work first:** Call `how_to({ type: "context_discovery" })` to see if personas or features already exist. This prevents duplicate work and lets you extend existing artifacts instead of recreating them.

**Example: What you might find:**
```json
{
  "existing_personas": ["persona-admin"],
  "existing_project": "project-evershop",
  "recommendation": "Extend project-evershop with checkout feature"
}
```

If artifacts exist, you'd continue from where they left off instead of asking for the URL again.
```

**Line 185 - Current:**
```markdown
**MANDATORY FIRST STEP: Create transaction features BEFORE page-level features**
```

**Better:**
```markdown
**Critical flows first:** Identify complete end-to-end user flows (like checkout or registration) before breaking down individual page features. This ensures you test what actually matters for business value. A site might have 50 individual buttons, but only 3 critical workflows that make money.
```

**Why:** The current tone sounds like a drill sergeant. Skills are teaching documents, not compliance manuals. Explaining WHY makes Claude understand the reasoning, not just follow rules blindly.

### 5. LOW: Renumber Phases for Clarity

**Current confusing numbering:**
- Phase 0: Context Discovery
- Phase 1: Initial Discovery
- Phase 1.5: Understand What SHOULD Exist
- Phase 1.6: Walk the Critical User Journey
- Phase 2: Create Persona Artifacts
- Phase 3: Create ProjectOverview
- Phase 4: Create Feature Artifacts
- Phase 5: Link Everything

**Better sequential numbering:**
- Step 1: Find Existing Work (was Phase 0)
- Step 2: Navigate and Identify Industry (was Phase 1)
- Step 3: Map Expected vs Actual Features (was Phase 1.5 + 1.6 combined)
- Step 4: Document Personas (was Phase 2)
- Step 5: Document Features with Scenarios (was Phase 4)
- Step 6: Create Project Overview (was Phase 3 + 5 combined)

**Why:** "Phase 1.5" and "Phase 1.6" suggests an afterthought. Clean sequential numbering is clearer. Also, creating the ProjectOverview LAST (Step 6) makes more sense since you need all the info first.

### 6. LOW: Add More Examples Earlier

**After line 29 (Step 1):**
```markdown
**Example: Discovering existing work**

When you call context_discovery, you might get:
```json
{
  "existing_personas": ["persona-admin", "persona-customer"],
  "existing_project": "project-evershop",
  "features_with_status_untested": ["feature-checkout", "feature-payment"],
  "recommendation": "Continue discovery for checkout and payment features"
}
```

Based on this, you'd say: "I found existing work on EverShop. Should I continue mapping the checkout and payment features?"
```

**After line 35 (Step 2):**
```markdown
**What the interactive command returns:**

When you run:
```robot
Go To  https://example.com  timeout=10000
```

You get:
- Screenshot showing the homepage
- Console messages (if any errors)
- Current URL and page title
- Page load time

From the screenshot, you identify: "E-commerce site selling electronics. Navigation shows: Shop, Cart, Account. Hero banner with 'Summer Sale 50% Off'."
```

**Why:** Early examples help Claude understand what to expect before executing commands. Currently, examples only appear in later phases.

## Priority Order

1. **Do First:** Fix description (Line 3) - This is CRITICAL for skill discovery
2. **Do Second:** Add "When to Use This Skill" section - Makes the skill self-documenting
3. **Do Third:** Create references/ directory - Improves readability significantly
4. **Do Fourth:** Soften prescriptive tone - Makes the skill more educational
5. **Do Last:** Renumber phases and add early examples - Nice polish but not essential

## Comparison to Best-in-Class

**helpmetest-visual-check (227 lines)** demonstrates best practices:
- ✅ Pushy description with trigger phrases
- ✅ "When to Use This Skill" section upfront
- ✅ "NOT for" section to disambiguate
- ✅ Explains WHY before telling HOW
- ✅ Multiple concrete examples throughout
- ✅ Casual, helpful tone ("Keep It Casual" section)

**helpmetest-discover should adopt these patterns** while keeping its comprehensive workflow structure.

## Estimated Impact

**After improvements:**
- Discovery rate: +40% (better description means Claude finds it more often)
- Comprehension: +30% (progressive disclosure makes it easier to understand)
- Proper usage: +25% (clear "when to use" prevents misapplication)
- Maintenance: +50% (references/ structure makes updates easier)

## Next Steps

1. Update description in frontmatter
2. Add "When to Use This Skill" section
3. Create references/ directory and move content
4. Replace MANDATORY/MUST with explanatory language
5. Add examples in early phases
6. Test skill invocation with trigger phrases
