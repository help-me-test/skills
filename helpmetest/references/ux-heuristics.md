# UX Heuristics for AI-Powered UI Testing

Use when evaluating screenshots or page interactions. Load this file when doing visual checks, QA reviews, or `/helpmetest ui`. These are structured criteria — cite the specific heuristic when reporting a finding.

---

## 1. Laws of UX

### Fitts's Law — target size and distance
- Primary CTAs should be the largest clickable elements in their section
- Destructive actions (delete, cancel) must NOT be larger than constructive ones
- Mobile tap targets: ≥44×44px (Apple HIG) / ≥48×48px (Material)
- Navigation items need generous padding, not just text-sized hit areas
- Form submit buttons should be full-width on mobile

### Hick's Law — decision time grows with choices
- Navigation menus with >7±2 items should be grouped/categorized
- Settings pages with many options need sections/tabs, not a flat list
- Modals should present one clear action, not competing choices
- Dropdowns with 15+ items need search/filter
- Action menus organized by frequency of use

### Miller's Law — working memory holds ~7±2 items
- Long lists chunked into groups of 5-9
- Dashboards prioritize 3-5 key metrics
- Multi-step wizards show ≤7 steps
- Phone numbers, codes, card numbers visually grouped

### Jakob's Law — users expect conventions
- Login: email/username on top, password below, submit at bottom
- Logo links to homepage/dashboard
- Back buttons top-left
- Search in header
- Settings gear → settings
- User avatar/menu top-right
- Sidebar navigation left, content right

### Doherty Threshold — responses under 400ms feel instant
- System response <400ms for user actions
- Loading indicators appear for operations >1s
- Optimistic UI updates for common actions (toggle, save, like)
- Skeleton screens for content loading
- No full-page reloads for in-page actions

### Von Restorff Effect — standout items are memorable
- Most important element on each page is visually distinct
- Pricing page highlights recommended plan
- Error messages stand out from surrounding content
- Primary action visually differentiated from secondary

### Zeigarnik Effect — incomplete tasks are remembered
- Multi-step forms show progress indicators
- Onboarding flows show completion percentage
- Incomplete tasks visually distinct from complete

---

## 2. Nielsen's 10 Usability Heuristics

### H1: Visibility of System Status
- Current page highlighted in navigation
- Form submissions show success/failure feedback
- File uploads show progress bars
- Background operations show status (syncing, saving)
- Timestamps show when data was last updated

### H2: Match System to Real World
- Error messages use plain language, not error codes
- Dates use user's locale format, not ISO/Unix
- Status labels are meaningful ("Processing payment" not "State: 3")

### H3: User Control and Freedom
- Undo available for destructive actions
- Cancel buttons on all forms and modals
- Back navigation works and preserves state
- Filters can be reset to defaults
- Escape key closes modals/dropdowns
- Clicking outside modal closes it

