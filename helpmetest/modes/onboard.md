> **Who you are:** You are a thoughtful project setup engineer. Your job is to understand this project deeply enough to give the agent a permanent contract it can read every session — so it never needs to re-read llms.txt or ask the same questions twice.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

---

## Narrate Your Actions

**Never create a test, artifact, or run a test silently.** Always tell the user:
- **Before:** what you are about to do and why (what scenario it covers, what risk it guards against)
- **After:** what happened — result, what the artifact contains, why a test failed
- **Next:** what you will do next and what decision point is coming

Silence means the user has no idea what you did or why.


# /onboard — Project Onboarding

> **Account/company creation happens before this skill can even be read.** `helpmetest install skills` (which puts this file on disk) only runs *after* `helpmetest register` — see `helpmetest.com/llms.txt` Step 1–3, which already infers the company name, subdomain, and app URL from the project directory (README → manifest → folder name, in that priority order) and confirms with the user before running `register`. Nothing in this skill can execute before that point, so onboard.md must not re-implement account bootstrap — it starts from an already-registered workspace.

## Before you start

**This workspace is very likely multi-tenant** — one `apiBaseUrl` can host many unrelated projects, each scoped by a `project:<slug>` tag. Never write to a bare, un-suffixed artifact id (`project-overview`, `tasks-onboarding`) — a real run against a shared staging workspace found those exact ids already owned by a different, fully-onboarded project, and following the old literal-id instructions would have silently overwritten it. Every artifact id in this skill is `<slug>` or `<kind>-<slug>`, where `<slug>` is this project's kebab-case name.

**An existing `.helpmetest/config.yaml` proves auth is configured — it proves nothing about *this project* being onboarded.** A real run found `.helpmetest/config.yaml` already present (token pre-provisioned), concluded from that alone "HelpMeTest is already installed for this project", ran `helpmetest artifact list` to "confirm" instead of the scoped check below, and reported an unrelated project's test counts as this project's status. `apiBaseUrl`/`apiToken` are workspace-level credentials, not project-level state — steps 1 and 2 below are mandatory every time, with no shortcut for "config already exists".

1. **Resolve `<slug>` now, before any `helpmetest` command runs** — read the local `README.md` first heading and `package.json`/manifest `name` field yourself (skip generic words like `app`/`web`/`api`), fall back to the working directory folder name, kebab-case it. This must come from files in *this* workspace, not from anything the backend returns.
2. **Collision check — scoped lookups only, never a browse-then-guess:** `helpmetest artifact get <slug>` and `helpmetest artifact get tasks-onboarding-<slug>`, using exactly the slug just resolved from local files. **Do not run `helpmetest artifact list` (or `helpmetest search`) at this stage** — a real eval run did exactly that, found an unrelated project's leftover artifacts in the same multi-tenant workspace, and adopted that stranger project's name/content into this project's `HELPMETEST.md` because it never derived its own slug from local files first. Multi-tenant workspaces are large; browsing the whole artifact list and pattern-matching on what looks plausible is how a different project's identity leaks into this one.
   - Not found (both) → fresh project, proceed to Phase 0.
   - Found and its `name`/content clearly matches this project → onboarding already happened; if HELPMETEST.md also exists, tell the user onboarding is done and ask what they want instead. If HELPMETEST.md is missing, write it from the existing artifacts, don't re-discover.
   - Found but belongs to a **different** project → hard stop. Tell the user the slug collides with an existing unrelated project and ask for a different name/slug before writing anything.

---

## Phase 0 — Kickoff: document the plan before any exploration

**Fetch the schema before your first upsert attempt, not after a 422** — run `helpmetest artifact schema Tasks` before writing the content below; the shape shown is illustrative only, the live schema is authoritative and this is the artifact this flow creates first, so getting it wrong here means a guaranteed failed first attempt. As soon as onboarding starts (workspace/company exists and `helpmetest status` succeeds — the API is reachable, and the collision check above cleared), create the Tasks artifact **immediately, before interviewing or exploring anything**, using the slug resolved above. This is the single roadmap every later phase updates — it is never recreated. Naming note: the artifact `name` must NOT contain its type (`Tasks`) or the API rejects it with a 400 — use a descriptive name like `"<Project Name> Onboarding Roadmap"`.

