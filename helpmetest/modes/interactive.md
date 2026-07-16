> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

---

# Interactive — browser as a console

Drive a real cloud browser one command at a time with Robot Framework keywords. Use it to explore pages, find working selectors, debug a failing test step by step, or verify something without running a full suite.

**This is the step before test writing.** When you have a working sequence, copy it into `helpmetest test create`.

---

## CLI syntax

```bash
helpmetest interactive "Go To  https://example.com"
helpmetest interactive "Click  [data-testid=submit-btn]"
helpmetest interactive "Fill Text  input[name=email]  user@example.com"
helpmetest interactive "Exit"
```

**Two spaces separate keyword from arguments.** `"Go To  https://..."` not `"Go To https://..."`. One space silently breaks it.

### Batching multiple commands in one call

Pass multiple commands as **separate quoted arguments** — the CLI joins them with `\n` automatically:

```bash
helpmetest interactive "Fill Text  input[name=email]  user@example.com" "Fill Text  input[name=password]  secret" "Click  button[type=submit]"
```

You can also use `\n` inside a single string:

```bash
helpmetest interactive $'Fill Text  input[name=email]  user@example.com\nFill Text  input[name=password]  secret\nClick  button[type=submit]'
```

When a command in a batch fails, subsequent commands are skipped (shown as `⊘` in output). Batch when you're confident the whole sequence works. Go step by step when exploring or debugging.

### Options

| Flag | Effect |
|---|---|
| `--screenshot` | Capture screenshot after the command (appends `Take Screenshot` automatically) |
| `--open` | Open the live session URL in your browser immediately — watch clicks happen |
| `--session <runId>` | Resume a specific named session (bypasses auto-resume) |
| `--timeout <ms>` | Per-command timeout (default 5000ms) |
| `--dom-diff` | Show DOM mutations (adds/removes/attribute/text changes) that happened during the command — sourced from the session's existing rrweb recording, added as a "DOM Diff" output section |
| `--debug` | Full diagnostics: OpenReplay events, perf metrics, network timings |
| `--json` | Output as JSON (for scripting/agents) |


### Watching the session live

The `--open` flag opens the live session URL in your browser so you can watch clicks happen in real time. Whether it's on by default is controlled by `autoOpenSession` in the project config.

At the start of an interactive session, inform the user of this capability — don't ask, just mention it:

> "You can watch this session live in your browser as I run commands. Want me to enable that? I'll set `autoOpenSession` in your project config."

If they say yes, run:
```bash
helpmetest config set autoOpenSession true
```
Then add `--open` to the current command. Don't ask again in future sessions — the config persists.

### Session continuity

**Sessions persist automatically between commands** via `.helpmetest/sessions/`. Each successful command updates the session file's mtime. The next `helpmetest interactive` call resumes the most recent active session — no `--session` flag needed.

Sessions expire after **20 minutes of inactivity**. Stale sessions are cleaned up automatically; the next command starts a fresh browser.

Use `--session <runId>` only when you want to resume a specific past session by its ID (visible in the session URL at the bottom of each response).

Use `Exit` to explicitly close the browser and end the session:
```bash
helpmetest interactive "Exit"
```

---

## Reviewing a past session (server-side, from any machine)

`helpmetest interactive review` fetches the **durable server-side record** of a session — every keyword result and HTTP request captured during it — even if the local `.helpmetest/sessions/` pointer is gone or you're on a different machine. Use it to answer "were we properly authenticated?" or to audit what actually happened in a session without re-running anything.

```bash
helpmetest interactive review                                              # current/last local session
helpmetest interactive review acme__interactive__2026-07-05T11:00:00.000Z  # any session by runId
```

### Shorthand flags

Each is `--select <field> --json` in one flag:

