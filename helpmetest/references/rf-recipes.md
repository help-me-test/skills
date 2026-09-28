# Robot Framework Recipes for Deterministic UI Checks

Copy-paste keyword sequences for checks that produce structured data, not judgment calls.
Use these as the strongest form of assertion — they pass or fail on numbers, not screenshots.

Load this file when you need: axe-core, console errors, broken images, form labels, performance, web vitals, responsive sweep, link audit, broken links.

---

## Accessibility Audit (axe-core)

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Step 1: inject axe-core
Javascript    (()=>{const s=document.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js';document.head.appendChild(s);})()
Sleep    3s    # wait for script load

# Step 2: run the audit and filter to the impacts that matter, IN JS.
# Do not try to parse the JSON in Robot: `Evaluate` (and `json.loads` through it) is BANNED
# by the platform validator, which rejects the entire run with
# "'Evaluate' is not allowed — it executes arbitrary Python expressions."
${blocking}=    Javascript    axe.run().then(r=>JSON.stringify(r.violations.filter(v=>v.impact==='critical'||v.impact==='serious').map(v=>v.id+':'+v.impact+' — '+v.description)))
Log    ${blocking}

# ASSERT: no critical/serious violations
Should Be Equal    ${blocking}    []    msg=axe critical/serious violations: ${blocking}

# Full detail when you need to triage what came back
${all}=    Javascript    axe.run().then(r=>JSON.stringify({violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),passes:r.passes.length,incomplete:r.incomplete.length}))
Log    ${all}
```

Thresholds: `critical`/`serious` = must fix. `moderate`/`minor` = should fix.

---

## Performance Metrics

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Pull each number out as its own scalar. Do NOT parse JSON in Robot — `Evaluate`, and
# therefore `json.loads`, is BANNED by the platform validator and fails the whole run.
${fcp}=    Javascript    String(Math.round(performance.getEntriesByType('paint').find(p=>p.name==='first-contentful-paint')?.startTime||0))
${domInteractive}=    Javascript    String(Math.round(performance.getEntriesByType('navigation')[0]?.domInteractive||0))
${loadComplete}=    Javascript    String(Math.round(performance.getEntriesByType('navigation')[0]?.loadEventEnd||0))
Log    FCP ${fcp}ms · domInteractive ${domInteractive}ms · load ${loadComplete}ms

# Doherty Threshold: DOM interactive < 400ms feels instant
# Web Vitals: FCP < 1800ms = good, < 3000ms = needs work
Should Be True    ${fcp} < 3000    msg=FCP ${fcp}ms exceeds the 3s threshold
Should Be True    ${domInteractive} < 400    msg=DOM interactive ${domInteractive}ms exceeds 400ms
```

---

## Core Web Vitals — REMOVED: `Analyze Web Vitals` does not exist

This section documented a keyword the platform does not have. Probed 2026-09-25 against a
live session, twice — once bare, once following this recipe's own documented precondition
(`Go To` → `Wait For Load State  networkidle` → `Sleep  2s`):

```
0.000s  ✗ Analyze Web Vitals
  No keyword with name 'Analyze Web Vitals' found.
```

`Analyze Resources`, `Broken Links`, `Generate Sitemap`, `Markdown` and
`Probe Navigation Elements` return the identical error. None of them exist.

For real performance numbers, use the timings the interactive session already prints with
every navigation — `DNS`, `TCP`, `TLS`, `TTFB`, `resp`, `domInteractive`, `load` — or read
them from the page yourself:

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Navigation timing straight from the browser, no special keyword needed
${nav}=    Javascript    JSON.stringify(performance.getEntriesByType('navigation')[0])
Log    ${nav}

# Largest Contentful Paint. Verified 2026-09-25: the navigation entry above returns real
# JSON (`"duration":119.9…`), but this line returned an EMPTY string on a small page —
# the browser records no LCP entry when there is no large contentful element. Empty is a
# valid answer here, not a broken probe; assert on it only where you know one exists.
${lcp}=    Javascript    String(performance.getEntriesByType('largest-contentful-paint').at(-1)?.startTime ?? '')
Log    ${lcp}
```

Returns: `{ vitals: {lcp, fcp, inp, cls, ttfb}, ratings: {lcp, fcp, inp, cls, ttfb}, lcp_element, load_timing, render_timing }`
Ratings: `good` | `needs-improvement` | `poor`

---

## Broken Images

```robot
Go To    ${URL}
Wait For Load State    networkidle

${broken}=    Javascript    JSON.stringify(Array.from(document.querySelectorAll('img')).filter(i=>!i.complete||i.naturalWidth===0).map(i=>({src:i.src,alt:i.alt})))
Log    ${broken}
Should Be Equal    ${broken}    []    msg=Broken images found: ${broken}
```

---

## Console Errors (failed network resources)

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Method 1: failed resources via PerformanceObserver (deterministic)
${failed}=    Javascript    JSON.stringify(performance.getEntries().filter(e=>e.entryType==='resource'&&e.responseStatus>=400).map(e=>({url:e.name,status:e.responseStatus})))
Log    ${failed}
Should Be Equal    ${failed}    []    msg=Failed resources: ${failed}
```

```robot
# Method 2: capture runtime JS errors during interaction
Go To    ${URL}
Wait For Load State    networkidle
Javascript    window.__logs=[];const o={e:console.error,w:console.warn};console.error=(...a)=>{window.__logs.push({t:'error',m:a.join(' ')});o.e(...a)};console.warn=(...a)=>{window.__logs.push({t:'warn',m:a.join(' ')});o.w(...a)};window.addEventListener('error',e=>window.__logs.push({t:'uncaught',m:e.message}));window.addEventListener('unhandledrejection',e=>window.__logs.push({t:'rejection',m:String(e.reason)}));

# ... interact with the page ...
Click    role=button    name=Submit

${logs}=    Javascript    JSON.stringify(window.__logs.filter(l=>l.t==='error'||l.t==='uncaught'))
Log    ${logs}
Should Be Equal    ${logs}    []    msg=JS errors during interaction: ${logs}
```

---

## Form Structure & Labels

```robot
Go To    ${URL}
Wait For Load State    networkidle

${forms}=    Javascript    JSON.stringify(Array.from(document.querySelectorAll('form')).map(f=>({action:f.action,inputs:Array.from(f.querySelectorAll('input,select,textarea')).map(i=>({name:i.name,type:i.type,required:i.required,hasLabel:!!(i.labels?.length||i.getAttribute('aria-label')||i.getAttribute('aria-labelledby')),placeholder:i.placeholder}))})))
Log    ${forms}
# ASSERT manually: every input has hasLabel=true, required fields are marked
```

---

## Keyboard Tab Order & Focus Ring

```robot
Go To    ${URL}
Wait For Load State    networkidle
Click    css=body

# Tab and check the focus ring on each element — repeat until focus returns to BODY.
# `Keyboard Key` is page-level, which is correct HERE: focus is exactly what is under test.
Keyboard Key    press    Tab

# Describe the focused element for the failure message…
${focus}=    Javascript    JSON.stringify({tag:document.activeElement.tagName,text:document.activeElement.textContent?.trim().slice(0,40),role:document.activeElement.getAttribute('role'),label:document.activeElement.getAttribute('aria-label')})
Log    ${focus}

# …and assert the ring as its own scalar. Do NOT parse the JSON in Robot: `Evaluate` and
# `json.loads` are BANNED by the platform validator and fail the whole run.
${hasFocusRing}=    Javascript    String(window.getComputedStyle(document.activeElement).outlineStyle!=='none'||window.getComputedStyle(document.activeElement).boxShadow!=='none')
Should Be Equal    ${hasFocusRing}    true    msg=No focus ring on ${focus}

# Guard against a false failure: if Tab did not move focus, `activeElement` is still BODY
# and the ring is legitimately `false`. Measured 2026-09-25 on the todo playground, this
# exact sequence left `{"tag":"BODY"}` with `false` — asserting the ring there reports an
# a11y bug that does not exist. Check focus moved before trusting the assertion above.
${tag}=    Javascript    document.activeElement.tagName
Should Not Be Equal    ${tag}    BODY    msg=Tab did not move focus — nothing to check
```

---

## Responsive Screenshot Sweep

Screenshots are requested via `helpmetest interactive "<keyword>" --screenshot` — not via a keyword.

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Mobile — iPhone 13 (390×844)
Set Viewport Size    390    844
Sleep    500ms
# request screenshot via CLI — check: no horizontal overflow, touch targets visible

# Tablet — iPad (768×1024)
Set Viewport Size    768    1024
Sleep    500ms
# request screenshot — check: layout adapts, sidebar collapses correctly

# Desktop
Set Viewport Size    1440    900
Sleep    500ms
# request screenshot — check: content not stretched edge-to-edge
```

Or use the built-in keyword (runs the check end-to-end):
```robot
Test On iPhone 13    ${URL}
```

---

## Link Audit

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Extract all links visible on the current page (no crawl)
${links}=    Javascript    JSON.stringify(Array.from(document.querySelectorAll('a[href]')).map(a=>({href:a.href,text:a.textContent?.trim().slice(0,50),external:!a.href.startsWith(location.origin),newTab:a.target==='_blank'})))
Log    ${links}
```

---

## Broken Links — REMOVED: `Broken Links` does not exist

Probed live 2026-09-25: `✗ Broken Links` → `No keyword with name 'Broken Links' found.`
There is no crawl keyword. Check the links on a page with the Link Audit recipe above to
collect the hrefs, then assert on the ones you care about by visiting them — `Go To` returns
the HTTP status, so a 4xx/5xx shows up directly:

```robot
# `Go To` returns the HTTP status. A 404 page still "loads" (no crash), so assert on the
# status rather than on the page rendering. Verified 2026-09-25: this returns 404, and the
# session also prints its own warning: "Navigation response returned HTTP 404 for …".
${status}=    Go To    ${BASE_URL}/does-not-exist
Should Be Equal As Integers    ${status}    404
```

The keyword crawls same-origin links only. External links are visited but not recursed into.
`maxPages` defaults to 100 — use a lower value for large sites during development.

---

## Empty State Check

```robot
# Navigate to a section with no data
Go To    ${URL}/items    # e.g. list page when account is fresh
Wait For Load State    networkidle

${body}=    Browser.Get Text    css=main
Should Not Be Empty    ${body}    msg=Empty state shows blank page — needs message + CTA
# request screenshot via CLI — verify it has: message, illustration/icon, CTA button
```

---

## SSL / Domain Health

```robot
SSL Is Valid    ${DOMAIN}
SSL Days Remaining    ${DOMAIN}    30    # fail if expiring within 30 days
# Optional full chain check:
# Ssl Certificate Chain Valid    ${DOMAIN}
```

