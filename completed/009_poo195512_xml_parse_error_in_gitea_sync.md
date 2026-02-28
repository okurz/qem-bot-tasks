# Fix XML parse error in gitea-sync

## Problem
In `openqabot/loader/gitea.py`, the function `add_packages_from_patchinfo` attempts to parse the content of a `_patchinfo` file fetched from Gitea. If the response is not valid XML (e.g., a Gitea error page or empty response), `osc.util.xml.xml_fromstring` raises an `xml.etree.ElementTree.ParseError`, which is currently caught by a broad `except Exception` in `make_submission_from_gitea_pr`, but it logs a full traceback and might be better handled closer to the source.

## Proposed Changes

### 1. openqabot/loader/gitea.py
- Import `xml.etree.ElementTree` to catch `ParseError`.
- In `add_packages_from_patchinfo`:
    - Perform the request and check for success.
    - Wrap the XML parsing in a `try-except` block to catch `xml.etree.ElementTree.ParseError` and `requests.RequestException`.
    - Log with level info if parsing fails and skip the file.

### 2. Testing
- Create a new test case in `tests/test_loader_gitea_submissions.py` (or a new test file) that mocks a `_patchinfo` request returning invalid XML.
- Verify that `qem-bot` continues processing other PRs instead of failing with a traceback (though it's already caught by a broad exception, we want to handle it more gracefully).

## Detailed Steps

1. **Reproduction:**
   - Create a test case that mocks `retried_requests.get` to return a 404 or a non-XML string when fetching `_patchinfo`.
   - Observe the current behavior (traceback in logs).

2. **Implementation:**
   - Update `openqabot/loader/gitea.py`:
     ```python
     import xml.etree.ElementTree as ET
     ...
     def add_packages_from_patchinfo(...):
         try:
             response = retried_requests.get(patch_info_url, verify=False, headers=token)
             response.raise_for_status()
             patch_info = osc.util.xml.xml_fromstring(response.text)
             submission["packages"].extend(res.text for res in patch_info.findall("package"))
         except (ET.ParseError, requests.RequestException) as e:
             log.error("Failed to parse patchinfo from %s: %s", patch_info_url, e)
     ```
   - Actually, `osc.util.xml.xml_fromstring` might raise other errors depending on `osc` version.

3. **Verification:**
   - Run `pytest tests/test_loader_gitea_submissions.py`.
   - Run `make tidy checkstyle typecheck-ty test-with-coverage`.
