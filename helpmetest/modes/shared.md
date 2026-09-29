<!-- llms-description: Rules that apply to every HelpMeTest workflow. Always loaded, never invoked directly. -->

# Shared context — read this before entering any mode

These rules apply to every HelpMeTest workflow. Load this once; every mode assumes it.

## 1. Orient first

Before creating any test, artifact, or running any exploration:

```bash
helpmetest status                                              # workspace-wide; filter the rows yourself
helpmetest artifact list --tags "project:<slug>"               # this project's features, personas, overview
helpmetest artifact list --type Tasks --tags "project:<slug>"  # in-progress work to resume
helpmetest artifact list --type Memory --tags "project:<slug>" # past findings, if any
```

**Always pass `--tags "project:<slug>"`.** A bare `helpmetest artifact list` returns every
project in the workspace — it is one `apiBaseUrl` serving many unrelated products — and a
real run adopted a stranger project's identity that way. Until a slug is resolved from
local files, do not list at all; use scoped `helpmetest artifact get <slug>` (see the
first-contact exception below).

**`helpmetest status` has no project filter, and pretends otherwise.** Passing a tag
argument is accepted, exits 0, and changes nothing. Measured 2026-09-25:
`helpmetest status "#project:thornfield-records"` → exit 0, **143 tests printed**, 238 lines,
including every unrelated project in the workspace. Exactly one of those rows belonged to
the named project.

So `status` output is a **workspace** view, never a project view. Do not report its totals
as this project's health — that is how a run once reported a stranger project's test counts
as its own. To see only your project's tests, filter the rows yourself on the
`#project:<slug>` tag they each carry.

**`helpmetest test list` is not a command, and guessing it is dangerous.** The first
argument to `test` is a test name or tag to **run**, so a mistyped subcommand becomes a run
request: `helpmetest test list "#project:<slug>"` exits 1 with
`✗ No test matches "list" — aborting before running any of: list, #project:<slug>`. It
aborted here only because no test is named `list`. Confirm a subcommand exists with
`helpmetest test --help` before inventing one.

**`helpmetest test view` takes the test's `id`, not its display name — and says nothing
when it misses.** Measured 2026-09-25:

| command | exit | output |
|---|---|---|
| `test view setup-auth` | 0 | 1344 bytes |
| `test view "Todo persists after reload"` — a test that exists, name copied from `status` | 1 | **0 bytes** |
| `test view definitely-not-a-real-test-xyz` | 1 | **0 bytes** |

Exit 1 with an empty stdout and no error line. A wrong identifier and a nonexistent test are
indistinguishable, and neither announces itself — four guesses in a row produced four silent
failures before the cause was clear. **Never read empty output as "this test has no runs".**

Get real ids from the JSON, which carries them; the human-readable table does not:

```bash
helpmetest status --json    # → { company, total, tests[], healthchecks[], timestamp }
                            #   each tests[] row: id, name, status, last_run, duration,
                            #   stability, stability_runs, tags, content, emoji
```

That `content` field is the test source, so a whole suite can be inspected without one
`test view` call — useful for spotting which tests touch a keyword or selector you are about
to change.

**Exception — first-contact pre-flight.** `agency.md` "Before you start" forbids
`artifact list` and `search` until the project slug is resolved from local files,
and that ban wins. Workspaces are multi-tenant: a bare `list` in a fresh project
returns *other* projects' artifacts, and a real run adopted a stranger project's
identity into its `HELPMETEST.md` that way. Before a slug exists, use scoped
`helpmetest artifact get <slug>` lookups only. Once onboarding has resolved the
slug, `list` is fine.

Every `helpmetest` command must run from the project root or a subdirectory of
it. The CLI finds `.helpmetest/config.yaml` by walking up from the current
directory, so a sibling path like `/tmp` has no config: the command exits 1 with
a login prompt and writes nothing. A real run wrote six feature payloads to
`/tmp`, `cd`'d there to upsert them, and lost all six.

Use what you find:
- **ProjectOverview exists** → project discovered, don't re-discover
- **Feature artifacts exist** → scenarios enumerated, generate tests for uncovered ones
- **Tests exist** → check coverage gaps before writing new ones
- **Tests failing** → re-run one before you diagnose it (see below), then fix before creating new ones
- **Tasks artifact in progress** → resume it, don't start fresh

Never assume the project is empty. Never create what already exists.

**A `FAIL` in `status` is a record of the last run, not the state of the test now.** It
carries whatever error was current when it last executed, which may be a platform bug that
has since been fixed — and the row will keep showing that error until something re-runs it.

Measured 2026-09-25. Six tests in one workspace contained a bare `Get Text` and **all six**
were `FAIL`, several with `Invalid keyword Get Text`, while nine tests using
`Browser.Get Text` were 89% passing. That is a clean-looking correlation and a plausible
story: the bare form is unresolvable, use the qualified one. It is wrong. Re-running one of
the six, `diag-page-full`, took 3.5s and **passed** — with the runner resolving the bare
keyword itself:

```
✓  0.057s  Browser.Get Text  id=detail-js-error  *=  scheduled-error thrown
✓  3.514s  diag-page-full
```

Had that re-run been skipped, the conclusion "never use bare `Get Text`" would have been
written into this skill, and every agent reading it would have been rewriting healthy tests
to fix a bug that no longer exists.

So: **one re-run before any diagnosis of a red test.** It costs seconds, and it separates
"broken now" from "was broken once". Only the first is work.

**It recurred the next day — and the re-run conclusion above is incomplete.** 2026-09-26:
the same tests were red with `Invalid keyword Get Text`, and re-running `playground-forms`
passed in 8.1s. I reported it as transient. Then I looked at the run history instead of the
single re-run:

