<!-- llms-description: Map a live app, PRD, API spec, tickets or codebase into Feature artifacts. Also fast bug-triage sweeps. -->

> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

> ### 🔴 AFTER EVERY TEST CREATE/UPDATE — TWO MORE STEPS ARE MANDATORY.
> 1. Run the test — call `helpmetest test run <test-id>` after creating or updating.
>    Run it even if you think the app server is down or not yet built. A FAIL result is valid — it documents current state. Never skip because you "expect it to fail."
> 2. Update the Feature artifact to include this test ID in the matching scenario's `test_ids` array.
> Create-only is **incomplete**. Both steps are required. No exceptions.

---

# Discover

Maps what exists into Feature artifacts. The source can be a live app, a spec doc, API docs, tickets, a codebase — or all of the above at once.

Also handles fast triage sweeps ("find bugs", "poke around", "good test around", "quick sanity check") — see **Triage mode** below.

## Workflow

1. **Orient** (below) — `helpmetest status`, `helpmetest artifact list`, check for a spec-driven-dev framework before asking the user for a source.
2. **Decide Triage vs Full Discovery**: "find what's broken fast" → **Triage Mode** (below); "map the app/spec into Feature artifacts" → **Full Discovery Mode** (`## Announce` → `Step 1` through `Step 5`, further down this file).
3. **Execute the chosen mode** end to end — Triage produces a findings table; Full Discovery produces Feature artifacts and hands off to `/tdd` (Step 5 is mandatory, not optional).
4. **Close out** per `modes/agent.md` Postflight.


**Reference files — load on demand:**
- `references/adversarial-patterns.md` — attack patterns for probe checks (forms, modals, keyboard, persistence, copy scan)
- `references/rf-recipes.md` — deterministic checks: axe-core, console errors, broken images, performance, web vitals, broken links, SSL
- `references/ux-heuristics.md` — heuristics for evaluating screenshots and reporting findings

Output: Feature artifacts with Given/When/Then scenarios (full mode), or a categorized findings table (triage mode).

## Orient First

```bash
helpmetest status
helpmetest artifact list --tags "project:<slug>"   # scoped — a bare list returns every project in the workspace
```

**Also check for a spec-driven-dev framework before asking the user for a source.** These
tools generate their own machine-readable spec/plan/task files — if present, that's the
source, full stop, don't ask "what's the source" first. Look for any of:

```bash
# spec-kit (github/spec-kit): /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
ls specs/*/spec.md specs/*/tasks.md .specify/ 2>/dev/null

# OpenSpec: /openspec-propose → /openspec-apply-change → /openspec-archive-change
ls openspec/changes/*/proposal.md openspec/specs/ 2>/dev/null

# Generic PRD/task-list pairs (create-prd + create-tasks skills)
ls PRD*.md prd.md docs/PRD*.md tasks/*/tasks-prd-*.md 2>/dev/null
```

Any hit → this is a **Framework-sourced discovery**, not a blind doc/PRD read. Skip straight
to Step 1's framework branch below; do not present the "what's the source" menu.

---

## Triage Mode — fast bug sweep, no test artifacts

Use this when the intent is "find what's broken fast" rather than "map the app for TDD."

Trigger phrases: "good test around", "find anything weird", "quick sanity check", "poke around", "see what's wrong", "any obvious issues".

### Pre-flight — announce before you start

Before touching the browser, present your plan in this format **then immediately start** — your first `helpmetest interactive` call happens in the same response turn:

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

Starting now.
```

Do not wait for a go/no-go. Proceed to "What to do" immediately.

### What to do

1. Walk the core user flows using `helpmetest interactive "<keyword>"` with screenshot flag
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
Javascript  document.body.offsetHeight
```
Request a screenshot via `helpmetest interactive` with screenshot flag to visually confirm the page state.

