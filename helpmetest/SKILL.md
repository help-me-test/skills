---
name: helpmetest
description: "Single entry point for all HelpMeTest QA work. Dispatches to a mode based on the first argument: agent (Tasks-artifact harness, base discipline), tdd (write/fix tests — default for code-work tasks), discover (map site into Features; also handles fast triage sweeps — 'find bugs', 'poke around', 'good test around'), fix (repair failing tests), coverage (gap analysis), regression (change-targeted run), validate (test quality review), improve (audit + rewrite tests in place — adds section comments, inline comments, fixes selectors and tags), comment (rewrite test comments to quality standard — grouped by intent, no per-line narration), report (read-only project health diagnosis), proxy (tunnel localhost), api (API-level RF tests), ui (visual walkthrough), interactive (drive a real browser one command at a time — explore, debug, prototype), onboard (new project bootstrap). Usage: /helpmetest [mode] [task...]. Bare /helpmetest runs full QA (discover + tdd)."
argument-hint: "[agent | tdd | discover | fix | coverage | regression | validate | improve | comment | report | proxy | api | ui | interactive | onboard | ssl | <task>]"
---

# /helpmetest — QA workflow router

You are a HelpMeTest agent. This skill is the single entry point. No matter which mode runs, two files always apply: `modes/shared.md` (common context) and `modes/agent.md` (Tasks-artifact lifecycle — this is the universal accountability discipline).

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
| `tdd` | **tdd** — write/fix tests (sub-step; for full code work use `dev`) |
| `dev` | **dev** — orchestrator for all code work: greenfield, new feature, change, refactor. Reads the situation and runs the right sequence: onboard → tests RED → build GREEN → interactive → discover → validate → improve → coverage |
| `discover` | **discover** — map into Feature artifacts |
| `fix-tests` or `fix` | **fix-tests** — diagnose and repair broken tests |
| `coverage` | **coverage** — gap analysis: what scenarios have no tests |
| `regression` | **regression** — run tests affected by a named set of changed files |
| `validate` | **validate** — score existing tests against R1-R13 quality rules. Outputs `ValidationReport` artifact with grade distribution (A/B/C/D/F), R11-R13 failures, and action queue (ship/rewrite/delete).
| `improve` | **improve** — audit every test against I2-I6 criteria (section comments, inline comments, assertions, selectors, tags), then rewrite and re-run each failing test in place. The only mode that both critiques and fixes.
| `comment` | **comment** — audit and rewrite test comments only (C1–C7 rules): group per-line comments into intent-based sections, remove numbering and decorations, replace implementation narration with product-context headings, name invariants instead of describing assertions. No keywords, selectors, or assertions are changed.
| `proxy` | **proxy** — tunnel localhost |
| `terminal` | **terminal** — run shell commands (Jest, pytest, bun test, Go test…) using the `Bash` keyword. Cross-references `ci` for running unit tests as a GHA step. |
| `ssl` or `domain` | **ssl** — write, run, and debug DomainChecker SSL certificate tests. No browser needed — keywords make direct TLS connections from inside the VM. Pass a domain to generate a test instantly. |
| `ci` | **ci** — CI integration: acquire a token, install the CLI, run tests in GitHub Actions / GitLab / CircleCI / Bitbucket. Cross-references `proxy` for private/staging URLs. |
| `api-testing` or `api` | **api-testing** — API-level RF tests |
| `ui-review` or `ui` | **ui-review** — visual walkthrough |
| `onboard` | **onboard** — new project bootstrap |
| `interactive` | **interactive** — drive a real browser one command at a time: explore pages, debug selectors, prototype a flow before writing a test, or verify something ad-hoc |
| `change-impact` or `impact` | **change-impact** — git diff → find @helpmetest annotations → run affected tests → RegressionRun artifact with verdict |
| `pre-push` or `push` | **pre-push** — run all priority:critical tests + annotation-covered changed files → BLOCKED or CLEAR TO PUSH |
| `pr-review` or `pr` | **pr-review** — branch diff → map to annotations → flag unannotated files as gaps → CoverageReport artifact (no test runs) |
| `nightly` | **nightly** — run all Feature tests, mark broken ones, discover new URLs, create stub Features |
| `report` | **report** — read-only project health diagnosis: triage → auth → tests → stability → sync → coverage → code → bugs → artifacts → drift → tiered report → recommended next fix. Sub-phase: `report <phase>`. |
| `continue` | **resume** — task mentions an existing Tasks artifact id; fetch it, find the first open subtask, resume (see `modes/agent.md` §Resuming an existing artifact). |
| (empty / bare `/helpmetest`) | **full-qa** — full cycle: discover + tdd + validate |
| anything else (e.g. looks like a task description) | **dev** if it sounds like code work ("build", "add", "change", "implement", "develop", "create", "refactor", "I want to make"); otherwise **tdd** |

