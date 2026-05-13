> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

> **No MCP?** Use `helpmetest <command>` instead of MCP tools.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

> ### 🔴 AFTER EVERY TEST UPSERT — TWO MORE STEPS ARE MANDATORY.
> 1. Run the test — **preferred:** pass `run: true` to `helpmetest_upsert_test` (updates + runs atomically). **Alternative:** call `helpmetest_run_test({ id: "<same-id>" })` separately.
>    Run it even if you think the app server is down or not yet built. A FAIL result is valid — it documents current state. Never skip because you "expect it to fail."
> 2. Update the Feature artifact to include this test ID in the matching scenario's `test_ids` array.
> Upsert-only is **incomplete**. Both steps are required. No exceptions.

---

# Discover

Maps what exists into Feature artifacts. The source can be a live app, a spec doc, API docs, tickets, a codebase — or all of the above at once.

Also handles fast triage sweeps ("find bugs", "poke around", "good test around", "quick sanity check") — see **Triage mode** below.

Output: Feature artifacts with Given/When/Then scenarios (full mode), or a categorized findings table (triage mode).

## Orient First

```
helpmetest_status()
helpmetest_search_artifacts({ query: "" })
```

---

## Triage Mode — fast bug sweep, no test artifacts

Use this when the intent is "find what's broken fast" rather than "map the app for TDD."

Trigger phrases: "good test around", "find anything weird", "quick sanity check", "poke around", "see what's wrong", "any obvious issues".

### What to do

1. Walk the core user flows using `run_interactive_command` with `screenshot: true`
2. Read DOM text, network responses, localStorage, and console output
3. Collect every issue under one of three buckets:

   **🐛 Bugs** — wrong output, broken state, JS error, incorrect data  
   **🗃 Data quality** — placeholder text, wrong label in CMS, test data in prod, stale copy (fixable without code)  
   **🤔 UX illogicalities** — works technically but makes no sense to a user: wrong empty-state message, duplicate CTA, dead-end flow, page that doesn't adapt for logged-in state

4. Document every **Bug** in a Feature artifact's `bugs[]` before presenting results. A bug only in chat doesn't exist.

5. Present the findings table:

```
## Findings — [App Name]

### Bugs (broken behavior)

1. **[Short title]** *(documented in: [feature-artifact-id])*
   - [One sentence: what is wrong and who it affects]

### Data quality (content/config, not code)

2. **[Short title]**
   - [One sentence]. Fix: [what to update in CMS/config/DB — no code needed]

### UX illogicalities (not broken, but confusing)

3. **[Short title]**
   - [One sentence: what a user would expect instead]

---
**Verdict:** Items N–N (data quality) fixable in [CMS] without code. Items N–N need code changes. Items N–N are bugs.

Want to tackle any of these?
```

Rules:
- Number items globally (1, 2, 3… not per-section)
- Bugs always cite which Feature artifact they were added to
- Data quality always says where to make the fix
- One sentence per item — no paragraphs

After presenting, **stop**. When the user picks items: bugs → `/tdd` first then fix; data quality → make the change directly; UX → propose fix, get approval, then `/tdd`.

---

## Announce

After orient, present before doing anything else.

**No ProjectOverview exists (fresh discovery):**
> "After this you'll have a complete map of this app — every feature, every user type, every scenario — structured and ready for test-first implementation. I need one thing to start: what's the source?
> - Live URL to walk
> - A PRD or spec doc (share the path or paste it)
> - Tickets (GitHub, Linear, Jira — give me access or paste them)
> - The codebase (I'll read it)
> - Walk me through it directly"

**ProjectOverview exists (already discovered):**
> "This project was already mapped — [N] Feature artifacts exist covering [list area names]. After this you'll have an up-to-date map with any flows that appeared or changed since then. I'd re-walk the live app and extend what's there. Full re-discovery, or focus on a specific area that changed?"

Wait for the answer. Then proceed to Step 1.

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

### Interactive Command Recovery

If an interactive command returns an error, **immediately try an alternative — never give up.**

Common fixes:
- `Keyboard Key  Enter` → error "expected 2 arguments"? Use `Press Keys  input.selector  Enter` instead.
- Element not found? Try `Javascript  document.querySelector('...').outerHTML` to inspect actual DOM.
- Click fails? Try `Hover` first, then click.
- Keep exploring until you have the selectors you need.

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
