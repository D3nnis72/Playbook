---
name: write-spec
description: Use when design is approved in brainstorming and you need to author the design spec file, validate it against the project, or hand off to writing-plans
---

# Write Spec

## Overview

Author and validate a design spec from an approved brainstorming outcome. Size the work, write the spec, run **one** review pass, get user approval, then invoke writing-plans.

A spec is a **compact project-scoped overview**: what changes, where in the system it lives, and what the implementer must respect. It is not an implementation plan. If a section could be pasted into a plan as-is — exact file paths, code blocks, step sequences — it belongs in writing-plans, not here.

**Announce at start:** "I'm using the write-spec skill to author and validate the design spec."

**Inputs:** Design Handoff artifact from brainstorming (path or structured block).

**Outputs:**
1. Spec file: `docs/playbook/specs/YYYY-MM-DD-<topic>-design.md`
2. Optional companion — same directory, `YYYY-MM-DD-<topic>-<kind>.md` where `<kind>` is `roadmap` or `adr` (only when the design needs a multi-spec slice or a durable decision record)

**Not an output: documentation updates.** This skill never edits canonical docs and never guesses which docs will need editing. Canonical docs explain current truth, and the code does not exist yet. Every plan's final work unit discovers and performs the doc updates from the real diff — see writing-plans.

## Checklist

You MUST create a task for each item and complete them in order:

1. **Read Design Handoff** — path or session block from brainstorming
2. **Size the work** — S / M / L; **S exits this skill**
3. **Write the spec** — at the detail level the size allows, save to `docs/playbook/specs/`
4. **Review pass** — dispatch one reviewer, fix blockers yourself, no re-review
5. **User review gate** — user approves the written spec
6. **Transition to planning** — invoke writing-plans

## Process Flow

```dot
digraph write_spec {
    rankdir=TB;
    node [shape=box];

    "Read Design Handoff" -> "Size the work (S/M/L)";
    "Size the work (S/M/L)" -> "Exit: implement or writing-plans directly" [label="S"];
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

## Step 2: Size the work

Detail is proportional to size. Decide the size **before** writing anything, and state it in the spec header.

| Size | Looks like | What to write |
|------|------------|---------------|
| **S** | One contained change: a component tweak, a copy change, a fix with a known cause, one endpoint's behavior | **No spec.** Go straight to writing-plans, or implement directly if the change is obvious. |
| **M** | One component or one contained capability; a few areas touched; no new architecture | `Vision`, `Now → Target`, `Scope`, `Verification`. Skip `Decisions` and `Not now` when there is nothing contested to record. |
| **L** | A complete flow or feature; new architecture, new integration, cross-domain behavior, anything others will build on | All sections. |

**Announce the size and why** in one sentence before writing. If the user disagrees, take their size.

Brainstorming already decided whether a spec is warranted at all ("pipeline vs. local fix"). This step decides how much spec. When brainstorming handed off but the work is clearly **S**, say so and move on — do not pad a small change into a full spec.

## Step 3: Spec Format

Fixed section order. Section names are literal — use them verbatim.

| Section | Answers | Content rules |
|---------|---------|---------------|
| **Vision** | What are we building, in this project's context? | Human language, 3–6 sentences. What exists today, what exists after, why it matters. No jargon, no file paths. |
| **Now → Target** | What actually changes? | Type-dependent before/after visualization. Only the delta — unchanged behavior is not described. |
| **Scope** | Where does this live and what must be respected? | Areas and components at name level, reuse pointers, docs to read, skills to use, guardrails. **No file paths, no code.** |
| **Decisions** | What is settled? | Lean table. Only entries someone might plausibly re-litigate. |
| **Not now** | What are we not building? | Explicit exclusions, one per line. |
| **Verification** | How do we know it works? | Scaled to what the spec delivers — see Verification Tiers. |

**Header block** — every spec starts with it:

```markdown
**Size:** M      **Type:** frontend      **Depends on:** —
```

`Type` is `frontend`, `backend`, `data`, or `mixed`. It selects the `Now → Target` shape.

**`Depends on` — one canonical spec per concept.** Before writing, scan `docs/playbook/specs/` for specs whose subject overlaps this one. Declare each as a link with its relation: **depends on** (this consumes a contract, model, or flow that spec defines), **supersedes** (this replaces part of it — name the part), or **overlaps** (both touch a shared surface that could drift — name the surface). Reference the other spec's content; never restate it. Restated content becomes a second source of truth and will drift. Use `—` when there are none.

**Readability test:** after Vision and Now → Target, would the user and the implementer describe the same change? If not, the spec fails review.

### Now → Target

Show the delta, minimally, in whatever form makes it fastest to read. Mermaid diagrams, before/after tables, and short step lists all qualify. Pick by `Type`:

| Type | Show |
|------|------|
| **frontend** | User flow before → after (step table or Mermaid), plus the UI states that change |
| **backend** | Contract or call sequence before → after — endpoints, function signatures at name level, who calls whom |
| **data** | Schema or derivation before → after, plus which consumers are affected |
| **mixed** | The flow that crosses the boundary, once — not one section per layer |

Do not restate behavior that stays the same. A reader should be able to point at this section and say "that is the change."

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

### Verification Tiers

Pick the tier that matches what the spec actually delivers. Over-testing a small change is as much a review failure as under-testing a flow.

| Tier | When | Verification looks like |
|------|------|-------------------------|
| **Flow** | The spec delivers a complete user flow or feature — a new user flow, billing, a full information flow | Given / When / Then scenarios written as end-to-end tests: Playwright for frontend flows, request/response e2e for backend functions. Name each scenario so it becomes the test title. |
| **Component** | The spec delivers one component or one contained capability | Component-level checks: states and props behavior, or "extend existing test X with case Y". No full e2e. |
| **Check** | An M-sized change that rode through the spec anyway | One or two observable checks, manual acceptable. Proportionality over ceremony. |

State the tier explicitly so the reviewer can judge proportionality:

```markdown
## Verification

