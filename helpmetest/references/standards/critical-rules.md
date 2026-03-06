# Critical Rules

1. **Authentication FIRST, always** - NEVER start testing other features until authentication is proven working:
   - Ask customer about registration strategy
   - Create AND RUN maintaining test (registration or login)
   - VALIDATE test passes and state exists
   - Test "As <StateName>" works
   - **BLOCK all other work until this completes**

2. **BDD/Test-First** - Create tests based on expected behavior, EVEN IF feature is broken

3. **Failing tests are valuable** - They document bugs and guide fixes

4. **NO bullshit tests** - Every test must have 5+ steps and verify actual outcomes

5. **Test features, not pages** - Tests verify business capabilities work

6. **Use artifacts** - All discoveries go into Persona/Feature/ProjectOverview

7. **Link everything** - Tests link to Features via scenario.test_ids

8. **Use FakeMail** - Use `Create Fake Email` for registration, never hardcode emails

9. **Tag properly** - All scenarios need priority: tag, all tests need type: and priority: tags

10. **Don't wait for fixes** - Generate ALL tests, let them fail if needed

11. **Customer consultation required** - Always ask about registration strategy before creating auth tests