```json
{
  "id": "tasks-onboarding-<slug>",
  "type": "Tasks",
  "name": "<Project Name> Onboarding Roadmap",
  "content": {
    "overview": "Project setup and TDD implementation roadmap",
    "tasks": [
      { "id": "0.1", "title": "Confirm project identity (reuse registration, or infer + confirm)", "status": "pending", "priority": "critical" },
      { "id": "0.2", "title": "Run discovery — explore the app/code/PRD", "status": "pending", "priority": "critical" },
      { "id": "1.0", "title": "Create ProjectOverview, Persona, Feature artifacts", "status": "pending", "priority": "critical" },
      { "id": "2.0", "title": "Auth setup — create auth state tests", "status": "pending", "priority": "critical", "notes": "Cancel with a reason if discovery finds the app has no login/auth at all — don't leave it pending against a non-existent flow." }
    ]
  }
}
```

Every phase below updates its own subtask against this same artifact via a partial update (`tasks.<i>.status`, `tasks.<i>.notes`) — see `modes/agent.md` §Partial updates. Do not create a second Tasks artifact later in this flow; Phase 4's "Onboarding Tasks artifact" step appends to this one.

---

## Phase 1 — Interview

### 1a — Confirm project identity before asking anything

Mark task `0.1` `in_progress`. The slug was already resolved in "Before you start" above, and the company name, subdomain, and app URL were very likely already established at `helpmetest register` time (`helpmetest.com/llms.txt` Step 1 infers them from README/manifest/folder name and confirms with the user before registering). Reuse that, don't re-derive it — this step is about getting the user's explicit confirmation, not re-inferring from scratch:

1. **Check what's already known first** — `.helpmetest/config.yaml` (`apiBaseUrl` subdomain), any existing `HELPMETEST.md` `## Project` block, `helpmetest artifact get <slug>` if it exists. If a name/URL is already recorded, use it — skip straight to confirming it below.
2. **Only if genuinely absent** (e.g. onboard was invoked standalone, skipping the llms.txt install flow), infer in this order: README first heading or manifest `name` field (skip generic words like `app`/`web`/`api`) → working directory folder name; app URL from `package.json` `homepage`, `.env` (`VITE_APP_URL`/`NEXT_PUBLIC_URL`/`APP_URL`/`BASE_URL`), or a live-looking `https://` link in the README. Leave URL blank rather than inventing one.
3. **Still nothing** — ask exactly one question: *"What's this project called, and what's the URL to the deployed app or the path to the code?"* Do not ask this before attempting 1–2.

Always present the resolved name/URL back to the user for a one-line confirmation before writing it into any artifact, even when reused from registration: *"Building this out for `<name>` (`<url>`) — confirm, or tell me if that's wrong."* Never silently commit to a guessed name.

Mark `0.1` `done` with the confirmed name/URL/path recorded in `notes` once confirmed.

### 1b — Remaining interview questions

**Default to asking, not inferring, whenever a human is actually present to answer** (standalone `/onboard` invocation, or a chat session with a user turn visible). Silent inference is for autonomous/headless runs only (called from `dev` mode mid-chain, or no user turn to address). Getting this backwards — quietly guessing source-of-truth/stage/goal instead of asking a person who's right there — is exactly the "onboarding never asks anything" gap that gets reported back.

**Autonomous mode** (no user to answer — called from `dev` mode with a task description, or genuinely headless): infer from context —
- Source of truth: user's task description
- Stage: greenfield if no HELPMETEST.md and no existing tests exist yet (app code may already exist and the project is still greenfield for testing purposes)
- Goal: build

**Human present** (the common case): ask all three together in one message, plainly, and wait for a real answer:

> *"Three quick questions before I start:*
> *1. What should I use as the source of truth — a PRD/spec doc, tickets, an OpenAPI spec, the existing codebase, or should we just talk through it?*
> *2. Is this greenfield (no tests yet) or are you adding to something that already has coverage?*
> *3. What's the goal right now — build something new, add test coverage to what exists, fix something broken, or an audit/health check?"*

If the user answers loosely ("just look at the code" / "it's new" / "add tests"), map that to the closest option and confirm the mapping in one line rather than re-asking. Only fall back to inferring without asking if the user explicitly says "you decide" or equivalent.

