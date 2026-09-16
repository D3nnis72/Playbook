# Documentation Work Unit Template

Copy this into every plan as its **final task**. It is the plan's mandatory documentation work unit.

**Why it lives at the end and not in the spec:** canonical docs explain current truth. At spec time the code does not exist, so any list of docs to update is a guess that goes stale the moment a plan task changes. At the end of implementation the diff is real.

**Three skills, three jobs.** playbook:docdriven-audit finds what became false
(change-scoped mode) and which in-scope docs need splitting (maintainability
pass). playbook:docdriven governs how docs get written and split. This work unit
calls both — it does not carry its own discovery procedure.

Fill in `<feature>` and the domain IDs from the spec's Scope section.

````markdown
### Task N: Documentation update

**Skills:**
- playbook:docdriven-audit — change-scoped mode + maintainability pass
- playbook:docdriven — read-before-change, split oversized knowledge docs,
  one canonical explanation per concept, link instead of copying, never copy type
  or schema definitions into docs

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

- [ ] **Step 2b: Run the maintainability pass**

Run `docs:audit` (or `audit-docdriven.mjs --format json`) on docs in scope:
every doc from Step 2, plus every knowledge doc touched in the plan's diff range.

For each doc with `suggestedAction: split-required` in scope, read
`_shared/doc-splitting.md` and write a split plan to
`docs/tmp/splits/YYYY-MM-DD-<id>-split-plan.md` before editing content. For
`split-review-required` (1,500–3,000 words), review whether the doc is still
one cohesive concern; split only if it is not, or document a kept exception with
narrowed routing.

- [ ] **Step 3: Read every doc you are about to change**

Do not edit a doc you have not read in full. Human docs and agent-routing docs
have different jobs — match the one you are in. Read any split plans from Step 2b.

- [ ] **Step 4a: Execute required splits**

For each **Split** row from the maintainability pass: execute the split plan
(overview + leaves, `includes`/`extends`, index and route updates), then delete
the split plan from `docs/tmp/splits/`. Do this before other doc updates.

- [ ] **Step 4b: Apply the change-scoped audit findings**

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

- [ ] **Step 8: Clean up playbook leftovers**

`docs/playbook/**` is temporary. Knowledge docs own shipped truth. Specs and
canvases may only hold remaining work — strip shipped content, do not
annotate it as history. After durable knowledge is updated via docdriven:
delete this plan; delete the spec if this slice is complete and no open spec
still Depends on that file, otherwise strip shipped units; delete the canvas
if every slice on it has shipped, otherwise remove the shipped slice. Ask
only when Depends-on or unfinished slices make ownership unclear.

- [ ] **Step 9: Commit**

```bash
git add docs/
git commit -m "docs: update <feature> documentation"
```
````

**Review:** this work unit always carries a review checkpoint. The reviewer checks that every audit finding was resolved or explicitly deferred with a gap, that required splits were executed and split plans deleted, that no doc restates content another doc owns, that route shards match reality, and that playbook leftovers were deleted, stripped to remaining work, or an explicit unclear-dependency reason was recorded — not that the docs match a list written before implementation.
