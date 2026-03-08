# Execution Plan: Improve Code Quality

This document outlines a structured plan to improve the overall code quality of the `qem-bot` project, focusing on reducing complexity, eliminating duplication, adopting functional paradigms, and streamlining the test suite.

## 1. Reduce Complexity (Targeting High CC Scores)
Based on `radon cc` analysis, several components have high Cyclomatic Complexity (Grades C and D). The following components will be refactored:

- **`openqabot/types/submission.py`**
  - Refactor `Submission.__init__` (CC 27): Break down initialization into smaller private helper methods or factory methods.
  - Simplify `Submission.rev` (CC 16): Utilize early returns and simplify conditional logic.
- **`openqabot/types/submissions.py`**
  - Refactor `Submissions.should_skip` (CC 20) and `Submissions.handle_submission` (CC 17): Replace verbose `if/elif/else` chains with mapping tables or dispatch dictionaries to route logic cleanly.
- **`openqabot/loader/gitea.py`**
  - Simplify `add_build_result` (CC 14) and `add_channel_for_build_result` (CC 11) by extracting helper routines for specific data transformations.
- **`openqabot/osclib/comments.py`**
  - Refactor `CommentAPI.comment_find` (CC 12) for better readability.

**Strategy:** 
- Reduce nested conditionals.
- Replace if/else trees with mapping tables.
- Achieve Grade A (MI >= 20) across all modified files through genuine simplification.

## 2. Shift to Functional Programming Style
Procedural code will be systematically replaced with functional equivalents for long-term maintainability.

- **List Comprehensions & Generators:** Replace procedural `for`-loops that build lists/dicts with comprehensions.
- **Map & Filter:** Utilize `map()` and `filter()` functions for data transformation pipelines instead of imperative loop structures.
- **Ternary Operators:** Convert simple `if/else` variable assignments into concise ternary operators (e.g., `val = a if cond else b`).

## 3. Reduce Duplication (Codebase & Dead Code)
- **Dead Code Cleanup:** Remove unused variables, imports, and functions identified by `vulture` (e.g., dead functions in `tests/conftest.py`, `tests/test_giteasync.py`, and unused properties in `openqabot/config.py`).
- **Extract Common Logic:** Identify duplicated boilerplate (like error handling wrappers around HTTP requests) and abstract them into reusable utility functions.

## 4. Reduce Test Code Duplication and Redundancy
The test suite will be optimized to be more concise and maintainable.

- **Parameterization:** Implement `pytest.mark.parametrize` extensively to collapse repetitive test cases (e.g., in `tests/test_smeltsync.py` and `tests/test_loader_incrementconfig.py` which scored poorly on CC due to repetitive setup).
- **Consolidate Fixtures:** Centralize scattered duplicate mocks (e.g., `fake_qem`, `mock_osc_requests`) into `conftest.py` to ensure zero duplication across test files. Remove unused or duplicate fixtures identified by vulture.
- **Remove Redundant Tests:** Audit existing tests for overlapping assertions. Retain tests that add genuine coverage value and remove those that test identical code paths without providing new constraints.

## 5. Verification Steps
After implementing the changes, the following checks will be enforced:
1. `make tidy` and `make checkstyle` (ruff + radon + vulture) pass without errors.
2. `make typecheck-ty` passes.
3. `make test-with-coverage` maintains 100% line coverage for all modified files.
4. Verify Maintainability Index (MI >= 20) and reduced Cyclomatic Complexity (aiming for Grade A across the board).
