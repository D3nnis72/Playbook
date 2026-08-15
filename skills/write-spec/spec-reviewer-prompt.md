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

    A spec is a human-readable design note: what we intend, what done looks
    like, how it works at name level, and what to respect. Prefer prose over
    tables. It is NOT an implementation plan. Exact file paths, code blocks,
    signatures, and step sequences belong in the plan — flag them here as scope
    leakage, not as missing detail.

    The reverse is also a finding. A spec must name the things its design
    introduces and say why load-bearing choices won — in Approach prose.
    Names and settled field lists at that level are Approach content, not
    leakage. Judge detail by whether it is a name/shape or a location, not by
    how specific it feels. Do not demand a data model the handoff never had.

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
    | Approach | The mechanism the handoff approved is present and named in prose — rule, named units, choices and why. Named units should make clear what *kind* of thing they are and which area owns them (UI vs durable state vs shell mode, etc.). Field lists only if the handoff settled them — do not demand a schema. A behavior-only Vision while the handoff settled a design is **missing detail** |
    | Readability | After Vision (including Target), a colleague who missed the brainstorm could understand intent and done state. A mostly-tabular spec is a finding |
    | Target | Free-text done state under Vision. Required tables, empty Today grids, or Target missing entirely are findings |
    | Decisions | Settled trade-offs live in Approach next to what they decide. A standalone Decisions table is legacy — advisory to fold in, not a reason to demand one |
    | Not now | Exclusions do not contradict what Vision promises |
    | Ambiguity | Requirements interpretable two ways |

    ### Project alignment

    | Category | What to Look For |
    |----------|------------------|
    | Current state | Claims about today in Vision/Target match the codebase when they assert current behavior. Greenfield with no baseline is fine — do not demand a Today table |
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
    | Verification form | Prefer structured prose walkthrough over a bullet inventory. UI/mixed: expected user flow (screens, navigation). Backend/data: verify path (contracts, schemas, observable result). Do not demand a fake user journey for pure backend work |
    | Verification tier | Tier matches the deliverable. Check is the default for M. Do not demand Flow or a long scenario list for a contract/ownership move |
    | Verification bulk | A QA checklist or unit-test-shaped case per Approach unit is over-testing — cut to the ship-decision path. Prefer existing suites over inventing new ones |
    | Scenario quality | A reader can tell what to walk through when the slice is done. Formal Given/When/Then is optional |
    | Scope leakage | File paths, code blocks, signatures, SQL, or step-by-step instructions that belong in the plan. Naming a projection, view, module, or check, and listing the fields a brainstormed shape carries, is Approach content — do not flag it |
    | Design homelessness | Mechanism and why missing from Approach, or Target stuffed with call-shape/mechanism prose that belongs in Approach |

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
