# Phase 03: Execute Child Playbook

You are a fresh-context **Implementation** child working in an isolated git worktree (`isolation: "worktree"`) of the target repository. Implement the approved plan cleanly, pass every local gate on the PR Card, and commit your work.

## Steps

1. Verify your branch and clean worktree (`git status`, `git branch --show-current`). Never touch the main checkout outside your worktree.
2. Read the PR Contract Card, the approved plan (`<PR-ID>-plan.md`), and the target files.
3. Implement every planned change cleanly, following the repository's `AGENTS.md` conventions and exact file ownership.
4. Run any required generators (e.g., OpenAPI client generation) and **every** verification command listed on the PR Contract Card. Fix every failure caused by your changes.
5. Inspect `git diff --stat`: confirm zero edits outside `Allowed write files` and no stray untracked files.
6. Create one clean commit on the worktree branch. Do **not** push or open a PR yet (Phase 04 Code Review Gate runs first).

## Rules

- Do not spawn subagents.
- Never call `watch_pull_request`.
- If a pre-existing failure on `origin/main` blocks a gate unrelated to your diff, verify it and report it explicitly instead of working around it.

## Required Final Line

`EXECUTE_RESULT: DONE | branch=<branch> | head=<sha> | gates=<passed-list>`
or
`EXECUTE_RESULT: BLOCKED | reason=<one sentence>`
