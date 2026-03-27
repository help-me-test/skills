# Phase 1: Deep Discovery

**GOAL: Find ALL pages, buttons, and interactable elements on the site.**

## Process

Keep discovering and exploring pages until no new pages are found for 3 consecutive exploration rounds.

For each page you explore:
1. Navigate to the page
2. Review interactable elements shown in the response (buttons, links, forms)
3. Note any new URLs you haven't seen before
4. Count interactable elements on this page
5. Mark this page as explored

Report progress after each page:
- How many pages discovered total
- How many pages explored so far
- How many new pages found this round
- Total interactable elements seen

Stop when: No new pages found for 3 consecutive explorations

## Steps

1. **Navigate to URL** using `helpmetest_run_interactive_command`

2. **Identify industry and business**:
   - What business is this?
   - What can users do here?
   - What are the critical user journeys?

3. **Explore unauthenticated pages EXHAUSTIVELY**:
   - Homepage, footer links, navigation menus
   - Review interactable elements in each interactive response
   - Follow ALL links, document ALL pages
   - Track pages discovered, pages explored, pages remaining

4. **Authentication Setup (CRITICAL - Must Complete Before Phase 2)**:

   **BLOCKING:** You must set up authentication before exploring authenticated areas.

   Call `how_to({ type: "authentication_state_management" })` for the complete authentication setup process.

   **Summary of what you'll do:**
   - Check for existing Persona artifacts with credentials
   - If none exist, consult user about registration strategy (3 options)
   - Create maintaining test (login or registration based on strategy chosen)
   - Run maintaining test and verify it passes
   - Confirm saved state exists and works
   - Document credentials in Persona artifact

   **Exit criteria:**
   - ✅ Maintaining test created and PASSING
   - ✅ Saved state confirmed exists via `helpmetest_status`
   - ✅ Saved state confirmed works via "As <StateName>" test
   - ✅ Persona artifact created with credentials

   **DO NOT PROCEED until all exit criteria met.**

   If authentication fails, STOP and debug interactively until it works.

5. **Create Persona artifacts** for each user type:
   - persona_type, description, goals, pain_points
   - username, password, auth_state (for authenticated personas)

6. **Explore authenticated pages EXHAUSTIVELY**:
   - Use "As <StateName>" to restore auth
   - Explore user menus, dashboards, settings
   - Review interactable elements in each interactive response
   - Follow ALL authenticated links
   - Track authenticated vs. unauthenticated page counts

7. **Create ProjectOverview artifact** with:
   - url, summary, industry
   - persona_ids (references to Persona artifacts)
   - features list (empty initially, will populate in Phase 2)
   - pages: [{ path, name, explored: true/false, interactable_count }]

## Exit Criteria

- ✅ No new pages discovered in last 3 exploration rounds
- ✅ ALL discovered pages explored
- ✅ Both unauthenticated AND authenticated sections explored
- ✅ Interactable elements reviewed on every page

## Report before Phase 2

```
Discovery Complete:
- Total pages discovered: X
- Total pages explored: X (100%)
- Unauthenticated pages: Y
- Authenticated pages: Z
- Total interactable elements: N
- Ready to enumerate features
```
