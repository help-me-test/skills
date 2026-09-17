# HelpMeTest Auth Mode

Set up and reuse browser session state in Robot Framework tests using the `HelpMeTest` library. Establish auth once in Suite Setup, reuse with `As` in every test case — never re-login inside individual tests.

---

## Trigger

```
/helpmetest auth          # set up auth pattern for current project
/helpmetest auth <task>   # e.g. "add 2FA to the login test"
```

---

## Core pattern: Save As / As

**Rule: every test suite establishes auth state once in Suite Setup, then reuses it with `As`. Never log in inside individual test cases.**

### Keywords

| Keyword | Alias | Args | What it does |
|---------|-------|------|-------------|
| `Save As` | `Save User` | `name` | Save current browser session (cookies, storage) under `name` |
| `As` | `User` | `name` | Restore a saved session — all subsequent keywords run authenticated |
| `Forget As` | `Delete User` | `name` | Delete a saved session |

### Setup pattern

```robotframework
*** Settings ***
Suite Setup    Authenticate

*** Keywords ***
Authenticate
    Go To    https://app.example.com/login
    Fill Text    id=email    admin@example.com
    Fill Text    id=password    secret
    Click    id=login-button
    Wait For Elements State    id=dashboard    visible
    Save As    Admin

*** Test Cases ***
Admin can see settings
    As    Admin
    Go To    https://app.example.com/settings
    Page Should Contain    Settings

Admin can create a user
    As    Admin
    Click    id=new-user-button
    ...
```

### Multi-user pattern

```robotframework
Suite Setup    Authenticate All Users

*** Keywords ***
Authenticate All Users
    Go To    ${BASE_URL}/login
    Fill Text    id=email    admin@example.com
    Fill Text    id=password    ${ADMIN_PASSWORD}
    Click    id=login
    Save As    Admin

    Go To    ${BASE_URL}/login
    Fill Text    id=email    user@example.com
    Fill Text    id=password    ${USER_PASSWORD}
    Click    id=login
    Save As    RegularUser

*** Test Cases ***
Admin sees all users, regular user does not
    As    Admin
    Go To    ${BASE_URL}/users
    Page Should Contain    user@example.com

    As    RegularUser
    Go To    ${BASE_URL}/users
    Page Should Contain    403
```

---

## 2FA / TOTP

```robotframework
Get 2FA Code    account_name          # by account name (looks up stored TOTP key)
Get 2FA Code    key=BASE32SECRETKEY   # by raw TOTP key
```

Use in login flow:

```robotframework
Authenticate With 2FA
    Go To    ${BASE_URL}/login
    Fill Text    id=email    admin@example.com
    Fill Text    id=password    secret
    Click    id=login
    ${code}=    Get 2FA Code    myapp-admin
    Fill Text    id=totp    ${code}
    Click    id=verify
    Save As    Admin2FA
```

---

## Passkey

Removed 2026-09-12: the `Passkey` keyword's own docstring example was already broken (`No keyword with name 'Setup Passkey Authenticator' found` — it called 5 keywords that never existed anywhere in the library). No working passkey/WebAuthn support exists in HelpMeTest today. If you need it, implement real CDP virtual-authenticator support (`WebAuthn.enable`/`WebAuthn.addVirtualAuthenticator` via Playwright's CDP session) rather than assuming this keyword works.

---

## Secrets (for credentials in tests)

```robotframework
Set Secret    production    password    db-password    s3cr3t
${pw}=    Get Secret    production    password    db-password
```

Use this instead of hardcoding credentials in test files.

---

## Workflow

1. Orient: `helpmetest status` + `helpmetest artifact list` — check existing tests and features
2. Write the test following the Save As / As pattern above
3. `helpmetest test create --id <id> --name "<name>" --file <file>` to push it
   - If `test create` fails with a validation error: read the error, fix the specific issue, retry once
   - If it fails again: check comment structure — every 1-2 keywords needs a section comment
   - Max 3 attempts total — do not loop indefinitely on the same error
4. `helpmetest test run --id <id>` to execute and confirm it passes
5. Report what session names are now saved and what tests protect them

---

## Notes

- `As` restores the exact browser state (cookies, localStorage, sessionStorage) — the app sees the user as already logged in, no page load or redirect needed.
- `Save As` captures whatever is in the browser at the moment — call it only after the login flow is complete.
- Session names are scoped to the test run — they don't persist between runs.
- `Forget As` is rarely needed; sessions auto-expire with the run.
