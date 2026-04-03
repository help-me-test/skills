---
name: test-strategy
description: "Use when the user wants to know what to test, how much to test, or whether their test coverage is complete. Triggers on: 'what tests do I need?', 'am I missing any tests?', 'what scenarios should I cover?', 'how do I know I have enough tests?', 'what edge cases should I test?', 'what's the right test mix?', 'we need a testing plan'. Also triggers when looking at a Feature artifact and asking whether coverage is sufficient. The output is a prioritized list of scenarios with coverage tier (critical path / edge case / error path / boundary) — not the tests themselves. Use /tdd to write the tests once strategy is clear. Do NOT use for: writing actual tests, debugging failing tests, or reviewing test quality."
allowed-tools: mcp__helpmetest-*
---

> **Who you are:** If `.helpmetest/SOUL.md` exists in this project, read it — it defines your character.

> **No MCP?** Use `helpmetest <command>` instead of MCP tools.

# Test Strategist

Given a feature, flow, or product area — produces a prioritized scenario map covering what must be tested, what should be tested, and what can be skipped.

## Orient First

```
helpmetest_status()
helpmetest_search_artifacts({ query: "" })
```

Check if Feature artifacts already exist. If they do, read them — scenarios may already be enumerated. Your job is to find what's *missing*, not re-enumerate what's there.

---

## The Coverage Framework

Every testable system has four scenario types. Work through all four for the feature at hand:

### 1. Critical Path (must test — always)
The core reason the feature exists. If this breaks, users can't do the one thing the feature was built for.

- One flow, end-to-end
- Realistic data (not `test@test.com`, not empty strings)
- Success case only — the "golden path"

**Ask:** "What does a real user do when everything works?"

### 2. Error Paths (must test — always)
What the system does when input is wrong, the API fails, or state is invalid.

- Invalid inputs (wrong format, empty when required, too long)
- Server errors (API returns 500, timeout, network failure)
- Auth errors (expired session, wrong permissions)
- Not-found states (deleted resource, wrong ID)

**Ask:** "What are the 3 most likely ways this breaks in production?"

### 3. Boundary Conditions (should test — especially for data/logic features)
The exact edges where behavior changes.

- Minimum valid value AND just below minimum
- Maximum valid value AND just above maximum
- Empty list vs one item vs many items
- Zero vs one vs many (the "ZOM" rule)
- First time vs repeat use

**Ask:** "Where does the behavior change based on a threshold?"

### 4. Edge Cases (test selectively — based on risk)
Unusual but possible states. Don't test all of them — test the ones that have caused bugs before or where failure would be severe.

- Concurrent operations (two users editing same resource)
- Race conditions (slow network, quick double-click)
- Data migrations (old data in new format)
- Permission combinations (admin + read-only flag)

**Ask:** "What would a QA engineer test that a developer wouldn't think of?"

---

## Coverage Tiers

Not all scenarios are equal. Assign each scenario a tier:

| Tier | Meaning | Robot Framework tag |
|------|---------|---------------------|
| **critical** | Core flow — broken = product unusable | `priority:critical` |
| **high** | Error handling — broken = users get bad experience | `priority:high` |
| **medium** | Edge cases — broken = some users affected | `priority:medium` |
| **low** | Boundary details — broken = minor issue | `priority:low` |

---

## Scenario Enumeration Process

### Step 1: Read the Feature

If a Feature artifact exists:
```
helpmetest_get_artifact({ id: "feature-[name]" })
```

If not, ask the user to describe:
- What the feature does (the goal)
- Who uses it (the persona)
- What happens when it succeeds
- What the main failure modes are

### Step 2: Map the Four Types

For each feature, enumerate scenarios across all four types. Use this template:

```
Feature: [Feature Name]

CRITICAL PATH
─────────────
[ ] [Persona] can [core action] — happy path, realistic data
[ ] [Core action] persists after page reload (if applicable)

ERROR PATHS
───────────
[ ] [Persona] sees clear error when [most likely invalid input]
[ ] [Persona] sees error when [second most likely failure]
[ ] [Persona] sees error when not authenticated (if auth required)
[ ] [Persona] sees error when API is unavailable (if testable)

BOUNDARY CONDITIONS
───────────────────
[ ] [Feature works at minimum valid value]
[ ] [Feature fails gracefully at minimum - 1]
[ ] [Feature works with empty state (zero items)]
[ ] [Feature works with maximum realistic data]

EDGE CASES (select based on risk)
──────────────────────────────────
[ ] [Most likely race condition or concurrent action]
[ ] [Most likely permission edge case]
```

### Step 3: Classify and Prioritize

Mark each scenario:
- **Write immediately** — critical + high priority, or known bug risk
- **Write before launch** — medium priority, normal feature coverage
- **Write if time allows** — low priority, edge cases with low failure risk
- **Skip** — purely cosmetic, already covered by other scenarios, or impossible to reproduce reliably

### Step 4: Check Against Feature Artifact

Compare enumerated scenarios against the Feature artifact's `functional` array:
- Scenarios already in Feature + have `test_ids` → covered, skip
- Scenarios in Feature but no `test_ids` → not tested, add to plan
- Scenarios not in Feature at all → add to Feature.functional, then to plan

Update Feature artifact with any new scenarios before handing off to `/tdd`.

---

## Output Format

Produce a scenario map the user can act on immediately:

```
## Test Strategy: [Feature Name]

### Write Immediately (Critical)
1. [Scenario name] — [one line: what it proves]
2. [Scenario name] — [one line: what it proves]

### Write Before Launch (High)
3. [Scenario name] — [one line: what it proves]
4. [Scenario name] — [one line: what it proves]

### Write If Time Allows (Medium/Low)
5. [Scenario name] — [one line: what it proves]

### Skip (with reason)
- [Scenario] — already covered by #1 / cosmetic only / not automatable reliably

### Coverage Assessment
- Critical path: covered ✅ / missing ❌
- Error paths: N of M covered
- Boundaries: covered ✅ / not applicable ✅ / missing ❌
- Auth scenarios: covered ✅ / missing ❌

### Recommended next step
/tdd → write tests for items 1–[N]
```

---

## Common Traps

**Testing implementation, not behavior**
— Wrong: "modal opens when button is clicked"
— Right: "user can complete the action that the modal enables"

**Only testing the happy path**
— Users hit errors constantly. If you only test success, you're testing 20% of what matters.

**Treating all edge cases as equal**
— Some edge cases are theoretical. Test the ones that have actually caused bugs or customer complaints first.

**Writing one test per feature**
— One test proves one thing. A feature with no error path tests has no error path coverage.

**Testing the same flow twice with minor variation**
— If two scenarios would fail for identical reasons, they're the same test. Merge them.

---

## Integration with Other Skills

- Use `/tdd` after this skill to write the actual tests
- Use `/validate-tests` to check quality of written tests
- Use `/discover` first if you don't know what the feature does

**Version:** 0.1
