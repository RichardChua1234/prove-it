"""Render a verdict as markdown (for humans) and JSON (for machines).

Takes a verdict and returns text. It never re-derives facts and never runs
anything, so a report cannot disagree with the verdict it is given.
"""
from __future__ import annotations

import json

TICK = "[x]"
CROSS = "[ ]"


def _evidence_lines(entries) -> list:
    out = []
    for e in entries:
        where = f"{e.file}:{e.line}" if e.file else ""
        out.append(f"    - `{e.test}` — {e.status} ({where})")
        if e.detail:
            out.append(f"      > {e.detail}")
    return out


def render_markdown(verdict, spec_path: str = "", ran: str = "") -> str:
    total = verdict.total_criteria
    proven = verdict.proven_count
    lines = ["# Prove It — evidence report", ""]

    if spec_path:
        lines += [f"**Spec:** `{spec_path}`"]
    if ran:
        lines += [f"**Tests run with:** `{ran}`"]
    lines += [
        f"**Criteria:** {total}   "
        f"**Proven:** {proven}   "
        f"**Failed:** {len(verdict.failed)}   "
        f"**Uncovered:** {len(verdict.uncovered)}",
        "",
    ]

    if verdict.errors:
        lines += ["## Could not complete the check", ""]
        lines += [f"- {e}" for e in verdict.errors]
        lines += [""]

    if verdict.annotation_errors:
        lines += ["## Annotation errors", ""]
        lines += [f"- {e}" for e in verdict.annotation_errors]
        lines += [""]

    # The gaps come first on purpose: a green suite that proves nothing is the
    # failure mode this tool exists to expose.
    lines += [f"## Uncovered — no test claims these ({len(verdict.uncovered)})", ""]
    if verdict.uncovered:
        for c in verdict.uncovered:
            lines.append(f"- {CROSS} **{c.id}** {c.text}")
    else:
        lines.append("- none")
    lines.append("")

    lines += [f"## Failed — claimed but not proven ({len(verdict.failed)})", ""]
    if verdict.failed:
        for cid in sorted(verdict.failed):
            lines.append(f"- {CROSS} **{cid}**")
            lines += _evidence_lines(verdict.failed[cid])
    else:
        lines.append("- none")
    lines.append("")

    lines += [f"## Proven — claimed and passing ({proven})", ""]
    if verdict.proven:
        for cid in sorted(verdict.proven):
            lines.append(f"- {TICK} **{cid}**")
            lines += _evidence_lines(verdict.proven[cid])
    else:
        lines.append("- none")
    lines.append("")

    if verdict.ok and total:
        lines += ["**Every criterion is proven by a test that ran.**", ""]
    elif total:
        lines += ["**This spec is not fully proven.** "
                  f"{len(verdict.uncovered)} uncovered, "
                  f"{len(verdict.failed)} failed.", ""]

    return "\n".join(lines)


def summary_line(verdict) -> str:
    """One plain-text line for build logs — no markdown to strip."""
    return (f"criteria {verdict.total_criteria} | proven {verdict.proven_count} | "
            f"failed {len(verdict.failed)} | uncovered {len(verdict.uncovered)}")


def render_json(verdict, spec_path: str = "", ran: str = "") -> str:
    def ev(e):
        return {"test": e.test, "file": e.file, "line": e.line,
                "status": e.status, "detail": e.detail}

    data = {
        "spec": spec_path,
        "command": ran,
        "summary": {
            "criteria": verdict.total_criteria,
            "proven": verdict.proven_count,
            "failed": len(verdict.failed),
            "uncovered": len(verdict.uncovered),
            "ok": verdict.ok,
        },
        "proven": {k: [ev(e) for e in v] for k, v in sorted(verdict.proven.items())},
        "failed": {k: [ev(e) for e in v] for k, v in sorted(verdict.failed.items())},
        "uncovered": [{"id": c.id, "text": c.text, "source": c.source}
                      for c in verdict.uncovered],
        "annotation_errors": verdict.annotation_errors,
        "errors": verdict.errors,
    }
    return json.dumps(data, indent=2)
