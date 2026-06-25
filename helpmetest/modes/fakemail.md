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
${email}=    Create Fake Email    prefix=signup   # with a readable prefix

${msg}=      Get Email    ${email}                # wait for an email to arrive (polls up to 60s)
${msg}=      Get Email    ${email}    subject=Welcome    # filter by subject
${msg}=      Get Email    ${email}    timeout=120        # custom timeout
```

### Verification codes and links

```robotframework
${code}=    Get Email Verification Code    ${email}              # extract 4-8 digit code from body
${code}=    Get Email Verification Code    ${email}    length=6  # exact digit count

Enter Verification Code    ${email}    id=otp_field              # extract + type code into field

${url}=    Get Email Link    ${email}                            # extract first link from body
${url}=    Get Email Link    ${email}    contains=verify         # link containing keyword
```

### Attachments

```robotframework
${path}=    Download Email Attachment    ${email}    filename=invoice.pdf
${path}=    Download Email Attachment    ${email}    index=0    # first attachment
```

### Cleanup (always in Suite Teardown)

```robotframework
Cleanup Emails    ${email}           # delete one inbox
Cleanup Emails    ${email1}    ${email2}    # delete multiple
```

---

## Example: signup email verification

```robotframework
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

1. Orient: `helpmetest status` + `helpmetest artifact list`
2. Identify the email flow to test (signup, password reset, magic link, etc.)
3. Write the test — always put `Cleanup Emails` in Suite Teardown
4. `helpmetest test create --id <id> --name "<name>" --file <file>` to push it
5. `helpmetest test run --id <id>` to execute
6. Report pass/fail; if `Get Email` times out, check the app actually sent the email

---

## Notes

- `Get Email` polls until the email arrives — default timeout 60s, increase for slow mailers
- `Enter Verification Code` combines `Get Email` + code extraction + `Fill Text` in one keyword
- Always use `Cleanup Emails` in Suite Teardown — leaked inboxes accumulate across runs
- For auth flows that send a verification email, chain: `auth` → `fakemail`
