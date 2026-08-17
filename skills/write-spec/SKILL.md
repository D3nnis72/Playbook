---
name: write-spec
description: Use when design is approved in brainstorming and you need to author the design spec file, validate it against the project, or hand off to writing-plans
---

# Write Spec

## Overview

Author and validate a design spec from an approved brainstorming outcome. Size the work, write the spec, run **one** review pass, get user approval, then invoke writing-plans.

A spec is a **human-readable design note**: what you intend, what done looks like, how it works at name level, and what the implementer must respect. Prefer prose over tables. Tighten: each fact lives in one section. Normal English, not telegram. It is not an implementation plan. If a section could be pasted into a plan as-is — exact file paths, code blocks, step sequences — it belongs in writing-plans, not here.

**Announce at start:** "I'm using the write-spec skill to author and validate the design spec."

**Inputs:** Approved brainstorming **Canvas** (`docs/playbook/canvases/...`) when one exists; otherwise the approved design in this session.

**Outputs:**
1. Spec file: `docs/playbook/specs/YYYY-MM-DD-<topic>-design.md` — **temporary** working artifact, not durable product knowledge
2. Optional companion — same directory, `YYYY-MM-DD-<topic>-<kind>.md` where `<kind>` is `roadmap` or `adr` (roadmap is temporary with the canvas; keep an ADR only when the team wants a durable decision record outside knowledge docs)

**Not an output: documentation updates.** This skill never edits canonical docs and never guesses which docs will need editing. Canonical docs explain current truth, and the code does not exist yet. Every plan's final work unit discovers and performs the doc updates from the real diff — see writing-plans. After that, leftover playbook files may only hold remaining work: delete or strip specs/plans/canvases; ask only when dependencies or ownership are unclear.

## Checklist

You MUST create a task for each item and complete them in order:

1. **Read the Canvas** — the approved brainstorm summary this spec distills from; if there is no canvas, use the approved design in this session
2. **Carry what the conversation already settled** — kind + home + any shapes from the canvas into Approach
3. **Size the work** — S / M / L; **S exits this skill**
4. **Write the spec** — at the detail level the size allows, save to `docs/playbook/specs/`
5. **Review pass** — dispatch one reviewer, fix blockers yourself, no re-review
6. **User review gate** — user approves the written spec
7. **Transition to planning** — invoke writing-plans

## Process Flow

```dot
digraph write_spec {
    rankdir=TB;
    node [shape=box];

    "Read Canvas" -> "Size the work (S/M/L)";
    "Size the work (S/M/L)" -> "Exit: implement, or writing-plans at Lite tier" [label="S"];
    "Size the work (S/M/L)" -> "Write spec at sized detail level" [label="M or L"];
    "Write spec at sized detail level" -> "Dispatch spec reviewer (./spec-reviewer-prompt.md)";
    "Dispatch spec reviewer (./spec-reviewer-prompt.md)" -> "Approved?";
    "Approved?" -> "Fix blockers in spec" [label="no"];
    "Fix blockers in spec" -> "User review gate" [label="self-fix, no re-review"];
    "Approved?" -> "User review gate" [label="yes"];
    "User review gate" -> "Write spec at sized detail level" [label="changes"];
    "User review gate" -> "Invoke writing-plans skill" [label="approved"];
}
```

**The terminal state is invoking writing-plans.** Do NOT write implementation plans, code, or invoke subagent-driven-development here.

<HARD-GATE>
Do NOT invoke writing-plans until the review pass is clean (or its blockers are fixed) AND the user approves the written spec. Do NOT edit canonical documentation in this skill. Do NOT commit until the user approves — and only when the user requests a commit.
</HARD-GATE>

## Step 1: Carry what the conversation already settled

After reading the canvas (or the approved design in session), pull into Approach anything concrete enough that a plan would otherwise re-invent it: **what kinds of things this slice creates** (UI step, durable record, shell mode, entry resolver, gate, …), **which area owns each**, and any **fields/shapes** the conversation already agreed. Skip inventing columns, enums, or schemas that were never discussed.

## Step 2: Size the work

