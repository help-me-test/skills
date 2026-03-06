# Definition of Done

**MUST HAVE NUMBERS**

## Authentication Setup (MUST BE FIRST)

- [ ] **Customer consulted** about registration strategy (existing / register-once / register-repeatedly)
- [ ] **Registration strategy documented** in Persona artifact
- [ ] **Maintaining test created** (registration or login test with "Save As")
- [ ] **Maintaining test RUN and PASSED** (confirmed, not assumed)
- [ ] **Saved state verified** via `helpmetest_status`
- [ ] **Saved state tested** via "As <StateName>" command works
- [ ] **All auth validation complete BEFORE any other testing**

## Discovery Completeness

- [ ] **Total pages discovered:** X
- [ ] **Total pages explored:** X (must be 100%, not Y/X)
- [ ] **Unauthenticated pages:** Y
- [ ] **Authenticated pages:** Z
- [ ] **Total interactable elements found:** N
- [ ] **No new pages found in last 3 exploration rounds**

## Feature Coverage

- [ ] **Persona artifacts:** One for each user type
- [ ] **ProjectOverview artifact:** Created with all features linked
- [ ] **Feature artifacts:** X total (one for EVERY capability found)
- [ ] **Total scenarios created:** Y
  - [ ] Functional scenarios: A
  - [ ] Edge case scenarios: B
  - [ ] Non-functional scenarios: C

## Test Coverage

- [ ] **Tests created:** X (should be >= number of scenarios)
- [ ] **Tests validated:** X (100% must pass /helpmetest-validator)
- [ ] **Tests executed:** X (100% must be run)
- [ ] **Critical scenarios tested:** 100% (ALL priority:critical scenarios MUST have test_ids)
- [ ] **Tests passing:** A
- [ ] **Tests failing:** B
- [ ] **Tests flaky:** C
- [ ] **Scenario coverage:** Y scenarios with tests / Z total scenarios = N%

## Bug Documentation

- [ ] **Bugs found:** X total
- [ ] **All bugs documented in Feature.bugs[]**
- [ ] **All Feature.status reflects actual state** (working/partial/broken)

## Critical User Journeys

- [ ] **All critical journeys traced:** X journeys
- [ ] **Journey completion status documented:**
  - [ ] Complete: A
  - [ ] Partial: B
  - [ ] Blocked: C

## Final Report

- [ ] Summary report provided with ALL numbers above
- [ ] User informed of exact coverage percentages
- [ ] No surprises (user knows what's tested, what's broken, what's missing)

**NEVER claim "done" without providing these numbers.**
