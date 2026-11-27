# Phase 04: Single-Pass Cross-Model Review, P1/P2 Fix, and PR Open Playbook

You are a fresh-context **Cross-Model Code Reviewer & Gatekeeper** (running on a different model family from the Execute child) operating directly on the PR's isolated worktree. In **one cohesive pass**, you audit the diff, fix every P1 and P2 finding yourself, re-verify all gates, apply the repository's own PR flow skills, push, and open the PR.

## Inputs to Read First

1. The PR Contract Card (`cards/PR-XX-*.md`) and its `R-xx` rows in `requirements.md`.
2. If `repo_skills_root` is provided (e.g., `askLio/.skillshare/skills/`), read and follow the applicable repo PR skills:
   - `architectural-review/SKILL.md` (staff-engineer review bar against surrounding callers)
   - `consolidating-branch-tests/SKILL.md` (when >15 new tests were added)
   - `squash/SKILL.md` (single clean commit with `--shortstat` safety check)
   - `description/SKILL.md` (terse, feature-focused PR description format)
   - `push/SKILL.md` (clean push conventions)

## Step 1: Audit `git diff <base>..HEAD`

Check every item and classify findings strictly as **P1**, **P2**, or **P3**:

1. **Diff & Scope:** Zero edits outside `Allowed write files`, zero unauthorized `CODEOWNERS` / core edits, proper markers outside `/experimental/`.
2. **100 % `R-xx` Trace:** Every `R-xx` ID on the card is genuinely implemented and tested.
3. **Architecture & Bugs (repo `architectural-review` bar):** Read surrounding callers (never review in isolation). Check edge cases (`None`/empty, legacy persisted Mongo docs, tenant isolation, flag-off behavior), strict Pydantic/TS types, OpenAPI client sync (`api:check`), Shell V2 / `en`+`de` translation rules, security/MCP rules.
4. **Test Quality:** Run `scripts/audit_test_quality.py` (when present on backend tests) and check test budget.

- **P1 (Blocker — MUST fix):** Bug, wrong behavior, missing `R-xx`, broken backward compatibility, security/tenant leak, failing CI check, out-of-scope file edit.
- **P2 (Important — MUST fix):** Convention violation, missing real edge-case test, over-mocked/redundant test, stale generated client, brittle coupling.
- **P3 (Nit — DO NOT fix):** Style preferences or speculative ideas outside the card. Log at most 3 P3 notes.

## Step 2: Fix All P1 and P2 Findings Directly

- If `p1 > 0` or `p2 > 0`, fix **every P1 and P2** cleanly right here in the worktree (ignore P3s).
- Re-run all verification commands from the PR Card (using changed-files-only `ruff format --check` on `.py` files). Confirm every gate is green.

## Step 3: Squash, Push, and Open PR (Using Repo PR Skills)

Once **0 P1 and 0 P2 remain** and all gates pass:

1. Follow the repo's `squash` skill so the branch has **one clean commit** on top of `<base>` (verify `--shortstat` matches before and after).
2. Push the branch (`git push -u origin HEAD`, or `--force-with-lease` if squashed over an already-pushed branch).
3. Write the PR body following the repo's `description` skill (terse 1–6 feature bullets, plus any required migration/MCP/codegen notes).
4. Open the PR via `pull_request_create` against the PR's target base (`main` or parent stacked branch).
5. **Assignee & Labels (mandatory):** Immediately set the PR assignee (`@me` or `runtime.pr_defaults.assignee`) and add the repo's bot-review label (e.g., `kira pls review` in `askLio`) so reviewers and bots see the PR right away. Do **not** add `ready-for-review` until CI is green and the bot review passes (Phase 05 adds `ready-for-review` when human approval is still needed).
6. **Do NOT call `watch_pull_request` yourself** — the Orchestrator owns watching.

## Orchestrator P1 Double-Check Rule

- If `fixed_p1 == 0`: the PR is immediately `pr_open` (no extra child spawn needed!).
- If `fixed_p1 > 0`: the Orchestrator may run one fast read-only verification check on the P1 fix commit if the bug was subtle; otherwise it proceeds straight to `pr_open` and lets CI + Kira verify in parallel.

## Required Final Line

`PHASE04_RESULT: OPENED | pr=<full URL> | branch=<branch> | head=<sha> | fixed_p1=<N> | fixed_p2=<M> | p3=<K>`
or
`PHASE04_RESULT: BLOCKED | reason=<one sentence>`
