<!-- llms-description: Drive a real cloud browser one command at a time — explore pages, debug selectors, prototype a flow. -->

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

When a command in a batch fails, the rest are skipped. Verified 2026-09-25 — the marker is
`○` with the word `(skipped)`, not `⊘` as this line used to claim, and the whole call exits
1:

```
0.139s  ✓ Go To  https://todo.playground.helpmetest.com
10.016s ✗ Click  .does-not-exist-anywhere
  TimeoutError: locator.click: Timeout 10000ms exceeded.
0.000s  ○ Get Title (skipped)
```

Note the cost in that line: a selector that does not exist burns the **full 10s timeout**
before the batch aborts. A long batch built on a guessed selector spends ten seconds finding
out. Batch when you're confident the whole sequence works; go step by step when exploring or
debugging.

### Options

| Flag | Effect |
|---|---|
| `--screenshot` | Capture screenshot after the command (appends `Take Screenshot` automatically) |
| `--open` | Open the live session URL in your browser immediately — watch clicks happen |
| `--session <runId>` | Resume a specific named session (bypasses auto-resume) |
| `--timeout <duration>` | Per-command timeout. A bare number is SECONDS (default 10s — raised from 5s 2026-08-11: the old default was shorter than legitimate slow selector/navigation waits, so it discarded the real RF error and misreported it as "the session ended unexpectedly" even when the browser was still alive and working). A string with units is parsed via `parse-duration` syntax for sub-second/compound precision — e.g. `--timeout 100ms`, `--timeout 1m10s`. Set via `Browser.set_browser_timeout(...)` — a plain Python call inside the RF `start_test` hook, never an RF keyword — so it's silent: it never appears in the keyword timeline/history, no matter how many commands run (fixed 2026-08-15; a prior version injected a synthetic `Set Browser Timeout` keyword on a session's first command, which leaked into `start_test`'s keyword list). |
| `--dom-diff` | Show DOM mutations (adds/removes/attribute/text changes) that happened during the command — sourced from the session's existing rrweb recording, added as a "DOM Diff" output section |
| `--debug` | Currently a no-op for `interactive` — accepted and threaded through the CLI/app-server/vm-manager, but nothing on the guest side reads it. The one function that could deliver "full diagnostics" (`CollectDiagnostics()` — OpenReplay events/WebVitals/FPS/resource timings) is explicitly skipped for interactive sessions in `vm/guest/listener.py` regardless of this flag. Confirmed live 2026-09-11: identical output with/without `--debug`. Don't rely on it; use `--dom-diff` for mutation data or `interactive history` for the full persisted event record instead. |
| `--json` | Output as JSON (for scripting/agents) |
| `--stream` | Emit newline-delimited JSON events (one JSON object per line: `keyword`, `keyword_result`, `phase_done`, final `{"type":"done",...}`) instead of TTY pretty-print or a single JSON blob — for agents that want to process events as they arrive rather than waiting for the full result |
| `--select <path>` | Select fields from the JSON output — e.g. `--select "[].type"` against `--json` output (a flat event array; see `--schema`) |
| `--schema` | Print the NDJSON event schema (field shapes per event type) as JSON and exit — no command is sent. Use it to know what `--select` can address |


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

Sessions expire after **3 minutes of inactivity** (`vm/config.yaml`'s `interactive_lru_ttl_s: 180` — confirmed live 2026-09-11; this doc and the CLI's own client-side staleness check previously assumed 20 minutes, which was wrong by >6x). Stale sessions are cleaned up automatically; the next command starts a fresh browser.

Use `--session <runId>` only when you want to resume a specific past session by its ID (visible in the session URL at the bottom of each response).

Use `Exit` to explicitly close the browser and end the session:
```bash
helpmetest interactive "Exit"
```

**Expect silence afterwards, and do not read it as a failure.** Observed 2026-09-25, in
this order, all exit 0:

| call | output |
|---|---|
| `interactive "Exit"` | `○ Exit (skipped)` then `PASS` |
| `interactive run "Exit"` | **empty** |
| `interactive run "Get Url"` | **empty** |
| `interactive run "Go To …" "Get Url"` | **empty** |
| the same command a few minutes later | normal output, new session |

So for a stretch after `Exit`, every call in that directory returns nothing at all and
still exits 0 — the §3b silent-success shape at session level. It recovered on its own once
a new session directory appeared under `.helpmetest/sessions/`; **nothing was deleted or
repaired to make that happen, and the cause was not established** — the timing is
consistent with the exited session still being the freshest one and being auto-resumed
until it aged out, but that was not confirmed.

Practical consequences:

- **Empty output with exit 0 is not "the command passed with nothing to say."** Check the
  byte count. A real command prints keyword lines, a divider and a page dump.
