# Product: Prove It

## Purpose

Prove It answers one question about a Kiro spec: **is every acceptance criterion
actually proven by a test that ran?**

Most teams have tests. Far fewer can show, on demand, that each stated
requirement has evidence behind it. Prove It closes that gap. It reads the spec
Kiro already produced, maps each acceptance criterion to the test that proves it,
runs the suite, and emits an evidence report showing which criteria are proven,
which failed, and — the uncomfortable category — which have **no test at all**.

## Who it is for

- Engineers using Kiro specs, who want their requirements to stay honest after
  the design doc is written and the code has drifted.
- Reviewers and auditors who need a reconstructable answer to "how do you know
  this works?" rather than a coverage percentage.
- Anyone who has to sign off on a system and would prefer evidence to assurance.

## Core principles

1. **The agent proposes; deterministic code disposes.** Any model involvement is
   limited to *suggesting* test cases and annotations. The verdict — covered,
   uncovered, passed, failed — is computed by plain, deterministic code that can
   be read and audited.
2. **Evidence, not assertion.** A criterion is not "covered" because a test name
   looks related. It is covered when a test explicitly claims that criterion and
   that test passed, and the report carries the captured output.
3. **Gaps are the point.** The most valuable output is the list of criteria with
   no test at all. A green suite that proves nothing is the failure mode this
   tool exists to expose.
4. **No invented results.** If a test cannot be run, the tool says so. It never
   reports a pass it did not observe.

## Non-goals

- Not a coverage tool. Line coverage measures code executed; Prove It measures
  *requirements evidenced*.
- Not a test generator that must be trusted. Generation is optional and its
  output is always reviewed as a proposal.
- Not a hosted service. It runs locally, reads local files, and needs no account.

## Success looks like

Running one command on a repo with a Kiro spec and getting either:

- a traceability report where every criterion maps to a passing test, or
- a precise list of the criteria that are unproven — which is a bug in the
  project's honesty, not in the tool.
