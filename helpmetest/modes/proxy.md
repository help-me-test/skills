## Announce (bare invocation — no port given)

If the user invoked `/helpmetest proxy` without specifying a port or domain:

> "After this your local dev server will be reachable by HelpMeTest's test runner — so every test you write can hit your local code as if it were deployed. What port is it running on? (e.g. 3000, 5173, 8080)"

Once you have the port, set up the tunnel, verify it with an interactive command, and confirm it works before the user writes any tests.

**If port is given upfront:** skip the question, go straight to setup + verification, then report:
> "Tunnel is live on `dev.local`. I verified it with a `Go To` — your app loaded. You can now write tests using `http://dev.local` as the URL."

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

1. You start a proxy via the CLI — it registers a tunnel with the proxy server (everything needed is **bundled with the CLI** — no separate installation needed)
2. The tunnel maps a domain (e.g. `dev.local`) to your local port
3. HelpMeTest's test runner routes traffic for that domain through the tunnel back to your machine
4. Your local server responds as if accessed directly

**The proxied URL (e.g. http://dev.local) is NOT accessible from your local browser or curl.** It only works inside HelpMeTest test commands (`Go To`, `helpmetest interactive`, etc.).

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

## ⚠️ Service must be reachable from the proxy

The proxy connects to `127.0.0.1:PORT` from the machine it runs on. If it runs in a container or cloud agent environment, it cannot reach a service that is only bound to `127.0.0.1` on the user's local machine.

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

## Proxy Installation

The proxy is **auto-installed on first use** — no manual steps needed. When you run `helpmetest proxy start`, the CLI downloads and sets up everything automatically.

If auto-install fails (e.g., network error), re-run `helpmetest proxy start` or check your internet connection.

## When to Use

- Testing against localhost during development
- Substituting production URLs with local versions
- Routing frontend and backend on different ports
- Before writing or running any local tests

## Quick Start

**Start a proxy:**
```
helpmetest proxy start localhost:3000
```

**Verify it works (use HelpMeTest, NOT curl):**
```bash
helpmetest interactive "Go To  http://dev.local"
```
Should load your local app. If it doesn't, fix the proxy before writing tests.

**Check active proxies:**
```bash
helpmetest proxy list
```

**Stop a proxy:**
```bash
helpmetest proxy stop dev.local
```

## Three Proxy Strategies

### Strategy 1: Single Tunnel to Frontend

**When:** Your dev server already proxies some routes internally (e.g., Vite's `server.proxy` sends `/api` to backend port)

```
helpmetest proxy start localhost:5001
```

Tests use `http://dev.local` — both UI and API calls work through one tunnel.

---

### Strategy 2: Separate Tunnels for Frontend and Backend

**When:** Services need different hostnames (cookies, CORS), or no internal proxy configured.

```
helpmetest proxy start localhost:5001  # maps to frontend.local
helpmetest proxy start localhost:3001  # maps to backend.local
```

Tests use `http://frontend.local` for UI and `http://backend.local` for API.

---

### Strategy 3: Substitute Production with Local

**When:** You have tests running against production URLs and want to test local changes without modifying test code.

```
helpmetest proxy start localhost:3000  # routes my.awesome.app traffic to local port 3000
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

```bash
helpmetest interactive "Go To  http://dev.local"
```

Expected: Your local app loads successfully. If you see `chrome-error://chromewebdata/` or a connection error, the proxy is not working — fix it before writing tests.

**Do NOT try to verify with curl or your local browser** — the proxy only works inside HelpMeTest's infrastructure.

## Troubleshooting

### Tests show chrome-error or connection refused

1. **Check you're using the proxy domain in test URLs** — `Go To  http://dev.local` NOT `http://localhost:3000`
2. **Check proxy is running:** `helpmetest proxy list`
3. **Check local server is running:** `curl http://127.0.0.1:3000` (this works locally — if this fails, start your server)
4. **Restart proxy if needed:** Stop and start again

### Service on 127.0.0.1 not reachable

If your server is bound to `127.0.0.1` (loopback only), restart it with `0.0.0.0` binding — see the "Service must be reachable" section above.

### Stale proxy blocking new one

If starting a proxy fails with "proxy already exists":
- Stop the proxy first: `helpmetest proxy stop dev.local`
- Or stop all: `helpmetest proxy stop --all`

### Custom hostname not resolving

Custom hostnames (like `frontend.local`) are handled entirely by the proxy — no `/etc/hosts` edits needed. If verification fails:
1. Verify proxy is running with `list` action
2. Make sure you're using HTTP (not HTTPS) unless you have TLS configured
3. Check the exact domain matches what you used in `start`

## Multiple Services Example

```
# Local frontend on port 5001
helpmetest proxy start localhost:5001  # frontend.local

# Local backend API on port 3001
helpmetest proxy start localhost:3001  # api.local

# Production service running locally on port 8000
helpmetest proxy start localhost:8000  # prod.myapp.com
```

Tests can now use all three domains inside HelpMeTest commands.

## Best Practices

1. **Start proxy BEFORE writing tests** — don't debug test failures caused by missing proxy
2. **Always verify with HelpMeTest** — use interactive commands, not curl or browser
3. **Choose simplest strategy** — if frontend already proxies backend, use Strategy 1
4. **Use consistent domains** — if you use `frontend.local` in one test, use it in all tests for that service
5. **Stop proxies when done** — `helpmetest proxy stop --all` cleans up everything

**Version:** 0.2
