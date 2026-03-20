# Plan: Ignore development job groups in posted comments

Ticket: [POO #197897](https://progress.opensuse.org/issues/197897)

## Objective
Ensure openQA overview links in comments exclude development/test job groups by appending `&not_group_glob=*Devel*%2C*Test*` to the URLs, matching the bot's internal filtering logic.

## Proposed Changes

### `openqabot/commenter.py`
- Update `summarize_message` to append `&not_group_glob=*Devel*%2C*Test*` to both the badge URL and the overview URL.
- This should only happen if `config.settings.allow_development_groups` is not truthy.

### `tests/test_commenter.py`
- Update `test_summarize_message` or add a new test to verify the inclusion of the glob parameter.
- Add a test case for when `allow_development_groups` is enabled to ensure the parameter is NOT added.

## Verification Plan

### Automated Tests
- Run `pytest tests/test_commenter.py` to verify the logic.
- Run `make test` to ensure no regressions and 100% coverage.
- Run `make tidy`, `make checkstyle`, and `make typecheck-ty` for quality assurance.

### Manual Verification
- A dry run with `qem-bot --dry sub-approve --comment` (if environment permits) to see the generated comment.
