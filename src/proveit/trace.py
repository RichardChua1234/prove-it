"""Map acceptance criteria to the tests that claim them, and compute a verdict.

`scan_tests` reads test files; `compute_verdict` is pure logic. Coverage is
established by ONE thing only — an explicit annotation:

    # criterion: 3.2

Naming conventions, docstrings and directory names are never treated as
evidence. They are too easy to make look right without being right.
"""
from __future__ import annotations

import ast
import io
import os
import re
import tokenize
from dataclasses import dataclass, field

ANNOTATION_RE = re.compile(r"#\s*criterion:\s*([0-9]+(?:\.[0-9]+)*)")


@dataclass
class TestRef:
    """A test function that claims one or more criteria."""

    name: str
    file: str
    line: int
    criterion_ids: list = field(default_factory=list)


@dataclass
class Evidence:
    """What actually happened when the suite ran."""

    test: str
    file: str
    line: int
    status: str                     # "passed" | "failed" | "errored" | "skipped"
    detail: str = ""


@dataclass
class Verdict:
    proven: dict = field(default_factory=dict)      # id -> [Evidence]
    failed: dict = field(default_factory=dict)      # id -> [Evidence]
    uncovered: list = field(default_factory=list)   # [Criterion]
    annotation_errors: list = field(default_factory=list)
    errors: list = field(default_factory=list)      # spec/test-level failures
    tests_seen: int = 0

    @property
    def total_criteria(self) -> int:
        return len(self.proven) + len(self.failed) + len(self.uncovered)

    @property
    def proven_count(self) -> int:
        return len(self.proven)

    @property
    def ok(self) -> bool:
        """True only when every criterion is proven and nothing else failed."""
        return (not self.failed and not self.uncovered
                and not self.annotation_errors and not self.errors)


def _test_spans(source: str):
    """Line spans of every test function, via the real parser.

    Using the AST rather than regex means a `def test_...` mentioned inside a
    string or a comment cannot be mistaken for a test.
    """
    tree = ast.parse(source)
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test"):
                spans.append((node.name, node.lineno, node.end_lineno or node.lineno))
    return spans


def scan_tests(path: str):
    """Find every test function and the criteria it claims.

    Annotations are read from genuine comments via `tokenize`, then attributed
    to the enclosing test function. Because a docstring is a STRING token and
    not a COMMENT, literal examples like `# criterion: 2.3` inside documentation
    are ignored — otherwise a well-documented suite would report phantom gaps.

    Returns (refs, errors). An unreadable or unparseable file is an error, never
    a silent skip.
    """
    refs, errors = [], []

    if not os.path.exists(path):
        return refs, [f"test path not found: {path!r}"]

    files = []
    if os.path.isfile(path):
        files = [path]
    else:
        for root, dirs, names in os.walk(path):
            dirs.sort()
            for n in sorted(names):
                if n.startswith("test") and n.endswith(".py"):
                    files.append(os.path.join(root, n))

    if not files:
        return refs, [f"no test files found under {path!r}"]

    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                source = fh.read()
        except OSError as exc:
            errors.append(f"{f}: cannot read ({exc})")
            continue

        try:
            spans = _test_spans(source)
        except SyntaxError as exc:
            errors.append(f"{f}: cannot parse ({exc})")
            continue

        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        except (tokenize.TokenError, IndentationError) as exc:
            errors.append(f"{f}: cannot tokenize ({exc})")
            continue

        for tok in tokens:
            if tok.type != tokenize.COMMENT:
                continue
            for cid in ANNOTATION_RE.findall(tok.string):
                lineno = tok.start[0]
                owner = next((name for name, a, b in spans if a <= lineno <= b),
                             None)
                if owner is None:
                    errors.append(
                        f"{f}:{lineno}: criterion annotation {cid} is not "
                        f"inside a test function"
                    )
                    continue
                existing = next(
                    (r for r in refs if r.name == owner and r.file == f), None)
                if existing is None:
                    start = next(a for name, a, b in spans if name == owner)
                    existing = TestRef(name=owner, file=f, line=start)
                    refs.append(existing)
                existing.criterion_ids.append(cid)

    return refs, errors


def compute_verdict(criteria, tests, results, errors=None) -> Verdict:
    """Combine criteria, test annotations and run results into a verdict.

    Pure: no I/O, no clock, no model. `results` maps test name -> status string.
    """
    v = Verdict(errors=list(errors or []))
    by_id = {c.id: c for c in criteria}
    v.tests_seen = len(tests)

    claimed = {}
    for t in tests:
        for cid in t.criterion_ids:
            if cid not in by_id:
                v.annotation_errors.append(
                    f"{os.path.basename(t.file)}:{t.line}: {t.name} claims "
                    f"criterion {cid}, which is not in the spec"
                )
                continue
            status = results.get(t.name, "not run")
            ev = Evidence(test=t.name, file=t.file, line=t.line,
                          status=status, detail=results.get(f"{t.name}#detail", ""))
            if status == "passed":
                claimed.setdefault(cid, {"proven": [], "failed": []})["proven"].append(ev)
            else:
                claimed.setdefault(cid, {"proven": [], "failed": []})["failed"].append(ev)

    for cid, crit in by_id.items():
        entry = claimed.get(cid)
        if not entry:
            v.uncovered.append(crit)
            continue
        if entry["proven"]:
            # A criterion is proven if at least one claiming test passed and no
            # claiming test failed: a failing claim contradicts a passing one.
            if entry["failed"]:
                v.failed[cid] = entry["proven"] + entry["failed"]
            else:
                v.proven[cid] = entry["proven"]
        else:
            v.failed[cid] = entry["failed"]

    if not tests and not v.errors:
        v.errors.append("no tests carry a criterion annotation")

    return v
