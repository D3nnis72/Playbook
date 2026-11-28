# Phase 03: Execute Child Playbook

You are a fresh-context **Implementation** child working in an isolated git worktree (`isolation: "worktree"`) of the target repository. Implement the PR cleanly, pass every local gate on the PR Card, and commit your work.

## Inputs to Read First

1. The PR Contract Card (`cards/PR-XX-*.md`) and its `R-xx` rows in `requirements.md`.
2. For `tier: "full"` PRs: the approved plan (`generated-plans/<PR-ID>-plan.md`). For `tier: "fast"` PRs: implement directly from the PR Card.
3. The live target files in your worktree plus the repository's scoped `AGENTS.md` files.

## Steps

1. Confirm you are in your isolated worktree on the right branch/base (`git status`, `git branch --show-current`). Never touch the main checkout outside your worktree.
2. Implement every `R-xx` requirement cleanly, strictly within `Allowed write files`.
   - Outside `/experimental/`, tag touched lines with the repo's required experimental marker; inside `/experimental/`, follow repo conventions without redundant markers.
   - If you discover a bug or missing hook in an **external/shared** subsystem outside `Allowed write files`, do **not** sneak it into this PR; stop and report `EXECUTE_RESULT: EXTERNAL_FIX_NEEDED | area=<...> | reason=<...>` so the orchestrator can spawn a separate clean PR off `origin/main`.
3. Run any required codegen (e.g., `npm run api:generate`) and **every** verification command on the PR Card.
   - If CI runs tests in parallel (pytest-xdist and similar), run the changed test files once in that mode locally too (e.g. `pytest -n 2 <files>`). Parametrize values must be identical in every worker: no generated ids, timestamps or random values in `parametrize`.
   - Run formatting checks (`ruff format --check`) on **changed `.py` files only** (`git diff --name-only <base>...HEAD -- '*.py'`) so pre-existing untouched repo drift never triggers false failures.
4. Inspect `git diff --stat` and confirm zero edits outside `Allowed write files` and zero stray untracked files.
5. Create one clean commit on your worktree branch. Do **not** push or open the PR here (Phase 04 Cross-Model Review-and-Fix Gate runs next on this worktree).

## Rules

- Do not spawn subagents. Never call `watch_pull_request`.

## Required Final Line

`EXECUTE_RESULT: DONE | worktree=<abs-path> | branch=<branch> | head=<sha> | gates=<passed-list>`
or
`EXECUTE_RESULT: EXTERNAL_FIX_NEEDED | area=<area> | reason=<one sentence>`
or
`EXECUTE_RESULT: BLOCKED | reason=<one sentence>`
