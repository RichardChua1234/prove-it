"""Run the test suite and capture what actually happened.

The only module allowed to execute a subprocess — kept deliberately small so the
verdict path above it stays auditable. It never invents a result: if the command
cannot run, that is returned as an error and the caller exits non-zero.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field

# unittest -v lines look like:
#   test_name (tests.test_x.ClassName.test_name) ... ok
#   test_name (tests.test_x.ClassName) ... FAIL
UNITTEST_LINE = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+\((?P<where>[^)]*)\)"
    r"(?:\s*\.\.\.)?\s*(?P<status>ok|FAIL|ERROR|skipped[^\n]*)$"
)

STATUS_MAP = {"ok": "passed", "FAIL": "failed", "ERROR": "errored"}


@dataclass
class RunResult:
    statuses: dict = field(default_factory=dict)    # test name -> status
    details: dict = field(default_factory=dict)     # test name -> first failure line
    output: str = ""
    error: str = ""                                 # set when the run itself failed
    returncode: int = 0

    @property
    def ok(self) -> bool:
        return not self.error


def parse_unittest_output(text: str):
    """Extract per-test statuses from unittest -v output."""
    statuses, details = {}, {}
    for line in text.splitlines():
        m = UNITTEST_LINE.match(line.strip())
        if not m:
            continue
        name = m.group("name")
        raw = m.group("status")
        status = STATUS_MAP.get(raw, "skipped" if raw.startswith("skipped") else raw)
        statuses[name] = status
    return statuses, details


def run_suite(command: str, cwd: str = ".", timeout: int = 900) -> RunResult:
    """Execute the test command and capture its real output.

    A command that cannot start, times out, or exits with no parseable results
    yields an error rather than an optimistic empty pass.
    """
    try:
        proc = subprocess.run(
            command, shell=True, cwd=cwd, capture_output=True, text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return RunResult(error=f"test command timed out after {timeout}s")
    except OSError as exc:
        return RunResult(error=f"could not run test command: {exc}")

    output = (proc.stdout or "") + (proc.stderr or "")
    if not output.strip():
        return RunResult(error="test command produced no output",
                         returncode=proc.returncode)

    statuses, details = parse_unittest_output(output)
    if not statuses:
        return RunResult(
            error="could not parse any test results from the command output",
            output=output, returncode=proc.returncode,
        )

    # failure detail: the assertion line immediately after a FAIL/ERROR block
    blocks = re.split(r"={10,}", output)
    for block in blocks:
        m = re.search(r"^(FAIL|ERROR):\s+(\S+)", block, re.M)
        if m:
            name = m.group(2).split(".")[-1].split(" ")[0]
            body = [l.strip() for l in block.splitlines() if l.strip()]
            detail = next((l for l in body if l.startswith(("AssertionError",
                                                            "Error", "Traceback"))),
                          body[-1] if body else "")
            if name in statuses:
                details[name] = detail[:300]

    for name, status in statuses.items():
        if status in ("failed", "errored"):
            details.setdefault(name, "")

    return RunResult(statuses=statuses, details=details, output=output,
                     returncode=proc.returncode)


def merge_details(result: RunResult) -> dict:
    """Statuses plus `name#detail` keys, ready for compute_verdict."""
    merged = dict(result.statuses)
    for name, detail in result.details.items():
        merged[f"{name}#detail"] = detail
    return merged
