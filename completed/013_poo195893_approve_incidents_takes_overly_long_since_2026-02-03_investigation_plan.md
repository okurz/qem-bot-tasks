# Execution Plan - Problem Investigation: Approve Incidents Takes Overly Long

This plan outlines the steps to investigate why the `sub-approve` (formerly `inc-approve`) process has been taking significantly longer since 2026-02-03.

## Problem Description

- **Symptom:** The `inc-approve` job duration increased from ~45 seconds (last good) to ~2 hours 10 minutes (first bad).
- **Observation:** The "first bad" log contains nearly 60,000 entries of "Ignoring failed aggregate" or "Ignoring failed aggregate job".
- **Hypothesis:** Certain submissions (e.g., smelt:42544, 42547, 42546, 42549, 42543, 42558) have an abnormally large number of aggregate jobs associated with them in the QEM Dashboard, causing `Approver` to perform an excessive number of openQA API requests to check for "older passing jobs".

## Investigation Tasks

### 1. Quantitative Analysis of Logs
- [ ] Count total number of `is_job_acceptable` calls per submission in the bad log.
- [ ] Identify if there's a specific "build" or "job setting" that has the majority of the failures.

### 2. Dashboard Data Verification
- [ ] Verify the content of `api/jobs/update/{job_aggr_id}` for the most problematic job settings identified in the logs.
- [ ] Confirm if the number of jobs returned by the dashboard for these settings is indeed in the thousands.
- [ ] Investigate why these settings have so many jobs (external to `qem-bot` but affects its performance).

### 3. Code Analysis & Optimization Opportunities
- [ ] **openqabot/approver.py:**
    - [ ] Review `was_ok_before` and `was_older_job_ok` for potential further caching or early exit conditions.
    - [ ] Evaluate if we should limit the number of jobs processed per `job_aggr_id` (e.g., only check the most recent N jobs).
    - [ ] Check if `lru_cache` sizes (currently 512 for `was_ok_before` and 256 for `get_single_job`) are sufficient given the observed scale.
- [ ] **openqabot/openqa.py:**
    - [ ] Check if `get_older_jobs` can be optimized or if its results can be shared across multiple calls if the `failed_job_id`s are close to each other.

### 4. Reproduction & Testing
- [ ] Create a unit test in `tests/test_approve_scenarios.py` that mocks a submission with thousands of aggregate jobs to reproduce the slow behavior (and verify any fix).

## Proposed Fixes (Pending Investigation)

1. **Limit Job Processing:** In `Approver.get_jobs`, only process the latest few jobs for each setting instead of all of them.
2. **Increase Cache Sizes:** Increase `lru_cache` for openQA API calls to handle larger batches of jobs.
3. **Short-circuit `was_ok_before`:** If a specific submission/setting is already known to have failed or passed, avoid redundant openQA checks.

## Ticket Reference
- @tasks/013_poo195893_approve_incidents_takes_overly_long_since_2026-02-03.json