**Pass:** body has content — a custom 404 page, a redirect to home, or any visible UI.  
**Fail:** `offsetHeight === 0` or the screenshot shows a blank white screen → **React/SPA catch-all route is missing.** The app silently renders nothing for unknown URLs. Every typo, broken link, or expired URL gives users a white screen with no way back.  
Document as a Bug: "No 404 page — unknown routes render blank white screen."

#### 2. SSL / TLS / security headers check

Use the `DomainChecker` library. Extract every distinct hostname the app touches (main domain + any subdomain seen in redirects during auth, API calls, or CDN loads), then run the full suite on each:

```robot
# --- Certificate health ---
SSL Is Valid                      <domain>    ==    True
SSL Certificate Chain Valid       <domain>    ==    True
SSL Days Remaining                <domain>    >=    30
SSL Certificate Key Strength      <domain>    >=    2048
SSL Certificate Transparency Logged  <domain>  ==  True

# --- Protocol hygiene ---
TLS Version                       <domain>    matches    TLSv1\\.[23]
SSL 3 Supported                   <domain>    ==    False
TLS Compression Enabled           <domain>    ==    False

# --- Security headers ---
HTTP HSTS Enabled                 <domain>    ==    True
HTTP HSTS Max Age                 <domain>    >=    31536000
HTTP X Frame Options              <domain>    !=    ${EMPTY}
HTTP X Content Type Options       <domain>    ==    nosniff
```

A clean cert on `app.example.com` says nothing about `auth.example.com` or `api.example.com` — check them all.

| Keyword | What it catches | Severity |
|---|---|---|
| `SSL Is Valid` | expired cert | P0 — blocks all users |
| `SSL Certificate Chain Valid` | self-signed, untrusted CA, broken chain | P0 |
| `SSL Days Remaining >= 30` | cert expiring soon | P1 — will block users in days |
| `SSL Certificate Key Strength >= 2048` | weak RSA key (< 2048 bits) | P1 |
| `SSL Certificate Transparency Logged` | cert not in public CT log (suspicious issuance) | P1 |
| `TLS Version matches TLSv1.[23]` | TLS 1.0/1.1 active — deprecated, browser warnings | P1 |
| `SSL 3 Supported == False` | POODLE attack vector | P1 |
| `TLS Compression Enabled == False` | CRIME attack vector | P1 |
| `HTTP HSTS Enabled` | missing HSTS — HTTP downgrade possible | P2 |
| `HTTP HSTS Max Age >= 31536000` | HSTS max-age too short (< 1 year) | P2 |
| `HTTP X Frame Options` | missing clickjacking protection | P2 |
| `HTTP X Content Type Options == nosniff` | MIME-sniffing vulnerability | P2 |

**Fail on P0:** document as a Bug immediately — it blocks or will soon block all users.
**Fail on P1/P2:** document as a Bug with severity. Security headers are table stakes for any production app.

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

The `helpmetest interactive` output already contains the full network request log for the page. **Read it — don't reinvent it with JS.**

After every `helpmetest interactive` call, scan the `network` section of the output for requests where `status >= 400` or `status == 0` (cancelled/failed). This catches broken images, missing JS chunks, failed API calls, blocked fonts — anything, not just images.