Mode detection is generous — "write tests for X" → tdd, "test is failing" → fix-tests, "what does this site do" → discover, "explore X" / "browse X" / "look at X" → interactive, "build X" / "add feature" / "I want to develop X" / "refactor X" / "change X" → dev. If ambiguous, pick the closest mode and narrate your choice before executing.
## 3. Load context

Load these files in this order, always:

1. `modes/shared.md` — common rules (orient first, narrate actions, auth, tools, events)
2. `modes/agent.md` — Tasks-artifact lifecycle (the accountability contract — read every time, not optional)
3. `modes/<mode>.md` — the mode-specific workflow

For `full-qa`: load `modes/discover.md`, then `modes/tdd.md`, then `modes/fix.md` — run them end to end.

These files live next to this SKILL.md. Use the `Read` tool with relative paths:

```
Read  modes/shared.md
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

Follow the loaded mode's instructions step by step, **while maintaining the Tasks artifact per `modes/agent.md`**. Narrate before and after each significant action (`modes/shared.md` §2).

## 5. When you're done

Close out every subtask in the Tasks artifact with evidence before exiting (see `modes/agent.md` §Evidence and §Final audit). Then end with a summary in the `What you can now trust works / What's still unprotected / Bugs found` format (see `modes/tdd.md`).

## Mode reference

Every mode follows the same pattern: orient → announce → act. The announce step always states what the user will have after the work, recommends a starting point, and ends with a binary scope choice (or proceeds if no ambiguity). See `modes/shared.md §1b` for the full rule.

```
agent         Tasks-artifact lifecycle only — baseline discipline, any workflow.
dev           Orchestrator for ALL code work — greenfield, new feature, change, refactor.
              Reads the situation (no project / new feature / existing / broken) and runs the right sequence:
              onboard → tdd RED → implement GREEN → interactive → discover → validate → improve → coverage.
              Triggers: 'build X', 'add feature X', 'I want to develop X', 'change X', 'refactor X', 'implement X'.
              Never build code before tests — the sequence is enforced, not suggested.
tdd           Write or fix tests. Sub-step called by dev, or use directly for targeted test work.
              Bare: presents TDD landscape (failing tests + uncovered scenarios), recommends one, asks "that or something specific?"
discover      Map a live app, PRD, or spec into Feature artifacts. Also handles fast triage sweeps
              ("find bugs", "poke around", "good test around") — outputs a three-section findings table
              (Bugs / Data quality / UX illogicalities) and documents bugs in Feature artifacts.
              Bare/no source: asks what the source is. Bare/existing artifacts: asks "extend or focus on a specific area?"
fix           Diagnose a failing test (selector, timing, auth, backend) and repair it.
              Bare: triage mode — collects status + git state, announces findings, recommends highest-priority failing test.
coverage      Read-only gap analysis — which scenarios lack tests, which tests are orphans.
              Bare: announces what user will know after, asks "full scope or critical/high first?"
regression    Given a list of changed files, run only tests affected by those files.
              Bare/no files: asks "what changed?" in one sentence framed as "after this you'll know if it's safe to push."
validate      Score existing tests against /tdd quality rules; produce a rewrite queue.
              Bare: announces what user will find, asks "full suite or critical first?"
improve       Audit all tests (I2 section comments, I3 inline comments,
              I4 assertions, I5 selectors, I6 tags), then rewrite and re-run each failing
              test in place. validate + fix in one pass.
              Bare: announces N tests, asks "all or specific filter?"
comment       Rewrite comments only — groups per-line comments into intent-based section
              headings (C1–C7: no numbering, no decorations, product context not
              implementation narration, invariants not assertion descriptions).
              No keywords, selectors, or assertions changed.
              Bare: asks which test(s) to target.
proxy         Set up localhost tunneling before testing dev servers.
              Bare/no port: asks "what port?" — then sets up + verifies before any tests are written.
ci            Set up HelpMeTest in CI: create a token, install the binary, run tests on push/PR/schedule.
              Cross-references proxy when tests target non-public URLs (staging, localhost).
terminal      Run shell commands in the test runner with the Bash keyword.
              Use for unit tests (Jest, pytest, bun test, Go test, Cargo), linting, builds.
              Cross-references ci for running as a GitHub Actions step.
              Covers GitHub Actions, GitLab CI, CircleCI, Bitbucket Pipelines, and plain shell.
api           REST/GraphQL API tests in Robot Framework via the HTTP library.
              Bare/no endpoint: asks "specific endpoint, feature area, or explore from Feature artifacts?"
ui            Screenshot-driven visual walkthrough across viewports.
              Bare: announces full audit (N pages × 3 viewports), asks "full audit or specific page?"
interactive   Drive a real cloud browser one command at a time with Robot Framework keywords.
              Use to explore pages, debug failing tests step by step, prototype a flow before writing a test,
              or verify something ad-hoc without running a full suite.
              Bare: announces intent, asks "what do you want to explore or debug?"
onboard       New project setup: create HELPMETEST.md + ProjectOverview + initial artifacts.
ssl           Write and run DomainChecker SSL keyword tests against any domain.
              Pass a domain: generates cert validity, expiry, issuer, algorithm, and SAN assertions instantly.
              Bare: asks "which domain to check?"
              Alias: domain
              Bare: runs the structured 3-question interview (source of truth, stage, goal).
full-qa       End-to-end: discover → tdd → fix — ran by default on bare /helpmetest.
change-impact git diff → @helpmetest annotations → run affected tests → RegressionRun verdict.
              Bare/no commit: announces intent, defaults to HEAD~1 diff, offers to use specific commit.
pre-push      All priority:critical tests + changed-file coverage → BLOCKED or CLEAR TO PUSH.
              Bare: announces binary verdict intent, proceeds immediately — no scope ambiguity.
pr-review     Branch diff → annotation map → gap report → CoverageReport (no test runs).
              Bare: announces analysis-only intent, proceeds immediately.
exploratory   Fast triage sweep — walk core flows, collect bugs/data-quality/UX illogicalities,
              present a three-section findings table, document bugs in Feature artifacts. No tests written.
              Bare: announces intent, asks "full app or specific area?"
nightly       Run all Feature tests, mark broken, discover new URLs, create stub Features.
              Bare: announces N tests + discovery run, proceeds immediately.
report        Read-only project health diagnosis. Layered: triage → auth → tests → stability → sync →
              coverage → code → bugs → artifacts → drift → tiered 🔴/🟠/🟡 report → recommended next fix.
              Stability uses last-10-runs history (catches the "last green, previous 5 red" flakiness).
              Code phase auto-skips if not in a code dir. No tests run, no artifacts modified.
              Bare: announces full sweep, asks "full report or just one phase?"
              Sub-tokens: report tests, report sync, report stability, etc.
```

