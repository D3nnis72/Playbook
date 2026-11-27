---
name: pr-stack-orchestrator
description: Use ONLY when the user explicitly asks to run an autonomous multi-PR orchestrator for a large multi-PR build or stack, or invokes pr-stack-orchestrator by name. Never use for single PRs, routine feature work, bug fixes, or ad-hoc subagent tasks.
---

# PR Stack Orchestrator

## Overview

Turn one T3 Code thread into a lean autonomous orchestrator for a large multi-PR build. The orchestrator never writes product code itself. It tracks progress in a project-owned `state.json`, runs fresh child threads in isolated worktrees inside the target code repository's T3 project, enforces a mandatory P1/P2 Code Review Gate before every push, and handles automated PR reviewers (such as Kira) and CI asynchronously via `watch_pull_request` while independent PRs keep moving in parallel.

## When to Use (Strict)

- **Use ONLY** when the user explicitly asks to orchestrate a large multi-PR build or invokes `pr-stack-orchestrator`.
- **Never use** for single-PR features, quick fixes, investigations, or normal `subagent-driven-development` work.

## Startup Checklist (Once Per Session)

1. Read the project's orchestration pack: `state.json`, `requirements.md`, and the PR Contract Cards (`cards/PR-*.md`).
2. Call `orchestrator_capabilities` **once** to inspect live providers (`claudeAgent`, `cursor`, `codex`) and available models.
3. **Target Machine & Project Selection:**
   - **Critical T3 Code rule:** Local `delegate_task` children and `isolation: "worktree"` always inherit the Orchestrator thread's own T3 project. Therefore, the Orchestrator thread itself **must live inside the target code repository's T3 project** (e.g., `askLio`, never a separate docs/customer repo). Omit `target.projectId` on local `delegate_task` calls; pass `target.environmentId` + `target.projectId` only when delegating to a different linked machine.
   - If the user asked to run on a specific linked machine (e.g., MacBook Air), check `t3_environment_links` and reachability first. If that machine is offline or unreachable, **fall back cleanly to the current machine** and note it in `state.json` (`runtime.active_environment_id`). Never block waiting for an offline machine.
4. Fetch `origin/main` cleanly in the target repo without modifying the main checkout. Never create git worktrees in shell.

## Model Routing and Coding-Limit Failover

Pick models from `orchestrator_capabilities` by phase:

| Phase | Preferred Model / Provider | Fallback when Claude hits limits |
| --- | --- | --- |
| **Orchestrator (this thread)** | Gemini 4 Neon (`cursor`) or Claude Opus | Gemini 4 Neon (`cursor`) |
| **01 Plan + 02 Plan Review** | Gemini 4 Neon (`cursor`) or Claude Opus | Gemini 4 Neon (`cursor`) |
| **03 Execute (heavy / core PRs)** | Claude Opus (`claudeAgent`) | Claude Opus/Sonnet on `cursor`, else Gemini 4 Neon |
| **03 Execute (small PRs & fixes)** | Claude Sonnet (`claudeAgent`) | Claude Sonnet or Gemini 4 Neon on `cursor` |
| **04A Code Review (Gate)** | **Cross-model:** different family from Execute (e.g., Gemini 4 Neon on `cursor` reviewing Claude code, or Opus reviewing Gemini) | Best available cross-family model on `cursor` |
| **04B Fix Pass + 05 PR/Bot Fix** | Claude Sonnet (`claudeAgent`) | Claude Sonnet or Gemini 4 Neon on `cursor` |

**Automatic Coding-Limit Rule:** Whenever any `claudeAgent` child fails with a usage cap, quota, or rate-limit error, set `runtime.claude_provider_limited = true` with timestamp in `state.json` and immediately re-dispatch on the `cursor` provider. Do not retry an exhausted provider or stop to ask the user while `cursor` is available.

## PR State Machine

```text
pending -> planning -> plan_reviewing -> executing -> code_reviewing
  -> [code_fixing if P1 > 0 or P2 > 0] -> pr_open (watch_pull_request)
  -> [bot_ci_fixing on async watch wake-up] -> ready_to_merge -> merged
```

## Phase Playbooks (Load Only What Each Child Needs)

Pass the matching reference file path in every `delegate_task` prompt:

- **Planning:** `references/01-plan.md` — map every `R-xx` requirement against live repo files into a concrete file-level plan.
- **Plan Review:** `references/02-plan-review.md` — audit plan against `R-xx`, file ownership, repo conventions, and test budget before any code is written.
- **Execute:** `references/03-execute.md` — implement in an isolated worktree (`isolation: "worktree"`), run every local gate on the PR Card, verify diff scope, commit cleanly (no push yet).
- **Code Review & Mandatory P1/P2 Fix Gate:** `references/04-code-review-gate.md` — cross-model review (04A) classifies findings into P1/P2/P3; if ANY P1 or P2 exists, spawn a Fix child (04B) and re-verify until **P1 = 0 and P2 = 0** (max 2 fix rounds).
- **Parallel Bot-Review (e.g., Kira) & CI Fix:** `references/05-pr-review-ci-fix.md` — triggered asynchronously on `watch_pull_request` wake-ups to triage bot comments honestly, fix valid P1/P2 findings and CI failures, push, and reply on PR threads.

## Parallelism and Non-Blocking PR Watch Loop

1. **Dispatch independent PRs in parallel:** Any PR whose `depends_on` are satisfied (`pr_open` when stacking, `merged` when `requires_base_merged: true`) can run immediately, up to `runtime.max_parallel_children` (default `3`) active worktrees at once.
2. **Never block on CI or bot reviews:** As soon as Phase 04 returns `CODE_REVIEW: PASS | p1=0 | p2=0`, push the branch, create the PR via `pull_request_create`, apply any configured review label (e.g., Kira), call `watch_pull_request`, update `state.json` to `pr_open`, and immediately advance to the next runnable PR. Never sleep or poll.
3. **Handle wake-ups asynchronously:** When T3 wakes this thread on a CI failure or bot review, spawn a fresh Phase 05 child for that PR while keeping other PRs running. Mark `ready_to_merge` once all required CI checks are green and zero valid P1/P2 review comments remain.
4. **Fresh context per check:** Every review or re-check is a new `delegate_task`, never `t3_thread_send` into an old review thread. Persist `state.json` after every state transition.

## Escalation Rules (When to Pause a PR and Ping the User)

Mark only the affected PR `blocked` in `state.json` and continue independent PRs when:
1. The same local gate, P1/P2 finding, or CI check fails twice in a row after fixes.
2. Live `origin/main` contradicts a frozen requirement or requires editing a forbidden / `CODEOWNERS` core file.
3. A required secret, auth token, or local service (e.g., Docker) is missing.
4. All configured providers (`claudeAgent` and `cursor`) are rate-limited or unavailable.

## Canary Mode First

Before running a full 10+ PR stack, set `"mode": "canary"` in `state.json` with 1 to 2 small, independent PRs. Verify end-to-end timings, gate behavior, model failover, and bot-review turnaround before expanding the remaining PR cards.