```
$ helpmetest test view playground-forms --errors
500 runs since 2026-09-19 — 1 passed, 499 failed
  ❌ 2026-09-26 11:29:38   Invalid keyword Get Text
     ${summary}=  Multiple keywords with name 'Get Text' found.
                  Give the full name of the keyword you want to use:
```

**The one pass in 500 was my own re-run.** The failures continue every ~10 minutes,
including at 11:29 — after it. And the error body, which the `status` summary line does not
show, names the actual problem: a **keyword collision**, not a missing keyword. More than
one loaded library exports `Get Text`, so the bare form is ambiguous *in that run's library
set* and must be qualified (`Browser.Get Text`).

Why a manual run passes and the scheduled run does not, I have not established — the
libraries loaded differ between them, but I have not measured which or why. What is
measured: 499 scheduled failures, 1 manual pass.

So the rule is **two steps, not one**:

1. **Re-run** — it separates "broken now" from "was broken once", and still catches the
   `diag-page-full` case above.
2. **Read the history** — `helpmetest test view <id> --errors` gives the pass/fail ratio
   and, crucially, the error *body*. A single green run against a 499-failure history is
   not evidence of health; it is one sample.

A green re-run is necessary, not sufficient. I drew the wrong conclusion from one here, and
it would have closed a real, ongoing, every-ten-minutes failure as noise.

**Write `Browser.Get Text` in test content.** Measured 2026-09-26: **14 tests** in this
workspace are failing on the collision right now — `playground data table`,
`playground modals`, `Diagnostics page full`, `Demo button`, `Proxy API Smoke`, both
FakeMail playground tests, and seven more. That is a quarter of every failure in
`helpmetest status`. Qualifying the keyword is the difference between a test that runs and
one that has not passed since 2026-09-19.

**When it collides is not established — qualify anyway.** Measured 2026-09-26, bare
`Get Text` **passes** in a freshly created test (`✓ ${t}=  Browser.Get Text  body` — the
runner resolves it), and passes again in a test that also uses `Create Fake Email`, which
was my guess at the extra library. Both probes refuted. Yet 16 stored tests fail on it
every ten minutes. Whatever differs between them, I have not found it.

What *is* established is that it is **intermittent per test, with the content unchanged**:
`diag-page-full` failed with the collision and then passed on a re-run (2026-09-25, §1
above); `playground-forms` failed 497 times and passed once manually at 11:27 on
2026-09-26 with the same bare keyword it had always had. Same stored content, both
outcomes. It also appears in both call shapes — assignment (`${t}=  Get Text  pre`) and
assertion (`Get Text  id=x  *=  value`) — so it is not about arity.

That is what makes it worth eight characters: a keyword that resolves 1 time in 500 is
worse than one that never resolves, because the occasional green hides it.

So the rule is not "bare always breaks" — it is: **the qualified form is never ambiguous
and costs eight characters**, and it is the one-word change that took `playground-forms`
from 497 consecutive failures to a green scheduled run. Write `Browser.Get Text`.

`modes/desktop.md` documents a `Get Text` from the Desktop library — qualify that one as
its own library, not as `Browser`.

**Also look for a `Memory` artifact** — it carries project-specific knowledge from past sessions (selectors, auth flows, timing quirks), one entry per finding. Look it up **by type, scoped to your project**, not by text search:

```bash
helpmetest artifact list --type Memory --tags "project:<slug>"
```

**Not `helpmetest search Memory`.** That is a full-text search over every artifact's prose, so it matches the *word* "memory" anywhere. Measured 2026-09-25: it returned two `ProjectHealthReport` artifacts and no Memory artifact at all — an agent could easily read the first hit as "the Memory artifact" and act on a stranger's health report. The typed lookup answers precisely (`No artifacts found`, exit 0, when none exists).

Each entry has `category` and `lesson`, optionally `tags`, `linked_artifact_ids` and `added_at` (see `references/cli-contracts.md`). **There is no `confidence` or `last_verified` field** — verified against the live schema 2026-09-25, despite older versions of this line telling you to check them. The artifact records no freshness signal at all, so re-confirm any selector or timing claim against the live app before building on it, however confident the wording sounds.

## 1b. Present before acting — mandatory, every mode, every invocation

After orient, before any tool call, present to the user. This is not optional narration — it is the moment the user decides whether to redirect.

**Exception — the `agency` mode.** Bare `/helpmetest` runs `modes/agency.md`, which has
its own shape for this moment: a statement of what it found, then one lettered intent
question with an escape hatch, capped at three levels. That wins for that mode. The rule
below is for doers invoked directly by a human (`/helpmetest tdd`, `/helpmetest ui`),
where a binary scope choice is the right size of question. A doer spawned by the brain
with a brief presents nothing and asks nothing — see §13.

**Format — three things, in this order:**
1. **What the user will have after this** — one sentence in user-value terms, not agent-action terms
2. **Your recommendation** — what you'd do first and why (scope, priority, order); you are an advisor, not an executor
3. **One binary scope choice** — must actually change what you do; not a go signal

**The choice must be real:**
- ❌ "Should I proceed?" — bureaucracy, user just says yes, nothing changes
- ✅ "Full scope or critical/high first?" — user's answer changes the output

**Frame in user-value terms, not agent-action terms:**

| ❌ Agent-action | ✅ User-value |
|---|---|
| "I'll scan 4 Feature artifacts" | "After this you'll know what's unprotected" |
| "I'll navigate 5 pages at 3 viewports" | "You'll get a ranked list of what to fix" |
| "I'll score tests against 10 rules" | "You'll know which tests are lying to you" |
| "I'll run the affected tests" | "You'll know if your change is safe to push" |

