> **Who you are:** If `.helpmetest/SOUL.md` exists, read it — it defines your character.

---

# Mode: dev — orchestrator for all code work

**This is the entry point for any code work.** It reads the situation, determines the right starting point, and runs the correct sequence of modes. You never build code before tests. Ever.

Triggers: "build X", "add feature X", "change X", "refactor X", "I want to develop X", "implement X", "create X from scratch", "I want to make X", "let's build X".

---

## Step 0 — Orient

Check for `HELPMETEST.md` first — it determines the situation immediately:

```bash
ls HELPMETEST.md 2>/dev/null && cat HELPMETEST.md
helpmetest artifact list
helpmetest artifact list --type Tasks
```

Then read the situation:

| What you find | Situation | Go to |
|---|---|---|
| No `HELPMETEST.md`, no app code | Greenfield — nothing exists yet | § Greenfield |
| `HELPMETEST.md` exists, no Feature artifact for this work | New feature on existing project | § New Feature |
| Feature artifact exists, tests exist, tests green | Changing/refactoring existing behavior | § Change or Refactor |
| Feature artifact exists, tests exist, tests failing | Suite is broken — fix before adding | § Fix First |

---

## Step 1 — Announce, then proceed

Announce the situation and plan in one paragraph, then **immediately continue** — do not wait for a response. If the user specified scope (e.g. "full"), use it. Default is full scope.

**Greenfield:**
> "Greenfield — no code, no tests, no HELPMETEST.md. Building [X] test-first: onboard → Feature artifacts → all tests RED → implement to GREEN → interactive check → discover → validate. Starting now."

**New feature:**
> "Adding [feature] to existing project. Writing all tests RED against the spec first, then implementing. Starting now."

**Change/refactor:**
> "Mapping blast radius before touching anything. Will classify every affected test, get approval on the impact plan, then update tests first and code second."

**Fix first:**
> "There are [N] failing tests. Not adding code on top of a broken suite — fixing first, then continuing. Starting now."
---

## Situation: Greenfield

Nothing exists. Start from zero.

### 1. Onboard
Load `modes/onboard.md` and run through all phases. It creates:
- `HELPMETEST.md`
- `ProjectOverview` artifact
- `Persona` artifacts
- `Feature` artifacts with Given/When/Then scenarios
- Test runner infrastructure (config files only — NO app source files)

**When onboard Phase 8 completes: do not yield. Immediately continue to §2.**

### 2. Write tests RED (via `tdd` mode)
Load `modes/tdd.md` immediately after onboard. Follow "I need to build something". Write ALL tests for every Feature artifact scenario. Every test must fail — no app code exists yet. That is correct.

**Do not write a single line of application code until every test exists and is confirmed failing.**

### 3. Build to GREEN
Implement the app incrementally — one failing test at a time. Pick the highest-priority failing test, write the minimum code to pass it, move to the next. No speculative code, no "I'll need this later."

### 4. Eyes on the result (via `interactive` + `proxy`)
App is now running. Load `modes/interactive.md`. Start a proxy tunnel if local (see `proxy` skill). Navigate to the app and read the Interactive section — verify real selectors match what tests use, spot anything tests missed.

### 5. Adversarial probe (via `discover`)
Load `modes/discover.md` triage mode. Walk the live app, run the adversarial probe, collect bugs/UX illogicalities tests didn't catch.

### 6. Quality gate (via `validate` + `improve`)
Load `modes/validate.md` — score all tests R1–R13. Then load `modes/improve.md` — fix every failing rule in-place.

### 7. Coverage gap check (via `coverage`)
Load `modes/coverage.md` — find any scenarios in Feature artifacts with no `test_ids`.

---

## Situation: New Feature

Project exists. Adding net-new behavior.

### 1. Create Feature artifact
Before any test or code, create a `Feature` artifact with all Given/When/Then scenarios for the new feature. This is the spec. Get it right before writing a single test.

### 2. Write tests RED (via `tdd` mode)
Load `modes/tdd.md` — follow "I need to build something". Tests written against the new Feature artifact scenarios. All fail. That is correct.

### 3. Implement to GREEN
Write the minimum code to pass each failing test, one at a time.

### 4. Eyes on the result (via `interactive` + `proxy`)
Same as Greenfield §4.

### 5. Quality gate (via `validate` + `improve`)
Same as Greenfield §6.

### 6. Coverage gap check (via `coverage`)
Same as Greenfield §7.

---

## Situation: Change or Refactor

Behavior exists, tests exist, tests green. Something is changing.

### 1. Blast radius — STOP before touching anything

Load `modes/tdd.md` — follow "Change this / Fix this bug / Refactor this". Do the full blast radius analysis:

```bash
grep -rn "@helpmetest" <files-to-change>
helpmetest status
git diff --stat HEAD
```

Classify every affected test: **still valid / needs update / delete / new test needed**. Present the impact plan. Wait for explicit approval.

### 2. Update tests first
Tests will fail immediately after you update them. That is correct — failing tests are now the spec for the implementation change.

### 3. Change the code
The failing tests tell you exactly what to implement. No more, no less.

### 4. Prove GREEN
Run all affected tests. Show the output. "Should work" is not done.

### 5. Eyes on the result (via `interactive` + `proxy`)
Same as Greenfield §4.

### 6. Quality gate (via `validate` + `improve`)
Same as Greenfield §6.

---

## Situation: Fix First

Tests are failing. Do not add code on top of a broken suite.

Load `modes/fix.md` — run triage, classify failures, fix or document bugs. When the suite is green, return to the top of this mode and re-read the situation — then proceed with the right branch.

---

## The one rule that overrides everything

**No application code before a failing test proves it's needed.**

If you catch yourself writing code "to prepare", "to scaffold", or "because I'll need it" — stop. Write the test first. If the test is hard to write, the design is wrong. Fix the design, not the rule.

---

## Tasks artifact

Create at the start of every `dev` session:

```json
{
  "type": "Tasks",
  "name": "Tasks: dev — [what you're building]",
  "content": {
    "overview": "What this implements and why",
    "tasks": [
      { "id": "1.0", "title": "Onboard / Feature artifact", "status": "pending", "priority": "critical" },
      { "id": "2.0", "title": "Write all tests RED", "status": "pending", "priority": "critical" },
      { "id": "3.0", "title": "Implement to GREEN", "status": "pending", "priority": "critical" },
      { "id": "4.0", "title": "Interactive — eyes on result", "status": "pending" },
      { "id": "5.0", "title": "Discover — adversarial probe", "status": "pending" },
      { "id": "6.0", "title": "Validate + improve — quality gate", "status": "pending" },
      { "id": "7.0", "title": "Coverage gap check", "status": "pending" }
    ]
  }
}
```

Omit phases that don't apply (e.g. no onboard for an existing project, no discover if scope is tiny). Track subtasks per `modes/agent.md`.
