# Task: Adapt openQA job priority based on SMELT incident priority

## Problem
Currently, `qem-bot` uses a fixed base priority (50) for openQA jobs, with some minor adjustments for EMU and "Minimal" flavors. It does not take into account the `priority` field from SMELT incidents. Urgent incidents with high priority in SMELT should result in openQA jobs with higher priority (lower `_PRIORITY` value).

## Proposed Changes

### 1. openqabot/config.py
Add a new configuration variable for the priority scale factor.
```python
BASE_PRIO = 50
PRIORITY_SCALE = int(os.environ.get("QEM_BOT_PRIORITY_SCALE", 20))
```

### 2. openqabot/types/submissions.py
Update `get_priority` to incorporate `sub.priority` divided by `PRIORITY_SCALE`.

```python
    def get_priority(self, ctx: SubContext) -> int | None:
        sub, flavor, data = ctx.sub, ctx.flavor, ctx.data
        if delta_prio := data.get("override_priority", 0):
            delta_prio -= 50
        else:
            delta_prio = 5 if flavor.endswith("Minimal") else 10
            if sub.emu:
                delta_prio = -20
            if sub.priority:
                delta_prio -= sub.priority // PRIORITY_SCALE
        
        return BASE_PRIO + delta_prio if delta_prio else None
```

### 3. openqabot/types/aggregate.py
Update `Aggregate` to also use incident priority scaled by `PRIORITY_SCALE`.

In `Aggregate.create_full_post`:
```python
        if max_prio := max(
            (s.priority for s in chain.from_iterable(data.test_submissions.values()) if s.priority is not None),
            default=0,
        ):
            full_post["openqa"]["_PRIORITY"] = BASE_PRIO - (max_prio // PRIORITY_SCALE)
```

### 4. Verification
- Update `tests/test_submissions_handle.py` and `tests/test_aggregate.py` to match the new scaled priority calculation.
- Run `make tidy checkstyle typecheck-ty test-with-coverage` to ensure everything is correct.

## Implementation Steps
1.  [x] Modify `openqabot/config.py` (Add BASE_PRIO, now need to add PRIORITY_SCALE)
2.  [ ] Modify `openqabot/types/submissions.py` (Update with PRIORITY_SCALE)
3.  [ ] Modify `openqabot/types/aggregate.py` (Update with PRIORITY_SCALE)
4.  [ ] Update `tests/test_submissions_handle.py`
5.  [ ] Update `tests/test_aggregate.py`
6.  [ ] Validate with full test suite.