## References

Load these from `references/` when relevant:

- The `helpmetest` CLI is the only interface (there is no MCP). For exact command syntax, options, or to confirm a command exists, run `helpmetest <command> --help` — it is the source of truth.
- `references/rf-recipes.md` — deterministic Robot Framework checks (axe-core, console errors, performance, web vitals, broken links/images, SSL).
- `references/adversarial-patterns.md` — attack patterns for forms, modals, keyboard nav, persistence.
- `references/ux-heuristics.md` — Laws of UX, Nielsen's 10, a11y — for evaluating screenshots / writing UX findings.

### Output Artifacts

#### ValidationReport

Created by `validate` mode after reviewing one or more tests.

```json
{
  "type": "ValidationReport",
  "id": "validation-[timestamp]",
  "name": "ValidationReport: [N] tests reviewed",
  "content": {
    "overview": "Reviewed [N] tests. [X] passed (A/B grade), [Y] failed (C/D/F grade).",
    "summary": {
      "total": <int>,
      "grade_distribution": { "A": <int>, "B": <int>, "C": <int>, "D": <int>, "F": <int> },
      "r11_mutagen_failures": [<test_ids>],
      "r12_framework_tests": [<test_ids>],
      "r13_overmocking": [<test_ids>],
      "bullshit_score_avg": <float>|null
    },
    "tests": [
      { "test_id": "...", "name": "...",
        "grade": "A|B|C|D|F",
        "r_scores": { "r1": "PASS|FAIL", "r2": "PASS|FAIL", ... },
        "r11_mutation_resistance": "PASS|FAIL",
        "r12_business_logic": "PASS|FAIL",
        "r13_minimal_mocking": "PASS|FAIL",
        "fail_reasons": ["R11: ...", "R12: ..."],
        "recommendation": "ship|rewrite|delete",
        "fix_notes": "<what to fix if rewrite>" }
    ],
    "actions": { "ship": [<ids>], "rewrite": [<ids>], "delete": [<ids>] }
  }
}
```

#### RegressionRun

Created by `change-impact` mode. See `modes/regression.md` for full schema.

#### CoverageReport

Created by `coverage` and `pr-review` modes. See `modes/coverage.md` for full schema.
