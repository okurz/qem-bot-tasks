# Execution Plan - Task 15: Improve Request Logging with Full URLs

The goal is to improve the log messages when an OBS request is handled by displaying the full URL to the request (e.g., `https://build.suse.de/request/show/399766`) instead of just the ID. The base URL should be derived dynamically from the OBS API URL, which in turn should default to the one configured in `osc`.

## Proposed Changes

### 1. Configuration Update

Modify `openqabot/config.py` to:
1.  Derive the default `obs_url` from `osc` configuration if not provided.
2.  Add a property `obs_web_url` to the `Settings` class that maps the API URL to the corresponding web UI URL.

- **File**: `openqabot/config.py`
- **Action**:
    - Add `import osc.conf` (handle potential import errors or missing config).
    - Update `obs_url` default to a factory method or a property that checks `osc` config.
    - Add `obs_web_url` property to `Settings` class.

#### Heuristic for `obs_web_url`:
- `https://api.suse.de` -> `https://build.suse.de`
- `https://api.opensuse.org` -> `https://build.opensuse.org`
- General rule: replace `api.` with `build.` in the hostname.

```python
# openqabot/config.py

def get_default_obs_url() -> str:
    try:
        import osc.conf
        osc.conf.get_config()
        if apiurl := osc.conf.config.get('apiurl'):
            return apiurl
    except Exception:
        pass
    return "https://api.opensuse.org"

class Settings(BaseSettings):
    # ...
    obs_url: str = Field(default_factory=get_default_obs_url, alias="OBS_URL")

    @property
    def obs_web_url(self) -> str:
        return self.obs_url.replace("api.", "build.")
```

### 2. Update Logging in Increment Approver

Update the log messages in `openqabot/incrementapprover.py` to use the full URL from `settings.obs_web_url`.

- **File**: `openqabot/incrementapprover.py`
- **Action**:
    - Update the `log.info` call in `find_request_on_obs`.
    - Update `id_msg` construction in `handle_approval` to include the full URL.
    - Update other log messages that use bare request IDs.

### 3. Verification Plan

#### Automated Tests
- Extend of the existing test files where most applicable
- Test `get_default_obs_url` with mocked `osc.conf`.
- Test `obs_web_url` property with various API URLs.
- Test `IncrementApprover` log output (mocking `settings.obs_web_url`).

#### Quality Assurance
- Run `make tidy`
- Run `make checkstyle`
- Run `make typecheck-ty`
- Run `make test`

## Rollback Plan
- Revert changes to `openqabot/config.py` and `openqabot/incrementapprover.py` and the extended test
