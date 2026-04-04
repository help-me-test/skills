---
name: proxy
description: "Set up HelpMeTest proxy tunnels for local development testing. Use when user needs to test localhost, wants to substitute production URLs with local ports, or needs to route multiple services. Use when user says 'set up proxy', 'test localhost', 'tunnel to local', or before running tests against local development servers."
allowed-tools: mcp__helpmetest-*
---

> **No MCP?** The CLI has full feature parity — use `helpmetest proxy start/stop/list` instead of `helpmetest_proxy({...})`. See the [CLI reference](../README.md#no-mcp-use-the-cli).

---

> ### 🔴 YOU WRITE THE TEST FIRST.
> Changed code → run the tests.
> New feature → write the test before the code.
> The test is the spec. The test is done when it's green.
> **No test = not done.**

---


# HelpMeTest Proxy Setup

Sets up proxy tunnels to test local development servers through HelpMeTest.

## How It Works

HelpMeTest tests run on remote infrastructure. Your local dev server (localhost:3000) is not reachable from there. The proxy creates a TCP tunnel:

1. You start a proxy via the MCP tool — it registers a tunnel with the proxy server and spawns an frpc process (frpc is **bundled with the CLI** — no separate installation needed)
2. The tunnel maps a domain (e.g. `dev.local`) to your local port
3. HelpMeTest's test runner routes traffic for that domain through the tunnel back to your machine
4. Your local server responds as if accessed directly

**The proxied URL (e.g. http://dev.local) is NOT accessible from your local browser or curl.** It only works inside HelpMeTest test commands (`Go To`, `helpmetest_run_interactive_command`, etc.).

## ❌ The #1 Mistake — Using localhost in test URLs

Setting up the proxy and then using `localhost` in tests accomplishes nothing. The cloud runner cannot reach localhost.

```robot
# WRONG — cloud runner can't reach localhost, proxy is useless
Go To  http://localhost:3000

# WRONG — same problem
Go To  http://127.0.0.1:3000

# RIGHT — use the proxy domain you configured
Go To  http://dev.local
```

**After starting the proxy, every test URL must use the proxy domain, not localhost.**

## ⚠️ Service must be reachable from where frpc runs

frpc connects to `127.0.0.1:PORT` from the machine it runs on. If frpc runs in a container or cloud agent environment, it cannot reach a service that is only bound to `127.0.0.1` on the user's local machine.

**If the proxy fails to connect to your local server:**

Check whether your dev server is bound to `127.0.0.1` (loopback only) instead of `0.0.0.0` (all interfaces). Many tools default to loopback:

```bash
# Vite — add --host flag
vite --host
# or in vite.config.js: server: { host: '0.0.0.0' }

# Next.js
next dev -H 0.0.0.0

# Other Node.js servers — pass host option or set HOST=0.0.0.0 env var
```

After changing the bind address, restart the server and retry the proxy.

## frpc Installation

frpc is **auto-installed on first use** — no manual steps needed. When you run `helpmetest proxy start` (or `helpmetest_proxy({ action: "start", ... })`), the CLI checks for frpc at `~/.local/bin/frpc`. If missing, it downloads and installs automatically from `https://slava.helpmetest.com/install/frpc`.

If auto-install fails (e.g., network error), install manually:
```bash
brew install frp   # macOS
# or download from https://github.com/fatedier/frp/releases
```

## When to Use

- Testing against localhost during development
- Substituting production URLs with local versions
- Routing frontend and backend on different ports
- Before writing or running any local tests

## Quick Start

**Start a proxy:**
```
helpmetest_proxy({ action: "start", domain: "dev.local", sourcePort: 3000 })
```

**Verify it works (use HelpMeTest, NOT curl):**
```
helpmetest_run_interactive_command({ command: "Go To  http://dev.local" })
```
Should load your local app. If it doesn't, fix the proxy before writing tests.

**Check active proxies:**
```
helpmetest_proxy({ action: "list" })
```

**Stop a proxy:**
```
helpmetest_proxy({ action: "stop", domain: "dev.local" })
```

## Three Proxy Strategies

### Strategy 1: Single Tunnel to Frontend

**When:** Your dev server already proxies some routes internally (e.g., Vite's `server.proxy` sends `/api` to backend port)

```
helpmetest_proxy({ action: "start", domain: "dev.local", sourcePort: 5001 })
```

Tests use `http://dev.local` — both UI and API calls work through one tunnel.

---

### Strategy 2: Separate Tunnels for Frontend and Backend

**When:** Services need different hostnames (cookies, CORS), or no internal proxy configured.

```
helpmetest_proxy({ action: "start", domain: "frontend.local", sourcePort: 5001 })
helpmetest_proxy({ action: "start", domain: "backend.local", sourcePort: 3001 })
```

Tests use `http://frontend.local` for UI and `http://backend.local` for API.

---

### Strategy 3: Substitute Production with Local

**When:** You have tests running against production URLs and want to test local changes without modifying test code.

```
helpmetest_proxy({ action: "start", domain: "my.awesome.app", sourcePort: 3000, externalPort: 80 })
```

Tests use `http://my.awesome.app` — routes to localhost:3000 instead of production.

**Port mapping:**
- `domain` — hostname in test URLs
- `externalPort` — port in test URLs (default 80 for HTTP)
- `sourcePort` — your local development port

## WebSocket Support

- `wss://` (TLS WebSocket) works through the tunnel via CONNECT
- `ws://` (plain WebSocket) does NOT work — browsers block non-TLS WebSocket through HTTP proxy

If your app uses WebSocket, make sure it connects over `wss://`.

## Verification

**After starting a proxy, always verify using HelpMeTest interactive commands:**

```
helpmetest_run_interactive_command({ command: "Go To  http://dev.local" })
```

Expected: Your local app loads successfully. If you see `chrome-error://chromewebdata/` or a connection error, the proxy is not working — fix it before writing tests.

**Do NOT try to verify with curl or your local browser** — the proxy only works inside HelpMeTest's infrastructure.

## Troubleshooting

### Tests show chrome-error or connection refused

1. **Check you're using the proxy domain in test URLs** — `Go To  http://dev.local` NOT `http://localhost:3000`
2. **Check proxy is running:** `helpmetest_proxy({ action: "list" })`
3. **Check local server is running:** `curl http://127.0.0.1:3000` (this works locally — if this fails, start your server)
4. **Restart proxy if needed:** Stop and start again

### Service on 127.0.0.1 not reachable

If your server is bound to `127.0.0.1` (loopback only), restart it with `0.0.0.0` binding — see the "Service must be reachable" section above.

### Stale frpc processes blocking new proxy

If starting a proxy fails with "proxy already exists":
- A previous frpc process may still be running with the same name
- Stop the proxy first: `helpmetest_proxy({ action: "stop", domain: "dev.local" })`
- Or stop all: `helpmetest_proxy({ action: "stop_all" })`
- If MCP-managed stop doesn't work, check for orphaned frpc processes: `ps aux | grep frpc`

### MCP tool shows old output format

If the proxy tool output looks different from what's documented here, the MCP server may be running old code. Restart the MCP server with `/mcp`.

### Custom hostname not resolving

Custom hostnames (like `frontend.local`) are handled entirely by the proxy — no `/etc/hosts` edits needed. If verification fails:
1. Verify proxy is running with `list` action
2. Make sure you're using HTTP (not HTTPS) unless you have TLS configured
3. Check the exact domain matches what you used in `start`

## Multiple Services Example

```
# Local frontend on port 5001
helpmetest_proxy({ action: "start", domain: "frontend.local", sourcePort: 5001 })

# Local backend API on port 3001
helpmetest_proxy({ action: "start", domain: "api.local", sourcePort: 3001 })

# Production service running locally on port 8000
helpmetest_proxy({ action: "start", domain: "prod.myapp.com", sourcePort: 8000, externalPort: 80 })
```

Tests can now use all three domains inside HelpMeTest commands.

## Best Practices

1. **Start proxy BEFORE writing tests** — don't debug test failures caused by missing proxy
2. **Always verify with HelpMeTest** — use interactive commands, not curl or browser
3. **Choose simplest strategy** — if frontend already proxies backend, use Strategy 1
4. **Use consistent domains** — if you use `frontend.local` in one test, use it in all tests for that service
5. **Stop proxies when done** — `stop_all` cleans up everything

**Version:** 0.2