```
# What to look for in the `helpmetest interactive` network output:
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

For deeper resource timing (slow JS bundles, large images, blocking fonts), read the
browser's own resource timing. **There is no `Analyze Resources` keyword** — probed live
2026-09-25, it returns `No keyword with name 'Analyze Resources' found.`

```robot
${resources}=    Javascript    JSON.stringify(performance.getEntriesByType('resource').map(r=>({name:r.name,type:r.initiatorType,ms:Math.round(r.duration),bytes:r.transferSize})).sort((a,b)=>b.ms-a.ms).slice(0,15))
Log    ${resources}
```

That gives the 15 slowest assets with transfer size and duration — enough to find the
heaviest resource behind a slow first paint.

#### 5. Mobile layout

Walk the primary user flow on iPhone. Use:

```robot
Test On  iPhone 13  <base-url>
Javascript  document.documentElement.scrollWidth > document.documentElement.clientWidth
```
Request a screenshot via `helpmetest interactive` with screenshot flag to eyeball nav, text clipping, and tap target sizes.

**Pass:** `False` — no horizontal overflow. Layout collapses correctly.  
**Fail:** `True` — content overflows the viewport horizontally. Users on mobile must scroll sideways, which is always a bug.

Also eyeball the screenshot for: nav hidden/unusable, text clipping, buttons too small to tap (< 44px), modals cut off. These are UX bugs — note them in the findings table even if overflow is clean.

After the probe, close the mobile context and switch back to desktop before continuing the rest of the triage.

#### 6. Performance thresholds

**`Analyze Web Vitals` does not exist** — probed live 2026-09-25, bare and with the
documented precondition, both `No keyword with name 'Analyze Web Vitals' found.` Read the
numbers from the browser instead. Note also that `Scroll By` takes **no** numeric offsets:
`Scroll By  0  300` fails with `Error while parsing css selector "0"`, because its first
argument is a selector. A bare `Scroll By` scrolls one viewport (measured: `scrollY` 0 →
1080); repeat it to go further.

```robot
Go To    ${URL}
Wait For Load State    networkidle
Scroll By
Sleep    2s

# Navigation timing — DNS, TCP, TLS, TTFB, domInteractive, load
${nav}=    Javascript    JSON.stringify(performance.getEntriesByType('navigation')[0])
Log    ${nav}

# Paint timings, when the browser recorded them
${paint}=    Javascript    JSON.stringify(performance.getEntriesByType('paint').map(p=>({name:p.name,ms:Math.round(p.startTime)})))
Log    ${paint}

# Layout shift total
${cls}=    Javascript    String(performance.getEntriesByType('layout-shift').reduce((s,e)=>e.hadRecentInput?s:s+e.value,0))
Log    ${cls}
```

The interactive session also prints `DNS / TCP / TLS / TTFB / resp / domInteractive / load`
under **Browser State** on every navigation, with no keyword at all — for a quick read that
is usually enough.

Apply Lighthouse thresholds to whatever you collected:

| Metric | Good | Needs improvement | Bug |
|---|---|---|---|
| LCP | < 2500ms | < 4000ms | ≥ 4000ms |
| FCP | < 1800ms | < 3000ms | ≥ 3000ms |
| CLS | < 0.1 | < 0.25 | ≥ 0.25 |
| INP | < 200ms | < 500ms | ≥ 500ms |

An empty result is a real answer, not a broken probe: a small page records no
`largest-contentful-paint` entry at all. Assert on a metric only where you know the page
produces it.

Measured on the todo playground 2026-09-25, this exact sequence returned
`[{"name":"first-paint","ms":408},{"name":"first-contentful-paint","ms":408}]` and a layout
shift total of `0` — so the recipe produces real numbers, not empty strings.

**Pass:** all ratings `good` or `needs-improvement`.  
**Fail (Bug):** any rating `poor` → document as a Bug with the raw value. LCP ≥ 4s loses conversions; CLS ≥ 0.25 means content jumps while users are clicking.  
**Warn:** `needs-improvement` → UX illogicality, note in findings.

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

**There is no `Broken Links` keyword** — probed live 2026-09-25:
`No keyword with name 'Broken Links' found.` Collect the links yourself, then visit the ones
you care about. `Go To` returns the HTTP status, so a dead link is visible directly:

```robot
# Every link on the page, with its target and whether it leaves the origin
${links}=    Javascript    JSON.stringify(Array.from(document.querySelectorAll('a[href]')).map(a=>({href:a.href,text:a.textContent?.trim().slice(0,40),external:!a.href.startsWith(location.origin)})))
Log    ${links}

# Then check the ones that matter — nav items and CTAs first
${status}=    Go To    <a-url-from-the-list>
Should Be Equal As Integers    ${status}    200
```

Verified 2026-09-25: `Go To https://todo.playground.helpmetest.com/definitely-missing-page`
returns `404`, and the session prints its own warning
(`Navigation response returned HTTP 404 for …`), so a dead link cannot pass unnoticed.

