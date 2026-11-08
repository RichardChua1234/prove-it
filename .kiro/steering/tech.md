# Technology: Prove It

## Language and runtime

- **Python 3.11+**, standard library only for the core.

The core must stay dependency-free. This is deliberate: the tool makes a claim
about evidence, so its own supply chain should be inspectable at a glance.
Anything that could not be read and audited in an afternoon does not belong in
the verdict path.

## Testing

- **`unittest`** from the standard library, so the suite runs anywhere Kiro does.
- Tests live in `tests/`, mirroring the module layout.
- Every test that claims a requirement carries an explicit annotation:

  ```
  # criterion: 2.3
  ```

  The annotation is the *only* thing that establishes coverage. Naming
  conventions, directory names and docstrings are never treated as evidence —
  they are too easy to make look right without being right.

## Design rules

1. **Deterministic verdicts.** The same inputs must always produce the same
   report. No model calls, no network, no clock-dependent output in the verdict.
2. **Separation of concerns.**
   - `spec_parser` — reads a Kiro spec into structured criteria. Pure parsing.
   - `trace` — maps criteria to tests, computes the verdict. Pure logic.
   - `runner` — executes the suite and captures real output. The only I/O edge.
   - `report` — renders the verdict as markdown and JSON.
   - `cli` — argument handling and exit codes.
3. **Stable identifiers.** Criteria are identified by their spec section number
   and index (for example `3.2`), never by line number, so reports stay
   comparable across edits.
4. **Failure is information.** Unparseable specs, missing test files and failed
   commands produce explicit, typed outcomes — never a silent pass.
5. **Exit codes mean something.** `0` all criteria proven; `1` at least one
   criterion unproven or failing; `2` the tool could not run the check at all.

## Kiro integration

- **Specs** — `.kiro/specs/*/` is the input format; Prove It verifies the specs
  Kiro produced rather than a bespoke schema.
- **Steering** — this directory. Conventions live here, not in scattered READMEs.
- **Hooks** — `.kiro/hooks/` re-runs the relevant check automatically so the
  report cannot go stale unnoticed.
- **Agents** — `.kiro/agents/` holds the optional proposer that drafts test cases
  for uncovered criteria. Proposals are written as reviewable files, never
  applied silently.
