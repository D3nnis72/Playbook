---
name: writing-plans
description: Use when a change needs a written implementation plan before touching code - sizes the plan Direct, Lite, or Full so small work stays small
---

# Writing Plans

## Overview

Write implementation plans for an engineer who has zero context for this codebase: which files to touch, what each task must produce, and how to prove it works. Assume they are skilled but know almost nothing about our toolset or problem domain, and do not know our test conventions well.

**Plans carry decisions, not volume.** Size the plan before writing it. Most changes need far less than the full template, and ceremony spent on a small change is not recoverable. DRY. YAGNI. TDD. Frequent commits.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan — [tier] tier, because [reason]."

**Upstream:** The spec, when there is one, has passed write-spec's review pass and user approval. Plan review verifies traceability, buildability, parsimony, and execution topology — it does not re-audit whether the design is doable, which write-spec settled.

**Downstream of the spec:** the spec is a human-readable design note — it names components and areas, not files. This plan owns all file-level detail. The spec's Verification outcomes become real checks (prefer existing suites); do not invent a unit test per Approach unit unless an outcome requires it. Every unit named in Approach gets a file and a task here under the name the spec gave it. If a named unit has no home in the plan, either the plan is incomplete or the spec's design changed — resolve it before execution rather than silently renaming.

**Context:** If working in an isolated worktree, it should have been created via the `playbook:using-git-worktrees` skill at execution time.

