# Design: Prove It

## Architecture

Prove It follows a linear pipeline with clear separation of concerns. Each module has a single responsibility, and the verdicts are computed by deterministic, auditable code that can be read in an afternoon.

```
Input: Kiro spec directory + test suite
  ↓
spec_parser (parse requirements into criteria)
  ↓
trace (map criteria to tests, compute verdict)
  ↓
runner (execute tests, capture output)
  ↓
report (render markdown + JSON)
  ↓
cli (handle arguments, exit codes)
```

## Module Responsibilities

### `spec_parser`

Reads a Kiro spec directory and parses it into structured criteria.

**Responsibilities:**
- Read requirement files from the provided spec directory.
- Parse criteria with stable identifiers (e.g., `2.3`) derived from section and index.
- Extract criterion text and constraints.
- Return typed `Criterion` objects or explicit parse failures.

**Constraints:**
- Must not touch the filesystem beyond the spec directory handed to it.
- Must not import anything from `runner`.
- Must be deterministic: same input always produces same output.

**Failure modes:**
- Unparseable spec format → typed `ParseError` with details.
- Missing spec directory → typed `FileNotFoundError`.
- Malformed criterion identifiers → typed `FormatError`.

### `trace`

Pure logic module that maps criteria to tests and computes the verdict.

**Responsibilities:**
- Accept a list of criteria and a list of test references (each with test name and criterion annotation).
- Match tests to criteria by annotation.
- Classify each criterion as proven (test passed), unproven (test failed), or uncovered (no test).
- Return a `Verdict` object containing all classifications.

**Constraints:**
- Must be pure: no I/O, no side effects, no time-dependent logic.
- Must not execute anything.
- Must not import anything from `runner`.

**Data flow:**
- Input: `List[Criterion]`, `List[TestResult]`
- Output: `Verdict` containing classifications for each criterion.

### `runner`

Executes the test suite and captures output. The only module allowed to execute subprocesses.

**Responsibilities:**
- Execute the configured test command.
- Capture stdout, stderr, and exit status.
- Parse test output to identify test names and pass/fail status.
- Extract `# criterion: <id>` annotations from test code.
- Return a list of `TestResult` objects.

**Constraints:**
- Must be the only module executing subprocesses.
- Must capture all output for inclusion in the report.
- Must handle test command failures gracefully and report them as typed outcomes.

**Failure modes:**
- Test command not found → typed `CommandNotFound`.
- Test command exits non-zero → typed `TestSuiteFailed` with captured output.
- Test file missing → typed `TestFileMissing`.
- Cannot parse test annotations → typed `AnnotationError`.

### `report`

Renders the verdict into markdown and JSON formats.

**Responsibilities:**
- Accept a `Verdict` object.
- Generate a markdown report organized by status (proven, unproven, uncovered).
- Generate a JSON report with the same information.
- Include test output and failure details as evidence.
- Handle empty or partial verdicts gracefully.

**Constraints:**
- Must not re-derive facts; only format the verdict provided.
- Must not make decisions about proof; only format what was computed.

**Output formats:**
- Markdown: human-readable, organized by status, includes evidence.
- JSON: machine-parseable, complete, suitable for downstream automation.

### `cli`

Entry point and argument handling.

**Responsibilities:**
- Parse command-line arguments.
- Invoke the pipeline in correct order.
- Catch and format errors for the user.
- Set exit codes based on verdict.
- Write reports to stdout or files.

**Exit codes:**
- `0`: all criteria proven.
- `1`: at least one criterion unproven or failing.
- `2`: tool could not run (unparseable spec, missing files, broken test command).

## Data Model

### `Criterion`

```
Criterion
├── id: str (e.g., "2.3")
├── section: int (e.g., 2)
├── index: int (e.g., 3)
├── text: str (criterion description)
└── constraints: List[str] (WHEN/WHILE/IF/WHERE clauses)
```

### `TestResult`

```
TestResult
├── name: str (test name)
├── passed: bool
├── output: str (captured stdout/stderr)
├── criterion_ids: List[str] (criterion annotations found)
└── error: Optional[str] (if test failed or could not run)
```

### `CriterionVerdict`

```
CriterionVerdict
├── criterion: Criterion
├── status: Enum (PROVEN | UNPROVEN | UNCOVERED)
├── test_results: List[TestResult] (tests claiming this criterion)
└── error: Optional[str] (if status is UNPROVEN, the failure details)
```

### `Verdict`

```
Verdict
├── criteria_verdicts: List[CriterionVerdict]
├── total_criteria: int
├── proven_count: int
├── unproven_count: int
├── uncovered_count: int
├── parse_errors: List[str] (any spec parsing issues)
└── runner_errors: List[str] (any test execution issues)
```

## Error Handling

Errors are typed, explicit, and never silently passed. Every failure is recorded in the verdict.

**Typing strategy:**
- Each module defines its own exception types.
- Exceptions are caught and converted to typed `Error` objects in the verdict.
- The verdict is never empty; it includes errors alongside successful results.

**Error categories:**

1. **Parse errors** (spec cannot be read/understood):
   - `spec_parser.ParseError`: spec format invalid.
   - `spec_parser.FileNotFoundError`: spec directory missing.
   - `spec_parser.FormatError`: criterion identifier malformed.

2. **Runner errors** (test suite cannot run):
   - `runner.CommandNotFound`: test command not found.
   - `runner.TestSuiteFailed`: test command exited non-zero.
   - `runner.TestFileMissing`: test file referenced but not found.
   - `runner.AnnotationError`: criterion annotation invalid.

3. **Logic errors** (verdict computation):
   - Logged and included in verdict; trace never raises exceptions.

**Reporting errors:**
- Markdown report includes an "Errors" section listing all typed failures.
- JSON report includes an `errors` array with type and message.
- Exit code reflects the presence of errors (exit 2 if tool cannot run).

## Testing Strategy

Every test carries an explicit `# criterion: <id>` annotation that is the sole evidence of coverage.

**Test organization:**
- `tests/` mirrors `src/` structure.
- `tests/test_spec_parser.py` tests `spec_parser.py`.
- `tests/test_trace.py` tests `trace.py`.
- `tests/test_runner.py` tests `runner.py`.
- `tests/test_report.py` tests `report.py`.
- `tests/test_cli.py` tests `cli.py`.

**Annotation rules:**
- Every test that claims a requirement must carry exactly one `# criterion: <id>` line.
- Annotation format: `# criterion: <id>` on a single line in the test function or module.
- Unparseable or duplicate annotations are errors, not silently ignored.

**Test scope:**
- Unit tests for pure functions (`spec_parser`, `trace`, `report`).
- Integration tests for the pipeline (spec → verdict → report).
- Error cases tested explicitly (unparseable specs, missing files, failed tests).
- No mocking of verdict computation; all tests run actual code paths.

## Determinism and Auditability

**Deterministic verdicts:**
- Same spec and test suite always produce same verdict.
- No model calls, no network, no time-dependent logic.
- Output is reproducible and can be diffed across runs.

**Auditability:**
- Core code uses only Python standard library (no dependencies).
- Code is readable in an afternoon; no magic frameworks.
- Errors are explicit, typed, and captured in the verdict.
- All evidence (test output, errors) is included in the report.

**Stability:**
- Criteria identified by stable section/index, not line numbers.
- Reports can be compared across spec edits without spurious diffs.
- Criterion text changes are visible but don't break traceability.
