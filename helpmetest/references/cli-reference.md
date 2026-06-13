# HelpMeTest CLI Reference

The single source of truth for `helpmetest` commands. Everything HelpMeTest does
is a CLI command — there is no MCP server. Generated from the live CLI; when in
doubt, run `helpmetest <command> --help`.

```bash
curl https://helpmetest.com/install.sh | bash   # install
helpmetest login                                 # authenticate (saves token locally)
helpmetest install skills                        # install AI skills for all detected agents
helpmetest --help                                # full command list
```

---

## Tests

```bash
helpmetest test run [identifiers...]    # run tests in parallel by name, tag, or ID
helpmetest test create                  # create a test (auto-runs immediately)
helpmetest test update <id>             # change content/tags/name, pause/resume
helpmetest test view <identifier>       # show a test's source, tags, keywords
```

- `test run` with no args runs all tests. Accepts names, IDs, or `tag:value`.
- `test create` requires `--id`, `--name`, `--content` (Robot Framework), `--tags`.
- Run `helpmetest test run --help` for output/filter flags.

## Status & monitoring

```bash
helpmetest status            # are tests green? are health checks up?
helpmetest status test       # test results only
helpmetest status health     # health check statuses only
helpmetest metrics           # inspect the heartbeat payload a host sends
helpmetest updates           # stream real-time test failures as NDJSON
```

`helpmetest status` is the first thing to run every session.

## Health checks (dead-man's switch)

```bash
helpmetest health <name> <grace_period> <command...>   # wrap a job; alert if it stops
helpmetest health <name> <grace_period>                # send a heartbeat
helpmetest delete health-check <name>                  # stop monitoring
```

Example: `helpmetest health nightly-backup 25h -- ./backup.sh` — alerts if the
backup doesn't check in within 25h.

## Interactive browser

```bash
helpmetest interactive "<keyword>"     # run one Robot keyword in a live browser
```

The browser persists between calls. Use to debug selectors or explore a page.
Send `helpmetest interactive "Exit"` to close the session.

## Search & keywords

```bash
helpmetest search [query]      # search docs, Robot keywords, artifacts, and tests
helpmetest search click        # find click-related keywords
helpmetest search wait         # find wait keywords
```

There is no separate `keywords` command — keyword lookup is part of `search`.

## Artifacts (AI knowledge base)

```bash
helpmetest artifact list             # browse artifacts (filter by type/tag/text)
helpmetest artifact get <id>         # read an artifact + full content
helpmetest artifact upsert           # create/update (idempotent, no dupes)
helpmetest artifact schema <type>    # show expected fields for a type
helpmetest artifact generate <type>  # AI-draft an artifact from a URL
helpmetest artifact delete <id>      # remove an artifact
```

Types: `ProjectOverview`, `Persona`, `Feature`, `Tasks`, etc. Run
`helpmetest artifact schema <type>` before creating one.

## Delete & undo

```bash
helpmetest delete test <identifier>      # remove a test (by name/ID/tag)
helpmetest delete health-check <name>    # remove a health check
helpmetest undo <update-id>              # restore a deleted test/health check
```

Deletions return an `update-id`; pass it to `undo` to restore.

## Deployments & dashboard

```bash
helpmetest deploy <app>          # stamp a deployment into the timeline
helpmetest open <type> [id]      # open a test/artifact/health check in the dashboard
```

## Local development (proxy)

Cloud browsers can't reach `localhost` — the proxy tunnels it:

```bash
helpmetest proxy start <target>      # e.g. ":3000" — tunnel local port to cloud
helpmetest proxy list                # active tunnels and who opened them
helpmetest proxy stop <domain>       # stop one tunnel
helpmetest proxy stop-all            # stop all tunnels
helpmetest proxy run-fake-server     # throwaway local server for testing the tunnel
```

Start the proxy BEFORE running tests against a local server.

## AI agents & skills

```bash
helpmetest agent [task...]    # spawn an AI agent with HelpMeTest skills
helpmetest ai [skill]         # shorthand for: helpmetest agent claude <skill>
helpmetest install skills     # install skills for all detected agents
helpmetest uninstall skills   # remove HelpMeTest skills
```

`install skills` installs for every detected agent. Pass `--agent <name>` to
target one (e.g. `claude-code`, `opencode`, `cursor`).

## Notifications

```bash
helpmetest notification list                 # list connected channels
helpmetest notification add telegram         # browser connect (deep link)
helpmetest notification add slack            # browser connect (OAuth)
helpmetest notification add discord          # browser connect (OAuth)
helpmetest notification add ntfy <topic>     # value channel
helpmetest notification add email <address>  # value channel
helpmetest notification add webhook <url>    # value channel
helpmetest notification test --connection-string <url>
helpmetest notification delete <id>
```

telegram/slack/discord open your browser to connect (gh/az style); the channel
appears once you authorize. ntfy/email/webhook take a value directly.

## Config & secrets

```bash
helpmetest config get <key>            # read a project config key
helpmetest config set <key> <value>    # set a key
helpmetest config unset <key>          # reset a key to default

helpmetest config env set <environment>          # default env for secrets
helpmetest config secret set/get/list/unset      # server-side secrets
helpmetest config otp set/get/list/unset         # OTP seeds
helpmetest config token create/list/delete       # API tokens
```

Secrets and OTP seeds are encrypted at rest and usable inside tests.

## Billing

```bash
helpmetest billing               # usage + subscription overview
helpmetest billing usage         # runs this period + estimated cost
helpmetest billing subscription  # plan, status, renewal
helpmetest billing invoices      # recent invoices
helpmetest billing setup         # add a payment method + start the usage subscription (opens Stripe)
```

Add `--json` to the read commands for machine-readable output. New workspaces are
free with a capped number of runs; `billing setup` lifts the cap.

## Account & maintenance

```bash
helpmetest register <companyName> <subdomain>  # create a NEW free workspace (browser login, no card)
helpmetest login          # authenticate an existing account, save token to .helpmetest/config.yaml
helpmetest logout         # remove saved token
helpmetest version        # show version
helpmetest update         # self-update to the latest CLI
helpmetest upload <file>  # upload a file to storage, print the URL
helpmetest chaos <duration>          # chaos run: random tests/order/concurrency
helpmetest completion <shell>        # tab-completion script (bash/zsh/fish)
```

---

## Conventions

- **Identifiers**: most commands accept a test by name, ID, or `tag:value`.
- **No MCP**: every capability is a CLI command. Agents call the CLI, not MCP tools.
- **Recoverable deletes**: deletions return an `update-id` for `undo`.
- **Help is authoritative**: `helpmetest <command> --help` always reflects the
  installed version. This reference summarizes it; the CLI is the source of truth.
