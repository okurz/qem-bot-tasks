# Plan for Task 35: get_product_version strict type

## Motivation
Address the feedback from PR #429 (https://github.com/openSUSE/qem-bot/pull/429#pullrequestreview-3920665752) regarding the ambiguity of the `get_product_version` functions. The reviewer requested a clear definition of what a product version is and what formats it can take, and questioned the decision to return a simple `str` instead of a stricter type. We will harden the type by introducing a validated `ProductVersion` string subclass, and replace the ambiguous `""` (empty string) return values with `None`.

## Design Choices
1. **New Type `ProductVersion`**:
   - Create a `ProductVersion` class in `openqabot/types/types.py` that inherits from `str`.
   - Implement validation in its `__new__` method to enforce the format `r"^[.\d]+$"`, rejecting arbitrary strings. This provides runtime guarantees and explicitly documents what constitutes a valid product version.
2. **Move Regex**:
   - Move `VERSION_EXTRACT_REGEX` from `openqabot/loader/gitea.py` to `openqabot/types/types.py` so it can be used for the `ProductVersion` validation.
3. **Replace `""` with `None`**:
   - Update extraction functions in `openqabot/loader/gitea.py` (`_extract_version`, `get_product_version_from_repo_listing`, `_get_product_version`) to return `ProductVersion | None` instead of an empty string when the version is missing or invalid.
   - Update `get_product_name_and_version_from_scmsync` to return `tuple[str, ProductVersion | None]`.
4. **Refactor dependent code**:
   - Update usages (e.g., `add_channel_for_build_result` and `_get_product_version`) to check `is not None` instead of checking string length.
5. **Update tests**:
   - Update existing test assertions and mocks (e.g., `test_loader_gitea_helpers.py`) to expect `None` instead of `""`.
   - Add dedicated unit tests for `ProductVersion` to ensure it correctly validates and rejects invalid strings.

## Execution Steps
1. **Implement `ProductVersion`**:
   - Edit `openqabot/types/types.py`:
     - Move `VERSION_EXTRACT_REGEX = re.compile(r"[.\d]+")` here.
     - Add `class ProductVersion(str):` with `__new__` that runs `VERSION_EXTRACT_REGEX.fullmatch(value)`. If it fails, raise `ValueError(f"Invalid product version format: '{value}'")`.
2. **Update `openqabot/loader/gitea.py`**:
   - Import `ProductVersion` and `VERSION_EXTRACT_REGEX` from `openqabot.types.types`.
   - Refactor `_extract_version` to: `return next((ProductVersion(part) for part in remainder.split("-") if VERSION_EXTRACT_REGEX.fullmatch(part)), None)`
   - Refactor `get_product_version_from_repo_listing` to return `ProductVersion | None`, returning `None` instead of `""` on exceptions or when not found.
   - Refactor `get_product_name_and_version_from_scmsync` to return `(m.group(1), ProductVersion(m.group(2)))` if match, else `("", None)`.
   - Refactor `_get_product_version` to use `pv is not None` checks.
   - In `add_channel_for_build_result`, check `if product_version is not None:`.
3. **Adapt existing types & usages (if needed)**:
   - Check if `Repos`, `ProdVer`, etc. need their `product_version: str` updated to `ProductVersion | str`, or if they can remain `str` for now. (Given they default to `""`, leaving them as `str` is fine unless we want a deeper refactoring, but at minimum the `get_product_version` functions will be hardened).
4. **Update Tests**:
   - Modify `tests/test_loader_gitea_helpers.py`: change `res == ""` to `res is None`.
   - Modify `tests/test_giteasync.py`: update `get_product_name_and_version_from_scmsync` assertions.
   - Create `tests/test_types.py` (if not exists) and add tests for `ProductVersion` ensuring correct instantiation and `ValueError` on bad formats.
5. **Verification**:
   - Run `make typecheck-ty`
   - Run `make test`
   - Run `make checkstyle`
   - Ensure 100% coverage on modified files.
