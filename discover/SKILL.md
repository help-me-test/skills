---
name: discover
description: "Map what exists into Feature artifacts — whether the source is a live app, a PRD, API specs, tickets, or a codebase. Use when: you have a running app but no artifacts ('what does this site do?'), you have specs/docs but no running app ('read the PRD', 'extract features from spec', 'here are the tickets'), or both. Output is always the same: Feature artifacts ready for /tdd. Triggers on: URL with no specific test in mind, 'explore before we test', 'read the PRD', 'extract features from spec', 'here are the requirements', 'I have a spec', 'what features does this have', 'create artifacts from'."
allowed-tools: mcp__helpmetest-*
---

> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

> **No MCP?** Use `helpmetest <command>` instead of MCP tools.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

---

# Discover

Maps what exists into Feature artifacts. The source can be a live app, a spec doc, API docs, tickets, a codebase — or all of the above at once.

Output is always the same: Feature artifacts with Given/When/Then scenarios, ready for `/tdd`.

## Orient First

```
helpmetest_status()
helpmetest_search_artifacts({ query: "" })
```

If a ProjectOverview already exists → artifacts have been created before. Check what's covered, extend rather than recreate.

---

## Step 1 — Identify the Source

You have two input types. Handle both if both exist.

**Docs (PRD / spec / tickets / API spec / Figma notes / codebase):**
Read the source completely before asking anything. Then extract features (Step 2A).

**Live app (running URL):**
Navigate and explore. Then create Persona + ProjectOverview + Features (Step 2B).

If the user hasn't said which, ask once:
> "What's the source? A live URL, a spec/PRD, tickets, or all of the above?"

---

## Step 2A — Extract from Docs

For each distinct capability in the source:

1. Name it in user-facing language ("User Authentication", not "auth module")
2. Map four coverage types:

| Type | Question |
|------|----------|
| Functional (happy path) | What does success look like? |
| Validation | What inputs get rejected and why? |
| State / persistence | Does the result survive a reload? |
| Error / failure | What happens when backend or network fails? |

3. Note every ambiguity. Ask at most 5 clarifying questions before creating artifacts:

```
I found some ambiguities before creating artifacts:

Must resolve (affects test design):
1. [question about unclear behavior]

I'll assume if you don't answer:
2. [assumption — tell me if wrong]
```

Wait for answers, then proceed to Step 3.

---

## Step 2B — Explore Live App

### Auth First

```
how_to({ type: "authentication_state_management" })
```

Check for existing Persona artifacts. If none:
- Navigate to the app, find the login/signup flow
- Create auth-setup test with `Save As <StateName>`
- Validate it passes before continuing
- **Block discovery until auth works**

### Navigate and Walk the Primary Flow

```robot
As  <StateName>
Go To  <base-url>
```

Look at navigation, identify pages and sections.

Then: **complete the primary user goal end-to-end as a new user** — don't just screenshot pages, actually try to do the thing the app exists for (buy, sign up, create, book). When you get blocked, that's a missing feature.

### Understand What Should Exist

After identifying the industry, think about what a complete product needs:

**Transactional (e-commerce, booking, marketplace):**
Discover → Evaluate → Transact → Confirm → History

**SaaS / productivity:**
Register → Dashboard → Core Feature → Settings → Billing

**Content / media:**
Browse → View → Engage → Subscribe

For each expected capability: find it → create Feature artifact. If missing → mark as "missing" in ProjectOverview.

### Create Persona Artifacts

```json
{
  "type": "Persona",
  "id": "persona-<name>",
  "name": "Persona: <Name>",
  "content": {
    "persona_type": "primary|secondary|admin",
    "description": "Who they are",
    "goals": ["What they want"],
    "username": "<from Create Fake Email>",
    "password": "SecureTest123!",
    "auth_state": "<StateName>",
    "permissions": ["what they can do"]
  }
}
```

### Create ProjectOverview

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
      { "name": "Checkout", "status": "missing", "priority": "critical", "reason": "Cannot complete purchases" }
    ]
  }
}
```

---

## Step 3 — Create Feature Artifacts

For each capability (whether found in docs or in the live app):

```json
{
  "id": "feature-<kebab-name>",
  "type": "Feature",
  "name": "<Feature Name>",
  "content": {
    "goal": "<what business outcome this serves — one sentence>",
    "source": "prd|api-spec|tickets|live-app|codebase|user",
    "functional": [
      {
        "name": "User can <accomplish goal>",
        "given": "<starting state>",
        "when": "<what the user does>",
        "then": "<expected outcome>",
        "tags": ["priority:critical"],
        "test_ids": []
      }
    ],
    "edge_cases": [
      {
        "name": "<error or edge scenario>",
        "given": "...", "when": "...", "then": "Error shown: <message>, state unchanged",
        "tags": ["priority:high"],
        "test_ids": []
      }
    ],
    "gaps": ["<unclear or missing — needs user input>"],
    "bugs": []
  }
}
```

**Minimum per feature: 5 functional scenarios + 5 edge cases.**

For every feature, cover all four types: happy path, validation (bad inputs), persistence (reload), error (backend failure).

---

## Step 4 — Approval Gate

```
I've created [N] Feature artifacts from [source]:

Feature: <Name> (feature-<id>)
  Critical: <scenario names>
  High: <scenario names>
  Gaps: <anything unclear>

Coverage gaps:
- [anything the source didn't cover that a real app would need]

Does this match what you expect? Anything wrong, missing, or out of scope?
```

Wait for approval. Update artifacts based on feedback.

---

## Step 5 — Hand off to /tdd

```
Feature artifacts ready.

→ /tdd — write tests for feature-<highest-priority-id> first
```

**Version:** 0.1
