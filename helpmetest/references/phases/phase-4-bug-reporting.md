# Phase 4: Bug Reporting

For each test result:

## If Test PASSES ✅

- Feature.status = "working"
- Move to next scenario

## If Test FAILS ❌

### Analyze Failure

Use test run output to understand what happened.

### Determine Root Cause

Two possibilities:

#### Bug

Actual behavior differs from expected.

**Actions:**
- Add to Feature.bugs with severity and actual behavior
- Update Feature.status to "broken" (if all tests fail) or "partial" (if some pass)
- Keep the failing test - it documents what needs to be fixed!

#### Test Issue

Selectors wrong, timing issue, test logic error.

**Actions:**
- Fix the test
- Re-validate with /helpmetest-validator
- Re-run test
- Continue testing

## Critical Philosophy

**Failing tests are NOT failures - they are specifications that guide development/fixes!**

When a test fails because the feature is broken, that's valuable information. The test documents what SHOULD happen. Keep it.
