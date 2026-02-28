Motivation

Based on bigger discussion in SUSE Slack #discuss-qa-maintenance https://suse.slack.com/archives/C02CLB8TZP1/p1771584214364009 brought up by @mmeissn. https://src.suse.de/products/SLFO/pulls/2247 and later SLFO PRs are not properly tested by openQA anymore as the format for OBS repo information comments was changed. We need to ensure that qem-bot can parse the relevant data, triggers according openQA tests again and approves PRs as before.
Acceptance criteria

    AC1: Recent SLFO PRs (2200+) are properly evaluated and processed by qem-bot
    AC2: https://src.suse.de/products/SLFO/pulls/2247 is processed with priority

Suggestions

    Follow https://github.com/openSUSE/openSUSE-git/issues/264 which tracks the regression from openSUSE-git side which caused a change of behaviour, in particular in https://src.opensuse.org/git-workflow/autogits/blame/branch/main/obs-staging-bot/main.go#L741
    There was a recent change to qem-bot https://github.com/openSUSE/qem-bot/pull/391, commits 16c27c3 and 5b32727, which does not seem to fix the problem referencing in particular https://src.suse.de/products/SLFO/pulls/2247 and maybe even introduces a regression

Add