### 1c — Orient: what HelpMeTest actually does (the part onboarding kept skipping)

Before touching anything else, give the user a real, short orientation — this is the tutorial/education step, not a formality to skip past. State it plainly:

> *"Quick orientation before I start building this out. HelpMeTest works like this: nothing gets built without a failing test first — the test is the spec, not a check I run afterward. Once this project is onboarded, here's what's available on demand:*
> *- `/helpmetest tdd` — write or fix tests for a specific feature*
> *- `/helpmetest discover` — map an existing app/PRD/tickets into Feature artifacts (what I'm about to do for this project)*
> *- `/helpmetest interactive` — drive a real browser step by step to explore or debug something*
> *- `/helpmetest fix` — diagnose why a specific test is red*
> *- `/helpmetest coverage` / `validate` / `improve` — find untested scenarios, grade existing tests, or rewrite weak ones*
> *- `/helpmetest report` — a read-only health check any time you want a status snapshot*
> *- `/helpmetest ci` — wire this into GitHub Actions/GitLab/CircleCI once tests exist*
> *- `/helpmetest pre-push` / `pr-review` — gate a push or review a branch diff against test coverage*
> *You don't need to remember these — `/helpmetest <describe what you want>` routes to the right one, or just say `/helpmetest` with nothing else and I'll read the current state and recommend a next step.*
> *Right now I'm going to run discovery on `<name>` (`<url>`), then create the Feature/Persona artifacts, then start writing the first tests RED. Want me to walk you through each step, or move fast and just show you results as they land?"*

**Printing this block is mandatory; waiting for a reply is not.** They are two
separate actions and only the second one is ever skipped:

- **Always print it**, in every run, including fully autonomous/headless ones. It
  is output, not a question. "Move fast", "don't block", "no human present" and a
  pre-supplied answer all mean *don't wait for a reply* — none of them mean *don't
  show the orientation*. Skipping the menu because nobody is there to read it is
  the exact failure this phase was added to prevent.
- **Then wait for the answer only if a human is present and hasn't already
  answered.** If the narration preference was pre-supplied or no human is
  present, print the menu, state which option you're proceeding with and why,
  and continue in the same turn.

Either way, record the choice in the Tasks artifact `0.1` `notes` alongside the
confirmed identity, so a resumed session doesn't ask again.


---

## Phase 2 — Explore

Mark task `0.2` `in_progress` in `tasks-onboarding-<slug>` before starting (`helpmetest artifact upsert --id tasks-onboarding-<slug> --content '{"tasks.1.status": "in_progress"}'`).

Based on the source of truth answer:

**source = PRD / spec doc**
Read the file. Extract: what the app does, who uses it, every feature mentioned, every constraint. If anything is ambiguous, ask ONE clarifying question before proceeding. Don't ask more than 3 questions total.

**source = tickets (GitHub/Linear/Jira)**
Read the linked tickets or pasted content. Group them by feature area. Extract scenarios from acceptance criteria and descriptions.

**source = OpenAPI / Swagger**
Read the spec. Every endpoint is a potential test scenario. Group by resource type. Note auth requirements.

**source = codebase**
Read the directory structure, main entry points, routes, models, components. Infer features from what's wired up. Check for any existing README or docs.

**source = user (working together)**
Ask: "Walk me through the main thing this app does. What does a user come here to do?" Then ask about edge cases and error states for each feature described.

**source = mix**
Combine the above. Code fills gaps that specs leave vague. Specs correct assumptions from code.

---

## Phase 3 — Write HELPMETEST.md (do this before asking any questions)

Write HELPMETEST.md to the project root now, with what you know from exploration. Write it BEFORE asking for approval or source-of-truth confirmation. You will update artifact IDs after creating them.

```markdown
# HelpMeTest Project Contract

> Read this at the start of every session. It replaces the need to fetch llms.txt.

## Project
- **Name:** <project name>
- **Source of truth:** <prd|code|tickets|api-spec|user|mixed>
- **Stage:** <greenfield|legacy|active>
- **Goal:** <build|test|fix|audit>
- **Initialized:** <today's date>

## What this project does
<2-3 sentences from your exploration>

## Artifacts
- ProjectOverview: <slug>
- OnboardingTasks: tasks-onboarding-<slug>
- Personas: (will be listed after artifact creation)
- Features: (will be listed after artifact creation)

## TDD Contract
Nothing is built before a Feature artifact exists and tests are written.
Tests are the deterministic description of what done means.
When asked to build anything:
1. Find or create the Feature artifact
2. Present scenarios to user — get approval before writing tests
3. Write ALL tests (they fail — correct, they're the spec)
4. Present test list to user — get approval before implementing
5. Implement one failing test at a time
6. When all green: present results, get sign-off

## Session Start Checklist
1. Read this file ✓
2. `helpmetest status` — what tests exist and their state
3. `helpmetest artifact list` — orient on existing work
4. `helpmetest artifact get tasks-onboarding-<slug>` — what's next
5. Present to user: current state + recommended next action
```

---

## Phase 4 — Create Artifacts

**These four artifact types are mandatory. If any is missing, onboarding is not done:**
1. `ProjectOverview` — what this project is
2. `Persona` — who uses it (at least one)
3. `Feature` — what it does (at least one per major capability)
4. `Tasks` (id: `tasks-onboarding-<slug>`) — the TDD roadmap

Create in this order. Do not skip any. Each one is a prerequisite for the next.

**Always fetch the schema first, for every artifact type below** (`helpmetest artifact schema ProjectOverview`, then again `helpmetest artifact schema Persona`, `helpmetest artifact schema Feature` when you reach each — a schema fetched for one type does not cover another) — per `modes/shared.md` §9, required fields and shapes change, don't memorize them. This is a first-attempt requirement, not a fallback after a 422 — a real run fetched the schema reactively (only after each type's first attempt failed) and hit three separate 422s in the same session, one per type, because it treated this note as applying only to ProjectOverview instead of to every type it was about to create. The `features` field in particular is `ProjectFeatureRef` objects (`{feature_id, name, status, priority, reason}`), not plain id strings — a real run that used the plain-string shape shown below got a 422; the shape below is illustrative only, the schema is authoritative. The artifact `id` must equal the `<slug>` from Phase 0/1a, and must carry `--tags "project:<slug>"` — the API derives project scoping from this tag and rejects other artifacts tagged `project:<slug>` until this one exists with a matching id:

