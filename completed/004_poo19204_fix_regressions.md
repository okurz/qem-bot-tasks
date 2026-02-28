# Fix Regressions and Implement Verified Submission Type Support

## Problem
Two regressions were identified in the generation of aggregate job data:
1.  **Repo URLs** incorrectly include the "smelt:" prefix (e.g., `.../smelt:41840/...` instead of `.../41840/...`).
2.  **Dashboard URLs** incorrectly include the `?type=smelt` query parameter, which is not supported by the dashboard.

These were caused by attempts to disambiguate submission types before the dashboard was ready to handle them.

## Analysis
-   **Repo URL Issue**: In `openqabot/types/aggregate.py`, the `_get_repo_url` method used string interpolation with the `Submission` object (`{sub}`). The `Submission.__str__` method returns `type:id` (e.g., `smelt:123`), causing the prefix to appear in the URL.
-   **Dashboard URL Issue**: In `openqabot/types/aggregate.py`, the `_finalize_post` method explicitly added `?type={sub.type}` to the `__DASHBOARD_INCIDENTS_URL`.

## Goal: Parallel Verified Support for Submission Types
To solve [poo192904](https://progress.opensuse.org/issues/192904) (Disambiguate gitea+smelt incidents in qem-bot+qem-dashboard), we need a coordinated update path.

### 1. Dashboard Readiness
The `qem-dashboard` must be updated to:
-   Accept `type` in `api/update_settings` payload (`incidents` as list of objects instead of integers).
-   Handle `type` parameter in `/incident/<id>` routes.
-   Disambiguate storage by `(id, type)`.

### 2. Coordinated Bot Update Plan
1.  **Phase 1: Safe Fallback (Completed)**:
    -   Bot uses `sub.id` for URLs and payload to maintain compatibility with the current dashboard.
    -   Regression tests added to `tests/test_aggregate.py` to prevent accidental inclusion of prefixes or parameters.

2.  **Phase 2: Feature Toggle / Dynamic Support**:
    -   Introduce a mechanism (e.g., a version check or a config toggle) to allow the bot to send the new format once the dashboard is confirmed to support it.
    -   Update `openqabot/types/aggregate.py` to optionally use the disambiguated format:
        ```python
        # Future format once dashboard is ready
        full_post["qem"]["incidents"] = [{"incident": sub.id, "type": sub.type} for sub in incidents]
        ```

3.  **Phase 3: Verification**:
    -   Create integration tests that simulate both old and new dashboard behaviors.
    -   Ensure `openqabot/types/submissions.py` and `openqabot/types/aggregate.py` are consistent in how they generate URLs and dashboard payloads.

## Prevention
-   **Strict Schema Validation**: Add schema validation for payloads sent to the dashboard in tests.
-   **URL Assertions**: Maintain and expand assertions in `test_aggregate_url_format` to cover all submission types (`smelt`, `git`).
-   **Mock Consistency**: Ensure mocks in `conftest.py` or fixtures accurately reflect the real `Submission` class behavior (especially `__str__`).

## Phase 4: API Redesign Proposal (New)

To fully resolve the ambiguity and move towards a RESTful design, we propose the following API route structure for `qem-dashboard`.

### Design Principles
-   **Resource-Oriented**: Use URL segments for resource identification (`:type/:id`) instead of query parameters.
-   **Consistent**: Apply the same pattern across all related endpoints (settings, jobs, etc.).

### Proposed Routes

| Action | Current Route | Proposed Route | Notes |
| :--- | :--- | :--- | :--- |
| **Get Submission** | `GET /api/incidents/:id?type=:type` | `GET /api/submissions/:type/:id` | Unified access to submission details. |
| **List Submissions** | `GET /api/incidents` | `GET /api/submissions` | Can support filtering via query params (e.g. `?active=true`). |
| **Get Settings** | `GET /api/incident_settings/:id?type=:type` | `GET /api/submissions/:type/:id/settings` | Retrieve job settings for a submission. |
| **Update Settings** | `GET /api/update_settings/:id?type=:type` | `GET /api/submissions/:type/:id/update_settings` | Retrieve aggregate update settings. |
| **Get Jobs** | `GET /api/jobs/incident/:id` | `GET /api/submissions/:type/:id/jobs` | Retrieve jobs associated with a submission. |
| **Sync Submissions** | `PATCH /api/incidents` | `PATCH /api/submissions/:type` | Bulk update/sync for a specific type. |

### Migration Strategy for qem-bot

1.  **Dual Support**: `qem-bot` logic should detect if the dashboard supports the new routes (e.g. via a capabilities endpoint or config flag) or attempt new routes and fall back to old ones.
2.  **Code Changes**:
    -   Update `openqabot/loader/qem.py`: Refactor `_get_submission` and `get_submission_settings` to construct URLs based on the new pattern.
    -   Update `openqabot/dashboard.py`: Ensure `get_json` and `patch` can handle the new paths.
    -   Update `openqabot/types/submissions.py`: Update `__DASHBOARD_INCIDENT_URL` generation.

### Example Usage (New)

```python
# Old
get_json(f"api/incident_settings/{sub_id}", params={"type": "git"})

# New
get_json(f"api/submissions/git/{sub_id}/settings")
```

This design eliminates the risk of missing `?type=` parameters and provides a cleaner API surface.