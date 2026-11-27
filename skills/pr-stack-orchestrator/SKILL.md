---
name: pr-stack-orchestrator
description: Use ONLY when the user explicitly asks to run an autonomous multi-PR orchestrator for a large multi-PR build or stack, or invokes pr-stack-orchestrator by name. Never use for single PRs, routine feature work, bug fixes, or ad-hoc subagent tasks.
---

# PR Stack Orchestrator

## Overview

Turn one T3 Code thread into a fast, autonomous orchestrator for a large multi-PR build. The orchestrator never writes product code itself. It maintains `state.json` (plus syncs the human-readable plan checklist after each PR), runs parallel isolated worktrees inside the target code repository's T3 project, integrates every approved PR into a live integration branch for local end-to-end testing, enforces a cross-model P1/P2 Review-and-Fix Gate before pushing, invokes the repository's own PR skills (e.g., `architectural-review`, `squash`, `description`, `push`), and handles automated PR reviewers (such as Kira) and CI asynchronously via `watch_pull_request`.

## When to Use (Strict)

- **Use ONLY** when the user explicitly asks to orchestrate a large multi-PR build or invokes `pr-stack-orchestrator`.
- **Never use** for single-PR features, quick fixes, investigations, or normal `subagent-driven-development` work.

## Startup Checklist (Once Per Session)

1. Read the project's orchestration pack: `state.json`, `requirements.md`, `REVIEWER-MAP.md` (if present), and runnable PR Cards (`cards/PR-*.md`).
2. Call `orchestrator_capabilities` **once** to inspect live providers (`claudeAgent`, `cursor`, `codex`) and available models.
3. **Target Machine & Project Selection:**
   - **Critical T3 Code rule:** Local `delegate_task` children and `isolation: "worktree"` always inherit the Orchestrator thread's own T3 project. Start the Orchestrator thread inside the target code repository's T3 project (e.g., `askLio`, never a separate docs repo). Omit `target.projectId` on local `delegate_task` calls; pass `target.environmentId` + `target.projectId` only when delegating to a different linked machine.
   - If the user asked to run on a linked machine (e.g., MacBook Air), check `t3_environment_links` / reachability first; if offline, **fall back cleanly to the current machine** and record `runtime.active_environment_id` in `state.json`.
4. Fetch `origin/main` cleanly in the target repo without modifying its root checkout. Never create git worktrees in shell.

## Parallel Worktrees, Stacked PRs, and the Live Integration Branch

Each PR is its own isolated worktree (`isolation: "worktree"`), its own git branch, and its own GitHub PR. Here is how parallel worktrees stay conflict-free and testable together:

1. **Disjoint parallel worktrees:** Any set of PRs whose `depends_on` are satisfied and whose `Allowed write files` are disjoint run simultaneously in separate worktrees (up to `runtime.max_parallel_children`, default **5**, split across `claudeAgent` and `cursor`).
2. **Stacked branching without waiting for merges:** If PR B depends on PR A (`requires_base_merged: false`), PR B branches off PR A (or the `integration_branch` checkpoint) as soon as PR A passes Phase 04 locally — **never wait for human GitHub approvals or 25-minute Kira reviews before building the next wave**.
   - **Mandatory Stacked-PR Guardrail (applies to EVERY PR whose base is not `main`):** GitHub does not enforce `main` branch protection or `CODEOWNERS` on feature branches. Therefore, whenever a PR targets a feature branch instead of `main`, Phase 04 MUST add the **`Do Not Merge`** label and put a bold warning at line 1 of the PR description (`> **Stacked PR (base: <base-branch>) — Do not merge into the parent feature branch.** Merge bottom-up into main; remove Do Not Merge once retargeted to main.`). Only remove `Do Not Merge` once the parent merges into `main` and GitHub retargets the PR onto `main`.