**Save plans to:** `docs/playbook/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## Checklist

You MUST create a task for each item and complete them in order:

1. **Size the plan** — Direct / Lite / Full; **Direct exits this skill**
2. **Map the files** — what gets created or modified, and what each one owns
3. **Decompose** — tasks, then work units (Full only)
4. **Write the plan** — at the tier's shape, saved to `docs/playbook/plans/`
5. **Check the plan** — self-check (Lite) or one reviewer pass (Full)
6. **Hand off to execution** — at the tier's execution path

## Step 1: Size the plan

Decide the tier **before writing anything** and state it in the plan header.

| Tier | The work looks like | You write |
|------|---------------------|-----------|
| **Direct** | Scope pinned by the request: one or two files, obvious done state, no open design questions — a typo, a rename, a config tweak, a bug with a known cause | **No plan.** Implement it. |
| **Lite** | One cohesive deliverable that stands or falls together — many files, runtimes, or check commands are fine; no independent packages to review separately, no parallel waves to schedule | **Lite plan** — about a page: goal, file map, ordered tasks, one closing task |
| **Full** | Several independently reviewable packages, genuine parallel waves, or sequencing where an early mistake in this plan gets built on before the next gate | **Full plan** — header, Global Constraints, Execution Schedule, detailed tasks, documentation work unit |

**Announce the tier and why** in one sentence. If the user names a different tier, take theirs. If the spec header names a `Plan tier`, start from that — revise only with a stated reason, never because "it touches a lot of files."

**Coming from a spec:**

| Spec size | Usual plan tier |
|-----------|-----------------|
| S, or no spec at all | Direct — Lite when the user wants a written artifact |
| M | **Lite** by default |
| L | Full |

**Do not pad up a tier.** A Lite plan that grows an Execution Schedule, a documentation work unit, and a reviewer dispatch is a Full plan in costume, and the ceremony now costs more than the change it describes. Adding tasks, abstraction, or scope to justify a higher tier is a plan failure.

**Several check commands ≠ Full.** Web tests + generation tests + an import-map check for one contract move is still Lite. Full requires packages a reviewer could accept or reject independently — not merely multiple commands that prove the same deliverable.

**Load-bearing ≠ Full.** A shared package others will import later can still be a Lite extraction plan. Choose Full when wrong sequencing *during this plan* would get built on, not because the result will be reused later.

**When torn between Lite and Full:** choose Full only if a reviewer could plausibly reject one part while approving the rest. If the whole change stands or falls together, it is Lite.

### What each tier requires

| | Direct | Lite | Full |
|--|--------|------|------|
| Plan file | — | ✓ | ✓ |
| Global Constraints section | — | only if the spec has them | ✓ |
| Execution Schedule table | — | — (single work unit) | ✓ |
| Review checkpoints | — | one review at the end | ✓ as declared |
| Plan reviewer subagent | — | — (self-check instead) | ✓ |
| Documentation update | fold into the change | final task of the plan | own work unit + checkpoint |
| Execution path | implement inline | playbook:executing-plans, or inline | playbook:subagent-driven-development |

This table is the contract downstream skills read. Do not invent a fourth shape.

## Step 2: Map the files

Before defining tasks, map which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure — but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

## Step 3: Decompose

**Scope check:** if the spec covers multiple independent subsystems, suggest breaking this into separate plans — one per subsystem, each producing working, testable software on its own.

Plans use two levels of decomposition:

| Concept | Purpose | Granularity |
|---------|---------|-------------|
| **Task** | Planning fidelity — files, interfaces, TDD steps | Smallest independently testable chunk |
| **Work unit (WU)** | Execution dispatch — one subagent, reviewed at the next checkpoint | One cohesive deliverable; often spans several tasks |

**Steps** (2–5 min TDD actions) live inside tasks. **Tasks** define what to build. **Work units** define how execution dispatches the work. A detailed Full plan may have 12 tasks and 4 work units. A Lite plan has one work unit and does not name it.

### Task right-sizing

A task is the smallest unit that carries its own test cycle. Fold setup, configuration, scaffolding, and documentation steps into the task whose deliverable needs them; split only where the deliverable or test surface is genuinely separate. Each task ends with an independently testable deliverable.

Task boundaries optimize for **planning clarity**, not dispatch. Each step inside a task is one action of 2–5 minutes: write the failing test, run it and watch it fail, write the minimal implementation, run the tests, commit.

### Work unit sizing (Full only)

A work unit is **one cohesive deliverable a reviewer could accept or reject on its own.**

- **Merge** tasks when they share files, when one is pure scaffolding for the next, or when dispatch overhead would dominate the work
- **Split** when tasks cross test surfaces or subsystems, or when a reviewer could reject one while approving its neighbor
- **Ceiling:** roughly 45 minutes of implementer time and about 5 commits. This is where a work unit becomes too big to review as one thing — **it is not a quota to fill.** Never add scope, tasks, or abstraction to reach it. A twenty-minute change is one work unit, and a Lite plan besides.

## Step 4: Write the plan

### Lite plan

One page. No Execution Schedule, no work unit table, no separate documentation work unit.

````markdown
# <Feature> Plan

**Tier:** Lite      **Goal:** <one sentence — what this builds>

**Files**
- Create: `src/export/filename.ts` — builds the download filename
- Modify: `src/export/dialog.tsx:120-150` — call the builder instead of inlining
- Test: `tests/export/filename.test.ts`

### Task 1: Filename builder

**Produces:** `buildFilename(project: string, at: Date): string`

- [ ] Write failing tests in `tests/export/filename.test.ts`:
      `slugifies the project name`, `appends an ISO date`,
      `truncates names over 64 chars`
- [ ] Run `npm test tests/export/filename.test.ts` — expect FAIL, no such module
- [ ] Implement `buildFilename` in `src/export/filename.ts` — slug + `-` + `YYYY-MM-DD`,
      project slug truncated at 64 chars
- [ ] Run `npm test tests/export/filename.test.ts` — expect PASS
- [ ] Commit

### Task 2: Wire the dialog and close out

- [ ] Replace the inline filename expression at `src/export/dialog.tsx:134` with
      `buildFilename(project.name, new Date())`
- [ ] Run `npm test` — expect PASS
- [ ] Run playbook:docdriven-audit in change-scoped mode over `<base>..HEAD`;
      apply what it flags per playbook:docdriven
- [ ] Commit
````

**The last task always closes out:** the full test command, the change-scoped documentation audit, and a commit. That is how a Lite plan keeps the docs-never-go-stale invariant without a dedicated work unit and checkpoint.

### Full plan header

**Every Full plan starts with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use playbook:subagent-driven-development (recommended) or playbook:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Tier:** Full

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

## Execution Schedule

| WU | Tasks | Summary | Files (write) | Depends on | Wave | Review |
|----|-------|---------|---------------|------------|------|--------|
| WU-1 | 1–2 | Auth types + store | `src/auth/types.ts`, ... | — | 1 | — |
| WU-2 | 3–5 | Export parser | `src/export/parser.ts`, ... | — | 1 | — |
| WU-3 | 6 | Export API wiring | `src/api/export.ts` | WU-1, WU-2 | 2 | ✅ checkpoint |
| WU-4 | 7 | Documentation update (docdriven) | `docs/...` | WU-3 | 3 | ✅ checkpoint |

- **Tasks:** inclusive range of plan task numbers this work unit implements
- **Depends on:** work units that must complete before this one starts
- **Wave:** parallel group — work units in the same wave have no blocking dependencies on each other and must not write the same files
- **Review:** `✅ checkpoint` marks a review gate after this work unit; `—` means execution continues straight to the next work unit

---
```

