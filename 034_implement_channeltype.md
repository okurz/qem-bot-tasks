# Implementation Plan - ChannelType for qem-bot

Implementing a `ChannelType` enum to replace hardcoded checks for "SLFO" and other channel types across the codebase.

## Proposed Changes

### 1. Define `ChannelType` Enum
In `openqabot/types/types.py`, add a `ChannelType` enum and update `Repos` to include it.

```python
from enum import Enum, auto

class ChannelType(Enum):
    UPDATES = auto()
    SLFO = auto()
    OPENSUSE = auto()
    UNKNOWN = auto()

class Repos(NamedTuple):
    product: str
    version: str
    arch: str
    product_version: str = ""
    channel_type: ChannelType = ChannelType.UNKNOWN
```

### 2. Update `Repos` logic
Update `Repos.compute_url` to use `self.channel_type` instead of `startswith` checks.

### 3. Implement Factory/Constructor logic
In `openqabot/types/submission.py`, update `_parse_channels` to set the correct `ChannelType` when creating `Repos` objects.

### 4. Refactor `Submission` and `Gitea` loader
*   Update `openqabot/loader/gitea.py` if it contains hardcoded SLFO logic.
*   Update `openqabot/types/submission.py` to use `ChannelType` in filtering/logic (e.g. `Submission.rev`).
*   Replace `project == "SLFO"` or `sub.project == "SLFO"` with `channel_type` checks where appropriate.

## Acceptance Criteria Verification
*   **AC1:** No more `channel.product == "SLFO"` or `self.product.startswith("SUSE:SLFO")`.
*   **AC2:** `GITEA_CHANNEL_PREFIXES` and `OPENSUSE_CHANNEL_PREFIXES` in `config.py` are already removed in previous preparatory work (PR #429).

## Verification Plan

### Automated Tests
*   Run existing tests: `make test`
*   Verify coverage: `make test-with-coverage`
*   Check maintainability: `make checkstyle`

### Manual Verification
*   Dry run `qem-bot.py` with SLFO and SMELT configurations to ensure URLs are still constructed correctly.
