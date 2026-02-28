# Task: Replace commitizen with gitlint for commit message checks

## Request
In this task, replace the current git commit checks by gitlint from the package python3-gitlint as that package is available in openSUSE. Use a simple .gitlint file that enables only `contrib=contrib-title-conventional-commits`, nothing else should be needed. Migrate the according GHA as well.

## Execution Plan
See [017_gitlint_git_commit_execution_plan.md](017_gitlint_git_commit_execution_plan.md)
