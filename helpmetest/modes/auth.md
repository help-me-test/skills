<!-- llms-description: Save As / As session management — establish auth once and reuse it across tests. Also 2FA/TOTP and secrets. -->

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

> **Format note.** The `*** Settings ***` / `*** Test Cases ***` blocks below show the
> keyword sequence, not the submission format. `test create --content` takes bare keywords
> — see `modes/shared.md` §3f. A `Suite Setup` keyword becomes the first line of the body;
> `As  <StateName>` is unchanged.

```text
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

```text
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

**The CLI and the keyword do not take the same shape, and nothing else says so.** Measured
2026-09-26:

| surface | form |
|---|---|
| CLI | `helpmetest secret set <name> <value>` — two arguments, and `secret get` has **no** `--env`/`--type` flag |
| keyword | `Get Secret  <env>  <type>  <name>` — exactly 3; `Set Secret` takes 4 to 5 |

So a secret stored from the CLI has no env or type to give, while the keyword demands
both. The error example below shows the pairing the platform itself uses —
`Get Secret  default  secret  <name>` — i.e. env `default`, type `secret`. **I could not
confirm that round trip end to end**: `Get Secret` resolves inside the cluster and the app
service it calls is currently unreachable from the test VM (the `ConnectTimeout` below is
that, and it is an open infrastructure issue, not a wrong name). Treat the mapping as the
documented intent, and verify it once the service answers.

**Both `Get Secret` and `Get 2FA Code` resolve server-side, inside the cluster.** Verified
2026-09-25: a positional argument maps to the secret *name*, and the VM calls
`/api/internal/secret?company=…&env=…&type=…&name=…` on the app service. Measured arities:
`Get Secret` takes exactly 3 (`env`, `type`, `name`); `Get 2FA Code` requires `account` or
`key` and accepts the account positionally.

**A `ConnectTimeout` from these keywords is infrastructure, not a wrong secret name:**

```
✗ Get Secret  default  secret  <name>
  ConnectTimeout: HTTPConnectionPool(host='app.slava.svc.cluster.local', port=3000):
  Max retries exceeded with url: /api/internal/secret?…
```

That is the test VM failing to reach the app service, so **every** secret and OTP lookup
fails the same way regardless of the name you pass. Observed on slava 2026-09-25, where the
identical error was also failing `Terminal CLI Smoke`, `Secrets Regression`,
`Small Stress Latency Probe` and `Webhook Notification Test`. Do not debug the secret; check
whether the app service is reachable from the VM first — a missing secret gives a different,
immediate error, not a 10s timeout.

**Still failing as of 2026-09-26.** Re-measured rather than inherited from the line above:
`Get Secret  default  secret  zz-nonexistent` → `ConnectTimeout` after **10.038s**, same
host and port. Re-run that one command before trusting this paragraph; if it returns
anything but a timeout, the outage is over and this note is what is stale.

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
- **Saved states persist across runs, and across the whole company.** This line used to say
  "session names are scoped to the test run — they don't persist between runs", which is
  false and contradicted every other mode's "`Save As` once, `As <State>` in every test".
  Measured 2026-09-26: `Save As  zzstateprobe` in one CLI invocation, then a **separate**
  invocation → `✓ As  zzstateprobe → Restored state 'zzstateprobe' | cookies=1`. The
  not-found error also lists the company's existing long-lived states (`Admin`,
  `Automation User`, `BlogState`, …), which is what persistence looks like.
- Because they are company-wide, a `Save As <name>` **overwrites** anyone else's state of
  that name. Namespace yours.
- `Forget As` deletes one: `✓ Forget As  zzstateprobe → Deleted state 'zzstateprobe'`, and
  a subsequent `As` then fails with `No state found for name …`. Use it to clean up a
  probe state you created; do not use it on a state a test depends on.