3. **Frozen Wave-Base Anchors for Parallel Waves (Zero Moving-Base Noise):**
   - Never open multiple parallel PRs targeting a moving `integration_branch` (merging PR 1 into `integration_branch` immediately pollutes the diff of PRs 2–7 on GitHub).
   - Instead, before launching a parallel wave whose parent stack is not merged to `main` yet, freeze a static checkpoint branch at the current `integration_branch` commit (e.g., `feat/<project>-stack1-base`). Every PR in that parallel wave branches off and targets that frozen base branch (with `Do Not Merge` + `Base: <anchor>`), while the orchestrator still merges every finished PR locally into `integration_branch` for live E2E testing.
   - **Merging to `main` later (clean, zero dead branches):** Never merge a `*-base` anchor into `main`. Once the parent stack lands on `main`, rebase each wave PR onto `origin/main` (`git rebase --onto origin/main <anchor-branch> <pr-branch>` + `git push --force-with-lease`), retarget the PR to `main`, drop `Do Not Merge`, and delete the temporary `*-base` anchor branch.
4. **Follow repo PR labels, assignees, and approval queue (`runtime.pr_defaults`):**
   - **Ball-in-court Assignee rule:** On PR open (Phase 04, Draft / waiting on CI + bot review), assign the PR author (`@me` / `pr_defaults.author_assignee`) and add the configured bot-review label (e.g., `kira pls review`). When transitioning to `ready_to_merge` and human approval is required, **swap Assignee off `@me` onto the designated human reviewer** (and add them to Reviewers if not already requested), so the PR actually lands in their GitHub queue instead of staying assigned to the author. When a reviewer requests changes and the ball returns to the author, swap Assignee back to `@me` while fixing.
   - Once CI is green and bot review approves (Phase 05 -> `ready_to_merge`): inspect `mergeStateStatus` and automated approval checks (e.g., Darkplane AutoMerge).
     - If automated approval satisfies mergeability (`mergeStateStatus == "CLEAN"`), mark `ready_to_merge (auto-approvable)` without pinging human reviewers.
     - If human `CODEOWNERS` approval is still required (`mergeStateStatus == "BLOCKED"` with pending `reviewRequests`), swap Assignee to the configured reviewer for that PR's scope (from `state.json` `pr_defaults.reviewer_by_scope` / `REVIEWER-MAP.md`), add `ready-for-review` (and `Core Approval` only if a critical core path was touched), and immediately update the project's `APPROVAL-QUEUE.md` with the PR link, 1-line summary, CI/bot/Darkplane status, and who is assigned to approve.
4. **Live Integration Branch (`integration_branch`, e.g. `feature/<project>-integration`):** As soon as any PR passes Phase 04 and opens its GitHub PR, merge its commit cleanly into `integration_branch` (in a dedicated merge step, never dirtying the root checkout). Result: all individual PRs stay small and reviewable for GitHub/Kira, AND `integration_branch` always holds the complete, up-to-date integrated build ready for local E2E testing at any moment.
4. **Separate PR Rule for Outside/External Changes:** Never sneak edits to shared/external subsystems (e.g., Ariba, Sourcing Agent, core utilities, or bugs discovered in untouched modules) into a feature PR. Instead, spawn a **separate minimal PR directly off `origin/main`** (`fix/<area>-<short-name>`) with a clear explanation of why it was needed, record it in `state.json`, and keep feature PRs strictly inside their `Allowed write files`.

## Speed Tiers and Look-Ahead Pipelining

- **`tier: "fast"`** (small, card-complete PRs whose card already specifies exact files, contracts, and tests): **skip Phase 01 and Phase 02** and dispatch directly to Phase 03 Execute.
- **`tier: "full"`** (complex stores, algorithms, multi-component UI, handoffs): run Phase 01 Plan + Phase 02 Plan Review **one wave ahead** (read-only) while the current wave is executing, so approved plans are ready before a coding slot opens.

## Model Routing and Coding-Limit Failover

Pick models dynamically from `orchestrator_capabilities`:

| Phase | Preferred Model / Provider | Fallback when Claude hits limits |
| --- | --- | --- |
| **Orchestrator (this thread)** | Gemini 4 Neon (`cursor`) or Claude Opus | Gemini 4 Neon (`cursor`) |
| **01 Plan + 02 Plan Review (`full` tier, look-ahead)** | Gemini 4 Neon (`cursor`) | Gemini 4 Neon (`cursor`) |
| **03 Execute (heavy / core `full` PRs)** | Claude Opus (`claudeAgent`) | Claude Opus/Sonnet on `cursor`, else Gemini 4 Neon |
| **03 Execute (`fast` PRs & targeted fixes)** | Claude Sonnet (`claudeAgent`) | Claude Sonnet or Gemini 4 Neon on `cursor` |
| **04 Review + P1/P2 Fix + Squash + Open PR** | **Cross-model:** different family from Execute (e.g., Gemini 4 Neon on `cursor` reviewing Claude, or Opus reviewing Gemini) | Best cross-family model on `cursor` |
| **05 Async Bot/Kira & CI Fix** | Claude Sonnet (`claudeAgent`) | Claude Sonnet or Gemini 4 Neon on `cursor` |

**Automatic Coding-Limit Rule:** On any `claudeAgent` usage-cap or rate-limit error, set `runtime.claude_provider_limited = true` with timestamp in `state.json` and immediately re-dispatch on `cursor`. Never stall waiting for manual intervention while `cursor` is available.

## PR State Machine

```text
pending
  -> [planning -> plan_reviewing]   (full tier only, pipelined 1 wave ahead)
  -> executing                      (Phase 03 in isolated worktree)
  -> reviewing_and_opening          (Phase 04 single-pass cross-model: review + fix P1/P2 + repo squash/description/push + open PR + assign @me + add `kira pls review`)
  -> [verify_p1_fix]                (only if Phase 04 fixed a real P1 bug)
  -> pr_open                        (watch_pull_request active + merged into integration_branch + plan checklist updated)
  -> [bot_ci_fixing]                (Phase 05 async on watch wake-up if CI failed or bot has P1/P2 comments)
  -> ready_to_merge                 (Orchestrator ALWAYS runs the PR-Green Transition Checklist below!)
  -> merged
```

### Mandatory Orchestrator PR-Green Transition Checklist (Runs on EVERY PR)

Whenever `watch_pull_request` wakes the Orchestrator with new comments, review events, or CI updates — and ALWAYS before marking any PR `ready_to_merge` or advancing a dependent wave:

1. **Triage ALL reviewer comments & threads (humans + bots — never only Kira):** Inspect `pull_request_read(include=["comments", "threads"])` across **all authors** (human teammates, code owners, AI reviewers like Kira, and inline threads). Never silently ignore a human comment, and never blindly accept every suggestion either — apply real engineering judgment via Phase 05 (`05-pr-review-ci-fix.md`):
   - **Actionable & clearly right** (real bug, missing flag/guard, naming/collection choice that would force a migration later, or P1/P2 convention fix) → spawn Phase 05 to fix cleanly, push, re-merge into `integration_branch`, and post one concise reply confirming what changed.
   - **Valid but belongs in a later PR** → record the requirement on the owning downstream PR card (`cards/PR-XX-*.md`) + `state.json` and reply briefly stating where it lands.
   - **Disagree / breaks a constraint or widens blast radius** (e.g., would break an existing assertion, expand into `@askLio/core`, or edit another owner's untouched files) → verify against live code and **push back respectfully with concrete evidence** (`file:line` / tradeoff); if a human reviewer asks for a structural or cross-PR scope change with real tradeoffs, **escalate to the user** before executing or arguing.
   - **Informational / no response needed** (empty `APPROVED`, Darkplane scorecard, PR-assigner notice, `"On it"`) → do **not** reply; keep PR threads noise-free.
2. Inspect live PR metadata (`gh pr view <n> --json assignees,labels,mergeStateStatus,reviewRequests,reviews`).
3. **Hand off Assignee to the reviewer when ready:** While fixing CI/reviews, keep `assignee` on the author (`@me`). Once CI is green, bot review passed, and human approval is required, **remove `@me` from Assignees and assign + request the designated human reviewer** (e.g., domain owner from `state.json` `pr_defaults.reviewer_by_scope` / `REVIEWER-MAP.md`, or leave for repo auto-assigner like Kira `pr-assigner` on `Core Approval` PRs — never leave a `ready-for-review` PR assigned solely to the author).
4. Check `mergeStateStatus`, target base, draft state, and automated approvals (e.g., Darkplane AutoMerge):
   - If `runtime.open_as_draft_until_green` is `true` and the PR is still a Draft, mark it Ready (`pull_request_update(..., ready=True)`) once CI is green and Kira has reviewed.
   - If base != `main`: ensure **`Do Not Merge`** is set until retargeted to `main`.
   - If base == `main` and `mergeStateStatus == "CLEAN"` (auto-approvable / no human gate blocking): set `human_approval_needed: false` in `state.json` and add the PR under **Auto-Merge Ready** in `approval_queue_doc` (`APPROVAL-QUEUE.md`) without pinging reviewers.
   - Otherwise (`mergeStateStatus == "BLOCKED"` or stacked awaiting bottom-up merge): add `runtime.pr_defaults.ready_labels_when_human_review_needed` (`ready-for-review`, plus `Core Approval` only if a core path was touched), set `human_approval_needed: true`, and update `APPROVAL-QUEUE.md` (bottom-up **Merge Order**, table row, and copy-pasteable Slack/Teams ping message).
   - Never commit playbook files, orchestration JSON/cards, or `.env` into the target code repo; never mention internal wave names or card IDs in GitHub PR text.
5. Update `state.json` (`status: "ready_to_merge"`) AND sync the human checklist in `plan_doc_to_sync` (e.g., `06_prs_und_review.md`).

## Phase Playbooks

Pass the matching file path in every `delegate_task` prompt, plus `runtime.repo_skills_root` when the target repo ships its own PR skills (e.g., `askLio/.skillshare/skills/`):

- `references/01-plan.md` — look-ahead file-level plan (`full` tier only).
- `references/02-plan-review.md` — look-ahead plan audit (`full` tier only).
- `references/03-execute.md` — implement in isolated worktree, run changed-files lint/format + card tests, commit cleanly.
- `references/04-code-review-gate.md` — single-pass cross-model review (using repo `architectural-review` & `consolidating-branch-tests` when present), fix ALL P1 and P2 directly, re-run gates, run repo `squash` + `description` + `push` + `pull_request_create`.
- `references/05-pr-review-ci-fix.md` — async triage & fix of ALL reviewer comments (human engineers + bots like Kira) and CI failures with genuine engineering judgment (fix, defer, challenge/escalate, or skip noise) without blocking other PRs.

## Continuous Plan Sync and Orchestrator Flexibility

- **Keep plans live:** After every PR reaches `pr_open` or `ready_to_merge`, update **both** `state.json` (with PR URL, head SHA, timings, and any non-blocking reviewer notes for later PRs) **and** the human-readable plan checklist listed in `state.json` (`plan_doc_to_sync`).
- **Autonomous plan adjustment:** You are authorized to re-order independent PRs, split an oversized PR, add a separate external-fix PR off `origin/main`, or adjust a later card based on real findings from an earlier PR (such as Kira's DB sampling notes). **Never weaken the `north_star_goal`** in `state.json`: full feature built cleanly, zero skipped requirements, zero silent hacks, zero unauthorized core/outside edits, and verified end-to-end.

## Escalation Rules

Mark only the affected PR `blocked` in `state.json` and keep running independent PRs when:
1. The same local gate, P1/P2 finding, or CI check fails twice in a row after fixes.
2. Live `origin/main` contradicts a frozen requirement or forces an unauthorized `@askLio/core` / critical-path edit.
3. A required secret, auth token, or local service (e.g., Docker) is missing.
4. All available providers are rate-limited.
5. A human reviewer requests a structural, naming, or cross-PR scope change with non-obvious tradeoffs (or disagrees with an architectural guardrail) — present the comment, concrete evidence, and options to the user instead of blindly accepting or silently ignoring it.