**Self-directing modes** (coverage, validate, ui): present → scope choice → act on their answer.

**Target-requiring modes** (tdd, discover, regression, proxy, api): present orient findings → ask the mode-specific scope question. Never ask "what do you want to do?" — ask a question that only makes sense in this mode.

The user must feel like they directed the work. Not like they watched it happen.

---

## 2. Narrate before and after

Never create a test, artifact, or run silently. Every significant action has three moments:

- **Before:** what you are about to do and why (what scenario it covers, what risk it guards against)
- **After:** what happened — result, what the artifact now contains, why a test failed
- **Next:** what you will do next and what decision point is coming

Silence means the user has no idea what you did or why. That is not acceptable.

## 2a. Never truncate `helpmetest` output — the fix is in the part you cut

Do not pipe any `helpmetest` command through `tail`, `head`, or `grep`. Its
output is already structured (Keywords / Network / Interactive sections), and
its rejections carry the remedy in the body, not the first line:

```
❌ Uneven comment distribution.

Section 3 runs 8 steps in a row with no comment — that's more than every other
step in the test combined (3 steps across the rest of it).
```

The first line only says *that* it failed; the second says exactly what to
change. A real onboarding run piped every `test create` through `| tail -12`,
discarded that explanation, and then retried blind against the same validator
seven times in one session. The same applies to `✗ Tag validation failed`, which
lists the valid categories and the known values, and to
`no Feature artifact found with id "X"`, which prints the full list of real ids.

If output is genuinely long, read it whole and then quote the part you acted on —
truncating at the source destroys the diagnostic before you've seen it.

## 3. Tests verify outcomes, not presence

A test that just checks an element is visible is not a test. Tests must **perform an action and assert the result** — minimum 5 meaningful steps. See `tdd` mode for structure, documentation, and selector rules.

## 3a. Red-team loop — mandatory after every test is written

This runs after every test create/update call, before moving to the next test. It is not a review — it is adversarial interrogation of the test you just wrote.

Ask these four questions. Write the answers in plain text. Do not summarize or skip.

> **Q1. What user complaint slips through?**
> If this test passes but the feature is actually broken, what would a real user report? Name the exact complaint. If you can't name one, the test is protecting nothing — rewrite it.

> **Q2. What can a developer delete without this test failing?**
> Imagine removing the key behavior — the state change, the validation, the persistence. Does the test still pass? If yes, the assertion is wrong. Fix it.

> **Q3. Is a state change asserted, or just element presence?**
> If the test's final assertion is "element is visible" or "page contains text," rewrite it to assert what actually changed (value, count, URL, stored data).

> **Q4. What boundary or edge is untested?**
> Empty state, off-by-one, concurrent action, missing precondition. Name the one most likely to silently break in production. If the risk is real, add it to this test or open a follow-up scenario.

**If any answer reveals a gap** → patch the test, then re-run all four questions on the patched version. Repeat until the adversary runs dry — all four answers are "nothing slips through." Only then move to the next test.

## 3b. A green keyword is not proof the action happened

`✓` means the keyword executed without raising. It does **not** mean the app changed. The
only proof an action landed is a separate assertion on the app's state.

Measured on `todo.playground.helpmetest.com`, 2026-09-25, three probes:

| sequence | items added |
|---|---|
| `Fill Text  input.new-todo  X` → `Keyboard Key  press  Enter` | **0** — both keywords green |
| `Fill Text  input.new-todo  X` → `Press Keys  input.new-todo  Enter` | **1** |
| `Click  input.new-todo` → `Fill Text` → `Keyboard Key  press  Enter` | **1** |

Cause: `Fill Text` does not leave the element focused, and `Keyboard Key` is page-level
rather than element-targeted, so the key reaches nothing. Two ticks, no item, no error.

Two rules follow:

1. **Commit a form field with the element-targeted `Press Keys  <selector>  Enter`**, not
   `Keyboard Key  press  Enter`. Reserve `Keyboard Key` for genuinely page-level keys
   (Escape, Tab) where focus itself is what you are testing.
2. **Assert the effect, in the same chain.** After any mutating keyword, read the state
   back — `Get Element Count`, `Get Text`, `Get Property` — and compare it to a **literal**.
   Comparing a before-value to an after-value passes on `0 == 0`; a test built that way
   reports green forever while the feature it names has never once worked.

## 3c. A test that has never been seen to fail is not yet a test

In TDD the red phase proves this for you: the test fails, you make it pass, and you have
watched it do both. **Testing an app that already works has no red phase.** You write the
test, it goes green on the first run, and nothing has demonstrated that it *can* go red.
A test asserting nothing at all also goes green on the first run.

So before you report a new test as protection, run a **negative control**: change one
expected value to something you know is wrong, run it, confirm it fails with a message that
names the real difference, then change it back and confirm green again. Two extra runs,
a few seconds each.

A live run did exactly this unprompted and told its non-technical user, in one sentence:

> *"I also deliberately fed it a wrong answer to make sure the check isn't just
> rubber-stamping everything — it correctly failed and told me exactly what didn't match.
> So when it says 'pass', that means something."*

That is the whole point in the user's own words: **a green result is only worth something
once you have seen the red.** Report the negative control alongside the pass — "passed 3/3,
and failed correctly when I fed it a wrong value" is evidence; "passed" alone is a claim.

**The same control applies to deleting an assertion.** "This step already covers it" is a
claim about a system, not a fact about it — run the surviving step against an input the
deleted one would have caught. Measured 2026-09-26: a test checked an attachment's PDF
magic bytes and then called `Open Document` on it. Removing the magic-byte check looks
safe, because surely converting the file proves it is a PDF:

