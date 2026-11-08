"""Tests for Prove It.

Every test that claims an acceptance criterion carries an explicit annotation:

    # criterion: 2.3

That annotation is the only thing establishing coverage — matching the rule the
tool itself enforces. This suite is the project's own demo: `proveit check` on
this repository should report every criterion proven.
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from proveit import report, runner, spec_parser, trace          # noqa: E402
from proveit.cli import check                                    # noqa: E402

SPEC = """# Requirements: demo

## 1. Parsing

**Acceptance criteria:**

1.1. WHEN given a directory THEN THE SYSTEM SHALL read every requirements file.

1.2. WHEN a spec file is read THEN THE SYSTEM SHALL produce structured criteria.

## 2. Other

2.1. WHEN a criterion has no test THEN THE SYSTEM SHALL record it as uncovered.
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*a, **kw)
    return rc, buf.getvalue()


class ParseSpec(unittest.TestCase):
    def test_reads_every_requirements_file(self):
        # criterion: 1.1
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "requirements.md"), SPEC)
            write(os.path.join(d, "bugfix.md"), "1.3. WHEN bug THEN THE SYSTEM SHALL note it.\n")
            result = spec_parser.parse_spec(d)
        self.assertEqual(len(result.sources), 2)
        self.assertTrue(result.criteria)

    def test_produces_structured_criteria_with_stable_ids(self):
        # criterion: 1.2
        result = spec_parser.parse_text(SPEC, "requirements.md")
        ids = [c.id for c in result.criteria]
        self.assertEqual(ids, ["1.1", "1.2", "2.1"])
        self.assertEqual(result.criteria[0].section, "1")
        self.assertEqual(result.criteria[0].modal, "WHEN")
        self.assertIn("SHALL", result.criteria[0].text)

    def test_unparseable_criterion_is_typed_not_silently_dropped(self):
        # criterion: 1.3
        result = spec_parser.parse_text(
            "9.1. This line has no obligation at all.\n", "bad.md")
        self.assertEqual(result.criteria, [])
        self.assertTrue(result.errors)
        self.assertIn("no SHALL clause", result.errors[0])

    def test_missing_spec_is_a_typed_failure(self):
        # criterion: 1.4
        result = spec_parser.parse_spec("/nonexistent/spec/path")
        self.assertEqual(result.criteria, [])
        self.assertTrue(result.errors)
        self.assertFalse(result.ok)

    def test_spec_with_no_criteria_is_an_error_not_a_pass(self):
        # criterion: 1.4
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "requirements.md"), "# nothing testable here\n")
            result = spec_parser.parse_spec(d)
        self.assertFalse(result.ok)
        self.assertTrue(result.errors)


class MapCriteriaToTests(unittest.TestCase):
    def test_finds_annotated_tests(self):
        # criterion: 2.1
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "test_a.py"),
                  "def test_one():\n    # criterion: 1.1\n    pass\n")
            refs, errors = trace.scan_tests(d)
        self.assertEqual(errors, [])
        self.assertEqual([r.name for r in refs], ["test_one"])

    def test_associates_test_with_its_criterion(self):
        # criterion: 2.2
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "test_a.py"),
                  "def test_one():\n    # criterion: 2.3\n    pass\n")
            refs, _ = trace.scan_tests(d)
        self.assertEqual(refs[0].criterion_ids, ["2.3"])
        self.assertEqual(refs[0].line, 1)

    def test_docstring_examples_are_not_treated_as_annotations(self):
        # criterion: 2.1
        # Regression: this exact case reported a phantom gap in this repo,
        # because the annotation example in the module docstring was matched as
        # if it were a real comment.
        with tempfile.TemporaryDirectory() as d:
            write(os.path.join(d, "test_a.py"),
                  '"""Docs: an example is   # criterion: 9.9\n"""\n'
                  "def test_real():\n    # criterion: 1.1\n    pass\n")
            refs, errors = trace.scan_tests(d)
        self.assertEqual(errors, [])
        self.assertEqual([r.name for r in refs], ["test_real"])
        self.assertEqual(refs[0].criterion_ids, ["1.1"])

    def test_criterion_without_annotation_is_uncovered(self):
        # criterion: 2.3
        criterion = spec_parser.parse_text(SPEC, "r.md").criteria[0]
        verdict = trace.compute_verdict([criterion], [], {})
        self.assertEqual([c.id for c in verdict.uncovered], ["1.1"])

    def test_multiple_tests_claiming_one_criterion_all_appear(self):
        # criterion: 2.4
        criterion = spec_parser.parse_text(SPEC, "r.md").criteria[0]
        refs = [trace.TestRef("t1", "f.py", 1, ["1.1"]),
                trace.TestRef("t2", "f.py", 9, ["1.1"])]
        verdict = trace.compute_verdict(criterion and [criterion], refs,
                                        {"t1": "passed", "t2": "passed"})
        self.assertEqual(len(verdict.proven["1.1"]), 2)


