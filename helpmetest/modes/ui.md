> **Who you are:** If `.helpmetest/SOUL.md` exists in this project, read it before starting — it defines your character and shapes how you work.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

---


# UI Review

Systematic visual walkthrough of every page in the app. You navigate, screenshot, analyze what you actually see, then deliver opinionated improvement pitches per page and per viewport.

This is NOT a formal test run. It is a design and UX audit through a real browser.

**Reference files — load on demand:**
- `references/ux-heuristics.md` — Laws of UX, Nielsen's 10, data display, visual checks, a11y — load when evaluating screenshots or writing findings
- `references/adversarial-patterns.md` — attack patterns for forms, modals, keyboard nav — load when doing interactive QA
- `references/rf-recipes.md` — axe-core, console errors, broken images, performance, responsive sweep — load when running deterministic checks

## Quick Check vs Full Audit

**Quick Check** — a focused visual question about one page or element.
Use when: "does the button look right", "is this centered", "check if the header renders on mobile".
Still produces a UIReview artifact — it's just scoped to what was asked.

**Full Audit** — systematic walkthrough of every page at desktop + tablet + mobile.
Use when: "review the UI", "walk through the app", "UX audit", "give me UI feedback".

The skill auto-detects which mode based on the scope of the request. In both cases, screenshots go into a UIReview artifact — nothing is a "one-off that doesn't get recorded".

## When to Use This Skill

- "Does this button look right?" / "Is this layout broken?"
- "Review the UI and pitch improvements"
- "Walk through the app and tell me what to fix"
- "UX audit"
- "How does this look on mobile?"
- Any visual question — quick or thorough

**NOT for:**
- Creating automated tests (use `/tdd`)
- Finding functional bugs (use `/helpmetest`)
- Debugging a specific broken test (use `/fix`)

---

## Quick Check Mode

If the request is focused (one page, one element, one question):

1. Navigate and screenshot the relevant state
2. Describe exactly what you see — specific elements, what's right, what's wrong
3. If needed, check responsive states (mobile/desktop) or interaction states (hover, open)
4. Create a UIReview artifact even for a quick check — scoped to the question:
   - `pages`: just the pages you looked at
   - `actions`: any fixes found, ranked
   - If nothing is wrong: `actions: []` is valid

Then stop. Don't launch a full audit unless the user asks for one.

---

## Phase 0: Orient Before You Act

**Always do this first. Never skip.**

Check what auth states are available:

```bash
helpmetest artifact list --type Persona
```

After orient, announce before navigating anywhere:

**No specific page or question given (bare invocation):**
> "After this you'll have screenshots of every page at desktop, mobile, and tablet, plus a ranked list of what to fix — ordered by impact across the whole app. Takes about 10–15 minutes. Full audit, or is there a specific page or flow you want me to focus on?"

**Specific page or question given:**
> "After this you'll know exactly what's wrong with [page/element] and what to change. Taking a look now."

Wait for scope answer if bare. If specific: proceed directly to Phase 1 scoped to that page.

Check:
1. What auth states are saved? (e.g. "Admin", "Helpmetest")
2. When was the state last used? Is it stale?

### Stale State Protocol

A saved state goes stale if the session expired or if `Save As` was never run against the live app. Signs of stale state: 302 redirects to login, landing on `/login` after `As <Name>`, empty/broken UI.

**If stale → refresh it first:**
- Find the maintaining test (usually named "Setup Auth <Name>" or similar)
- Run it: `helpmetest test run <test-id>`
- It performs login and calls `Save As <Name>` — now the state is fresh
- Only proceed to the walkthrough after that test passes

### Domain Lock

Auth cookies are scoped to a domain. Once you authenticate on `app.example.com`, stay on that domain for the entire session. Never navigate to a different domain (e.g. prod vs staging) mid-session — it will destroy the auth state silently.

---

## Phase 1: Discover the Pages

If you don't already know all pages/tabs in the app:

```robot
As  <StateName>
Go To  <base-url>
```

Look at the screenshot. Identify:
- Top-level navigation items (tabs, sidebar links)
- Any visible sub-pages or drawers
- The URL structure

List all pages you will visit. This becomes your review checklist.

---

## ⚠️ Screenshots: Use What You Already Have

**NEVER invent an alternative screenshot method.** Do NOT use playwright, puppeteer, Python scripts, curl, or any other tool to capture screenshots.

`helpmetest interactive "<keyword>" --screenshot` captures the page and saves the screenshot file (path shown in the output). That file IS the screenshot. Use it.

To upload a screenshot to storage:

```bash
helpmetest upload page-name-desktop.png
```

The screenshot file path is shown in the `helpmetest interactive ... --screenshot` output. Use it immediately — do not re-capture, do not write code, do not use external tools.

---

## Phase 2: Desktop Walkthrough (1440x900)

For each page in your checklist:

```robot
As  <StateName>
Set Viewport Size  1440  900
Go To  <page-url>
```

