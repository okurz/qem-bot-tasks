# Plan: Run qem-bot independent of qem-dashboard

## Objective
Enable `qem-bot` to operate independently of `qem-dashboard`. The goal is to support triggering openQA tests based on Gitea PRs and approving them based on results, using only `qem-bot` and `openQA`, without requiring the maintenance-focused dashboard infrastructure.

## Motivation
Currently, `qem-bot` is tightly coupled with `qem-dashboard`. It syncs data to the dashboard, which then serves as the source of truth for scheduling. This works for the maintenance workflow (SMELT incidents) but is heavy-handed for simpler CI/CD use cases or new projects that just want "PR testing" via openQA.

## Proposed Architecture
The new workflow will bypass the dashboard:
1.  **Source**: Gitea PRs.
2.  **Processor**: `qem-bot` (Stateless* execution).
3.  **Executor**: openQA.
4.  **Feedback**: `qem-bot` posts results/approval back to Gitea.

*Stateless in the sense that `qem-bot` doesn't maintain its own database; it relies on Gitea (current PR state) and openQA (current Job state) as the state providers.

## Implementation Steps

### 1. Configuration Extensions
*   Ensure all necessary test definitions (job templates, product variables, etc.) can be loaded from local configuration files (YAML) or command-line arguments, rather than fetched from the dashboard API.
*   Define a mapping between Gitea Repositories and openQA Job Templates in the configuration.

### 2. New Subcommand: `gitea-run` (or similar)
A new command (or extension of existing ones) to handle the direct workflow.

**Logic:**
1.  **Fetch**: Retrieve open Pull Requests from configured Gitea repositories.
2.  **Filter**: Apply filters (e.g., Labels like `test-on-openqa`, specific branches).
3.  **Resolve**: For each PR, calculate the necessary openQA jobs.
    *   *Challenge*: Currently, some settings might come from the dashboard. These must be moved to config.
4.  **Schedule/Check**:
    *   Query openQA: "Are there existing jobs for this PR/Commit hash?" (using job group and custom vars).
    *   **If missing**: Trigger the jobs.
    *   **If running**: Wait or just log status.
    *   **If finished**: Collect results.
5.  **Feedback**:
    *   Post a summary comment to the Gitea PR.
    *   (Optional) Set Gitea Commit Status (Build Status).
    *   (Optional) Approve the PR if all tests passed.

### 3. Modifications to Existing Modules
*   **`openqabot.loader.gitea`**: Reuse logic for fetching PRs and parsing `multibuild` container definitions if applicable.
*   **`openqabot.openqa`**: Ensure the openQA client can be used to search for jobs by specific variables (e.g., `GITEA_PR_ID`, `GITEA_COMMIT`) to avoid duplicate scheduling without a database.

## Tasks
- [ ] **Design Config Schema**: Define how to map a Gitea Repo to openQA Job Group/Templates in `qem-bot` config.
- [ ] **Job Discovery**: Implement logic to determine *what* to test without querying the dashboard.
- [ ] **Direct Scheduling**: Create a scheduler that pushes directly to openQA.
- [ ] **Result Polling**: Implement a mechanism to check results of triggered jobs.
- [ ] **Gitea Feedback**: Implement logic to post results back to Gitea (Comment/Status/Approval).
- [ ] **CLI Entry Point**: Add the new subcommand (e.g., `bot-run` or `ci-run`).

## detailed analysis of current coupling
*   `smelt-sync`, `gitea-sync`: Push to Dashboard.
*   `submissions-run`: Pulls from Dashboard.
*   `approver.py`: Checks Dashboard for "passed" state.

**New Path**:
`gitea-ci` command -> `loader.gitea` -> `DirectScheduler` -> `openQA`.
`DirectScheduler` -> checks `openQA` -> `Approver` -> `Gitea`.
