# Prove It — evidence report

**Spec:** `.kiro/specs/prove-it`
**Tests run with:** `/opt/hermes/.venv/bin/python3 -m unittest discover -s tests -v`
**Criteria:** 27   **Proven:** 27   **Failed:** 0   **Uncovered:** 0

## Uncovered — no test claims these (0)

- none

## Failed — claimed but not proven (0)

- none

## Proven — claimed and passing (27)

- [x] **1.1**
    - `test_reads_every_requirements_file` — passed (tests/test_proveit.py:54)
- [x] **1.2**
    - `test_produces_structured_criteria_with_stable_ids` — passed (tests/test_proveit.py:63)
- [x] **1.3**
    - `test_unparseable_criterion_is_typed_not_silently_dropped` — passed (tests/test_proveit.py:72)
- [x] **1.4**
    - `test_missing_spec_is_a_typed_failure` — passed (tests/test_proveit.py:80)
    - `test_spec_with_no_criteria_is_an_error_not_a_pass` — passed (tests/test_proveit.py:87)
- [x] **2.1**
    - `test_finds_annotated_tests` — passed (tests/test_proveit.py:97)
    - `test_docstring_examples_are_not_treated_as_annotations` — passed (tests/test_proveit.py:115)
- [x] **2.2**
    - `test_associates_test_with_its_criterion` — passed (tests/test_proveit.py:106)
- [x] **2.3**
    - `test_criterion_without_annotation_is_uncovered` — passed (tests/test_proveit.py:129)
- [x] **2.4**
    - `test_multiple_tests_claiming_one_criterion_all_appear` — passed (tests/test_proveit.py:135)
- [x] **3.1**
    - `test_captures_real_per_test_status` — passed (tests/test_proveit.py:146)
- [x] **3.2**
    - `test_passing_claim_marks_criterion_proven` — passed (tests/test_proveit.py:158)
- [x] **3.3**
    - `test_failing_claim_marks_criterion_unproven_with_detail` — passed (tests/test_proveit.py:166)
- [x] **3.4**
    - `test_no_claiming_test_is_uncovered` — passed (tests/test_proveit.py:176)
- [x] **3.5**
    - `test_unrunnable_suite_is_typed_and_invents_nothing` — passed (tests/test_proveit.py:182)
- [x] **4.1**
    - `test_markdown_groups_by_status` — passed (tests/test_proveit.py:207)
- [x] **4.2**
    - `test_proven_entries_include_evidence` — passed (tests/test_proveit.py:214)
- [x] **4.3**
    - `test_unproven_entries_include_failure_detail` — passed (tests/test_proveit.py:220)
- [x] **4.4**
    - `test_uncovered_criteria_are_listed_explicitly` — passed (tests/test_proveit.py:225)
- [x] **4.5**
    - `test_json_report_carries_the_same_information` — passed (tests/test_proveit.py:230)
- [x] **5.1**
    - `test_exit_zero_when_everything_proven` — passed (tests/test_proveit.py:252)
- [x] **5.2**
    - `test_exit_one_when_a_criterion_is_unproven` — passed (tests/test_proveit.py:263)
- [x] **5.3**
    - `test_exit_two_when_the_check_cannot_run` — passed (tests/test_proveit.py:273)
- [x] **6.1**
    - `test_parse_error_names_the_offending_criterion` — passed (tests/test_proveit.py:296)
- [x] **6.2**
    - `test_missing_test_path_is_a_typed_failure` — passed (tests/test_proveit.py:304)
- [x] **6.3**
    - `test_failing_command_is_reported_not_invented` — passed (tests/test_proveit.py:311)
- [x] **6.4**
    - `test_invalid_criterion_identifier_is_an_annotation_error` — passed (tests/test_proveit.py:318)
- [x] **6.5**
    - `test_claimed_but_never_run_is_not_proven` — passed (tests/test_proveit.py:189)
- [x] **7.1**
    - `test_plain_summary_line_is_printed` — passed (tests/test_proveit.py:279)

**Every criterion is proven by a test that ran.**
