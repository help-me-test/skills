# HelpMeTest Skills

Official skills for HelpMeTest — AI-powered test automation agent.

## Installation

```bash
helpmetest install skills
# or
npx skills add help-me-test/skills
```

Installs as a single skill (`helpmetest`) with 27 internal modes. Your AI agent invokes it with `/helpmetest <mode>` (e.g. `/helpmetest tdd`), or with no mode token at all — natural language routes to the right mode automatically.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

---

## Modes (27)

- **onboard** — new project setup: interview, explore, create all foundational artifacts, write HELPMETEST.md
- **discover** — map what exists into Feature artifacts, whether the source is a live app, PRD, API spec, tickets, or codebase
- **tdd** — test-first development: plan coverage → write all tests (they fail) → implement until green
- **full-qa** (bare `/helpmetest`) — full QA pass: discover pages, set up auth, enumerate features, generate and run tests, report bugs
- **fix-tests** — everything wrong with your tests: one broken, suite broken, stale after refactor, or quality review. Detects the situation, picks the mode.
- **ui-review** — visual inspection from a quick "does this look right?" to a full UX audit across all pages and viewports. Always produces a UIReview artifact.
- **api-testing** — test REST endpoints via authenticated browser session
- **proxy** — tunnel from HelpMeTest cloud browsers to your localhost dev server
- 19 more modes (dev, mobile, desktop, auth, fakemail, ssl, doc2html, ci, terminal, interactive, coverage, regression, validate, improve, comment, change-impact, pre-push, pr-review, nightly, report) — see the skill's `SKILL.md` §Mode reference for the full table.

## Which mode to use

```
NEW PROJECT              → /helpmetest onboard
HAVE SPECS / LIVE APP    → /helpmetest discover
WRITING CODE / TESTS     → /helpmetest tdd
FULL QA PASS             → /helpmetest
TESTS BROKEN / STALE     → /helpmetest fix-tests
VISUAL QUESTION          → /helpmetest ui-review
API TESTING              → /helpmetest api-testing
LOCALHOST TESTING        → /helpmetest proxy (then any other mode)
```

## Compatibility

These skills follow the [Agent Skills open standard](https://github.com/vercel-labs/skills) and work with:

- Claude Code
- Cline
- Cursor
- Windsurf
- GitHub Copilot
- And 30+ other AI coding agents

## CLI Reference

The HelpMeTest CLI is the primary interface:

| Command | What it does |
|---------|--------------|
| `helpmetest status` | Show tests and their current state |
| `helpmetest test run <id>` | Run a test |
| `helpmetest test create` / `helpmetest test update <id>` | Create or update a test |
| `helpmetest test view <id>` | Show a test's source + tags + last 10 runs (`--limit N` for more) |
| `helpmetest test view <id> --since 7d [--errors]` | Filtered run list — timestamps, status, error messages (was `test runs`/`test errors`) |
| `helpmetest test view <id> <timestamp>` | Full detail (keywords, network, errors) for one specific run (was `test history`); also `--open` to open in browser (was `test open`) |
| `helpmetest interactive "<command>"` | Run an interactive browser command |
| `helpmetest search [query]` | Search docs, keywords, artifacts, and tests |
| `helpmetest proxy start/stop/list` | Manage localhost tunnels |
| `helpmetest artifact upsert` | Create or update an artifact |
| `helpmetest artifact get <id>` | Fetch an artifact (`--open` to view in browser, `--include-linked` for related artifacts) |
| `helpmetest artifact list` | List artifacts |
| `helpmetest deploy` | Deploy |
| `helpmetest open <id>` | Open a resource |
| `helpmetest delete test <id>` | Delete a test |
| `helpmetest undo` | Undo last update |

## License

MIT
