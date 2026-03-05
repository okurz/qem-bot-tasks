## Issue #196820: [qem-bot] comment in gitea PRs pointing to openQA test results
- Status: Blocked
- Priority: Normal
- Assignee: asmorodskyi
- URL: https://progress.opensuse.org/issues/196820

### Description
## Motivation
We failed putting comments on OBS submit requests from qem-bot years ago (even though nowadays in OBS it's possible to update comments) but in gitea it's so much easier. The spike solution #192427 showed how qem-bot can comment on gitea PRs. Do it production grade for all gitea PRs.

## Acceptance criteria
* **AC1:** qem-bot posts links to openQA build results for each gitea PR that it triggered tests for
* **AC2:** qem-bot does not write any duplicate information into gitea PRs (no spam!)

## Suggestions
* Read what was done in #192427 in particular
https://github.com/openSUSE/qem-bot/compare/master...r-richardson:qem-bot:gitea_staging_tests_poo192427#diff-8e0562a6d7068b57635c0570dc2ac22e01dfd638037a863c8a0e84e00a74ca00R100
 how to post comments
* Take a look into existing functionality that writes non-duplicate comments on OBS and apply the same for gitea
* Feel free to experiment on https://src.suse.de/products/SLFO/pulls/2068
* Just put a simple link to the related build, e.g.https://openqa.suse.de/tests/overview?distri=sle&version=16.1&build=PR-2068-SLES-16.1-Full-x86_64-Build3.3.install.iso&groupid=714 from https://src.suse.de/products/SLFO/pulls/2068
* Refer:
      - https://docs.gitea.com/api/1.25/ 
      - https://docs.gitea.com/api/1.25/#tag/issue/operation/issueGetRepoComments


## Out of scope
badges in openQA which show build results . For now just make it simple and link to all

### Journals
#### okurz at 2026-02-20T12:24:33Z
#192268
--------------------
