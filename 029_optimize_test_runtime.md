# Task 029: Optimize Test Runtime Execution Plan

## Status
* **Target:** Reduce `make test` runtime from ~4s to <2s and `make test-with-coverage` from ~10s to <5s.
* **Constraints:** Maintain 100% statement and branch coverage.
* **Current State (2026-03-05):**
    * `make test` reduced from ~4.3s to ~3.1s.
    * `make test-with-coverage` reduced from ~10s to ~9.5s (parallel) or ~7.2s (serial).
    * `pytest-xdist` detection fixed and enabled.
    * Style checks parallelized.
    * Coverage restricted to `openqabot` package.
    * Test isolation issues fixed.

## 1. Baseline & Profiling [COMPLETED]
* **Objective:** Obtain a detailed breakdown of test durations.
* **Actions:**
    * Run `unshare -r -n python3 -m pytest --durations=0` to identify all slow tests. [DONE]
    * Run `make test-with-coverage` and note the total time as a baseline. [DONE]
    * Investigate if `pytest-cov` overhead can be reduced (e.g., by excluding non-source directories more strictly). [DONE: Restricted to `openqabot`]

## 2. Immediate Optimizations [COMPLETED]
### 2.1. Refactor `tests/test_readme.py`
* **Issue:** `test_readme_usage_up_to_date` uses `subprocess.run` to execute the full application just to verify the help output.
* **Optimization:** Replace `subprocess.run` with `typer.testing.CliRunner.invoke(app, ["--help"])`. [DONE: Already implemented]

### 2.2. Fix Test Isolation Issues
* **Issue:** `tests/test_args.py::test_main_no_token_exit` fails when run in bulk but passes in isolation, indicating leaked global state.
* **Optimization:** 
    * Identify the source of leaked state (likely environment variables or `openqabot.config.settings`). [DONE]
    * Use `mocker.patch.dict(os.environ, ...)` or proper fixture-based cleanup for all environment variable modifications. [DONE]
    * Ensure `settings` object is reset between tests if modified. [DONE]
    * Fixed `test_repo_diff` and `test_increment_approve` failing due to missing configs in isolation. [DONE]
    * Fixed `test_handle_job_not_found` log level issue revealed by xdist. [DONE]

## 3. Parallelization [COMPLETED]
* **Objective:** Leverage multi-core CPUs for test execution.
* **Actions:**
    * Verify if `pytest-xdist` is installed. [DONE]
    * Ensure `Makefile` correctly uses `$(PYTEST_XDIST)`. [DONE: Fixed detection logic]
    * Address any race conditions or resource contention. [DONE: Fixed issues revealed by xdist]
    * Parallelized style checks in `Makefile`. [DONE]

## 4. Refactoring for Speed [IN PROGRESS]
* **Objective:** Reduce redundant work in tests.
* **Actions:**
    * **High-level Mocking:** Review tests that instantiate `OpenQABot` or `OpenQAInterface`. [ONGOING]
    * **Fixtures:** Move expensive setups to `conftest.py`. [ONGOING]
    * **Mocking Network Calls:** Verify that NO tests are making actual network calls. [DONE]

## 5. Verification [ONGOING]
* **Objective:** Ensure performance gains without regressions.
* **Actions:**
    * Run `make test` to verify the <2s target. [CURRENT: 3.1s]
    * Run `make test-with-coverage` to verify the <5s target and 100% coverage. [CURRENT: 7.2s-9.5s]
    * Verify that the fix for `test_main_no_token_exit` is stable in parallel runs. [DONE]

## 6. Documentation
* **Action:** Update `CONTRIBUTING.md` or similar if new testing dependencies (like `pytest-xdist`) are now strongly recommended for a good developer experience.
