_Note:_ Not appearing numbers mean already done tasks, moved to
tasks/completed/

_Howto:_ For every numbered task create an according implementation planning
document in tasks/ in a numbered fashion, e.g. "11. my task" ->
"tasks/011_my_task.md" and inform the user. Do not execute the plan without
confirmation.

26. *PLANNED* gitea priorities along with smelt
34. Run all qem-bot commands in dry-mode as integration tests in Makefile part
    of CI, e.g. in github PRs before merge. Compare to "make
    test-all-commands-unstable"
35. Follow-up on
    https://github.com/openSUSE/qem-bot/pull/429#pullrequestreview-3920665752
    questioning the decision to extract a function "get_product_version" when
    it is not clear how exactly a product version is extracted and also the
    returned type is "str". Can we harden this? Maybe with a specific type?
36. Based on
    https://suse.slack.com/archives/C02AJ1E568M/p1773154561834589?thread_ts=1773150152.787119&cid=C02AJ1E568M
    Only expect assets and trigger openQA tests when a configurable list of
    reviewers have approved, defaulting to "autogits_obs_staging_bot" and
    "sle_installcheck_bot". Triggering openQA tests when assets are incomplete
    or packages don't install should be avoided.
