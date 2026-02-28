# Task: Distinguish "failed, not-ignored job" from unfinished or waiting jobs in Approver

## Problem Statement
The current `Approver` class in `openqabot/approver.py` conflates all non-passing job statuses (as defined in `openqabot/utils.py`) into a single "failed" category for the purposes of logging and approval decisions. This makes it difficult to tell if a submission is not approved because it actually failed tests or because the tests are still in progress.

Statuses from `normalize_results` in `openqabot/utils.py`:
- `passed` (includes `softfailed`)
- `waiting` (from `none`)
- `stopped` (includes `timeout_exceeded`, `incomplete`, `obsoleted`, etc.)
- `failed` (includes `failed` and unknown results)

## Proposed Solution

### 1. Refine Job Result Handling in `openqabot/approver.py`

#### A. Introduce a Job Status Enum
Define a internal enum or set of constants in `openqabot/approver.py` (or a more appropriate types file) to represent the combined result of a job:
- `PASSED`
- `FAILED`
- `WAITING` (Unfinished/Scheduled)
- `STOPPED`

#### B. Update `is_job_acceptable`
Modify `is_job_acceptable` to return this new status instead of a boolean.
- If `is_job_passing(job_result)` is true -> `PASSED`.
- If manually marked as acceptable or `was_ok_before` -> `PASSED`.
- Else, return `WAITING`, `STOPPED`, or `FAILED` based on `job_result["status"]`.
- Update logging within `is_job_acceptable` to use specific messages:
    - "Found unfinished job..." for `waiting`
    - "Found stopped job..." for `stopped`
    - "Found failed, not-ignored job..." for `failed`

#### C. Update `get_jobs` and `get_submission_result`
- `get_jobs` should aggregate the statuses of all jobs in a group.
    - Priority: `FAILED` > `STOPPED` > `WAITING` > `PASSED`.
- `get_submission_result` should also aggregate these statuses across all `JobAggr` groups.

#### D. Update `approvable`
Modify the log messages in `approvable` based on the aggregated status:
- If `FAILED` -> log "...has at least one failed job"
- If `WAITING` -> log "...has tests still in progress"
- If `STOPPED` -> log "...has stopped tests"

### 2. Implementation Details

#### Example change for `is_job_acceptable`:
```python
def is_job_acceptable(self, sub: int, api: str, job_result: dict) -> JobStatus:
    if self.is_job_passing(job_result):
        return JobStatus.PASSED
    # ... check manual overrides ...
    
    status = job_result.get("status")
    url = f"{self.client.url.geturl()}/t{job_id}"
    if status == "waiting":
        log.info("Found unfinished job %s for submission %s:%s", url, ...)
        return JobStatus.WAITING
    if status == "stopped":
        log.info("Found stopped job %s for submission %s:%s", url, ...)
        return JobStatus.STOPPED
    
    log.info("Found failed, not-ignored job %s for submission %s:%s", url, ...)
    return JobStatus.FAILED
```

### 3. Verification Plan

#### Automated Tests
1. **New Scenario Tests**: Add tests in `tests/test_approve_scenarios.py` that mock dashboard API responses with `status: "waiting"` and `status: "stopped"`.
2. **Log Verification**: Ensure that the output logs correctly distinguish between "failed", "unfinished", and "stopped" jobs.
3. **Approval Logic**: Confirm that submissions with `waiting` or `stopped` jobs are still NOT approved (consistent with current behavior, but with better logging).
4. **Regression Testing**: Run `pytest` to ensure no existing functionality is broken.

#### Quality Assurance
- Run `make tidy` to ensure code formatting.
- Run `make checkstyle` for linting.
- Run `make typecheck-ty` for type consistency.
- Ensure 100% code coverage for the new logic.

## Dependencies
- Changes in `openqabot/approver.py`.
- No changes expected in `qem-dashboard` or other external services.
