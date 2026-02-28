# Execution Plan: [tools] Product increments including kernel livepatches trigger openQA tests (poo190542)

This plan outlines the implementation steps for automating openQA tests for product increments that include kernel livepatches, ensuring they are correctly triggered and approved while minimizing product-specific logic.

## 1. Goal and Acceptance Criteria

**Goal:** Product increments including kernel livepatches trigger openQA tests and openQA approval is given if all tests pass.

**Acceptance Criteria:**
- **AC1:** SLE 16 maintenance product increments including kernel livepatches trigger openQA tests.
- **AC2:** openQA approval is given if all tests pass.
- **AC3:** As little as possible additional product-specific logic is present in `qem-bot`.
- **AC4:** No product-specific logic in openQA.

## 2. Identified Issues for Resolution

Based on the investigation, the following issues in the previous attempts need to be fixed:
1.  **Wrong triggers:** Initial livepatches bundled with kernel updates were triggered. These cannot be tested separately and must be ignored.
2.  **Unwanted builds:** Debuginfo packages triggered tests, which is unnecessary.
3.  **Repo Diff accuracy:** The "correct" way to compute the diff is by comparing `primary.xml` from both repositories, but we need a way to specify the reference repositories in the configuration.
4.  **Configuration flexibility:** A mapping for `reference_repos` is missing in the configuration.

## 3. Workflow (Per Step)

For each implementation step below:
1.  Implement the changes (code and tests).
2.  **Verify:** Run `make tidy test-with-coverage` to ensure code style, type safety, and 100% test coverage.
    - *Note:* This satisfies the validation requirements in `GEMINI.md` by combining auto-formatting (`tidy`) with the comprehensive test/style/type-checking target (`test-with-coverage`).
3.  **Commit:** Create a clear, concise, and atomic commit for the changes.

## 4. Implementation Plan

### Step 1: Enhance `IncrementApprover` filtering
- Modify `extra_builds_for_package` in `openqabot/incrementapprover.py`.
- **Action:** Add checks to skip packages that:
    - Match `re.match(r'^1(?:\..*)?$', package.version)` (initial livepatches).
    - Contain `-debuginfo` or are of architecture `src` or `nosrc`.
- **Verification:** `make tidy test-with-coverage`.
- **Commit:** Finish step with an atomic commit.

### Step 2: Extend `IncrementConfig` with `reference_repos`
- Modify `openqabot/loader/incrementconfig.py`.
- **Action:**
    - Add `reference_repos: dict[str, str] = field(default_factory=dict)` to the `IncrementConfig` dataclass.
    - Update `from_config_entry` to parse `reference_repos` from the YAML configuration.
- **Verification:** `make tidy test-with-coverage`.
- **Commit:** Finish step with an atomic commit.

### Step 3: Improve `get_package_diff` logic
- Modify `openqabot/incrementapprover.py`.
- **Action:**
    - Update `get_package_diff` to prioritize `reference_repos` if defined in the configuration.
    - Ensure that repository diffing only considers relevant architectures and ignores `-Debug` and `-Source` repository paths unless specifically needed.
- **Verification:** `make tidy test-with-coverage`.
- **Commit:** Finish step with an atomic commit.

### Step 4: Documentation Update
- Update `doc/config.md`.
- **Action:** Document the new `reference_repos` field and the filtering logic for kernel livepatches.
- **Verification:** `make tidy checkstyle`.
- **Commit:** Finish step with an atomic commit.

### Step 5: Final Validation
- Ensure all new test cases in `tests/test_incrementapprover_helpers.py` and elsewhere pass.
- **Verification:** Run `make tidy test-with-coverage` for a final check of the entire project state.
- **Commit:** Final project state check.

## 5. Proposed Timeline (Summary)

1.  **Phase 1 (Filtering):** Implement Step 1 and corresponding unit tests.
2.  **Phase 2 (Configuration):** Implement Step 2 and Step 3.
3.  **Phase 3 (Validation):** Comprehensive testing and documentation (Step 4 and 5).
