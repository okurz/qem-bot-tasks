# Execution Plan - poo196820: [qem-bot] comment in gitea PRs pointing to openQA test results

This plan outlines the steps to implement a feature in `qem-bot` that comments on Gitea Pull Requests with openQA test results, similar to the existing functionality for OBS requests.

## 1. Research & Analysis
- [x] Confirm the structure of `git` type submissions in the QEM Dashboard.
- [ ] Verify that `get_submission_results` and `get_aggregate_results` correctly retrieve data for `git` type submissions.
- [x] Analyze existing Gitea interaction in `openqabot/loader/gitea.py` (e.g., `review_pr`).

## 2. Refactoring Existing Commenting Logic
To avoid code duplication and simplify the addition of new commenters, the generic Markdown summarization logic will be extracted.

- [ ] Update `openqabot/types/submission.py`:
    - Ensure `Submission` objects store the PR URL for `git` type submissions in `self.url`.
- [ ] Create `openqabot/base_commenter.py` with `BaseCommenter` class.
- [ ] Move the following generic methods from `Commenter` to `BaseCommenter`:
    - `summarize_message`
    - `_process_job`
    - `_create_group_if_missing`
    - `_format_group_message`
    - `escape_for_markdown`
    - `__summarize_one_openqa_job`
- [ ] Update `openqabot/commenter.py`:
    - Inherit `Commenter` from `BaseCommenter`.
    - Keep OBS-specific logic (`osc_comment`).
    - Update `__call__` to iterate over all submissions and delegate to either `osc_comment` or the new `GiteaCommenter.gitea_comment`.

## 3. Implementation of Gitea Commenter
A new commenter specifically for Gitea PRs, reusing the refactored summarization.

- [ ] Update `openqabot/loader/gitea.py`:
    - Add `add_comment(token, repo_name, pr_number, body)` as a simpler alternative to `review_pr` for posting non-review comments.
    - Add `delete_comment(token, repo_name, comment_id)` to support removing obsolete bot comments.
- [ ] Create `openqabot/gitea_commenter.py` with `GiteaCommenter` class inheriting from `BaseCommenter`.
- [ ] Implement `gitea_comment(self, sub: Submission, msg: str, state: str) -> None`:
    - Extract repository and PR number from `sub.url`.
    - Fetch comments using `get_json` on the `comments_url`.
    - Use `CommentAPI.add_marker` (from `openqabot.osclib.comments`) to tag comments with `openqa` and the current `state`.
    - Implement deduplication:
        - Convert Gitea's list of comments to a dictionary format compatible with `CommentAPI.comment_find`.
        - Use `comment_find` to identify previous bot comments.
        - Skip posting if the new message is too similar to the existing one.
        - Delete previous bot comments if a new one is needed.
    - Post the new comment using `loader.gitea.add_comment`.

## 4. Verification & Testing
- [ ] **Unit Tests**:
    - Create `tests/test_gitea_commenter.py` with extensive mocking of the Gitea API.
    - Verify that `BaseCommenter` methods remain correct for both `Commenter` and `GiteaCommenter`.
    - Test the deduplication logic specifically for Gitea comments.
- [ ] **Integration Tests**:
    - Run `qem-bot sub-comment` with `--dry` and `--fake-data` to ensure the correct flow for `git` submissions.
- [ ] **Code Quality**:
    - Run `make tidy`, `make checkstyle`, and `make typecheck-ty`.
    - Run `make test-with-coverage` and ensure 100% coverage for new/modified files.

## 5. Documentation
- [ ] Update README or internal documentation if necessary.
