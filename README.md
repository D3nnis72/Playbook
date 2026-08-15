# Playbook

Playbook is a set of agent skills for disciplined software work: find the right
skill, design before you build, write a spec, plan the work, then execute with
review gates.

It is process infrastructure for coding agents. Skills tell the agent *how* to
approach a task before it touches code. The goal is fewer guesses, fewer
parallel architectures, and changes that fit the system you already have.

## Quickstart

Install all skills:

```bash
npx skills add D3nnis72/Playbook
```

Install one skill:

```bash
npx skills add D3nnis72/Playbook --skill using-playbook
```

Then tell your coding agent to follow Playbook. Start with `using-playbook` so
it learns to invoke the right skill before acting.

If you do not know how to start, give this README to your coding agent and tell
it to install Playbook and use the skills for the next feature.

## How It Works

`using-playbook` is the entry skill. Before any response or action, the agent
checks whether a skill applies — even a 1% chance means it should load the
skill and follow it.

Substantive features follow a process chain:

```text
brainstorming → write-spec → writing-plans → subagent-driven-development
                                            (or executing-plans)
```

**The chain is a maximum, not a minimum.** Every phase sizes its own output and
can exit early: `write-spec` sizes the spec S / M / L, and `writing-plans` sizes
the plan Direct (no plan, just implement), Lite (one page, one work unit), or
Full (work units, waves, checkpoint reviews). A typo, a one-file fix, or a known
bug goes straight to implementation after a short design check.

## What's Inside

### Skills

| Skill | Role |
|-------|------|
| `using-playbook` | Entry point — find and invoke skills before acting |
| `brainstorming` | Explore intent on a living canvas; design approval before building |
| `write-spec` | Author a temporary design spec after brainstorming |
| `writing-plans` | Size the plan, then turn a spec into bite-sized tasks |
| `subagent-driven-development` | Execute a Full plan with work units and checkpoint reviews |
| `executing-plans` | Execute a Lite plan, or a Full plan in a separate session |
| `writing-skills` | Create or improve skills with a TDD-style process |

### Process Chain

1. **Brainstorm** — understand the problem, propose approaches, get approval.
2. **Spec** — size the work, then write a temporary design spec distilled from
   the brainstorming canvas (not durable product docs).
3. **Plan** — size the plan, then break the work into tasks, and into work units
   with checkpoints when the tier calls for them.
4. **Execute** — implement, review where the plan said to, update canonical
   knowledge via docdriven, then **ask** whether leftover playbook files
   (specs, plans, canvases) can be deleted.

```text
skill check → design → spec → plan → implement + review → done
```

## Philosophy

- Skills before action. Check first; do not rationalize past the check.
- User instructions win. Project files and direct requests override Playbook.
- Process skills first, then implementation skills.
- Right-size the process. Every phase names its size and can exit early.
- Ceremony is a cost. Padding small work up to a bigger shape is a failure, not caution.
- Plans carry decisions, not transcriptions. A plan that pre-writes the code is the change written twice.
- Specs, plans, and brainstorming canvases under `docs/playbook/` are temporary working files. Durable product truth lives in canonical knowledge docs after docdriven; delete leftovers when documentation is clearly done, and ask only when ownership is unclear.
- Specs and plans earn their keep on multi-step work others will build on.
- Rigid skills (discipline) are followed exactly. Flexible skills adapt.

## Standalone Installs

`npx skills` installs one skill directory at a time. Each skill in this repo is
self-contained: references and scripts resolve inside that skill folder.

CI runs:

```bash
node scripts/verify-install.mjs
```

That copies each skill out of the repo on its own and fails when frontmatter is
invalid or a same-skill relative reference no longer resolves.

## Updating

```bash
npx skills update
```

Or re-add:

```bash
npx skills add D3nnis72/Playbook -y
```
