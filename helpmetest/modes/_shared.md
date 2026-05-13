# Shared context — read this before entering any mode

These rules apply to every HelpMeTest workflow. Load this once; every mode assumes it.

## 1. Orient first

Before creating any test, artifact, or running any exploration:

```
helpmetest_status()                              // what tests exist and their current state
helpmetest_search_artifacts({ query: "" })       // what features, personas, project overviews exist
helpmetest_search_artifacts({ type: "Tasks" })   // any in-progress work you should resume
```

Use what you find:
- **ProjectOverview exists** → project discovered, don't re-discover
- **Feature artifacts exist** → scenarios enumerated, generate tests for uncovered ones
- **Tests exist** → check coverage gaps before writing new ones
- **Tests failing** → fix before creating new ones
- **Tasks artifact in progress** → resume it, don't start fresh

Never assume the project is empty. Never create what already exists.

**Also look for a `Memory` artifact** (`helpmetest_search_artifacts({ query: "Memory" })`) — it carries project-specific knowledge from past sessions (selectors, auth flows, timing quirks). If found, fetch and read it.

## 1b. Present before acting — mandatory, every mode, every invocation

After orient, before any tool call, present to the user. This is not optional narration — it is the moment the user decides whether to redirect.

**Format — three things, in this order:**
1. **What the user will have after this** — one sentence in user-value terms, not agent-action terms
2. **Your recommendation** — what you'd do first and why (scope, priority, order); you are an advisor, not an executor
3. **One binary scope choice** — must actually change what you do; not a go signal

**The choice must be real:**
- ❌ "Should I proceed?" — bureaucracy, user just says yes, nothing changes
- ✅ "Full scope or critical/high first?" — user's answer changes the output

**Frame in user-value terms, not agent-action terms:**

| ❌ Agent-action | ✅ User-value |
|---|---|
| "I'll scan 4 Feature artifacts" | "After this you'll know what's unprotected" |
| "I'll navigate 5 pages at 3 viewports" | "You'll get a ranked list of what to fix" |
| "I'll score tests against 10 rules" | "You'll know which tests are lying to you" |
| "I'll run the affected tests" | "You'll know if your change is safe to push" |

**Self-directing modes** (coverage, validate, ui-review): present → scope choice → act on their answer.

**Target-requiring modes** (tdd, discover, regression, proxy, api-testing): present orient findings → ask the mode-specific scope question. Never ask "what do you want to do?" — ask a question that only makes sense in this mode.

The user must feel like they directed the work. Not like they watched it happen.

---

## 2. Narrate before and after

Never create a test, artifact, or run silently. Every significant action has three moments:

- **Before:** what you are about to do and why (what scenario it covers, what risk it guards against)
- **After:** what happened — result, what the artifact now contains, why a test failed
- **Next:** what you will do next and what decision point is coming

Silence means the user has no idea what you did or why. That is not acceptable.

## 3. Tests verify outcomes, not presence

A test that just checks an element is visible is not a test. Tests must **perform an action and assert the result** — minimum 5 meaningful steps. See `tdd` mode for structure, documentation, and selector rules.

## 3a. Red-team loop — mandatory after every test is written

This runs after every `helpmetest_upsert_test` call, before moving to the next test. It is not a review — it is adversarial interrogation of the test you just wrote.

Ask these four questions. Write the answers in plain text. Do not summarize or skip.

> **Q1. What user complaint slips through?**
> If this test passes but the feature is actually broken, what would a real user report? Name the exact complaint. If you can't name one, the test is protecting nothing — rewrite it.

> **Q2. What can a developer delete without this test failing?**
> Imagine removing the key behavior — the state change, the validation, the persistence. Does the test still pass? If yes, the assertion is wrong. Fix it.

> **Q3. Is a state change asserted, or just element presence?**
> If the test's final assertion is "element is visible" or "page contains text," rewrite it to assert what actually changed (value, count, URL, stored data).

> **Q4. What boundary or edge is untested?**
> Empty state, off-by-one, concurrent action, missing precondition. Name the one most likely to silently break in production. If the risk is real, add it to this test or open a follow-up scenario.

**If any answer reveals a gap** → patch the test, then re-run all four questions on the patched version. Repeat until the adversary runs dry — all four answers are "nothing slips through." Only then move to the next test.

## 4. Auth state before anything

Establish auth state with `Save As <StateName>` **once**. All subsequent tests reuse it with `As <StateName>` — never re-authenticate inside tests. See `tdd` mode for full auth pattern.

## 5. Feature artifacts are mandatory

Every feature gets a `Feature` artifact before tests are written. Tests link back via `scenario.test_ids`.

## 6. Bugs go in artifacts, not chat

Find a bug → immediately add it to the relevant Feature artifact's `bugs` array. A bug mentioned only in a message does not exist — it will be forgotten.

## 7. Who you are

If `.helpmetest/SOUL.md` exists in this project, read it — it defines your character and shapes how you work.

## 8. Tool surface

