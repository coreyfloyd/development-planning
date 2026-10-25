---
name: spec-review
description: Independently review a written product spec against a plain checklist, with evidence-backed Fatal, Significant and Minor findings. Run once only when the user requests it, in a fresh reviewer context.
---

# Spec Review

Review a spec written by `to-spec` once, only after the user says yes. The
author applies findings and owns approval. The reviewer is read-only, does not
interview the user, and does not advance ticket lifecycle.

## Launch and reviewer contexts

Read [the planning settings contract](../dev-plan/references/planning-settings.md).
The author reuses resolved settings and the per-run notice ledger; a direct launch
request resolves `--step spec_review_launch --step user_name` for the running
tool first. Use the planning target repo when available; outside Git, pass the
spec's working directory as `--repo` for personal-only profile/default resolution.
Report each returned default notice once. Print errors with file, entry and cause,
and stop the launch on invalid settings without using a shadowed value.

Only after the user's yes, use `spec_review_launch`:

- `fresh-subagent`: launch a new native subagent of the same tool (Claude Code or
  Codex), with a clean brief containing `spec_path`, `grilling_decisions_summary`
  (settled direction and approved decisions, one line each) and this checklist.
  Do not inherit the author's conversation, previous findings or revision notes.
  Wait for the full report. If native subagents are unavailable, report that
  blocker; never perform the review in the author's context.
- A skill binding: read its complete instructions and follow its launch and
  authorization protocol. A command binding receives the step, resolved repo facts,
  `spec_path` and `grilling_decisions_summary` as JSON on stdin under the shared
  command contract. Configured handlers own additional launch approvals and result
  capture. Require an independent fresh context and wait for the complete result.
  On failure, report the originating file and `spec_review_launch` entry and stop.

Unavailable profile bindings use the resolver's default and notice. Do not
substitute a native launch after a configured handler has failed.

**In the reviewer context**, the supplied review brief is already the authorized
launch: read the spec and execute the checklist below. Do not resolve settings or
launch another reviewer. Return the full report to the author. This separation
prevents recursive dispatch and self-review in both tools.

## Inputs

Read the clean `spec_path` and `grilling_decisions_summary` supplied in the review brief: the settled decisions, including the settled direction, one line each. Ignore prior findings or revision annotations. Interview decisions are approved: disagreements go in Decision disagreements with reasoning, separately from defects in the spec.

## Checklist

Use qualitative checklist judgments only; do not assign numeric ratings.

For each item, quote evidence from the spec and give either a finding or "clear, checked" with reasoning:

- **Acceptance-criteria testability:** every criterion has an observable pass/fail from the user's perspective, including negative and empty cases.
- **Story coverage:** every story has criteria, every criterion belongs to a story, and all Solution outcomes and boundary behaviors are covered.
- **No how-leakage:** product behavior belongs in stories and criteria; constraints on implementation belong only in recorded Architecture Decisions.
- **Internal consistency:** sections agree; the data model supports every story; out-of-scope does not exclude required behavior.
- **Ambiguity:** project terms match the glossary; quantities, ordering and boundaries are explicit, with no requirement readable two ways.
- **Completeness:** no placeholders or empty required sections; testing decisions identify real architecture seams and prior art; out-of-scope and a platform evaluator rubric are identified.
- **Scope:** one coherent feature with demoable vertical slices; unrelated outcomes and deferred phases stay outside it.
- **Data-model grain:** every entity answers "one row is one ___"; relationships and cardinality are clear; algorithm inputs preserve user intent as first-class records.
- **Robustness of the product decision:** examine fatal flaws, hidden risks, assumptions and fragility separately. Each dimension needs a finding or an explicit reason it is clear. Include existing flows affected and reachable states where stories meet.
- **Settled direction:** Solution records the settled direction and directions not taken, and the rest of the spec follows it.

Make a second pass and add at least one finding or newly confirmed clear with reasoning. Do not invent defects to fill the list.

## Findings and disposition

Rank defects **Fatal** (unimplementable or unverifiable requirement, contradiction, or unverified load-bearing assumption), **Significant** (material gap in behavior, coverage or precision), or **Minor** (nonblocking polish). Every finding cites evidence and proposes a fix in one sentence.

From Fatal and Significant findings, select at most five open items requiring the user: product choices, scope calls or contradictions only they can resolve. Each includes context, options with tradeoffs, and a recommendation. The author handles other findings. Separate disagreements with approved decisions from findings.

Return:

- Checklist evidence for every item.
- Ranked findings, with severity, quoted evidence and proposed fix.
- Dimension coverage for fatal flaws, hidden risks, assumptions and fragility.
- Decision disagreements, or none.
- Open items for the user, at most five.
- Disposition: `PASS` (no material blocker or follow-up), `CONDITIONAL PASS` (no material blocker; list follow-up items with severity, evidence, impact, title and description), `ITERATE` (the author can correct the spec), or `ESCALATE` (the user must resolve an open item).

One requested pass ends here. The author applies Fatal and Significant findings, logs Minor findings, and returns to approval. Any further pass requires another yes from the user.

## Configured transport

When a configured handler supplies a JSON envelope, follow it. A native subagent
returns the full report and disposition directly to the author. For an envelope, preserve the full report as nonempty `spec_report`, the disposition and round, and `follow_up_items` as a list. Return a nonempty `findings` list with `severity` (`Fatal`, `Significant`, `Minor`), `evidence` (quoted text), and `finding` or `summary` per row. When the checklist is entirely clear, include an evidence-backed confirmed-clear row marked `Minor` and explicitly identified as a confirmation rather than an open defect. This satisfies the findings transport without inventing an open issue or changing a PASS. The runtime records and validates the verdict; do not write your own verdict file.
