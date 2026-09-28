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
helpmetest config env                            # set the default environment for secret commands
```

Every one of these takes `--json`, `--select <path>` and `--schema` for machine-readable
output.

Known keys: `apiBaseUrl` (default `https://helpmetest.com`, set automatically by `register`/`login` — don't hand-edit unless pointing at a non-default server), `apiToken` (prefer `helpmetest login` over setting this directly; masked in output), `autoOpenSession` (`true`/`false`, default `true` — opens the live interactive session in a browser), `debug` (`true`/`false`, default `false`), `env` (default environment for `helpmetest secret`/`helpmetest otp`, default `default`), `timeout` (request timeout in seconds, default `30`), `retries` (default `3`). Boolean/number keys are validated on `set`. Unknown keys are still stored and shown under "Other settings".

**Verified 2026-09-25** against `helpmetest config --help` and live output: all seven keys
exist with exactly these defaults (`timeout` 30, `retries` 3, `autoOpenSession` true), and
the unknown-key behaviour is real — `helpmetest config set madeUpKey somevalue` in a scratch
directory produced an `Other settings:` section listing `madeUpKey: somevalue`. Unlike the
`TestValidation` section below, nothing here had drifted.

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
  "tags": [],
  "auth": ["admin", "user"],
  "test_ids": ["todo-create-new-item"]
}
```

**Verified 2026-09-25** against `helpmetest artifact schema Feature --json` (`$defs.Bug`).
Required exactly: `name`, `given`, `when`, `then`, `actual`, `severity`. `severity` is an
enum — `blocker`, `critical`, `major`, `minor`, nothing else. `url`, `tags`, `auth`
(required auth states) and `test_ids` (linked automated test ids) are optional; the last two
were missing from this doc.

After adding a bug, update the owning Feature's `status` field to `"broken"` or `"partial"` — never leave it `"working"` alongside an open bug.

---

## `TestValidation` artifact — NOT `ValidationReport`

Created by `validate` mode after reviewing one or more tests.

**The type is `TestValidation`.** `ValidationReport` does not exist, and this file used to
say it did, along with a `content` shape that was invented end to end. Measured 2026-09-25 —
of ten artifact types the skill names, this was the only one that failed:

```
$ helpmetest artifact schema ValidationReport
✗ API Error: Failed to fetch schema for ValidationReport
  Status Code: 500
```

`Tasks`, `Persona`, `ProjectOverview`, `UIReview`, `RegressionRun`, `CoverageReport`,
`Memory`, `Feature` and `Bug` all return schemas. The real class is `TestValidationContent`
in `ai/artifact_types.py`, documented there as *"output of `/helpmetest validate`"*.

Real fields, from `helpmetest artifact schema TestValidation --json`:

| field | type | meaning |
|---|---|---|
| `name` | string | **required** — human-readable artifact name |
| `description` | string | **required** — one-line summary |
| `scope` | string | **required** — what was reviewed: `all tests`, `tests tagged X`, … |
| `tests_reviewed` | integer | **required** — count of tests evaluated |
| `grade_distribution` | object | counts keyed by letter grade (A/B/C/D/F) |
| `validations` | array | per-test entries, one per reviewed test |
| `rewrite_queue` | array | test ids graded D or F — the actionable rewrite queue |
| `fixable_queue` | array | test ids graded B or C — smaller fixes |
| `links` | array | ids of related artifacts (undirected) |

The old documented keys — `overview`, `summary`, `summary.r11_mutagen_failures`,
`bullshit_score_avg`, `tests[]` — exist nowhere in the schema. An upsert using them is
rejected.

**Fetch the schema yourself before the first upsert of a type** rather than trusting any
copy of it, including this table. That rule exists because of exactly this: a hand-written
schema in a doc drifted from the server and nobody noticed until someone ran the command.

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
    "name": "<project> testing knowledge",
    "description": "Project-specific testing knowledge",
    "entries": [
      {
        "category": "Selectors",
        "lesson": "Login form's submit button is `button[data-testid=login-submit]`, not `button[type=submit]` — there are two submit-typed buttons on that page.",
        "tags": ["auth"],
        "linked_artifact_ids": ["feature-auth"],
        "added_at": "2026-08-20"
      },
      {
        "category": "Flaky areas",
        "lesson": "Staging takes ~8s to cold-start after 15 min idle — the first request of a session often times out at the default 10s.",
        "added_at": "2026-07-02"
      }
    ],
    "notes": "…"
  }
}
```

**Verified 2026-09-25** against `helpmetest artifact schema Memory --json`. Entry fields are
exactly `category`, `lesson`, `tags`, `linked_artifact_ids`, `added_at`, of which
**`category` and `lesson` are required**. Top-level content is `type`, `name`,
`description`, `links`, `entries`, `notes`.

**This doc previously described a different shape entirely** — `text`, `scope`,
`confidence`, `last_verified` — none of which exist in the schema. That is the second
invented schema found in this file in one audit (see `TestValidation` above), which is the
case for fetching the schema yourself rather than trusting a written copy.

`category` is a grouping label the schema documents as one of `Auth`, `Selectors`, `Flows`,
`UI quirks`, `Data dependencies`, `Flaky areas`. There is no confidence or verification-date
field, so **staleness is not recorded by the artifact** — `added_at` is when the note was
written, not when it was last checked. Re-verify an old selector before relying on it.

Field meaning:
- `category` — grouping label: `Auth`, `Selectors`, `Flows`, `UI quirks`, `Data dependencies`, `Flaky areas`.
- `lesson` — the note itself, written so a future agent can act on it without context.
- `tags` / `linked_artifact_ids` — how an entry is narrowed to a Feature or test. **These are
  the only scoping mechanism**; there is no `scope` field.
- `added_at` — when the note was written. Not a verification date.

**There is no `confidence` and no `last_verified` field.** This doc used to describe both,
along with a three-level confidence scale and a "re-check anything older than ~30 days"
rule, and told `modes/shared.md` and `modes/report.md` to act on them. None of it is in the
schema, so no agent could have read those values and no staleness check could have fired.

Since the artifact records no freshness signal, judge an entry on its own terms: a selector
or timing claim should be re-confirmed against the live app before you build on it,
regardless of how confident the wording sounds.
