# Execute Handoff Prompt

Use this template when a Lite or Full plan is saved and execution is **not** starting in this session.

**Purpose:** Give the user a prompt they can paste into a fresh agent (often a different model) that already has the plan path and the execute skill, and nothing else.

**Do not use this template to start coding in the planning session.** Fill it, paste it in a fenced code block, stop.

**Execute skill by tier:**

| Plan tier | `[EXECUTE_SKILL]` |
|-----------|-------------------|
| Lite | `playbook:executing-plans` |
| Full | `playbook:subagent-driven-development` |

Fill in `[PLAN_FILE_PATH]`, `[EXECUTE_SKILL]`, and `[REPO_ROOT]` (the project cwd). Do not paste planning-session history, canvas notes, or "which approach?" menus. The plan is the source of truth.

````markdown
Execute the implementation plan at `[PLAN_FILE_PATH]`.

Load [EXECUTE_SKILL]. Do not re-plan. Do not expand scope. Do not wait for confirmation. Follow the plan steps exactly. If the plan has a critical gap, stop and ask.

Repo: `[REPO_ROOT]`
````
