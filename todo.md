_Note:_ Not appearing numbers mean already done tasks, moved to
tasks/completed/

_Howto:_ For every numbered task create an according implementation planning
document in tasks/ in a numbered fashion, e.g. "11. my task" ->
"tasks/011_my_task.md" and inform the user. Do not execute the plan without
confirmation.

10. *DONE* review comments in https://github.com/openSUSE/qem-bot/pull/364 ask
    for documentation for config variables in openqabot/config.py as well as
        for the feature in general. Extend the user facing documentation as
            well as developer facing in-file comments.
11. *DONE* 011_bot_inc-sync-results_.log is a full log of one
    "inc-sync-results" which is very big. We should reduce the verbosity of
    log entries, e.g.  bundling the information about individual openQA job
    references together.
15. *DONE* qem-bot outputs log messages like "Found product increment request
    on SUSE:SLFO:Products:SL-Micro:6.2:ToTest: 399766". The bare number at the
    end should be logged as full URL for convience. In this case 399766
    relates to https://build.suse.de/request/show/399766. Improve the log
    message to yield the full URL based on the the according variables or
    config variables pointing to the right server.
26. *PLANNED*
27. *PLANNED* Cleanup of unwanted test results: When openQA test reviewers
    remove not-ok openQA jobs that are already in the qem-dashboard database
    completely those shadow references block the approval of submissions.
    Find more details about this topic in
    * https://github.com/openSUSE/qem-dashboard/issues/61
    * https://progress.opensuse.org/issues/109310
    * https://progress.opensuse.org/issues/113345

    Normally this should not happen due to automatic cleanup of old test
    results.  For manual cleanup it is possible to delete such results from
    the database manually, e.g. to cleanup "Leap" jobs in the development job
    group, id 432:

    ```
    ssh root@qam.suse.de
    machinectl shell postgresql
    sudo -u postgres psql dashboard_db
    delete from openqa_jobs where flavor ~ 'Leap' and version = '15.4' and group_id=432;
    ```

    what I did to manually patch now for another case was `select * from
    openqa_jobs where build=':git:2161:podman' and status!='passed';` for
    ":git:2161:podman". We should automatically handle such cases, e.g. if
    qem-dashboard states that such jobs would block approval but the actual
    openQA jobs do not exist anymore.
28. *PLANNED* https://progress.opensuse.org/issues/196820 "comment in gitea
    PRs pointing to openQA test results"
29. *DONE* tests were pretty fast with execution within 1-2s but recently many
    more tests were added and test runtime unfortunately increased
    significantly with `make test` taking about 4s and `make
    test-with-coverage` around 10s for me. Optimize the runtime with runtime
    optimizations in the overall test execution, individual tests, more
    high-level mocking, etc., to decrease overall runtime but keeping
    sufficient statement and branch coverage.
30. *PLANNED* gitea comments
