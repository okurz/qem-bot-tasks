# Execution Plan - Ignore development job groups in product increments

This plan outlines the steps to ensure that openQA jobs in development job groups are ignored during the product increment approval process in `qem-bot`.

## User Review Required

> [!IMPORTANT]
> The implementation relies on fetching job details for each job ID returned by `isos/job_stats`. While `get_single_job` is cached, this might increase the number of API calls to openQA during the first run for each build.

## Proposed Changes

### `openqabot/openqa.py`

- Move the `is_in_devel_group` logic from `SyncRes` (in `openqabot/syncres.py`) to `OpenQAInterface`.
- This method will take a job dictionary (as returned by openQA API) and check if it belongs to a development group based on the group name patterns ("Devel", "Test") or its parent group ID.

### `openqabot/syncres.py`

- Refactor `SyncRes.is_in_devel_group` to delegate to `self.client.is_in_devel_group(data)`.
- Ensure compatibility with existing synchronization logic for submissions and aggregates.

### `openqabot/incrementapprover.py`

- Add a helper method `is_job_in_devel_group(self, job_id: int)` that:
    1. Fetches job details using `self.client.get_single_job(job_id)`.
    2. Checks if the job is in a development group using `self.client.is_in_devel_group(job)`.
    3. Caches the result to minimize API calls.
- Update `evaluate_openqa_job_results` to filter the list of `job_ids` using this helper before processing them.

## Verification Plan

### Automated Tests
- **Reproduction Test**: Create `tests/test_incrementapprover_ignore_devel.py` to:
    - Mock `job_stats` to return a failed job.
    - Mock `get_single_job` for that job ID to return a job in a "Development" group.
    - Assert that `IncrementApprover` ignores this failure and approves the request (assuming other relevant jobs passed or none exist).
- **Regression Testing**: Run all existing tests to ensure that synchronization of submissions and aggregates still correctly filters development jobs.
    - `pytest tests/test_incrementapprover_*.py`
    - `pytest tests/test_subsyncres.py`
    - `pytest tests/test_aggrsync.py`
    - `pytest tests/test_syncres.py`

### Manual Verification
- N/A (Automated tests should cover the logic sufficiently).
