# Mode: comment — rewrite test comments to quality standard

**What this mode does:** audit every comment in a test (or set of tests) and rewrite them so the test reads as a coherent narrative — grouped by intent, written for a reader who understands the product but not the implementation.

**When to use:** user says "fix comments", "clean up comments", "comments are noisy", "too many comments", "comment every line", "rewrite comments", or after `/improve` when comment quality is the remaining issue.

---

## The Problem This Solves

A test with per-line comments has MORE noise than one with none:

```robot
# get the latest passing desktop-smoke-demo run id
  ${run_id}=  Javascript    ...

# run_id must contain the current year — confirms a real run was found
  Should Contain  ${run_id}  2026  run_id invalid: ${run_id}

# fetch the HLS manifest and return segment count + validation result as a compact string
  ${manifest_info}=  Javascript    ...

# manifest_info must start with ok
  Should Start With  ${manifest_info}  ok  ...
```

Each comment narrates the line below it. The reader has to read both and reconcile. The comments add no new information — they describe what the keywords already say. This is documentation debt, not documentation.

---

## The Rules (C1–C13)

**C1 — Group, don't annotate**

One comment covers 2–8 related steps. No per-line comments. A step group is a set of steps that together accomplish one user-visible action or one verification goal.

A single keyword under its own comment is always a C1 violation. `As  <state>` (auth state restoration) must be bundled with the `Go To` and initial wait that follow it — it has no value as a standalone section.

```robot
# Find a recent passing run to replay
  ${run_id}=  Javascript    ...
  Should Contain  ${run_id}  2026  run_id invalid: ${run_id}
```

Not:
```robot
# get the run id
  ${run_id}=  Javascript    ...
# confirm run id is recent
  Should Contain  ${run_id}  2026  run_id invalid: ${run_id}
```

**C2 — No numbering**

Comments are narrative headings, not steps in a procedure. Never write `# 1. Open the page`, `# Step 3:`, or any ordinal.

This applies even when the grouping is otherwise correct. `# 1. Authenticate` → `# Auth and open the app`. Remove the number, keep the intent.

**C3 — No decorations**

No `# --- section ---`, no `# ===`, no dashes around text, no separator lines. This applies to ALL comments including the first one — `# === SETUP ===` is a C3 violation regardless of position.

**C4 — Written in test/product context, not implementation context**

Comments describe what the test is *doing from the user's perspective*, not what the code is doing.

```robot
# Find a recent passing run to replay       ← product context (why this matters to the test)
```

Not:
```robot
# get the latest passing desktop-smoke-demo run id    ← implementation narration
```

**C5 — Don't narrate what keywords say**

`Go To`, `Click`, `Fill Text`, `Wait For Elements State` are self-explanatory. A comment above `Go To https://helpmetest.slava.helpmetest.com/test/...` that says `# navigate to the replay page` adds nothing. If the Go To is the *start of a meaningful phase*, name the phase — not the navigation.

Critically: never isolate a `Go To` (or any single navigation keyword) under its own comment. Navigation is always the *start* of a group — bundle it with the steps that follow.

```robot
# WRONG — Go To gets its own comment, one step under it
# navigate to the login page
  Go To  https://.../login

# log in as automation user
  Wait For Elements State  ...
  Fill Text  ...

# RIGHT — navigation is bundled into the action group
# Log in as automation user
  Go To  https://.../login
  Wait For Elements State  ...
  Fill Text  ...
```

```robot
# Replay page loads with real video
  Go To  https://helpmetest.slava.helpmetest.com/test/desktop-smoke-demo/${ts}
  Wait For Elements State  css=.replay-player-container video  visible  timeout=20s
```

Not:
```robot
# navigate to the replay page for this run
  Go To  https://helpmetest.slava.helpmetest.com/test/desktop-smoke-demo/${ts}
# video element must appear in the player container
  Wait For Elements State  css=.replay-player-container video  visible  timeout=20s
```

**C6 — Assertion comments name the invariant, not the check**

When a group of steps ends in assertions, the section comment names the *invariant being protected*, not a description of what the assertions do.

```robot
# Last segment is a valid non-empty MP4 container
  ${seg_info}=  Javascript    ...
  Should Contain  ${seg_info}  ftyp=ftyp  segment not a valid MP4: ${seg_info}
```

Not:
```robot
# ftyp=ftyp confirms a valid self-contained MP4 container
  Should Contain  ${seg_info}  ftyp=ftyp  ...
# segment must be at least 1000 bytes
  Should Not Contain  ${seg_info}  size=0  ...
```

The failure message on the assertion itself carries the diagnostic detail. The section comment carries the *why it matters*.

**C7 — Section size discipline**

If a section grows beyond 8 steps, split it with a more specific sub-comment. No single comment should own half the test.

---

## Correct section structure

```robot
# <phase: what the user/test is doing>
  <2–8 steps>

# <next phase>
  <2–8 steps>
```

Phases for a typical replay test:
```robot
# Auth and open the app
# Find a recent passing run to replay
# Confirm the HLS manifest is valid and has segments
# Last segment is a valid non-empty MP4 container
# Replay page loads with real video
# Video decodes real desktop frames at expected resolution
# Video plays when started
```