The Execution Schedule is required before a Full plan's review. Do not offer Full-plan execution without it.

**Parallelization:** work units in the same wave have no `Depends on` relationship to each other and must have **disjoint write file sets**. Integration and wiring work units go in later waves after their dependencies.

### Review checkpoints (Full only)

**The plan decides where implementation gets reviewed.** Reviewing after every work unit spends real time without producing progress; reviewing only at the very end lets an early mistake get built on. Checkpoints sit where a mistake would actually be expensive.

Place a checkpoint on a work unit when:

- It **completes a logical package** — a coherent slice of behavior that stands on its own (the data layer is done, the parser works end to end)
- **Other work units depend on it.** The `Depends on` column is the signal: when several later work units consume a work unit or group, review before they build on it
- It is the **last code work unit** — required
- It is the **documentation work unit** — required

Target roughly **one checkpoint per two to four work units**, plus the two required ones. A three-work-unit package with a checkpoint at its end is right; three consecutive checkpoints inside it is not.

A checkpoint reviews **everything since the previous checkpoint**, not just the last work unit — the reviewer sees the whole package as one diff, which is also how it catches integration problems a single-unit review misses.

### Documentation work unit (Full only)

**Every Full plan's final work unit is the documentation update.** It is always in its own last wave, depends on all preceding work units, and always carries a review checkpoint. A Full plan without it fails plan review. On a Lite plan the same job is the last task's audit step — do not promote it to a work unit.

Copy [docs-work-unit-template.md](docs-work-unit-template.md) into the plan as its final task, filling in the feature name and affected domains.

The work unit **discovers** what to document rather than following a pre-written list, and it delegates both halves of that job:

| Job | Skill |
|-----|-------|
| Find which docs became false, from the diff | playbook:docdriven-audit, change-scoped mode |
| Write the updates correctly | playbook:docdriven |

Why discovery instead of a list: at spec time the code does not exist, so any list of docs to update is a guess that goes stale as soon as a plan task changes. At the end of implementation the evidence is real. This also means the docs describe what was **built** — where implementation diverged from the spec, the divergence gets documented and recorded in `gaps.md` instead of silently contradicting the docs.

**Do not restate documentation rules in the plan.** The plan's docs task names the two skills and the diff range; those skills carry the procedure.

### Full task structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

`function(input: Input) -> Output` in `src/path/file.py` — [what it does,
in terms the test already pins]

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Completeness

**A step is complete when the implementer cannot make a wrong choice from it** — not when it contains the most text. Show code where the code *is* the decision; use prose where prose pins the outcome exactly.

**Always show the real content:**
- Test cases — names, inputs, expected values
- Interfaces — signatures, parameter and return types, exported names
- Data shapes — schemas, migrations, config values, user-visible copy
- Commands — exact invocation and expected output

**Prose is enough** for an implementation step whose test and signature already determine the behavior. Name the function, its signature, and what it does. Pre-writing a function body the test already specifies makes the plan the change written twice — once in Markdown, once in code — and only the second one runs.

**Never write these** — they are plan failures:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases" — name the errors, the rules, the cases
- "Write tests for the above" without test names and assertions
- "Similar to Task N" — repeat it; tasks get read out of order
- Steps that state an outcome without the interface or command that pins it
- References to types, functions, or methods no task defines

**One exception:** the documentation work unit's file list is discovered at execution time, because which docs became false is only knowable from the finished diff. Its steps must still be complete — the discovery procedure itself is the content.

