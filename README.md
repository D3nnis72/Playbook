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

Small, already-scoped changes skip the full chain. A typo, a one-file fix, or a
known bug can go straight to implementation after a short design check when
needed.

## What's Inside

### Skills

| Skill | Role |
|-------|------|
| `using-playbook` | Entry point — find and invoke skills before acting |
| `brainstorming` | Explore intent and get design approval before building |
| `write-spec` | Author and validate the design spec after brainstorming |
| `writing-plans` | Turn a spec into a bite-sized implementation plan |
| `subagent-driven-development` | Execute the plan with work units and checkpoint reviews |
| `executing-plans` | Execute a plan in a separate session with review checkpoints |
| `writing-skills` | Create or improve skills with a TDD-style process |

### Process Chain

1. **Brainstorm** — understand the problem, propose approaches, get approval.
2. **Spec** — write the design handoff into a durable spec file.
3. **Plan** — break the work into tasks and work units with checkpoints.
4. **Execute** — implement work units, review at checkpoints, update docs.

```text
skill check → design → spec → plan → implement + review → done
```

## Philosophy

- Skills before action. Check first; do not rationalize past the check.
- User instructions win. Project files and direct requests override Playbook.
- Process skills first, then implementation skills.
- Right-size the process. Small scoped work does not need a full plan.
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
