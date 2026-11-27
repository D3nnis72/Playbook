# Phase 05: Parallel Bot Review & CI Triage Child Playbook

You are a fresh-context child spawned asynchronously by the Orchestrator whenever `watch_pull_request` wakes it up with automated review comments (e.g., Kira, Codex, Bugbot) or failing CI checks on an open PR. Other PRs continue running in parallel.

## Steps

1. **Inspect PR & CI:**
   - Call `pull_request_read` on `pr_url` to read all review comments, threads, and check statuses.
   - Call `ci_logs` on any failed check run to inspect the exact failure.
2. **Triage every review comment honestly (no blind bloat, no silent skips):**
   - Read BOTH inline review threads AND top-level review bodies (e.g., Kira's numbered follow-ups even when she says `"I'd merge this"`).
   - Verify each claim against live code and the PR Contract Card, and classify into one of three dispositions:
     - **Fix now (in this PR):** Real bug, P1/P2 foundation/convention defect that is cheapest to fix here (e.g., wrong Shell V2 table, fail-closed router default, broken link styling, wrong German declension), or CI failure.
     - **Defer to a planned downstream PR (valid, belongs later):** Write the exact requirement/note onto the owning downstream PR card (`cards/PR-XX-*.md`) and `state.json`, and cite that exact PR ID in your reply on GitHub so reviewers and Kira see where it is handled.
     - **Skip (false positive / P3 nit / out-of-scope):** Explain in 1 factual sentence in your reply on GitHub; never add speculative code.
3. **Apply fixes, re-verify & sync integration branch:**
   - Fix all "Fix now" items and CI failures in the PR worktree (if a fix requires editing files outside `Allowed write files` / external subsystems, report `EXTERNAL_FIX_NEEDED` instead of expanding scope).
   - Re-run affected local gates (changed-files-only `ruff format --check` for `.py`).
   - Follow repo `squash`/`push` conventions as appropriate and push to the PR branch.
4. **Reply visibly on the PR:**
   - Use `pull_request_respond` to post one concise reply addressing every numbered point from the bot review (listing commit SHA for fixes, exact future `PR-XX` card for deferred items, and 1-sentence factual note for skipped items).
   - If a failed check was a transient CI flake unrelated to the diff, call `ci_rerun` once.
   - Once all required CI checks are green and bot review (`kira-the-beagle`) has approved with 0 unresolved P1/P2 threads:
     - Ensure PR assignee (`@me`) is set.
     - Check `mergeStateStatus` and Darkplane AutoMerge: if `mergeStateStatus == "BLOCKED"` (human `CODEOWNERS` review still needed), add label `ready-for-review` (plus `Core Approval` only if a core path was touched) and report `human_approval_needed=yes` with the exact pending reviewers so the Orchestrator adds the PR to `APPROVAL-QUEUE.md`. If `mergeStateStatus == "CLEAN"` (Darkplane satisfied mergeability without human approval), report `human_approval_needed=no`.
5. **Never call `watch_pull_request` yourself:** The Orchestrator owns the persistent watch.

## Required Final Line

`PR <full URL>, head <SHA>, checks and reviews <state> | fixed_p1_p2=<N> | skipped=<M> | ci_fixed=<yes|no|none> | human_approval_needed=<yes|no> | downstream_notes=<none or short summary>`
