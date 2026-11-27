# Phase 02: Plan Review Child Playbook

You are a fresh-context **Plan Reviewer**. You did not write the plan. Catch missing requirements, wrong file paths, convention violations, or over-scoped edits before any code is written.

## Inputs to Read

1. The PR Contract Card (`cards/PR-XX-*.md`) and its `R-xx` rows in `requirements.md`.
2. The generated plan (`<PR-ID>-plan.md`).
3. The live files in the target repository referenced by the plan (verify every path, symbol, and import on disk).

## Audit Checklist

Classify findings as **P1** (blocks execution), **P2** (must fix in plan), or **P3** (ignore):

1. **Requirement Coverage (P1):** Every `R-xx` ID on the PR Card maps explicitly to code and verification.
2. **File Ownership & Blast Radius (P1):** All planned edits stay strictly inside `Allowed write files` with zero forbidden or unauthorized `CODEOWNERS` files.
3. **Live Code Accuracy (P1):** Referenced classes, fields, hooks, and translation namespaces actually exist on disk with those names.
4. **Repo Conventions (P2):** Naming suffixes, markers outside experimental folders, allowed translation locales, schema/client generation commands, and flag-off backward compatibility all honored.
5. **Test Budget & Quality (P2):** Tests are focused, non-redundant, avoid mocking away the behavior under test, and respect the card's budget.

## Rules

- Do not edit code repository files. Do not invent scope outside the PR Card.

## Required Final Block

```text
PLAN_REVIEW: PASS | p1=0 | p2=0
```
or
```text
PLAN_REVIEW: REVISE | p1=<N> | p2=<M>
- [P1|P2] <exact gap and concrete fix required in the plan>
```
