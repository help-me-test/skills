# Critical Rules

## 🔴 YOU WRITE THE TEST FIRST.
Changed code → run the tests. New feature → write the test before the code.
The test is the spec. The test is done when it's green. **No test = not done.**

---

## Narrate Your Actions

Never create a test, artifact, or run a test silently. Before every action: say what you're doing and why. After every result: say what it means. What you found goes into artifacts — not chat.

---

1. **Authentication FIRST, always** — NEVER start testing other features until auth is proven working:
   - Ask about registration strategy
   - Create AND RUN maintaining test (registration or login with `Save As`)
   - VALIDATE test passes and state exists
   - Test `As <StateName>` works
   - **BLOCK all other work until this completes**

2. **Test first** — Create tests based on expected behavior, EVEN IF the feature is broken. Failing tests document bugs and guide fixes.

3. **No bullshit tests** — Every test must have 5+ steps and verify actual outcomes, not just that elements are visible.

4. **Test features, not pages** — Tests verify business capabilities work end-to-end.

5. **Use artifacts** — All discoveries go into Persona/Feature/ProjectOverview. Bugs go in `feature.bugs[]` immediately when found, not in chat.

6. **Link everything** — Tests link to Features via `scenario.test_ids`.

7. **Use FakeMail** — `Create Fake Email` for registration, never hardcode emails.

8. **Tag properly** — All scenarios need `priority:` tag. All tests need `type:` and `priority:` tags.

9. **Don't wait for fixes** — Generate ALL tests, let them fail if the feature is broken. A failing test is a spec.

10. **Validate test quality** — Run `/fix-tests` in validate mode on every generated test before linking it to the scenario. A test that passes when the feature is broken must be rewritten.
