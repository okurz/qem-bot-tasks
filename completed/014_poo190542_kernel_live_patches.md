# Task: [tools] Product increments including kernel livepatches trigger openQA tests (poo190542)

## Status Update (2026-02-09)

The execution plan has been updated to streamline verification while still adhering to the project's strict validation requirements.

### Workflow (Per Step)

For each implementation step:
1.  Implement the changes (code and tests).
2.  **Verify:** Run `make tidy test-with-coverage` to ensure code style, type safety, and 100% test coverage.
    - *Note:* While `GEMINI.md` lists `make tidy checkstyle typecheck-ty test-with-coverage`, `make test-with-coverage` already depends on `checkstyle` and `typecheck-ty`, making the shorter sequence sufficient and more efficient.
3.  **Commit:** Create a clear, concise, and atomic commit for the changes.

### Implementation Steps

#### Step 1: Enhance `IncrementApprover` filtering
- Modify `extra_builds_for_package` in `openqabot/incrementapprover.py`.
- **Action:** Add checks to skip packages that:
    - Match `re.match(r'^1(?:\..*)?$', package.version)` (initial livepatches).
    - Contain `-debuginfo` or are of architecture `src` or `nosrc`.
- **Verification:** `make tidy test-with-coverage`.
- **Commit:** Finish step with an atomic commit.

#### Step 2: Extend `IncrementConfig` with `reference_repos`
- Modify `openqabot/loader/incrementconfig.py`.
- **Action:**
    - Add `reference_repos: dict[str, str] = field(default_factory=dict)` to the `IncrementConfig` dataclass.
    - Update `from_config_entry` to parse `reference_repos` from the YAML configuration.
- **Verification:** `make tidy test-with-coverage`.
- **Commit:** Finish step with an atomic commit.

#### Step 3: Improve `get_package_diff` logic
- Modify `openqabot/incrementapprover.py`.
- **Action:**
    - Update `get_package_diff` to prioritize `reference_repos` if defined in the configuration.
    - Ensure that repository diffing only considers relevant architectures and ignores `-Debug` and `-Source` repository paths unless specifically needed.
- **Verification:** `make tidy test-with-coverage`.
- **Commit:** Finish step with an atomic commit.

#### Step 4: Documentation Update
- Update `doc/config.md`.
- **Action:** Document the new `reference_repos` field and the filtering logic for kernel livepatches.
- **Verification:** `make tidy checkstyle`.
- **Commit:** Finish step with an atomic commit.

#### Step 5: Final Validation
- Ensure all new test cases in `tests/test_incrementapprover_helpers.py` and elsewhere pass.
- **Verification:** Run `make tidy test-with-coverage` for a final check of the entire project state.
- **Commit:** Final project state check.

For more details on the investigation, see [014_poo190542_execution_plan.md](./014_poo190542_execution_plan.md).