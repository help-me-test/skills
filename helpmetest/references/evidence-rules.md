# Evidence Rules

Applies to every mode that diagnoses a failure, summarizes findings, or reports project health (`fix`, `report`, `tdd` bug documentation, `coverage`, `validate`). Referenced, not restated — if a mode file needs this discipline, it links here instead of re-explaining it in its own words.

- **Quote or summarize concrete evidence.** A classification, root cause, or health verdict must point at something you actually read: a run's Keywords/Network/Interactive section, a specific line in a Feature artifact, a `git diff` hunk, a CLI command's actual output.
- **Say what's missing when it limits confidence.** If you didn't get a screenshot, didn't see the network log, or a command failed, say so explicitly rather than filling the gap with a plausible-sounding guess.
- **Never invent evidence.** Don't describe a screenshot, log line, selector, run URL, or Memory entry that wasn't actually returned by a tool call in this session. If you need it and don't have it, go get it — don't narrate as if you already did.
- **Category is a hypothesis, not a verdict.** A classification (e.g. from `references/failure-categories.md`) is your best read of the evidence collected so far — say so, and be ready to revise it if a later check contradicts it. Don't present a hypothesis with the confidence of a confirmed fact.
- **If the CLI/API call fails or a tool is unavailable, say exactly what evidence you don't have** instead of silently proceeding as if you'd checked. "Couldn't reach `helpmetest status` — proceeding without current test state" is honest; silently assuming a clean slate is not.
