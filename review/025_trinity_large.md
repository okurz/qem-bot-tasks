# Task 025: Fix Wrong openQA Jobs Referenced in sub-approve

## Issue Reference
- **ID**: 193690
- **Project**: QA (public)
- **Tracker**: action
- **Status**: Blocked
- **Priority**: Normal
- **Author**: nicksinger
- **Assignee**: okurz
- **Fixed Version**: Ready
- **Parent**: 180629
- **Subject**: [tools][infra][qem-bot] Wrong openQA job runs referenced in qem-bot `inc-approve`-runs size:S

## Problem Description

From Slack observation: The qem-bot incorrectly references openQA job runs in `inc-approve` operations. Specifically:

- A job (t20256065) was reported as failed but is actually green
- The job is a clone of another job (t20252358) that actually failed
- The bot needs to correctly identify and reference the most recent scenario reference

## Acceptance Criteria
- **AC1**: qem-bot only references failed openQA jobs which are actually not ok (failed, incomplete, etc.)
- **AC2**: qem-bot still clearly references blocking failures

## Investigation Steps

### 1. Locate the Source Code
- Start with `openqabot/approver.py` at line 288 where the log message "Found failed, not-ignored ..." is sent
- Examine how job references are retrieved and processed

### 2. Understand Job Reference Logic
- Identify how openQA jobs are looked up for a given incident
- Determine if the bot is using outdated or cloned job references
- Check if the bot properly handles job status and force-result scenarios

### 3. Verify Current Behavior
- Reproduce the issue locally using the same incident data
- Confirm that the bot references the wrong job (t20256065 instead of t20252358)
- Test with force-result soft-failed scenarios

## Implementation Plan

### Phase 1: Code Analysis
1. **Examine `approver.py`** (tasks/025_poo193690_wrong_openqa_jobs_referenced_in_sub_approve.json: line 288)
2. **Trace job lookup logic** - identify functions that retrieve openQA job references
3. **Analyze status checking** - verify how job statuses are evaluated
4. **Review force-result handling** - check how soft-failed jobs are processed

### Phase 2: Fix Implementation
1. **Update job reference logic** to use the most recent scenario reference
2. **Improve status validation** to ensure only truly failed jobs are referenced
3. **Enhance force-result handling** for soft-failed jobs
4. **Add logging improvements** for better debugging

### Phase 3: Testing
1. **Create test cases** for the specific scenario (cloned jobs, force-result)
2. **Verify AC1** - only truly failed jobs are referenced
3. **Verify AC2** - blocking failures are still clearly referenced
4. **Test edge cases** - old jobs, force-result scenarios, etc.

## Files to Modify

1. `openqabot/approver.py` - Core logic for job reference and status checking
2. `tests/test_approver.py` - Add test cases for the new logic
3. `tests/conftest.py` - Add test fixtures if needed

## Testing Strategy

### Unit Tests
- Test job reference resolution with cloned jobs
- Test force-result soft-failed job handling
- Test status validation logic
- Test edge cases (old jobs, missing jobs, etc.)

### Integration Tests
- Run full `inc-approve` with test data
- Verify log messages are accurate
- Confirm only correct jobs are referenced

## Risk Assessment

- **Low Risk**: The changes are localized to job reference logic
- **Medium Risk**: Force-result handling might affect other scenarios
- **High Risk**: Breaking existing functionality if not properly tested

## Rollback Plan

- Keep original code commented with detailed explanations
- Use feature flags if possible for gradual rollout
- Have comprehensive test coverage before deployment

## Success Criteria

- No incorrect job references in `inc-approve` runs
- All acceptance criteria are met
- Test coverage for new logic is 100%
- No regressions in existing functionality

## Timeline Estimate

- **Investigation**: 2-3 hours
- **Implementation**: 4-6 hours
- **Testing**: 3-4 hours
- **Review & Refinement**: 2-3 hours

**Total Estimate**: 11-16 hours