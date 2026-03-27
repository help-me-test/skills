---
name: helpmetest-sync
description: "Sync tests with code — find discrepancies, fix what's stale. Use when tests are failing after a code change, when you suspect tests are out of date, after a refactor or rename, before a release, or whenever you want to audit whether tests and code actually agree. Triggers on: 'sync tests', 'tests out of date', 'tests don't match code', 'what's failing and why', 'test audit', 'align tests with code', 'tests are stale', 'do tests still match', 'cleanup tests'. Goes beyond a simple test run — it classifies each discrepancy (code broke it, test is stale, not deployed yet, false positive, etc.) and lets you decide per-item whether the test or the code is the source of truth."
allowed-tools: mcp__helpmetest-*
---

> **Who you are:** If `.helpmetest/SOUL.md` exists, read it before starting — it defines your character.

> **No MCP?** Use `helpmetest <command>` CLI instead. See the README for CLI reference.

# HelpMeTest Sync

Finds discrepancies between code and tests, classifies each one, and walks you through resolving them one by one — letting you decide per item whether the test or the code is the source of truth.

## Phase 0: Orient

Before anything else, establish context:

```
helpmetest_status()
helpmetest_search_artifacts({ query: "" })
helpmetest_search_artifacts({ query: "Memory" })
```

Check git state:
```bash
git log --oneline -10
git diff --stat HEAD
git stash list
```

From this, build a picture:
- What tests exist and what's their current state?
- Which Feature/Persona/ProjectOverview artifacts exist?
- What changed recently in the code? (file paths tell you which features are affected)
- Is local code ahead of deployed code? (uncommitted or undeployed changes)

## Phase 1: Run Tests

Run all tests to get a fresh picture. Don't skip this — cached results hide recent code changes.

Get all test IDs from `helpmetest_status()`, then run them in parallel:

```
// 1. Get all test IDs
const status = await helpmetest_status()
const allIds = status.tests.map(t => t.id)

// 2. Run all in parallel
helpmetest_run_test({ id: allIds })
```

If the project is large and running everything is slow, prioritize in this order:
1. Tests linked to features touched by recent git changes (cross-reference git diff file paths with Feature artifact tags)
2. Tests that were failing in the last known run
3. Everything else

Wait for results. Note which tests passed, failed, or were skipped.

## Phase 2: Collect & Classify Discrepancies

A discrepancy is any mismatch between what tests assert, what code does, and what Feature artifacts document. Cast a wide net — don't only look at failures.

For each test and each feature artifact, check all 12 types:

### Failure-based (test is currently failing)

**1. Code Broke It**
Signal: Test was passing, something changed in code, test now fails.
How to spot: `git log --oneline` shows recent changes to files the test exercises. Test history shows recent regression.
Presumption: Test is right. Code introduced a bug.

**2. Test Is Stale**
Signal: Code intentionally changed (refactor, rename, new flow), test hasn't been updated yet.
How to spot: Code change looks deliberate (not a bug). Test assertions reference old selectors, old text, old endpoints.
Presumption: Code is right. Test needs to catch up.

**3. Not Deployed**
Signal: Test fails against deployed env, but local code has a fix. The fix exists — it just hasn't shipped.
How to spot: `git diff HEAD` shows relevant code changed locally. Test fails against a remote URL, not localhost. Sometimes the test was recently green on a dev branch.
Presumption: Neither is wrong. A release is pending.

**4. Removed Feature**
Signal: Test exercises a page, endpoint, or UI element that no longer exists in the codebase.
How to spot: grep for the URL or selector in the test — nothing found in code. Feature artifact may be missing or marked deprecated.
Presumption: Code is right (feature was intentionally removed). Test should be deleted or archived.

### Passing but suspicious (test is currently passing)

