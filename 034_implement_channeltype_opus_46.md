# Execution Plan: Implement ChannelType Enum (poo#197357)

Ticket: https://progress.opensuse.org/issues/197357

## Current State

Branch `feature/034_implement_channeltype` contains preparatory refactoring
(5 commits on top of `origin/main`). The prior attempt on branch
`feature/034_implement_channeltype_1st_attempt_unexpected_behavioural_change_still_if_else`
added a single commit `165612d` that introduced `ChannelType` but caused
unexpected behavioural changes — specifically in `Submission.rev()` where the
`project == "SLFO"` guard was broadened, changing filtering semantics.

### Hardcoded checks to replace (AC1)

| Location | Current check | Line |
|---|---|---|
| `types/types.py` `Repos.compute_url` | `project == "SLFO" or self.product.startswith("SUSE:SLFO")` | 30 |
| `types/types.py` `Repos.compute_url` | `self.product.startswith("openSUSE")` | 42 |
| `types/submission.py` `_parse_channels` | `r.startswith("SUSE:Updates")` | 72 |
| `types/submission.py` `_parse_channels` | `r.startswith("SUSE:SLFO")` | 78 |
| `types/submission.py` `rev` | `project == "SLFO"` | 202 |
| `types/submissions.py` `make_repo_url` | `chan.product == "SUSE:SLFO"` | 126 |
| `types/submissions.py` `get_matching_channels` | `channel.product == "SLFO"` | 132 |
| `types/submissions.py` `add_metadata_urls` | `sub.project == "SLFO"` | 235 |
| `types/aggregate.py` `_get_repo_url` | `product.startswith("openSUSE")` | 114 |
| `loader/gitea.py` `compute_repo_url_for_job_setting` | `project="SLFO"` (literal arg) | 149 |

### Constants to remove (AC2)

`GITEA_CHANNEL_PREFIXES` and `OPENSUSE_CHANNEL_PREFIXES` do not exist in the
current codebase — already absent. AC2 is satisfied.

## Lessons from Prior Attempt (165612d)

1. **Behavioural change in `Submission.rev()`**: The prior attempt removed the
   `project == "SLFO"` guard and replaced it with a per-repo `ChannelType`
   check. This changed filtering semantics — non-SLFO repos in a mixed list
   would now be filtered differently. **Fix**: keep the `project` parameter
   guard intact; use `ChannelType` only for the per-repo `startswith` checks.
2. **`add_metadata_urls` changed from `sub.project` to channel inspection**:
   `sub.project == "SLFO"` was replaced with
   `any(get_channel_type(c.product) == ChannelType.SLFO for c in sub.channels)`.
   This is a semantic change (project-level vs channel-level). **Fix**: use
   `sub.type == "git"` which is the actual intent (Gitea PRs have `type="git"`,
   SMELT incidents have `type="SMELT"`), or keep `sub.project` comparison using
   the enum on `sub.project`.
3. **Good ideas to keep**: `ChannelType` enum, `get_channel_type()` helper with
   mapping table, `ProdVer.from_issue_channel()` factory.

## Implementation Steps

### Step 1: Define `ChannelType` enum and `get_channel_type()` helper

**File**: `openqabot/types/types.py`

```python
from enum import Enum, auto

class ChannelType(Enum):
    UPDATES = auto()
    SLFO = auto()
    OPENSUSE = auto()

_CHANNEL_PREFIX_MAP = {
    "SUSE:SLFO": ChannelType.SLFO,
    "SLFO": ChannelType.SLFO,
    "openSUSE": ChannelType.OPENSUSE,
}

def get_channel_type(product: str) -> ChannelType:
    return next(
        (v for k, v in _CHANNEL_PREFIX_MAP.items() if product.startswith(k)),
        ChannelType.UPDATES,
    )
```

No `UNKNOWN` variant — the default is `UPDATES` which matches the existing
behaviour (unrecognized channels are silently ignored in `_parse_channels` and
all URL construction falls through to the SUSE Updates path).

### Step 2: Add `ProdVer.from_issue_channel()` factory

**File**: `openqabot/types/types.py`

Centralize the `issue.split(":")`/`split("#")` parsing that is duplicated in
`Submissions.product_version_from_issue_channel()` and
`Aggregate.normalize_repos()`.

```python
class ProdVer(NamedTuple):
    ...
    @classmethod
    def from_issue_channel(cls, issue: str) -> ProdVer:
        channel_parts = issue.split(":")
        version_parts = channel_parts[1].split("#")
        return cls(channel_parts[0], version_parts[0],
                   version_parts[1] if len(version_parts) > 1 else "")
```

Update call sites:
- `Submissions.product_version_from_issue_channel()` → delegate to
  `ProdVer.from_issue_channel()`
- `Aggregate.normalize_repos()` → use `ProdVer.from_issue_channel(value)`

### Step 3: Replace hardcoded checks in `Repos.compute_url()`

**File**: `openqabot/types/types.py`

Replace:
```python
if project == "SLFO" or self.product.startswith("SUSE:SLFO"):
```
With:
```python
if get_channel_type(self.product) == ChannelType.SLFO or project == "SLFO":
```

Replace:
```python
if self.product.startswith("openSUSE"):
```
With:
```python
if get_channel_type(self.product) == ChannelType.OPENSUSE:
```