Phases for a typical form test:
```robot
# Open the form as an authenticated user
# Fill and submit the form
# Confirm the record was saved
# Persistence check — reload and verify the data survives
```

**C8 — No "verify / check / assert / validate" in section comments**

These words are tautological in a test — every assertion verifies something. Name the invariant being protected instead.

```robot
# WRONG
# verify the order total is correct

# RIGHT
# Order total includes the applied discount
```

**C9 — No generic labels**

`# setup`, `# given`, `# teardown`, `# cleanup`, `# pre-conditions`, `# test step N`, `# expected result`, `# action`, `# verify` without specificity are meaningless. Every comment must be specific to what *this* test does at *this* point.

```robot
# WRONG
# setup

# RIGHT
# Open the cart with 3 items as a guest
```

**C10 — Present tense, active voice**

Comments describe what the test does now. Not past tense, not future.

```robot
# WRONG
# logged in as automation user
# will navigate to settings

# RIGHT
# Log in as automation user
# Auth and open the app
```

**C11 — No selector or variable names in comments**

CSS selectors, JS expressions, and RF variable names belong in the keywords, not in comments. Comments are read by humans, not machines.

```robot
# WRONG
# wait for .replay-player-container video to be visible

# RIGHT
# Video player is ready
```

**C12 — Section comment must be more specific than the test name**

If the test is `user-can-export-csv`, a section that says `# export the data` restates the test name. Section comments add specificity — what state, what user, which step of the flow.

```robot
# Test name: user-can-export-csv

# WRONG — restates the test name
# export the data

# RIGHT — adds specificity
# Trigger export from the settings modal
```

**C13 — Error path comments name the expected failure**

On negative / error scenarios, the comment names what's supposed to break and why — not just what's being done.

```robot
# WRONG
# submit the form

# RIGHT
# Submit with the required email field blank
```

---

## Workflow

### 1. Read the test

```bash
helpmetest test view <id>
```

### 2. Identify the comment violations

For each comment in the test body, classify:
- **C1** — per-line comment (one comment, one step)
- **C2** — numbered comment
- **C3** — decorated comment (dashes, equals)
- **C4** — implementation narration instead of product context
- **C5** — narrates what the keyword already says
- **C6** — describes the assertion instead of naming the invariant
- **C7** — section larger than 8 steps with no sub-comment
- **C8** — uses verify/check/assert/validate as first word
- **C9** — generic label (setup, given, pre-conditions, test step N, etc.)
- **C10** — past tense or future tense wording
- **C11** — CSS selector or variable name inside the comment
- **C12** — comment restates the test name without adding specificity
- **C13** — error path comment names the action, not the expected failure

### 3. Rewrite

The output MUST have section comments. Every group of related steps starts with a `#` comment — the comment comes first, then the keywords it covers. Never produce keywords before their group's leading comment. Never produce a flat block with no comments — that is always wrong. The job is to rewrite bad comments into good ones, not to delete all comments.

Structure:
```
# comment
  keyword
  keyword
# comment
  keyword
  keyword
```

Each comment describes what the keywords immediately below it do — not what came before, not a summary of the whole test. Group steps by intent. Write one section comment per group. Apply C1–C13. Do not change any keyword, selector, assertion value, or failure message — only comments change.

### 4. Apply

```bash
helpmetest test update <id> --file /tmp/<id>-commented.robot --no-run
```

### 5. Verify it still passes

```bash
helpmetest test run <id>
```

Comment changes should never break a test. If it fails, a keyword was accidentally changed — diff and fix.

---

## Before / after example

**Before** (desktop-replay-quality, problematic sections):
```robot
# get the latest passing desktop-smoke-demo run id
  ${run_id}=  Javascript    (async ()=>{ ... })()

# run_id must contain the current year — confirms a real run was found
  Should Contain  ${run_id}  2026  run_id invalid: ${run_id}

# fetch the HLS manifest and return segment count + validation result as a compact string
  ${manifest_info}=  Javascript    (async ()=>{ ... })()

# manifest_info must start with ok
  Should Start With  ${manifest_info}  ok  manifest check failed: ${manifest_info}

# extract the segment count (second token after ok|)
  ${seg_count}=  Javascript    Number('${manifest_info}'.split('|')[1])

# segment count must be positive (at least 1 segment)
  Should Be True  ${seg_count} > 0  manifest has zero segments
```

**After:**
```robot
# Find a recent passing run to replay
  ${run_id}=  Javascript    (async ()=>{ ... })()
  Should Contain  ${run_id}  2026  run_id invalid: ${run_id}

# Manifest is valid and has at least one segment
  ${manifest_info}=  Javascript    (async ()=>{ ... })()
  Should Start With  ${manifest_info}  ok  manifest check failed: ${manifest_info}
  ${seg_count}=  Javascript    Number('${manifest_info}'.split('|')[1])
  Should Be True  ${seg_count} > 0  manifest has zero segments
```

---

## Integration with improve

`/helpmetest improve` applies I2 (section comments) and I3 (inline comments). This mode goes deeper — it enforces C1–C7 on every comment, not just whether comments exist. Run `comment` after `improve` when the test has comments but they're dense or implementation-facing.

**Version:** 0.1