**5. False Positive**
Signal: Test passes but assertions are too weak to actually verify the feature works. Classic signs: only checks that an element is visible, doesn't verify outcomes, no state verification after actions.
How to spot: Read the test steps. Would this test catch a real breakage? If you deleted the core logic from the code, would the test still pass? If yes, it's vacuous.
Presumption: Test is wrong (not wrong enough to fail — wrong in that it provides false confidence).

**6. Flaky**
Signal: Test passes sometimes, fails sometimes, with no code change in between. Non-deterministic behavior.
How to spot: Test history shows alternating PASS/FAIL. Error messages vary across runs (different selectors missing, different timeouts, different values).
Presumption: Test quality issue — likely timing, shared state, or test isolation problem. Neither code nor test is "right" until stability is confirmed.

**7. Duplicate Coverage**
Signal: Two or more tests cover the exact same scenario from the same feature. One is redundant.
How to spot: Compare test steps across tests linked to the same scenario. Check `scenario.test_ids` for multiple IDs on the same scenario.
Presumption: One test should be kept (the better one), the other deleted.

### Coverage gaps (things that should exist but don't)

**8. Missing Test**
Signal: A feature or code path exists with no test coverage at all. Users can do it, code supports it, but nothing verifies it.
How to spot: Feature artifacts with scenarios that have empty `test_ids`. Code areas with no corresponding Feature artifact.
Presumption: Test is missing. Write one.

**9. Scenario Gap**
Signal: Feature artifact has a documented scenario, but `test_ids` is empty or null. The scenario was planned but never implemented as a test.
How to spot: Check all Feature artifacts, find scenarios with no `test_ids`.
Presumption: Test work is pending. Prioritize or deprioritize explicitly.

**10. Scenario Drift**
Signal: Both code and tests have evolved together, but the Feature artifact still documents the old behavior. The artifact is the stale thing — tests and code agree with each other but disagree with the documented spec.
How to spot: Read Feature.scenarios, compare with what tests actually do and what code actually does. All three should agree.
Presumption: Feature artifact needs updating to reflect current reality.

### Contract mismatches

**11. API Contract Drift**
Signal: Test expects a specific API response shape (field names, status codes, data types) but the code now returns something different.
How to spot: Compare test assertions on API responses against actual route handlers or response schemas in code.
Presumption: Depends on whether the API change was intentional. If yes, update test. If no, fix code.

**12. Selector / Schema Drift**
Signal: Test uses a CSS selector, element text, or attribute that no longer matches what the code renders. Subtle version of "test stale" — the feature still works, but the test's handle on it is broken.
How to spot: Extract selectors from failing tests, grep for them in component/template files.
Presumption: Test needs its handle updated. Feature still works.

---

For each discrepancy found, record:
- Type (from the 12 above)
- Which test(s) and Feature artifact are involved
- What the test expects vs. what code does
- Relevant git evidence (which commit, which files)
- A one-sentence plain-language summary

## Phase 3: Summary Report

Before going one-by-one, present the full picture in clean markdown. This lets the user understand scope and decide if some categories can be bulk-handled.

Format — plain text, emojis, vertical layout, no markdown, omit zero-count groups:

🔄 Sync Report · <project> · <date>
<N> failing · <N> flaky · <N> gaps · <N> passing

💥 Failures

   Code Broke It · <N> tests

   <test name>
   does: <one line — what the test verifies>
   issue: <one line — what specifically is broken / what changed>

   <test name>
   does: <one line>
   issue: <one line>

   Not Deployed · <N> tests

   <test name>
   does: <one line>
   issue: <which file/feature is uncommitted and why the test can't pass yet>

🎲 Suspicious

   Flaky · <N> tests

   <test name>
   does: <one line>
   issue: <what makes it non-deterministic — timing, shared state, intermittent redirect, etc>

🕳 Gaps

   Missing Test · <N>

   <feature or code area>
   does: <what the feature does>
   issue: <why there's no test — new code, never written, scenario gap, etc>

Go in order, or jump to a specific group?

Wait for user to confirm before starting Phase 4.

