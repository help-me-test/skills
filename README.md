# HelpMeTest Skills

Official skills for HelpMeTest - AI-powered test automation agent.

## Installation

### Using npx skills (Standard)

```bash
npx skills add help-me-test/skills
```

### Using HelpMeTest CLI (Convenience)

```bash
helpmetest install skills
```

This command uses the `skills` package under the hood but provides HelpMeTest-branded experience.

## Available Skills

- **helpmetest** - QA Agency orchestrator for comprehensive test automation
- **helpmetest-discover** - Explore websites to discover features and personas
- **helpmetest-test-generator** - Generate Robot Framework tests for features
- **helpmetest-validator** - Validate test quality and score
- **helpmetest-debugger** - Debug failing tests
- **helpmetest-self-heal** - Self-healing test maintenance
- **helpmetest-visual-check** - Quick visual verification of design and UI

## Compatibility

These skills follow the [Agent Skills open standard](https://github.com/vercel-labs/skills) and work with:

- Claude Code
- Cline
- Cursor
- Windsurf
- GitHub Copilot
- And 30+ other AI coding agents

## No MCP? Use the CLI

If your AI agent doesn't support MCP, or you prefer shell commands, the HelpMeTest CLI has **full feature parity** with all MCP tools. Every MCP tool has an equivalent CLI command:

| MCP tool | CLI equivalent |
|----------|----------------|
| `helpmetest_status` | `helpmetest status` |
| `helpmetest_run_test` | `helpmetest test run <id>` |
| `helpmetest_upsert_test` | `helpmetest test create` / `helpmetest test update <id>` |
| `helpmetest_run_interactive_command` | `helpmetest interactive "<command>"` |
| `helpmetest_keywords` | `helpmetest keywords [search]` |
| `how_to` | `helpmetest how-to [type]` |
| `helpmetest_proxy` | `helpmetest proxy start/stop/list/stop_all` |
| `helpmetest_upsert_artifact` | `helpmetest artifact upsert` |
| `helpmetest_get_artifact` | `helpmetest artifact get <id>` |
| `helpmetest_search_artifacts` | `helpmetest artifact list` |
| `helpmetest_generate_artifact` | `helpmetest artifact generate <type>` |
| `helpmetest_delete_artifact` | `helpmetest artifact delete <id>` |
| `helpmetest_deploy` | `helpmetest deploy` |
| `helpmetest_open` | `helpmetest open <id>` |
| `helpmetest_delete_test` | `helpmetest delete test <id>` |
| `helpmetest_undo_update` | `helpmetest undo` |

Skills use `mcp__helpmetest-*` in their frontmatter, but you can ignore that and use the CLI equivalents above. The skills describe workflows — the tool names are interchangeable.

## Contributing

Skills are defined using standard SKILL.md format with YAML frontmatter. See individual skill directories for examples.

## License

MIT
