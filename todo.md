_Note:_ Not appearing numbers mean already done tasks, moved to
tasks/completed/

_Howto:_ For every numbered task create an according implementation planning
document in tasks/ in a numbered fashion, e.g. "11. my task" ->
"tasks/011_my_task.md" and inform the user. Do not execute the plan without
confirmation.

10. *DONE* review comments in https://github.com/openSUSE/qem-bot/pull/364 ask for
    documentation for config variables in openqabot/config.py as well as for
    the feature in general. Extend the user facing documentation as well as
    developer facing in-file comments.
11. *DONE* 011_bot_inc-sync-results_.log is a full log of one "inc-sync-results"
    which is very big. We should reduce the verbosity of log entries, e.g.
    bundling the information about individual openQA job references together.
15. *DONE* qem-bot outputs log messages like "Found product increment request on
    SUSE:SLFO:Products:SL-Micro:6.2:ToTest: 399766". The bare number at the
    end should be logged as full URL for convience. In this case 399766
    relates to https://build.suse.de/request/show/399766. Improve the log
    message to yield the full URL based on the the according variables or
    config variables pointing to the right server.
