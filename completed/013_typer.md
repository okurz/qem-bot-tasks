# Task 013: Migrate CLI to Typer

## Objective
Replace `argparse` with `Typer` to modernize the CLI, reduce boilerplate code in `openqabot/args.py`, and integrate tightly with the Pydantic settings model established in Task 012.

## Dependencies
- `typer`

## Detailed Steps

### 1. Update Project Dependencies
Modify `pyproject.toml` to add `typer` to the `dependencies` list.

### 2. Refactor `openqabot/args.py` (The CLI Definition)
The current `args.py` contains both argument parsing logic (`get_parser`) and command implementation logic (`do_*` functions).

**Strategy:**
1. Initialize a `typer.Typer` app instance.
2. Convert each `do_*` function into a `@app.command()` decorated function.
3. Replace `argparse.Namespace` arguments with explicit, typed function signatures.
4. Use `typer.Option` and `typer.Argument` to define CLI flags.
5. Use `Annotated` type hints for better metadata support.

**Command Mapping:**
- `full-run` -> `do_full_schedule`
- `submissions-run` -> `do_submission_schedule`
- `updates-run` -> `do_aggregate_schedule`
- `smelt-sync` -> `do_sync_smelt`
- `gitea-sync` -> `do_sync_gitea`
- `sub-approve` -> `do_approve`
- `sub-comment` -> `do_comment`
- `sub-sync-results` -> `do_sync_sub_results`
- `aggr-sync-results` -> `do_sync_aggregate_results`
- `increment-approve` -> `do_increment_approve`
- `repo-diff` -> `do_repo_diff_computation`
- `amqp` -> `do_amqp`

**Handling Global Options:**
Global options like `--token`, `--debug`, `--dry` need to be handled via a callback on the main `app` callback to ensure they are available to all subcommands.
```python
@app.callback()
def main(
    ctx: typer.Context,
    token: str = typer.Option(..., envvar="QEM_BOT_TOKEN"),
    debug: bool = False,
    # ...
):
    # Store global state in ctx.obj or configure logging here
    pass
```

### 3. Integrate with Pydantic Settings
Ensure that CLI options can override the Pydantic settings defaults.
- For options that map directly to settings (like `token` or `openqa_instance`), use the `envvar` parameter in `typer.Option` to respect the same environment variables, OR allow the `Settings` object to be updated by the CLI values before the logic runs.

### 4. Update Entry Point
Refactor `openqabot/main.py`.
- **Current:** Calls `get_parser()`, parses args, and invokes `args.func(args)`.
- **New:** Simply calls `app()`.

```python
# openqabot/main.py
from .args import app

def main():
    app()
```

### 5. Cleanup
- Remove `get_parser` and `argparse` imports from `openqabot/args.py`.

### 6. Verification
- Run `python qem-bot.py --help` to verify the help text is generated correctly.
- Check individual command help, e.g., `python qem-bot.py full-run --help`.
- Run a dry-run command to ensure arguments are passed correctly to the logic functions.
