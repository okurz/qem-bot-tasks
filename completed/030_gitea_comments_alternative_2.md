# Execution Plan: Gitea Comments Alternative 2 (Issue #196820)

## Motivation
Fulfill issue #196820 to allow `qem-bot` to post comments on Gitea PRs containing openQA build results. The objective is to post non-duplicate test results (AC1, AC2) utilizing the new build result badges and to ensure actions are properly simulated during dry-mode (AC3).

## Architecture & Design Choices
Instead of creating a standalone Gitea commenter, the most maintainable approach is to extend the existing `openqabot.commenter.Commenter` class. The `Commenter` already queries the QEM dashboard, aggregates test results, handles running jobs, and determines the state. By adding branching logic, `Commenter` can handle `sub.type == "git"` submissions and route them to Gitea API endpoints.

## Execution Steps

### 1. Enhance Gitea API Client (`openqabot/loader/gitea.py`)
- **Action**: Add a `patch_json` function.
- **Details**: Implement `patch_json` exactly like `post_json` but invoking `retried_requests.patch`. This is required to update existing comments and prevent PR comment spam (AC2).

### 2. Update `Commenter` Initialization (`openqabot/commenter.py`)
- **Action**: Initialize Gitea token.
- **Details**: In `Commenter.__init__`, retrieve the Gitea token securely using `make_token_header(args.gitea_token)` and store it as `self.gitea_token` (importing `make_token_header` and `gitea` from `openqabot.loader`).

### 3. Branching Logic in `Commenter.__call__`
- **Action**: Relax submission filtering to process `git` PRs.
- **Details**: 
  - Change the early skip condition from `if sub.type != config.settings.default_submission_type:` to allow both `default_submission_type` and `"git"`.
  - In the summary/post phase of the loop, route to either OBS or Gitea:
    ```python
    if sub.type == config.settings.default_submission_type:
        msg = self.summarize_message(all_jobs)
        self.osc_comment(sub, msg, state)
    elif sub.type == "git":
        msg = self.summarize_gitea_message(all_jobs)
        self.gitea_comment(sub, msg, state)
    ```

### 4. Implement Gitea Message Summarizer (`Commenter.summarize_gitea_message`)
- **Action**: Create markdown containing openQA badges.
- **Details**: 
  - Parse `jobs` and extract distinct combinations of `build`.
  - Format a markdown response containing the newly introduced openQA badge:
    `[![Test Results]({base_url}/tests/overview/badge?build={build})]({base_url}/tests/overview?build={build})`
  - Group identical builds to ensure clean and concise PR comments.

### 5. Implement Gitea Committing Logic (`Commenter.gitea_comment`)
- **Action**: Create the `gitea_comment` logic which respects idempotency.
- **Details**:
  - If `self.gitea_token` is missing, skip and log a warning.
  - Append the `CommentAPI` hidden marker `<!-- openqa state=... -->` to the message so `qem-bot` can locate its own previous comments.
  - Use `gitea.get_json(gitea.comments_url(sub.project, sub.id))` to retrieve the PR's comment history.
  - Convert the Gitea list of dictionaries (`[{"id": 1, "body": "..."}]`) into the dictionary schema `CommentAPI.comment_find` expects (e.g. formatting `"body"` into `"comment"`).
  - Use `self.commentapi.comment_find()` to locate the active bot comment.
  - **Dry Mode (AC3)**: If `self.dry == True`, log `Would write/update comment to PR ...` and return early.
  - **No duplicate (AC2)**: If the existing comment's body has identical line-count or content, skip the update.
  - If no comment exists, call `gitea.post_json()`. If it exists, call `gitea.patch_json()` against `repos/{project}/issues/comments/{id}`.

### 6. Verification and Tests
- **Action**: Expand testing suite.
- **Details**:
  - Add tests in `tests/test_loader_gitea_helpers.py` for `patch_json`.
  - Add mocks in `tests/test_commenter.py` for `gitea_comment` validating that it calls `patch_json` when comments exist and `post_json` when they don't.
  - Verify that `sub.type == 'git'` is successfully dispatched to Gitea endpoints.
