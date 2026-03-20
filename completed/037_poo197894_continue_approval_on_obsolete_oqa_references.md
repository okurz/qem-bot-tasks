# Implementation Plan - Continue approval on obsolete openQA references

This plan addresses issue #197894 where openQA jobs marked as obsolete on the dashboard still block the approval process.

## Problem
When an openQA job is not found, `qem-bot` marks it as `obsolete` on the dashboard. However, the `Approver` still treats this job as "not-ok" and blocks the submission approval.

## Proposed Changes
1.  **Modify `openqabot/approver.py`**:
    *   Update `is_job_acceptable` to return `True` if the job is marked as `obsolete`.
2.  **Add/Update Tests**:
    *   Add a test case to `tests/test_approve_scenarios.py` (or a new test file) where a failed job is marked as `obsolete` and ensure the submission is approved.
    *   Ensure that other non-obsolete failed jobs still block approval.

## Execution Steps
1.  **Research & Verification**:
    *   [x] Locate relevant code in `openqabot/approver.py` and `openqabot/openqa.py`.
    *   [x] Verify if `obsolete` field is present in `job_result` passed to `is_job_acceptable`.
2.  **Implementation**:
    *   [x] Modify `is_job_acceptable` in `openqabot/approver.py`.
3.  **Testing**:
    *   [x] Create a reproduction test case in `tests/test_approve_obsolete.py`.
    *   [x] Run tests with `make test`.
4.  **Verification**:
    *   [x] Run `make tidy`, `make checkstyle`, `make typecheck-ty`.
