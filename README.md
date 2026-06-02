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

## CLI Reference

The HelpMeTest CLI is the primary interface:

| Command | What it does |
|---------|--------------|
| `helpmetest status` | Show tests and their current state |
| `helpmetest test run <id>` | Run a test |
| `helpmetest test create` / `helpmetest test update <id>` | Create or update a test |
| `helpmetest interactive "<command>"` | Run an interactive browser command |
| `helpmetest keywords [search]` | List available keywords |
| `helpmetest how-to [type]` | Show how-to guides |
| `helpmetest proxy start/stop/list` | Manage localhost tunnels |
| `helpmetest artifact upsert` | Create or update an artifact |
| `helpmetest artifact get <id>` | Fetch an artifact |
| `helpmetest artifact list` | List artifacts |
| `helpmetest deploy` | Deploy |
| `helpmetest open <id>` | Open a resource |
| `helpmetest delete test <id>` | Delete a test |
| `helpmetest undo` | Undo last update |

## License

MIT