What to observe per screenshot:
- **Layout**: Is the page using space well? Blank areas? Dense areas?
- **Hierarchy**: Does the most important thing dominate visually?
- **Navigation**: Is it clear where you are? Are active states visible?
- **Actions**: Are the primary actions obvious? Are secondary actions buried?
- **Data density**: Too much? Too little? Is it scannable?
- **Typography**: Readable at a glance? Inconsistent sizing?
- **Empty states**: What happens when there's no data?
- **Loading states**: Are they informative or just spinners?
- **Bugs visible from looking**: Wrong labels, truncated text, misalignment, invisible controls

Scroll if the page is long:
```robot
Scroll By  0  800
```

Interact to see more states:
```robot
# Open a dropdown, expand a row, hover a button — whatever reveals more UI
Click  <selector>
Hover  <selector>
```

---

## Phase 3: Mobile Walkthrough (375x667)

Repeat for every page at iPhone SE viewport:

```robot
Set Viewport Size  375  667
Go To  <page-url>
```

Mobile-specific things to check:
- **Does the layout collapse correctly?** No horizontal scroll, no text clipping
- **Touch targets**: Are buttons big enough? (min 44x44px recommended)
- **Navigation**: Is the nav accessible? Hidden behind hamburger? Visible at all?
- **Tables/grids**: Do they reflow? Or do they overflow off-screen?
- **Text**: Does it resize? Is anything too small to read?
- **Modals/popups**: Do they fit the viewport? Can you scroll inside them?
- **Forms**: Are inputs full-width? Keyboard-friendly?

---

## Phase 4: Tablet Walkthrough (768x1024)

Repeat for every page at iPad viewport:

```robot
Set Viewport Size  768  1024
Go To  <page-url>
```

Tablet-specific things to check:
- **Breakpoint fallback**: Does it inherit desktop or mobile layout? Is it the right choice?
- **Column count**: Single-column mobile vs multi-column desktop — what happens in between?
- **Navigation**: Hamburger or full nav? Right call for this width?
- **Data tables**: Readable? Or horizontally scrolling?
- **Cards/grids**: Good column count or oddly sparse?

---

## Phase 5: Accessibility Audit (axe-core + screen reader)

Run automated accessibility checks on each page. Inject via browser console:

```javascript
javascript:(function(){var s=document.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.0/axe.min.js';document.head.appendChild(s);s.onload=function(){axe.run(function(results){console.log(JSON.stringify(results,null,2));});};})();
```

**For each page, capture:**
- Violation count by impact: critical / serious / moderate / minor
- Rule IDs: e.g. ["color-contrast", "button-name", "image-alt"]

**Severity thresholds:**
- **Critical** (blocks users — missing alt, unlabeled button) → fix immediately
- **Serious** (major barriers — contrast, missing form labels) → current sprint
- **Moderate** (annoyances — redundant alt) → backlog
- **Minor** (technically violations, no practical impact) → document only

**Screen reader flow check** on 2-3 key pages (home, main feature, form):
- Tab through → all focusable elements reachable in logical order?
- Check: button names announced, form labels read, image descriptions given
- Look for: missing `aria-label`, `role` conflicts, focus traps

Add accessibility findings to `actions` with `category: accessibility`.

---

## Phase 6: Create the UIReview Artifact

After all screenshots, create a `UIReview` artifact using `helpmetest artifact upsert --type UIReview`.

**Artifact structure:**

```json
{
  "type": "UIReview",
  "name": "<App Name> — UI Review",
  "description": "UI walkthrough of <App Name> at <date>",
  "app_name": "<App Name>",
  "base_url": "<base URL>",
  "reviewed_at": "<ISO date>",
  "pages": [
    {
      "name": "Home",
      "url": "https://...",
      "what_i_saw": "2-4 sentences: what you observed. Name specific elements. Mention what's good too.",
      "screenshots": [
        { "viewport": "desktop", "width": 1440, "height": 900, "url": "<uploaded screenshot URL>" },
        { "viewport": "mobile",  "width": 375,  "height": 667, "url": "<uploaded screenshot URL>" },
        { "viewport": "tablet",  "width": 768,  "height": 1024, "url": "<uploaded screenshot URL>" }
      ]
    }
  ],
  "actions": [
    {
      "rank": 1,
      "page": "Home",
      "title": "Fix nav active state visibility",
      "description": "The active nav item renders at 30% opacity. Users can't tell where they are. Make it solid with a distinct background or underline.",
      "priority": "high",
      "status": "pending"
    },
    {
      "rank": 2,
      "page": "Settings",
      "title": "Move Save button above the fold on mobile",
      "description": "On 375px the Save button is offscreen. Sticky footer or move to top of form.",
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

**Rules for `actions`:**
- One flat list across all pages — do NOT write separate per-page issues, pitches, or a priority_stack
- `rank` = global priority order (1 = most impactful across the entire app)
- `title` = short, actionable ("Fix X", "Add Y", "Remove Z") — not a description
- `description` = what to change + why + expected impact — enough to act on without needing context
- `priority` = `"high"` | `"medium"` | `"low"`
- `status` = `"pending"` (always start as pending)

---

## Interaction Patterns

Use these to reveal more UI states during the walkthrough:

```robot
# Check hover states
Hover  <selector>