- **You rarely need `Exit`.** Sessions expire on their own after 3 minutes of inactivity.
  Calling it buys nothing and costs the next few invocations.
- A clean directory is unaffected — the same commands in a fresh temp dir with a copied
  `config.yaml` worked immediately.

---

## Reviewing a past session (server-side, from any machine)

`helpmetest interactive history` fetches the **durable server-side record** of a session — every keyword result and HTTP request captured during it — even if the local `.helpmetest/sessions/` pointer is gone or you're on a different machine. Use it to answer "were we properly authenticated?" or to audit what actually happened in a session without re-running anything. Same output format as `helpmetest test view <id> <timestamp>` (formerly `test history`) — both render through one shared formatter.

```bash
helpmetest interactive history                                              # current/last local session
helpmetest interactive history acme__interactive__2026-07-05T11:00:00.000Z  # any session by runId
```

### Shorthand flags

Each is `--select <field> --json` in one flag:

| Flag | Equivalent | Returns |
|---|---|---|
| `--keywords` | `--select keywords --json` | `[{keyword, status, line, elapsed}]` |
| `--errors` | `--select errors --json` | `[{keyword, message, timestamp}]` |
| `--results` | `--select results --json` | `[{keyword, value, timestamp}]` — Get/assertion return values |
| `--screenshots` | `--select screenshots --json` | `[{timestamp, image}]` — base64 PNG from `Take Screenshot` |
| `--network` | `--select network --json` | `[{kind: "http"\|"graphql"\|"ws", method, url, status, duration, ...}]` — HTTP requests, GraphQL operations, WebSocket messages |
| `--metrics` | `--select metrics --json` | `[{tag, args}]` — WebVitals, PageLoadTiming, ResourceTiming, LongTask/LongAnimationTask, PageRenderTiming, rage-click (MouseThrashing) |
| `--interactions` | `--select interactions --json` | `[{tag, args}]` — MouseClick, InputChange, SelectionChange, TabChange |
| `--console` | `--select console --json` | `[{tag, args}]` — ConsoleLog, JSException |
| `--events` | `--select events --json` | `[{tag, args}]` — Redux/Zustand/Vuex/NgRx dispatches, custom app-reported issues/user id |
| `--navigation` | `--select navigation --json` | `[{url, title, referrer, ts}]` — page location changes |
| `--auth` | `--select authEvents --json` | `[{kind: "keyword"\|"request", ...}]` — Save As/As/Login calls and 401/403 responses |
| `--dom-diff` | `--select domDiff --json` | `[{timestamp, counts, added, removedIds, attributeChanges, textChanges}]` — DOM mutations across the whole session, from the same rrweb recording |

Only one shorthand (or an explicit `--filter`) at a time — combining them is an error, not a silent merge.

For a custom shape, use `--select` directly with a JMESPath-style expression:
```bash
helpmetest interactive history --select "keywords[].{keyword,status}" --json
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
  "Fill Text  \#email  user@example.com" \
  "Click  button[type=submit]"
```

**Note the `\#`.** This example used to say `#email` and did not run at all: `#` starts a
Robot Framework comment, so the whole chain fails before the first keyword with
`syntax error: # starts a comment and must be escaped`. Verified 2026-09-26 — broken as
written, green with the backslash (`✓ Fill Text  \#email  user@example.com`). Use a
backslash, never quotes; see `modes/shared.md` §3h for why quoting makes it worse.

**Rules:**
- Commands run sequentially; on first failure, later commands are skipped — marked `○` with a `(skipped)` suffix, e.g. `0.000s  ○ Click  button[type=submit] (skipped)`. (Measured 2026-09-26; this line used to say `⊘`.)
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

**Opportunistic accessibility check** — while you're already on a new page during exploration or debugging, running the axe-core recipe from `references/rf-recipes.md` costs one extra `Evaluate` call and surfaces obvious a11y issues (missing labels, contrast, keyboard traps) without the user having to ask for a dedicated audit. Note anything `critical`/`serious` in your findings; don't let it derail the exploration you're actually there for.

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
  --id login-redirects-to-dashboard \
  --name "Login redirects to dashboard" \
  --tags "feature:auth,priority:high,persona:test-user,project:myapp,url:myapp.com" \
  --content '# Log in with valid credentials and confirm the redirect to the dashboard
