# Plan: Review and Update Style Issues Task List

This plan outlines the steps to update `tasks/002_fix_more_style_issues.md` based on the current state of the codebase.

## 1. Final Verification of Current State

- [ ] Execute `ruff check .` and `ruff check tests/` without any filters to see all current violations (even those with `noqa`).
- [ ] List all unique `noqa` codes currently used in the codebase and compare them with the ones listed in `tasks/002_fix_more_style_issues.md`.
- [ ] Verify which global ignores in `pyproject.toml` are still necessary by temporarily removing them and running `ruff check`.

## 2. Update `tasks/002_fix_more_style_issues.md`

- [ ] **Correct Status of Local Ignores**:
    - Re-evaluate `SLF001` (private-member-access). Multiple files (e.g., `tests/test_aggregate.py`) still have `# noqa: SLF001` despite being marked as DONE.
    - Add `S603` (subprocess-untrusted-input) to the list of security issues, as it is suppressed in `scripts/update_readme.py` and `tests/test_readme.py`.
    - Update `BLE001` and `TRY301` status. Verify if they are truly fixed or just ignored/logged.
- [ ] **Update Global Ignores**:
    - Confirm that `D100-D103`, `D105`, `D203`, `D213`, `DOC201`, `DOC501`, `TC001-TC003`, `COM812`, `B019`, and `FURB140` are still pending.
    - Verify that `N801`, `N802`, `N803`, `N806`, `UP032`, `S101`, `PLC0415`, `PLR0912`, `PLR0913`, `PLR0914`, `PLR0915`, `PLR2004`, `PLR6301`, `PLC1901`, `PLW2901`, `PLW0127`, `PLW0128`, `PLW0129`, and `ANN401` are correctly handled (either enabled or explicitly suppressed where appropriate).
- [ ] **Add New Tasks**:
    - Add any newly discovered style rules that should be addressed.

## 3. Prioritize Remaining Tasks

- [ ] Group remaining tasks by effort and impact.
- [ ] Focus on enabling more `D` (docstring) and `TC` (type-checking) rules.
- [ ] Address the remaining `SLF001` issues in tests by proper refactoring.

## 4. Execution of Updates

- [ ] Apply the changes to `tasks/002_fix_more_style_issues.md`.
- [ ] Ensure all `[x]` marks reflect reality (no `noqa` remains for that rule in the project, unless it's a verified false positive that is explicitly documented).

## Verification Rules for Each Fix

1. `make tidy`
2. `make test-with-coverage`
3. Commit each atomic change separately.
