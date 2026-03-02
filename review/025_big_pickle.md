# Execution Plan: Fix Wrong openQA Jobs Referenced in inc-approve

## Issue Reference
- **Redmine Issue**: #193690
- **Project**: QA (public)
- **Tracker**: action
- **Priority**: Normal (High priority for blocking updates)
- **Assignee**: okurz

## Problem Summary
The qem-bot `inc-approve` command is incorrectly referencing old/cloned openQA jobs instead of the most recent reference of a scenario. This causes false negatives where the bot reports a job as failed when it's actually green in openQA.

### Root Cause
- openQA job clones (e.g., `t20256065` is a clone of `t20252358`)
- The bot references the old job ID instead of the current/latest job
- Job t20252253 blocks (despite being a force-result soft-failed) but shouldn't

## Acceptance Criteria
1. **AC1**: qem-bot only references failed openQA jobs which are actually not ok (failed, incomplete, etc.)
2. **AC2**: qem-bot still clearly references blocking failures

## Investigation Steps

### Step 1: Understand the Code Flow
- **Start Point**: `openqabot/approver.py` line ~288
  - Log message: "Found failed, not-ignored …"
- Investigate how jobs are looked up and referenced
- Find where the job clone relationship is handled (or missing)

### Step 2: Identify Affected Code Paths
- Locate all places where openQA job IDs are fetched/referenced
- Check if clone relationships are being considered
- Review the logic that determines if a job is "failed" or "blocking"

### Step 3: Understand openQA Clone Behavior
- Research how openQA handles job clones
- Determine how to get the most recent job reference for a scenario
- Identify the correct API call to get current job status

## Implementation Plan

### Phase 1: Code Investigation
- [ ] Read `openqabot/approver.py` around line 288
- [ ] Trace the job lookup logic
- [ ] Identify where job clone info should be fetched
- [ ] Check existing tests for approver logic

### Phase 2: Solution Design
- [ ] Determine how to resolve job clone to current reference
- [ ] Design fix to use latest job reference
- [ ] Ensure AC1 and AC2 are met

### Phase 3: Implementation
- [ ] Implement fix to fetch correct job reference
- [ ] Update logic to check current job status
- [ ] Ensure backward compatibility

### Phase 4: Testing
- [ ] Write or adapt tests to cover clone scenario
- [ ] Run existing test suite
- [ ] Verify with coverage (100% for modified files)

## Notes
- Related Slack thread: https://suse.slack.com/archives/C02CANHLANP/p1765446174817959
- Example false negative: https://gitlab.suse.de/qa-maintenance/bot-ng/-/jobs/5724923
- Affected job example: t20256065 (appears failed in bot, green in openQA)
- Clone source: t20252358 (actual failure)
