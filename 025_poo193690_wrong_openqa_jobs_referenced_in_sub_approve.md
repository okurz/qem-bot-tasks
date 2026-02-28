# Execution Plan - Fix wrong openQA job runs referenced in `inc-approve` (poo#193690)

The `inc-approve` process in `qem-bot` sometimes incorrectly blocks approvals because it considers all job runs for a given scenario, including older failed runs that have since been superseded by successful clones or restarts.

## Proposed Changes

### 1. `openqabot/approver.py`
- Modify `Approver.get_jobs` to ensure only the latest job run (highest `job_id`) is considered for each scenario (each `job_aggr.id`).
- Add a check to ensure `job_results` is a list and handle potential error dictionaries from `get_json`.

### 2. `tests/test_poo193690.py` (New Test)
- Create a reproduction test case that mocks a dashboard response containing multiple job runs for a single setting ID.
- Verify that a submission is approved if the latest run is "passed", even if an older run is "failed".
- Verify that a submission is NOT approved if the latest run is "failed".

## Detailed Steps

1. **Investigation & Reproduction**:
   - Verify the current behavior by adding a test case to `tests/test_approve_scenarios.py` or a new file that fails under the current logic.
   - Example mock data: `[{"job_id": 100, "status": "failed"}, {"job_id": 101, "status": "passed"}]` for a single setting.

2. **Implementation**:
   - In `openqabot/approver.py`, update `get_jobs`:
     ```python
     def get_jobs(self, job_aggr: JobAggr, api: str, sub: int, submission_type: str | None = None) -> bool | None:
         # ... existing fetching logic ...
         job_results = get_json(api + str(job_aggr.id), headers=self.token, params=params)
         if not job_results or "error" in job_results:
             # handle error/empty
             return None
         
         # AC1: Only consider the latest job run for each scenario
         latest_job = max(job_results, key=lambda x: x["job_id"])
         job_results = [latest_job]
         
         self.mark_jobs_as_acceptable_for_submission(job_results, sub)
         return all(self.is_job_acceptable(sub, api, r) for r in job_results)
     ```

3. **Verification**:
   - Run the new test case.
   - Run all existing tests: `pytest tests/test_approve_*.py`.
   - Run full test suite with coverage: `make test-with-coverage`.
   - Verify 100% coverage for the modified lines in `openqabot/approver.py`.
   - Run `make tidy` and `make checkstyle` to ensure code quality.

## Acceptance Criteria Verification
- **AC1**: qem-bot only references failed openQA jobs which are actually not ok (i.e., it ignores superseded failures).
- **AC2**: qem-bot still clearly references blocking failures (if the latest run is still not ok, it will be reported).