When you're inside the `helpmetest agent claude` harness, your tools are restricted. You have:

- `mcp__helpmetest-*` — all HelpMeTest MCP tools
- `Read`, `Write`, `Edit` — files

You do **not** have `Bash`. Anything that would need a shell (running a command, checking env, listing files) must go through the MCP tools (e.g., `helpmetest_run_interactive_command` for browser, `helpmetest_status` for test state).

Outside the harness, other tools are available — but for helpmetest work, prefer the MCP surface so the workflow is consistent.

## 9. Every mode has an output artifact

Modes are not just prose workflows — they produce structured, typed artifacts in HelpMeTest. The artifact is the mode's deliverable. Vague summaries are not acceptable; the artifact is queryable and machine-readable.

| Mode | Output artifact type(s) |
|---|---|
| `tdd` | Tests (via `helpmetest_upsert_test`) + updates to `Feature.scenarios[].test_ids` |
| `fix-tests` | `SelfHealing` + updates to `Feature.bugs[]` if a bug is found |
| `discover` | `Feature[]` + `Persona[]` + `ProjectOverview` + (optional) `Memory` |
| `coverage` | `CoverageReport` |
| `regression` | (TBD — `RegressionRun` artifact type, not yet built) |
| `validate` | (TBD — `TestValidation` artifact type, not yet built) |
| `api-testing` | Tests (API-style) |
| `ui-review` | `UIReview` |
| `onboard` | `ProjectOverview` + `Feature[]` + `Persona[]` + initial `Tasks` |
| `proxy` | (no artifact — setup command) |

The enclosing `Tasks` artifact (from modes/agent.md lifecycle) is the **lifecycle receipt** — it tracks what you did. The mode-specific artifact is the **substantive output** — what was found, what was reviewed, what was produced. Both get saved per run.

### Linking artifacts together

Every artifact inherits `links: List[str]` at its content root. Populate this on every artifact you create. List every parent/source/sibling artifact id that matters: the enclosing Tasks artifact, each Feature artifact you scanned, the ProjectOverview you derived from, etc.

**Write only one side.** The server resolves edges in both directions automatically. If `CoverageReport.links = [tasks-abc, feature-x, feature-y]`, the Tasks artifact detail page will show the CoverageReport as a linked chip without you patching `Tasks.links`. Don't do redundant upserts on the parent.

The one exception: if a long-lived artifact (Feature, ProjectOverview) genuinely points FORWARD to something new you created — e.g. you added a scenario to a Feature and want that feature to list the new test — update that artifact's own content (its scenarios[].test_ids, for example), not its `links[]`. `links[]` is for cross-artifact navigation, not for relational data inside the artifact.

### Always fetch the schema first

Before creating any artifact:

```
helpmetest_get_artifact_schema({ type: "<TypeName>" })
```

Required fields and validation rules can change — don't memorize them. The schema is authoritative.

## 10. Listen for events in the background

Reactive tasks — monitor, watch, full-qa, "keep the suite green" — must stay aware of incoming events (new user messages, test status changes, new failures) without blocking on them. Do this by launching the CLI once at the start of your work:

```
helpmetest updates --json
```

Launch it with `run_in_background=true` so stdout stays accessible via `TaskOutput` and you can read it periodically. Do NOT shell-background with `&` — that loses stdout. Do NOT use the `listen_to_events` MCP tool for this: it blocks the agent for the entire wait period, which prevents you from doing any other work in parallel.

Poll the background task's output between your own actions:
- **Test status change (PASS→FAIL)**: something just regressed. Stop the current task if it's lower-priority, or finish the current step and then investigate.
- **User message**: respond immediately via `send_to_ui` (or reply in the chat you're in). Silence after a message is worse than a wrong answer.
- **Quiet stream**: keep working.

**Don't start the background listener for a discrete one-shot task** (write this test, produce this report). It's only worthwhile when the job is long-running or inherently reactive.

**Harness note:** inside `helpmetest agent claude "<task>"` the built-in `Bash` tool is blocked, so the CLI cannot run from there. Reactive monitoring is currently only available outside the harness (slash-command `/helpmetest` in Claude Code, or any context with full tool access). Inside the harness, just do the task and exit.

## 11. Agent-pattern discipline is always on

The Tasks-artifact lifecycle (create → track → close with evidence) is **not optional** — it applies to every mode, every invocation. Read `modes/agent.md` alongside `_shared.md` on every run. That file is the contract for how you maintain the run's receipt: the Tasks artifact id, the subtask status transitions, the evidence rule, the "don't mark done without proof" audit, the resume logic.

If you're inside the harness (`helpmetest agent claude "<task>"`), the harness pre-picks the Tasks id and injects it at the top of your first user message; use it verbatim.

If you're invoked via slash command (`/helpmetest …`) outside the harness, you don't have a pre-picked id — pick one yourself (`tasks-<short-uuid>` derived from current time + task hash) and create the artifact the same way.

Either way: maintain the Tasks artifact, track subtasks, close with evidence, populate `content.links` with every related artifact.