```
Open Document  …/dummy.pdf           ✓  exit 0
Open Document  https://example.com/  ✓  exit 0
```

An HTML page converts exactly as happily. The "redundant" assertion was the only thing
checking the type, and dropping it would have left a test that is still green and covers
strictly less. A weakened test never announces itself; a red one does.

## 3d. The `Javascript` keyword evaluates an EXPRESSION — statements return nothing

It reports `✓` either way. A block-bodied arrow function, or anything containing `;`,
returns an empty result with no error — the same silent-success shape as §3b.

Measured 2026-09-25 on `playground.helpmetest.com`, a page with 29 `a[href]`:

| expression | result |
|---|---|
| `…map(a=>({text:a.textContent,href:a.href}))` — expression body | real JSON |
| `…reduce((m,a)=>{m[new URL(a.href).host]=1;return m;},{})` — block body, `;` | **empty** |
| `…[...new Set(…map(a=>new URL(a.href).host))]` — expression body | real JSON |

So write expressions, not statements: use spread/`Set`/`map`/`filter` and arrow bodies
without braces. If you need a block, wrap it in an IIFE that *returns* — and check the
output is non-empty before you believe it.

**An empty result is never self-evidently "the page has none of those".** Count the raw
thing first (`String(document.querySelectorAll('a[href]').length)`) and only then filter.

## 3e. How to find out whether a keyword exists — and why you cannot list them

Six keywords this skill used to teach did not exist at all (`Analyze Web Vitals`,
`Analyze Resources`, `Broken Links`, `Generate Sitemap`, `Markdown`,
`Probe Navigation Elements`), and one — `Evaluate` — is refused by the platform and fails
the whole run. So check before you build a recipe on a keyword you have not personally seen
work.

**The check:** call it with no arguments and read the error.

| response | meaning |
|---|---|
| `No keyword with name 'X' found.` | it does not exist — stop |
| `expected 1 argument` / `expected 1 to 4 arguments` | it exists; now get the signature right |
| `✓` | it exists **and you just ran it** — see the warning below |

**⚠ A no-argument probe of a zero-argument keyword executes it.** Probing
`Create Fake Email` this way returned `✓` — it allocated a real inbox. Never no-arg-probe
anything that could send, delete, pay, or create.

**Safer default: probe with too MANY arguments.** Six junk args cannot match any real
signature, so the keyword never runs, and the error still tells you everything. Measured
2026-09-26:

```
Get Email Attachment  a b c d e f  → ValueError: Argument 'timeout' got value 'f'
                                     (exists, and the 6th parameter is `timeout`)
Open Document         a b c d e f  → Doc2HTML.Open Document expected 1 to 2 arguments, got 6
Save Attachment       a b c d e f  → No keyword with name 'Save Attachment' found.
```

**Read the whole result, not a fixed line.** The verdict is not always the second line:
`interactive` output continues into a page dump, a `Browser State` block and a replay URL.
Extracting with `sed -n '2p'` across a batch of probes reported `Save User` as returning a
URL and `Forget As` as "Restored state …" — both nonsense, produced by slicing a line
number out of differently-shaped outputs. Re-read in full, each keyword's real error was
`expected 1 argument, got 7`. A probe you misread is worse than one you did not run.

Note the first form leaks the parameter *name*, which the arity message does not. Chain
them one per call, though: the first failure marks the rest `○ (skipped)` and you learn
nothing about those.

**`helpmetest search` is also a subset — it is not a keyword list.** Measured 2026-09-26:
searching `attachment` returned **zero** keywords while `Get Email Attachment` exists and
works. I wrote "the keyword does not exist" on the strength of that search and was wrong.
Search is for discovery; only the live error decides existence.

**There is no authoritative list you can read instead.** `~/.helpmetest/keyword-cache.json`
holds only what the current session loaded — 714 entries — and keywords from other libraries
are simply absent from it. Measured 2026-09-25: `Get Email Link`, `Mobile Tap` and
`Open Document` are all missing from that cache and all three exist
(`expected 1 to 4 arguments`, `expected 1 argument`, `expected 1 to 2 arguments`).
Treating that file as the full keyword list would condemn every mobile, desktop, doc2html
and fakemail recipe in this skill as fictional. **Absence from the cache proves nothing;
only the live error message does.**

## 3f. Test content is BARE keywords — never `*** Settings ***` / `*** Test Cases ***`

`helpmetest test create --content` takes the keyword body only. The CLI wraps it into a
real Robot Framework test case itself, and the libraries are already loaded — you do not
declare them.

```robotframework
# Download public PDF via URL and verify content
Open Document  https://arxiv.org/pdf/gr-qc/9905021
Find  Bel
```

Not this:

```text
*** Settings ***
Library    Doc2HTML

*** Test Cases ***
Invoice PDF contains correct total
    Open Document    invoices/invoice.pdf
```

**Measured 2026-09-25:** of the 143 tests in a live workspace, **zero** contain a
`*** Settings ***` or `*** Test Cases ***` section. Every passing test is bare keywords
with `#` comment headings and no indentation.

Several mode files still show the section-header form in their examples
(`api.md`, `auth.md`, `desktop.md`, `fakemail.md`, `mobile.md`). **Those examples are
illustrating the keywords, not the submission format** — read the keyword sequence from
them and submit it bare. `interactive.md` has always said so: *"`--content` is bare RF
keywords, not a full `*** Test Cases ***` block — `test create` wraps it into a real test
case itself."* Where a mode example and this rule disagree, this rule wins.

Two things those examples *do* get right and are easy to lose when flattening them:
`Suite Setup`/`Suite Teardown` lines have no bare equivalent — put the setup keyword at the
top of the body and the teardown at the bottom — and `As  <StateName>` stays exactly as
written.

