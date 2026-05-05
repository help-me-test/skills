---
name: helpmetest
description: "Single entry point for all HelpMeTest QA work. Dispatches to a mode based on the first argument: agent (Tasks-artifact harness, base discipline), tdd (write/fix tests — default for code-work tasks), discover (map site into Features), fix-tests (repair failing), coverage (gap analysis), regression (change-targeted run), validate (test quality review), report (read-only project health diagnosis), proxy (tunnel localhost), api-testing (API-level RF tests), ui-review (visual walkthrough), onboard (new project bootstrap). Usage: /helpmetest [mode] [task...]. Bare /helpmetest runs full QA (discover + tdd)."
allowed-tools: mcp__helpmetest-*
argument-hint: "[agent | tdd | discover | fix-tests | coverage | regression | validate | report | proxy | api-testing | ui-review | onboard | <task>]"
---

# /helpmetest — QA workflow router

You are a HelpMeTest agent. This skill is the single entry point. No matter which mode runs, two files always apply: `modes/_shared.md` (common context) and `modes/agent.md` (Tasks-artifact lifecycle — this is the universal accountability discipline).

## 1. Normalize the input

The user's request may or may not start with `/helpmetest` as a literal prefix. **Strip it if present** before reading the mode token:

```
"/helpmetest tdd write login test"   →  first mode token: "tdd",  rest: "write login test"
"tdd write login test"               →  first mode token: "tdd",  rest: "write login test"
"write login test"                   →  first mode token: NONE,   rest: "write login test"
```

This lets the same pasted text work from a terminal (`helpmetest agent claude "/helpmetest tdd ..."`) and from a slash-command context (`/helpmetest tdd ...`).

## 2. Determine the mode

Parse the first remaining token:

| First token | Mode |
|------------|------|
| `agent` | **agent-only** — you were invoked with no downstream workflow; maintain the Tasks artifact lifecycle around whatever the user describes next, pick the closest workflow mode based on the task text. |
| `tdd` | **tdd** — write/fix tests |
| `discover` | **discover** — map into Feature artifacts |
| `fix-tests` or `fix` | **fix-tests** — diagnose and repair broken tests |
| `coverage` | **coverage** — gap analysis: what scenarios have no tests |
| `regression` | **regression** — run tests affected by a named set of changed files |
| `validate` | **validate** — score existing tests against quality rules |
| `proxy` | **proxy** — tunnel localhost |
| `api-testing` or `api` | **api-testing** — API-level RF tests |
| `ui-review` or `ui` | **ui-review** — visual walkthrough |
| `onboard` | **onboard** — new project bootstrap |
| `change-impact` or `impact` | **change-impact** — git diff → find @helpmetest annotations → run affected tests → RegressionRun artifact with verdict |
| `pre-push` or `push` | **pre-push** — run all priority:critical tests + annotation-covered changed files → BLOCKED or CLEAR TO PUSH |
| `pr-review` or `pr` | **pr-review** — branch diff → map to annotations → flag unannotated files as gaps → CoverageReport artifact (no test runs) |
| `nightly` | **nightly** — run all Feature tests, mark broken ones, discover new URLs, create stub Features |
| `report` | **report** — read-only project health diagnosis: triage → auth → tests → stability → sync → coverage → code → bugs → artifacts → drift → tiered report → recommended next fix. Sub-phase: `report <phase>`. |
| `continue` | **resume** — task mentions an existing Tasks artifact id; fetch it, find the first open subtask, resume (see `modes/agent.md` §Resuming an existing artifact). |
| (empty / bare `/helpmetest`) | **full-qa** — full cycle: discover + tdd + validate |
| anything else (e.g. looks like a task description) | **tdd** (default) with the whole input as the task |

Mode detection is generous — "write tests for X" → tdd, "test is failing" → fix-tests, "what does this site do" → discover. If ambiguous, pick the closest mode and narrate your choice before executing.

## 3. Load context

Load these files in this order, always:

1. `modes/_shared.md` — common rules (orient first, narrate actions, auth, tools, events)
2. `modes/agent.md` — Tasks-artifact lifecycle (the accountability contract — read every time, not optional)
3. `modes/<mode>.md` — the mode-specific workflow

For `full-qa`: load `modes/discover.md`, then `modes/tdd.md`, then `modes/fix-tests.md` — run them end to end.

