# Documentation Work Unit Template

Copy this into every plan as its **final task**. It is the plan's mandatory documentation work unit.

**Why it lives at the end and not in the spec:** canonical docs explain current truth. At spec time the code does not exist, so any list of docs to update is a guess that goes stale the moment a plan task changes. At the end of implementation the diff is real.

**Two skills, two jobs.** playbook:docdriven-audit finds what became false (change-scoped mode). playbook:docdriven governs how docs get written. This work unit calls both — it does not carry its own discovery procedure.

Fill in `<feature>` and the domain IDs from the spec's Scope section.

````markdown
### Task N: Documentation update

**Skills:**
- playbook:docdriven-audit — change-scoped mode, to discover what became false
- playbook:docdriven — read-before-change, one canonical explanation per concept,
  link instead of copying, never copy type or schema definitions into docs

**Domains:** <domain ids from the spec's Scope section, or "derive from the diff">

**Files:** discovered in Step 2 — do not assume them.

- [ ] **Step 1: Establish the diff range**

```bash
git log --oneline <PLAN_BASE_COMMIT>..HEAD
```

Confirm `<PLAN_BASE_COMMIT>` is the commit the plan started from, so nothing
implemented in this plan falls outside the range.

- [ ] **Step 2: Run the change-scoped doc audit**

Use playbook:docdriven-audit in **change-scoped mode** over
`<PLAN_BASE_COMMIT>..HEAD`. It returns the changed subjects, the docs that became
false with an action each, route shard changes needed, duplication findings, and
any divergence from the spec.

Its report is your file list for the rest of this task. Do not substitute a list
from the spec or the plan.

- [ ] **Step 3: Read every doc you are about to change**

Do not edit a doc you have not read in full. Human docs and agent-routing docs
have different jobs — match the one you are in.

- [ ] **Step 4: Apply the audit findings**

Per playbook:docdriven, and per the action the audit assigned each row:
**Update** the docs that became false, **Verify** the ones it flagged, **Promote**
tmp content that is now durable truth, and resolve **duplication** findings by
linking to the owning doc instead of restating it.

Where implementation diverged from the spec, document what was **built**.

- [ ] **Step 5: Update route shards**

Apply the route shard changes the audit listed: `readFirst`, `codeAreas`, and
`updateDocs` where ownership, validation, or structure changed. Add a route when
new structure has no owner. If this change created a new convention, the
architecture doc changes in this same task.

- [ ] **Step 6: Record gaps**

Append the audit's **Add gap** rows to `docs/agent/gaps.md`, including any
spec divergence.

- [ ] **Step 7: Report completion evidence**

Per playbook:docdriven: docs read, routes used, code changed, docs updated,
validation run, gaps recorded.

- [ ] **Step 8: Commit**

```bash
git add docs/
git commit -m "docs: update <feature> documentation"
```
````

**Review:** this work unit always carries a review checkpoint. The reviewer checks that every audit finding was resolved or explicitly deferred with a gap, that no doc restates content another doc owns, and that route shards match reality — not that the docs match a list written before implementation.
