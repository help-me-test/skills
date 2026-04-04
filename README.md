# HelpMeTest Skills

Official skills for HelpMeTest — AI-powered test automation agent.

## Installation

```bash
helpmetest install skills
# or
npx skills add help-me-test/skills
```

Skills are installed to `.agents/skills/` in your project. Your AI agent can then invoke them with `/<skill-name>`.

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

---

## Available Skills (8)

- **onboard** — new project setup: interview, explore, create all foundational artifacts, write HELPMETEST.md
- **discover** — map what exists into Feature artifacts, whether the source is a live app, PRD, API spec, tickets, or codebase
- **tdd** — test-first development: plan coverage → write all tests (they fail) → implement until green
- **helpmetest** — full QA pass: discover pages, set up auth, enumerate features, generate and run tests, report bugs
- **fix-tests** — everything wrong with your tests: one broken, suite broken, stale after refactor, or quality review. Detects the situation, picks the mode.
- **ui-review** — visual inspection from a quick "does this look right?" to a full UX audit across all pages and viewports. Always produces a UIReview artifact.
- **api-testing** — test REST endpoints via authenticated browser session
- **proxy** — tunnel from HelpMeTest cloud browsers to your localhost dev server

## Which skill to use

```
NEW PROJECT → /onboard
HAVE SPECS / LIVE APP / TICKETS → /discover
WRITING CODE / TESTS → /tdd
FULL QA PASS → /helpmetest
TESTS BROKEN / STALE / SUSPICIOUS → /fix-tests
VISUAL QUESTION (any scope) → /ui-review
API TESTING → /api-testing
LOCALHOST TESTING → /proxy (then any other skill)
```

## Compatibility

These skills follow the [Agent Skills open standard](https://github.com/vercel-labs/skills) and work with:

- Claude Code
- Cline
- Cursor
- Windsurf
- GitHub Copilot
- And 30+ other AI coding agents

## No MCP? Use the CLI

If your AI agent doesn't support MCP, the HelpMeTest CLI has **full feature parity** with all MCP tools:

| MCP tool | CLI equivalent |
|----------|----------------|
| `helpmetest_status` | `helpmetest status` |
| `helpmetest_run_test` | `helpmetest test run <id>` |
| `helpmetest_upsert_test` | `helpmetest test create` / `helpmetest test update <id>` |
| `helpmetest_run_interactive_command` | `helpmetest interactive "<command>"` |
| `helpmetest_keywords` | `helpmetest keywords [search]` |
| `how_to` | `helpmetest how-to [type]` |
| `helpmetest_proxy` | `helpmetest proxy start/stop/list` |
| `helpmetest_upsert_artifact` | `helpmetest artifact upsert` |
| `helpmetest_get_artifact` | `helpmetest artifact get <id>` |
| `helpmetest_search_artifacts` | `helpmetest artifact list` |
| `helpmetest_deploy` | `helpmetest deploy` |
| `helpmetest_open` | `helpmetest open <id>` |
| `helpmetest_delete_test` | `helpmetest delete test <id>` |
| `helpmetest_undo_update` | `helpmetest undo` |

## License

MIT
