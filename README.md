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

## Contributing

Skills are defined using standard SKILL.md format with YAML frontmatter. See individual skill directories for examples.

## License

MIT
