# HelpMeTest Terminal Mode

Run shell commands inside the HelpMeTest test runner using the `Bash` keyword. Use this to run unit tests (Jest, pytest, Go test, Cargo…), lint, build, or any CLI tool as part of a HelpMeTest test.

---

## The One Keyword: `Bash`

```robot
${output}=    Bash    <command>
```

- Runs the command in a persistent bash session inside the VM
- Returns **stdout as a plain string** — captured, not printed
- The session persists across `Bash` calls in the same test — environment variables, working directory, and installed packages carry over
- Default timeout: 30s. Override with the `timeout` argument: `Bash    npm install    timeout=120s`

**Critical:** `Bash` only captures stdout. To capture stderr too, append `2>&1` to the command.

---

## Exit Code Pattern

`Bash` does **not** raise on non-zero exit — it just returns whatever stdout produced. To assert the exit code, append `; echo "EXIT=$?"` to the command and check for `EXIT=0`:

```robot
${result}=    Bash    npm test 2>&1; echo "EXIT=$?"
Should Contain    ${result}    EXIT=0
```

This works even when the command itself fails — the `echo` always runs.

---

## Running Unit Tests — Full Pattern

This is the canonical pattern. Works for any test runner.

```robot
# 1. Clone the repo (or it may already be available in the VM)
${clone}=    Bash    git clone https://github.com/your-org/your-repo /tmp/repo && echo "CLONE_OK"
Should Contain    ${clone}    CLONE_OK

# 2. Install dependencies
${install}=    Bash    cd /tmp/repo && npm ci 2>&1 && echo "INSTALL_OK"    timeout=120s
Should Contain    ${install}    INSTALL_OK

# 3. Run tests — capture stderr too, always capture exit code
${result}=    Bash    cd /tmp/repo && npm test -- --no-coverage 2>&1; echo "EXIT=$?"    timeout=120s
Log    ${result}

# 4. Assert they passed
Should Contain    ${result}    EXIT=0
```

**Why `; echo "EXIT=$?"`** — not `&&`: `&&` only runs the echo on success. `;` always runs it, so you can see whether it passed or failed in the output before the assertion fires.

---

## What's Pre-installed

The test runner comes with:

- `node` / `npm` / `npx`
- `python3` / `pip3`
- `git`
- `curl` / `wget`
- `bun`
- Standard Linux userland (bash, grep, awk, sed, find…)

**Not pre-installed:** Go, Rust/Cargo, Java, Ruby — install them in the test if needed.

---

## Examples by Test Runner

### Jest

```robot
# Clone repo
${clone}=    Bash    git clone https://github.com/your-org/repo /tmp/repo && echo "OK"
Should Contain    ${clone}    OK

# Install
${install}=    Bash    cd /tmp/repo && npm ci 2>&1 && echo "OK"    timeout=120s
Should Contain    ${install}    OK

# Run
${result}=    Bash    cd /tmp/repo && npx jest --ci --no-coverage 2>&1; echo "EXIT=$?"    timeout=120s
Should Contain    ${result}    EXIT=0
Should Match Regexp    ${result}    \\d+ passed
```

### pytest

```robot
${clone}=    Bash    git clone https://github.com/your-org/repo /tmp/repo && echo "OK"
Should Contain    ${clone}    OK

${install}=    Bash    cd /tmp/repo && pip3 install -r requirements.txt 2>&1 && echo "OK"    timeout=120s
Should Contain    ${install}    OK

${result}=    Bash    cd /tmp/repo && python3 -m pytest -v 2>&1; echo "EXIT=$?"    timeout=120s
Should Contain    ${result}    EXIT=0
Should Match Regexp    ${result}    \\d+ passed
```

### Bun test

```robot
${clone}=    Bash    git clone https://github.com/your-org/repo /tmp/repo && echo "OK"
Should Contain    ${clone}    OK

${install}=    Bash    cd /tmp/repo && bun install 2>&1 && echo "OK"    timeout=60s
Should Contain    ${install}    OK

${result}=    Bash    cd /tmp/repo && bun test 2>&1; echo "EXIT=$?"    timeout=120s
Should Contain    ${result}    EXIT=0
```

### Go test

```robot
# Install Go first
${go}=    Bash    curl -fsSL https://go.dev/dl/go1.22.linux-amd64.tar.gz | tar -C /usr/local -xz && echo "OK"    timeout=120s
Should Contain    ${go}    OK

${clone}=    Bash    PATH=$PATH:/usr/local/go/bin git clone https://github.com/your-org/repo /tmp/repo && echo "OK"
Should Contain    ${clone}    OK

${result}=    Bash    cd /tmp/repo && PATH=$PATH:/usr/local/go/bin go test ./... 2>&1; echo "EXIT=$?"    timeout=120s
Should Contain    ${result}    EXIT=0
```

---

## Using as a CI Gate in GitHub Actions

Combine with the `ci` mode: HelpMeTest runs unit tests in the VM as a step in your GHA pipeline.

```yaml
- name: Run unit tests via HelpMeTest
  env:
    HELPMETEST_API_TOKEN: ${{ secrets.HELPMETEST_API_TOKEN }}
  run: helpmetest test run "Jest Unit Tests"
```

The test clones your repo, installs, runs Jest, and fails the HelpMeTest test (exit 1) if any Jest tests fail — which fails the GHA job. No browser needed, no separate test runner setup.

See `modes/ci.md` for the full CI integration guide.

---

## Asserting More Than Exit Code

The full Jest output is in `${result}` — you can assert specific things:

```robot
${result}=    Bash    cd /tmp/repo && npx jest --ci 2>&1; echo "EXIT=$?"    timeout=120s

# Exit clean
Should Contain    ${result}    EXIT=0

# At least some tests ran (guard against empty suite)
Should Match Regexp    ${result}    \\d+ passed

# No tests were skipped unexpectedly
Should Not Contain    ${result}    0 passed

# No snapshot failures
Should Not Contain    ${result}    obsolete snapshots
```

---

## Timeouts

The default is 30s — too short for `npm install`. Always set `timeout` on install and test steps:

```robot
Bash    cd /tmp/repo && npm ci 2>&1    timeout=120s
Bash    cd /tmp/repo && npm test 2>&1; echo "EXIT=$?"    timeout=180s
```

---

## Private Repos

For private GitHub repos, pass a token via the clone URL:

```robot
${token}=    Get Secret    default    secret    github_token
${clone}=    Bash    git clone https://${token}@github.com/your-org/private-repo /tmp/repo && echo "OK"
Should Contain    ${clone}    OK
```

Store the token with `helpmetest secret set github_token ghp_xxxx`.

---

## Troubleshooting

**`CLONE_OK` not in output** — repo URL is wrong or the network is blocked. Check the exact URL and whether the repo is public.

**`INSTALL_OK` not in output** — `npm ci` failed. Add `Log    ${install}` before the assertion to see the error.

**Test output is empty** — you forgot `2>&1`. Jest writes to stderr by default.

**EXIT=1 but tests look fine** — Jest exits 1 on any failure including snapshot mismatches or coverage thresholds. Read the full output with `Log    ${result}`.

**Timeout** — increase the `timeout` argument. `npm ci` on a cold VM can take 60–90s.

**Version:** 0.1
