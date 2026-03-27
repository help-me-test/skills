# Phase 3: Test Generation for ALL Enumerated Scenarios

**CRITICAL: Only start this phase AFTER Phase 2 is 100% complete (all features enumerated, all scenarios discovered).**

## Philosophy

Generate tests for EVERY scenario. One feature at a time. Failing tests are VALUABLE - they document what needs fixing.

## Test Priority Rule

Always test priority:critical scenarios FIRST within each feature. These critical scenarios represent complete end-to-end flows. Without testing them first, you might create 10 partial tests and claim the feature is "tested" while never verifying the core transaction works.

## Process

Report: "Phase 2 complete. Starting test generation for X features with Y total scenarios."

For each feature, work on it completely before moving to the next:

### 1. Report Which Feature You're Testing

- Feature name
- How many scenarios it has (functional, edge cases, non-functional)

### 2. Sort Scenarios by Priority

- List critical scenarios first, then high, medium, low
- Report priority breakdown (how many of each)

### 3. For Each Scenario in Priority Order

#### a. Create Test

Using `helpmetest_upsert_test`:
- Scenario was explored in Phase 2, so selectors are known
- Write test for what SHOULD happen (from scenario.then)
- Include proper waits and assertions
- Test MUST be 5+ steps with outcome verification
- Use "As <auth_state>" if scenario requires auth

#### b. Validate Test Quality

Call `/helpmetest-validator`:
- Pass test_id and feature_id to validator
- Validator checks for bullshit patterns
- If REJECTED → Fix test based on feedback, validate again
- If PASSED → Continue
- DO NOT SKIP VALIDATION

#### c. Link Test to Scenario

Add test_id to scenario.test_ids

#### d. Run Test

Using `helpmetest_run_test`:
- Execute and wait for result
- Document outcome (pass/fail/flaky)

#### e. If Test FAILS, Debug Interactively

- Run test steps manually one by one using `helpmetest_run_interactive_command`
- Observe what happens at each step
- When you hit the failure, investigate why (element missing? wrong value? timeout?)
- Determine root cause:
  * **TEST ISSUE** (wrong selector, timing, expectation) → Fix test, validate interactively, then update
  * **APPLICATION BUG** (feature broken) → Document in feature.bugs[], keep test as specification

### 4. After All Scenarios in This Feature Are Tested

#### a. Validate Critical Coverage

- Review all scenarios with priority:critical in this feature
- Check each critical scenario has at least one test_id
- If ANY critical scenario has empty test_ids:
  * ERROR: "Cannot mark feature as done - critical scenarios untested"
  * List which critical scenarios are missing
  * STOP: Generate tests for missing critical scenarios before moving on

#### b. Update Feature Status

- "working" if all tests pass
- "partial" if some pass, some fail
- "broken" if all tests fail

#### c. Calculate Coverage

- Total scenarios
- Scenarios with tests
- Critical scenarios with tests (must be 100%)
- Overall coverage percentage

#### d. Report Feature Completion

- Feature name and status
- Critical scenarios tested (must be 100%)
- Total scenarios count
- Tests created
- Tests passing
- Tests failing
- Bugs found

### 5. Move to Next Feature

Repeat the process.

## Critical Rules

- ✅ Phase 2 MUST be complete before starting Phase 3
- ✅ All scenarios already discovered in Phase 2 - don't re-explore
- ✅ Create test for expected behavior (from scenario)
- ✅ VALIDATE EVERY test with /helpmetest-validator
- ✅ Run EVERY test immediately after creation
- ✅ Document bugs in feature.bugs[], don't wait for fixes
- ✅ Complete ONE feature fully before moving to next

## Final Validation

Before reporting that testing is done, review ALL features:

For each feature, check all scenarios with priority:critical. Verify each critical scenario has at least one test_id populated.

When you find ANY critical scenario with empty test_ids:
- List the feature name
- List the untested critical scenario names
- STOP claiming "all features tested"
- Go back and generate tests for those critical scenarios

This validation prevents you from saying "tested 25 features" when the most important scenarios were never tested.

## Exit Criteria

- ✅ Tests created for ALL scenarios (100% coverage)
- ✅ **ALL priority:critical scenarios have test_ids** (NO exceptions)
- ✅ ALL tests validated by /helpmetest-validator
- ✅ ALL tests executed
- ✅ ALL bugs documented in feature.bugs[]
- ✅ ALL feature.status updated based on results
