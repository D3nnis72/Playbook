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
2. **Stacked branching inside a stack:** If PR B depends on PR A inside the same stack (`requires_base_merged: false`), PR B branches off PR A's head SHA as soon as PR A passes Phase 04 locally — **do not wait 25 minutes for Kira or human merge** before starting PR B. Only pause for a `main` merge when a PR explicitly sets `requires_base_merged: true`.
3. **Live Integration Branch (`integration_branch`, e.g. `feature/<project>-integration`):** As soon as any PR passes Phase 04 and opens its GitHub PR, merge its commit cleanly into `integration_branch` (in a dedicated merge step, never dirtying the root checkout). Result: all individual PRs stay small and reviewable for GitHub/Kira, AND `integration_branch` always holds the complete, up-to-date integrated build ready for local E2E testing at any moment.
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
  -> reviewing_and_opening          (Phase 04 single-pass cross-model: review + fix P1/P2 + repo squash/description/push + open PR)
  -> [verify_p1_fix]                (only if Phase 04 fixed a real P1 bug)
  -> pr_open                        (watch_pull_request active + merged into integration_branch + plan checklist updated)
  -> [bot_ci_fixing]                (Phase 05 async on watch wake-up, non-blocking)
  -> ready_to_merge -> merged
```

## Phase Playbooks

Pass the matching file path in every `delegate_task` prompt, plus `runtime.repo_skills_root` when the target repo ships its own PR skills (e.g., `askLio/.skillshare/skills/`):

- `references/01-plan.md` — look-ahead file-level plan (`full` tier only).
- `references/02-plan-review.md` — look-ahead plan audit (`full` tier only).
- `references/03-execute.md` — implement in isolated worktree, run changed-files lint/format + card tests, commit cleanly.
- `references/04-code-review-gate.md` — single-pass cross-model review (using repo `architectural-review` & `consolidating-branch-tests` when present), fix ALL P1 and P2 directly, re-run gates, run repo `squash` + `description` + `push` + `pull_request_create`.
- `references/05-pr-review-ci-fix.md` — async triage & fix of Kira/bot comments and CI failures without blocking other PRs.

## Continuous Plan Sync and Orchestrator Flexibility

- **Keep plans live:** After every PR reaches `pr_open` or `ready_to_merge`, update **both** `state.json` (with PR URL, head SHA, timings, and any non-blocking reviewer notes for later PRs) **and** the human-readable plan checklist listed in `state.json` (`plan_doc_to_sync`).
- **Autonomous plan adjustment:** You are authorized to re-order independent PRs, split an oversized PR, add a separate external-fix PR off `origin/main`, or adjust a later card based on real findings from an earlier PR (such as Kira's DB sampling notes). **Never weaken the `north_star_goal`** in `state.json`: full feature built cleanly, zero skipped requirements, zero silent hacks, zero unauthorized core/outside edits, and verified end-to-end.

## Escalation Rules

Mark only the affected PR `blocked` in `state.json` and keep running independent PRs when:
1. The same local gate, P1/P2 finding, or CI check fails twice in a row after fixes.
2. Live `origin/main` contradicts a frozen requirement or forces an unauthorized `@askLio/core` / critical-path edit.
3. A required secret, auth token, or local service (e.g., Docker) is missing.
4. All available providers are rate-limited.
