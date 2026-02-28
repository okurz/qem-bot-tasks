# Plan to split large test files

This plan outlines the process of splitting the largest test files in `tests/` into smaller, more maintainable modules. This will improve readability and make it easier for developers and automated tools to work with the codebase.

## Files to be split

Based on the initial analysis, the following files are the primary candidates for splitting:

*   `tests/test_submissions.py` (DONE)
*   `tests/test_approve.py` (DONE)
*   `tests/test_incrementapprover.py` (DONE)
*   `tests/test_loader_gitea.py` (DONE)

## Splitting Strategy

### 1. `tests/test_submissions.py`

Split into:
*   `tests/test_submissions_call.py`
*   `tests/test_submissions_handle.py`
*   `tests/test_submissions_gitea.py`
*   `tests/test_submissions.py` (trimmed)
*   `tests/fixtures/submissions.py` (MockSubmission)

### 2. `tests/test_approve.py`

Split into:
*   `tests/test_approve_scenarios.py`
*   `tests/test_approve_unblock.py`
*   `tests/test_approve_obs.py`
*   `tests/test_approve_git.py`
*   `tests/test_approve_helpers.py`
*   `tests/approve_fixtures.py` (Shared fixtures)

### 3. `tests/test_incrementapprover.py`

Split into:
*   `tests/test_incrementapprover_scenarios.py`
*   `tests/test_incrementapprover_obs.py`
*   `tests/test_incrementapprover_build_info.py`
*   `tests/test_incrementapprover_diff.py`
*   `tests/test_incrementapprover_helpers.py`
*   `tests/incrementapprover_fixtures.py` (Shared fixtures)

### 4. `tests/test_loader_gitea.py`

Split into:
*   `tests/test_loader_gitea_prs.py`
*   `tests/test_loader_gitea_submissions.py`
*   `tests/test_loader_gitea_build_results.py`
*   `tests/test_loader_gitea_archs.py`
*   `tests/test_loader_gitea_helpers.py`

## Implementation Steps

1.  [x] Create the new test files as outlined above.
2.  [x] Move the relevant test functions and helper classes/functions to the new files.
3.  [x] Update imports in all affected files.
4.  [x] Run all tests to ensure that no regressions have been introduced.
5.  [x] Remove the original large test files once the new files are in place and all tests pass.
6.  [x] Update this plan with the analysis of `test_approve.py` and `test_incrementapprover.py`.
7.  [x] Repeat the process for the other identified files.