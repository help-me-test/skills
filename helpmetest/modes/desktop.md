# HelpMeTest Desktop Mode

Test Mac and Linux native desktop apps using the `Desktop` library (Appium mac2 / atspi2 drivers). **Desktop = Mac + Linux only** — for Android/iOS use `mobile` mode.

---

## Trigger

```
/helpmetest desktop          # write desktop app tests
/helpmetest desktop <task>   # e.g. "test my Mac app", "automate the Electron app"
```

Triggers on: mac app, macos app, desktop app, Electron, Mac Start, Linux app, Linux Start.

---

## Starting a session

```robotframework
Mac Start      com.apple.Safari          # Mac — by bundle ID
Mac Start      /Applications/MyApp.app  # Mac — by path
Linux Start    /usr/bin/myapp            # Linux — by executable path
```

Teardown is automatic via listener — no explicit close needed.

---

## Interaction keywords

All AppiumLibrary keywords are available after `Mac Start` / `Linux Start`:

```robotframework
Type Desktop Text    text\n           # type text (use \n for Enter)
Click Element        locator
Input Text           locator    text
Wait Until Element Is Visible    locator
Get Text             locator
Element Should Be Visible        locator
```

---

## Example test

```robotframework
*** Settings ***
Library    Desktop

*** Test Cases ***
Safari opens and navigates to example.com
    # Launch Safari via Mac automation driver
    Mac Start    com.apple.Safari

    # Navigate to the URL
    Type Desktop Text    https://example.com\n

    # Verify the page loaded
    Wait Until Element Is Visible    xpath=//AXStaticText[@AXValue='Example Domain']
```

---

## Workflow

1. Orient: `helpmetest status` + `helpmetest artifact list`
2. Identify the app bundle ID (Mac) or executable path (Linux)
3. Write the test using `Mac Start` / `Linux Start` + AppiumLibrary keywords
4. `helpmetest test create --id <id> --name "<name>" --file <file>` to push it
5. `helpmetest test run --id <id>` to execute
   - Note: test run requires a Mac/Linux environment with the app installed; a 503 from the service means the desktop driver isn't available in this environment — the test is still valid
6. Report result or note service availability

---

## Notes

- Mac driver: `mac2` (Appium mac2 driver) — requires macOS + Appium server
- Linux driver: `atspi2` (AT-SPI2 accessibility bridge) — requires Linux + AT-SPI2
- Never use `Open App`, `Mobile Tap`, or other Mobile keywords here — those belong in `mobile` mode
- For apps with login flows, chain with `auth` mode: `desktop` → `auth`