Detail is proportional to size. Decide the size **before** writing anything, and state it in the spec header.

| Size | Looks like | What to write |
|------|------------|---------------|
| **S** | One contained change: a component tweak, a copy change, a fix with a known cause, one endpoint's behavior | **No spec.** Implement directly, or write a **Lite** plan when the user wants an artifact — say the tier out loud so writing-plans does not default to its Full shape. |
| **M** | One capability or contained change — even when it touches several files, runtimes, or domains. No new product flow; Verification is usually a short Check walkthrough | `Vision` (with `Target`), `Scope`, short `Verification`, plus `Approach` when the design introduces named units or picks a mechanism. Skip `Not now` when there is nothing to exclude. **Usual plan tier: Lite.** |
| **L** | Multiple independent capabilities in one spec, a complete user/system flow, or a new subsystem with Flow-level verification. Touching several domains alone is not L | All sections. **Usual plan tier: Full.** |

**Announce the size and why** in one sentence before writing. If the user disagrees, take their size.

**Multi-domain ≠ L.** A shared-package extraction, a cross-runtime contract move, or a change that lists several Affected domains is still M when it is one capability that stands or falls together. L is for scope that could be split into separate specs, or for a flow others will extend as a subsystem.

Brainstorming already decided whether a spec is warranted at all ("pipeline vs. local fix"). This step decides how much spec. When brainstorming invoked this skill but the work is clearly **S**, say so and move on — do not pad a small change into a full spec.

**Size travels downstream.** Put the expected plan tier in the header (`Direct` / `Lite` / `Full`). writing-plans owns the final call and the tier definitions, but it starts from this hint — do not leave it blank and let "several files" upgrade an M spec into a Full plan.

## Step 3: Spec Format

Fixed section order. Section names are literal — use them verbatim.

| Section | Answers | Content rules |
|---------|---------|---------------|
| **Vision** | What are we intending, and why? | Prose: problem, intent, why it matters. Ends with **`### Target`**. Does not list screens or recap mechanism. |
| **Approach** | How does it work, and why these choices? | Named units with kind + conceptual home; mechanisms and why. Field-level shapes only when brainstorm already settled them. |
| **Scope** | Where does this live and what must be respected? | Short bullets: areas, reuse, docs to read, skills, guardrails. **No file paths, no code.** |
| **Not now** | What are we not building? | Explicit exclusions, one per line. |
| **Verification** | What can you walk through when this is done? | One walkthrough: screens/navigation for UI, contracts/behavior for backend. Not a policy recap or unit-test inventory. |

**Tighten, don't telegram.** Specs stay normal English — articles, full sentences, exact terms. Cut filler, hedging, and restatement. Do not drop articles or write fragments that a later reader has to decode.

**Each fact lives in one section.** Repeating a name to walk through it is fine. Repeating the rule, the why, or the full description is not.

| Section | Owns | Does not own |
|---------|------|----------------|
| **Vision** | Problem, intent, why. Short baseline if something exists today. | Screen inventory, mechanism, walkthrough |
| **Target** | Done state: what exists, how surfaces behave, what is gone. Named surfaces once. | How it works, why a choice won |
| **Approach** | Named units (kind + home + rule). Load-bearing why. Unchanged. | Repeating Target. File paths. |
| **Scope** | Areas, reuse, docs, skills, guardrails | Design restated as bullets |
| **Verification** | One walkthrough that would change a ship decision | Re-explaining Approach units or Target policy |

**Prefer prose over tables.** Specs are design notes people read. Tables are allowed only when a comparison is genuinely clearer as a grid (rare). Target, Approach, and Verification use tight sentences or short bullets — not essays, not telegram. Verification may be a light numbered walkthrough. A spec that is mostly tables, or that tells the same fact in Vision, Target, Approach, and Verification, fails review.

**Header block** — every spec starts with it:

```markdown
**Size:** M      **Type:** frontend      **Plan tier:** Lite      **Depends on:** —      **Canvas:** —
```

