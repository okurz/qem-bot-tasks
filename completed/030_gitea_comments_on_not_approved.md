# Plan for Task 030: Gitea Comments on Not Approved PRs

## Status
* **Goal:** Implement functionality for `qem-bot` to post openQA test results as comments on Gitea Pull Requests.
* **Ticket:** [poo#196820](https://progress.opensuse.org/issues/196820)
* **Constraints:**
    * Avoid duplicate comments (spam).
    * Edit existing comments if status updates, or delete/repost smartly.
    * Use a format similar to OBS comments but adapted for Gitea.
    * Do not block approval; this is for information/feedback.

## 1. Data Availability & Structure
To comment on a PR, the bot needs:
1.  **Gitea Repository Name** (Owner/Repo).
2.  **PR Number**.
3.  **openQA Test Results**.

The `Submission` object currently stores:
*   `id`: PR Number.
*   `project`: Short repo name (e.g., "SLFO").
*   It does *not* explicitly store the full repo name or the Gitea URL in a structured way that guarantees access to the full API path.

### Actions:
*   **Modify `openqabot/loader/gitea.py`:**
    *   Update `make_submission_from_gitea_pr` to ensure the `url` field in the submission dictionary contains the API URL or a parseable URL. (It currently stores `pr["url"]` which is usually the API URL).
*   **Modify `openqabot/types/submission.py`:**
    *   Update `Submission.__init__` to extract and store `self.url` from the input dictionary.
    *   Add a property or helper to `Submission` (or utility) to parse `self.url` into `(owner, repo)` if `self.url` is a Gitea API URL.

## 2. Implementation of GiteaCommenter
Create a new class `GiteaCommenter` in `openqabot/giteacommenter.py` (or similar location) that mimics `openqabot/commenter.py` but targets Gitea.

### Class Structure:
*   **`__init__(self, args)`:**
    *   Initialize with arguments (token, Gitea token, etc.).
    *   Load `Settings`.
*   **`__call__(self)`:**
    *   Fetch submissions from Dashboard (`loader.qem.get_submissions`).
    *   Filter for `type == "git"`.
    *   Iterate through submissions:
        *   Call `self.process_submission(sub)`.
*   **`process_submission(self, sub)`:**
    *   Parse `sub.url` to get `owner` and `repo`.
    *   Fetch openQA results (`loader.qem.get_submission_results`).
    *   Summarize results into a Markdown message (reuse `Commenter.summarize_message` logic or adapt it).
    *   Call `self.update_comment(owner, repo, sub.id, message)`.
*   **`update_comment(self, owner, repo, pr_number, message)`:**
    *   Fetch existing comments for the PR (`loader.gitea.get_json(comments_url(...))`).
    *   Find the bot's previous comment (identify by `config.settings.git_review_bot_user` or a hidden marker in the comment body).
    *   **Duplicate Check:**
        *   If found: compare existing body with new message.
        *   If identical (state hasn't changed): Do nothing.
        *   If different: Update the comment (`PATCH`).
    *   If not found:
        *   Create a new comment (`POST`).

## 3. Integration
*   **Modify `openqabot/args.py`:**
    *   Add a new command `gitea-comment` to the CLI.
    *   Arguments: similar to `sub-comment` (token, gitea-token, dry-run).

## 4. Refactoring (Optional/As Needed)
*   Ensure `openqabot.loader.gitea` exports necessary URL constructors (`comments_url`) and request helpers (`get_json`, `post_json`, `patch_json`? - might need to add `patch_json`).

## 5. Verification Plan
*   **Unit Tests:**
    *   Test `Submission` URL parsing.
    *   Test `GiteaCommenter` logic (mocking Gitea API and Dashboard).
    *   Test duplicate detection (same content vs different content).
*   **Manual/Dry-Run:**
    *   Run with `--dry` against a real Gitea repo/PR to see what it *would* post.

## 6. Detailed Steps
1.  Update `openqabot/types/submission.py` to store `url`.
2.  Create `openqabot/giteacommenter.py` with `GiteaCommenter` class.
3.  Add `patch_json` to `openqabot/loader/gitea.py` if missing.
4.  Implement `gitea-comment` command in `openqabot/args.py`.
5.  Add tests in `tests/test_giteacommenter.py`.