These files live next to this SKILL.md. Use the `Read` tool with relative paths:

```
Read  modes/_shared.md
Read  modes/agent.md
Read  modes/<mode>.md
```

If a relative path doesn't resolve, try the install location explicitly:

```
Read  ~/.claude/skills/helpmetest/modes/<name>.md
Read  .claude/skills/helpmetest/modes/<name>.md
```

If you are running inside the harness (`helpmetest agent claude "<task>"`), the skill bundle composer inlines every `modes/*.md` file into your system prompt — you already have them and do not need to `Read`. Check: if your system prompt already contains sections labeled `# Mode: agent`, `# Mode: tdd`, etc., skip the Read step.

## 4. Execute

Follow the loaded mode's instructions step by step, **while maintaining the Tasks artifact per `modes/agent.md`**. Narrate before and after each significant action (`modes/_shared.md` §2).

## 5. When you're done

Close out every subtask in the Tasks artifact with evidence before exiting (see `modes/agent.md` §Evidence and §Final audit). Then end with a summary in the `What you can now trust works / What's still unprotected / Bugs found` format (see `modes/tdd.md`).

## Mode reference

Every mode follows the same pattern: orient → announce → act. The announce step always states what the user will have after the work, recommends a starting point, and ends with a binary scope choice (or proceeds if no ambiguity). See `modes/_shared.md §1b` for the full rule.

```
agent         Tasks-artifact lifecycle only — baseline discipline, any workflow.
tdd           Write or fix tests. Default for 'write tests', 'implement X', 'fix bug', 'refactor'.
              Bare: presents TDD landscape (failing tests + uncovered scenarios), recommends one, asks "that or something specific?"
discover      Map a live app, PRD, or spec into Feature artifacts. Prerequisite for full-qa.
              Bare/no source: asks what the source is. Bare/existing artifacts: asks "extend or focus on a specific area?"
fix-tests     Diagnose a failing test (selector, timing, auth, backend) and repair it.
              Bare: triage mode — collects status + git state, announces findings, recommends highest-priority failing test.
coverage      Read-only gap analysis — which scenarios lack tests, which tests are orphans.
              Bare: announces what user will know after, asks "full scope or critical/high first?"
regression    Given a list of changed files, run only tests affected by those files.
              Bare/no files: asks "what changed?" in one sentence framed as "after this you'll know if it's safe to push."
validate      Score existing tests against /tdd quality rules; produce a rewrite queue.
              Bare: announces what user will find, asks "full suite or critical first?"
proxy         Set up localhost tunneling before testing dev servers.
              Bare/no port: asks "what port?" — then sets up + verifies before any tests are written.
api-testing   REST/GraphQL API tests in Robot Framework via the HTTP library.
              Bare/no endpoint: asks "specific endpoint, feature area, or explore from Feature artifacts?"
ui-review     Screenshot-driven visual walkthrough across viewports.
              Bare: announces full audit (N pages × 3 viewports), asks "full audit or specific page?"
onboard       New project setup: create HELPMETEST.md + ProjectOverview + initial artifacts.
              Bare: runs the structured 3-question interview (source of truth, stage, goal).
full-qa       End-to-end: discover → tdd → fix-tests — ran by default on bare /helpmetest.
change-impact git diff → @helpmetest annotations → run affected tests → RegressionRun verdict.
              Bare/no commit: announces intent, defaults to HEAD~1 diff, offers to use specific commit.
pre-push      All priority:critical tests + changed-file coverage → BLOCKED or CLEAR TO PUSH.
              Bare: announces binary verdict intent, proceeds immediately — no scope ambiguity.
pr-review     Branch diff → annotation map → gap report → CoverageReport (no test runs).
              Bare: announces analysis-only intent, proceeds immediately.
nightly       Run all Feature tests, mark broken, discover new URLs, create stub Features.
              Bare: announces N tests + discovery run, proceeds immediately.
report        Read-only project health diagnosis. Layered: triage → auth → tests → stability → sync →
              coverage → code → bugs → artifacts → drift → tiered 🔴/🟠/🟡 report → recommended next fix.
              Stability uses last-10-runs history (catches the "last green, previous 5 red" flakiness).
              Code phase auto-skips if not in a code dir. No tests run, no artifacts modified.
              Bare: announces full sweep, asks "full report or just one phase?"
              Sub-tokens: report tests, report sync, report stability, etc.
```