**Pass:** no links returning 404/500.  
**Fail:** dead links found → document as a Bug listing affected URLs. 404s on navigation items or CTAs are P1 — they break user journeys silently.

#### 9. Empty state

Visit the app before any data exists (clear localStorage if needed, or use a fresh session) and screenshot the core content area:

```robot
Javascript  localStorage.clear()
Go To  <base-url>
Javascript  document.body.innerText.trim().length
```
Request a screenshot via `helpmetest interactive` with screenshot flag to confirm the empty state visually.

**Pass:** the empty area has a message explaining what belongs there, plus a CTA or instruction to create the first item.  
**Fail:** blank area, just a background, or only a spinner with no content → document as a UX illogicality: "Empty state missing — first-time users see no guidance."  
**Fail:** `innerText.length === 0` or near-zero → the whole page is blank, not just the list area → escalate to Bug.

Also check: search results with a query that returns nothing, filtered views with no matching items, and dashboards with no activity yet. Each is a separate empty state.

#### 10. Persistence after reload

Create or update data, reload the page, verify the data is still there:

```robot
# After creating data:
Go To  <base-url>
Javascript  JSON.stringify(localStorage)
```
Request a screenshot via `helpmetest interactive` with screenshot flag to confirm data is still visible after reload.

**Pass:** data survives a full page reload — either from localStorage, cookies, or the backend.  
**Fail:** data disappears on reload → the app stores state only in memory (React useState, in-memory variable). Document as a Bug: "Data not persisted — lost on page reload." This is a silent failure — the app looks functional but any reload wipes user work.

#### 11. Back/forward navigation

Navigate into a flow, then go back, and verify the app state is correct:

```robot
Go To  <base-url>
# Navigate forward (click into a detail, form, or sub-page)
Click  <link-or-cta>
Go Back
Javascript  document.body.offsetHeight
```
Request a screenshot via `helpmetest interactive` with screenshot flag to confirm the previous page rendered correctly.

**Pass:** back navigation lands on the previous state with correct content rendered.  
**Fail:** blank screen, crash, redirect loop, or wrong page after `Go Back` → SPA history is broken. Document as a Bug: "Browser Back renders [blank/wrong state] — back navigation broken."  
**Fail:** `offsetHeight === 0` after going back → page is empty, same class of error as the 404 blank screen.

Also try `Go Forward` after going back — SPA routers frequently handle one direction but break the other.

#### 12. Copy quality scan

Extract the page as Markdown — cleaner text than `innerText` for scanning copy artifacts:

`Markdown` is not a keyword either (`No keyword with name 'Markdown' found.`, probed
2026-09-25) — but the interactive session already prints the page's readable text for you
under the divider, so you rarely need to fetch it. To assert on it inside a test, read the
text and scan it in JS. `Evaluate` is BANNED by the platform validator, so the Python
`lambda` this recipe used to carry could never have run:

```robot
${hits}=    Javascript    JSON.stringify(['undefined','null','[object Object]','TODO','lorem ipsum','NaN','{{','}}'].filter(p=>document.body.innerText.toLowerCase().includes(p.toLowerCase())))
Should Be Equal    ${hits}    []    msg=Copy artifacts found: ${hits}
```

Scanning the rendered text catches leaked template variables, raw `[object Object]` renders,
unfilled placeholder copy, and unhandled nulls in the actual content.

**Watch the false positives**: `null` and `NaN` are substrings of ordinary words
("annulled", "financial"), and `innerText` includes nav and footer chrome. Treat a hit as a
lead to look at, not an automatic bug.

**Pass:** `${hits}` is empty.  
**Fail:** any match → document as Data quality with the matched term. These appear in prod more often than anyone expects: unrendered template variables (`{{name}}`), unformatted JS objects (`[object Object]`), unfilled placeholder copy (`lorem ipsum`), unhandled null values shown raw (`null`, `undefined`).

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

