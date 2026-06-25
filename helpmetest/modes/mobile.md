# HelpMeTest Mobile Mode

Test Android and iOS apps on real devices via the `Mobile` library (appium-device-farm). Write, push, and run mobile tests using Robot Framework keywords.

---

## Trigger

```
/helpmetest mobile          # write mobile tests for the current project
/helpmetest mobile <task>   # e.g. "debug my android app", "test iOS login flow"
```

Triggers on: android, ios, apk, ipa, mobile app, phone, device farm, Open App, debug my app.

---

## Starting a session

```robotframework
Open App    path/to/app.apk          # Android — inferred from .apk extension
Open App    path/to/app.ipa          # iOS — inferred from .ipa extension
Open Android    path/to/app.apk      # explicit Android
Open iOS        path/to/app.ipa      # explicit iOS
```

The library proxies all AppiumLibrary keywords via `__getattr__` — use any AppiumLibrary keyword after `Open App`.

---

## Interaction keywords

```robotframework
Mobile Tap                  locator
Mobile Input Text           locator    text
Mobile Wait For Element     locator
Mobile Wait For Element     locator    timeout=10s
Mobile Swipe                start_locator    end_locator
Mobile Long Press           locator
Mobile Scroll To Element    locator
```

---

## Example test

```robotframework
*** Settings ***
Library    Mobile

*** Test Cases ***
User can log in on Android
    # Open the app on a real Android device
    Open App    builds/myapp.apk

    # Enter credentials and submit
    Mobile Wait For Element    id=email_field
    Mobile Input Text    id=email_field    test@example.com
    Mobile Input Text    id=password_field    secret123
    Mobile Tap    id=login_button

    # Verify dashboard is visible after login
    Mobile Wait For Element    id=dashboard    timeout=15s
```

---

## Workflow

1. Orient: `helpmetest status` + `helpmetest artifact list`
2. Identify the app binary path (`.apk` for Android, `.ipa` for iOS)
3. Write the test using `Open App` / `Open Android` / `Open iOS` + Mobile keywords
4. `helpmetest test create --id <id> --name "<name>" --file <file>` to push it
5. `helpmetest test run --id <id>` to run on a real device
6. If test fails: use `interactive` mode to debug step by step, then fix and re-run

---

## Notes

- `Mobile` is separate from `Desktop` — never use `Mac Start` / `Linux Start` here
- Device is allocated from the farm automatically — no device selection needed
- AppiumLibrary keywords work directly after `Open App` (proxied transparently)
- Teardown is automatic — session closes when the test ends