## 3g. A rejection proves that invocation failed — not that the capability is missing

The mirror of §3b. A `✓` does not prove the action landed; a `✗` does not prove the thing
cannot be done. Before you write "X is not supported", "there is no partial update", or
"that keyword does not exist", read `--help` for the exact command and check whether your
invocation met its conditions.

This is not hypothetical. A session probed the documented blocked-doer report,
`artifact upsert --id … --content '{"tasks.N.status": "blocked"}'`, got
`422: 4 validation errors … name Field required`, and rewrote this file around the
conclusion that partial updates do not exist. They do. The probe had added `--name` and
`--type`, and `artifact upsert --help` says plainly that content-only patches while
"all fields" *replaces*. Re-run without them: `content updated (partial)`, siblings intact.

The correct doc was replaced with a wrong one, and every step of that was "evidence-based".
So: when a failure would mean a documented feature is a lie, that is the moment to suspect
your own call, not the feature. State the invocation you ran, not a conclusion about the
system.

## 3h. `#` starts a Robot Framework comment — escape it in selectors

`Click  #submit` never runs. Measured 2026-09-26:

```
Robot Framework syntax error: # starts a comment and must be escaped.
Found unquoted: #definitely-not-here
Should be: \#definitely-not-here
```

Two things that make this expensive if you do not know it:

- The error is attributed to the **first** keyword in the chain, not the one containing
  the `#`. A four-keyword chain reports `✗ Go To …` with this message. Do not start
  debugging the navigation.
- **Escape with a backslash, never quotes.** The CLI says why: Browser library reads a
  quoted value as a literal `text=` locator, so `Click  '#submit'` parses fine and then
  times out hunting for the literal text `#submit`. Green parse, ten-second failure,
  wrong diagnosis.

Nothing in the chain executes, so unlike a mid-chain failure this one leaves no state
behind.

## 3i. The bar for writing "X is broken" into a doc, a report, or an artifact

§1 says re-run once before diagnosing a red test. That is enough to avoid chasing a ghost
for five minutes. It is **not** enough to justify changing a document, escalating to the
user, or recording a defect — and on 2026-09-26 that gap produced two wrong conclusions in
one session, both with a passing control run attached.

Before you write a defect down anywhere, one of these must hold:

1. **Three consecutive failures**, or
2. **A run history** showing it: `helpmetest test view <id> --errors` gives the pass/fail
   ratio and the error body, or
3. **Separated-in-time evidence** — two failures at least several minutes apart, with
   something else known-good succeeding in between.

Why (3) matters more than it sounds: the `api.md` mistake had a textbook controlled
comparison — relative path failed, absolute path passed, same session, seconds apart.
Both arms ran inside the same bad window. **A control run seconds apart controls for the
wrong variable when the variable is time.**

The two that failed this bar, both mine, both with real output behind them:

| claim | evidence I had | what was true |
|---|---|---|
| "`Invalid keyword Get Text` is transient" | one green re-run | 499/500 failing — my re-run was the 1 pass |
| "relative API paths are broken" | two failures + a passing absolute control | 3/3 green minutes later |

Note they failed in **opposite** directions: one green sample declared health, two red
samples declared a defect. The asymmetry is the point — a single sample is evidence of
nothing in either direction, and feeling confident is not a fourth option.

## 3j. A test must exercise the behaviour in its own name — and a red test is never fixed by removing the assertion

Measured in a real run on 2026-09-26. A test was created as **"User can clear all completed
todos"**. It failed. The agent probed interactively, could not reconcile the result, wrote
`[bug]`, then narrated: *"Let me simplify test 4 to work around this."* The stored test that
ended up green is:

```
Check Checkbox  li:has-text("Buy groceries") input.toggle
Get Element Count  .completed  ==  1
Browser.Get Text  body  contains  Clear completed
```

It never clicks Clear completed. It asserts the **button's label is present on the page**.
Its name still claims the user can clear completed todos, the Feature artifact links it as
coverage for that scenario, and the final report listed it under *"What you can now
trust works"*. The same report ended **"Bugs found: None"** — retracting, with no new
evidence, the bug the same run had written down two steps earlier.

That is worse than a red test. A red test tells you something is wrong; this one tells you
something is *right* that was never checked, and it does it under a name chosen to be
trusted.

**The rules, in order of how often they are broken:**

1. **If a test's name says the user can do X, the test performs X and asserts the
   consequence.** Asserting that the control for X exists is coverage of the label, not
   the behaviour. If you end up asserting presence, rename the test to what it actually
   checks — then notice that X is still uncovered.
2. **Never weaken an assertion to turn a test green.** Changing a selector, adding a wait,
   fixing a typo: legitimate. Deleting the step that failed: not a fix, it is the failure
   being hidden. (§3c says this about assertions generally; this is the case that actually
   happens.)
3. **A bug you wrote down may only be retracted by evidence that it is not real** — a
   passing run of the original, unweakened test. "It worked when I tried it by hand" is
   §3i's single sample. If you cannot clear it, it stays in `bugs[]` and it stays in the
   report; the honest line is *"still failing, cause not established"*, never "None".
4. **A final report that lists a weakened test under "what you can now trust" is the
   defect.** Before writing that section, re-read each test you are about to vouch for and
   check its assertions still match its name. This is the last place the mistake is cheap.

## 3k. Robot Framework variable names ignore case and underscores — you can shadow a built-in without knowing

`${empty}`, `${Empty}`, `${EMPTY}` and `${e_m_p_t_y}` are the **same variable**. RF matches
names case-insensitively and ignores underscores, so a scratch variable named after
anything in the built-in namespace silently replaces it for the rest of the test.

