# Fix More Style Issues

Plan to fix currently ignored style issues in `qem-bot`.

## 1. Local Ignores (`# noqa:`)

These issues are suppressed locally in the code. We should aim to resolve them or verify if they are false positives.

### Security (Bandit - S)
- [x] `scripts/update_readme.py`: `S607` (start_process_with_partial_path) - *FIXED by using sys.executable*.
- [x] `tests/test_readme.py`: `S607` - *FIXED*.
- [x] `scripts/update_readme.py`, `tests/test_readme.py`: `S404`, `S603` (subprocess usage) - *Action*: Verify if `subprocess` usage is safe or can be replaced. **(DONE)**
- [x] `tests/test_syncres.py`, `tests/test_commenter.py`: `S106` (hardcoded-password-func-arg) - *Verified safe in tests (dummy tokens).* **(DONE)**
- [x] `tests/test_aggrsync.py`, `tests/test_openqabot.py`: `S105` (hardcoded-password-string) - *Verified safe in tests.* **(DONE)**
- [x] `openqabot/loader/repohash.py`: `S324` (hashlib-insecure-hash-function) - *FIXED by using usedforsecurity=False*. **(DONE)**

### Testing / Private Access (SLF001)
- [x] Remaining use of `SLF001` (private-member-access) in tests:
    - `tests/test_aggregate.py` **(DONE)**
    - Verified others: `tests/test_syncres.py`, `tests/test_amqp.py`, `tests/test_submissions.py`, `tests/test_approve_helpers.py`, `tests/test_submission.py`, `tests/test_smeltsync.py`, `tests/test_repodiff.py`, `tests/test_osclib_comments.py` **(DONE)**
- [x] *Action*: Refactor code to allow testing through public interfaces or expose necessary methods properly. **(DONE)**

### Arguments (ARG)
- [x] `tests/test_baseconf.py`: `ARG002` (unused-method-argument), `ARG004` (unused-static-method-argument)
- [x] `tests/fixtures/submissions.py`: `ARG002`
- [x] *Action*: Remove unused arguments or rename with `_` prefix if they must exist. **(DONE)**

### Complexity (C901, PLR)
- [x] `openqabot/commenter.py`: `C901` (complex-structure) - *Action*: Refactor `summarize_message` to reduce complexity. **(DONE)**
- [x] `openqabot/types/aggregate.py`: `C901` **(FIXED)**
- [x] `openqabot/approver.py`: `PERF203` (try-except-in-loop) **(FIXED)**
- [x] *Action*: Refactor to reduce complexity. **(DONE for C901 in aggregate.py and PERF203)**

### Exception Handling (BLE001, TRY301)
- [x] `openqabot/pc_helper.py`: `BLE001` (blind-except), `TRY301` (raise-within-try) **(FIXED)**
- [x] `openqabot/loader/gitea.py`: `BLE001` - *Action*: Catch specific exceptions. **(DONE)**
- [x] `openqabot/loader/incrementconfig.py`: `BLE001` - *Action*: Catch specific exceptions. **(DONE)**

### Output (T201)
- [x] `scripts/update_readme.py`: `T201` (print) **(FIXED)**
- [x] `openqabot/repodiff.py`: `T201` **(FIXED)**

### Imports
- [x] `tests/helpers.py`: `F401` (unused-import)
- [x] `tests/test_repohash.py`: `A004` (builtin-import-shadowing)
- [x] `tests/test_aggregate.py`, `tests/test_osclib_comments.py`: `PLC2701` (import-private-name)

## 2. Global Ignores (`pyproject.toml`)

These rules are ignored project-wide. We should enable them one by one and fix the violations.

### Documentation (D)
- [x] `D100`: Missing docstring in public module. **(DONE)**
- [x] `D101`: Missing docstring in public class. **(DONE)**
- [x] `D102`: Missing docstring in public method. **(DONE)**
- [x] `D103`: Missing docstring in public function. **(DONE)**
- [x] `D104`: Missing docstring in public package. **(FIXED)**
- [x] `D105`: Missing docstring in magic method. **(DONE)**
- [x] `D107`: Missing docstring in `__init__`. **(FIXED)**
- [x] `D203`: Incorrect blank line before class. **(IGNORED IN FAVOR OF D211)**
- [x] `D213`: Multi-line summary second line. **(IGNORED IN FAVOR OF D212)**
- [ ] `DOC201`, `DOC501`: Docstring return/exception missing.

### Naming (N)
- [x] `N801`, `N802`, `N803`, `N806`: Invalid names for classes, functions, arguments, variables. **(ENABLED and FIXED)**

### Refactoring / Complexity (PLR, PLW, PLC)
- [x] `PLC0415`: Import outside toplevel. **(ENABLED and FIXED)**
- [x] `PLR0912`: Too many branches. **(ENABLED and FIXED - none found)**
- [x] `PLR0913`: Too many arguments. **(ENABLED and SUPPRESSED in tests)**
- [x] `PLR0914`: Too many locals. **(ENABLED and SUPPRESSED in args.py)**
- [x] `PLR0915`: Too many statements. **(ENABLED and SUPPRESSED in args.py)**
- [x] `PLR2004`: Magic value comparison. **(ENABLED and SUPPRESSED in gitea.py, submission.py)**
- [x] `PLR6301`: No self use. **(ENABLED and SUPPRESSED in multiple files)**
- [x] `PLC1901`: Compare to empty string. **(ENABLED and FIXED)**
- [x] `PLW2901`, `PLW0127`, `PLW0128`, `PLW0129`: Shadowing and reassigning. **(ENABLED and FIXED)**

### Typing (ANN, TC)
- [x] `ANN401`: Any type. **(ENABLED and SUPPRESSED where necessary)**
- [x] `TC001` - `TC003`: Type checking imports. **(DONE)**

### Others
- [x] `UP032`: f-string. **(ENABLED and FIXED)**
- [x] `S101`: Use of assert (likely needs exclusion for tests only). **(ENABLED and FIXED)**
- [x] `COM812`: Missing trailing comma. **(IGNORED - INCOMPATIBLE WITH FORMATTER)**
- [x] `B019`: functools.lru_cache on methods. **(DONE)**
- [x] `FURB140`: reimplemented-starmap. **(DONE)**

## Prioritized Strategy with Validation

Each step below MUST be followed by these validation commands:
1. `make tidy` (to ensure correct formatting)
2. `make test-with-coverage` (to ensure formatting, checks, 100% coverage and no regressions)

Only after ALL these commands pass should the change be committed and the next step started. Ensure for each individual style rule change to commit.