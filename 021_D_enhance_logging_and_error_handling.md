# Execution Plan: D. Enhance Logging and Error Handling

## Goal
Enhance error reporting and ensure consistent hierarchical logging.

## Tasks
- [ ] **D1: Improve Exception Logging**: Refactor `openqabot/main.py` to use `log.exception("Unexpected error occurred")` instead of `log.error(e)`.
- [ ] **D2: Consistent Logger Naming**: 
    - Ensure all loggers follow the hierarchical pattern `bot.<module_path>` (e.g., `bot.loader.gitea`).
    - Audit `openqabot/approver.py`, `openqabot/commenter.py`, etc., to verify they don't use the generic `bot` logger when a more specific one is appropriate.
- [ ] **D3: Log Level Consistency**: Ensure that debug-level logs provide sufficient context without cluttering the output during normal runs.

## Verification Protocol
1. **Linting and Type Checking**: Run `make tidy checkstyle typecheck-ty`.
2. **Unit Testing**: Run `pytest`.