After orient, present this **then immediately proceed** — do not wait for a reply. Your first tool call (Step 1 navigation or read) happens in the same response turn as the announcement.

**URL already provided in the prompt (most common):**
> "Discovering `<url>` — I'll walk the live app, map every feature, and create Feature artifacts ready for /tdd. Starting now."
→ Immediately call `helpmetest interactive "Go To  <url>" --screenshot` in the same response.

**No source given yet:**
> "After this you'll have a complete map of this app — every feature, every user type, every scenario — structured and ready for test-first implementation. What's the source?
> - Live URL to walk
> - A PRD or spec doc (share the path or paste it)
> - Tickets (GitHub, Linear, Jira — give me access or paste them)
> - The codebase (I'll read it)"
→ Wait for the user's answer before proceeding.

**ProjectOverview exists (already discovered):**
> "This project was already mapped — [N] Feature artifacts exist covering [list area names]. I'll re-walk the live app to check for new features, drift, and undiscovered edge cases, and run an adversarial probe (SSL, 404s, console errors). Starting now."
→ **Immediately proceed to Step 2B. Do NOT summarize existing artifacts and stop. The re-walk AND adversarial probe are mandatory.**

---

## Step 1 — Identify the Source

You have three input types. Handle whichever exist.

**Framework-sourced (spec-kit / OpenSpec / PRD+tasks — detected in Orient First):**
Read the framework's spec file(s) completely (e.g. spec-kit's `specs/*/spec.md`, OpenSpec's
`openspec/specs/**`, or a `PRD*.md` + its matching `tasks-prd-*.md`). Do not ask the user
for a source — the framework's own output *is* the source. Extract features per Step 2A,
using the framework's own scenario language (spec-kit: Given/When/Then acceptance scenarios
and `FR-XXX` functional requirements; OpenSpec: its `## Requirements`/`## Scenarios` blocks;
PRD: its functional requirements section) verbatim — don't paraphrase, that's where drift
from the real spec starts.

**Docs (PRD / spec / tickets / API spec / Figma notes / codebase) — no framework detected:**
Read the source completely before asking anything. Then extract features (Step 2A).

**Live app (running URL):**
Navigate and explore. Then create Persona + ProjectOverview + Features (Step 2B).

If none of the above and the user hasn't said which, ask once:
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

3. **Framework-sourced only — requirement/scenario-to-task coverage gate:** before treating
   any implementation as complete, cross-check every requirement/scenario in the spec against
   the framework's own task breakdown (spec-kit's `tasks.md`, OpenSpec's `tasks.md`, a
   create-tasks PRD's parent tasks). A requirement with no matching task means the
   implementation may be silently incomplete — the test you write for it is likely to go red
   not because of a bug, but because the feature was never built. Flag these explicitly to the
   user before writing tests, rather than discovering the gap only when a test fails. (Observed
   real case: a spec-kit spec's `FR-006` — delete-a-list-with-confirmation — had no matching
   task in `tasks.md`; `/speckit.implement` never built it; the gap surfaced only when the
   resulting HelpMeTest test went red against a live app with no delete-list UI at all.)
4. Note every ambiguity. Ask at most 5 clarifying questions before creating artifacts:

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

**HARD LIMIT: ≤10 interactive calls total for exploration.** After 10 calls, you MUST stop exploring and proceed to Step 3 (create artifacts). More exploration is always available later — right now, artifact creation is the deliverable.

**Browser tool:** all live exploration uses `helpmetest interactive`. Load `modes/interactive.md` before starting — it covers session continuity, batching, output sections, selector discovery, and keyword reference. The Interactive section of every response gives you ready-to-paste commands for everything on the current page; use it instead of guessing selectors.
If an interactive command returns an error, **immediately try an alternative — never give up.**

