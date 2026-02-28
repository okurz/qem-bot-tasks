# Implementation Plan - Task 11: Reduce Log Verbosity

## Task Description
`011_bot_inc-sync-results_.log` is a full log of one "inc-sync-results" which is very big. We should reduce the verbosity of log entries, e.g. bundling the information about individual openQA job references together.

## Goal
Reduce the volume of log output during synchronization operations to make logs more readable and efficient, while preserving critical information in debug mode.

## Proposed Changes

### 1. openQA Job Fetching: `openqabot/openqa.py`
- Change the log level of `Fetching openQA jobs for ...` in `OpenQAInterface.get_jobs` from `INFO` to `DEBUG`. This avoids a log entry for every single API query.

### 2. Dashboard Syncing: `openqabot/syncres.py`
- Change the log level of `Syncing ... job ... Status ...` in `SyncRes.post_result` from `INFO` to `DEBUG`. This avoids spamming the log with every individual job being synced.

### 3. Summary Logging: `openqabot/subsyncres.py` & `openqabot/aggrsync.py`
- In `SubResultsSync.__call__`:
    - Add an `INFO` log message at the start: `Synchronizing results for {len(self.active)} active submissions...`.
    - After fetching all jobs, add an `INFO` log message: `Fetched {total_jobs} total jobs from openQA.`.
    - After posting results, add an `INFO` log message: `Successfully synced {len(results)} job results to the dashboard.`.
- In `AggregateResultsSync.__call__`:
    - Add similar summary logging for aggregate results synchronization.

## Verification Plan

### Automated Tests
- Run existing tests to ensure no regressions: `make test`.
- Verify coverage: `make test-with-coverage`.

### Manual Verification
- Run `qem-bot sub-sync-results --dry` and `qem-bot aggr-sync-results --dry` with and without the `--debug` flag.
- Verify that normal output (`INFO` level) provides concise summaries.
- Verify that detailed per-job output is still available when using `--debug`.