| Flag | Equivalent | Returns |
|---|---|---|
| `--keywords` | `--select keywords --json` | `[{keyword, status, line}]` |
| `--errors` | `--select errors --json` | `[{keyword, message, timestamp}]` |
| `--results` | `--select results --json` | `[{keyword, value, timestamp}]` — Get/assertion return values |
| `--screenshots` | `--select screenshots --json` | `[{timestamp, image}]` — base64 PNG from `Take Screenshot` |
| `--network-requests` | `--select requests --json` | `[{ts, method, url, status, duration}]` |
| `--auth` | `--select authEvents --json` | `[{kind: "keyword"\|"request", ...}]` — Save As/As/Login calls and 401/403 responses |
| `--dom-diff` | `--select domDiff --json` | `[{timestamp, counts, added, removedIds, attributeChanges, textChanges}]` — DOM mutations across the whole session, from the same rrweb recording |

Only one shorthand (or an explicit `--filter`) at a time — combining them is an error, not a silent merge.

For a custom shape, use `--select` directly with a JMESPath-style expression:
```bash
helpmetest interactive review --select "keywords[].{keyword,status}" --json
```

`--limit <n>` caps events fetched (default 500).

---

## What the output contains

### Content
Page text extracted from DOM — what's actually displayed on the page.

### Interactive
**The most useful section.** Ready-to-paste RF commands for every actionable element:

```
* Click  [data-testid='submit-btn']  —  Submit Form
* Fill Text  [data-testid='input-name']  —  Full Name
* Select  [data-testid='input-country']  —  — select —
      United States
      United Kingdom
      Germany
* Check  [data-testid='checkbox-testing']  —  testing
* Radio  [data-testid='radio-contact-email']  —  email
```

Copy these directly — selectors are verified against the live page. Use these to build your next command rather than guessing.

### Browser State
Current URL, viewport, memory, timing. Check the URL to confirm navigation. Check **Tabs** — if it shows `chrome-error://chromewebdata/`, the session has crashed (network failure or the browser died); run `Exit` and start fresh.

### Network
All requests with status codes. **Scan this on every call.** A 401, 403, or 500 in the network log is often the actual cause of what looks like a UI problem.

### Keywords
What ran, timing, return values, errors. `✓` = success, `✗` = failure, `⊘` = skipped (because a prior command in the batch failed).

### Screenshots
Saved to `.helpmetest/screenshots/`. Session URL is shown at the bottom — open it to watch live.

---

## Running interactively (agent usage)

Pass commands as positional arguments:

```bash
helpmetest interactive \
  "Go To  https://forms.playground.helpmetest.com" \
  "Fill Text  #email  user@example.com" \
  "Click  button[type=submit]"
```

**Rules:**
- Commands run sequentially; on first failure, later commands are skipped (`⊘`).
- Use `--screenshot` to capture a screenshot after the run.
- Use `--json` to get structured event output (all keyword results + OpenReplay events).
- Session continuity is automatic — the browser stays open between calls within the same session.
- Batch commands when the path is confirmed; go step by step when exploring.

---

## Finding keywords

```bash
helpmetest search "fill text"
helpmetest search "select option"
helpmetest search "get text"
```

The search output shows the library prefix (e.g., `Get Text · Browser`). When multiple libraries define the same keyword name, RF raises `Multiple keywords with name 'X' found` — use the fully-qualified form: `Browser.Get Text`, `Browser.Get Element States`, etc.

---

## Workflow: prototype a test

### 1. Navigate — read the Interactive section

```bash
helpmetest interactive "Go To  https://myapp.com/login" --open --screenshot
```

Read **Interactive** — it gives you the exact selectors and keyword types for everything on the page.

### 2. Work step by step

```bash
helpmetest interactive "Fill Text  input[name=email]  user@test.com"
helpmetest interactive "Fill Text  input[name=password]  secret"
helpmetest interactive "Click  button[type=submit]" --screenshot
```

Check **Browser State** → URL after submit: did it go where expected?

### 3. Batch when confirmed

Once the sequence is verified:

```bash
helpmetest interactive "Fill Text  input[name=email]  user@test.com" "Fill Text  input[name=password]  secret" "Click  button[type=submit]" --screenshot
```

### 4. Exit

```bash
helpmetest interactive "Exit"
```

### 5. Copy into a test

