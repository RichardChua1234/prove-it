# Requirements: Prove It

## 1. Parse Kiro Specification

**User story:** As an engineer, I want Prove It to read and parse a Kiro spec directory so that it can extract acceptance criteria in a structured format.

**Acceptance criteria:**

1.1. WHEN the user provides a path to a Kiro spec directory THEN THE SYSTEM SHALL read all requirements files from that directory.

1.2. WHEN the system encounters a spec file THEN THE SYSTEM SHALL parse it into structured criteria with stable identifiers (e.g., `2.3`).

1.3. WHEN the system encounters an unparseable spec file THEN THE SYSTEM SHALL produce an explicit, typed outcome indicating the parsing failure.

1.4. WHERE a spec file is missing or inaccessible THEN THE SYSTEM SHALL report this as a typed failure, not a silent pass.

## 2. Map Criteria to Tests

**User story:** As a reviewer, I want Prove It to find which tests claim to prove each acceptance criterion, so that I can see the mapping between requirements and evidence.

**Acceptance criteria:**

2.1. WHEN the system scans the test suite THEN THE SYSTEM SHALL identify all tests that carry a `# criterion: <id>` annotation.

2.2. WHEN a test carries a criterion annotation THEN THE SYSTEM SHALL associate that test with the corresponding criterion.

2.3. IF a criterion has no test annotation claiming it THEN THE SYSTEM SHALL record it as uncovered.

2.4. WHEN a criterion is claimed by multiple tests THEN THE SYSTEM SHALL include all of them in the verdict.

## 3. Compute Verdict

**User story:** As a tool user, I want Prove It to execute the test suite and determine which criteria are proven, which have failed tests, and which have no test at all.

**Acceptance criteria:**

3.1. WHEN the system runs the test suite THEN THE SYSTEM SHALL capture the real output and pass/fail status of each test.

3.2. WHEN a test carrying a criterion annotation passes THEN THE SYSTEM SHALL mark that criterion as proven.

3.3. WHEN a test carrying a criterion annotation fails THEN THE SYSTEM SHALL mark that criterion as unproven and include the failure details.

3.4. WHEN a criterion has no test annotation claiming it THEN THE SYSTEM SHALL mark it as uncovered.

3.5. WHEN the system cannot run the test suite THEN THE SYSTEM SHALL produce an explicit typed outcome and not report invented results.

## 4. Report Results

**User story:** As an auditor, I want a clear, evidence-backed report showing which criteria are proven, which are unproven, and which have no test at all.

**Acceptance criteria:**

4.1. WHEN the verdict is computed THEN THE SYSTEM SHALL render a markdown report showing all criteria grouped by status (proven, failed, uncovered).

4.2. WHEN a criterion is proven THEN THE SYSTEM SHALL include the test output as evidence in the report.

4.3. WHEN a criterion is unproven THEN THE SYSTEM SHALL include the test failure details in the report.

4.4. WHEN a criterion is uncovered THEN THE SYSTEM SHALL list it explicitly so gaps are visible.

4.5. WHEN the verdict is computed THEN THE SYSTEM SHALL also emit a JSON report containing the same information in machine-readable form.

## 5. Exit Codes

**User story:** As a script author, I want Prove It to use exit codes that signal whether all criteria are proven, some are unproven, or the tool could not run at all.

**Acceptance criteria:**

5.1. WHEN all criteria are proven and all tests pass THEN THE SYSTEM SHALL exit with code `0`.

5.2. WHEN at least one criterion is unproven or has a failing test THEN THE SYSTEM SHALL exit with code `1`.

5.3. WHEN the system cannot run the check (e.g., test suite broken, spec unparseable) THEN THE SYSTEM SHALL exit with code `2`.

## 6. Honest Failure Handling

**User story:** As an engineer, I want Prove It to be transparent about what went wrong instead of hiding failures behind green passes.

**Acceptance criteria:**

6.1. WHEN a spec file cannot be parsed THEN THE SYSTEM SHALL report the specific parsing error, not skip it silently.

6.2. WHEN a test file is missing THEN THE SYSTEM SHALL record this as a typed failure in the verdict.

6.3. WHEN the test suite command fails to execute THEN THE SYSTEM SHALL capture and report the error, not invent a result.

6.4. WHEN a test carries an invalid criterion identifier THEN THE SYSTEM SHALL report this as an annotation error.

6.5. WHEN the system produces a report THEN THE SYSTEM SHALL never include a criterion marked as proven unless a test explicitly claimed it and actually ran successfully.

## 7. Summary Line

**User story:** As a CI author, I want one plain-text summary line so that build logs stay readable without parsing markdown.

**Acceptance criteria:**

7.1. WHEN the check completes THEN THE SYSTEM SHALL print a single plain-text summary line stating the counts of criteria, proven, failed and uncovered.
