# Task: Gitea PR priorities along with SMELT (poo#197348)

The goal of this task is to ensure that Gitea PR-based submissions show their correct priorities on the QEM Dashboard, similar to how SMELT incidents do. SMELT now provides priority information for Gitea PR-based submissions.

## Research Findings
- Gitea PR submissions are currently synced to the QEM Dashboard with a hardcoded priority of `0` in `openqabot/loader/gitea.py`.
- SMELT incidents are synced with their actual priority in `openqabot/smeltsync.py`.
- SMELT's GraphQL API can be queried by `incidentId`, which for Gitea-based submissions corresponds to the PR number.
- The QEM Dashboard handles sorting and display based on the `priority` field sent by `qem-bot`.

## Proposed Changes

### 1. Update `openqabot/loader/smelt.py`
- Add a new function `get_priority_from_smelt(incident_id: int) -> int` to fetch only the priority for a given incident/PR ID.
- Alternatively, modify `get_submission_from_smelt` to be more flexible or ensure it works for Gitea PR IDs.
- Ensure the GraphQL query is optimized if we only need the priority.

### 2. Update `openqabot/loader/gitea.py`
- In `make_submission_from_gitea_pr`, replace the hardcoded `priority: 0` with a call to fetch the priority from SMELT.
- Handle cases where SMELT might not have the information (fallback to 0).
- Consider performance: Fetching priority for each PR might be slow if done sequentially. However, `get_submissions_from_open_prs` already uses a `ThreadPoolExecutor`.

### 3. Verification Plan
- **Unit Tests:**
    - Add/update tests in `tests/test_loader_smelt.py` to verify fetching priority by ID.
    - Update `tests/test_loader_gitea_submissions.py` to verify that `make_submission_from_gitea_pr` correctly calls SMELT and populates the priority field.
- **Integration Tests:**
    - If possible, verify with a dry-run of `gitea-sync` and mock SMELT responses.
- **Coverage:**
    - Run `make test-with-coverage` to ensure 100% line coverage for the modified files.

## Execution Steps

1.  **Preparation:**
    - Create a reproduction/test case that shows a Gitea PR having priority 0.
2.  **Implementation - SMELT Loader:**
    - Implement `get_priority_from_smelt` in `openqabot/loader/smelt.py`.
    - Add unit tests for this new function.
3.  **Implementation - Gitea Loader:**
    - Integrate the SMELT priority fetch into `make_submission_from_gitea_pr`.
    - Update Gitea loader tests to mock the SMELT call and verify the priority is set.
4.  **Validation:**
    - Run all tests: `make test`.
    - Check style and types: `make tidy checkstyle typecheck-ty`.
    - Verify coverage: `make test-with-coverage`.