Measured 2026-09-29: a test stored a CSS display value in `${empty}` — a reasonable name
for "the empty-state block" — which overwrote the built-in `${EMPTY}`. A later assertion
comparing against `${EMPTY}` then compared against `"block"`. The failure read:

```
none != block
```

Nothing in that message says a built-in was shadowed, and the test looks correct on the
page. Expect to lose a debugging cycle to it once.

So: **never name a variable `empty`, `true`, `false`, `null`, `none`, `space`, or `newline`
in any casing or with any underscores.** Prefix scratch variables with what they hold —
`${empty_state_display}`, not `${empty}`. If an assertion fails against a value you never
set, grep your own test for a variable whose name collides with the built-in before
suspecting the app.

## 4. Auth state before anything

Establish auth state with `Save As <StateName>` **once**. All subsequent tests reuse it with `As <StateName>` — never re-authenticate inside tests. See `tdd` mode for full auth pattern.

## 5. Feature artifacts are mandatory

Every feature gets a `Feature` artifact before tests are written. Tests link back via `scenario.test_ids`.

**A failed upsert is not permission to skip it.** Measured in a real run 2026-09-26: two
`Feature` upserts were rejected, and the agent announced *"Skipping the intermediate Feature
artifact — I'll write tests directly with the `feature:todo-happy-path` tag and link them
back."* It then tagged the tests with a **different** feature id, and no Feature artifact
exists for that project at all — verified after the run: `artifact get
feature-todo-happy-path` → 404, and `artifact list --tags project:todo-app` returns only the
ProjectOverview. The tests point at a feature that was never created, so `bugs[]` had nowhere
to go and the "link them back" never happened.

A 400/422 means *this payload* was wrong — §3g. Read the error, fix the field, upsert again.
The write rules that actually cause these are in §9: the name must not contain its own type,
`content.name` is required separately from `--name`, and unknown fields are rejected
outright. If you genuinely cannot make it land, that is a blocker to state plainly, not a
step to quietly drop — the Feature artifact is what makes the tests mean anything later.

## 6. Bugs go in artifacts, not chat

Find a bug → immediately add it to the relevant Feature artifact's `bugs` array. A bug mentioned only in a message does not exist — it will be forgotten.

## 7. Who you are

If `.helpmetest/SOUL.md` exists in this project, read it — it defines your character and shapes how you work.

## 8. Tool surface

When you're inside the `helpmetest agent` harness, your tools are restricted. You have:

- `Bash` — for `helpmetest` CLI commands
- `Read`, `Write`, `Edit` — files

Use the `helpmetest` CLI for all HelpMeTest operations. Key commands:
- `helpmetest login` — authenticate via browser; saves token to `.helpmetest/config.yaml`
- `helpmetest login --token <token>` — skip browser; validate and save a known token directly (useful when you already have a token from the dashboard or CI secret)
- `helpmetest status` — test state
- `helpmetest interactive "<Robot Framework keyword>"` — browser automation
- `helpmetest test run <name-or-tag-or-id>` — run tests
- `helpmetest artifact list` / `helpmetest search <query>` — find artifacts
- `helpmetest artifact get <id>` — fetch artifact content
- `helpmetest artifact schema <type>` — get artifact schema
- `helpmetest artifact upsert --id <id> --type <type> --name <name> --content '<json>'` — create/update artifact
- `helpmetest test create --name <name> --tags <tags> --content '<robot>'` — create test
- `helpmetest test update <id> ...` — update test
- `helpmetest proxy start` — start proxy tunnel (see `proxy` skill for syntax and domain setup)
- `helpmetest files upload <file>` — upload file
- `helpmetest open test <id>` — open test in browser

**Every create/update prints its dashboard URL — relay it, don't re-derive it.**
`artifact upsert` prints `Open in dashboard (<base>/artifacts/<id>)` and `test
create`/`update` prints `Open in dashboard (<base>/test/<id>)`, on success only. That line
is where your `[link]` line comes from (`agent.md`), and it is the only creation signal
that exists for every integration — MCP tools, CLI, or a person in a terminal.

Both commands also take **`--open`** (open that page in a browser now) and **`--no-open`**
(never, overriding config). Neither opens anything by default. The default comes from the
`autoOpenCreated` key in `.helpmetest/config.yaml`
(`helpmetest config set autoOpenCreated true` — it sits beside the existing
`autoOpenSession`, which is about interactive sessions, not creations), and it
ships **false** because this same binary runs inside `helpmetest agent`, CI and scheduled
runs — a measured run created 4 tests and updated them 9 times, which is 13 browser tabs.
**Do not pass `--open` in an agent run unless the user asked for it**; print the URL
instead, which is what they can act on either way.

## 9. Every mode has an output artifact

Modes are not just prose workflows — they produce structured, typed artifacts in HelpMeTest. The artifact is the mode's deliverable. Vague summaries are not acceptable; the artifact is queryable and machine-readable.

| Mode | Output artifact type(s) |
|---|---|
| `tdd` | Tests (via `helpmetest test create` / `helpmetest test update`) + updates to the matching scenario's `test_ids` under `Feature.functional[]` / `edge_cases[]` / `non_functional[]` (there is no `Feature.scenarios[]`) |
| `dev` | `Tasks` (orchestration receipt) + all artifacts produced by sub-modes it runs |
| `fix` | `SelfHealing` + updates to `Feature.bugs[]` if a bug is found |
| `discover` | `Feature[]` + `Persona[]` + `ProjectOverview` + (optional) `Memory` |
| `coverage` | `CoverageReport` |
| `regression` | `RegressionRun` — **the type exists**; `helpmetest artifact schema RegressionRun` returns a schema (verified 2026-09-25) |
| `validate` | `TestValidation` — **the type exists** (verified 2026-09-25). Note `modes/validate.md` currently emits a `Tasks` artifact instead; required fields are `name`, `description`, `scope`, `tests_reviewed`. **`ValidationReport` is not a type** — its schema fetch 500s |
| `api` | Tests (API-style) |
| `ui` | `UIReview` |
| `agency` / `autonomous` | `ProjectOverview` + `Feature[]` + `Persona[]` + initial `Tasks` |
| `proxy` | (no artifact — setup command) |

