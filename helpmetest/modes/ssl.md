<!-- llms-description: TLS certificates, DNS, WHOIS, security headers, SPF/DKIM/DMARC, plus email, IP, IBAN/VAT and phone intelligence. -->

# HelpMeTest SSL Mode

Write and run tests that check TLS certificates using the `DomainChecker` library. No browser needed — keywords make direct TLS socket connections from inside the VM.

---

## Trigger

```
/helpmetest ssl <domain>
/helpmetest ssl              # prompts for domain
/helpmetest domain <domain>  # alias
```

---

## The Keywords

### Fetch (always first — primes the cache)

```robot
${info}=    SSL Certificate Info    helpmetest.com
```

Returns a dict with raw cert data. Every subsequent SSL keyword for the same domain reuses this cached result within the test run.

### Validity

```robot
SSL Is Valid    helpmetest.com    ==    ${TRUE}      # CA chain + hostname + not expired
SSL Is Expired    helpmetest.com    ==    ${FALSE}
SSL Days Remaining    helpmetest.com    >    30
SSL Valid From    helpmetest.com    contains    2025
SSL Valid To    helpmetest.com    contains    2026
```

### Identity

```robot
SSL Subject    helpmetest.com    *=    helpmetest.com          # *= means "contains"
SSL Subject    slava.helpmetest.com    ==    *.slava.helpmetest.com   # exact wildcard string
SSL SANs    helpmetest.com    contains    helpmetest.com       # list contains value
SSL Issuer Organization    helpmetest.com    ==    Let's Encrypt
SSL Issuer Country    helpmetest.com    ==    US
SSL Serial Number    helpmetest.com    ==    <exact serial>
SSL Resolved IP    helpmetest.com    is not empty
```

### Algorithm and protocol

```robot
SSL Algorithm    helpmetest.com    ==    sha256WithRSAEncryption
SSL Version    helpmetest.com    ==    2       # TLS 1.2 → 2, TLS 1.3 → 3
```

**Verified live 2026-09-25** against `helpmetest.com` — every keyword above exists and
returns real data. Actual values, useful as a sanity reference when a test starts failing
and you need to know whether the cert changed or the test is wrong:

| keyword | returned |
|---|---|
| `SSL Subject` | `*.slava.helpmetest.com` — note the cert serving `helpmetest.com` is a **wildcard for a different host**, so an `==` assertion on the bare domain fails while `*=` passes |
| `SSL Version` | `2` (TLS 1.2, not 1.3) |
| `SSL Algorithm` | `sha256WithRSAEncryption` |
| `SSL Issuer Organization` | `Let's Encrypt` |
| `SSL Days Remaining` | `72` |
| `SSL SANs` | `["DNS:*.helpmetest.com","DNS:*.playground.helpmetest.com","DNS:*.slava.helpmetest.com","DNS:helpmetest.com", …]` |

**`contains` is a substring match across the list, not an exact element match.** The SAN
entries all carry a `DNS:` prefix, yet both
`SSL SANs  helpmetest.com  contains  helpmetest.com` and
`SSL SANs  helpmetest.com  contains  DNS:helpmetest.com` pass. Prefer the prefixed form
when you mean a specific SAN — the bare form also matches `mta-sts.helpmetest.online` and
every wildcard, so it will keep passing after the SAN you cared about is removed.

### Assertion operators

| Operator | Meaning |
|----------|---------|
| `==` | exact equal |
| `!=` | not equal |
| `>` / `<` / `>=` / `<=` | numeric comparison |
| `*=` | contains (substring) |
| `contains` | list contains value |
| `is not empty` | non-empty string/list |

---

## Workflow: `/helpmetest ssl <domain>`

1. **Check for existing test** — look for a test covering the domain:
   ```bash
   helpmetest test view ssl-<domain-slug>
   ```
   - Found → show current pass rate, offer to run or update
   - Not found → proceed to generate

   > `test view` takes the test **id**, not its display name, and on a miss it exits 1 with
   > **no output at all** — an empty result means "no test with that id", never "a test with
   > no runs". If you need to search by name, read `helpmetest status --json` and match on
   > `tests[].name`; every row also carries `id` and the full `content`.
   >
   > This step previously said `helpmetest test show`, which does not exist. The first
   > argument to `test` is something to **run**, so the typo became a run request:
   > `✗ No test matches "show" — aborting before running any of: show, ssl-example-com`
   > (measured 2026-09-25). It aborted only because no test happens to be named `show`.

