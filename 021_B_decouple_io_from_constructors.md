# Execution Plan: B. Decouple IO from Class Constructors

## Goal
Decouple data loading from object instantiation to improve testability and follow functional programming principles.

## Tasks
- [ ] **B1: Refactor GiteaSync**: 
    - Move `get_open_prs` and `get_submissions_from_open_prs` out of `GiteaSync.__init__`.
    - Implement a `load()` or similar method (or perform IO in `__call__`).
- [ ] **B2: Refactor OpenQABot**:
    - Move `get_submissions` and `load_metadata` out of `OpenQABot.__init__`.
    - Defer this loading to a dedicated initialization phase or the start of the `__call__` method.
- [ ] **B3: Identify and Refactor Other Classes**: Audit `Approver`, `Commenter`, and other command classes for similar IO-in-constructor patterns and refactor them.
- [ ] **B4: Update Tests**: Adjust unit tests that currently rely on mocking these constructors to instead mock the loading phase.

## Verification Protocol
1. **Unit Testing**: Run `pytest`.
2. **Integration Testing**: Verify a subset of commands in dry-run mode (e.g., `python3 qem-bot.py --dry full-run`).