Mechanical code is still worth transcribing when it is genuinely mechanical: subagent-driven-development dispatches fully-specified work units on the cheapest model. That is a reason to spell out rote code, not a reason to spell out all of it.

## Step 5: Check the plan

### Lite: self-check

No reviewer dispatch. Read the plan once against four questions — all four answer yes, or you fix it:

- Is every file the change needs in the file map?
- Does every task end with a command that proves it?
- Does every step pin its decisions, leaving nothing for the implementer to invent?
- Does the last task run the full test command and the change-scoped docs audit?

Fix what fails and move to execution. If the plan keeps failing these because it has grown several deliverables, it was a Full plan — re-size it rather than patching.

### Full: one reviewer pass

**Review subagent:** check whether your runtime has a dedicated review subagent configured. **OpenCode:** use your `review` subagent (`Subagent (review):` in [plan-reviewer-prompt.md](plan-reviewer-prompt.md)). **Other runtimes:** look in platform config, agent manifests, or project docs for a subagent named `review`, `code-reviewer`, or similar with readonly/edit-deny permissions — use it when present. Fall back to `general-purpose` only when no review subagent exists. Do not substitute an inline self-review when a review subagent is available. When subagents are unavailable entirely, perform the same review scope yourself in readonly mode.

After writing and saving the complete plan including its Execution Schedule, dispatch **one** readonly plan reviewer using [plan-reviewer-prompt.md](plan-reviewer-prompt.md). Fill in `[PLAN_FILE_PATH]`, `[SPEC_FILE_PATH]`, and `[GLOBAL_CONSTRAINTS]` copied verbatim from the plan.

Fix blockers yourself, then proceed to execution. Do not re-dispatch the reviewer after self-fixes — only when the user edits the plan or you changed scope by adding or removing tasks.

**Scope:** spec traceability, buildability, **parsimony** (no unnecessary new components, types, or files where something existing should be extended; fixtures and helpers reused), and Execution Schedule topology — including the documentation work unit and sane checkpoints. It does not re-audit whether the design is doable.

**Reviewer prompt rules:**
- Do not pre-judge findings — let the reviewer raise issues; you adjudicate when fixing
- Do not paste session history into reviewer dispatches — paths and global constraints only
- Advisory items do not block approval; fix blockers only unless you choose to act on advisory suggestions
- If a finding conflicts with an intentional spec decision, present both to the user and ask which governs

## Step 6: Hand off to execution

The tier decides the execution path — do not offer a menu the tier already settled.

**Lite:**

> "Plan saved to `docs/playbook/plans/<filename>.md` — one work unit. I'll execute it directly with playbook:executing-plans unless you want subagent dispatch."

**REQUIRED SUB-SKILL:** playbook:executing-plans, or implement inline for the shortest plans.

**Full:**

> "Plan complete and saved to `docs/playbook/plans/<filename>.md`. Two execution options:
>
> **1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per work unit, parallel within waves, review at the plan's checkpoints
>
> **2. Inline Execution** — I execute work units in this session using executing-plans, batch execution with checkpoints
>
> Which approach?"

- Subagent-Driven → **REQUIRED SUB-SKILL:** playbook:subagent-driven-development
- Inline → **REQUIRED SUB-SKILL:** playbook:executing-plans

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll write the full template to be safe" | The template is the Full tier. Safety on a small change is cost, not rigor. |
| "This Lite plan needs an Execution Schedule too" | Then it is a Full plan, or it is padded. Re-read Step 1. |
| "It touches three runtimes / five check commands, so Full" | One deliverable that stands or falls together is Lite. Independently reviewable packages make Full. |
| "Others will import this package, so Full" | Reuse later is not sequencing risk during this plan. Lite extractions are allowed. |
| "Let me add a task so the work unit hits 45 minutes" | The ceiling is a limit, never a quota. Ship the small work unit. |
| "I should spell out every function body" | Spell out decisions. A body the test already pins is transcription. |
| "One more reviewer pass will help" | One pass, then you fix. Loops that don't change the outcome are waste. |
| "The user asked for a plan, so it needs the whole shape" | Ask which tier they want, or size it yourself and say so. |
