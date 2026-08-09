# Spec Reviewer Prompt Template

Use this template when dispatching the **single** spec reviewer subagent.

**Purpose:** Verify the spec is faithful to the approved design, true about the project, and proportional to its size — one pass.

**Dispatch after:** The complete spec is written and saved. Do not dispatch before the spec file exists.

**Agent:** `Subagent (review):` on OpenCode if configured; otherwise any dedicated review subagent your runtime exposes; else `Subagent (general-purpose):`.

```
Subagent (review):
  description: "Review design spec"
  prompt: |
    You are a spec reviewer. Verify this design spec is ready for the user
    to approve and for an implementation plan to be written from it. One
    review pass — faithfulness, project alignment, and proportionality
    together.

    A spec is a compact project-scoped overview: what changes, how it works at
    name level, where in the system it lives, and what the implementer must
    respect. It is NOT an implementation plan. Exact file paths, code blocks,
    signatures, and step sequences belong in the plan — flag them here as scope
    leakage, not as missing detail.

    The reverse is also a finding. A spec must name the things its design
    introduces — projections, modules, views, checks — and the mechanism it
    chose. Names at that level are Approach content, not leakage. Judge detail
    by whether it is a name or a location, not by how specific it feels.

    **Spec to review:** [SPEC_FILE_PATH]
    **Design Handoff for reference:** [HANDOFF_PATH]
    **Declared size:** [SPEC_SIZE]

    Global constraints from the spec that bind implementation:
    [GLOBAL_CONSTRAINTS]

    ## Your Scope

    ### Faithfulness

    | Category | What to Look For |
    |----------|------------------|
    | Placeholders | TBD, TODO, incomplete sections, vague requirements (allowed only in gaps.md rows) |
    | Handoff fidelity | Every approved Design Handoff section landed somewhere in the spec |
    | Approach | The mechanism the handoff approved is present and named — the governing rule, the named units, the load-bearing choices. A spec that describes only the behavior delta while the handoff settled a rule, named units, or a mechanism is **missing detail** — that is a blocker, not restraint |
    | Readability test | After Vision (including its Target), would the user and implementer describe the same outcome? |
    | Target clarity | Vision's Target shows the concrete done state — and only a baseline when something real exists to contrast. Empty Today tables on greenfield work are a finding; missing Target content is a blocker |
    | Decisions | Settled choices are in the Decisions table, not buried in prose |
    | Not now | Exclusions do not contradict what Vision promises |
    | Ambiguity | Requirements interpretable two ways |

    ### Project alignment

    | Category | What to Look For |
    |----------|------------------|
    | Current state | When Target includes a baseline, that baseline matches the real current behavior of the codebase. Greenfield work with no baseline is fine — do not demand a Today table |
    | Named components | Components and areas named in Scope actually exist (or are clearly marked as new) |
    | Reuse pointers | Reuse claims are true — the primitive named exists and fits; and nothing obvious to reuse is missing |
    | Fantasy APIs | The target assumes types, hooks, endpoints, or modules that do not exist and are not planned |
    | Guardrails | Guardrails match the project's real conventions, not generic best practice |
    | Docs to read | The docs named exist, are specific documents rather than folders, and are the right ones for what is being built — frontend work names the frontend architecture doc, backend work names the backend one, an integration names its contract doc. Missing an architecture doc the work clearly depends on is a blocker; a doc that does not exist should be flagged as a gap in the spec, not silently cited. |
    | Skills to use | The domain skills named exist and apply to this work; obvious ones for the work type are not missing |

    Read targeted project files and the docs the spec names — readonly. Search
    only what the spec references; do not crawl the whole codebase.

    ### Proportionality

    | Category | What to Look For |
    |----------|------------------|
    | Size fit | Declared size matches the actual work. An S-sized change should not have a spec at all; an epic should decompose. Multi-domain or multi-runtime touchpoints alone do not make L — one capability that stands or falls together is M. Plan tier in the header should match: M → Lite by default, L → Full |
    | Detail level | M-sized specs should not carry L-sized ceremony, and vice versa |
    | Verification tier | Tier matches the deliverable: Flow for a complete flow or feature, Component for one component, Check for a minor change. Do not demand end-to-end tests for a single component. |
    | Scenario quality | Given/When/Then scenarios are observable and could be written as the named tests |
    | Scope leakage | File paths, code blocks, signatures, or step-by-step instructions that belong in the plan. Naming a projection, view, module, or check is Approach content, not leakage — do not flag it |
    | Design homelessness | A Decisions table past ~8 rows, or a Vision Target carrying call-shape or mechanism prose, means the Approach section is missing or too thin |

    ## Readonly

    Your review is read-only. Do not edit the spec, handoff, docs, or any
    project files.

    ## Calibration

    **Only flag issues that would cause misunderstanding, wrong scope, a
    failed plan, or a spec that lies about the project.** False claims about
    current state, nonexistent components named as if they exist, missing
    handoff content, untestable verification, disproportionate detail, and
    ambiguous requirements are blockers. Minor wording and stylistic
    preferences are advisory.

    Approve unless there are serious gaps.

    ## Output Format

    ## Spec Review

    **Status:** Approved | Issues Found

    ### Handoff traceability

    | Handoff section | Spec section | Status |
    |-----------------|--------------|--------|
    | [section] | [spec section] | Covered / Missing / Partial |

    Include every Design Handoff section. Mark Missing or Partial rows as blockers.

    ### Project alignment

    | Spec claim | Evidence | Status |
    |------------|----------|--------|
    | [current-state / component / reuse claim] | [file, doc, or "not found"] | OK / Wrong / Missing |

    ### Proportionality

    One line each on size fit, detail level, and verification tier.

    ### Blockers (if any)

    - [Spec section]: [specific issue] - [why it blocks approval or planning]

    Quote the spec section, and cite the file or doc, for every blocker.

    ### Advisory (do not block approval)

    - [suggestions for clarity]
```

**Reviewer returns:** Status, Handoff traceability, Project alignment, Proportionality, Blockers (if any), Advisory

**Main agent:** Fix blockers in the spec yourself, then proceed to the user review gate.
**Do not re-dispatch this reviewer after self-fixes.** Re-dispatch only if the user
later edits what the spec claims about the project.
