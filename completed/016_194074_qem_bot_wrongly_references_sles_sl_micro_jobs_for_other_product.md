# Execution Plan: Fix Wrong openQA Job References in Increment Approver

## Problem Description
`qem-bot` incorrectly associates openQA jobs with OBS requests for different products. For example, SLES-specific failures are being applied to SL-Micro requests and vice versa. This leads to `AmbiguousApprovalStatusError` (after a recent "safeguard" PR) or incorrect approvals/disapprovals.

The root cause seems to be a combination of:
1. `isos/job_stats` openQA API query not being specific enough (missing `product` filter).
2. `IncrementConfig` being too broad (`version: any`, `flavor: any`).
3. Potential overlap in `BuildInfo` discovery or `params` generation.
4. If a request ID is specified via CLI, it is processed against ALL configured products regardless of the request's actual target project.

## Proposed Changes

### 1. Investigation and Reproduction
- Create a reproduction unit test in `tests/test_issue_194074.py`.
- Mock OBS project file listings to return builds for two different products (e.g., SLES and SL-Micro) in their respective projects.
- Mock openQA `isos/job_stats` to return specific jobs for each.
- Simulate the `IncrementApprover.__call__` loop and verify if jobs leak across requests.

### 2. Enhancing openQA Query Parameters
- Modify `openqabot/types/increment.py`: Ensure `BuildInfo` and `ApprovalStatus` are used correctly.
- Modify `openqabot/incrementapprover.py`:
    - In `make_scheduling_parameters`, include `PRODUCT: build_info.product` in the `base_params`.
    - In `request_openqa_job_results`, add `product: p.get("PRODUCT")` to the `query_params` sent to openQA.
    - This ensures that openQA results are filtered by product, even if distri/version/flavor/arch/build are identical (though they should normally differ).

### 3. Improving Configuration Filtering
- In `openqabot/loader/buildinfo.py`:
    - Ensure that if `config.version` or `config.flavor` are NOT "any", they are strictly matched against the parsed values from the build filename. (It seems to do this, but double-check).
- In `openqabot/incrementapprover.py`:
    - In `__call__`, if `self.args.request_id` is specified, add a check to only process the `config` whose `build_project()` matches the request's target project. This prevents one specific request from being evaluated against all products.

### 4. Refining Error Handling and Logging
- Ensure `AmbiguousApprovalStatusError` provides enough context (which job ID, which requests).
- Improve log messages in `handle_approval` to be even more specific about which product/build is being checked for which request (partially done in previous PRs).

## Verification Plan

### Automated Tests
- Run existing tests: `make test`
- Run the new reproduction test: `pytest tests/test_issue_194074.py`
- Run integration-like tests if possible.

### Manual Verification
- Dry-run `qem-bot increment-approve` with a config file containing both SLES and SL-Micro and verify the logs show correct job associations.
- Test with `-r <request_id>` and verify it only processes the relevant product.

## Deployment
- The changes are in the `qem-bot` codebase.
- No database migrations or external service changes required.
- Requires openQA to respect the `product` parameter in `isos/job_stats` (most openQA instances do if it's a setting in the jobs).