2. **Generate and push the test** — use this exact `test create` command. Comments are required and must be evenly distributed (one comment per 1-2 keywords). Required tags: `feature:ssl`, `url:<domain>`, `priority:high`, `persona:public`, `project:<project-id>`.

   ```bash
   helpmetest test create \
     --id "ssl-<domain-slug>" \
     --name "SSL Certificate Check: <domain>" \
     --tags "feature:ssl,url:<domain>,priority:high,persona:public,project:robot-infra" \
     --no-run \
     --content '# Fetch certificate and verify validity
   SSL Certificate Info    <domain>
   SSL Is Valid    <domain>    ==    ${TRUE}

   # Confirm expiry status and days remaining
   SSL Is Expired    <domain>    ==    ${FALSE}
   SSL Days Remaining    <domain>    >    30

   # Validate issuer organization
   SSL Issuer Organization    <domain>    ==    Let'\''s Encrypt

   # Check subject and subject alternative names
   SSL Subject    <domain>    *=    <domain>
   SSL SANs    <domain>    contains    <domain>

   # Verify encryption algorithm and DNS resolution
   SSL Algorithm    <domain>    ==    sha256WithRSAEncryption
   SSL Resolved IP    <domain>    is not empty'
   ```

   **Important:** Adjust `SSL Issuer Organization` and `SSL Algorithm` if the domain uses a different CA or algorithm. If unsure, run the debug check first (see below) before asserting these values.

   Use `--no-run` on create, then run separately:

3. **Run and report**
   ```bash
   helpmetest test run ssl-<domain-slug>
   ```
   Paste the literal command output. If `SSL Issuer Organization` or `SSL Algorithm` fails,
   leave the test unchanged and report the actual versus expected value and the certificate
   or server configuration change required for the existing test to pass. Do not update the
   test with a newly observed value.

4. **Report result** — PASS only alongside the literal run output; otherwise report the
   specific failing assertion and required server-side change.

---

## Debug: inspect a cert before writing assertions

Run this one-shot to see what a cert actually contains:

```bash
helpmetest test run ssl-debug-show-cert
```

Or write a quick throwaway:

```robot
${info}=    SSL Certificate Info    <domain>
Log    ${info}    console=True
```

Run it interactively:
```bash
helpmetest interactive
> Bash    python3 -c "from ssl_checker import SSLChecker; c=SSLChecker(); h,_=c.filter_hostname('<domain>:443'); cert,ip=c.get_cert(h,443); print(c.get_cert_info(h,cert,ip))"
```

---

## badssl.com fixture domains

Use these for negative assertions and library regression tests:

| Domain | `SSL Is Valid` | `SSL Is Expired` | Notes |
|--------|---------------|-----------------|-------|
| `expired.badssl.com` | `${FALSE}` | `${TRUE}` | Days remaining < 0 (~-4000) |
| `self-signed.badssl.com` | `${FALSE}` | `${FALSE}` | CA not trusted |
| `wrong.host.badssl.com` | `${FALSE}` | `${FALSE}` | Hostname mismatch |
| `untrusted-root.badssl.com` | `${FALSE}` | `${FALSE}` | Root CA not in trust store |
| `client-cert-missing.badssl.com` | `${TRUE}` | `${FALSE}` | Skip `SSL Is Valid` — handshake varies |
| `sha256.badssl.com` | `${TRUE}` | `${FALSE}` | Algorithm: `sha256WithRSAEncryption` |
| `ecc256.badssl.com` | `${TRUE}` | `${FALSE}` | Algorithm: `ecdsa-with-SHA384` |
| `rsa4096.badssl.com` | `${TRUE}` | `${FALSE}` | Algorithm: `sha256WithRSAEncryption` |

---

## Full regression test

`ssl-domainchecker-regression` covers all keywords across all fixture domains. Run it to verify DomainChecker is healthy end-to-end:

```bash
helpmetest test run ssl-domainchecker-regression
helpmetest test view ssl-domainchecker-regression --since 7d   # check history
```

Pass rate should be ≥95%. Residual ⚠️ INFRA_ERR are VM network jitter — not FAIL.

---

## Troubleshooting

**`TimeoutError: timed out` on `SSL Certificate Info`**
Transient VM network jitter on outbound port 443. The library timeout is 15s — if it still fires, retry. If every run fails, check outbound connectivity from the VM pod:
```bash
kubectl-hetzner1 exec deploy/vm -c pool -- curl -I https://helpmetest.com
```

**`SSL Is Valid` returns `${TRUE}` for self-signed**
CA validation regressed — the library is checking expiry only, not the trust chain. File a DomainChecker bug.

**`SSL Is Valid` returns `${FALSE}` for a known-good cert**
Check: clock skew on the VM, cert actually expired (`SSL Days Remaining`), or hostname mismatch (compare `SSL Subject` to the domain you passed).

**`SSL Subject` assertion fails on a wildcard cert**
Wildcard certs return the wildcard string literally, e.g. `*.helpmetest.com`. Use exact match (`==`) not contains:
```robot
SSL Subject    sub.helpmetest.com    ==    *.helpmetest.com   # correct
SSL Subject    sub.helpmetest.com    *=    helpmetest.com     # also works
```

**Cache caveat**
`SSL Certificate Info` is cached per domain per robot session. Call it once per domain at the top of the test, then run all assertions for that domain. Calling it again is a no-op — it won't re-fetch.

---

**Version:** 0.1