Common keyword mistakes (these will error — use the right-hand side):
- `Type  selector  text` → **`Fill Text  selector  text`** (`Type` does not exist)
- `Check  selector` → **`Click  selector`** (use Click on checkboxes too; `Check` does not exist)
- `Scroll By  0  300` → **`Scroll By`** with no arguments. Its first argument is a *selector*,
  so `0` errors with `Error while parsing css selector "0"`. One bare call scrolls one
  viewport (measured 2026-09-25: `scrollY` 0 → 1080); repeat it to go further. Named args
  do not work either — `Scroll By  dy=500` errors with `Unknown engine "dy"`.
- `Analyze Web Vitals`, `Analyze Resources`, `Broken Links`, `Generate Sitemap`, `Markdown`,
  `Probe Navigation Elements` → **none of these keywords exist.** All six return
  `No keyword with name '<name>' found.` (probed live 2026-09-25, `Analyze Web Vitals` also
  retried with its documented OpenReplay precondition). Use the `Javascript` keyword to read
  the same data from the page — recipes are in the performance, link-audit and navigation
  sections of this file.
- `Keyboard Key  Enter` → error "expected 2 arguments"? Use `Press Keys  input.selector  Enter` instead.
- **The dangerous version of that mistake does NOT error.** `Keyboard Key  press  Enter` after a
  `Fill Text` is accepted, reports `✓`, and commits nothing — `Fill Text` leaves the element
  unfocused and `Keyboard Key` is page-level, so the key lands nowhere. Measured 2026-09-25 on
  `todo.playground.helpmetest.com`: that pair added **0** items with both keywords green, while
  `Press Keys  input.new-todo  Enter` added **1**. Committing a field is always
  `Press Keys  <selector>  Enter`; always read the state back afterwards.
- Element not found? Try `Javascript  document.querySelector('...').outerHTML` to inspect actual DOM.
- Click fails? Try `Hover` first, then click.
- Keep exploring until you have the selectors you need.

### Auth First

```
Read: modes/auth.md
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

Immediately map the app structure. **`Probe Navigation Elements` and `Generate Sitemap` do
not exist** — both return `No keyword with name '<name>' found.` (probed live 2026-09-25).
Read the structure out of the page instead:

```robot
# Every link on the page, grouped by host. Do NOT pre-filter to nav/header/aside or to
# location.origin — see the measured note below; both filters can silently return [].
${links}=    Javascript    JSON.stringify(Array.from(document.querySelectorAll('a[href]')).map(a=>({text:a.textContent?.trim().slice(0,40),href:a.href,host:new URL(a.href).host})))
Log    ${links}

# Distinct hosts, so a multi-subdomain product shows its real shape
${hosts}=    Javascript    JSON.stringify([...new Set(Array.from(document.querySelectorAll('a[href]')).map(a=>new URL(a.href).host))])
Log    ${hosts}

# Clickable things that are NOT links — these will not appear above
${clickable}=    Javascript    String(document.querySelectorAll('[onclick], [data-href], button').length)
Log    ${clickable}
```

Use the link list as your exploration checklist, and note two ways a narrower version of
this returns nothing. Measured on `playground.helpmetest.com`, 2026-09-25: the page has
**29** `a[href]`, yet `nav a, header a, [role=navigation] a, aside a` matched **0** (the
links live in a card grid), and filtering with `startsWith(location.origin)` also matched
**0**, because every link points at a *subdomain* (`diagnostics.playground…`,
`webhook.playground…`). An empty result from a filtered selector usually means the filter is
wrong, not that the page has no links — count `a[href]` first.

This is one page's worth of links, not a crawl. Pages nothing links to (admin routes, deep
links, settings sub-pages) never appear; find those from the codebase, the router, or by
asking. The `clickable` count is a hint that navigation happens via JS handlers, which no
link query will reveal.

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
  "name": "<Name> — shop staff, admin, etc.",
  "content": {
    "name": "<Name> — shop staff, admin, etc.",
    "description": "Who they are",
    "persona_type": "primary|secondary|admin",
    "goals": ["What they want"],
    "username": "<from Create Fake Email>",
    "password": "SecureTest123!",
    "auth_state": "<StateName>",
    "permissions": ["what they can do"]
  }
}
```