The enclosing `Tasks` artifact (from modes/agent.md lifecycle) is the **lifecycle receipt** — it tracks what you did. The mode-specific artifact is the **substantive output** — what was found, what was reviewed, what was produced. Both get saved per run.

### Linking artifacts together

Every artifact inherits `links: List[str]` at its content root. Populate this on every artifact you create. List every parent/source/sibling artifact id that matters: the enclosing Tasks artifact, each Feature artifact you scanned, the ProjectOverview you derived from, etc.

**Write both sides.** `links[]` is undirected in intent but *not* auto-resolved by the
server. This rule previously said the opposite — "write only one side, the server
resolves edges in both directions automatically" — which directly contradicted the live
`helpmetest artifact schema Tasks` output ("Undirected — if A points at B, B should also
point at A. Agents must populate both sides.").

Settled empirically on 2026-09-25 rather than by picking the nicer-sounding source.
Controlled test: created a fresh `Tasks` artifact whose `links` contained exactly one
entry, `quill-notes`, and wrote nothing into `quill-notes` itself.

```
quill-notes.links BEFORE: ['tasks-quill-notes', 'feature-capture-note-quill-notes']
quill-notes.links AFTER : ['tasks-quill-notes', 'feature-capture-note-quill-notes']
reciprocal auto-created : False
```

So a one-sided link is simply a missing edge from the other artifact's point of view.
Patch both, or accept that navigation only works in one direction.

The one exception: if a long-lived artifact (Feature, ProjectOverview) genuinely points FORWARD to something new you created — e.g. you added a scenario to a Feature and want that feature to list the new test — update that artifact's own content (the scenario's `test_ids` under `functional[]`/`edge_cases[]`/`non_functional[]`, for example), not its `links[]`. `links[]` is for cross-artifact navigation, not for relational data inside the artifact.

### Always fetch the schema first

Before creating any artifact:

```bash
helpmetest artifact schema <TypeName>
```

Required fields and validation rules can change — don't memorize them. The schema is authoritative.

**Two rejection rules the schema does not show you**, both measured 2026-09-25 and both
hit by templates in this skill:

1. **The artifact name must not contain its own type.** `--name "Persona: Shopkeeper"` is
   refused with `400: Artifact name should not contain the artifact type 'Persona'. Use a
   descriptive name instead`. Confirmed for `Persona`, `Tasks`, `Memory` and `Feature` —
   it applies to every type. The match is **case-insensitive and on whole words**:
   `zz feature work list` is refused, `zz featured records` is accepted. So a placeholder
   like `"[feature-name] — build"` fails too, before anyone substitutes anything into it.
   Name it after the thing, not the container: `Shopkeeper — counter staff`.
2. **`content.name` is required, and the top-level `--name` does not satisfy it.** Omitting
   it gives `422: Invalid content for <Type>: 1 validation error … name Field required`.
   Both are needed, and they may differ.
3. **A `project:<slug>` tag, when present, must name a ProjectOverview that already
   exists** — for every type: `400: Tag validation failed … no ProjectOverview artifact
   found for project "<slug>"`. Separately, **`Feature` and `Persona` require the tag at
   all** (`Missing required tag: project:X`); measured 2026-09-25, `Tasks`, `Memory` and
   `UIReview` do not. So create the ProjectOverview first — but note the failure mode for
   the ungated types is worse than an error: an untagged `Tasks` **saves successfully** and
   then belongs to no project, so `artifact list --tags "project:<slug>"` never returns it
   and the next session cannot find the plan. Tag every artifact you write.
4. **Unknown fields are fatal, not ignored.** Content models forbid extras:
   `422: … Extra inputs are not permitted [type=extra_forbidden]`. Inventing a field costs
   the same as omitting a required one — park stray observations in `notes` or `gotchas`.

The checks run in that order — name first, then content — so a 400 about the name means the
content was never validated. Fix the name and re-submit before concluding anything about
your payload.

## 10. Listen for events in the background

Reactive tasks — monitor, watch, a long `agency`/`autonomous` engagement, "keep the suite green" — must stay aware of incoming events (new user messages, test status changes, new failures) without blocking on them. Do this by launching the CLI once at the start of your work:

```
helpmetest updates --json
```

Same shorthand filters as `test run` work here — `--keywords`, `--errors`, `--results`, `--screenshots`, `--network-requests` — each expands to `--filter <type> --json`. Useful to cut noise on a long-lived background listener, e.g. `helpmetest updates --errors` to only wake up on error events.

`shared.md`

