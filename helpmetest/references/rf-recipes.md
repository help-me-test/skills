# Robot Framework Recipes for Deterministic UI Checks

Copy-paste keyword sequences for checks that produce structured data, not judgment calls.
Use these as the strongest form of assertion — they pass or fail on numbers, not screenshots.

Load this file when you need: axe-core, console errors, broken images, form labels, performance, responsive sweep, link audit.

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

```robot
Go To    ${URL}
Wait For Load State    networkidle

# Mobile — iPhone 13 (390×844)
Set Viewport Size    390    844
Sleep    500ms
Take Screenshot    mobile-${name}.png

# Tablet — iPad (768×1024)
Set Viewport Size    768    1024
Sleep    500ms
Take Screenshot    tablet-${name}.png

# Desktop
Set Viewport Size    1440    900
Sleep    500ms
Take Screenshot    desktop-${name}.png

# After screenshots, read each with Read tool and check:
# Mobile: hamburger menu present? No horizontal overflow?
# Tablet: layout adapts? Sidebar collapses?
# Desktop: content not stretched edge-to-edge?
```

Or use the built-in keyword:
```robot
Test On iPhone 13    ${URL}
```

---

## Link Audit

```robot
Go To    ${URL}
Wait For Load State    networkidle

${links}=    Evaluate    JSON.stringify(Array.from(document.querySelectorAll('a[href]')).map(a=>({href:a.href,text:a.textContent?.trim().slice(0,50),external:!a.href.startsWith(location.origin),newTab:a.target==='_blank'})))
Log    ${links}
# Then use Broken Links keyword for automated check:
Broken Links    ${URL}
```

---

## Empty State Check

```robot
# Navigate to a section with no data
Go To    ${URL}/items    # e.g. list page when account is fresh
Wait For Load State    networkidle
Take Screenshot    empty-state.png

${body}=    Get Text    css=main
Should Not Be Empty    ${body}    msg=Empty state shows blank page — needs message + CTA
# Manually verify screenshot has: message, illustration/icon, CTA button
```

---

## SSL / Domain Health

```robot
SSL Is Valid    ${DOMAIN}
SSL Days Remaining    ${DOMAIN}    30    # fail if expiring within 30 days
# Optional full chain check:
# Ssl Certificate Chain Valid    ${DOMAIN}
```

---

## Web Vitals (via Analyze Web Vitals keyword)

```robot
Go To    ${URL}
Wait For Load State    networkidle
${vitals}=    Analyze Web Vitals
Log    ${vitals}
# Check FCP, LCP, CLS, TBT against thresholds in the result
```