**Note**: The `project == "SLFO"` fallback must remain in `compute_url` because
`loader/gitea.py:compute_repo_url_for_job_setting` passes `project="SLFO"`
explicitly for repos that already have `product="SUSE:SLFO"`. Removing it
would break nothing today but the fallback is a safety net.

### Step 4: Replace hardcoded checks in `Submissions`

**File**: `openqabot/types/submissions.py`

- `make_repo_url`: replace `chan.product == "SUSE:SLFO"` with
  `get_channel_type(chan.product) == ChannelType.SLFO`
- `get_matching_channels`: replace `channel.product == "SLFO"` with
  `get_channel_type(channel.product) == ChannelType.SLFO`
- `add_metadata_urls`: replace `sub.project == "SLFO"` with
  `sub.type == "git"` (this is the actual semantic intent — Gitea submissions
  have `type="git"`, SMELT have `type="SMELT"`). If this is too broad a
  semantic change, alternatively use
  `get_channel_type(sub.project) == ChannelType.SLFO` which is 1:1 equivalent.

### Step 5: Replace hardcoded checks in `Submission`

**File**: `openqabot/types/submission.py`

- `_parse_channels`: replace `r.startswith("SUSE:Updates")` with
  `get_channel_type(r) == ChannelType.UPDATES` — **BUT** this would misclassify
  unknown prefixes as UPDATES. Instead, keep `startswith` for the parsing
  dispatch since `_parse_channels` explicitly branches on known prefixes and
  silently ignores unknown ones. Replace with:
  ```python
  ct = get_channel_type(r)
  if ct == ChannelType.UPDATES:
      ...
  elif ct == ChannelType.SLFO:
      ...
  ```
  This works because `get_channel_type` maps everything that doesn't match
  SLFO or openSUSE to UPDATES, and unknown channels (which should be ignored)
  would also map to UPDATES. **However**, this changes behaviour: channels
  like `SUSE:Maintenance:...` would now enter the UPDATES branch and fail
  parsing. **Decision**: keep `startswith("SUSE:Updates")` for `_parse_channels`
  since this is a *parsing* dispatch (structural), not a *type* dispatch
  (semantic). The enum is for downstream type checks, not for parsing raw
  strings.

- `rev`: replace `project == "SLFO"` with
  `get_channel_type(project) == ChannelType.SLFO` — **but keep the `project`
  parameter guard** intact. Do NOT change the filtering logic. The prior attempt
  broke this by broadening the filter.

### Step 6: Replace hardcoded check in `Aggregate`

**File**: `openqabot/types/aggregate.py`

- `_get_repo_url`: replace `product.startswith("openSUSE")` with
  `get_channel_type(product) == ChannelType.OPENSUSE`

### Step 7: Write tests

**File**: `tests/test_types.py` (new)

Tests for:
- `get_channel_type()` with all three channel types and edge cases
- `ProdVer.from_issue_channel()` with and without product version
- `Repos.compute_url()` for SLFO, openSUSE, and UPDATES paths

Ensure 100% line coverage for all modified files.

### Step 8: Verification

Run in order:
1. `make tidy` — format
2. `make checkstyle` — lint + radon + vulture
3. `make typecheck-ty` — type check
4. `make test` — all tests pass with full coverage
6. Verify radon MI >= 20 for all modified files

## Files Modified

| File | Changes |
|---|---|
| `openqabot/types/types.py` | Add `ChannelType`, `get_channel_type()`, `ProdVer.from_issue_channel()` |
| `openqabot/types/submission.py` | Import `ChannelType`/`get_channel_type`; update `rev()` |
| `openqabot/types/submissions.py` | Import + update `make_repo_url`, `get_matching_channels`, `add_metadata_urls`, delegate `product_version_from_issue_channel` |
| `openqabot/types/aggregate.py` | Import + update `_get_repo_url`, `normalize_repos` |
| `tests/test_types.py` | New test file for `ChannelType`, `get_channel_type`, `ProdVer.from_issue_channel` |

## Decisions Log

| Decision | Rationale |
|---|---|
| No `UNKNOWN` variant | Default to `UPDATES` matches existing fallthrough behaviour |
| Keep `startswith` in `_parse_channels` | Parsing dispatch is structural, not type-based; enum is for downstream |
| Keep `project` parameter in `rev()` | Removing it caused behavioural change in prior attempt |
| `add_metadata_urls`: prefer `sub.type == "git"` over channel inspection | Semantically correct — the URL format depends on submission source, not channel type; falls back to `get_channel_type(sub.project)` if too risky |
| `project="SLFO"` literal in `compute_repo_url_for_job_setting` stays | This is a Gitea-specific caller; the `project` param in `compute_url` is a routing hint, not a channel type; removing it requires broader refactoring |
| `_parse_channels` ignores openSUSE channels | Existing behaviour; openSUSE channels only appear in aggregate `test_issues` configs, not in raw SMELT/Gitea channel strings |

## Risk Assessment

- **Low risk**: Steps 1-2 (additive only, no behaviour change)
- **Low risk**: Steps 3, 6 (1:1 equivalent replacements)
- **Medium risk**: Step 4 (`add_metadata_urls` semantic change if using `sub.type`)
- **Low risk**: Step 5 (`rev()` — keep guard intact, only replace `startswith`)
- **Mitigation**: Full test suite + coverage verification after each step