`Type` is `frontend`, `backend`, `data`, or `mixed`. It steers what Target should describe, not which table template to fill. `Plan tier` is the expected writing-plans tier (`Direct` / `Lite` / `Full`) — writing-plans may revise it, but only with a stated reason. `Canvas` links the brainstorming canvas this spec was distilled from; use `—` when there was none.

**`Depends on` — one canonical spec per concept.** Before writing, scan `docs/playbook/specs/` for specs whose subject overlaps this one. Declare each as a link with its relation: **depends on** (this consumes a contract, model, or flow that spec defines), **supersedes** (this replaces part of it — name the part), or **overlaps** (both touch a shared surface that could drift — name the surface). Reference the other spec's content; never restate it. Restated content becomes a second source of truth and will drift. Use `—` when there are none.

**Readability test:** after Vision (including Target), would a colleague who missed the brainstorm understand the intent and the done state in one sitting? If they would reach for a decoder ring, the spec fails review. If they would notice the same rule or description three times, it also fails — tighten, don't add a fourth telling.

### Vision

Write the shared vision of what you intend to do with this work — in human form, for a reader who was not in the brainstorm. Length follows the idea: a small capability may need a paragraph; a cross-domain redesign may need a page. Be as technical as the idea needs to be clear. File paths and step sequences still belong in the plan, not here.

Cover what matters for shared understanding: the problem or opportunity in this project's context, what you intend to build, why it matters, and — when something already exists — what is wrong or incomplete about today. Do not pad, and do not truncate a real vision to hit a sentence count. Do not preview Target's surface list or Approach's mechanism — those belong below.

Every Vision ends with a **`### Target`** subsection — free text describing the done state. Write it as you would explain to a teammate: what exists when this is finished, how the important surfaces behave, what is gone. Name surfaces once here. No Today/Done tables, no step grids unless a tiny comparison truly helps (and even then prefer two short paragraphs).

By `Type`, make sure Target covers the right kind of done state:

| Type | Cover in prose |
|------|----------------|
| **frontend** | What the user sees and can do when it is done; important UI states |
| **backend** | Who calls what, and what contracts or results exist at done |
| **data** | What the model or derivation looks like at done, and which consumers care |
| **mixed** | The cross-boundary outcome once — not one mini-essay per layer |

**Baseline is optional.** When something already exists, say what is wrong with today inside Vision or Target in a sentence or two. Greenfield needs no fake before-state.

Approach owns how the design works; Target owns what done looks like. Do not turn Target into a mechanism dump, and do not recap Target inside Approach.

**UI mockups:** Brainstorm already put Markdown mockups on the canvas, grounded in this project's components. During or after the spec, only promote those into a real in-app / route mock when that would clarify a still-open choice — do not redesign arbitrarily outside the project's design system.

### Approach

The design the brainstorm settled, at a level someone can hold in their head — and the reasons that matter. Without this section the mechanism has nowhere to live and gets forgotten between chat and plan.

Write tight sentences or short bullets — two to four sentences per named unit, not an essay wrapping it. Cover:

- **The rule** — the one or two sentences that make the change coherent, plus any corollaries.
- **Named units** — `**Name** — kind, conceptual home. Rule. Why, when the choice is load-bearing.` Say (1) **what kind of thing it is** (UI step, durable record, shell mode, entry use-case, gate, bootstrap hook, …), (2) **which area owns it** conceptually (onboarding domain, workspace shell, Career Profile, …), and (3) what it is responsible for. Enough that a reader knows whether this slice creates UI, durable state, both, or something else — not file paths or component inventories. Stop. Do not recap other units or Target.
- **Settled shapes** *(only if the conversation already went there)* — fields, relationships, or payloads next to the unit they belong to. Omit when brainstorm stayed at intent; do not invent a model to look complete.
- **Mechanism and why** — the load-bearing choices *and* why they won. Decisions live here, next to the thing they decide.
- **Unchanged** — what this deliberately leaves alone, so the plan does not go looking.

**Level test — kind and home, not locations.** “A durable onboarding workflow record owned by the onboarding domain” belongs here. `src/onboarding/...` and SQL belong in the plan. Field lists belong here only when already agreed.

**By size:** L always. M when the design introduces named units or picks a mechanism — skip it when the change is behavior with an obvious implementation. S has no spec at all.

