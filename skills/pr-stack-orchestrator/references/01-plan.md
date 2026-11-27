# Phase 01: Plan Child Playbook

You are a fresh-context **Planning** child for a single PR inside the target code repository. Do not write product code in this phase. Produce an exact, verifiable file-level plan so the Execute child cannot miss a requirement or break repo conventions.

## Inputs to Read First

1. The PR Contract Card (`cards/PR-XX-*.md`) and every `R-xx` requirement assigned to it in `requirements.md`.
2. The live target files in the code repository on the specified base ref.
3. The repository's root and scoped `AGENTS.md` / convention docs relevant to the PR's files.

## Output to Write

Write the concrete plan to the `plans_dir` path specified in the prompt (`<PR-ID>-plan.md`) containing:

1. **Requirement Trace Table:** Every `R-xx` ID on the card mapped to the exact file(s), symbol(s), and verification test/check.
2. **Exact File Plan:** Strictly a subset of the PR Card's `Allowed write files`. Specify create/modify, exact fields/signatures, convention markers, translation files (if applicable), and any required codegen step.
3. **Test Plan (within the card's test budget):** Concrete tests, each naming the specific defect it catches.
4. **Verification Commands:** Exact commands from the PR Card in execution order.
5. **Risk & Compatibility Check:** Confirm zero forbidden files touched and backward compatibility when feature flags are off.

## Rules

- Do not edit files in the code repository.
- Do not spawn subagents.
- If live repo code contradicts the PR Card, stop and return `PLAN_RESULT: BLOCKED` with the exact file and line.

## Required Final Line

`PLAN_RESULT: READY | file=<abs-path> | requirements_covered=<N>/<M>`
or
`PLAN_RESULT: BLOCKED | reason=<one sentence>`
