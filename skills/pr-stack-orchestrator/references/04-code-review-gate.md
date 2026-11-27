# Phase 04: Code Review & Mandatory P1/P2 Fix Gate Playbook

Every PR runs through two fresh-context roles before pushing or opening a PR:
- **04A · Code Review Child** (read-only audit, cross-model from the Execute child).
- **04B · Mandatory Fix Child** (runs automatically whenever **any P1 or P2 finding** exists).

No PR may be pushed until a fresh 04A check reports **P1 = 0, P2 = 0**, and all verification commands pass.

---

## Role 04A: Code Review Child (Read-Only)

You did not write this code. Audit the actual `git diff` against the PR Contract Card, `requirements.md`, and repository conventions.

### Checklist

1. **Diff & Scope Audit:** Run `git diff <base>..HEAD --stat` and `git diff <base>..HEAD`. Confirm zero edits outside `Allowed write files`, zero forbidden/`CODEOWNERS` violations, and exact required markers.
2. **Requirement Trace Audit:** Verify every `R-xx` ID on the PR Card is genuinely implemented and verified (not stubbed or half-wired).
3. **Engineering & Bug Audit:** Check edge cases (`None`/empty inputs, legacy persisted records, tenant isolation, flag-off backward compatibility), strict typing/Pydantic/TS contracts, generated API artifacts, UI/design-system/translation rules, and security/permission/MCP rules.
4. **Test Quality Audit:** If tests were added, run the repo's test quality audit script (when present) and verify tests assert real behavior within the card's test budget.
5. **Independent Gate Check:** Re-run fast lint/type/test checks if anything looks unformatted or stale.

### Severity Rules

- **P1 (Blocker — MUST fix):** Bug, wrong behavior, missing `R-xx` requirement, broken backward compatibility, security/tenant leak, failing CI gate, or out-of-scope/forbidden file edit.
- **P2 (Important — MUST fix before PR):** Convention violation (naming, markers, wrong locale/glossary, design-system violation), missing edge-case test for a real failure mode, over-mocked/redundant test, stale generated client, or brittle coupling.
- **P3 (Nit — DO NOT fix / DO NOT block):** Pure style preferences or speculative ideas outside the PR Card. Log at most 3 P3 notes; never fail the gate for P3s.

### Required Final Block (Role 04A)

```text
CODE_REVIEW: PASS | p1=0 | p2=0 | p3=<K>
```
or
```text
CODE_REVIEW: FIX_REQUIRED | p1=<N> | p2=<M> | p3=<K>
- [P1] <file:line> — <exact defect> | Fix: <concrete fix>
- [P2] <file:line> — <exact defect> | Fix: <concrete fix>
```

---

## Role 04B: Mandatory P1/P2 Fix Child

Spawned automatically by the Orchestrator on the PR's worktree branch whenever Role 04A reports `p1 > 0` or `p2 > 0`.

1. Fix **every P1 and P2 finding** cleanly. Ignore P3 nits unless trivial on an already-touched line.
2. Re-run **all** verification commands on the PR Card (and codegen if schemas changed).
3. Confirm `git diff --stat` remains strictly inside `Allowed write files`.
4. Commit cleanly (squash to one commit before push if repo conventions require single-commit PRs).

### Required Final Line (Role 04B)

`FIX_RESULT: DONE | branch=<branch> | head=<sha> | fixed_p1=<N> | fixed_p2=<M> | gates=<passed-list>`

### Orchestrator Gate Policy

- After 04B finishes, run a **fresh** 04A verification pass.
- Max **2** fix rounds per PR; if the same P1/P2 persists, mark the PR `blocked` in `state.json` and notify the user.
- On `CODE_REVIEW: PASS | p1=0 | p2=0`, push the branch, open the PR via `pull_request_create`, apply the bot-review label if needed, call `watch_pull_request`, set `state.json` to `pr_open`, and immediately proceed to the next runnable PR.