class ComputeVerdict(unittest.TestCase):
    def test_captures_real_per_test_status(self):
        # criterion: 3.1
        sample = (
            "test_ok (tests.test_a.Case.test_ok) ... ok\n"
            "test_bad (tests.test_a.Case.test_bad) ... FAIL\n"
            "test_err (tests.test_a.Case.test_err) ... ERROR\n"
        )
        statuses, _ = runner.parse_unittest_output(sample)
        self.assertEqual(statuses["test_ok"], "passed")
        self.assertEqual(statuses["test_bad"], "failed")
        self.assertEqual(statuses["test_err"], "errored")

    def test_passing_claim_marks_criterion_proven(self):
        # criterion: 3.2
        criterion = spec_parser.parse_text(SPEC, "r.md").criteria[0]
        refs = [trace.TestRef("t1", "f.py", 1, ["1.1"])]
        verdict = trace.compute_verdict([criterion], refs, {"t1": "passed"})
        self.assertIn("1.1", verdict.proven)
        self.assertTrue(verdict.ok)

    def test_failing_claim_marks_criterion_unproven_with_detail(self):
        # criterion: 3.3
        criterion = spec_parser.parse_text(SPEC, "r.md").criteria[0]
        refs = [trace.TestRef("t1", "f.py", 1, ["1.1"])]
        verdict = trace.compute_verdict(
            [criterion], refs, {"t1": "failed", "t1#detail": "AssertionError: nope"})
        self.assertIn("1.1", verdict.failed)
        self.assertEqual(verdict.failed["1.1"][0].detail, "AssertionError: nope")
        self.assertFalse(verdict.ok)

    def test_no_claiming_test_is_uncovered(self):
        # criterion: 3.4
        criterion = spec_parser.parse_text(SPEC, "r.md").criteria[0]
        verdict = trace.compute_verdict([criterion], [], {})
        self.assertIn("1.1", [c.id for c in verdict.uncovered])

    def test_unrunnable_suite_is_typed_and_invents_nothing(self):
        # criterion: 3.5
        result = runner.run_suite("this-command-does-not-exist-xyz")
        self.assertTrue(result.error)
        self.assertEqual(result.statuses, {})
        self.assertFalse(result.ok)

    def test_claimed_but_never_run_is_not_proven(self):
        # criterion: 6.5
        criterion = spec_parser.parse_text(SPEC, "r.md").criteria[0]
        refs = [trace.TestRef("t1", "f.py", 1, ["1.1"])]
        verdict = trace.compute_verdict([criterion], refs, {})
        self.assertNotIn("1.1", verdict.proven)
        self.assertIn("1.1", verdict.failed)


class Reporting(unittest.TestCase):
    def _verdict(self):
        criteria = spec_parser.parse_text(SPEC, "r.md").criteria
        refs = [trace.TestRef("t_pass", "f.py", 1, ["1.1"]),
                trace.TestRef("t_fail", "f.py", 5, ["1.2"])]
        return trace.compute_verdict(criteria, refs, {
            "t_pass": "passed", "t_fail": "failed",
            "t_fail#detail": "AssertionError: expected 2 got 3"})

    def test_markdown_groups_by_status(self):
        # criterion: 4.1
        md = report.render_markdown(self._verdict(), "spec", "cmd")
        self.assertIn("## Proven", md)
        self.assertIn("## Failed", md)
        self.assertIn("## Uncovered", md)

    def test_proven_entries_include_evidence(self):
        # criterion: 4.2
        md = report.render_markdown(self._verdict())
        self.assertIn("t_pass", md)
        self.assertIn("passed", md)

    def test_unproven_entries_include_failure_detail(self):
        # criterion: 4.3
        md = report.render_markdown(self._verdict())
        self.assertIn("expected 2 got 3", md)

    def test_uncovered_criteria_are_listed_explicitly(self):
        # criterion: 4.4
        md = report.render_markdown(self._verdict())
        self.assertIn("2.1", md)

    def test_json_report_carries_the_same_information(self):
        # criterion: 4.5
        v = self._verdict()
        data = json.loads(report.render_json(v, "spec", "cmd"))
        self.assertEqual(data["summary"]["proven"], len(v.proven))
        self.assertIn("1.1", data["proven"])
        self.assertIn("1.2", data["failed"])
        self.assertEqual(len(data["uncovered"]), len(v.uncovered))