## Phase 4: One-by-One Resolution

Work through each discrepancy. Present one at a time, wait for the user's decision, apply it, then move on.

### Discrepancy card format

Present each item as plain text with emojis. No markdown, no code blocks, no bold.

Example card — plain text, vertical, emojis, no markdown:

#3 of 29 · TEST IS STALE
📋 <test name>
   feature   <feature name>

   expects
      <what the test currently asserts>

   code now
      <what the code actually does>
      <file> · <commit> · <N>d ago

   1 · Fix the test
      <specific change to make>  [code leads]

   2 · Fix the code
      <specific change to make>  [test leads]

   3 · Skip

   4 · Delete test

   5 · Document bug
      keep test as spec, add to Feature.bugs[]

   6 · Not deployed
      mark pending-deploy, revisit after release

Each option gets its own line. If the fix description is more than a few words, put it on the line below indented. No option should be crammed together with another.

### Applying the decision

**Option 1 — Fix the test:**
- Make the specific change described
- Run the test to confirm it now passes: `helpmetest_run_test({ id: "test-id" })`
- Update `scenario.test_ids` if needed
- Confirm to user with result

**Option 2 — Fix the code:**
- Describe the exact code change needed (file, line, what to change)
- You generally cannot make the code change yourself — you're a QA agent
- If the user wants you to make it, do so only if it's clearly safe and well-scoped
- After code is fixed (by user or by you), re-run the test to verify it passes
- If the code fix changes behavior that other tests rely on, flag those tests

**Option 3 — Skip:**
- Note it in the deferred list
- Continue to next discrepancy
- Report deferred items at the end

**Option 4 — Delete test:**
- Confirm once before deleting: "Delete test 'User can reset password'? This can't be undone."
- `helpmetest_delete_test({ id: "test-id" })`
- Remove `test_ids` reference from Feature artifact scenario
- Update feature coverage metrics

**Option 5 — Document bug:**
- Add to Feature.bugs[] with severity, given/when/then/actual
- Update Feature.status to "broken" or "partial"
- Keep the test — it is now the specification for the fix

**Option 6 — Not deployed:**
- Tag the test as "pending-deploy" (add to deferred list with note)
- Remind user at end: "3 items are pending-deploy — re-run sync after next release"

### Bulk decisions

If the user says things like "fix all selector drifts" or "skip all scenario gaps for now", apply the decision across the whole category and move on. Don't make them click through each one if the answer is clearly uniform.

## Phase 5: Summary of Changes

After resolving all items, give a final report. Plain text, no markdown, emojis for cues:

✅ Sync done · <project>

   Tests fixed        <N>
   Code to fix        <N>   needs dev action
   Bugs documented    <N>
   Tests deleted      <N>
   Deferred           <N>
   Pending deploy     <N>

   Before   <N> passing · <N> failing · <N> skipped
   After    <N> passing · <N> failing · <N> skipped (deferred)

⏳ Pending deploy

   <test name>
   waiting on <commit>

   <feature> — <N> scenario gaps
   <priority note>

▶ Next

   Re-run full suite to confirm no regressions
   After deploy: run sync again to clear pending items

## Key Principles

**Code may not be deployed.** The most common false alarm: a test fails against a remote env, but the fix is already in local code waiting to ship. Always check `git diff HEAD` before concluding "code is broken" — the code might already be fixed.

**Tests and code are both sources of truth — neither wins automatically.** A failing test might mean the test is wrong, the code is wrong, or the code changed intentionally. Don't fix the test just because it's failing. Understand why before acting.

**Prefer fixing over deleting.** A broken test still describes desired behavior. Before deleting, ask: is this scenario worth testing? If yes, fix it. If the feature is gone, then delete.

**Sync is not debugging.** The goal is not to make tests pass at any cost — it's to make tests and code *agree*. A test that passes because you weakened its assertions is worse than a failing test.

**Version:** 0.1
