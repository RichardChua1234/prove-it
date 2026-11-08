"""Read a Kiro spec directory into structured acceptance criteria.

Pure parsing: no subprocess, no network, no model calls, no clock. Given the same
files it always returns the same criteria in the same order.

Handles the format Kiro itself writes:

    ## 3. Compute Verdict

    **Acceptance criteria:**

    3.1. WHEN the system runs the test suite THEN THE SYSTEM SHALL capture ...

Criteria are identified by their spec number (`3.1`), never by line number, so
reports stay comparable across edits.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

CRITERION_RE = re.compile(r"^\s*(\d+\.\d+)\s*[.)]\s+(.*\S)\s*$")
SECTION_RE = re.compile(r"^\s*#{1,3}\s+(\d+)\.\s+(.*\S)\s*$")
MODALS = ("WHEN", "WHILE", "IF", "WHERE")


@dataclass(frozen=True)
class Criterion:
    """One testable statement from a spec."""

    id: str                 # "3.1"
    section: str            # "3"
    section_title: str      # "Compute Verdict"
    text: str               # the full criterion sentence
    source: str             # file it came from
    line: int               # where it was found (for humans only)

    @property
    def modal(self) -> str:
        upper = self.text.upper()
        for m in MODALS:
            if upper.startswith(m):
                return m
        return ""


@dataclass
class ParseResult:
    criteria: list = field(default_factory=list)
    errors: list = field(default_factory=list)      # parse-level problems
    sources: list = field(default_factory=list)     # files read

    @property
    def ok(self) -> bool:
        return bool(self.criteria) and not self.errors


def _spec_files(path: str):
    """Every markdown file holding requirements, in a stable order."""
    if os.path.isfile(path):
        return [path]
    if not os.path.isdir(path):
        return []
    found = []
    for root, dirs, files in os.walk(path):
        dirs.sort()
        for name in sorted(files):
            if name.endswith(".md"):
                found.append(os.path.join(root, name))
    return found


def parse_text(text: str, source: str) -> ParseResult:
    """Parse one requirements document."""
    result = ParseResult(sources=[source])
    section, section_title = "", ""

    for lineno, line in enumerate(text.splitlines(), 1):
        m = SECTION_RE.match(line)
        if m:
            section, section_title = m.group(1), m.group(2)
            continue

        m = CRITERION_RE.match(line)
        if not m:
            continue

        cid, body = m.group(1), m.group(2)

        # A criterion must state a testable obligation. If it has no SHALL
        # clause it is prose that happens to start with a number, and silently
        # dropping it would hide a gap rather than report one.
        if "SHALL" not in body.upper():
            result.errors.append(
                f"{source}:{lineno}: criterion {cid} has no SHALL clause"
            )
            continue

        if not body.upper().startswith(MODALS):
            result.errors.append(
                f"{source}:{lineno}: criterion {cid} does not begin with a "
                f"trigger word ({'/'.join(MODALS)})"
            )
            continue

        result.criteria.append(Criterion(
            id=cid,
            section=section or cid.split(".")[0],
            section_title=section_title,
            text=body,
            source=source,
            line=lineno,
        ))

    return result


def parse_spec(path: str) -> ParseResult:
    """Parse a spec directory (or a single file) into criteria.

    Missing paths and specs with no criteria are typed errors, never an empty
    pass — an unreadable spec must not look like a proven one.
    """
    files = _spec_files(path)
    if not files:
        return ParseResult(errors=[f"no spec files found at {path!r}"])

    merged = ParseResult(sources=files)
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            merged.errors.append(f"{f}: cannot read ({exc})")
            continue
        part = parse_text(text, f)
        merged.criteria.extend(part.criteria)
        merged.errors.extend(part.errors)

    if not merged.criteria and not merged.errors:
        merged.errors.append(f"no acceptance criteria found under {path!r}")

    # stable, comparable ordering
    merged.criteria.sort(key=lambda c: [int(p) for p in c.id.split(".")])
    return merged