```bash
helpmetest test create \
  --name "Login redirects to dashboard" \
  --tags "feature:auth" \
  --content '*** Test Cases ***
Login Redirects To Dashboard
    As    Guest
    Go To    https://myapp.com/login
    Fill Text    input[name=email]    ${TEST_USER_EMAIL}
    Fill Text    input[name=password]    ${TEST_USER_PASSWORD}
    Click    button[type=submit]
    Get Url    contains    /dashboard'
```

Then run it: `helpmetest test run <id>`. If green, add the test id to the Feature artifact's `scenarios[].test_ids`.

---

## Workflow: debug a failing test

```
Test fails
  ↓
Reproduce interactively — run the exact same steps, observe each result
  ↓
Find the exact failing step — look at the Keywords section for the ✗
  ↓
Diagnose: wrong selector? Element not loaded? Auth issue? 4xx in network?
  ↓
Fix interactively — prove the fix works before touching the test
  ↓
Update the test, run it, confirm green
```

### Element not found

Read the **Interactive** section — it lists every actionable element on the live page with its actual selector. If your selector isn't listed, it either doesn't exist or has a different name than expected.

```bash
# What's actually on the page?
helpmetest interactive "Go To  https://myapp.com/page"
# Read Interactive section
```

### Element exists but click fails

```bash
# Is it visible and enabled?
helpmetest interactive "Browser.Get Element States  [data-testid=submit]"

# In the viewport?
helpmetest interactive "Scroll To Element  [data-testid=submit]"
```

### Wrong text / assertion mismatch

```bash
# What's actually displayed?
helpmetest interactive "Browser.Get Text  h1"
helpmetest interactive "Browser.Get Property  input[name=email]  value"

# Where are we?
helpmetest interactive "Get Url"
```

### Silent failures

Look at **Network** — a 4xx or 5xx there explains most "the page did nothing" problems. A 401 means auth state wasn't set up. A 500 means a backend error the UI is swallowing.

---

## Authentication

Before any auth flow, check if a saved state exists:

```bash
helpmetest status  # look for auth state names in test data
```

Restore an existing state — don't re-authenticate:
```bash
helpmetest interactive "As  Admin"
```

If no state exists, authenticate once and save:
```bash
helpmetest interactive "Go To  https://myapp.com/login" --open
# fill and submit...
helpmetest interactive "Save As  Admin"
```

Future sessions: `As  Admin` restores without re-authenticating.

---

## RF keyword reference

| Intent | Keyword |
|---|---|
| Navigate | `Go To  https://example.com` |
| Click | `Click  [data-testid=btn]` |
| Fill input (clears first) | `Fill Text  input[name=email]  value` |
| Type into input (appends) | `Type Text  input[name=q]  more text` |
| Read text | `Browser.Get Text  h1` |
| Read input value | `Browser.Get Property  input  value` |
| Read URL | `Get Url` |
| Check element states | `Browser.Get Element States  button` |
| Wait for element | `Wait For Elements State  .spinner  hidden  timeout=10000` |
| Select dropdown | `Select Options By  select  label  Germany` |
| Check a checkbox | `Check  [data-testid=checkbox-testing]` |
| Select a radio | `Radio  [data-testid=radio-email]` |
| Scroll to element | `Scroll To Element  footer` |
| Screenshot | `Take Screenshot` (or `--screenshot` flag) |
| Run JS | `Evaluate Javascript  document.title` |
| Save auth state | `Save As  Admin` |
| Restore auth state | `As  Admin` |
| Close session | `Exit` |

When unsure: `helpmetest search "<intent>"`.
When getting ambiguity errors: prefix with library — `Browser.Get Text`, `Browser.Get Element States`.

---

## What to do with findings

- **Good selector found** → add to the Feature artifact's `memory` field so future sessions don't re-discover it
- **Working command sequence** → copy into `helpmetest test create`
- **Bug observed** → add to Feature artifact's `bugs` array immediately — don't just note it in chat
- **Auth flow discovered** → `Save As <StateName>`, document it in the ProjectOverview artifact
