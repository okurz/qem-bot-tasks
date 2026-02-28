# Execution Plan: Fix Wrong openQA Jobs Referenced in inc-approve

## Issue Summary
The qem-bot incorrectly references old/cloned openQA jobs instead of the most recent job in a scenario chain. For example:
- Job t20256065 is reported as failed
- But t20256065 is actually a **clone** of t20252358 (which actually failed)
- The bot should reference the most recent job in the clone chain

## Root Cause
The bot retrieves job results from QEM Dashboard but doesn't account for openQA job clones. When a job is cloned in openQA, the clone (t20256065) can have a different result than the original (t20252358). The bot needs to follow the clone chain to find the most recent job reference.

## Affected Components
- `openqabot/approver.py`: Lines 282-325 (is_job_passing, mark_jobs_as_acceptable_for_submission, is_job_acceptable)
- `openqabot/loader/qem.py`: Functions that retrieve job results (get_submission_results, get_aggregate_results)
- `openqabot/loader/qem.py`: JobAggr NamedTuple may need enhancement

## Acceptance Criteria
- **AC1:** qem-bot only references failed openQA jobs which are actually not ok (failed, incomplete, etc.)
- **AC2:** qem-bot still clearly references blocking failures

## Implementation Plan

### Phase 1: Research and Understanding
1. [ ] Examine how openQA job clones work (check OpenQAInterface class in openqa.py)
2. [ ] Understand how job results are retrieved from QEM Dashboard API
3. [ ] Identify where clone information is available in openQA API responses
4. [ ] Look at existing clone handling in the codebase (if any)

### Phase 2: Solution Design
1. [ ] Determine where to handle clone resolution:
   - Option A: In approver.py when checking job results
   - Option B: In loader/qem.py when fetching job data
   - Option C: In OpenQAInterface when retrieving job details
2. [ ] Design the clone resolution logic:
   - For each failed job, check if it's a clone
   - If it's a clone, find the original/most recent job in the chain
   - Use the result of the most recent job for approval decisions
3. [ ] Ensure logging still references the correct blocking job

### Phase 3: Implementation
1. [ ] Add clone detection functionality to OpenQAInterface or create helper
2. [ ] Modify job result processing to handle clones
3. [ ] Update the log message to show correct job reference
4. [ ] Ensure backward compatibility with existing functionality

### Phase 4: Testing
1. [ ] Write/update unit tests for clone handling
2. [ ] Verify existing tests pass
3. [ ] Test with mock data representing clone scenarios
4. [ ] Run `make test-with-coverage` and verify 100% coverage for modified files

### Phase 5: Validation
1. [ ] Run `make tidy` for code formatting
2. [ ] Run `make checkstyle` for style checks
3. [ ] Run `make typecheck-ty` for type checking
4. [ ] Verify all acceptance criteria are met

## Key Code Locations to Modify
- `openqabot/approver.py:282-325` - Job result checking logic
- `openqabot/loader/qem.py:180-192` - get_submission_results function
- `openqabot/loader/qem.py:239-251` - get_aggregate_results function

## References
- Issue: POOL #193690
- Slack discussion: https://suse.slack.com/archives/C02CANHLANP/p1765446174817959
- Related GitLab job: https://gitlab.suse.de/qa-maintenance/bot-ng/-/jobs/5724923
