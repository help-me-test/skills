---
name: ui-review
description: "Deep UI walkthrough with screenshot-based analysis across all pages and viewports (desktop + tablet + mobile). Delivers per-page improvement pitches grounded in what you actually see. Use when user says 'review the UI', 'pitch UI improvements', 'how does this look', 'UX audit', 'walk through the app'."
argument-hint: [url-or-app-name]
allowed-tools: mcp__helpmetest-*
---

> **Who you are:** If `.helpmetest/SOUL.md` exists in this project, read it before starting — it defines your character and shapes how you work.

> **No MCP?** The CLI has full feature parity — use `helpmetest <command>` instead of MCP tools. See the [CLI reference](../README.md#no-mcp-use-the-cli).

# UI Review

Systematic visual walkthrough of every page in the app. You navigate, screenshot, analyze what you actually see, then deliver opinionated improvement pitches per page and per viewport.

This is NOT a formal test run. It is a design and UX audit through a real browser.

## When to Use This Skill

- "Review the UI and pitch improvements"
- "Walk through the app and tell me what to fix"
- "UX audit"
- "How does this look on mobile?"
- "Give me UI feedback on all pages"

**NOT for:**
- Creating automated tests (use `/test-generator`)
- Finding functional bugs (use `/helpmetest`)
- Debugging a specific broken test (use `/debug-tests`)

---

## Phase 0: Orient Before You Act

**Always do this first. Never skip.**

```
helpmetest_status()
how_to({ type: "authentication_state_management" })
```

Check:
1. What auth states are saved? (e.g. "Admin", "Helpmetest")
2. When was the state last used? Is it stale?

### Stale State Protocol

A saved state goes stale if the session expired or if `Save As` was never run against the live app. Signs of stale state: 302 redirects to login, landing on `/login` after `As <Name>`, empty/broken UI.

**If stale → refresh it first:**
- Find the maintaining test (usually named "Setup Auth <Name>" or similar)
- Run it: `helpmetest_run_test({ id: "<test-id>" })`
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

## Phase 5: Deliver the Pitch

After all screenshots, write a structured UI improvement pitch.

**Format per page:**

```
## [Page Name]

### What I Saw (Desktop / Tablet / Mobile)
[2-4 sentences describing actual visual observations. Reference specific elements by name. Mention what's good too — not everything needs fixing.]

### Issues Found
- [Specific issue]: [What you saw, what it breaks for the user]
- [Specific issue]: [What you saw, what it breaks for the user]

### Improvement Pitches
1. **[Change name]** — [What to change, why, expected impact]
2. **[Change name]** — [What to change, why, expected impact]

### Viewport Notes
- Desktop: [anything desktop-specific]
- Tablet: [any breakpoint weirdness]
- Mobile: [any mobile-specific issues or wins]
```

End with a **Priority Stack** — a ranked list of the top 5 changes across all pages that would have the biggest impact:

```
## Top 5 Improvements (Ranked by Impact)

1. [Page] — [Change] — [Why it's #1]
2. ...
3. ...
4. ...
5. ...
```

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

# ... repeat for all pages ...

# Phase 5: Write the pitch
```

---

## Checklist Before Submitting the Pitch

- [ ] Visited every page at desktop (1440x900)
- [ ] Visited every page at mobile (375x667)
- [ ] Visited every page at tablet (768x1024)
- [ ] Scrolled long pages at each viewport
- [ ] Triggered at least one interactive state per page (hover, click, expand)
- [ ] Every observation references what was seen in a screenshot, not guessed from code
- [ ] Every suggestion is specific and actionable (names the element, states the change)
- [ ] Priority stack lists top 5 across all pages
