# Tasks: Prove It

## Phase 1: Data Model and Parsing

- [ ] Define `Criterion`, `TestResult`, `CriterionVerdict`, and `Verdict` dataclasses in `src/proveit/spec_parser.py`.
- [ ] Implement `spec_parser.parse_requirements()` to read and parse requirement files from a spec directory.
- [ ] Implement stable criterion identifier extraction (section number + index, e.g., `2.3`).
- [ ] Add `spec_parser.ParseError`, `FileNotFoundError`, and `FormatError` exception types.
- [ ] Write unit tests for spec parsing in `tests/test_spec_parser.py` with criterion annotations.
- [ ] Test error handling: unparseable specs, missing directories, malformed identifiers.

## Phase 2: Core Tracing Logic

- [ ] Implement `trace.map_criteria_to_tests()` to match tests to criteria by annotation.
- [ ] Implement `trace.compute_verdict()` to classify each criterion as PROVEN, UNPROVEN, or UNCOVERED.
- [ ] Ensure `trace` module is pure (no I/O, no side effects).
- [ ] Write unit tests for tracing logic in `tests/test_trace.py` with criterion annotations.
- [ ] Test edge cases: criteria with no tests, criteria claimed by multiple tests, invalid annotations.

## Phase 3: Test Runner and Evidence Capture

- [ ] Implement `runner.execute_test_suite()` to run the configured test command.
- [ ] Implement `runner.extract_criterion_annotations()` to find `# criterion: <id>` lines in test files.
- [ ] Implement `runner.parse_test_output()` to identify test names and pass/fail status.
- [ ] Add `runner.CommandNotFound`, `TestSuiteFailed`, `TestFileMissing`, and `AnnotationError` exception types.
- [ ] Ensure `runner` is the only module executing subprocesses.
- [ ] Write unit tests for runner in `tests/test_runner.py` with criterion annotations.
- [ ] Test error handling: missing test command, failed tests, missing test files, invalid annotations.

## Phase 4: Report Generation

- [ ] Implement `report.render_markdown()` to generate markdown report grouped by status.
- [ ] Implement `report.render_json()` to generate JSON report.
- [ ] Include test output and failure details as evidence in reports.
- [ ] Handle empty and partial verdicts gracefully.
- [ ] Write unit tests for report generation in `tests/test_report.py` with criterion annotations.
- [ ] Test edge cases: no criteria, all uncovered, mixed status.

## Phase 5: CLI and Integration

- [ ] Implement `cli.main()` entry point with argument parsing.
- [ ] Implement `cli.run_check()` to orchestrate the pipeline: spec_parser → trace → runner → report.
- [ ] Implement exit code logic: 0 for all proven, 1 for unproven/failing, 2 for tool errors.
- [ ] Write integration tests in `tests/test_cli.py` with criterion annotations.
- [ ] Test full pipeline with realistic specs and test suites.
- [ ] Test exit codes under all three scenarios.

## Phase 6: Error Handling and Robustness

- [ ] Ensure all parse errors are typed and included in the verdict.
- [ ] Ensure all runner errors are caught and reported, not silently skipped.
- [ ] Add explicit error section to markdown and JSON reports.
- [ ] Verify that a green test suite never marks an uncovered criterion as proven.
- [ ] Write tests for all error paths in `tests/test_error_handling.py` with criterion annotations.

## Phase 7: Testing Self-Proof

- [ ] Run `prove-it check .kiro/specs/prove-it/` on this repository to verify every criterion has a test.
- [ ] Ensure all tests carry valid `# criterion: <id>` annotations.
- [ ] Fix any uncovered criteria by adding tests or removing criteria.
- [ ] Verify exit code `0` when all criteria are proven.
- [ ] Document any criteria that cannot be tested (if any) and justify why.

## Phase 8: Documentation and Polish

- [ ] Create `docs/` directory with user guide and examples.
- [ ] Add README.md with quick-start instructions.
- [ ] Document the annotation format for test authors.
- [ ] Document error messages and troubleshooting.
- [ ] Add example Kiro spec and corresponding test suite.
- [ ] Verify code is readable in an afternoon; simplify if needed.

## Phase 9: CI and Deployment

- [ ] Add `.kiro/hooks/` post-commit hook to run `prove-it check` automatically.
- [ ] Set up CI to run the full test suite and verify all criteria are proven.
- [ ] Configure exit codes so CI fails when criteria are unproven.
- [ ] Tag repository as MIT licensed.
- [ ] Prepare for public release.
