# HelpMeTest CI Integration

Run HelpMeTest tests as part of your CI pipeline — on every push, PR, or scheduled run.

## Overview

HelpMeTest runs tests in a real cloud browser. From CI, you:

1. Create a CI-scoped API token
2. Install the `helpmetest` binary
3. Run tests with `helpmetest test run` and exit on failure

Your CI machine never runs a browser. Tests execute remotely — CI just triggers them and streams results.

---

## Step 1 — Create a CI Token

**Never use your personal API token in CI.** Create a dedicated token so you can rotate or revoke it without breaking your local setup.

```bash
helpmetest token create ci-github-actions
```

Output:
```
✓ Created token 'ci-github-actions'
  Token: HELP-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Copy the token. Store it as a secret in your CI system:

| Platform | How |
|----------|-----|
| GitHub Actions | Settings → Secrets and variables → Actions → `HELPMETEST_API_TOKEN` |
| GitLab CI | Settings → CI/CD → Variables → `HELPMETEST_API_TOKEN` |
| CircleCI | Project Settings → Environment Variables → `HELPMETEST_API_TOKEN` |
| Bitbucket | Repository settings → Repository variables → `HELPMETEST_API_TOKEN` |

**Manage tokens:**
```bash
helpmetest token list          # see all tokens
helpmetest token delete old-token   # rotate a compromised one
```

---

## Step 2 — Install the CLI in CI

Add this to your CI job before running tests. It downloads the latest binary for the runner's OS:

```bash
curl -fsSL https://helpmetest.com/install | sh
```

The binary lands at `/usr/local/bin/helpmetest` and is immediately available.

**If your runner blocks curl-to-shell installs**, download the binary directly:

```bash
# Linux x86_64
curl -fsSL https://helpmetest.com/install/helpmetest-linux-x64 -o /usr/local/bin/helpmetest
chmod +x /usr/local/bin/helpmetest

# Linux arm64
curl -fsSL https://helpmetest.com/install/helpmetest-linux-arm64 -o /usr/local/bin/helpmetest
chmod +x /usr/local/bin/helpmetest
```

**Verify:**
```bash
helpmetest version
```

---

## Step 3 — Run Tests

The `HELPMETEST_API_TOKEN` env var is picked up automatically — no `helpmetest login` needed in CI.

```bash
# Run all tests
helpmetest test run

# Run tests with a specific tag
helpmetest test run "#priority:critical"

# Run a specific test by name
helpmetest test run "Login Flow"

# Run multiple tags
helpmetest test run "#priority:critical" "#feature:checkout"
```

Exit code is `0` on all pass, `1` on any failure — standard CI gate behavior.

---

## Platform Examples

### GitHub Actions

```yaml
name: HelpMeTest

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install HelpMeTest
        run: curl -fsSL https://helpmetest.com/install | sh

      - name: Run critical tests
        env:
          HELPMETEST_API_TOKEN: ${{ secrets.HELPMETEST_API_TOKEN }}
        run: helpmetest test run "#priority:critical"
```

### GitLab CI

```yaml
helpmetest:
  stage: test
  image: ubuntu:latest
  before_script:
    - curl -fsSL https://helpmetest.com/install | sh
  script:
    - helpmetest test run "#priority:critical"
  variables:
    HELPMETEST_API_TOKEN: $HELPMETEST_API_TOKEN
```

### CircleCI

```yaml
version: 2.1
jobs:
  helpmetest:
    docker:
      - image: cimg/base:stable
    steps:
      - checkout
      - run:
          name: Install HelpMeTest
          command: curl -fsSL https://helpmetest.com/install | sh
      - run:
          name: Run tests
          command: helpmetest test run "#priority:critical"
```

### Bitbucket Pipelines

```yaml
pipelines:
  default:
    - step:
        name: HelpMeTest
        script:
          - curl -fsSL https://helpmetest.com/install | sh
          - helpmetest test run "#priority:critical"
```

### Makefile / shell script

```bash
#!/bin/bash
set -e

curl -fsSL https://helpmetest.com/install | sh
helpmetest test run "#priority:critical"
```

---

## JSON Output for CI Tooling

Stream results as NDJSON for custom reporters, Slack notifications, or test result aggregators:

```bash
helpmetest test run "#priority:critical" --json
```

Each line is a JSON event. The final line with `"type": "end_suite"` carries the overall result:

```json
{"type": "end_suite", "status": "PASS", "passed": 12, "failed": 0}
```

Use `--select` to pull only what you need:

```bash
# Just the final status line
helpmetest test run "#priority:critical" --json \
  | grep '"type":"end_suite"' \
  | python3 -c "import json,sys; r=json.load(sys.stdin); print(r['status'])"
```

---

## Mark Deployments in the Timeline

After deploying, stamp it so test failures are correlated with the release:

```bash
helpmetest deploy my-app --description "$(git log -1 --pretty=%s)"
```

This appears in the HelpMeTest timeline — you can see whether a test started failing before or after a given deploy.

---

## What Tag to Run

| Tag | When |
|-----|------|
| `#priority:critical` | Every push to main — fast, catches regressions |
| `#priority:critical #priority:high` | PR gates — broader coverage |
| `#feature:checkout` | After deploying checkout changes only |
| (all tests) | Nightly / scheduled runs |

Don't run all tests on every push — it's slow and noisy. Run critical on push, full suite on schedule.

---

## Testing a Staging or Localhost Server from CI

If your tests hit a URL that isn't publicly reachable (internal staging, localhost, VPN-only), the cloud runner can't reach it directly. Use the proxy to bridge the gap.

**Add a proxy start step before running tests:**

```bash
# Tunnel your local dev server
helpmetest proxy start localhost:3000

# Or tunnel an internal staging server
helpmetest proxy start https://staging.internal.mycompany.com
```

Then tests use the proxy domain (`http://dev.local`) instead of the real URL. The proxy step must come before `helpmetest test run` in your CI job.

**Full details in `modes/proxy.md`** — covers multi-tunnel strategies, WebSocket, and how to verify the tunnel actually works before writing tests.

---

## Troubleshooting

**`HELPMETEST_API_TOKEN` not set** — double-check the secret name in your CI platform matches exactly, including case.

**`helpmetest: command not found`** — install step failed silently. Add `set -e` to abort on error, or check the install output explicitly.

**Tests pass locally, fail in CI** — most likely the tests hit a URL that isn't reachable from HelpMeTest's cloud runners (e.g. a staging server on a private VPN). Either open the firewall or use `helpmetest proxy` to tunnel.

**All tests skip / 0 run** — the tag filter matched nothing. Check tag names with `helpmetest status` locally.

**Version:** 0.1
