# Shared context — read this before entering any mode

These rules apply to every HelpMeTest workflow. Load this once; every mode assumes it.

## 1. Orient first

Before creating any test, artifact, or running any exploration:

```bash
helpmetest status                        # what tests exist and their current state
helpmetest artifact list                 # what features, personas, project overviews exist
helpmetest artifact list --type Tasks    # any in-progress work you should resume
```

Use what you find:
- **ProjectOverview exists** → project discovered, don't re-discover
- **Feature artifacts exist** → scenarios enumerated, generate tests for uncovered ones
- **Tests exist** → check coverage gaps before writing new ones
- **Tests failing** → fix before creating new ones
- **Tasks artifact in progress** → resume it, don't start fresh

Never assume the project is empty. Never create what already exists.

**Also look for a `Memory` artifact** (`helpmetest search Memory`) — it carries project-specific knowledge from past sessions (selectors, auth flows, timing quirks). If found, fetch and read it with `helpmetest artifact get <id>`.

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

**Self-directing modes** (coverage, validate, ui): present → scope choice → act on their answer.

**Target-requiring modes** (tdd, discover, regression, proxy, api): present orient findings → ask the mode-specific scope question. Never ask "what do you want to do?" — ask a question that only makes sense in this mode.

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

This runs after every test create/update call, before moving to the next test. It is not a review — it is adversarial interrogation of the test you just wrote.

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

- `Bash` — for `helpmetest` CLI commands
- `Read`, `Write`, `Edit` — files

Use the `helpmetest` CLI for all HelpMeTest operations. Key commands:
- `helpmetest login` — authenticate via browser; saves token to `.helpmetest/config.yaml`
- `helpmetest login --token <token>` — skip browser; validate and save a known token directly (useful when you already have a token from the dashboard or CI secret)
- `helpmetest status` — test state
- `helpmetest interactive "<Robot Framework keyword>"` — browser automation
- `helpmetest test run <name-or-tag-or-id>` — run tests
- `helpmetest artifact list` / `helpmetest search <query>` — find artifacts
- `helpmetest artifact get <id>` — fetch artifact content
- `helpmetest artifact schema <type>` — get artifact schema
- `helpmetest artifact upsert --id <id> --type <type> --name <name> --content '<json>'` — create/update artifact
- `helpmetest test create --name <name> --tags <tags> --content '<robot>'` — create test
- `helpmetest test update <id> ...` — update test
- `helpmetest proxy start` — start proxy tunnel (see `proxy` skill for syntax and domain setup)
- `helpmetest upload <file>` — upload file
- `helpmetest open test <id>` — open test in browser

## 9. Every mode has an output artifact

Modes are not just prose workflows — they produce structured, typed artifacts in HelpMeTest. The artifact is the mode's deliverable. Vague summaries are not acceptable; the artifact is queryable and machine-readable.

| Mode | Output artifact type(s) |
|---|---|
| `tdd` | Tests (via `helpmetest test create` / `helpmetest test update`) + updates to `Feature.scenarios[].test_ids` |
| `dev` | `Tasks` (orchestration receipt) + all artifacts produced by sub-modes it runs |
| `fix` | `SelfHealing` + updates to `Feature.bugs[]` if a bug is found |
| `discover` | `Feature[]` + `Persona[]` + `ProjectOverview` + (optional) `Memory` |
| `coverage` | `CoverageReport` |
| `regression` | (TBD — `RegressionRun` artifact type, not yet built) |
| `validate` | (TBD — `TestValidation` artifact type, not yet built) |
| `api` | Tests (API-style) |
| `ui` | `UIReview` |
| `onboard` | `ProjectOverview` + `Feature[]` + `Persona[]` + initial `Tasks` |
| `proxy` | (no artifact — setup command) |

The enclosing `Tasks` artifact (from modes/agent.md lifecycle) is the **lifecycle receipt** — it tracks what you did. The mode-specific artifact is the **substantive output** — what was found, what was reviewed, what was produced. Both get saved per run.

### Linking artifacts together

Every artifact inherits `links: List[str]` at its content root. Populate this on every artifact you create. List every parent/source/sibling artifact id that matters: the enclosing Tasks artifact, each Feature artifact you scanned, the ProjectOverview you derived from, etc.

**Write only one side.** The server resolves edges in both directions automatically. If `CoverageReport.links = [tasks-abc, feature-x, feature-y]`, the Tasks artifact detail page will show the CoverageReport as a linked chip without you patching `Tasks.links`. Don't do redundant upserts on the parent.

The one exception: if a long-lived artifact (Feature, ProjectOverview) genuinely points FORWARD to something new you created — e.g. you added a scenario to a Feature and want that feature to list the new test — update that artifact's own content (its scenarios[].test_ids, for example), not its `links[]`. `links[]` is for cross-artifact navigation, not for relational data inside the artifact.

### Always fetch the schema first

Before creating any artifact:

```bash
helpmetest artifact schema <TypeName>
```

Required fields and validation rules can change — don't memorize them. The schema is authoritative.

## 10. Listen for events in the background

Reactive tasks — monitor, watch, full-qa, "keep the suite green" — must stay aware of incoming events (new user messages, test status changes, new failures) without blocking on them. Do this by launching the CLI once at the start of your work:

```
helpmetest updates --json
```

`shared.md`

Poll the background task's output between your own actions:
- **Test status change (PASS→FAIL)**: something just regressed. Stop the current task if it's lower-priority, or finish the current step and then investigate.
- **User message**: respond immediately (write to stdout or reply in the chat you're in). Silence after a message is worse than a wrong answer.
- **Quiet stream**: keep working.

**Don't start the background listener for a discrete one-shot task** (write this test, produce this report). It's only worthwhile when the job is long-running or inherently reactive.

**Harness note:** inside `helpmetest agent claude "<task>"` reactive monitoring is only useful for long-running or reactive tasks — for a discrete one-shot task, just do the task and exit.

## 11. Agent-pattern discipline is always on

`shared.md`

If you're inside the harness (`helpmetest agent claude "<task>"`), the harness pre-picks the Tasks id and injects it at the top of your first user message; use it verbatim.

If you're invoked via slash command (`/helpmetest …`) outside the harness, you don't have a pre-picked id — pick one yourself (`tasks-<short-uuid>` derived from current time + task hash) and create the artifact the same way.

Either way: maintain the Tasks artifact, track subtasks, close with evidence, populate `content.links` with every related artifact.


## 12. Use interactive as your eyes — always

You have a real browser available at any time via `helpmetest interactive`. Use it. Don't guess what an app looks like, what selectors exist, or whether a flow works — go look.

This applies to all work, not just QA: writing a feature, debugging a bug, reviewing a UI, writing a test. If the app is running, open it.

**For a local dev server**, the cloud browser can't reach `localhost` directly — set up a proxy tunnel first. Read the `proxy` skill for exact syntax and domain setup, then come back and use the domain it gives you in `interactive` commands.

**When to reach for it:**
- Starting work on any feature → navigate to the relevant page first, see what's actually there
- Selector in a test is wrong → go find the real one in the Interactive section
- "Does this work?" → go check, don't speculate
- Writing a test → prototype the flow interactively first, then copy into `helpmetest test create`
- Something looks broken → open it, look at Network for 4xx/5xx, look at the page state

The Interactive section of every response lists ready-to-paste RF commands for every element on the page. Use those — don't invent selectors.