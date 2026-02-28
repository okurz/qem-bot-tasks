# Task: Implement .env support for local testing

To make `qem-bot.py` easier to call for local testing, we will implement support for `.env` files. This allows developers to set common arguments once in a file rather than repeating them on the command line.

## Goal
Enable `qem-bot.py` to automatically load environment variables from a `.env` file in the current working directory.

## Proposed Changes

### 1. Update Dependencies
- Add `python-dotenv` to the `dependencies` section in `pyproject.toml`. Although it is currently a transient dependency of `pydantic-settings`, explicitly declaring it ensures it remains available if `pydantic-settings` changes its internal dependencies.

### 2. Modify `openqabot/main.py`
- Import `load_dotenv` from `dotenv`.
- Call `load_dotenv()` at the start of the `main()` function. This ensures that any variables defined in a `.env` file are loaded into `os.environ` before `typer` parses the command-line arguments.

### 3. Update `openqabot/args.py`
- Add `envvar` parameters to `typer.Option` for all global options that currently lack them.
- Suggested mapping:
    - `--configs` / `-c`: `envvar="QEM_BOT_CONFIGS"`
    - `--dry`: `envvar="QEM_BOT_DRY"`
    - `--fake-data`: `envvar="QEM_BOT_FAKE_DATA"`
    - `--dump-data`: `envvar="QEM_BOT_DUMP_DATA"`
    - `--debug` / `-d`: `envvar="QEM_BOT_DEBUG"`
    - `--gitea-token` / `-g`: `envvar="QEM_BOT_GITEA_TOKEN"`
    - `--openqa-instance` / `-i`: `envvar="OPENQA_INSTANCE"`
    - `--singlearch` / `-s`: `envvar="QEM_BOT_SINGLEARCH"`
    - `--retry` / `-r`: `envvar="QEM_BOT_RETRY"`

### 4. Create `.env.example`
- Create a template `.env.example` in the project root with the following content:
  ```env
  # QEM-Bot Configuration Template
  QEM_BOT_TOKEN=1234
  QEM_BOT_CONFIGS=metadata/qem-bot
  QEM_BOT_SINGLEARCH=metadata/qem-bot/singlearch.yml
  QEM_BOT_DRY=True
  QEM_BOT_FAKE_DATA=True
  # QEM_BOT_DEBUG=True
  # QEM_DASHBOARD_URL=http://localhost:3000/
  ```

## Verification Plan

### Automated Tests
- Add a new test file `tests/test_dotenv.py` that:
    - Mocks `os.environ`.
    - Creates a temporary `.env` file.
    - Verifies that `main()` correctly triggers the loading of these variables into the app context.

### Local Manual Verification
1. Copy `.env.example` to `.env`.
2. Edit `.env` to set specific values (e.g., `QEM_BOT_DRY=True`).
3. Run `python3 qem-bot.py --help`.
4. Check if the default values displayed in the help message (where applicable) or the behavior of the bot reflects the settings in `.env`.
5. Run a command like `python3 qem-bot.py smelt-sync` and verify it respects the `DRY` and `FAKE_DATA` flags from `.env`.

## Code Quality
- Run `make tidy` to ensure formatting is correct.
- Run `make checkstyle` and `make typecheck` to verify no regressions.
- Run `make test` to ensure all existing tests pass.
