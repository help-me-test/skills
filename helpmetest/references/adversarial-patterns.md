# Adversarial Test Patterns (Robot Framework)

Use these patterns to try to break features. Apply them to every interactive element you test.
The goal is to find bugs, not confirm things work.

---

## Forms — try to break them

```robot
# Empty submission
Take Screenshot    before-empty-submit.png
Click    css=button[type="submit"]
Take Screenshot    after-empty-submit.png
# ASSERT: error messages appeared, form not submitted

# Long input (500+ chars)
${long}=    Evaluate    'a' * 500
Fill Text    css=#name    ${long}
Take Screenshot    long-input.png
# ASSERT: layout not broken, text truncated or scrolled, no crash

# Special characters / XSS
Fill Text    css=#name    <script>alert('xss')</script>
Fill Text    css=#email    '; DROP TABLE users;--
Click    css=button[type="submit"]
${body}=    Get Text    body
Should Not Contain    ${body}    <script>
Take Screenshot    xss-attempt.png
# ASSERT: input sanitized, no raw HTML rendered

# Rapid double-submit
Click    css=button[type="submit"]
Click    css=button[type="submit"]
Take Screenshot    double-submit.png
# ASSERT: only one submission processed (no duplicate toast, no duplicate record)
```

---

## Modals — test the full lifecycle

```robot
# Open
Take Screenshot    before-modal.png
Click    css=[data-testid="open-modal"]    # or role=button name="..."
Wait For Elements State    role=dialog    visible
Take Screenshot    after-modal-open.png
# ASSERT: dialog role visible in DOM

# Escape to close
Keyboard Key    press    Escape
Wait For Elements State    role=dialog    hidden
Take Screenshot    after-escape.png
# ASSERT: dialog gone

# Click outside to close (if expected)
Click    css=[data-testid="open-modal"]
Wait For Elements State    role=dialog    visible
Click    css=.modal-backdrop    # or click at coordinates outside dialog
Take Screenshot    after-click-outside.png
# ASSERT: dialog dismissed

# Re-open → cancel
Click    css=[data-testid="open-modal"]
Wait For Elements State    role=dialog    visible
Click    role=button    name=Cancel
Wait For Elements State    role=dialog    hidden
# ASSERT: dialog gone, no side effect

# Re-open → confirm
Click    css=[data-testid="open-modal"]
Wait For Elements State    role=dialog    visible
Click    role=button    name=Confirm
Wait For Elements State    role=dialog    hidden
Take Screenshot    after-confirm.png
# ASSERT: dialog gone AND side effect occurred (item deleted, action taken, etc.)
```

---

## Navigation — verify routing works

```robot
${url_before}=    Get Url
Take Screenshot    before-nav.png

Click    role=link    name=Dashboard
Wait For Load State    networkidle
${url_after}=    Get Url
Should Not Be Equal    ${url_before}    ${url_after}
Take Screenshot    after-nav.png
# ASSERT: URL changed, page content matches destination

# Back button
Go Back
${url_back}=    Get Url
Should Be Equal    ${url_back}    ${url_before}
Take Screenshot    after-back.png
# ASSERT: back to original URL, content matches
```

---

## Error states — find missing ones

```robot
# Empty list state
Go To    ${BASE_URL}/items
Wait For Load State    networkidle
Take Screenshot    empty-list.png
${body}=    Get Text    css=main
# ASSERT: there is a designed message + CTA, not blank space

# 404 page
Go To    ${BASE_URL}/does-not-exist-xyz
Wait For Load State    networkidle
Take Screenshot    404-page.png
${title}=    Get Title
# ASSERT: custom 404 page, not blank or nginx default

# Error recovery — input preserved after failed submit
Fill Text    css=#email    not-an-email
Click    css=button[type="submit"]
${val}=    Get Property    css=#email    value
Should Be Equal    ${val}    not-an-email
# ASSERT: user input is preserved, not cleared on error
```

---

## Keyboard accessibility — without a mouse

```robot
# Focus the page body first
Click    css=body

# Tab once and check what's focused
Keyboard Key    press    Tab
${focused}=    Evaluate    JSON.stringify({tag:document.activeElement?.tagName,text:document.activeElement?.textContent?.trim().slice(0,40),role:document.activeElement?.getAttribute('role'),hasFocusRing:(()=>{const s=window.getComputedStyle(document.activeElement);return s.outlineStyle!=='none'||s.boxShadow!=='none';})()})
Log    ${focused}
Take Screenshot    keyboard-focus-1.png
# ASSERT: hasFocusRing=true, element is interactive (not BODY, not DIV)

# Tab through all interactive elements and check focus ring is visible each time
# Repeat Keyboard Key / Evaluate until activeElement.tagName === 'BODY' again

# Activate focused button via keyboard
Keyboard Key    press    Enter
Take Screenshot    keyboard-enter-action.png
# ASSERT: same action happened as a mouse click would produce
```

---

## Persistence — survives reload

```robot
# Set some state (e.g. add item, change setting)
Fill Text    css=.new-todo    Buy milk
Keyboard Key    press    Enter
${count_before}=    Get Element Count    css=.todo-item

# Reload
Reload
Wait For Load State    networkidle

${count_after}=    Get Element Count    css=.todo-item
Should Be Equal As Integers    ${count_before}    ${count_after}
# ASSERT: data persisted across reload
```

---

## Back/forward navigation

```robot
Go To    ${BASE_URL}/page-a
Wait For Load State    networkidle
Click    role=link    name=Page B
Wait For Load State    networkidle

Go Back
Wait For Load State    networkidle
${url}=    Get Url
Should Contain    ${url}    page-a
Take Screenshot    back-nav.png
# ASSERT: correct page, no blank screen, no JS error

Go Forward
Wait For Load State    networkidle
Take Screenshot    forward-nav.png
# ASSERT: returned to Page B correctly
```

---

## Copy quality scan

```robot
${hits}=    Evaluate    (()=>{const t=document.body.innerText;const bad=['undefined','null','[object Object]','TODO','lorem ipsum','NaN','{{','}}'];const found=bad.filter(p=>t.toLowerCase().includes(p.toLowerCase()));return found.length?JSON.stringify(found):'clean';})()
Should Be Equal    ${hits}    clean
# ASSERT: no leaked debug values or placeholder text visible to users
```
