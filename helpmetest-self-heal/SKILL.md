---
name: helpmetest-self-heal
description: "Autonomous test maintenance agent. Monitors test failures and fixes them automatically. Use when user mentions 'fix failing tests', 'heal tests', 'auto-fix', 'monitor test health', or test suite has multiple failures needing systematic repair. Distinguishes fixable test issues from real bugs."
allowed-tools: mcp__helpmetest-*
---

# Self-Healing Agent

Monitors test failures and fixes them autonomously.

**Mode:** On startup, fix all existing failures. Then monitor for new failures and fix them as they occur.

## Prerequisites

**MANDATORY:** Before healing, call:
```
how_to({ type: "debugging_self_healing" })
how_to({ type: "interactive_debugging" })
```

## Startup: Fix Existing Failures

On startup, check all tests for failures:

1. Get list of all failing tests using `helpmetest_status`
2. For each failing test:
   - Get recent test history to understand failure pattern
   - Classify failure type (selector change, timing issue, etc.)
   - Determine if fixable or not

3. For fixable failures (test issues):
   - Investigate interactively using `helpmetest_run_interactive_command`
   - Find the fix (new selector, longer timeout, etc.)
   - Apply fix using `helpmetest_upsert_test`
   - Verify fix works using `helpmetest_run_test`
   - Document the fix in SelfHealing artifact

4. For non-fixable failures (likely bugs):
   - Document why not fixable in SelfHealing artifact
   - Include issue type, error message, recommendation

5. After processing all existing failures, enter monitoring mode

## Monitoring: Respond to New Failures

After startup, monitor for test failures using `listen_to_events`:

When a test fails:
1. Get error details
2. Classify failure pattern
3. If fixable: investigate, fix, verify, document
4. If not fixable: document as potential bug
5. Continue monitoring

## Healing Workflow

Use this workflow for both startup failures and new failures during monitoring:

1. **Fetch test history:**
   - Get last 10 runs using `helpmetest_status`
   - Look for patterns (alternating PASS/FAIL? changing error values?)

2. **Classify failure pattern:**
   - Check error type (selector? timeout? assertion?)
   - Determine root cause using `debugging_self_healing.md` categories
   - Decide: test issue (fixable) vs app bug (not fixable)

3. **If fixable (test issue):**
   - Investigate interactively using `helpmetest_run_interactive_command`
   - Find the fix (new selector, longer timeout, etc.)
   - Validate fix works interactively first
   - Apply fix using `helpmetest_upsert_test`
   - Verify fix by running test multiple times (especially for isolation issues)
   - Document in SelfHealing artifact:
     * test_id, pattern_detected, fix_applied, verification_result, timestamp
     * Tags: feature:self-healing, test:, pattern:

4. **If not fixable (app bug):**
   - Document in SelfHealing artifact:
     * issue_type, error_message, why_not_fixable, recommendation

5. **Continue monitoring** for new failures

## Fixable vs Not Fixable

**Fixable (test issues):**
- Selector changed (element still exists, different selector needed)
- Timing issue (element appears later, need longer wait)
- Form field added/removed (form structure changed)
- Button moved (still exists, different location)
- Test isolation (shared state between tests, make idempotent)

**Not fixable (likely bugs):**
- Authentication broken
- Server errors (500, 404)
- Missing pages/features
- Data corruption
- API endpoints removed
