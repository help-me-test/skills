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

### Pre-flight — announce before you start

Before touching the browser, present your plan in this format and wait for a go/no-go:

```
## Triage plan — <site>

I will run 8 adversarial probe checks + walk these flows:
1. <primary flow — e.g. homepage → sign up → dashboard>
2. <secondary flow — e.g. logged-in: core feature>
3. <edge — e.g. empty state, error state>

Adversarial probe covers: 404 blank screen, SSL certs, console errors,
failed network requests, mobile layout, performance thresholds,
keyboard navigation, broken links, empty state, persistence after reload,
back/forward navigation, copy quality scan.

Expected time: ~N minutes. Ready to start?
```

The user may add flows, remove checks, or change the target URL. Update your plan accordingly before proceeding.

### What to do

1. Walk the core user flows using `run_interactive_command` with `screenshot: true`
2. **Run the Adversarial Probe on every page you visit** (see below)
3. Read DOM text, network responses, localStorage, and console output
4. Collect every issue under one of three buckets:

   **🐛 Bugs** — wrong output, broken state, JS error, incorrect data  
   **🗃 Data quality** — placeholder text, wrong label in CMS, test data in prod, stale copy (fixable without code)  
   **🤔 UX illogicalities** — works technically but makes no sense to a user: wrong empty-state message, duplicate CTA, dead-end flow, page that doesn't adapt for logged-in state

---

### Adversarial Probe — run this on every site, every triage

**Before running the probe, announce it:**
> "Running adversarial probe — 12 checks: 404 blank screen, SSL certs, console errors, failed network requests, mobile layout (iPhone 13), performance thresholds, keyboard navigation, broken links, empty state, persistence after reload, back/forward navigation, copy quality scan. Starting now."

Then run them in order. After all 8, report the full verdict in one block (see verdict format below) — do not drip-feed individual results.

These are fast deterministic checks. Each one catches a class of critical bug that normal flow-walking misses. Run all twelve. Checks 1–5 take < 8 interactive commands; checks 6–8 read existing session data or run a single keyword; checks 9–12 are single JS evals or one navigation step.

#### 1. 404 / blank screen

Navigate to a guaranteed non-existent route:

```robot
Go To  <base-url>/does-not-exist-xyz-404-probe
Take Screenshot
Javascript  document.body.offsetHeight
```

**Pass:** body has content — a custom 404 page, a redirect to home, or any visible UI.  
**Fail:** `offsetHeight === 0` or the screenshot shows a blank white screen → **React/SPA catch-all route is missing.** The app silently renders nothing for unknown URLs. Every typo, broken link, or expired URL gives users a white screen with no way back.  
Document as a Bug: "No 404 page — unknown routes render blank white screen."

#### 2. SSL cert check

Use the `DomainChecker` library. Extract every distinct hostname the app touches (main domain + any subdomain seen in redirects during auth, API calls, or CDN loads), then check each:

```robot
SSL Is Valid          <domain>  ==  True
Ssl Certificate Chain Valid  <domain>  ==  True
SSL Days Remaining    <domain>  >=  30
```

A clean cert on `app.example.com` says nothing about `auth.example.com` or `api.example.com` — check them all.

