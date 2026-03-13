# HTTP Check Alternative Plan for poo#197270: Prevent scheduling of packages on non-supported architectures

## Motivation
As discussed in ticket #197270, certain maintenance updates (like `kernel-livepatch`) are only supported on a subset of architectures (e.g., `x86_64`, `ppc64le`, `s390x`). When `qem-bot` schedules tests on unsupported architectures (e.g., `aarch64`), openQA fails because the IBS repository exists but the specific architecture subfolder inside it is missing (as there are no packages built for it).

For example, in PR 2702:
- Base Repo exists: `https://download.suse.de/ibs/SUSE:/SLFO:/1.2:/PullRequest:/2702:/SLES/product/repo/SLES-16.0-aarch64/`
- Valid architecture exists: `https://download.suse.de/ibs/SUSE:/SLFO:/1.2:/PullRequest:/2702:/SLES/product/repo/SLES-16.0-aarch64/aarch64/` (HTTP 200)
- Invalid architecture does not exist: `https://download.suse.de/ibs/SUSE:/SLFO:/1.2:/PullRequest:/2702:/SLES/product/repo/SLES-16.0-ppc64le/ppc64le/` (HTTP 404)

This plan proposes an active validation approach: checking the availability of the `INCIDENT_REPO` via a lightweight HTTP `HEAD` request before submitting the job to openQA.

## Proposed Changes in `qem-bot`

We propose a two-step approach, with **Step 1 being the primary fix** and **Step 2 being an optional safety net**.

### Step 1: Filter during gitea-sync (Primary Fix)
This step prevents invalid channels from being created in the first place, earlier in the pipeline.

**Problem verified in PR 2702:**
- OBS `_result` API returns `state="published"` for ppc64le architecture
- BUT all packages inside have `code="excluded"`
- qem-bot incorrectly adds the channel `SUSE:SLFO:1.2:PullRequest:2702:SLES:ppc64le#16.0` to the submission

**Fix location:** `openqabot/loader/gitea.py` in the `add_build_result` function.

**Important correction:** The check must happen **BEFORE** `add_channel_for_build_result()` is called, not after. Looking at the code flow in `add_build_result()`:
- Line 333: `add_channel_for_build_result(...)` adds the channel to `results.projects`
- Lines 339-341: Status checks happen **after** the channel is already added

**Implementation:**
Place the check at the beginning of `add_build_result()`, before calling `add_channel_for_build_result()`:
```python
def add_build_result(
    submission: dict[str, Any],
    res: Any,  # noqa: ANN401
    results: BuildResults,
) -> None:
    """Process a single build result and update submission and results."""
    project = res.get("project")
    arch = res.get("arch")

    # Check if ALL packages are excluded BEFORE adding the channel
    statuses = res.findall("status")
    if statuses and all(s.get("code") == "excluded" for s in statuses):
        log.debug("Skipping %s:%s: all packages are excluded", project, arch)
        return

    # Rest of the function...
```
This prevents the channel from being added to `results.projects` and subsequently to `submission["channels"]`.

**Expected outcome:** After implementing Step 1 alone, qem-bot will no longer create channels for architectures where no packages are built (all excluded). This should completely solve the problem without needing additional changes.

### Step 2: HTTP Check as Safety Net (Optional - Implement Only If Step 1 Proves Insufficient)

**Note:** If Step 1 works correctly, Step 2 should rarely trigger. Only implement this if production experience shows edge cases where OBS `_result` API state is inconsistent or the download directory structure differs from expectations.

This serves as a fallback validation:

1. Add a new optional config setting (e.g., `http_repo_validation: bool = False`) to enable/disable
2. Open `openqabot/types/submissions.py`.
3. Locate the `handle_submission` function.
4. After the `INCIDENT_REPO` string is generated from the `repos` set (line 285), iterate over those base URLs.
5. Construct the validation URL by appending `/{arch}/` to the base URL.
6. Use `requests.head(url, allow_redirects=True, timeout=10)` to check for a `404`.
7. If any of the required repos return `404` and `http_repo_validation` is enabled, log a debug/info message and return `None` to prevent scheduling.
8. Update unit tests in `tests/test_submissions_handle.py` to mock `requests.head` and verify that the bot correctly filters out missing repos.

## User Benefits
- **Solves the Root Cause:** Filtering during gitea-sync removes invalid channels at the source, preventing them from ever reaching the scheduling stage.
- **No External Dependencies:** Works without requiring changes to IBS configurations, `scmsync` workflows, Gitea repositories, or `smelt`.
- **Clean Fallback:** Gracefully bypasses empty architectures without blocking the entire Pull Request or marking it as failed.
- **Optional Safety Net:** The HTTP check (Step 2) can be added later if needed for extra robustness against OBS inconsistencies.

## Implementation Steps

### Step 1: Filter during gitea-sync (Implement First - May Be Sufficient)
See **Step 1** in the "Proposed Changes" section above for implementation details.

### Step 2: HTTP Check as Safety Net (Optional)
See **Step 2** in the "Proposed Changes" section above for implementation details.

## Verification Tests

### Step 1 Tests (tests/test_loader_gitea_build_results.py)

Add the following test cases:

1. **`test_add_build_result_all_excluded_skips_channel`** - Verify channel is NOT added when ALL packages have `code="excluded"`
2. **`test_add_build_result_some_excluded_includes_channel`** - Verify channel IS added when SOME packages are excluded (but not all) - ensures we don't over-filter
3. **`test_add_build_result_mixed_status_codes`** - Verify existing behavior unchanged for succeeded/failed packages

Example test structure:
```python
def test_add_build_result_all_excluded_skips_channel(mocker: MockerFixture) -> None:
    """Verify channel is skipped when all packages have code='excluded'."""
    mocker.patch("openqabot.loader.gitea.get_product_name", return_value="SLES")
    mocker.patch("openqabot.config.settings.obs_products", "SLES")
    mocker.patch("openqabot.loader.gitea.add_channel_for_build_result")

    incident = {"number": 123}
    res = mocker.Mock()
    res.get.side_effect = lambda k: {"project": "proj", "arch": "ppc64le", "state": "published"}.get(k, "")
    # Three packages, all excluded
    res.findall.return_value = [
        mocker.Mock(get=lambda k: "excluded"),
        mocker.Mock(get=lambda k: "excluded"),
        mocker.Mock(get=lambda k: "excluded"),
    ]

    results = BuildResults()
    gitea.add_build_result(incident, res, results)

    # Channel should NOT be added to results.projects
    assert "proj:ppc64le" not in results.projects
```

### Step 2 Tests (tests/test_submissions_handle.py) - Only if implemented

Add the following test cases:

1. **`test_handle_submission_http_check_404_skips_job`** - Mock `requests.head` returning 404, verify job is skipped
2. **`test_handle_submission_http_check_200_allows_job`** - Mock `requests.head` returning 200, verify job is scheduled
3. **`test_handle_submission_http_check_network_error_handled`** - Handle network errors gracefully

### Coverage Requirements

Run `make test-with-coverage` after implementing and ensure:
- 100% line coverage for modified files
- No "Missing" lines in the coverage report for the new code paths
