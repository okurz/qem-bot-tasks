# Plan to Fix Empty INCIDENT_REPO Regression

## Problem
A regression in commit `65866c63` caused some openQA tests to be scheduled with an empty `INCIDENT_REPO` variable. This happens when the filtering logic in `_handle_submission` results in an empty `repos` set because none of the matched channels have a `product_version` matching the expected `version`.

Example from `tasks/job.log` for incident 42229:
```
'VERSION': '15-SP7', ..., 'INCIDENT_REPO': ''
```

## Analysis
The current logic in `openqabot/types/submissions.py`:
```python
version = self.product_version or self.settings["VERSION"]
...
repos = {c for matched in matches.values() for c in matched if c.product_version == version}
settings["INCIDENT_REPO"] = ",".join(sorted(self._make_repo_url(sub, chan) for chan in repos))
```
If `c.product_version == version` is never true, `repos` is empty and `INCIDENT_REPO` becomes `""`.

Commit `65866c63` intended to prevent "non-sensible product+version combinations" by filtering channels based on the product version. However, it seems it's too restrictive or failing to find a match when it should.

## Proposed Fix
If the filtered `repos` set is empty, we should fallback to using all matched channels (the behavior before commit `65866c63`), or at least ensure we don't schedule with an empty repo string if we have matches.

Actually, if we have matches in `matches`, we should use them. Commit `65866c63` filtered them further.

Revised logic:
1. Calculate `repos` with the version filter.
2. If `repos` is empty, use all channels from `matches`.
3. If it's still empty, it should have been skipped by `_should_skip`, but we can add an extra check.

However, the user wants to keep the "intended fix of 65866c63 in place". The intended fix was to prevent WRONG combinations. If NO combination matches the version, then maybe we shouldn't even be here for this product? But if we ARE here, and we have matches, scheduling with empty repo is definitely wrong.

Wait, `matches` already filtered channels by `arch` and `version` (via `_get_matching_channels`).

Let's look at `_get_matching_channels`:
```python
    def _get_matching_channels(self, sub: Submission, channel: ProdVer, arch: str) -> list[Repos]:
        if channel.product == "SLFO":
            ...
        f_channel = Repos(channel.product, channel.version, arch, channel.product_version)
        return [f_channel] if f_channel in sub.channels else []
```
For non-SLFO, it checks `f_channel in sub.channels`. `f_channel` has `channel.product_version`.

In the log for incident 42229, `VERSION` is `15-SP7`.
If `self.product_version` is None and `self.settings["VERSION"]` is `15-SP7`, then `version` is `15-SP7`.
The channels in `sub.channels` for incident 42229 might have a different `product_version` string (e.g. `None` or something else) even if they match otherwise.

If `repos` is empty, we should probably log a warning and fallback to all matched channels to avoid breaking things, while still preferring the filtered ones.

## Implementation
Modify `openqabot/types/submissions.py`:
```python
        repos = {c for matched in matches.values() for c in matched if c.product_version == version}
        if not repos:
            repos = {c for matched in matches.values() for c in matched}
```

## Verification
1. Add a test case to `tests/test_submissions.py` that reproduces this scenario (where version doesn't match `product_version` but we have matches).
2. Run `make test`.