| Keyword | What it catches |
|---|---|
| `SSL Is Valid` | expired cert |
| `Ssl Certificate Chain Valid` | self-signed, untrusted CA, broken chain |
| `SSL Days Remaining >= 30` | cert expiring soon (user won't see it now, but will in days) |

**Fail on any:** document as a Bug with the domain and which check failed. An invalid or expiring cert is always P0 on auth/API subdomains — it blocks or will soon block all users.

#### 3. Console errors on page load

```robot
Javascript  JSON.stringify((window.__consoleErrors || []).slice(0, 5))
```

If `window.__consoleErrors` is not pre-populated, inject a collector first:

```robot
Javascript  window.__errs = []; const orig = console.error; console.error = (...a) => { window.__errs.push(a.join(' ')); orig(...a); }; 'patched'
# Then navigate and reload, then:
Javascript  JSON.stringify(window.__errs.slice(0, 5))
```

**Pass:** empty array.  
**Fail:** any entries → note them. Errors with `TypeError`, `ReferenceError`, or failed fetch URLs are bugs. Log noise (e.g. React DevTools hints) is not.

#### 4. Failed network requests

The `run_interactive_command` output already contains the full network request log for the page. **Read it — don't reinvent it with JS.**

After every `run_interactive_command` call, scan the `network` section of the output for requests where `status >= 400` or `status == 0` (cancelled/failed). This catches broken images, missing JS chunks, failed API calls, blocked fonts — anything, not just images.

```
# What to look for in the run_interactive_command network output:
# status 4xx → resource not found or forbidden (broken images, missing JS/CSS, bad API endpoints)
# status 5xx → server error on a resource load
# status 0   → request was cancelled or net::ERR_* (DNS failure, connection refused, CORS block)
```

**Pass:** all requests in the network log have status < 400.  
**Fail:** any 4xx/5xx/0 entries → list them by URL and status. Triage:
- Image URLs → broken image bug (user-visible)
- JS/CSS chunks → may break functionality silently
- API endpoints → data missing from the page
- Third-party → note but deprioritise (external service down)

Document as a Bug if the failing resource is user-facing or affects page functionality.

#### 5. Mobile layout

Walk the primary user flow on iPhone. Use:

```robot
Test On  iPhone 13  <base-url>
Take Screenshot
Javascript  document.documentElement.scrollWidth > document.documentElement.clientWidth
```

**Pass:** `False` — no horizontal overflow. Layout collapses correctly.  
**Fail:** `True` — content overflows the viewport horizontally. Users on mobile must scroll sideways, which is always a bug.

Also eyeball the screenshot for: nav hidden/unusable, text clipping, buttons too small to tap (< 44px), modals cut off. These are UX bugs — note them in the findings table even if overflow is clean.

After the probe, close the mobile context and switch back to desktop before continuing the rest of the triage.

#### 6. Performance thresholds

`run_interactive_command` sessions already capture Web Vitals — check `Analyze Web Vitals` output from the session. No extra commands needed.

Read the output and apply these thresholds:

| Metric | Good | Needs improvement | Bug |
|---|---|---|---|
| First Contentful Paint (FCP) | < 1800ms | < 3000ms | ≥ 3000ms |
| Load complete | < 3000ms | < 5000ms | ≥ 5000ms |
| DOM interactive | < 400ms | < 1000ms | ≥ 1000ms |

The 400ms DOM interactive threshold is the [Doherty Threshold](https://lawsofux.com/doherty-threshold/) — below it the app feels instant, above it users perceive lag.

**Pass:** all three metrics in the "Good" column.  
**Fail (Bug):** any metric in the "Bug" column → document as a Bug with the measured value. A 3s+ FCP on a marketing page loses conversions; a 1s+ DOM interactive on a dashboard is a UX defect.  
**Warn:** "Needs improvement" values are UX illogicalities — note in findings but don't block.

#### 7. Keyboard navigation

Tab through the primary interactive area and verify every element is reachable and shows a visible focus ring:

```robot
Javascript  document.activeElement?.tagName
Press Keys  body  TAB
Javascript  JSON.stringify({tag:document.activeElement?.tagName, text:document.activeElement?.textContent?.trim().slice(0,40), hasFocus:(()=>{const s=window.getComputedStyle(document.activeElement);return s.outlineStyle!=='none'||s.boxShadow!=='none';})()})
# Repeat Press Keys + eval 5-8 times to walk the main form/nav
```

**Pass:** every element is reachable in logical order and `hasFocus` is `true` (visible outline or box-shadow).  
**Fail:** any element where `hasFocus === false` → focus ring stripped. Document as a Bug: "Keyboard focus indicator missing on `<element>` — inaccessible to keyboard-only users."  
**Fail:** tab order skips or loops before reaching key actions → document as UX illogicality.

Stop after 8 tabs. If the page has a form, prioritize tabbing through all its inputs.

#### 8. Broken links

Crawl the site and find all dead links in one command:

```robot
Broken Links  <base-url>  maxPages=50
```

This keyword crawls all same-domain links up to `maxPages`, issues HEAD requests, and returns a map grouped by HTTP status code (`{404: [...], 500: [...], ...}`).

**Pass:** empty map — no dead links.  
**Fail:** any entries → document as a Bug listing affected URLs grouped by status code. 404s on navigation items or CTAs are P1 — they break user journeys silently.

Set `maxPages=50` for most sites. For large sites (> 200 pages) use `maxPages=20` to keep the probe fast. Broken Links only follows same-domain hrefs — external links are not checked.

#### 9. Empty state

Visit the app before any data exists (clear localStorage if needed, or use a fresh session) and screenshot the core content area:

```robot
Javascript  localStorage.clear()
Go To  <base-url>
Take Screenshot
Javascript  document.body.innerText.trim().length
```

**Pass:** the empty area has a message explaining what belongs there, plus a CTA or instruction to create the first item.  
**Fail:** blank area, just a background, or only a spinner with no content → document as a UX illogicality: "Empty state missing — first-time users see no guidance."  
**Fail:** `innerText.length === 0` or near-zero → the whole page is blank, not just the list area → escalate to Bug.

Also check: search results with a query that returns nothing, filtered views with no matching items, and dashboards with no activity yet. Each is a separate empty state.

#### 10. Persistence after reload

Create or update data, reload the page, verify the data is still there:

```robot
# After creating data:
Go To  <base-url>
Take Screenshot
Javascript  JSON.stringify(localStorage)
```

**Pass:** data survives a full page reload — either from localStorage, cookies, or the backend.  
**Fail:** data disappears on reload → the app stores state only in memory (React useState, in-memory variable). Document as a Bug: "Data not persisted — lost on page reload." This is a silent failure — the app looks functional but any reload wipes user work.

#### 11. Back/forward navigation

Navigate into a flow, then go back, and verify the app state is correct:

```robot
Go To  <base-url>
# Navigate forward (click into a detail, form, or sub-page)
Click  <link-or-cta>
Go Back
Take Screenshot
Javascript  document.body.offsetHeight
```

**Pass:** back navigation lands on the previous state with correct content rendered.  
**Fail:** blank screen, crash, redirect loop, or wrong page after `Go Back` → SPA history is broken. Document as a Bug: "Browser Back renders [blank/wrong state] — back navigation broken."  
**Fail:** `offsetHeight === 0` after going back → page is empty, same class of error as the 404 blank screen.

Also try `Go Forward` after going back — SPA routers frequently handle one direction but break the other.

#### 12. Copy quality scan

After every page load, scan the visible text for dev artifacts that leaked into production:

```robot
Javascript  (()=>{const t=document.body.innerText;const hits=[];['undefined','null','[object Object]','TODO','lorem ipsum','NaN','{{','}}'].forEach(p=>{if(t.toLowerCase().includes(p.toLowerCase()))hits.push(p);});return hits.length?JSON.stringify(hits):'clean';})()
```

**Pass:** `"clean"` — no dev artifacts in visible text.  
**Fail:** any match → document as Data quality with the matched term and the element containing it. These appear in prod more often than anyone expects: unrendered template variables (`{{name}}`), unformatted JS objects (`[object Object]`), unfilled placeholder copy (`lorem ipsum`), unhandled null values shown raw (`null`, `undefined`).

---

**Adversarial Probe verdict format** (add to the findings table alongside the three buckets):

```
### Infrastructure (adversarial probe)

A. **[Short title]** *(documented in: [feature-artifact-id])*
   - [One sentence: what is broken, what user impact is]
```

Infrastructure bugs go at the top of the findings table — they are always higher priority than UX illogicalities and often higher than individual feature bugs.

4. Document every **Bug** in a Feature artifact's `bugs[]` before presenting results. A bug only in chat doesn't exist.

5. Present the findings table:

```
## Findings — [App Name]

### Infrastructure (adversarial probe) — fix these first

A. **[Short title]** *(documented in: [feature-artifact-id])*
   - [One sentence: what is broken, what user impact is]

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
**Verdict:** Items A–A are infrastructure/P0 (fix before anything else). Items N–N (data quality) fixable in [CMS] without code. Items N–N need code changes. Items N–N are bugs.

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

**Run the Adversarial Probe immediately after your first page load** — before deeper exploration. This catches P0 infrastructure failures (SSL certs, blank 404s, console crashes) that would waste time if discovered later. See **Adversarial Probe** in the Triage Mode section above.

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
