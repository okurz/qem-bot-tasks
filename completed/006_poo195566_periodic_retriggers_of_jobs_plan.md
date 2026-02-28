# Execution Plan - Fix Periodic Retriggers of Jobs

## Issue Analysis
The issue "Periodic retriggers of jobs" is caused by multiple factors leading to the bot failing to recognize existing scheduled jobs or oscillating between states.

### 1. Unstable RepoHash (Oscillation)
The `REPOHASH` calculation in `openqabot/loader/repohash.py:get_max_revision` ignores repositories that return an HTTP error (e.g., 404), continuing with a partial set. This causes the calculated hash to fluctuate (Full Hash vs. Partial Hash) as repositories flap, leading to periodic retriggers.

### 2. Blindness to Existing Jobs (Regression)
Bisecting identified commit `38ec1e45` ("feat: disambiguate different kind of submissions") as a culprit. This commit introduced filtering by `type` (e.g., `?type=git`) when querying the dashboard for existing jobs (`is_scheduled_job`).
Tests with `reproduce.sh` show that this filtering causes the bot to miss existing jobs (likely created without a type or with a different type), leading to unnecessary triggers.

### 3. RepoHash Drift
Even with stable calculation, `REPOHASH` might change due to valid repository updates or configuration changes (e.g., `limit_archs`). To prevent retriggering when the underlying source commit (`SCM_INFO`) is identical, a fallback check is needed.

## Proposed Changes

### 1. Fix RepoHash Oscillation
*   **File:** `openqabot/loader/repohash.py`
*   **Change:** Raise `NoRepoFoundError` immediately if a repository request fails (non-200 status), instead of ignoring it. This prevents partial hash calculation.
*   **Tests:** Update `tests/test_repohash.py` to assert `NoRepoFoundError` is raised on error.

### 2. Fix Dashboard Query Blindness
*   **File:** `openqabot/types/submissions.py`
*   **Change:** In `is_scheduled_job`, remove the `type` parameter from the dashboard API request. This ensures the bot retrieves all existing jobs for the incident ID, regardless of how they were typed when created.

### 3. Add SCM_INFO Robustness
*   **File:** `openqabot/types/submissions.py` & `openqabot/types/submission.py`
*   **Change:** Update `is_scheduled_job` to check `SCM_INFO` (if available) as a fallback if `REPOHASH` mismatches.
*   **Change:** Pass `product` name to `is_scheduled_job` to correctly retrieve per-product SCM info.

## Verification
1.  **Unit Tests:** Run `make test` (specifically `tests/test_repohash.py` and `tests/test_submissions.py`).
2.  **Reproduction:** Run `./reproduce.sh`. It should show "already scheduled" for existing jobs (like `gitea:1668`) instead of "Would trigger", provided the existing jobs match either RepoHash or SCM_INFO.