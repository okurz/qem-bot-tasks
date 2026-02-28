# Execution Plan: Refactoring and Maintainability Improvements

This document outlines the plan to address the architectural and maintainability issues identified in the code review, specifically focusing on code duplication, IO in constructors, type consistency, and logging practices.

## Goal
Improve the long-term maintainability of the `qem-bot` codebase by addressing identified debt and ensuring a clean separation of concerns.

## Tasks

### A. Eliminate Code Duplication (Shared Utilities)
- [x] **A1: Centralize String Utilities**: Move `strip_ansi` and `normalize_whitespace` (currently duplicated in `tests/test_readme.py` and `scripts/update_readme.py`) into `openqabot/utils.py`.
- [x] **A2: Refactor README Tools**: Update `tests/test_readme.py` and `scripts/update_readme.py` to import and use these centralized utilities.
- [x] **A3: Verification**: Ensure that `make test` and `make update-readme` continue to function correctly.

### B. Decouple IO from Class Constructors
- [ ] **B1: Refactor GiteaSync**: 
    - Move `get_open_prs` and `get_submissions_from_open_prs` out of `GiteaSync.__init__`.
    - Implement a `load()` or similar method (or perform IO in `__call__`).
- [ ] **B2: Refactor OpenQABot**:
    - Move `get_submissions` and `load_metadata` out of `OpenQABot.__init__`.
    - Defer this loading to a dedicated initialization phase or the start of the `__call__` method.
- [ ] **B3: Identify and Refactor Other Classes**: Audit `Approver`, `Commenter`, and other command classes for similar IO-in-constructor patterns and refactor them.
- [ ] **B4: Update Tests**: Adjust unit tests that currently rely on mocking these constructors to instead mock the loading phase.

### C. Standardize Type Usage
- [ ] **C1: Replace argparse.Namespace**: Identify all occurrences of `argparse.Namespace` (e.g., in `openqabot.py`, `giteasync.py`, `approver.py`).
- [ ] **C2: Update Type Hints**: Update these hints to use `types.SimpleNamespace` (reflecting the current `args.py` implementation) or a more specific `Pydantic` model / `Dataclass` where appropriate.
- [ ] **C3: Improve Type Safety**: Ensure that all CLI arguments are accessed in a type-safe manner.

### D. Enhance Logging and Error Handling
- [ ] **D1: Improve Exception Logging**: Refactor `openqabot/main.py` to use `log.exception("Unexpected error occurred")` instead of `log.error(e)`.
- [ ] **D2: Consistent Logger Naming**: 
    - Ensure all loggers follow the hierarchical pattern `bot.<module_path>` (e.g., `bot.loader.gitea`).
    - Audit `openqabot/approver.py`, `openqabot/commenter.py`, etc., to verify they don't use the generic `bot` logger when a more specific one is appropriate.
- [ ] **D3: Log Level Consistency**: Ensure that debug-level logs provide sufficient context without cluttering the output during normal runs.

## Verification Protocol
1. **Linting and Type Checking**: Run `make tidy checkstyle typecheck-ty`.
2. **Unit Testing**: Run `pytest`.
3. **Integration Testing**: Verify a subset of commands in dry-run mode (e.g., `python3 qem-bot.py --dry full-run`).
4. **Coverage**: Ensure no regression in test coverage.