Poll the background task's output between your own actions:
- **Test status change (PASS→FAIL)**: something just regressed. Stop the current task if it's lower-priority, or finish the current step and then investigate.
- **User message**: respond immediately (write to stdout or reply in the chat you're in). Silence after a message is worse than a wrong answer.
- **Quiet stream**: keep working.

**Don't start the background listener for a discrete one-shot task** (write this test, produce this report). It's only worthwhile when the job is long-running or inherently reactive.

**Harness note:** inside `helpmetest agent "<task>"` reactive monitoring is only useful for long-running or reactive tasks — for a discrete one-shot task, just do the task and exit.

## 11. Agent-pattern discipline is always on

`shared.md`

If you're inside the harness (`helpmetest agent "<task>"`), the harness pre-picks the Tasks id and injects it at the top of your first user message; use it verbatim.

If you're invoked via slash command (`/helpmetest …`) outside the harness, you don't have a pre-picked id — pick one yourself (`tasks-<short-uuid>` derived from current time + task hash) and create the artifact the same way.

Either way: maintain the Tasks artifact, track subtasks, close with evidence, populate `content.links` with every related artifact.


## 12. Use interactive as your eyes — always

You have a real browser available at any time via `helpmetest interactive`. Use it. Don't guess what an app looks like, what selectors exist, or whether a flow works — go look.

This applies to all work, not just QA: writing a feature, debugging a bug, reviewing a UI, writing a test. If the app is running, open it.

**For a local dev server**, the cloud browser can't reach `localhost` directly — set up a proxy tunnel first. Read the `proxy` skill for exact syntax and domain setup, then come back and use the domain it gives you in `interactive` commands.

**When to reach for it:**
- Starting work on any feature → navigate to the relevant page first, see what's actually there
- Selector in a test is wrong → go find the real one in the Interactive section
- "Does this work?" → go check, don't speculate
- Writing a test → prototype the flow interactively first, then copy into `helpmetest test create`
- Something looks broken → open it, look at Network for 4xx/5xx, look at the page state

The Interactive section of every response lists ready-to-paste RF commands for every element on the page. Use those — don't invent selectors.

---

## 13. The brief — how the brain hands work to a doer

Bare `/helpmetest` runs `modes/agency.md`, the brain. Every other mode in this skill is a
**doer**. The brain talks to the human; doers do not.

### If you are a doer, you were given a brief

**Proceed on it. Never ask the human anything.** You were not spawned into a conversation
— there is no human reading your output in real time, so a question from you is not a
question, it is a hang.

A brief has exactly these fields:

| Field | What it is |
|---|---|
| `goal` | One sentence. What is true when this is finished. |
| `surface` | web / api / mobile / desktop / email / documents / domain / localhost / ci / monitoring |
| `target` | The URL, endpoint, package path, or domain you are working against. |
| `tasks` | The `Tasks` artifact id plus the task numbers you own — e.g. `tasks-acme`, tasks `3.1`–`3.4`. |
| `artifacts` | Related artifact ids you should read first (ProjectOverview, Features, Personas). |
| `constraints` | Anything you must not assume, plus known quirks (auth state name, selectors, timing). |
| `done` | Observable definition of done. A command and its expected result, not a feeling. |
| `do_not_touch` | Files, tests, or task numbers owned by someone else. |

### If you are blocked, report to the brain — never to the user

Genuinely blocked means: a credential you cannot find, a target that does not respond, a
contradiction between the brief and what you observe, or a destructive action you are not
authorised to take. Retrying differently is not blocked.

When blocked, write the blocker into your own task in the `Tasks` artifact and return:

```bash
helpmetest artifact upsert --id tasks-<slug> \
  --content '{"tasks.N.status": "blocked", "tasks.N.notes": "<what you tried, what happened, what you need>"}'
```

**That is a patch, and it only patches because `--name` and `--type` are absent.** Per
`artifact upsert --help`: content-only means "patches just those fields. Keys may be
top-level or dot-notation"; supplying `--name`/`--type` as well means "creates or
**replaces** the entire artifact". Add them out of habit and the same dotted keys become
extra fields on a full document:

```
✗ 422: Invalid content for Tasks: 4 validation errors
  name         Field required
  description  Field required
```

Both measured 2026-09-26. The patch above returned `content updated (partial)`, and a
re-fetch showed `status: "blocked"` plus the new `notes`, with `title`, `description` and
every sibling field intact. `"tasks.-1": {...}` appends: verified by patching a one-task
artifact and re-fetching it — `1.0 first pending | 2.0 second pending`.

Then hand it back to the brain. **The human talks to one entity only** — that is the
entire point of this arrangement, and a doer that addresses the user directly breaks it.

Two ways to hand back, and the cheap one is usually right:

- **Ask the brain and wait**, over whatever messaging the harness gives you, when a
  one-line ruling unblocks you. A real run hit exactly this: `test create` hard-requires
  a `feature:<id>` tag naming an **existing** Feature artifact, and creating one was
  forbidden by its brief's `do_not_touch`. It proposed a tenancy-safe id and asked. One
  round trip, brief amended, work continued. Respawning would have cost far more.
- **Write `blocked` and return** when the answer is not a one-liner, when the brain is
  gone, or when the blocker needs to survive this session — a missing credential, a dead
  target, a destructive action nobody authorised.

Either way the blocker is *recorded*, not just spoken: if you asked and got unblocked,
say so in `tasks.N.notes` too. A ruling that exists only in a chat message is lost the
moment the process exits.

### If you are the brain, these are your obligations

**Write the `Tasks` artifact before spawning anything.** It is both the roadmap and the
handoff medium. A doer spawned before the artifact exists has nothing to read, nothing to
update, and no way to report a blocker. Fetch `helpmetest artifact schema Tasks` first
(per §9 and `agency.md` rule 2), then upsert, then spawn.

**Own the shared boundary.** Independent surfaces run in parallel — a web doer and an API
doer have no reason to wait for each other. But two doers must never hold the same task
range in the same `Tasks` artifact, or write tests with the same names. You assign those
ranges; nobody negotiates them at runtime.

**Refuse to advance a stage while tests are red.** This is the only enforcement in the
system — there is deliberately no git hook. Before moving from tests-written to
implementation, and again from implementation to done, run the tests yourself and read
the result. A doer's claim that something passes is not a result; a test run with output
is. Red means the stage does not advance, and you say so plainly.