**No separate Decisions section.** A standalone Decisions table is legacy. If you find yourself building one, fold each row into the Approach paragraph it belongs to.

### Scope

This is the section that orients the implementer without doing the plan's job. Cover, in short bullets:

- **Areas and components involved** — named at component level: "the export dialog and the billing store", not `src/features/export/ExportDialog.tsx`
- **Reuse pointers** — what already exists that must be used instead of rebuilt: "a date-range picker already exists — extend it, do not add another"
- **Docs to read** — the canonical docs that *constrain* this work (see below)
- **Skills to use** — the domain skills that govern this work
- **Guardrails** — what the implementer must not violate: patterns to follow, boundaries not to cross, performance or accessibility floors that apply
- **Affected domains** — DocDriven domain IDs from `docs/agent/manifest.json`, when the project uses them. The plan's documentation work unit uses these to load route shards.

**Docs to read** is not a generic pointer at the docs folder — name the specific documents this work must obey, chosen by what is being built. Read the project's `docs/agent/manifest.json` route shards for the affected domains and take their `readFirst` entries as the starting point, then add anything the work type demands:

| Work involves | Name docs like |
|---------------|----------------|
| Frontend / UI | Frontend architecture, design language and visual system, component and state conventions, accessibility baseline |
| Backend / API | Backend architecture, API and contract conventions, auth and permission model, error and logging conventions |
| Data / schema | Data model doc, migration policy, derivation and read-model rules |
| Integrations / machine-to-machine | The integration's own contract doc, retry and idempotency policy, secret and credential handling |
| Infrastructure / deployment | Environment and config doc, deployment and rollback policy |

The list should be short and specific: three or four documents an implementer must read before starting, not everything that mentions the topic. If a needed doc does not exist, say so — that is a gap worth recording rather than an excuse to invent conventions.

**Skills to use** names the domain skills the implementer should invoke — the Supabase skill for edge functions and Postgres, the frontend design skill for new interface surfaces, the shadcn skill for component work, and so on. The plan repeats them per task; the spec establishes which apply at all.

**Docs to read are not docs to update.** Which docs need *updating* is discovered after the code exists — the plan's final work unit runs a change-scoped docdriven audit against the real diff. Do not try to predict that list here.

### Verification

Describe **what someone should be able to walk through when this slice is done** — the expected delivered flow, not a test-case inventory and not a recap of Approach.

Write it as a readable path (short paragraphs or a light numbered walkthrough). Name the surfaces as you walk them; do not re-explain their rules. Formal Given/When/Then is optional and usually worse here.

**By type:**

| Type | Verification reads like |
|------|-------------------------|
| **frontend** / **mixed with UI** | A **user flow**: which screens or steps exist, how you enter them, where you can go next (continue / back / exit), what you confirm along the way, and what “done for this slice” looks like. Name the path, not every assertion. |
| **backend** / **data** | A **verify path**: which functions or contracts exist, which schemas or records are in place, who can call what, and what observable result proves it (command, response shape, persisted row). No fake user journey. |
| **mixed** | One cross-boundary walkthrough when the UI and backend meet; do not split into two mini-test plans. |

**Default lean.** Prefer extending or running checks that already exist over inventing a new unit-test suite in the spec. Over-specifying tests is a review failure: a bullet list that mirrors every Approach unit usually means the spec is doing the plan's job.

State a tier so the plan knows how heavy to automate:

| Tier | When | What the prose covers |
|------|------|------------------------|
| **Check** | Most M work; refactors; ownership moves | A short verify path — one or two things you can observe or run |
| **Component** | One contained capability with real branches | The main happy path plus the branches that would change a ship decision |
| **Flow** | A complete user or system journey | The end-to-end walkthrough (screens or call sequence) for this slice |

Keep it short enough to read once. If it turns into a QA checklist or restates Approach policy, cut to the path that would change a ship decision.

This section is acceptance criteria for the plan. writing-plans turns it into verification steps; it must not invent a unit test for every named Approach unit unless the flow actually requires it.

### Global constraints (optional)

