<!-- llms-description: Tunnel HelpMeTest cloud browsers to a localhost dev server. -->

## Announce (bare invocation — no port given)

If the user invoked `/helpmetest proxy` without specifying a port or domain:

**Derive the port before you ask for it.** Check, in order: the manifest's dev/start
script (`"dev": "vite --port 5173"`, `python3 -m http.server 4321`), `.env`
(`PORT`, `VITE_PORT`), `docker-compose.yml` / `Dockerfile` `ports:`/`EXPOSE`, then a
running process on a common port. A real run found the port sitting in `package.json`
while this file was telling it to ask — which violates the brain's core rule that a
question about a fact is an admission you didn't look.

If you derived it, say so and proceed:

> "Your dev server is on port 4321 (from `package.json`'s `dev` script). Tunnelling it so
> the cloud runner can reach your local code as if it were deployed."

Only if it genuinely isn't discoverable, ask once:

> "After this your local dev server will be reachable by HelpMeTest's test runner — so every test you write can hit your local code as if it were deployed. What port is it running on? (e.g. 3000, 5173, 8080)"

Then set up the tunnel, verify it with an interactive command, and confirm it works before the user writes any tests.

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

## ❌ The #1 Mistake — a test URL the tunnel does not cover

The cloud runner cannot reach your machine on its own. It reaches whatever **domain and
external port you registered**, and nothing else. The URL in the test must be the one you
tunnelled.

**`localhost` is rejected as a proxy domain.** Measured 2026-09-25, both forms:

```
$ helpmetest proxy start localhost:37331
$ helpmetest proxy start localhost:37331:37331
✗ Cannot use "localhost" as a proxy domain — it is the external name tests navigate to,
  not the local address.
Use a project-named domain instead, e.g.: myapp.local:37331
```

This section previously argued the opposite, citing `proxy start --help`, which still lists
`localhost:3001:3001` among its examples. **The CLI's help and the CLI's validation
disagree, and validation wins** — that example cannot run. Do not "fix" a working tunnel
back to `localhost` on the strength of the help text.

The bare-port form does work, but not the way you might assume: `helpmetest proxy start
:37331` prints `Starting tunnel: dev.local:37331`. It defaults the **domain** to
`dev.local`; tests then navigate to `http://dev.local`, not to `localhost`.

```robot
# RIGHT — you ran: helpmetest proxy start dev.local:80:3000
Go To  http://dev.local

# RIGHT — you ran: helpmetest proxy start :3000  (domain defaults to dev.local)
Go To  http://dev.local

# WRONG — nothing forwards localhost to the cloud runner, and the tunnel could not
# have been registered under that name in the first place
Go To  http://localhost:3000
```

**Every test URL must match the tunnel you actually registered.** Check with
`helpmetest proxy list` if you are unsure — note it displays the *external* port, not the
source port.

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
helpmetest proxy start dev.local:3000        # tests navigate to http://dev.local
```

**Verify it works (use HelpMeTest, NOT curl):**
```bash
helpmetest interactive "Go To  http://dev.local"
```
Should load your local app. If it doesn't, fix the proxy before writing tests.

**No app to point at yet? The CLI ships a throwaway one** — `helpmetest proxy
run-fake-server` (default port 37331, `--port` to change). It was undocumented here until
2026-09-25. The full loop, verified end to end that day:

```bash
helpmetest proxy run-fake-server --port 37331   # terminal 1 — serves a demo page
helpmetest proxy start zzprobe.local:37331      # terminal 2 — KEEP RUNNING
helpmetest interactive run "Go To  http://zzprobe.local" "Get Title"
```

Real output from that run — the cloud browser reaching a server on this laptop:

```
✓ Go To  http://zzprobe.local        200
✓ Get Title                          Demo App - HelpMeTest Tutorial
✓ Browser.Get Text  body             This is a demo app running on localhost:37331
```

`proxy start` is a **long-running foreground process** — it holds the tunnel open and
prints `KEEP THIS PROCESS RUNNING while tests execute`. Run it in its own terminal or as a
managed background process; if you launch it from a script and the script waits on it, you
will wait forever. Tear down with `helpmetest proxy stop <domain>` and confirm with
`helpmetest proxy list` → `No active tunnels found`.

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
helpmetest proxy start dev.local:5001
```

Tests use `http://dev.local` — both UI and API calls work through one tunnel.

---

### Strategy 2: Separate Tunnels for Frontend and Backend

**When:** Services need different hostnames (cookies, CORS), or no internal proxy configured.

```
helpmetest proxy start frontend.local:5001
helpmetest proxy start backend.local:3001
```

Tests use `http://frontend.local` for UI and `http://backend.local` for API.

---

### Strategy 3: Substitute Production with Local

**When:** You have tests running against production URLs and want to test local changes without modifying test code.

```
helpmetest proxy start my.awesome.app:80:3000   # tests hit my.awesome.app → local port 3000
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
- Or stop all: `helpmetest proxy stop-all` — **`proxy stop --all` does not exist**; it
  fails with `error: unknown option '--all'` (verified 2026-09-25). `stop` takes a required
  domain argument; `stop-all` is its own subcommand.

### Custom hostname not resolving

Custom hostnames (like `frontend.local`) are handled entirely by the proxy — no `/etc/hosts` edits needed. If verification fails:
1. Verify proxy is running with `list` action
2. Make sure you're using HTTP (not HTTPS) unless you have TLS configured
3. Check the exact domain matches what you used in `start`

## Multiple Services Example

```
# Local frontend on port 5001
helpmetest proxy start frontend.local:5001

# Local backend API on port 3001
helpmetest proxy start backend.local:3001

# Production hostname served from a local port 8000
helpmetest proxy start prod.myapp.com:80:8000
```

Tests can now use all three domains inside HelpMeTest commands.

## Best Practices

1. **Start proxy BEFORE writing tests** — don't debug test failures caused by missing proxy
2. **Always verify with HelpMeTest** — use interactive commands, not curl or browser
3. **Choose simplest strategy** — if frontend already proxies backend, use Strategy 1
4. **Use consistent domains** — if you use `frontend.local` in one test, use it in all tests for that service
5. **Stop proxies when done** — `helpmetest proxy stop-all` cleans up everything (not `stop --all`)

**Version:** 0.2
