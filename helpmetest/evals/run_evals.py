#!/usr/bin/env python3
"""
Shared eval runner for helpmetest skill modes.

Uses `claude -p` (Claude Code CLI) — no API key management needed.

Each mode has a <mode>.evals.json that carries:
  - "prompt_preamble": distilled rule bullets specific to that mode
  - "evals": list of cases with must_contain / must_not_contain checks

The runner assembles: preamble + shared output constraints + TEST BODY.

Usage:
  python run_evals.py --mode comment
  python run_evals.py --mode comment --id 4
  python run_evals.py --mode comment --verbose
"""

import argparse
import json
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    import yaml
    def load_evals(path: Path) -> dict:
        yaml_path = path.with_suffix(".yaml")
        if yaml_path.exists():
            return yaml.safe_load(yaml_path.read_text())
        return json.loads(path.read_text())
except ImportError:
    def load_evals(path: Path) -> dict:
        return json.loads(path.read_text())

EVALS_DIR = Path(__file__).parent

DEFAULT_OUTPUT_CONSTRAINTS = textwrap.dedent("""
    Rules for your response:
    - Output the COMPLETE rewritten test body — every single line, not just the changed sections.
    - First character of your response must be a space or `#` (the start of the test body).
    - No explanation, no preamble, no markdown fences, no thinking out loud, no trailing notes.
    - Do NOT echo or repeat the original input. Your entire response is the rewritten version only. No before/after comparisons. Start immediately with the first rewritten comment or keyword — no prose intro, no "I'll rewrite..." sentence.
    - Do not omit any section with a comment like "rest is unchanged" — output everything.
""").strip()


def build_prompt(preamble: str, output_constraints: str, input_body: str) -> str:
    return f"{preamble}\n\n{output_constraints}\n\nTEST BODY:\n{input_body}"


def extract_rf_block(raw: str) -> str:
    """Return the last contiguous RF block (comments + keywords) from model output.

    The model sometimes leaks reasoning before the actual rewrite. Taking the
    last block that contains both a comment line and a keyword line skips any
    prose preamble.
    """
    lines = raw.splitlines()

    def is_rf(line: str) -> bool:
        return line == "" or line.startswith("  ") or line.startswith("#")

    blocks, current = [], []
    for line in lines:
        if is_rf(line):
            current.append(line)
        else:
            if current:
                blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    for block in reversed(blocks):
        has_comment = any(l.startswith("#") for l in block)
        has_keyword = any(l.startswith("  ") for l in block)
        if has_comment and has_keyword:
            return "\n".join(block)

    return raw


def run_eval(case: dict, preamble: str, output_constraints: str, strip_rf_preamble: bool, verbose: bool) -> dict:
    prompt = build_prompt(preamble, output_constraints, case["input"])
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        capture_output=True,
        text=True,
    )
    raw = result.stdout.strip()
    output = extract_rf_block(raw) if strip_rf_preamble else raw

    failures = []
    for term in case.get("must_not_contain", []):
        if term in output:
            failures.append(f"  MUST NOT CONTAIN: {repr(term)}")
    for term in case.get("must_contain", []):
        if term not in output:
            failures.append(f"  MUST CONTAIN:     {repr(term)}")

    passed = len(failures) == 0
    return {"id": case["id"], "passed": passed, "failures": failures, "output": output}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, help="Mode name (e.g. comment, improve)")
    parser.add_argument("--id", type=int, action="append", help="Run only this eval ID (repeatable)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    evals_file = EVALS_DIR / f"{args.mode}.evals.json"
    if not evals_file.exists() and not (EVALS_DIR / f"{args.mode}.evals.yaml").exists():
        print(f"No evals file found for mode: {args.mode}")
        sys.exit(1)

    data = load_evals(evals_file)
    preamble = data["prompt_preamble"]
    output_constraints = data.get("output_constraints", DEFAULT_OUTPUT_CONSTRAINTS)
    strip_rf_preamble = data.get("strip_rf_preamble", True)
    cases = data["evals"]

    if args.id is not None:
        cases = [c for c in cases if c["id"] in args.id]
        if not cases:
            print(f"No evals with id in {args.id}")
            sys.exit(1)

    results = []
    for case in cases:
        rules = ", ".join(case["rules"]) if case["rules"] else "clean"
        label = f"[{case['id']}] {rules:<20}  {case['violation'][:55]}"
        print(f"  {label}", end="  ", flush=True)
        result = run_eval(case, preamble, output_constraints, strip_rf_preamble, args.verbose)
        print("PASS" if result["passed"] else "FAIL")
        if not result["passed"]:
            for f in result["failures"]:
                print(f)
        if args.verbose or not result["passed"]:
            print("  --- output ---")
            for line in result["output"].splitlines():
                print("  " + line)
            print()
        results.append(result)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{passed}/{total} passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