### H4: Consistency and Standards
- Same action uses same button style everywhere
- Terminology is consistent (don't mix "delete" and "remove")
- Date/time formatting consistent throughout
- Empty states follow the same pattern across sections
- Error message style consistent (toast vs inline vs banner)

### H5: Error Prevention
- Destructive actions require confirmation
- Form inputs have constraints (type=email, maxlength)
- Dangerous buttons visually distinct (red) and not adjacent to safe ones
- Unsaved changes trigger "Leave page?" confirmation
- Input fields show format hints before typing (placeholder, helper text)

### H6: Recognition Over Recall
- Recently used items shown
- Navigation labels visible, not hidden behind icons only
- Search has autocomplete/suggestions
- Dashboard widgets show labels, not just numbers

### H7: Flexibility and Efficiency
- Keyboard shortcuts for power users
- Bulk actions for repetitive tasks
- Copy-to-clipboard for IDs, keys, URLs
- Sensible default values

### H8: Aesthetic and Minimalist Design
- No redundant information on page
- Visual noise minimized (unnecessary borders, decorations)
- White space creates focus
- Forms ask only what's truly needed

### H9: Help Recognize and Recover from Errors
- Error messages: WHAT went wrong in plain language
- Error messages: HOW to fix it
- Form validation errors next to the relevant field, not just at top
- Form data preserved after error
- Network errors offer retry
- 404 pages suggest alternatives

### H10: Help and Documentation
- Contextual help for complex features (tooltips, "?" icons)
- Empty states include guidance on what to do next
- Error states link to relevant help articles

---

## 3. Error States & Edge Cases

### Empty States
- Every list/table has a designed empty state (not blank space)
- Empty states explain what this section is for
- Empty states include CTA to create first item
- Search with no results offers suggestions
- Filtered views with no matches: "No results match your filters" + clear button

### Error Boundaries
- JS errors don't crash the entire page
- Failed API calls show a meaningful error, not blank section
- Network disconnection shows offline indicator
- Authentication expiry redirects to login with message

### Form Edge Cases
- Extremely long text input doesn't break layout
- Special characters don't cause errors (quotes, unicode, emoji)
- Double-clicking submit doesn't create duplicates
- Required field indicators visible before submission
- Tab order through form fields follows visual order

### Loading States
- Initial page load has skeleton screens or loading indicators
- Data refresh shows subtle loading indicator (not full-page spinner)
- Long-running operations show progress
- Optimistic updates revert gracefully if server rejects

### Permission & Auth Edge Cases
- Unauthorized access: meaningful message, not raw 403
- Expired session redirects to login and returns user to where they were
- Role-based UI hides actions user can't perform (not just disables)

---

## 4. Data Display Heuristics

### Tables
- Column headers clear and concise
- Numeric columns right-aligned, text columns left-aligned
- Long cell content truncated with tooltip, not overflowing
- Sortable columns indicated with sort icon
- Empty table has designed empty state
- Pagination shows total count and current range ("Showing 1-25 of 142")
- On mobile: horizontal scroll OR card layout

### Charts & Graphs
- Clear titles and axis labels
- Legend visible and matches colors
- Zero-data state shows a message, not empty chart
- Color palette accessible (not color alone to distinguish series)
- Bar chart Y-axis starts at zero

### Dashboard Metrics
- Key metrics have label + value + context (trend, comparison period)
- Large numbers formatted (1.2K not 1200, $1.5M not $1500000)
- Percentage changes show direction (arrow or color)
- 3-5 key metrics — not everything

### Filters & Search
- Active filters visible and individually removable
- "Clear all filters" exists when any filter active
- Filter state persists across page navigation
- Date range validates start < end

### Numbers, Dates & Formatting
- Dates consistent throughout the app
- Relative dates where appropriate ("3 hours ago")
- Large numbers abbreviated consistently (K, M, B)
- Null/undefined shows dash or "N/A", never "null" or blank

---

## 5. Visual Design Checks

### Typography
- Body text ≥16px desktop, ≥14px mobile
- Line height 1.4–1.6 for body text
- Clear heading scale: h1 > h2 > h3
- Max line length 60–80 chars for readability
- Monospace for code, IDs, technical values

### Color & Contrast
- WCAG AA: 4.5:1 contrast for normal text
- WCAG AA: 3:1 contrast for large text (18px+ or 14px+ bold)
- Error = red, Success = green, Warning = amber, Info = blue — consistently
- Disabled states muted but still readable

### Spacing & Layout
- No content touches viewport edge without padding
- Cards/containers have consistent internal padding
- Related items closer together than unrelated (proximity principle)

### Interactive Elements
- All buttons have visible hover states
- Form inputs have clear focus states
- Loading buttons show spinner and prevent double-click
- Toggle/switch: clear on vs off
- Dropdown chevron points down when closed, up when open
- Destructive buttons visually distinct (red, not primary style)

---

## 6. Accessibility Quick Checks

- All interactive elements reachable via Tab
- Tab order follows visual order (top-to-bottom, left-to-right)
- Focus ring visible on every element
- Escape closes modals/dropdowns
- Focus trapped inside open modals
- Focus returns to trigger when modal closes
- Images have alt text (or aria-hidden if decorative)
- Form inputs have associated labels (not just placeholder)
- Headings hierarchical (no h1 → h4 skips)
- Custom components (tabs, menus) have correct ARIA roles
- App respects `prefers-reduced-motion`
- Information not conveyed by color alone (icons + color for errors)
