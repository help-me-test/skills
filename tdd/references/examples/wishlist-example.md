# TDD Example: Wishlist Feature

A complete walkthrough of adding a wishlist feature using Test-Driven Development.

---

**User**: "Add a wishlist feature where users can save items for later"

**TDD Agent**:

```
Step 1: Understanding requirements
- Add items to wishlist
- View wishlist
- Remove from wishlist
- Persist across sessions

Step 2: Setting up local development
Is your app running on localhost? What port?

Step 3: Starting proxy
$ helpmetest proxy start localhost:3000
✓ Proxying localhost -> localhost:3000

Step 4: Creating Feature artifact...
[creates feature-wishlist artifact]

Step 5: Writing ALL tests (not implementing yet!)

Tests to write:
1. Add item to wishlist (priority:critical)
2. View wishlist items (priority:critical)
3. Remove from wishlist (priority:critical)
4. Empty wishlist shows message (priority:medium)
5. Cannot add duplicate items (priority:high)
6. Wishlist persists after reload (priority:critical)
7. Add fails gracefully if API error (priority:medium)
8. Wishlist has max 100 items (priority:low)

Writing all 8 tests now...
[creates all 8 tests with helpmetest_upsert_test]

All 8 tests written. Running them...
[runs all tests]

Expected results:
All 8 tests failing (feature not implemented)

This is GOOD! Tests show exactly what to build.

Step 6: Starting implementation...

Next: Make "Add item to wishlist" pass

Checking syntax...
Syntax OK

Implementing add functionality...
[writes code]

Running test...
Test passes!

Next: Make "View wishlist items" pass
[implements]
[checks syntax]
[runs test]
Test passes!

[continues until all 8 tests pass]

All 8 tests passing!

Reviewing for missing edge cases...
Found gap: What if user adds item while offline?

Writing test for offline scenario...
[writes test]
Test fails as expected
[implements offline handling]
[checks syntax]
Test passes!

All 9 tests passing!
No other edge cases found
Feature complete!

Summary:
- 9 tests written (4 critical, 3 high, 2 medium)
- All tests passing
- Covers happy paths, edge cases, and persistence
- Offline handling implemented
```
