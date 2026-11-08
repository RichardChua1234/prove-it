"""Prove It — command line entry point.

    python -m proveit check --spec .kiro/specs/prove-it --tests tests

Exit codes are part of the contract:
    0  every criterion is proven by a test that ran
    1  at least one criterion is uncovered or its claiming test failed
    2  the check could not be completed (bad spec, unreadable tests, no results)
"""
from __future__ import annotations

import argparse
import os
import sys

from .report import render_json, render_markdown
from .runner import merge_details, run_suite
from .spec_parser import parse_spec
from .trace import compute_verdict, scan_tests

DEFAULT_CMD = f"{sys.executable} -m unittest discover -s tests -v"


def check(spec: str, tests: str, command: str, cwd: str = ".",
          md_out: str = "", json_out: str = "") -> int:
    parse = parse_spec(spec)
    refs, scan_errors = scan_tests(tests)

    # A spec we cannot read is exit 2, not an empty pass.
    if parse.errors and not parse.criteria:
        verdict = compute_verdict([], refs, {}, parse.errors)
        print(render_markdown(verdict, spec, command))
        return 2

    run = run_suite(command, cwd=cwd)
    if run.error:
        errors = list(parse.errors) + list(scan_errors) + [run.error]
        verdict = compute_verdict(parse.criteria, refs, {}, errors)
        print(render_markdown(verdict, spec, command))
        return 2

    verdict = compute_verdict(parse.criteria, refs, merge_details(run),
                              errors=list(parse.errors) + list(scan_errors))

    md = render_markdown(verdict, spec, command)
    js = render_json(verdict, spec, command)
    print(md)

    if md_out:
        with open(md_out, "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"[written] {md_out}")
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            fh.write(js)
        print(f"[written] {json_out}")

    return 0 if verdict.ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="proveit",
        description="Prove that a Kiro spec is backed by tests that actually ran.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="verify a spec against its test suite")
    c.add_argument("--spec", default=".kiro/specs",
                   help="spec directory or requirements file")
    c.add_argument("--tests", default="tests", help="test directory or file")
    c.add_argument("--run", default=DEFAULT_CMD, help="command that runs the suite")
    c.add_argument("--md-out", default="", help="write the markdown report here")
    c.add_argument("--json-out", default="", help="write the JSON report here")
    c.add_argument("--cwd", default=".", help="working directory for the run")

    args = ap.parse_args(argv)
    if args.cmd == "check":
        return check(args.spec, args.tests, args.run, cwd=args.cwd,
                     md_out=args.md_out, json_out=args.json_out)
    return 2


if __name__ == "__main__":
    sys.exit(main())
