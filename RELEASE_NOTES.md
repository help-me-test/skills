# Release notes

## 3.0.0 — 2026-09-29

### Breaking workflow change

Existing tests are now immutable evidence. HelpMeTest skills no longer modify, skip, disable,
weaken, remove assertions from, or delete an existing test to make a result pass.

When a test fails or conflicts with product behaviour, the skills now preserve the test and
report its literal command output, expected versus observed behaviour, and the code,
configuration, fixture, or environment change required for it to pass.

### Reporting evidence

Every final report now starts by declaring whether test files changed. A claim that a test
passes must include the literal test command and result output; a count or paraphrase is not
accepted as proof.

### Mode changes

- `fix` repairs the product or environment, not the test.
- `dev` treats affected tests as contracts during code changes.
- `improve` and `comment` audit and report only.
- `ssl` leaves mismatched certificate assertions red and reports the required server-side
  correction.
