# Execution Plan: C. Standardize Type Usage

## Goal
Standardize CLI argument types and improve type safety across the application.

## Tasks
- [ ] **C1: Replace argparse.Namespace**: Identify all occurrences of `argparse.Namespace` (e.g., in `openqabot.py`, `giteasync.py`, `approver.py`).
- [ ] **C2: Update Type Hints**: Update these hints to use `types.SimpleNamespace` (reflecting the current `args.py` implementation) or a more specific `Pydantic` model / `Dataclass` where appropriate.
- [ ] **C3: Improve Type Safety**: Ensure that all CLI arguments are accessed in a type-safe manner.

## Verification Protocol
1. **Linting and Type Checking**: Run `make tidy checkstyle typecheck-ty`.
2. **Unit Testing**: Run `pytest`.