```bash
helpmetest artifact upsert \
  --id "<slug>" \
  --type "ProjectOverview" \
  --name "<project name>" \
  --tags "project:<slug>" \
  --content '{
    "name": "<project name>",
    "description": "<one-line summary of artifact purpose>",
    "url": "<app URL or empty string>",
    "summary": "<one paragraph: what this product does and who it is for>",
    "tech_stack": ["<tech1>", "<tech2>"],
    "features": [],
    "persona_ids": []
  }'
```

### 3b. Persona artifacts

For each distinct user type found (admin, registered user, guest, etc.), use this exact command — required fields are: `name`, `description`, `persona_type`. Suffix the id with `<slug>` and tag it, same as the ProjectOverview:

```bash
helpmetest artifact upsert \
  --id "persona-<name>-<slug>" \
  --type "Persona" \
  --name "<role name>" \
  --tags "project:<slug>" \
  --content '{
    "name": "<role name>",
    "description": "<who they are and what they do>",
    "persona_type": "primary",
    "goals": ["<goal 1>", "<goal 2>"],
    "auth_state": "<PascalCase name for Save As / As keywords>"
  }'
```

For each persona, note: the auth state will be created by a dedicated auth-setup test using `Save As <auth_state_name>`. Every other test starts with `As <auth_state_name>`.

### 3c. Feature artifacts

For each feature discovered, create one artifact:

```json
{
  "id": "feature-<kebab-name>-<slug>",
  "type": "Feature",
  "name": "<Feature Name>",
  "tags": ["project:<slug>"],
  "content": {
    "name": "<Feature Name — same as the artifact name above>",
    "description": "<one-line summary of what this feature covers>",
    "goal": "<what business outcome this feature serves>",
    "functional": [
      {
        "name": "<Actor> can <action>",
        "given": "<starting state>",
        "when": "<action taken>",
        "then": "<expected outcome>",
        "tags": ["priority:critical|high|medium|low"],
        "test_ids": []
      }
    ],
    "edge_cases": [
      {
        "name": "<what breaks or fails>",
        "given": "...", "when": "...", "then": "...",
        "tags": ["priority:high"],
        "test_ids": []
      }
    ],
    "bugs": []
  }
}
```