**Tier:** Flow

- **Given** a project with two exports pending, **when** the user opens the export dialog and confirms, **then** both exports move to running and the dialog closes.
```

Written this way, the scenarios **are** the acceptance criteria — writing-plans converts them into tests nearly verbatim. Do not add a separate acceptance-criteria section.

### Global constraints (optional)

Project-wide requirements that bind every task: version floors, dependency limits, naming and copy rules. Include only when they exist. writing-plans copies this section into the plan verbatim.

### Canonical Template

````markdown
# <Feature Name>

**Size:** L      **Type:** frontend      **Depends on:** [`YYYY-MM-DD-other-design.md`](./YYYY-MM-DD-other-design.md)

## Vision
<3–6 sentences, human language: what the user wants in this project's context,
what exists today, what exists after, why it matters>

## Now → Target

**Today**
| Step | What happens |
|------|--------------|
| ... | ... |

**After**
| Step | What happens |
|------|--------------|
| ... | ... |

**UI states that change:** ...

## Scope

**Areas involved**
- ...

**Reuse**
- ...

**Docs to read**
- `docs/knowledge/architecture/frontend.md` — state placement and data flow
- `docs/knowledge/design-language.md` — visual system this must match

**Skills to use**
- ...

**Guardrails**
- ...

**Affected domains:** ui, generation

## Decisions

| # | Decision | Why |
|---|----------|-----|
| 1 | ... | ... |

## Not now
- ...

## Global constraints
- ... (optional)

## Verification

**Tier:** Flow | Component | Check

- **Given** ..., **when** ..., **then** ...
````

There is no doc-impact section. Documentation updates are discovered from the real diff and performed by the plan's final work unit.

**Legacy specs** may use Problem / Goal / Non-Goals / Design / Testing Strategy, or the older Vision Contract (Deliverables / Acceptance criteria / Locked decisions / Blueprint). Migrate to this format when implementation touches them. Blueprint content that is file-level detail moves into the plan, not the new spec.

## Step 4: Review Pass

**One pass. One reviewer. No re-review.** Iterations that do not change the outcome are waste — the reviewer reports, you fix, you move on.

**Review subagent:** Check whether your runtime has a dedicated review subagent configured. **OpenCode:** use your `review` subagent (`Subagent (review):` in the prompt template). **Other runtimes:** look in platform config, agent manifests, or project docs for a subagent named `review`, `code-reviewer`, or similar with readonly/edit-deny permissions — use it when present. Fall back to `general-purpose` only when no review subagent exists. Do not substitute an inline self-review when a review subagent is available. When subagents are unavailable entirely, perform the same review scope yourself in readonly mode.

Dispatch using [spec-reviewer-prompt.md](spec-reviewer-prompt.md), filling in:
- `[SPEC_FILE_PATH]` — the saved spec
- `[HANDOFF_PATH]` — Design Handoff scratch file, or "session block"
- `[SPEC_SIZE]` — S / M / L from the header
- `[GLOBAL_CONSTRAINTS]` — the spec's Global constraints section, or "none"

**Scope:** placeholders, handoff fidelity, readability test, project alignment (does `Now → Target` describe the real current state, do the named components and reuse pointers exist), proportionality (detail and verification tier match the size), and scope discipline (no plan-level detail leaking in).

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

**Commit:** do not commit until the user approves, and only when the user requests a commit. Commit the spec plus the handoff scratch file when one exists.

**Terminal state:** invoke writing-plans — no other skill.
