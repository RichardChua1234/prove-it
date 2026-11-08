# Structure: Prove It

## Layout

```
prove-it/
├── .kiro/
│   ├── specs/
│   │   └── prove-it/           # the spec for this tool, verified by this tool
│   │       ├── requirements.md
│   │       ├── design.md
│   │       └── tasks.md
│   ├── steering/               # product.md, tech.md, structure.md
│   ├── hooks/                  # automatic re-checks
│   └── agents/                 # optional test-case proposer
├── src/proveit/
│   ├── __init__.py
│   ├── spec_parser.py          # Kiro spec -> structured criteria
│   ├── trace.py                # criteria + tests -> verdict
│   ├── runner.py               # runs the suite, captures evidence
│   ├── report.py               # verdict -> markdown + JSON
│   └── cli.py                  # entry point
├── tests/                      # mirrors src/, carries criterion annotations
├── docs/
└── README.md
```

## Naming

- Modules: lowercase, single word where possible (`spec_parser`, not
  `SpecParserUtils`).
- Public functions: verb-first and specific — `parse_requirements`,
  `map_criteria_to_tests`, `render_report`.
- Data: plain dataclasses (`Criterion`, `TestRef`, `Verdict`, `Evidence`). No
  framework types crossing module boundaries.

## Boundaries

- **`spec_parser` must not touch the filesystem beyond the spec directory it is
  handed**, and must not import anything from `runner`.
- **`trace` is pure.** Given criteria and test references, it returns a verdict.
  It does not run anything.
- **`runner` is the only module allowed to execute a subprocess.**
- **`report` takes a verdict and returns text.** It does not re-derive facts.

This ordering matters: the model-optional part of the system sits outside the
verdict path, so no amount of agent creativity can turn an unproven criterion
into a proven one.

## Repository conventions

- Public repository, MIT licensed.
- Every acceptance criterion in the spec has at least one test carrying its
  `# criterion: <id>` annotation. The project holds itself to the standard it
  enforces, and `proveit check` on this repo is part of the demo.
