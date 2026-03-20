# Task: Address `PLR0913` in `openqabot/args.py` using `typer.Depends` and `typer.Context`

The goal is to fix `PLR0913` (too many arguments) violations in `openqabot/args.py` by grouping CLI options using `typer.Depends` and leveraging `typer.Context` for managing global state.

## 1. Context and Analysis
Currently, several functions in `openqabot/args.py` have too many arguments, leading to `PLR0913` violations that are suppressed with `# noqa: PLR0913`.
- `main` callback: ~11 arguments.
- `increment_approve` command: ~14 arguments.

## 2. Plan

### Step 1: Group Global Options in `main`
1. Define a dependency function `global_options_dep` in `openqabot/args.py`.
2. Move all arguments from `main` (except `ctx`) to `global_options_dep`.
3. Ensure all `Annotated` and `typer.Option` definitions are preserved exactly to keep the CLI interface unchanged.
4. Have `global_options_dep` return a `SimpleNamespace` containing all the options.
5. Update `main` to accept `ctx: typer.Context` and `options: Annotated[SimpleNamespace, typer.Depends(global_options_dep)]`.
6. Update `main` body to use `options` and store it in `ctx.obj`.
7. Remove `# noqa: PLR0913` from `main`.

### Step 2: Group Options in `increment_approve`
1. Identify logical groups of options for `increment-approve`:
    - **Project Settings**: `project_base`, `build_project_suffix`, `diff_project_suffix`, `build_listing_sub_path`.
    - **Product Filters**: `distri`, `version`, `flavor`, `product_regex`.
    - **Scheduling & Logic**: `schedule`, `reschedule`, `accepted`, `request_id`, `increment_config`, `build_regex`.
2. Define dependency functions for each group (e.g., `project_options_dep`, `product_filter_options_dep`, `scheduling_options_dep`).
3. Update `increment_approve` signature to use these dependency functions with `typer.Depends`.
4. Update `increment_approve` body to unpack these options into `ctx.obj` (maintaining current behavior of `args = ctx.obj` and adding to it).
5. Remove `# noqa: PLR0913` from `increment_approve`.

### Step 3: Verify CLI Interface
1. Run `python qem-bot.py --help` and compare with the previous output to ensure no changes in option names, flags, defaults, or help messages.
2. Run `python qem-bot.py increment-approve --help` and verify similarly.
3. Verify that `envvar` support still works as expected.

### Step 4: Quality Checks
1. Run `ruff check openqabot/args.py --select PLR0913` to confirm the violations are gone.
2. Run `make tidy` to ensure formatting and style are correct.
3. Run `make typecheck-ty` to ensure type hints are valid.
4. Run `make test` to ensure no regressions in argument handling.

## 3. Anticipated Challenges
- Ensuring `typer` correctly displays all options in `--help` when they are grouped via `Depends`. According to Typer documentation, this should work as long as `Depends` is used in the command/callback signature.
- Maintaining exact compatibility with `envvar` and `help` strings.