class ExitCodes(unittest.TestCase):
    def _project(self, body):
        d = tempfile.mkdtemp()
        write(os.path.join(d, "spec", "requirements.md"), SPEC)
        write(os.path.join(d, "tests", "test_s.py"), body)
        return d

    def _run(self, d):
        cmd = f"{sys.executable} -m unittest discover -s tests -v"
        return quiet(check, os.path.join(d, "spec"),
                     os.path.join(d, "tests"), cmd, cwd=d)

    def test_exit_zero_when_everything_proven(self):
        # criterion: 5.1
        d = self._project(
            "import unittest\n\n"
            "class C(unittest.TestCase):\n"
            "    def test_a(self):\n        # criterion: 1.1\n        pass\n"
            "    def test_b(self):\n        # criterion: 1.2\n        pass\n"
            "    def test_c(self):\n        # criterion: 2.1\n        pass\n")
        rc, _ = self._run(d)
        self.assertEqual(rc, 0)

    def test_exit_one_when_a_criterion_is_unproven(self):
        # criterion: 5.2
        d = self._project(
            "import unittest\n\n"
            "class C(unittest.TestCase):\n"
            "    def test_a(self):\n        # criterion: 1.1\n        pass\n"
            "    def test_b(self):\n        # criterion: 1.2\n        self.fail('nope')\n")
        rc, out = self._run(d)
        self.assertEqual(rc, 1)

    def test_exit_two_when_the_check_cannot_run(self):
        # criterion: 5.3
        d = self._project("import unittest\n")
        rc, _ = self._run("/nonexistent/spec")
        self.assertEqual(rc, 2)

    def test_plain_summary_line_is_printed(self):
        # criterion: 7.1
        d = self._project(
            "import unittest\n\n"
            "class C(unittest.TestCase):\n"
            "    def test_a(self):\n        # criterion: 1.1\n        pass\n"
            "    def test_b(self):\n        # criterion: 1.2\n        pass\n"
            "    def test_c(self):\n        # criterion: 2.1\n        pass\n")
        rc, out = self._run(d)
        first = [l for l in out.splitlines() if l.strip()][0]
        self.assertRegex(
            first,
            r"^criteria \d+ \| proven \d+ \| failed \d+ \| uncovered \d+$")
        self.assertNotIn("**", first)


class HonestFailure(unittest.TestCase):
    def test_parse_error_names_the_offending_criterion(self):
        # criterion: 6.1
        result = spec_parser.parse_text(
            "6.1. no obligation here\n", "broken.md")
        self.assertTrue(result.errors)
        self.assertIn("6.1", result.errors[0])
        self.assertIn("broken.md", result.errors[0])

    def test_missing_test_path_is_a_typed_failure(self):
        # criterion: 6.2
        refs, errors = trace.scan_tests("/nonexistent/tests")
        self.assertEqual(refs, [])
        self.assertTrue(errors)
        self.assertIn("not found", errors[0])

    def test_failing_command_is_reported_not_invented(self):
        # criterion: 6.3
        result = runner.run_suite("python3 -c 'import sys; sys.exit(3)'")
        self.assertTrue(result.error)
        self.assertEqual(result.statuses, {})
        self.assertIn("no output", result.error)

    def test_invalid_criterion_identifier_is_an_annotation_error(self):
        # criterion: 6.4
        criterion = spec_parser.parse_text(SPEC, "r.md").criteria[0]
        refs = [trace.TestRef("t1", "f.py", 1, ["9.9"])]
        verdict = trace.compute_verdict([criterion], refs, {"t1": "passed"})
        self.assertTrue(verdict.annotation_errors)
        self.assertIn("9.9", verdict.annotation_errors[0])
        self.assertNotIn("9.9", verdict.proven)


if __name__ == "__main__":
    unittest.main(verbosity=2)