Project-wide requirements that bind every task: version floors, dependency limits, naming and copy rules. Include only when they exist. writing-plans copies this section into the plan verbatim.

### Canonical Template

````markdown
# <Feature Name>

**Size:** M      **Type:** mixed      **Plan tier:** Lite      **Depends on:** —      **Canvas:** —

## Vision

<Short prose: what you intend to build in this project's context, why it
matters, and what is wrong or incomplete about today when something already
exists. Do not list surfaces or recap mechanism.>

### Target

<What done looks like. How the important surfaces behave. What is gone.
Name surfaces once. No required tables.>

## Approach

<The governing rule. Each named unit in two to four sentences: kind +
conceptual home + rule; why when load-bearing; what stays unchanged.
Shapes only when brainstorm already settled them. Do not recap Target.>

## Scope

**Areas involved**
- ...

**Reuse**
- ...

**Docs to read**
- `docs/knowledge/...` — why this one constrains the work

**Skills to use**
- ...

**Guardrails**
- ...

**Affected domains:** ...

## Not now
- ...

## Global constraints
- ... (optional)

## Verification

**Tier:** Flow | Component | Check

<One walkthrough when this slice is done. For UI: screens, navigation, what
you confirm. For backend: contracts, schemas, and the observable verify
path. Name surfaces; do not re-explain their rules.>
````

There is no doc-impact section. Documentation updates are discovered from the real diff and performed by the plan's final work unit.

**Legacy specs** may use Problem / Goal / Non-Goals / Design / Testing Strategy, a standalone Decisions table, Today/Done grids, the older Vision Contract, or a top-level `Now → Target` section. Migrate when implementation touches them: fold decisions into Approach prose, Target into free text under Vision, and Blueprint file-level detail into the plan.

## Step 4: Review Pass

**One pass. One reviewer. No re-review.** Iterations that do not change the outcome are waste — the reviewer reports, you fix, you move on.

**Review subagent:** Check whether your runtime has a dedicated review subagent configured. **OpenCode:** use your `review` subagent (`Subagent (review):` in the prompt template). **Other runtimes:** look in platform config, agent manifests, or project docs for a subagent named `review`, `code-reviewer`, or similar with readonly/edit-deny permissions — use it when present. Fall back to `general-purpose` only when no review subagent exists. Do not substitute an inline self-review when a review subagent is available. When subagents are unavailable entirely, perform the same review scope yourself in readonly mode.

Dispatch using [spec-reviewer-prompt.md](spec-reviewer-prompt.md), filling in:
- `[SPEC_FILE_PATH]` — the saved spec
- `[CANVAS_PATH]` — brainstorming canvas path, or "none"
- `[SPEC_SIZE]` — S / M / L from the header
- `[GLOBAL_CONSTRAINTS]` — the spec's Global constraints section, or "none"

**Scope:** placeholders, canvas fidelity, approach fidelity (named units with kind + home when Approach is present; mechanism-with-why; shapes only if settled), section ownership (no restated rules across Vision/Target/Approach/Verification), human readability, project alignment, verification as a walkthrough (user flow or backend verify path — not a unit-test inventory or policy recap), and scope discipline (no plan-level paths — kind and home are not leakage).

**Dispatch rules:**
- Do not pre-judge findings — the reviewer raises, you adjudicate
- Do not paste session history — pass paths and constraints only
- Advisory items do not block; fix blockers unless the user chooses otherwise
- Fix blockers yourself and proceed — do not re-dispatch the reviewer
- When the runtime supports model selection for subagents, prefer a different model family from the authoring agent. Do not hard-code model slugs.

## Step 5: User Review Gate

After the review pass:

> "Spec written and reviewed at `<path>`. Please review and approve before we write the implementation plan."

Wait for user approval.

**On user changes:** edit the spec. Re-dispatch the reviewer only when the change alters what the spec claims about the project (new components, different current state, changed verification tier). Wording and scope trims do not need another pass.

**Commit:** do not commit until the user approves, and only when the user requests a commit. Commit the spec (and the canvas if it is new or changed).

**Terminal state:** invoke writing-plans — no other skill.
