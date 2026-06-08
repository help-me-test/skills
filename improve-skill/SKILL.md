---
name: improve-skill
description: >-
  Workflow for improving a helpmetest skill mode (comment, validate, improve,
  skill, fix-tests, tdd, etc.) when its output is wrong or incomplete.
  Use this skill whenever: the user shows a bad output from a helpmetest mode
  and says "this is wrong / this shouldn't happen / fix this", OR evals are
  failing, OR the user wants to add a new rule to a mode. The workflow is:
  complaint → new failing eval → fix the mode → iterate until all evals green.
  Trigger on phrases like "fix the comment mode", "the validate output is wrong",
  "add a rule to improve", "this skill produced bad output", "evals are failing".
---

# improve-skill — TDD workflow for helpmetest skill modes

The complaint becomes a failing eval. The eval becomes the spec. The mode changes until the eval is green. That's the whole loop.

## Paths

```
Modes:      helpmetest-skills/helpmetest/modes/<mode>.md
Evals:      helpmetest-skills/helpmetest/evals/<mode>.evals.yaml
Runner:     ./h evals <mode> [--id N] [--verbose]
```

The `prompt_preamble` in the `.evals.yaml` is the distilled prompt sent to the model during evals. The `modes/<mode>.md` is the full human-readable instructions used when the mode runs in the real agent. **Both must stay in sync** — a fix to one needs a corresponding fix to the other.

## Workflow

### 1. Orient

Ask the user (or infer from context):
- Which mode? (`comment`, `validate`, `improve`, `skill`, `fix-tests`, `tdd`, …)
- What went wrong? Get a concrete example of the bad input and bad output.

Run the current evals to establish a baseline:

```bash
./h evals <mode> 2>&1 > /tmp/<mode>-baseline.log
cat /tmp/<mode>-baseline.log | strings | grep -E "PASS|FAIL|passed"
```

Tell the user: "N/M currently passing. Here's what's already failing."

### 2. Translate the complaint into a failing eval case

The user's example of bad output IS the new eval case. Write it now, before touching any mode instructions.

Read the existing eval file to understand the format and find the next available `id`:

```bash
# Read modes/<mode>.md to understand the rules
# Read evals/<mode>.evals.yaml to see existing cases and get next id
```

Add a new case to `<mode>.evals.yaml`:

```yaml
- id: <next>
  rules: [<rule-id-if-applicable>]
  violation: <one-line description of what the mode got wrong>
  input: |
    <the exact input that triggered the bad output>
  must_contain:
    - "<something the correct output should include>"
  must_not_contain:
    - "<something the bad output contained that it shouldn't>"
```

**For must_contain / must_not_contain**: be precise. Check the actual bad output the user showed you — the must_not_contain should match a literal string from that bad output so the case actually fails right now.

Run the new case alone to confirm it fails:

```bash
./h evals <mode> --id <new-id> --verbose 2>&1 > /tmp/<mode>-newcase.log
grep -E "PASS|FAIL|MUST" /tmp/<mode>-newcase.log
```

Show the user: "New case [N] fails as expected — the model produces `<bad thing>`. Now fixing the mode."

### 3. Fix the mode

Two things to update, always both:

**a. `evals/<mode>.evals.yaml` — `prompt_preamble`**

This is what the model sees during eval runs. Add the missing rule or clarification as a bullet. Keep it tight — one declarative sentence per rule. Use CRITICAL sparingly; only for rules the model systematically ignores.

**b. `modes/<mode>.md`**

This is what the agent reads when the mode runs in production. Add the same rule here in the appropriate section, with a short explanation of WHY. The .md can have examples and more prose; the preamble should be the compressed version.

Think about the failure pattern before writing:
- Is the model misunderstanding the output format? → clarify format rules
- Is the model doing something instead of something else? → explain why that's wrong, name the invariant
- Is it a first-item / last-item exemption bug? → add a CRITICAL noting no exemptions
- Is the model deleting things it should rewrite? → make the distinction explicit

### 4. Iterate

Run all evals for the mode:

```bash
./h evals <mode> 2>&1 > /tmp/<mode>-iter1.log
grep -E "PASS|FAIL|passed" /tmp/<mode>-iter1.log | strings
```

For each failure:
- If the **new case** still fails: the fix didn't land. Read the verbose output, understand why, adjust the preamble or mode.
- If an **old case regressed**: the fix overcorrected. Read what broke, narrow the rule.

Repeat steps 3–4 until all cases pass. Each iteration:

```bash
./h evals <mode> --id <new-id> --verbose 2>&1 > /tmp/<mode>-iter<N>.log
```

Show the user the result after each round. When all cases are green, stop.

### 5. Sanity check

Run the full suite one final time from a clean log:

```bash
./h evals <mode> 2>&1 > /tmp/<mode>-final.log
strings /tmp/<mode>-final.log | grep "passed"
```

Report: "N/N passing. The new case [id] now passes and no regressions."

### 6. Sync the skill install

The `helpmetest-skills` submodule needs to be committed and the skill reinstalled so changes take effect in real agent runs:

```bash
cd helpmetest-skills && git add helpmetest/modes/<mode>.md helpmetest/evals/<mode>.evals.yaml
cd helpmetest-skills && git commit -m "fix(<mode>): <one-line description of the fix>"
cd .. && git add helpmetest-skills
# DO NOT commit the parent yet — user will decide when to commit
```

Tell the user: "Submodule committed. Run `helpmetest install skills` to apply the updated mode in real runs."

---

## When the user adds a new rule (not just a bug fix)

Same workflow, but step 2 is slightly different: the user describes the desired behavior, you write an eval case that would test for it (which will fail because the rule doesn't exist yet), then add the rule to the mode.

Make sure the new rule is:
- In the `prompt_preamble` as a one-line bullet
- In `modes/<mode>.md` with a WHY explanation
- Covered by at least one eval case in `must_contain` or `must_not_contain`

---

## When evals are already failing (no user complaint)

Start from step 1: run the baseline, show the user which cases fail. Ask if they want to fix them or if they're known failures. Then proceed from step 3.

---

## Output constraints to watch for

Each mode has its own output format enforced via `output_constraints` in the `.evals.yaml`. When adding a rule, check that the expected output still conforms:
- `comment` mode: RF block with section comments
- `validate` mode: `GRADE: X` + `FAILS: ...` lines
- `improve` mode: `[DESCRIPTION]/[TAGS]/[BODY]` delimiters
- `skill` mode: `MODE: <name>` + `REASON: <sentence>`

Don't add `must_contain` checks that would conflict with the output format the model is already constrained to produce.
