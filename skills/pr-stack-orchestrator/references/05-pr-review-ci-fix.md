# Phase 05: Parallel All-Reviewer (Human + Bot) & CI Triage Child Playbook

You are a fresh-context child spawned asynchronously by the Orchestrator whenever `watch_pull_request` wakes it up with new review comments (from human teammates, code owners, or automated reviewers like Kira/Codex/Bugbot) or failing CI checks on an open PR. Other PRs continue running in parallel.

## Steps

1. **Inspect PR & CI (ALL authors, never only bots):**
   - Call `pull_request_read(include=["comments", "threads", "checks"])` on `pr_url` to read **every** issue comment, review body, inline review thread, and check status across **all authors** (human engineers, code owners, and automated bots).
   - Call `ci_logs` on any failed check run to inspect the exact failure.
2. **Triage every comment with real engineering judgment (no blind obedience, no silent skips):**
   - Read BOTH inline review threads AND top-level review/issue comments (including human reviewer notes and Kira's numbered follow-ups even when she says `"I'd merge this"`).
   - Verify every single claim against live code, existing tests, and the PR Contract Card, then classify into one of four dispositions:
     - **Fix now (in this PR):** Real bug, CI failure, P1/P2 convention/security defect that is cheapest to fix here (e.g., wrong Shell V2 table, fail-closed router default, missing parent flag), OR a clean human-reviewer request that prevents painful migrations later (e.g., collection/path naming before data exists).
     - **Defer to a planned downstream PR (valid, belongs later):** Write the exact requirement/note onto the owning downstream PR card (`cards/PR-XX-*.md`) and `state.json`, and cite that exact PR ID in your reply on GitHub so both human reviewers and bots see where it is handled.
     - **Challenge / Push back (or Escalate to Orchestrator -> User):** If a suggestion (from a bot OR a human) is based on a misunderstanding, breaks an existing test/invariant, violates a hard isolation boundary (e.g., editing another owner's untouched files or `@askLio/core`), or adds speculative complexity:
       - For clear factual/technical points (e.g., bot false positive, P3 nit, or concrete test constraint like an existing route-count assertion): push back respectfully in 1–2 factual sentences citing exact `file:line` / test evidence.
       - For human-reviewer requests that change architecture, cross-PR scope, or have real tradeoffs: **do not** blindly implement or argue unilaterally — return `HUMAN_DECISION_NEEDED` with the reviewer's comment, verified code evidence, and concrete recommendation so the Orchestrator escalates cleanly to the user.
     - **No reply needed (informational noise):** Empty `APPROVED` reviews, Darkplane auto-scorecards, PR-assigner comments, `"On it"` status updates, or plain acknowledgments (`"LGTM"`, `"Thanks"`) require **zero** reply — never spam PR threads.
3. **Apply fixes, re-verify & sync:**
   - Fix all "Fix now" items and CI failures in the PR worktree (if a fix requires editing files outside `Allowed write files` / external subsystems, report `EXTERNAL_FIX_NEEDED` instead of expanding scope).
   - Re-run affected local gates (changed-files-only `ruff format --check` for `.py`).
   - Follow repo `squash`/`push` conventions as appropriate and push to the PR branch.
4. **Reply concisely on the PR (only where a response adds value):**
   - Start PR comments directly with the content (no filler greetings like "Hey Name,").
   - Use `pull_request_respond` to post one concise reply addressing every substantive human or bot point (listing commit SHA for fixes, exact future `PR-XX` card for deferred items, and brief factual evidence for challenged/skipped points).
   - Skip posting any reply if all new activity was purely informational noise.
   - If a failed check was a transient CI flake unrelated to the diff, call `ci_rerun` once.
   - Once all required CI checks are green, all human comments are resolved/answered, and bot review (`kira-the-beagle`) has approved with 0 unresolved P1/P2 threads:
     - Check `mergeStateStatus` and Darkplane AutoMerge: if `mergeStateStatus == "BLOCKED"` or the PR is stacked awaiting bottom-up merge:
       - If the PR needs `@askLio/approvers` or `@askLio/core` approval (shared wiring, flags, Celery task, or core path): **remove `@me` from Assignees and add `Core Approval`** (`pr_defaults.approvers_trigger_label`) even while stacked (`Do Not Merge` stays on) so `pr-assigner` assigns an approver for early review.
       - If the PR is 100% covered by a domain owner (`pr_defaults.domain_owner_assignee_for_isolated_packages`, e.g. `the-hugo`): **do NOT add `Core Approval`** — remove `@me` and **assign + request the domain owner directly**.
       - Add label `ready-for-review` and report `human_approval_needed=yes` with the assigned reviewer/routing so the Orchestrator keeps `APPROVAL-QUEUE.md` current.
     - If `mergeStateStatus == "CLEAN"` on `main` (Darkplane satisfied mergeability without human approval), report `human_approval_needed=no`.
5. **Never call `watch_pull_request` yourself:** The Orchestrator owns the persistent watch.

## Required Final Line

`PR <full URL>, head <SHA>, checks and reviews <state> | fixed_p1_p2=<N> | challenged_or_skipped=<M> | ci_fixed=<yes|no|none> | human_comments=<none|resolved|escalated> | human_approval_needed=<yes|no> | downstream_notes=<none or short summary>`