# Open dropdowns, menus, modals
Click  <selector>

# Fill in a search to see filtered states
Fill Text  input[type="search"]  test

# Scroll to bottom to check footer / infinite scroll
Scroll By  0  9999

# Check empty state by navigating to a page with no data
Go To  <empty-page-url>

# Check loading state (if possible)
# Navigate to a slow page and screenshot immediately
Go To  <url>
```

---

## Guidelines

**Ground everything in screenshots.**
Do not describe what you think the page looks like from reading the code. Navigate, take the screenshot, describe what is actually rendered.

**Be specific and opinionated.**
- Bad: "The layout could be improved"
- Good: "The GROUP BY tabs are nearly invisible at 30% opacity — users won't know they can filter by status. Make them solid with a clear active indicator."

**Name the element.**
Always say which button, which column, which tab, which card. "The button" is useless. "The 'Run Test' button in the test card's bottom-right corner" is actionable.

**Cover the full picture.**
- What is good (don't tear down everything)
- What is confusing or broken
- What is missing that users will want
- What is there that users don't need

**Separate viewport feedback.**
Desktop feedback != mobile feedback. A layout can be great on desktop and terrible on mobile. Call both out separately.

**Respect existing conventions.**
If the app has an established design language (colors, spacing, component styles), pitch improvements that fit within it — don't suggest wholesale redesigns unless the system is fundamentally broken.

---

## Example Session Skeleton

```robot
# Phase 0: Orient
# → checked auth states, found "Helpmetest" state, ran Setup Auth test to refresh it

# Phase 1: Discover pages
As  Helpmetest
Set Viewport Size  1440  900
Go To  https://app.example.com
# → screenshot shows: Dashboard, Tests, Updates, Artifacts, Settings tabs

# Phase 2: Desktop
Go To  https://app.example.com/dashboard
# screenshot + notes

Go To  https://app.example.com/tests
# screenshot + notes

Go To  https://app.example.com/updates
# screenshot + notes

Go To  https://app.example.com/artifacts
# screenshot + notes

Go To  https://app.example.com/settings
# screenshot + notes

# Phase 3: Mobile
Set Viewport Size  375  667
Go To  https://app.example.com/dashboard
# screenshot + notes

# ... repeat for all pages ...

# Phase 4: Tablet
Set Viewport Size  768  1024
Go To  https://app.example.com/dashboard
# screenshot + notes

# Phase 5: Accessibility Audit + Write the pitch

# ... repeat for all pages ...

# Phase 5: Accessibility Audit (axe-core + screen reader)
```

---

## Phase 7: Fix Loop (when the user asks you to fix an action)

When the user picks an action and says "fix this" or "can you fix #N":

1. **Fix the code** — make the change in the source file
2. **Verify live** — take a new screenshot at the relevant viewport to confirm it looks right
3. **Upload the new screenshot** — `helpmetest upload <path>`
4. **Update the artifact** — two partial updates:
   - Mark the action done: `helpmetest artifact upsert --id <id> --content '{"actions.<N>.status": "done"}'`
   - Replace the screenshot: `helpmetest artifact upsert --id <id> --content '{"pages.<P>.screenshots.<V>.url": "<new-url>"}'`

   Where `<N>` is the action index (0-based), `<P>` is the page index, `<V>` is the screenshot index for the viewport that changed.

**Never mark an action done without a new screenshot proving it works.**

**Screenshot index reference:**
- `pages.<P>.screenshots.0` = desktop
- `pages.<P>.screenshots.1` = mobile
- `pages.<P>.screenshots.2` = tablet

---

## Checklist Before Creating the Artifact

- [ ] Accessibility check run at each viewport (axe-core violations captured)
- [ ] Visited every page at mobile (375x667)
- [ ] Visited every page at tablet (768x1024)
- [ ] Scrolled long pages at each viewport
- [ ] Triggered at least one interactive state per page (hover, click, expand)
- [ ] Every `what_i_saw` references what was seen in a screenshot, not guessed from code
- [ ] `actions` is a single flat list — no separate issues/pitches/priority_stack
- [ ] Every action has `rank`, `page`, `title`, `description`, `priority`, `status`
- [ ] `title` is short and actionable ("Fix X", "Add Y")
- [ ] `description` has enough context to act on without reading anything else

## Checklist After Fixing an Action

- [ ] Code change made in source file
- [ ] New screenshot taken at the affected viewport showing the fix
- [ ] New screenshot uploaded via `helpmetest upload`
- [ ] Action `status` updated to `"done"` via partial artifact update
- [ ] Screenshot URL in artifact updated to the new post-fix screenshot
