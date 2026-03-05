# Implementation Plan - Task 12: Further Reduce Log Verbosity

## Goal
Reduce the high volume of INFO level log entries for purely operational chatter and configuration skipping without losing valuable debugging information. Group repetitive information like 'already scheduled' items.

## Proposed Changes

### 1. `openqabot/loader/qem.py`
- Change `log.info("Fetching settings for submission %s:%s", ...)` to `log.debug` (line 147). This creates an entry for every submission, but overall processing summaries are already logged.

### 2. `openqabot/loader/config.py`
- Change `log.info("Configuration skipped: File %s missing required setting %s", path, e)` to `log.debug` (line 176). This logs missing "aggregate" keys for non-aggregate bot profiles, generating unnecessary spam.
- Note: Keep `log.info("Configuration skipped: File %s is empty", path)` and invalid format logs as INFO since they indicate possible configuration errors.
- Update `test_load_one_metadata_missing_settings` in `tests/test_loader_config.py` if it relies on INFO level logging for these specific messages (though missing `aggregate` specifically is a `KeyError` in `_parse_product`).

### 3. `openqabot/types/submissions.py`
- Address the high volume of "already scheduled" logs by grouping them.
- Instead of logging immediately in `should_skip` or tracking states internally across the call stack, add a class-level dictionary or an instance-level attribute during `__call__` to track scheduled jobs, and log the summary after processing.
- However, since `should_skip` is called individually for each flavor/arch combination during `process_sub_context`, modifying `Submissions.__call__` to collect skipping reasons might involve significant refactoring.
- *Alternative grouping approach:* Collect skipped/already-scheduled info in a dictionary during `__call__`, then log summary per submission ID at the end of `__call__`. 
- Actually, `__call__` processes list of submissions for a given configuration. So we can aggregate by Submission across the loops:
```python
        scheduled_summary = defaultdict(list)
        
        # ... inside loop where should_skip happens
        if not cfg.ignore_onetime and self.is_scheduled_job(cfg.token, ctx, self.settings["VERSION"], submission_type=sub.type):
            scheduled_summary[sub].append(f"{flavor} on {arch}")
            return True
```
Then log at the end: `log.info("Submission %s already scheduled for %s", sub, ", ".join(combos))`

## Steps
1. Create isolated commits for:
   a. "Fetching settings" -> DEBUG
   b. "Configuration skipped: ... missing required setting" -> DEBUG
2. Refactor `submissions.py` to aggregate "already scheduled" messages.
3. Test modifications and ensure `make test` and `make test-with-coverage` pass.
