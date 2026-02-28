# Execution Plan: Replace commitizen with gitlint for commit message checks

## Goal
Replace the current git commit message checks performed by `commitizen` with `gitlint`, ensuring it uses the `contrib-title-conventional-commits` rule. This aligns with the availability of `python3-gitlint` on openSUSE and provides a simpler configuration.

## Proposed Changes

### 1. Configuration: `.gitlint`
Create a `.gitlint` file at the root of the repository to configure `gitlint`.
```ini
[general]
# Enable the conventional commits contrib rule
contrib=contrib-title-conventional-commits
```

### 2. GitHub Actions: `.github/workflows/ci.yml`
Update the `lint-commits` job to use `gitlint` instead of `commitizen`.
- Update the job steps to install `gitlint` using `uv tool install gitlint`.
- Use `gitlint` to check the commit range in pull requests.

### 3. Pre-commit hooks: `.pre-commit-config.yaml`
Replace the `commitizen` hook with a `gitlint` hook to maintain local commit message validation.
- Remove the `commitizen-tools/commitizen` repository entry.
- Add the `jorisroovers/gitlint` repository entry.

### 4. Dependencies: `pyproject.toml`
Update the development dependencies and remove `commitizen` specific configuration.
- Remove `commitizen` from `dev` dependencies in `[dependency-groups]`.
- Add `gitlint` to `dev` dependencies.
- Remove the `[tool.commitizen]` section.

### 5. Documentation
- Verify if `doc/development.md` needs any updates regarding commit message rules (though it currently points to an external resource which is still valid).

## Verification Plan

### Local Verification
1. Run `uv sync` to update the virtual environment.
2. Manually test `gitlint` on the current branch:
   ```bash
   uv run gitlint --commits HEAD~1..HEAD
   ```
3. Test pre-commit hook installation:
   ```bash
   make setup-hooks
   ```
4. Verify that a non-conventional commit message fails (using a temporary commit).

### CI Verification
1. Push the changes and ensure the `lint-commits` job in GitHub Actions passes for the PR commits.
2. Ensure other CI jobs still pass.
