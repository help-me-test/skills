# Failure Categories

Fixed taxonomy for classifying a failing test. Use exactly one category — never free text.
Modeled on the same discipline as fixed-vocabulary classifiers: a hypothesis, backed by first checks, not a guess.

| Category | Use When | First Checks |
|---|---|---|
| `element_not_found` | A selector, element, or UI description used by the test was unavailable at run time. | Failed step's Keywords entry, `Interactive` section from a reproduction run — is the element gone (real bug) or renamed/moved (test issue)? |
| `timing` | The right element/state exists but the test acted before it was ready, or asserted before an async update landed. | Step duration in the run, whether a `Wait For Load State`/explicit wait preceded the failing step. |
| `assertion_failure` | The app was reachable and interactable, but the actual value/state didn't match what the test expected. | The assertion's expected vs actual values; whether the underlying behavior intentionally changed (`git log`/`git diff` on the owning feature). |
| `auth_or_state` | Test failed because of missing/expired auth, or state not carried over from a prior step (`Save As`/`As` misuse, test isolation). | `--auth` history on the session, whether `Save As` ran and succeeded earlier in the same suite, 401/403 in Network. |
| `api_or_backend` | The UI is fine but a backend call failed — 4xx/5xx, malformed response, or an endpoint that doesn't exist. | `Network` section for the failing request's status code and response body. |
| `environment` | Failure is about the test's surroundings, not the app or the test logic — proxy down, env var missing, wrong base URL, VM/browser session died. | `Browser State` → `chrome-error://` means a dead session; proxy status; `.helpmetest/config.yaml` values. |
| `test_isolation` | Test alternates PASS/FAIL across runs with no code change — shared state, ordering dependency, leftover data from a prior run. | Compare two recent runs of the same test; look for state the test assumes is clean but isn't reset. |
| `unknown` | Evidence collected so far doesn't clearly fit any category above. | Say exactly what evidence is missing and what the next check would be — do not force a fit into a category that's a stretch. |

Always report: the category, a one-line reason grounded in evidence from a First Check, and the next action. If the evidence is genuinely ambiguous between two rows (e.g. a deploy just happened AND only one test failed), state both candidates and which First Check would disambiguate — don't silently pick one.