As    Guest
Go To    https://myapp.com/login
Fill Text    input[name=email]    ${TEST_USER_EMAIL}
Fill Text    input[name=password]    ${TEST_USER_PASSWORD}
Click    button[type=submit]
Get Url    contains    /dashboard'
```

`--id` is required (URL-safe, no spaces, no "test" suffix — becomes the permanent identifier). `--content` is bare RF keywords, not a full `*** Test Cases ***` block — `test create` wraps it into a real test case itself. Every keyword group needs a leading `#` comment or creation is rejected (run `/helpmetest comment` to auto-fix). Tags must satisfy the full schema — a real `feature:`/`priority:`/`persona:`/`project:`/`url:` set, not placeholders; run `helpmetest test create --help` with no valid tags to see the exact existing values accepted for your project.

Then run it: `helpmetest test run <id>`. If green, add the test id to the matching scenario's `test_ids` in the Feature artifact. **There is no top-level `scenarios` array** — verified against `artifact schema Feature` 2026-09-25: scenarios live under `functional`, `edge_cases` and `non_functional`, each an array of `Scenario` (`name, given, when, then, auth, url, tags, test_ids`). So the path is `functional[N].test_ids`, not `scenarios[N].test_ids`.

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

Before any auth flow, check if a saved state exists — `As` with any bogus name lists every
real saved state for your company in its error message (confirmed live: no dedicated
"list states" command exists, this is the actual discovery mechanism):

```bash
helpmetest interactive "As  ?"
# FAIL: No state found for name '?' ... Available states: 'Admin', 'DevAuth', ...
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
| Type into input, key by key — **also replaces, does not append** | `Type Text  input[name=q]  text` |
| Read text | `Browser.Get Text  h1` |
| Read input value | `Browser.Get Property  input  value` |
| Read URL | `Get Url` |
| Check element states | `Browser.Get Element States  button` |
| Wait for element | `Wait For Elements State  .spinner  hidden  timeout=10s` |
| Select dropdown | `Select Options By  select  label  Germany` |
| Check a checkbox or radio button | `Check Checkbox  [data-testid=checkbox-testing]` |
| Scroll to element | `Scroll To Element  footer` |
| Screenshot | `Take Screenshot` (or `--screenshot` flag) |
| Run JS | `Javascript  return document.title` |
| Save auth state | `Save As  Admin` |
| Restore auth state | `As  Admin` |
| Close session | `Exit` |
| Upload a file from local content (no filesystem path needed on the VM — see below) | `Upload File By Selector  input[type=file]  ${buffer}` |

**Measured 2026-09-25 — this table used to say `Type Text` appends. It does not.** Two runs
against the same input, reading the value back with `Get Property`:

| sequence | resulting value |
|---|---|
| `Fill Text  aaa` → `Type Text  bbb` | `bbb` (not `aaabbb`) |
| `Type Text  xxx` → `Type Text  yyy` | `yyy` (not `xxxyyy`) |

So neither keyword accumulates text. To append, read the current value first and type the
concatenation:

```robot
${current}=    Get Property    input[name=q]    value
Fill Text    input[name=q]    ${current} more
```

The real difference is *how* they enter it — `Fill Text` sets the value in one step,
`Type Text` emits key events, which matters for inputs with per-keystroke handlers
(autocomplete, live search, input masks).

When unsure: `helpmetest search "<intent>"`.
When getting ambiguity errors: prefix with library — `Browser.Get Text`, `Browser.Get Element States`.

### Uploading a file (no local file on the VM)

`Upload File By Selector` normally takes a filesystem path — but that path is resolved **on
the remote VM**, not your machine, so a bare local path (`/tmp/my-file.txt`) always fails with
`Nonexistent input file path`. Instead, build a buffer dict **in the same command batch** using
the classic `Create Dictionary` keyword (RF's newer `VAR` syntax is parser-level, not an
invokable keyword, and does not work through the interactive one-command-at-a-time dispatcher):

```bash
helpmetest interactive \
  "Go To  https://myapp.com/upload" \
  "\${buffer}=  Create Dictionary  name=report.txt  mimeType=text/plain  buffer=aGVsbG8gd29ybGQ=" \
  "Upload File By Selector  input[type=file]  \${buffer}"
```

`buffer` is base64-encoded file content (`base64 -i file` or `python3 -c "import base64;
print(base64.b64encode(open('file','rb').read()).decode())"` to produce it). The `${buffer}`
variable does **not** persist across separate `helpmetest interactive` invocations of the same
session (only the browser/page state does) — the `Create Dictionary` call and the
`Upload File By Selector` call must be in the same command batch.

---

## What to do with findings

- **Good selector found** → add to the Feature artifact's `memory` field so future sessions don't re-discover it
- **Working command sequence** → copy into `helpmetest test create`
- **Bug observed** → add to Feature artifact's `bugs` array immediately — don't just note it in chat
- **Auth flow discovered** → `Save As <StateName>`, document it in the ProjectOverview artifact
