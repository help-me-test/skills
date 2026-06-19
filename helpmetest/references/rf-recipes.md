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
Evaluate    (()=>{const s=document.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js';document.head.appendChild(s);})()
Sleep    3s    # wait for script load

# Step 2: run audit
${result}=    Evaluate    axe.run().then(r=>JSON.stringify({violations:r.violations.map(v=>({id:v.id,impact:v.impact,desc:v.description,nodes:v.nodes.length,help:v.helpUrl})),passes:r.passes.length,incomplete:r.incomplete.length}))
Log    ${result}
${parsed}=    Evaluate    json.loads("""${result}""")    json

# ASSERT: no critical/serious violations
${violations}=    Set Variable    ${parsed}[violations]
FOR    ${v}    IN    @{violations}
    Should Not Be Equal    ${v}[impact]    critical    msg=axe critical: ${v}[id] — ${v}[desc]
    Should Not Be Equal    ${v}[impact]    serious    msg=axe serious: ${v}[id] — ${v}[desc]
END
```

Thresholds: `critical`/`serious` = must fix. `moderate`/`minor` = should fix.

---

## Performance Metrics

```robot
Go To    ${URL}
Wait For Load State    networkidle

${metrics}=    Evaluate    (()=>{const nav=performance.getEntriesByType('navigation')[0];const paint=performance.getEntriesByType('paint');return JSON.stringify({fcp:Math.round(paint.find(p=>p.name==='first-contentful-paint')?.startTime||0),domInteractive:Math.round(nav?.domInteractive||0),loadComplete:Math.round(nav?.loadEventEnd||0),transferSize:nav?.transferSize||0});})()
Log    ${metrics}
${m}=    Evaluate    json.loads("""${metrics}""")    json

# Doherty Threshold: DOM interactive < 400ms feels instant
# Web Vitals: FCP < 1800ms = good, < 3000ms = needs work
Run Keyword If    ${m}[fcp] > 3000    Log    WARN: FCP ${m}[fcp]ms exceeds 3s threshold    WARN
Run Keyword If    ${m}[domInteractive] > 400    Log    WARN: DOM interactive ${m}[domInteractive]ms exceeds 400ms    WARN
```

---

## Core Web Vitals (Analyze Web Vitals)

Requires OpenReplay recording to be active (started before navigation). Returns LCP, FCP, INP, CLS, TTFB with Lighthouse-style ratings.

```robot
# Start recording before navigating — Analyze Web Vitals reads OpenReplay events
Go To    ${URL}
Wait For Load State    networkidle

# Interact with the page to trigger INP/CLS measurements
Scroll By    0    500
Sleep    2s    # let vitals accumulate

${vitals}=    Analyze Web Vitals
Log    ${vitals}

# ASSERT: Core Web Vitals are in "good" range (Lighthouse thresholds)
# LCP < 2500ms = good, FCP < 1800ms = good, CLS < 0.1 = good
# Returns None if no OpenReplay data captured yet
Run Keyword If    '${vitals}' != 'None'    Run Keywords
...    Should Not Be Equal    ${vitals}[ratings][lcp]    poor    msg=LCP is poor: ${vitals}[vitals][lcp]ms
...    AND    Should Not Be Equal    ${vitals}[ratings][fcp]    poor    msg=FCP is poor: ${vitals}[vitals][fcp]ms
...    AND    Should Not Be Equal    ${vitals}[ratings][cls]    poor    msg=CLS is poor: ${vitals}[vitals][cls]
```

Returns: `{ vitals: {lcp, fcp, inp, cls, ttfb}, ratings: {lcp, fcp, inp, cls, ttfb}, lcp_element, load_timing, render_timing }`
Ratings: `good` | `needs-improvement` | `poor`

---

## Broken Images

```robot
Go To    ${URL}
Wait For Load State    networkidle

${broken}=    Evaluate    JSON.stringify(Array.from(document.querySelectorAll('img')).filter(i=>!i.complete||i.naturalWidth===0).map(i=>({src:i.src,alt:i.alt})))
Log    ${broken}
Should Be Equal    ${broken}    []    msg=Broken images found: ${broken}
```

---

## Console Errors (failed network resources)

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Method 1: failed resources via PerformanceObserver (deterministic)
${failed}=    Evaluate    JSON.stringify(performance.getEntries().filter(e=>e.entryType==='resource'&&e.responseStatus>=400).map(e=>({url:e.name,status:e.responseStatus})))
Log    ${failed}
Should Be Equal    ${failed}    []    msg=Failed resources: ${failed}
```

```robot
# Method 2: capture runtime JS errors during interaction
Go To    ${URL}
Wait For Load State    networkidle
Evaluate    window.__logs=[];const o={e:console.error,w:console.warn};console.error=(...a)=>{window.__logs.push({t:'error',m:a.join(' ')});o.e(...a)};console.warn=(...a)=>{window.__logs.push({t:'warn',m:a.join(' ')});o.w(...a)};window.addEventListener('error',e=>window.__logs.push({t:'uncaught',m:e.message}));window.addEventListener('unhandledrejection',e=>window.__logs.push({t:'rejection',m:String(e.reason)}));

# ... interact with the page ...
Click    role=button    name=Submit

${logs}=    Evaluate    JSON.stringify(window.__logs.filter(l=>l.t==='error'||l.t==='uncaught'))
Log    ${logs}
Should Be Equal    ${logs}    []    msg=JS errors during interaction: ${logs}
```

---

## Form Structure & Labels

```robot
Go To    ${URL}
Wait For Load State    networkidle

${forms}=    Evaluate    JSON.stringify(Array.from(document.querySelectorAll('form')).map(f=>({action:f.action,inputs:Array.from(f.querySelectorAll('input,select,textarea')).map(i=>({name:i.name,type:i.type,required:i.required,hasLabel:!!(i.labels?.length||i.getAttribute('aria-label')||i.getAttribute('aria-labelledby')),placeholder:i.placeholder}))})))
Log    ${forms}
# ASSERT manually: every input has hasLabel=true, required fields are marked
```

---

## Keyboard Tab Order & Focus Ring

```robot
Go To    ${URL}
Wait For Load State    networkidle
Click    css=body

# Tab and check focus ring on each element — repeat until back to BODY
Keyboard Key    press    Tab
${focus}=    Evaluate    (()=>{const el=document.activeElement;const s=window.getComputedStyle(el);return JSON.stringify({tag:el.tagName,text:el.textContent?.trim().slice(0,40),role:el.getAttribute('role'),label:el.getAttribute('aria-label'),hasFocusRing:s.outlineStyle!=='none'||s.boxShadow!=='none'});})()
Log    ${focus}
${f}=    Evaluate    json.loads("""${focus}""")    json
Should Be True    ${f}[hasFocusRing]    msg=No focus ring on ${f}[tag] "${f}[text]"
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
${links}=    Evaluate    JSON.stringify(Array.from(document.querySelectorAll('a[href]')).map(a=>({href:a.href,text:a.textContent?.trim().slice(0,50),external:!a.href.startsWith(location.origin),newTab:a.target==='_blank'})))
Log    ${links}
```

---

## Broken Links (site crawl)

Crawls the site starting from a URL, visits all internal pages, and returns links that returned 4xx/5xx or failed to load.

```robot
# Crawl entire site for broken links — visits up to maxPages pages
${broken}=    Broken Links    ${BASE_URL}    maxPages=50
Log    ${broken}
# ${broken} is a dict: { url: { status, referrer } } for every broken link found
# ASSERT: no broken links
Should Be Empty    ${broken}    msg=Broken links found: ${broken}
```

The keyword crawls same-origin links only. External links are visited but not recursed into.
`maxPages` defaults to 100 — use a lower value for large sites during development.

---

## Empty State Check

```robot
# Navigate to a section with no data
Go To    ${URL}/items    # e.g. list page when account is fresh
Wait For Load State    networkidle

${body}=    Get Text    css=main
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

