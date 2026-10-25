---
name: dev-plan
description: Feature planning pipeline — strawman → grilling → to-spec → optional spec review → approval → ticket breakdown when needed. Use for new features; dev-execute owns approved-ticket execution and bug fixes.
---

# Dev Plan — Feature Planning Pipeline

Produce one approved product spec and the tickets to execute. `dev-execute` owns execution.

## Planning settings

Before the interview, read [the shared planning settings contract](references/planning-settings.md)
and run its resolver with the target repo and the running tool's available skills.
Reuse the resolved settings and notice ledger throughout this run, including `to-spec`.
Address the user using `user_name`; without a planning profile, say "the user".
Repository facts resolve independently; invalid overrides stop the affected step.
The generic tracker publishes to GitHub issues from the target repo's git remote.
Review hosting and spec-review launch follow their personal settings bindings.

## Pipeline

1. **Strawman.** Invoke `strawman` on every run, including when decisions already exist. Offer directions from existing context and settle the overall shape. If only one direction is sensible or the conversation settled it, use the two-line shortcut and proceed to grilling.
2. **Grilling.** Invoke `grilling` starting from that settled direction. Work the decision frontier until it is empty. Do not write a document here. Use `grill-with-docs` when ADRs and glossary entries need updating inline, preserving the grilling question protocol.
3. **Spec.** Invoke `to-spec` with the settled direction, directions not taken, and resolved decisions. It drafts without a second interview, then derives whether the acceptance criteria fit one ticket or several and states the consequence in one line. The user can overrule that call; take the other path without more questions.
4. **Optional spec review and approval.** `to-spec` asks once whether the user wants a fresh `spec-review`. Only their yes permits a fresh review through the resolved spec-review launch binding. Apply Fatal and Significant findings; log Minor findings. One ticket gets approval in chat; its spec destination follows the resolved settings; several get an epic; the resolved spec location determines whether a repo file is also written. Review delivery follows the resolved review-hosting binding. Use `to-spec` §Spec approval ask on either surface. Record their answers; record approval only with explicit approval and no unchecked open questions, using the resolved tracker’s protocol.
5. **Ticket breakdown when needed.** For several tickets, use the installed ticket-breakdown skill on the approved spec according to its invocation rules. If none is installed, draft independently demoable slices and publish them through the resolved tracker after approval. It owns vertical slices, acceptance criteria and native blocking edges. For one ticket, the ticket body is already the binding spec; skip breakdown.
6. **Execution handoff.** Choose AFK or HITL with the user and hand off to `dev-execute`. Open questions go back to the user before any execution slate.

## Context before the interview

Optional competitor or UX research can precede planning when requested; `strawman` itself never researches the web. For UI features in a repo with `screen-design`, offer it before grilling.

For pricing, onboarding, or acquisition, use relevant domain material the user supplies during grilling.

## Tracker placement

Before publishing a ticket or epic, list the repository's open milestones and epics. New functionality joins the milestone it is required to ship; if none fits, propose a milestone with an exit criterion. A ticket required to complete an existing epic becomes its sub-issue and inherits its milestone. Membership means required to ship. Record ordering as native blockers. Respect the target repo’s required label/workflow policy as well as the resolved vocabulary. The default vocabulary adds no restrictions; an explicit vocabulary that cannot satisfy repo policy stops publication with its settings file and entry named. `/to-tickets` applies this to every slice.

## Harness architecture seams

An architecture seam serving both Claude Code and Codex harness payloads needs a pair of tickets, each built and tested by an agent native to that harness. Use any harness labels required by the resolved tracker. Pure logic without harness payloads needs no pairing. See `codebase-design` for architecture seam vocabulary.

## Hard rules

- No generator dispatch before an approved spec: strawman → grilling → to-spec → the user's optional spec-review decision → explicit approval.
- Spec review is never automatic and never runs in the author's context. A revision needs a new yes before another pass.
- The spec is the binding contract. Platform evaluators judge implementation against its acceptance criteria.
- Missing decisions go back to grilling. The approval renderer maps the spec one-to-one; it does not re-derive it. The local-HTML default renders directly; configured handlers own any hosted-review requirements.

## Pipeline skill protocol

State expected inputs and assumptions. Announce each phase as `[Step N — skill]`, including the ticket-count call after drafting. Stop at the user's direction choice, spec-review decision, spec approval and execution-mode choice.

Track phases with the running tool’s task tools when available. Mark breakdown skipped when the spec fits one ticket.

**Data-model practice:** when a feature feeds a ranking or scoring algorithm, persist user intent as a first-class record rather than reconstructing it from structure.
