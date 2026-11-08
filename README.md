# Prove It

**Prove that a Kiro spec is actually backed by tests that ran.**

Most teams have tests. Far fewer can show, on demand, that every stated
requirement has evidence behind it. Prove It reads the spec Kiro already
produced, maps each acceptance criterion to the test that claims it, runs the
suite, and reports three things:

- **Proven** — a test claimed this criterion and passed
- **Failed** — a test claimed it and did not pass, with the failure detail
- **Uncovered** — no test claims it at all

That third list is the point. A green suite that proves nothing is the failure
mode this tool exists to expose.

## Try it in one command

```bash
PYTHONPATH=src python3 -m proveit check \
  --spec .kiro/specs/prove-it \
  --tests tests \
  --md-out docs/evidence-report.md \
  --json-out docs/evidence-report.json
```

Exit codes: `0` every criterion proven · `1` something uncovered or failing ·
`2` the check could not be completed.

## See it catch a gap

The suite can be entirely green while the spec is not proven. Remove a
`# criterion: 3.4` annotation, leaving the criterion in the spec with no test
claiming it:

```
$ python3 -m unittest discover -s tests
OK                        <- the suite is still happy

$ python3 -m proveit check --spec .kiro/specs/prove-it --tests tests
**Criteria:** 26   **Proven:** 24   **Failed:** 0   **Uncovered:** 2
exit 1                    <- the spec is not proven, and it says which
```

## How coverage is established

By exactly one thing — an explicit annotation inside a test function:

```python
def test_failing_claim_marks_criterion_unproven(self):
    # criterion: 3.3
    ...
```

Naming conventions, docstrings and directory names are **never** treated as
evidence; they are too easy to make look right without being right. Annotations
are read from genuine comments via `tokenize` and attributed to the enclosing
function via `ast`, so an example like `# criterion: 9.9` written inside a
docstring cannot create a phantom claim.

## Design

The agent proposes; deterministic code disposes. Any model involvement is
confined to *suggesting* tests and annotations. The verdict is computed by plain
Python you can read in an afternoon:

| Module | Responsibility |
|---|---|
| `spec_parser` | Kiro spec → structured criteria. Pure parsing. |
| `trace` | criteria + annotations + results → verdict. Pure logic. |
| `runner` | runs the suite and captures real output. The only subprocess. |
| `report` | verdict → markdown and JSON. Never re-derives facts. |
| `cli` | argument handling and exit codes. |

No third-party dependencies. Standard library only, and `unittest` for the
suite, so it runs anywhere Kiro does.

## Built with Kiro

This project is developed using Kiro, and uses Kiro's own features rather than
treating it as a text editor:

- **Specs** — `.kiro/specs/prove-it/` (`requirements.md`, `design.md`,
  `tasks.md`), authored with Kiro CLI. It is the input format *and* the thing
  being verified: the project holds itself to the standard it enforces.
- **Steering** — `.kiro/steering/` (`product.md`, `tech.md`, `structure.md`)
  carries the conventions, so they live in one place instead of scattered
  READMEs.
- **Hooks** — `.kiro/hooks/prove-it.json` re-runs the check automatically so the
  report cannot silently go stale.
- **Agents** — `.kiro/agents/` holds an optional proposer that drafts test cases
  for uncovered criteria. Proposals are written as reviewable files and never
  applied silently.

## Licence

MIT
