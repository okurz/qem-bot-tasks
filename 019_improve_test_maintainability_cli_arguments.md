# Task: Improve CLI Argument Maintainability and Type Safety

## Objective
Refactor `openqabot/args.py` to eliminate redundant configuration checks (DRY), replace brittle "white-box" help detection with idiomatic `typer` patterns, and improve type safety for the shared context object.

## Research Phase
- [ ] Identify all commands in `openqabot/args.py` that perform the `configs.is_dir()` check.
- [ ] Investigate `typer`'s `is_eager` flag or `callback` order to see if `token` validation can be handled natively without breaking `--help`.
- [ ] Verify if `ctx.invoked_subcommand` can be used to skip validation for specific commands (e.g., `amqp` if it doesn't need the token, though currently it seems to).

## Strategy Phase
1. **Centralize Validation**: Move the `Path.is_dir()` check for `configs` into the `main` callback.
2. **Refactor Context Object**: Replace `SimpleNamespace` with a `dataclass` or `TypedDict` to provide better IDE support and type checking.
3. **Idiomatic Help Handling**: Refactor the manual `sys.argv` check for help options. If `token` is truly mandatory for all subcommands except help, explore using a custom validator or handling it within the context of the subcommand execution.
4. **Test Simplification**: Transition `tests/test_openqabot.py` from mocking `sys.argv` and `ctx` to using `CliRunner.invoke()`, which naturally handles the CLI lifecycle.

## Execution Phase

### Step 1: Centralize Configuration Directory Check
- [ ] Modify `openqabot.args.main` to perform the `configs.is_dir()` check immediately after parsing.
- [ ] Remove the redundant check from all `@app.command()` functions (`full_run`, `submissions_run`, `smelt_sync`, etc.).

### Step 2: Implement Type-Safe Context Object
- [ ] Define a `BotArgs` dataclass in `openqabot/args.py` (or a separate types file).
- [ ] Update `ctx.obj` assignment in `main` to use this dataclass.
- [ ] Update type hints in subcommands to reflect the new object type.

### Step 3: Refactor Token/Help Logic
- [ ] Attempt to use `typer.Option(..., show_default=False)` or similar for the token if it helps with the "required but not for help" issue.
- [ ] Alternatively, move the token check to a point where `typer` has already determined if help is being shown.

### Step 4: Update Tests
- [ ] Refactor `test_main_missing_token_with_help_returns_early` to use `CliRunner`.
- [ ] Ensure all coverage restored in the previous commit is maintained with the new, cleaner implementation.

## Validation Phase
- [ ] Run `make tidy` to ensure formatting is consistent.
- [ ] Run `make checkstyle` to verify maintainability metrics (radon) and linting (ruff).
- [ ] Run `make typecheck-ty` to confirm the new dataclass improves type safety.
- [ ] Run `make test-with-coverage` to ensure no regressions and 100% coverage.
