# Execution Plan: A. Eliminate Code Duplication (Shared Utilities)

## Goal
Improve code reuse and maintainability by centralizing common string utilities.

## Tasks
- [x] **A1: Centralize String Utilities**: Move `strip_ansi` and `normalize_whitespace` (currently duplicated in `tests/test_readme.py` and `scripts/update_readme.py`) into `openqabot/utils.py`.
- [x] **A2: Refactor README Tools**: Update `tests/test_readme.py` and `scripts/update_readme.py` to import and use these centralized utilities.
- [x] **A3: Verification**: Ensure that `make test` and `make update-readme` continue to function correctly.

## Verification Protocol
1. **Linting and Type Checking**: Run `make tidy checkstyle typecheck-ty`.
2. **Unit Testing**: Run `pytest`.
