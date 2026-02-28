# Task 007: More CLI Parameters and Filters

## Goal
Improve the flexibility of `qem-bot` by:
1. Exposing configuration parameters from `openqabot/config.py` (those with environment variables) as global CLI arguments.
2. Adding filtering parameters (`--arch`, `--flavor`, `--product`, `--version`) to scheduling subcommands (`full-run`, `submissions-run`, `updates-run`) for easier testing and targeted runs.

## Proposed Changes

### 1. Refactor Configuration Access
To allow runtime overrides of global configuration variables, modules should import the `config` module instead of individual names.

- **Action**: Update all files that use `from .config import ...` or `from openqabot.config import ...` to use `from . import config` or `import openqabot.config as config`.
- **Target Files**:
    - `openqabot/args.py`
    - `openqabot/dashboard.py`
    - `openqabot/smeltsync.py`
    - `openqabot/repodiff.py`
    - `openqabot/syncres.py`
    - `openqabot/amqp.py`
    - `openqabot/types/submission.py`
    - `openqabot/types/aggregate.py`
    - `openqabot/types/submissions.py`
    - `openqabot/loader/smelt.py`
    - `openqabot/loader/incrementconfig.py`
    - `openqabot/loader/repohash.py`
    - `openqabot/loader/gitea.py`
    - `openqabot/loader/qem.py`

### 2. Add Configuration CLI Parameters
Add global arguments to `get_parser` in `openqabot/args.py`.

- **New Arguments**:
    - `--dashboard-url`: Overrides `QEM_DASHBOARD_URL`
    - `--smelt-url`: Overrides `SMELT_URL`
    - `--gitea-url`: Overrides `GITEA_URL`
    - `--obs-url`: Overrides `OBS_URL`
    - `--obs-download-url`: Overrides `OBS_DOWNLOAD_URL`
    - `--obs-repo-type`: Overrides `OBS_REPO_TYPE`
    - `--obs-products`: Overrides `OBS_PRODUCTS`
    - `--allow-development-groups`: Overrides `QEM_BOT_ALLOW_DEVELOPMENT_GROUPS`
    - `--download-base-url`: Overrides `DOWNLOAD_BASE_URL`
    - `--download-maintenance-base-url`: Overrides `DOWNLOAD_MAINTENANCE_BASE_URL`
    - `--amqp-url`: Overrides `AMQP_URL`
    - `--deprioritize-limit`: Overrides `QEM_BOT_DEPRIORITIZE_LIMIT`
    - `--priority-scale`: Overrides `QEM_BOT_PRIORITY_SCALE`
    - `--main-openqa-domain`: Overrides `MAIN_OPENQA_DOMAIN`
    - `--git-review-bot`: Overrides `GIT_REVIEW_BOT`

- **Implementation**: In `openqabot/main.py` or `openqabot/args.py`, update the `openqabot.config` module attributes with values from `args` after parsing.

### 3. Add Filtering CLI Parameters
Add filtering arguments to scheduling subcommands.

- **Subcommands**: `full-run`, `submissions-run`, `updates-run`.
- **New Arguments**:
    - `--arch`: Multiple values allowed.
    - `--flavor`: Multiple values allowed.
    - `--product`: Multiple values allowed.
    - `--version`: Multiple values allowed.

- **Implementation**:
    - **`openqabot/loader/config.py`**: Update `load_metadata` to filter loaded configuration files by `product` and `version` if filters are provided.
    - **`openqabot/types/baseconf.py`**: Update `BaseConf.__call__` signature to accept optional `arch_filter` and `flavor_filter`.
    - **`openqabot/types/submissions.py`**: In `__call__`, filter by `arch` and `flavor`.
    - **`openqabot/types/aggregate.py`**: In `__call__`, filter by `arch` and `flavor`.
    - **`openqabot/openqabot.py`**: In `OpenQABot.__init__`, pass filters from `args` to `load_metadata`. In `__call__`, pass filters to worker calls.

## Verification Plan

### Automated Tests
1. **Unit Tests for Filtering**: Add tests in `tests/test_loader_config.py` to verify that `load_metadata` correctly filters by product and version.
2. **Unit Tests for Worker Filtering**: Add tests in `tests/test_submissions.py` and `tests/test_aggregate.py` to verify that `__call__` respects arch and flavor filters.
3. **CLI Override Tests**: Add a test (e.g., in `tests/test_args.py`) to verify that CLI arguments correctly override configuration variables.

### Manual Verification
1. Run `python qem-bot.py submissions-run --arch x86_64 --dry` and verify only x86_64 jobs are considered.
2. Run `python qem-bot.py full-run --product SLES --dry` and verify only SLES products are considered.
3. Run `python qem-bot.py --dashboard-url http://localhost:8000 ...` and verify the bot attempts to talk to the local dashboard.

## Validation Commands
```bash
make tidy
make checkstyle
make typecheck-ty
make test
```