**`content.name` is required and this template used to omit it.** Verified against
`artifact schema Persona` 2026-09-25: content requires `name`, `description` and
`persona_type`. The top-level `name` on the upsert is a different field — it does not
satisfy the content requirement, and the write is rejected. The same trap applies to every
type: `Tasks`, `Feature` and `ProjectOverview` all require `name` *inside* content too.

Full content fields available: `type, name, description, links, persona_type, goals,
pain_points, username, password, auth_state, permissions, environment`.

### Create ProjectOverview

**Do this first, before any Feature artifacts.** Feature upserts require a `project:X` tag, which requires the ProjectOverview to exist first.

Required top-level fields: `name`, `description`, `url`, `summary`. Use `--file`:

```bash
cat > /tmp/project-overview.json << 'EOF'
{
  "name": "<Site Name> — Project Overview",
  "description": "What this site does and who it's for",
  "url": "<base url>",
  "summary": "One paragraph: what the app does, who uses it, core features",
  "industry": "todo|saas|e-commerce|etc",
  "persona_ids": [],
  "features": [
    { "feature_id": "feature-<id>", "name": "<Feature Name>", "status": "working" }
  ]
}
EOF
helpmetest artifact upsert --id "<domain>" --type ProjectOverview \
  --name "<Site Name> — Project Overview" \
  --tags "project:<domain>" \
  --file /tmp/project-overview.json
```

**The `--id` must be exactly `<domain>` — the project namespace is derived from the
ProjectOverview's id, not from its tags.** This line used to say `--id "project-<domain>"`,
which creates a namespace called `project-<domain>` while every Feature is tagged
`project:<domain>` — so the first Feature upsert is rejected with `no ProjectOverview
artifact found`. Measured 2026-09-26: a ProjectOverview created with **no tags at all**
still accepted Features tagged with its id, and one tagged `project:A` with id `B` accepted
Features tagged `project:B`, not `project:A`. The id is the namespace.

This has already happened on the live instance: `project-overview-scratchpad-notes` exists
as a ProjectOverview and shows up in the "Existing projects" list, while the real project
is `scratchpad-notes` — a phantom namespace with nothing in it.

---

## Step 3 — Create Feature Artifacts

**Run `helpmetest artifact schema Feature` if you change anything below.** This template is
verified against the live schema (2026-09-25), but it was wrong for a long time precisely
because an earlier version of this line said *"do NOT call artifact schema"* — it shipped
`"source"` and `"gaps"`, neither of which exists, and nothing could catch it.

For each capability. Required content fields: `name`, `description`, `goal`. Use `--file` and tag with `project:<domain>`:

```bash
cat > /tmp/feature-<id>.json << 'EOF'
{
  "name": "<Feature Name>",
  "description": "One sentence: what this feature lets users do",
  "goal": "<what business outcome this serves — one sentence>",
  "status": "untested",
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
  "notes": [],
  "bugs": []
}
EOF
helpmetest artifact upsert --id "feature-<id>" --type Feature \
  --name "<Feature Name>" \
  --tags "project:<domain>,priority:high" \
  --file /tmp/feature-<id>.json
```

The `--tags "project:<domain>"` is **required** — omitting it causes tag validation failure. Use the same `<domain>` as the ProjectOverview ID.
**Fields that do not exist**: `source` and `gaps` are both rejected with `422: Extra inputs are not permitted`. Anything not in the schema is fatal, not ignored — put stray observations in `notes` (array of strings) or `gotchas`.
**If you populate `bugs[]`**, each entry requires: `name` (string), `severity` (`critical|major|minor`), `given`, `when`, `then`, `actual`. Missing `name` causes a 422. Leave `bugs: []` empty during initial discovery — document bugs only if you observe broken behavior.

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

**This is mandatory.** Your final response MUST end with this exact block — do not skip it:

```
Feature artifacts ready.

→ /tdd — write tests for feature-<highest-priority-id> first
```

**Version:** 0.1
