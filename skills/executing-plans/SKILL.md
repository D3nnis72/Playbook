---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**This is the low-drama execution path:** no per-task subagent reviewers, no review loops. Use when you want straight execution with verifications built into the plan steps — including many **small and medium** changes that never needed write-spec or subagent dispatch.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** For multi-work-unit plans with parallel dispatch, playbook:subagent-driven-development is usually faster — but it adds review gates at the plan's declared checkpoints. If subagents are available and you want maximum throughput with lighter ceremony, stay on executing-plans. If you want isolated implementer context per work unit, use subagent-driven-development instead.

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create todos for the plan items and proceed

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

For long plans (8+ tasks), pause once at the halfway point and give your human partner a one-paragraph progress summary — not a subagent review, just a checkpoint.

**The plan's final work unit is the documentation update** — never skip it. Run playbook:docdriven-audit in change-scoped mode over the diff you just produced to find which docs became false, then update them per playbook:docdriven. Work whose docs are stale is unfinished work.

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use playbook:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **playbook:using-git-worktrees** - Ensures isolated workspace (creates one or verifies existing)
- **playbook:writing-plans** - Creates the plan this skill executes
- **playbook:finishing-a-development-branch** - Complete development after all tasks
