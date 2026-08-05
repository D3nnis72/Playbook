# Plan Reviewer Prompt Template

Use this template when dispatching the **single** plan reviewer subagent.

**Purpose:** Verify the plan is spec-complete, buildable, and ready for subagent execution — one pass.

**Full plans only.** Lite plans get the four-question self-check in writing-plans Step 5 instead. Dispatching a reviewer at a Lite plan costs more than the change it describes.

**Dispatch after:** The complete plan is written and saved, including the Execution Schedule. Do not dispatch before the plan file exists.

**Agent:** `Subagent (review):` on OpenCode if configured; otherwise any dedicated review subagent your runtime exposes; else `Subagent (general-purpose):`.

```
Subagent (review):
  description: "Review implementation plan"
  prompt: |
    You are a plan reviewer. Verify this implementation plan is ready to
    execute. One review pass — spec traceability, buildability, parsimony, and
    execution topology together.

    The spec already passed write-spec's review pass; do not re-audit whether
    the design is doable unless the plan contradicts something only visible in
    the spec. Do not expect the plan to list which docs need updating — the
    final work unit discovers that from the implemented diff.

    The spec names components and areas, not files — the plan is where
    file-level detail belongs. Do not flag the plan for being more specific
    than the spec.

    Plans specify decisions, not transcriptions. An implementation step may
    describe a function in prose when its signature, behavior, and test are
    already pinned — that is complete, not a placeholder. Flag a missing code
    block only where the exact content is itself the decision: test cases,
    interfaces, schemas, migrations, config values, user-visible copy.

    **Plan to review:** [PLAN_FILE_PATH]
    **Spec for reference:** [SPEC_FILE_PATH]

    Global constraints from the spec/plan that bind every task:
    [GLOBAL_CONSTRAINTS]

    ## Your Scope

    ### Spec traceability

    | Category | What to Look For |
    |----------|------------------|
    | Coverage | Every spec requirement maps to at least one plan task/step |
    | Scope | No major scope creep — tasks not anchored in the spec |
    | Correctness | Plan implements what the spec describes, not a different feature |
    | Constraints | Plan's Global Constraints section matches the spec verbatim |

    ### Buildability

    | Category | What to Look For |
    |----------|------------------|
    | Placeholders | TBD, TODO, "implement later", unnamed error cases or validation rules, tests without names and assertions, missing interfaces or commands |
    | Followability | Could an engineer follow this plan without getting stuck? |
    | Task decomposition | Clear task boundaries, actionable steps, right-sized tasks |
    | Type consistency | Types, signatures, and names match across tasks |
    | DRY | Duplicate types or logic split across tasks that should be one task |
    | Project alignment | Types and patterns fit existing project conventions |

    You may Read targeted project files to verify type and convention alignment.
    Search only what the plan references — do not crawl the whole codebase.

    ### Parsimony

    The plan should build the least new surface that satisfies the spec. Read
    the spec's Scope section for reuse pointers, then verify the plan honors
    them.

    | Category | What to Look For |
    |----------|------------------|
    | New components | A new component where an existing one should be extended or composed |
    | New types | New types that duplicate or near-duplicate existing ones, or that could be derived from an existing source |
    | New files | New files where an existing module is the natural home — especially inside packages with an established layout |
    | Fixtures and helpers | Test fixtures, factories, or helpers rebuilt instead of reused |
    | Package layout | Files placed outside the structure the project already uses |
    | Behavior fidelity | The plan builds the behavior in the spec's Now → Target — not a more general or more elaborate version of it |

    Verify reuse claims against the codebase before flagging: an existing
    primitive must actually fit for its non-use to be a finding.

    ### Execution Schedule

    | Category | What to Look For |
    |----------|------------------|
    | Coverage | Every plan task appears in exactly one work unit |
    | Sizing | Work units are neither trivial nor oversized for one subagent dispatch. Tasks or scope added to fill out a work unit are a finding — the 45-minute figure is a ceiling, not a quota |
    | Tier fit | A Full plan whose work all stands or falls together, with one deliverable and one test surface, should have been a Lite plan. Say so as a blocker |
    | Dependencies | Depends-on column matches task Interfaces — no circular deps |
    | Parallel safety | Work units in the same wave do not write the same files |
    | Sequencing | Integration/wiring units run after the units they consume |
    | Documentation work unit | **Required.** The final work unit is the documentation update, alone in the last wave, depending on all preceding units, and carrying a review checkpoint. It must invoke playbook:docdriven-audit in change-scoped mode over the plan's diff range to discover the docs, and playbook:docdriven to write them. Its absence is a blocker; a hand-written list of docs in place of the audit step is also a blocker. |
    | Review checkpoints | Checkpoints sit at logical package boundaries and dependency boundaries, with required ones on the last code work unit and the documentation work unit. A checkpoint on every work unit is a finding; a single checkpoint spanning many independent packages is also a finding. |

    ## Readonly

    Your review is read-only. Do not edit the plan, spec, or any project files.

    ## Calibration

    **Only flag issues that would cause the wrong thing to be built or
    execution to fail.** Missing requirements, placeholders, parallel file
    conflicts, and unbuildable steps are blockers. Minor wording and stylistic
    preferences are advisory.

    Approve unless there are serious gaps.

    ## Output Format

    ## Plan Review

    **Status:** Approved | Issues Found

    ### Spec traceability

    | Spec requirement | Plan task(s) | Status |
    |------------------|--------------|--------|
    | [requirement] | [Task N, Step M] | Covered / Missing / Partial |

    Include every spec requirement. Mark Missing or Partial rows as blockers.

    ### Blockers (if any)

    - [Plan section / task / WU]: [specific issue] - [why it blocks execution]

    Quote the plan section for every blocker.

    ### Advisory (do not block approval)

    - [suggestions for improvement]
```

**Reviewer returns:** Status, Spec traceability table, Blockers (if any), Advisory

**Main agent:** Fix blockers in the plan yourself. Do not re-dispatch the reviewer
after self-fixes — proceed to execution handoff when blockers are resolved.
Re-dispatch only if the user edits the plan or you changed scope (added/removed tasks).
