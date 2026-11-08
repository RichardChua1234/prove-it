"""Prove It — prove that a Kiro spec is actually backed by tests.

The verdict path is deterministic. No model calls, no network, no clock.
"""
from .spec_parser import Criterion, ParseResult, parse_spec
from .trace import Evidence, TestRef, Verdict, compute_verdict, scan_tests
from .report import render_json, render_markdown

__all__ = [
    "Criterion", "ParseResult", "parse_spec",
    "TestRef", "Evidence", "Verdict", "scan_tests", "compute_verdict",
    "render_markdown", "render_json",
]
__version__ = "0.1.0"