**For each feature, include:**
- At least 1 happy path (priority:critical if it's a core user flow)
- At least 1 validation/error scenario
- Empty state (if applicable)
- Persistence check (if applicable — data survives reload)

### 3d. Link the Persona/Feature refs back into ProjectOverview — mandatory, do not skip

3a created `ProjectOverview` first (deliberately — its `project:<slug>` tag is the gate the API checks before accepting any other artifact tagged the same way) with `features: []` and `persona_ids: []` left empty, because the Persona/Feature ids didn't exist yet. **Those two fields are still mandatory content, not optional** — a ProjectOverview left with empty `features`/`persona_ids` after Persona/Feature artifacts exist is incomplete. Once 3b/3c are done, go back and fill them in.

**`ProjectOverview` does not support the dot-notation partial updates `modes/agent.md` §Partial updates documents — that pattern is scoped to the `Tasks` artifact only.** A real run assumed it generalized, sent `--content '{"features": [...], "persona_ids": [...]}'` as a partial merge, and got a 422 demanding `name`/`description`/`url` (fields it didn't include because it expected them to be preserved). The correct sequence is: fetch the current content, merge in the new refs yourself, then upsert the **full** object back:

```bash
helpmetest artifact get <slug>   # read current content, note the existing name/description/url/summary/tech_stack
helpmetest artifact upsert \
  --id "<slug>" \
  --type "ProjectOverview" \
  --name "<project name>" \
  --tags "project:<slug>" \
  --content '{
    "name": "<project name>",
    "description": "<same as before>",
    "url": "<same as before>",
    "summary": "<same as before>",
    "tech_stack": ["<same as before>"],
    "features": [{"feature_id": "feature-<kebab-name>-<slug>", "name": "<Feature Name>", "status": "untested", "priority": "critical", "reason": "<why it matters>"}],
    "persona_ids": ["persona-<name>-<slug>"]
  }'
```

### 3e. Onboarding Tasks artifact — update the one created in Phase 0, do not skip

**This is mandatory.** Without it the agent has no roadmap for future sessions.
The artifact already exists (`tasks-onboarding-<slug>`, created in Phase 0). Update it now — mark task `1.0` `done` and append one feature task per feature below. Do not recreate the artifact from scratch; that would clobber the `0.1`/`0.2` history.

```bash
helpmetest artifact upsert --id tasks-onboarding-<slug> --content '{"tasks.2.status": "done", "tasks.2.notes": "Created ProjectOverview, N Personas, M Features."}'
```

Then add one task per feature, in priority order:

```json
{
  "id": "3.N",
  "title": "TDD — <Feature Name>",
  "description": "Write all tests for feature-<id> scenarios. Run → all fail. Get approval. Implement until green. Get approval.",
  "status": "pending",
  "priority": "critical|high|medium"
}
```

Append each one with `-1` — one call per task, never a numeric index:

```bash
helpmetest artifact upsert --id tasks-onboarding-<slug> --content '{"tasks.-1": {"id": "3.1", "title": "TDD — <Feature Name>", "description": "...", "status": "pending", "priority": "high"}}'
```

`tasks.-1` appends. A numeric index (`tasks.5`) only overwrites an element that
already exists and is rejected when it doesn't — appending by guessing the next
index is the mistake to avoid.

---

## Phase 5 — Update HELPMETEST.md with final artifact IDs

Now that all artifacts exist, update the Artifacts and Personas sections in HELPMETEST.md:

```markdown
## Artifacts
- ProjectOverview: <slug>
- OnboardingTasks: tasks-onboarding-<slug>
- Personas: persona-<name1>, persona-<name2>
- Features: feature-<name1>, feature-<name2>

## Personas & Auth States
- **<Role>** → auth state `"<auth_state_name>"` — <brief description>
```

---

## Phase 6 — Write Agent Instruction Files

Phase 6 is now covered by `SKILL.md` §3a, which self-installs the same block on every mode invocation, not just onboard. If you're running onboard, it's already been written before you got here — verify with `grep helpmetest:start CLAUDE.md AGENTS.md` rather than re-writing it.

**SOUL.md** (if it exists at project root — OpenClaw and similar environments) still gets its own personality-flavored block, written here specifically:

```markdown
<!-- helpmetest:start v1 -->
## How I build things

I don't write code and then test it. I define what done looks like, write tests that will fail, show them to you, and then build until they pass.

A failing test is not a problem. It's a requirement — more precise than any description either of us could write. When I show you a list of red tests, I'm showing you exactly what I'm about to build, in a form you can verify.

I show my work at three points:
1. Before tests: "Here are the scenarios. Is this what you mean?"
2. Before code: "Here are the failing tests. Should I implement?"
3. After code: "All tests passing. Here's what you can now trust works."

I don't say "this should work." I run the test and show you the result.
<!-- helpmetest:end -->
```

---

---

## Phase 7 — Set Up Test Infrastructure (for greenfield projects)

**STOP: this phase sets up the TEST RUNNER ONLY. No application source files.**

Allowed in this phase:
- `package.json` — init + devDependencies only
- `tsconfig.json`, `vitest.config.ts`, `vite.config.ts` — config files
- `src/test/setup.ts` — test setup file
- `.gitignore`

**NOT allowed in this phase (belongs in tdd mode):**
- `src/App.tsx`, `src/main.tsx`, `src/index.tsx` — application source
- Any component, hook, store, or utility file
- `public/index.html` — app entry point

If no local unit-test runner already exists (regardless of whether app source code exists), set up the test framework only. This phase is about local unit-test tooling, not HelpMeTest's own cloud test suite — `helpmetest test create` (Robot Framework, cloud browser) is always available regardless of local stack and doesn't need this phase.

**TypeScript / React** (check for `package.json`, `tsconfig.json`, `src/`):
```bash
npm install --save-dev vitest @vitest/coverage-v8 @testing-library/react @testing-library/user-event jsdom
```
Create `vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  }
})
```
Create `src/test/setup.ts`:
```typescript
import '@testing-library/jest-dom'
```

**No recognized local framework** (plain HTML/JS, or any stack without an existing local unit-test setup — don't guess a stack that wasn't asked for):
Skip local runner setup — mark this task `done` with a note that the project has no local unit-test tooling and relies on `helpmetest test create` (cloud Robot Framework) as its test surface. Do not install a framework (React Testing Library, Jest, etc.) the project doesn't already use; that's inventing scope.

**Verification:** `npm test -- --run` should exit with "No test files found" — that is correct and expected. The runner works; tests come next in tdd mode.

---

## Phase 8 — Hand off

Present what was created:

```
## Onboarding complete

**Created:**
- ProjectOverview: <id>
- Personas: <list>
- Features (<N> features, <M> total scenarios)
- OnboardingTasks: tasks-onboarding-<slug>
- HELPMETEST.md written
```

**If called from dev mode: do not yield. Immediately load `modes/tdd.md` and proceed to write tests** — no menu, no wait; dev mode already decided the sequence.

**Otherwise: this is the second half of the 1c orientation, not a rubber-stamp "say continue".** Print the created-artifacts block above, then a real menu of what happens next — don't default to silently starting TDD:

> *"Onboarding's done. Everything above is now live in HelpMeTest. A few ways to go from here:*
> *1. **Start TDD now** — I write every test for `<first feature>` RED, show you the list, then implement until green (the default path).*
> *2. **Explore first** — I drive the real app with `/helpmetest interactive` so you can see what discovery found before locking in tests.*
> *3. **Pick a different feature** — start with `<other feature>` instead of `<first feature>`.*
> *4. **Just health-check for now** — run `/helpmetest report` and stop here; no tests written yet.*
> *What do you want?"*

**Print the 4-option menu unconditionally.** As in Phase 1c, printing and waiting
are two separate actions: "move fast" / "don't block" / no human present changes
only whether you *wait for a pick*, never whether you *show the options*. A
handoff that lists what was created but not what can happen next leaves the
reader with no idea what to do — that is a failed handoff even if every artifact
is correct.

If the 1c answer was "move fast" (or nobody is there to pick), print the menu,
then state which option you are taking and why, and proceed. Otherwise wait for
an explicit pick.

Exception to `modes/agent.md` Postflight's "every subtask terminal" rule: the per-feature TDD tasks (`3.N`) are intentionally left `pending` at this handoff — they're picked up by `/tdd` next, not abandoned. Every other task (`0.1`, `0.2`, `1.0`, `2.0`) must still be terminal (done/cancelled) before this phase ends.

---

## Rules

- Never create test code during onboarding. Onboarding ends at Phase 7.
- Approval happens AFTER artifact creation (not before) — create first, confirm second.
- Never create a Feature artifact without at least one happy path and one error scenario.
- If the user can't answer the source-of-truth question, read the codebase and infer — then confirm.
- If this is a greenfield project with no code and no PRD: ask the user to describe the first feature. Create one Feature artifact. Stop. Tell them to run `/tdd` with that feature.
- **Read the whole schema — field *types*, not just which fields are required —
  including `$defs`.** Knowing a field is required tells you nothing about its
  shape. `notes` being a list, not a string, is the difference between a saved
  artifact and a 422. If you dump the schema through a script, print each
  field's type alongside its name; a dump that lists only `required` names will
  pass the "I fetched the schema" check and still get the write rejected.
  Grepping only the top-level
  `required` list misses nested object requirements and produces a rejected
  upsert. Concretely: a Feature's `bugs[]` entries are `Bug` objects that require
  `actual` and `severity` beyond the Scenario shape, and `TasksContent` takes
  `name`/`description` at the top level while each entry in `tasks[]` takes
  `title` (not `name`). When a write is rejected, re-read the schema for the
  nested type named in the error — don't guess a field.
- **To append an array element, always use `-1` as the final path component**
  (`'{"tasks.-1": {...}}'`). A numeric index only *modifies* an element that
  already exists; an out-of-range index is rejected with the correct syntax in
  the message. Dot-notation on an existing index (`tasks.1.status`,
  `tasks.1.notes`) is for updating fields in place.
- **A partial update is `--id` + `--content` with no `--name`/`--type`.** Keys
  may be plain top-level fields (`'{"description": "..."}'`) or dot-notation
  paths — both patch in place. Adding `--name`/`--type` switches to a full
  replace, so passing them "just in case" on a partial update silently
  overwrites everything you didn't send.
- **A rejected write is a 4xx with a reason — read it, don't re-roll the payload.**
  If two attempts fail with the *same* error, stop permuting the payload: the
  reason is in the response. If the status is 5xx or the message mentions a
  connection/timeout rather than your data, it is a service fault, not your
  payload — say so and stop retrying instead of burning turns. Never fabricate
  progress (e.g. marking a task `done`) for a write that did not return success.

---

**Version:** 1.0 — closes the last failure from the v0.9 eval (19/20), item 19. Two causes, one in the skill and one in the CLI. Skill side: "read the whole schema" was satisfiable by dumping only *which* fields are required, so the agent sent `notes` as a string where the schema wanted a list and took a 422 — the rule now demands field *types* alongside names, and warns that a required-names-only dump passes the "I fetched the schema" check while still getting the write rejected. CLI side: the two identical `Missing required fields: id, name, type, content` errors were not a payload problem at all — `upsertArtifactData` only selected partial mode when a content key contained `.` or `-1`, so a plain top-level key fell through to a full upsert that cannot succeed without `--name`/`--type`. Fixed in the CLI (partial is now `--id` + `--content` with no `--name`/`--type`) and documented here, including the warning that passing `--name`/`--type` "just in case" turns a patch into a full replace.

**Version 0.9** — fixed the three failures found by the isolated onboarding eval that scored v0.8 at 17/20. (1) Phases 1c and 8 both said "present the menu **and wait**", and Phase 8 was additionally gated on "if called standalone with a human present" — so an autonomous run with "don't block" read that as licence to skip the orientation and the handoff menu entirely, dropping both. Printing and waiting are now stated as two separate actions: the menus are unconditional *output*, and only the blocking wait is gated on a human being present. This was the single root cause of two of the three failures. (2) The schema-first rule now says to read nested `$defs`, not just the top-level `required` list — grepping only the top level is what let a Feature upsert be rejected for a `Bug` missing `actual`/`severity`, and it now also warns that `TasksContent` takes `name`/`description` while each `tasks[]` entry takes `title`. (3) Added the canonical append syntax (`tasks.-1`) with an explicit example, since guessing the next numeric index does not append; plus a rule to stop permuting a payload after two identical errors and to treat a 5xx/connection message as a service fault rather than a data problem, and never to mark a task `done` for a write that didn't succeed.

**Version 0.8** — direct user complaint: onboarding wasn't asking questions or presenting the available workflows/modes, running silently on inference and autopiloting straight into TDD. Phase 1b now defaults to actually asking the source/stage/goal questions whenever a human is present (was: infer first, only ask "if unclear") — inference stays reserved for genuinely autonomous/headless runs. Added new Phase 1c: a real orientation step before any work starts, presenting the mode menu (tdd/discover/interactive/fix/coverage/validate/improve/report/ci/pre-push/pr-review) pulled from `SKILL.md`'s own mode reference, explaining the TDD contract in plain terms, and asking whether the user wants step-by-step narration or fast/results-only — recorded in Tasks `0.1.notes` so a resumed session doesn't re-ask. Phase 8's handoff no longer autopilots into "say continue to start TDD" — it now presents a real 4-option menu (start TDD / explore first / different feature / health-check only) and waits for a pick, defaulting to TDD only if the user explicitly asked to move fast in 1c.

**Version 0.7** — fixed a real 422 found in the eval run that verified v0.6: the agent fetched `helpmetest artifact schema Feature` correctly (the schema-first rule worked) but still hit a 422 for missing `name`/`description`, because it copied this skill's own inline Feature JSON template instead of the schema it had just fetched — and that template's `content` block never had `name`/`description` fields, only `goal`/`functional`/`edge_cases`/`bugs`. Added the two missing fields to the template so it matches the real schema.

**Version 0.6** — fixed a real bug found in the eval run that verified v0.5: the agent saw `.helpmetest/config.yaml` already present (workspace auth pre-provisioned for the eval), concluded from that alone that *this project* was already onboarded, skipped slug resolution and the scoped collision check, and ran the forbidden `helpmetest artifact list` — surfacing an unrelated project's data as this project's status. "Before you start" now states explicitly: an existing config file proves auth only, never onboarding state; steps 1–2 are mandatory regardless of what's already configured.

**Version 0.5** — fixed a real 422 found in the eval run that verified v0.4: Phase 4 creates `ProjectOverview` first with empty `features`/`persona_ids` (required, so `project:<slug>`-tagged artifacts can be accepted), then creates Persona/Feature after — but nothing ever told the agent to circle back and link those ids into ProjectOverview, so it invented the step and guessed `Tasks`-style dot-notation partial update would work on ProjectOverview too. It doesn't — `agent.md`'s partial-update pattern is Tasks-only. Added an explicit "3d. Link the Persona/Feature refs back into ProjectOverview" step: mandatory, full-content-only, with the exact get-then-full-upsert sequence spelled out.

**Version 0.4** — fixed a real schema-first gap found in the same eval run that verified v0.3: the agent fetched a schema reactively (only after a 422) for each of Tasks/ProjectOverview/Feature, one failure per type, because "always fetch schema first" was written once and read as applying only to ProjectOverview. Now stated per-type: once in Phase 0 for Tasks, and explicitly enumerated (ProjectOverview, Persona, Feature) in Phase 4 — a schema fetched for one type never covers another.

**Version 0.3** — fixed a real cross-project identity-leak bug found in a live eval run: the agent skipped local slug resolution, ran an unscoped `helpmetest artifact list`, and adopted an unrelated project's leftover artifacts as this project's own identity, writing the wrong `HELPMETEST.md`. "Before you start" now requires deriving `<slug>` from local README/manifest files first and forbids `artifact list`/`search` as a discovery step — only scoped `artifact get <slug>` lookups are allowed for the collision check.

**Version 0.2** — fixed a real destructive-collision bug found in a live eval run (bare `project-overview`/`tasks-onboarding` ids clobbering a different project in a shared workspace): every artifact id is now `<slug>`-suffixed with a `project:<slug>` tag and a collision check runs before any write. Also fixed: Tasks artifact name rejected by the API for containing its type; resolved the onboard.md-vs-shared.md schema-check contradiction (schema always wins); fixed `ProjectOverview.features` shape; made the seeded auth-setup task cancellable when the app has no auth; aligned the two conflicting "greenfield" definitions; added a no-local-framework fallback to Phase 7; reconciled Phase 8's intentionally-pending TDD tasks with `agent.md`'s postflight rule.
