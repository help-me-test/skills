# CLI & Artifact Contracts

Consolidated schema/flag reference. Mode files link here instead of re-typing these shapes — always fetch `helpmetest artifact schema <TypeName>` before creating, since the schema is authoritative and can change; this file documents the shape agents should expect, not a frozen contract.

The `Tasks` artifact schema and its lifecycle rules (Preflight/Postflight, partial updates, evidence requirements) live in `modes/agent.md` — that file is the Tasks-artifact owner. This file covers everything else.

---

## `helpmetest config` — project settings (`.helpmetest/config.yaml`)

```bash
helpmetest config                               # show all settings (file value or default)
helpmetest config get <key>                     # show one value
helpmetest config set <key> <value>              # write one value
helpmetest config unset <key>                    # remove key, revert to default
```

Known keys: `apiBaseUrl` (default `https://helpmetest.com`, set automatically by `register`/`login` — don't hand-edit unless pointing at a non-default server), `apiToken` (prefer `helpmetest login` over setting this directly; masked in output), `autoOpenSession` (`true`/`false`, default `true` — opens the live interactive session in a browser), `debug` (`true`/`false`, default `false`), `env` (default environment for `helpmetest secret`/`helpmetest otp`, default `default`), `timeout` (request timeout in seconds, default `30`), `retries` (default `3`). Boolean/number keys are validated on `set`. Unknown keys are still stored and shown under "Other settings".

Distinct from `helpmetest secret` (test passwords), `helpmetest otp` (2FA seeds), and `helpmetest token` (workspace API tokens) — `config` covers CLI behavior only.

---

## `Feature.bugs[]` entry shape

Used by `fix` (Phase 4B), `discover`, and any mode that finds a bug during exploration or debugging.

```json
{
  "name": "Brief description",
  "given": "Precondition",
  "when": "Action taken",
  "then": "Expected outcome",
  "actual": "What actually happens",
  "severity": "blocker|critical|major|minor",
  "url": "http://example.com/page",
  "tags": []
}
```

After adding a bug, update the owning Feature's `status` field to `"broken"` or `"partial"` — never leave it `"working"` alongside an open bug.

---

## `ValidationReport` artifact

Created by `validate` mode after reviewing one or more tests.

```json
{
  "type": "ValidationReport",
  "id": "validation-[timestamp]",
  "name": "ValidationReport: [N] tests reviewed",
  "content": {
    "overview": "Reviewed [N] tests. [X] passed (A/B grade), [Y] failed (C/D/F grade).",
    "summary": {
      "total": "<int>",
      "grade_distribution": { "A": "<int>", "B": "<int>", "C": "<int>", "D": "<int>", "F": "<int>" },
      "r11_mutagen_failures": ["<test_ids>"],
      "r12_framework_tests": ["<test_ids>"],
      "r13_overmocking": ["<test_ids>"],
      "bullshit_score_avg": "<float>|null"
    },
    "tests": [
      { "test_id": "...", "name": "...",
        "grade": "A|B|C|D|F",
        "r_scores": { "r1": "PASS|FAIL", "r2": "PASS|FAIL" },
        "r11_mutation_resistance": "PASS|FAIL" }
    ]
  }
}
```

Full R1–R13 rules and grading in `modes/validate.md`.

---

## `CoverageReport` artifact

Created by `coverage` and `pr-review` modes. See `modes/coverage.md` for the full schema.

---

## `Memory` artifact — scoped entries

Replaces a single free-text blob. Each entry records one piece of project knowledge (a selector, an auth flow quirk, a timing gotcha) discovered mid-session, with enough metadata for a future agent to judge whether to trust it without re-verifying from scratch.

```json
{
  "type": "Memory",
  "id": "memory-<project>",
  "content": {
    "entries": [
      {
        "text": "Login form's submit button is `button[data-testid=login-submit]`, not `button[type=submit]` — there are two submit-typed buttons on that page.",
        "scope": "feature:auth",
        "confidence": "high",
        "last_verified": "2026-08-20"
      },
      {
        "text": "Staging environment takes ~8s to cold-start after 15 min idle — first request of a session often times out at the default 10s.",
        "scope": "project",
        "confidence": "medium",
        "last_verified": "2026-07-02"
      }
    ]
  }
}
```

Field meaning:
- `scope` — `project` (true anywhere in this project), `feature:<id>` (only relevant to one Feature), or `test:<id>` (only relevant to one test). Narrower scope = safer to trust without re-checking; `project`-scope claims age faster as the app changes.
- `confidence` — `high` (directly observed and re-confirmed at least once), `medium` (observed once, plausible), `low` (inferred, not directly observed — flag for re-verification before relying on it).
- `last_verified` — the date this was last confirmed true, not the date it was first written. Update it every time an agent re-confirms the entry still holds; don't touch it on entries left untouched.

An agent reading Memory should treat entries with `confidence: low` or `last_verified` older than ~30 days as needing a quick re-check before being trusted, not as settled fact — see `modes/shared.md` §"Also look for a Memory artifact" and `modes/report.md`'s staleness check.
