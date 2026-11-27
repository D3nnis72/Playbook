# Phase 05: Parallel Bot Review & CI Triage Child Playbook

You are a fresh-context child spawned asynchronously by the Orchestrator whenever `watch_pull_request` wakes it up with automated review comments (e.g., Kira, Codex, Bugbot) or failing CI checks on an open PR. Other PRs continue running in parallel.

## Steps

1. **Inspect PR & CI:**
   - Call `pull_request_read` on `pr_url` to read all review comments, threads, and check statuses.
   - Call `ci_logs` on any failed check run to inspect the exact failure.
2. **Triage every review comment honestly (no blind bloat):**
   - Verify each claim against live code and the PR Contract Card.
   - **Valid P1 / P2 (MUST fix):** Real bug, edge case, missing test, convention/lint/type/OpenAPI/translation defect, or CI failure.
   - **False positive / Out-of-scope / P3 (DO NOT add speculative code):** Invented edge cases prevented by invariants or scope outside the PR Card.
   - **Cross-PR Insights:** If a bot (like Kira sampling staging/prod DBs) surfaces a genuine insight relevant to a **later** PR, capture it in your summary so the Orchestrator records it in `state.json` and the affected downstream card.
3. **Apply fixes & re-verify:**
   - Fix all valid P1/P2 findings and CI failures in the PR worktree (if a fix requires editing files outside `Allowed write files` / external subsystems, report `EXTERNAL_FIX_NEEDED` instead of expanding scope).
   - Re-run affected local gates (changed-files-only `ruff format --check` for `.py`).
   - Follow repo `squash`/`push` conventions as appropriate and push to the PR branch.
4. **Respond clearly on the PR and sync labels:**
   - Use `pull_request_respond` to reply concisely on every addressed thread with the fix commit SHA, or a 1-sentence factual explanation when skipped.
   - If a failed check was a transient CI flake unrelated to the diff, call `ci_rerun` once.
   - Once all required CI checks are green and bot review (`kira-the-beagle`) has approved with 0 unresolved P1/P2 threads:
     - Ensure PR assignee (`@me`) is set.
     - Check `mergeStateStatus` and Darkplane AutoMerge: if `mergeStateStatus == "BLOCKED"` (human `CODEOWNERS` review still needed), add label `ready-for-review` (plus `Core Approval` only if a core path was touched) and report `human_approval_needed=yes` with the exact pending reviewers so the Orchestrator adds the PR to `APPROVAL-QUEUE.md`. If `mergeStateStatus == "CLEAN"` (Darkplane satisfied mergeability without human approval), report `human_approval_needed=no`.
5. **Never call `watch_pull_request` yourself:** The Orchestrator owns the persistent watch.

## Required Final Line

`PR <full URL>, head <SHA>, checks and reviews <state> | fixed_p1_p2=<N> | skipped=<M> | ci_fixed=<yes|no|none> | human_approval_needed=<yes|no> | downstream_notes=<none or short summary>`
