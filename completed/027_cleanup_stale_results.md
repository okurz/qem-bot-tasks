# Refined Execution Plan - Task 27: Cleanup of unwanted test results

## Problem Statement
`qem-bot` relies on openQA job results stored in `qem-dashboard`. When a job is deleted or restarted in openQA, the dashboard often retains the old "not-ok" status. `qem-bot` does not proactively refresh these stale entries during the approval process or regular sync, leading to blocked approvals for submissions that should otherwise pass.

## Goal
Ensure that `qem-bot` refreshes stale or missing openQA job results in the dashboard, particularly when they are blocking a submission's approval.

## Proposed Changes

### 1. openqabot/openqa.py (OpenQAInterface)
- **Update `get_single_job(job_id)`**:
    - Specifically handle `HTTPStatus.NOT_FOUND` (404) from openQA.
    - If a job is not found, call `self.handle_job_not_found(job_id)` to mark it as obsolete in the dashboard and return `None`.
    - Log at `INFO` level when a job is missing, but avoid `ERROR` level exceptions for expected 404s during refresh.
- **Update `get_job_comments(job_id)`**:
    - Ensure it consistently handles 404s by marking jobs as obsolete (already partially implemented, but needs verification).

### 2. openqabot/approver.py (Approver)
- **New/Refined Job Refresh Logic**:
    - Enhance the non-passing job check to proactively verify current state in openQA.
    - For each job that is not "passed" in the dashboard:
        1. **Check Existence/Status**: Call `self.client.get_single_job(job_id)`.
        2. **Handle Missing Jobs**: If it returns `None` (404), ensure the local `job_result` is marked as `obsolete`.
        3. **Handle Cloned Jobs**: If the job has a `clone_id` in openQA, it means a newer attempt exists. Mark the current job as `obsolete` locally and in the dashboard.
        4. **Update Status**: If the job status in openQA has changed (e.g., it finished since the last sync), update the local `job_result` and the dashboard.
- **Update `is_job_acceptable`**:
    - Add a check: `if job_result.get("obsolete"): return True`. This ensures that obsolete jobs no longer block approval.

### 3. openqabot/syncres.py (SyncRes)
- **Proactive Refresh during Sync**:
    - Add logic to the sync process to verify the status of existing non-passing jobs in the dashboard for active submissions.
    - This ensures the dashboard stays clean even if the `Approver` is not run.

## Verification Plan

### Unit Tests
- **Test Case: Missing Job**:
    - Mock openQA API to return 404 for a specific `job_id`.
    - Verify `Approver` marks the job as obsolete and does not block approval.
    - Verify `patch` is called on the dashboard API with `{"obsolete": True}`.
- **Test Case: Cloned Job**:
    - Mock openQA API to return a job with a `clone_id`.
    - Verify `Approver` marks the original job as obsolete.
- **Test Case: Changed Status**:
    - Mock openQA API to return `passed` for a job currently marked as `failed` in the dashboard.
    - Verify `Approver` updates the status and allows approval.

### Integration Tests
- Run `make test` and `make test-with-coverage` to ensure no regressions in approval logic.
- Specifically check `tests/test_approve_obs.py` and `tests/test_openqaclient.py`.

## Detailed Implementation Steps

1. **Modify `OpenQAInterface.get_single_job`** in `openqabot/openqa.py`:
    - Improve error handling to catch 404 and call `handle_job_not_found`.
2. **Modify `Approver.is_job_acceptable`** in `openqabot/approver.py`:
    - Allow `obsolete` jobs to pass.
3. **Enhance `Approver` refresh logic** in `openqabot/approver.py`:
    - Integrate status and clone checks for non-passing jobs.
4. **Update Tests**:
    - Add scenarios for 404 and cloned jobs in `tests/test_approve_obs.py`.
