<!-- llms-description: Disposable email addresses for signup, verification codes, password reset and attachments. -->

# HelpMeTest FakeMail Mode

Test email flows using the `FakeMail` library — disposable email addresses, verification codes, magic links, attachments. Always clean up after tests.

---

## Trigger

```
/helpmetest fakemail          # test email flows
/helpmetest email <task>      # alias — e.g. "test email verification", "check the signup email"
```

Triggers on: email verification, verification code, inbox, email link, disposable email, fake email.

---

## Keywords

### Create and receive

```robotframework
${email}=    Create Fake Email                    # generate a unique disposable address

${msg}=      Get Email    ${email}                # wait for an email to arrive (polls up to 60s)
${msg}=      Get Email    ${email}    subject=Welcome    # filter by subject
${msg}=      Get Email    ${email}    timeout=120        # custom timeout
```

**`Create Fake Email` takes no arguments.** This section used to show
`Create Fake Email    prefix=signup`; that fails with
`Keyword 'FakeMail.Create Fake Email' expected 0 arguments, got 1` (measured 2026-09-25).
The generated address already carries a readable random prefix —
`technology1af81b.him@helpmetest.helpmetest.com` from a real call.

### Verification codes and links

```robotframework
${code}=    Get Email Verification Code    ${email}              # extract 4-8 digit code from body
${code}=    Get Email Verification Code    ${email}    length=6  # exact digit count

Enter Verification Code    ${email}    id=otp_field              # extract + type code into field

${url}=    Get Email Link    ${email}                            # extract first link from body
${url}=    Get Email Link    ${email}    contains=verify         # link containing keyword
```

Measured arities, 2026-09-25: `Get Email` 1-8, `Get Email Verification Code` 1-7,
`Get Email Link` 1-4, `Enter Verification Code` 2-5. All exist.

### Attachments — no keyword exists

This section used to document `Download Email Attachment`. **There is no such keyword** —
`No keyword with name 'Download Email Attachment' found.` (measured 2026-09-25), and the
FakeMail library exposes nothing attachment-related at all. Read the message with
`Get Email` and assert on what it returns; if you need an attachment byte-for-byte, that
capability is not in this library today.

### Other FakeMail keywords, undocumented until now

```robotframework
Create Email And Fill    input[name=email]    # generate an address AND type it into a field
Send Test Email          ${email}    Subject  # send a message to a disposable inbox
Delete Email             ${email}             # delete one inbox
```

### Cleanup (always at the end of the test body)

```robotframework
Cleanup Emails                       # no arguments — releases this session's inboxes
```

**`Cleanup Emails` takes no arguments either.** `Cleanup Emails    ${email}` fails with
`expected 0 arguments, got 1`. To delete one specific inbox, use `Delete Email  ${email}`.

---

## Example: signup email verification

> **Format note.** The block below shows the keyword sequence. `test create --content`
> takes bare keywords — no `*** Settings ***`, no `Library` line — see
> `modes/shared.md` §3f. `Suite Teardown  Cleanup Emails` has no bare equivalent: put
> `Cleanup Emails` (no arguments) as the last line of the body instead, so the inboxes are
> still released. The block below also shows `Create Fake Email  prefix=signup`, which does
> not work — see above.

```text
*** Settings ***
Library    FakeMail
Suite Teardown    Cleanup Emails    ${EMAIL}

*** Variables ***
${EMAIL}    ${EMPTY}

*** Test Cases ***
User receives verification email and activates account
    # Create a disposable inbox
    ${EMAIL}=    Create Fake Email    prefix=signup
    Set Suite Variable    ${EMAIL}

    # Trigger signup with the fake address
    Go To    https://app.example.com/register
    Fill Text    id=email    ${EMAIL}
    Click    id=register-button

    # Wait for verification email and extract the code
    Enter Verification Code    ${EMAIL}    id=verification-code
    Click    id=verify-button

    # Confirm account is activated
    Wait For Elements State    id=dashboard    visible
```

---

## Workflow

1. Orient: `helpmetest status` + `helpmetest artifact list --tags "project:<slug>"`
2. Identify the email flow to test (signup, password reset, magic link, etc.)
3. Write the test — always end the body with `Cleanup Emails` (no arguments)
4. `helpmetest test create --id <id> --name "<name>" --file <file>` to push it
5. `helpmetest test run --id <id>` to execute
6. Report pass/fail; if `Get Email` times out, check the app actually sent the email

---

## Notes

- `Get Email` polls until the email arrives — default timeout 60s, increase for slow mailers
- `Enter Verification Code` combines `Get Email` + code extraction + `Fill Text` in one keyword
- Always end the body with `Cleanup Emails` — no arguments; leaked inboxes accumulate across runs. `Delete Email  ${email}` removes one specific inbox.
- For auth flows that send a verification email, chain: `auth` → `fakemail`
