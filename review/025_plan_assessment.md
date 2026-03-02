# Assessment of Plan Documents for poo#193690

## Issue Summary

All 5 plans address the same issue: qem-bot incorrectly references old/cloned openQA jobs in `inc-approve`, causing false negatives where the bot reports a job as failed when it's actually green in openQA.

## Plans Reviewed

| Plan File | Lines | Key Approach | Technical Depth |
|-----------|-------|--------------|-----------------|
| `025_big_pickle.md` | 67 | General investigation | Low - vague steps |
| `025_minimax_m25_free.md` | 66 | Follow clone chain in openQA API | Medium - mentions openQA clone API |
| `025_poo193690_wrong_openqa_jobs_referenced_in_sub_approve.md` | 49 | Keep only highest `job_id` per scenario | Medium - has code snippet |
| `025_trinity_large.md` | 108 | Use most recent scenario reference | Medium - verbose but lacks HOW |
| `025_opus_46.md` | ~200 | Deduplicate by `name` (scenario), keep highest `job_id` | **Very High** - deep code analysis |

---

## Key Differences

### 1. Root Cause Understanding

| Plan | Root Cause Assumption |
|------|----------------------|
| `big_pickle`, `minimax_m25_free`, `trinity_large` | Assume the problem is that the bot looks up the **wrong job** (e.g., looks up t20252358 instead of t20256065) |
| `poo193690_md`, `opus_46` | Correctly identify the problem is that the bot checks **ALL jobs** returned by dashboard with `all()` — both the old failed job AND the new passed clone coexist in the response |

### 2. Fix Strategy

| Plan | Strategy | Complexity |
|------|----------|------------|
| `minimax_m25_free` | Follow clone chain via openQA API | Complex - requires extra API calls |
| `poo193690_md` | Simple `max(job_results, key=lambda x: x["job_id"])` — takes highest job_id | Simple |
| `opus_46` | Group by `name` (scenario) first, then keep highest job_id per group | Medium - handles multiple scenarios under same settings_id |

### 3. Actionability

| Plan | Provides | Missing |
|------|----------|---------|
| `poo193690_md` | Actual code to implement | Test fixtures, quality gate steps |
| `opus_46` | Full phase-by-phase plan with tests, quality gates, atomic commits | Nothing significant |
| `trinity_large` | Risk, rollback, timeline | HOW to implement - too vague |
| `minimax_m25_free` | 3 options (A/B/C) | Decision, complexity may be overkill |
| `big_pickle` | Only investigation steps | Solution design |

---

## Final Verdict Rating (Best → Worst)

### 1. `025_opus_46.md` — **BEST**

- Deepest technical analysis from actual codebase exploration
- Correct root cause (all jobs checked, not clone lookup)
- Complete plan: reproducer test → deduplication fix → unit tests → quality gates → atomic commits
- Considers alternatives and risks
- Lines up with actual code at `approver.py:343`

### 2. `025_poo193690_wrong_openqa_jobs_referenced_in_sub_approve.md` — **GOOD**

- Correct high-level fix (highest job_id)
- Has actual code snippet
- Missing: test fixtures, quality gate steps, edge case handling

### 3. `025_trinity_large.md` — **FAIR**

- Most detailed structure (risk assessment, rollback plan, timeline)
- But "follow clone chain" is vague — doesn't explain HOW to implement
- Timeline (11-16h) seems overestimated for a simple deduplication fix

### 4. `025_minimax_m25_free.md` — **FAIR**

- Mentions 3 implementation options (A/B/C)
- Suggests following clone chain via openQA API — more complex than needed
- Good exploration but lacks final decision

### 5. `025_big_pickle.md` — **WEAKEST**

- Only investigation steps, no solution design
- Too vague to execute
- Checkboxes without specifics

---

## Recommendation

**Use `025_opus_46.md`** as the execution plan. It is the only plan that:

- Correctly identifies the root cause from actual code analysis
- Provides a concrete, testable fix with deduplication logic
- Includes full test strategy and quality gates
- Has been validated against the actual `approver.py:get_jobs()` implementation

The fix in `opus_46` adds a `_deduplicate_jobs_by_scenario()` static method to `Approver` that keeps only the job with the highest `job_id` per unique `name` field (which represents the scenario). This is:
- Self-contained within qem-bot
- Simple and auditable
- Consistent with how openQA assigns job IDs (monotonically increasing)
- Requires no dashboard changes

---

## Technical Background (from code analysis)

The root cause is in `openqabot/approver.py` at line 343:

```python
return all(self.is_job_acceptable(sub, api, r) for r in job_results)
```

This checks **every** job returned by the dashboard for a given `settings_id`. When a failed job gets cloned as a passing job, **both** records coexist in the dashboard — the `all()` fails because the old failed job is still present. There is zero deduplication by scenario in the current implementation.

The deduplication approach in `opus_46` solves this by keeping only the most recent job (highest `job_id`) for each unique scenario (`name` field).
