---
name: to-spec
description: Write a product-level feature spec from settled grilling decisions, derive whether it fits one ticket or several, publish it, and ask whether to run an independent spec review. No second interview; use dev-execute for bug fixes.
---

# To Spec

Write the one binding artifact of the feature pipeline: a product-level spec that defines WHAT to build. It is the contract the user approves, the artifact `spec-review` checks, the input `to-tickets` slices, and the acceptance criteria `eval-{platform}` scores code against.

## Planning settings

Read [the shared planning settings contract](../dev-plan/references/planning-settings.md).
Reuse the settings and per-run notice ledger passed by `dev-plan`; if entered directly,
run that contract's resolver first. Use `user_name` for the addressee, `tracker` for
publication/approval policy, `label_vocabulary` for labels, and `spec_location` for
the durable destination (select its ticket-count branch after drafting when configured). Report each default notice once across the whole run.
Stop the affected step on a reported settings error; never substitute a shadowed value.
Review hosting and spec-review launch use their personal bindings from the planning
profile. A missing profile uses local HTML/chat approval and a fresh same-tool
subagent only on the user's yes. Configured handlers own their additional gates.

## Position in Workflow

```
grilling → to-spec → the user decides: spec-review or not → the user approves (resolved approval flow) → to-tickets → gen↔eval
```

- **Input:** settled grilling decisions, the settled direction and directions not taken. If decisions are missing, return to `grilling`.
- **Output:** one ticket's body, or a repository spec file plus epic when configured, derived after drafting (§Ticket count).
- **Review:** ask the user once whether to run a fresh `spec-review`; never launch by default.
- **Consumer:** one ticket goes to execution after chat approval; several go through the resolved review delivery and ticket breakdown.

## Keep the originating scope visible

When a spec comes from a broader epic, carry the repo-qualified epic link and one sentence explaining this spec's contribution into every review surface and final summary. State what remains outside this spec so a narrowed design stays connected to the original work.

## Ticket count

Draft first. From the completed acceptance criteria, decide whether one demoable ticket can deliver the outcome or several independently demoable slices are needed. State the call and consequence in one line:

- "Fits one ticket, so approval is in chat and the resolved spec location controls its durable destination. Say so if you want a different destination."
- "Needs several tickets, so the spec goes in an epic, the resolved spec location controls any repo file, and ticket breakdown follows approval. Say so if you want the ticket-body path."

The user may overrule the call. Take the other path without further questions. Do not trim scope to preserve the call.

| | One ticket | Several tickets |
|---|---|---|
| Durable spec | Ticket body; also a dated repo file when configured | Epic body; also a dated repo file when spec location is a directory |
| Review input, only on the user's yes | Scratch draft as `spec_path` | Scratch draft or configured spec file as `spec_path` |
| Approval | Chat, with open questions inline | Render open questions as decision cards; deliver via review hosting; default approval in chat |
| After approval | Execute the ticket | Use the installed ticket-breakdown skill under its invocation rules, or publish approved slices via the tracker |

For a ticket-body spec, use a session scratch draft for publishing and optional spec review, read the published body back, then discard the draft after updating the durable ticket. Its header records `Spec — YYYY-MM-DD, spec review: <verdict>` or `spec review: not run (the user)`; no numeric rating.

## Process

1. **Confirm the interview is finished.** Grilling ends when every branch of the design tree is visited. If a branch is unvisited, hand back to `grilling`. A decision grilling surfaced that the user has not yet made goes in the spec's `## Open questions`, one checkbox each. This skill asks nothing new: "no interview" means no second interview.
2. **Read the repo for vocabulary.** Read the repo's `CONTEXT.md` when present; otherwise use the repository’s documented terms. Use those terms, never a word on an `_Avoid_` list, and raise a missing term with the user instead of inventing one — specs are where names enter tickets and code. Respect ADRs in the area (see `grill-with-docs` output if it ran). Do not explore for architecture; the decisions are already made.
3. **Sketch the test architecture seams** (inherited from mattpocock's to-spec; see `codebase-design` for the definition of an architecture seam): prefer existing architecture seams, at the highest level that exercises the feature; propose new ones only where none exist. Confirm with the user in one message. These become Testing Decisions.
4. **Write the spec** with the template below. Each user story carries its own acceptance-criteria checklist. Fill Architecture Decisions only if grilling settled architecture; otherwise omit the section entirely.
5. **Self-check** (from brainstorming): placeholders or TBDs; sections that contradict each other; scope fits one feature that `to-tickets` can slice; derive the ticket count from the completed acceptance criteria (§Ticket count); any requirement readable two ways. Fix inline, once.
6. **Save.** Follow the resolved spec location: `issues` keeps the spec in the issue body for either ticket count; a directory receives a dated feature Markdown file. Keep a scratch draft for publication and optional review.
7. **Publish to the tracker.** Follow the resolved tracker binding and label vocabulary in the shared contract. The generic default creates or updates the target repo's GitHub issue using a body file and explicit `--repo`, after satisfying the target repo’s required label/workflow policy. A default vocabulary adds no restrictions; it does not waive repository requirements. No private labels or board attachment are imposed on other repos. Follow the shared contract’s preflight before creating an issue, and stop on an incompatible explicit vocabulary. Several tickets use an epic body containing the full spec; one ticket uses its own body. Read the published body back. Link a repository spec file when the configured destination produces one.
8. **Ask the user whether to run `spec-review`.** Ask once with recommendation and cost: "Run one independent spec review on this spec (~N minutes), or go straight to approval?" Never dispatch by default or on a revision without asking again. On yes, use the resolved `spec_review_launch` binding, with `spec_path` and `grilling_decisions_summary`: settled direction and approved decisions, one line each. Read a mapped skill's instructions or invoke the command with that request as JSON on stdin. Follow `spec-review`'s launch/context separation: the default is a fresh subagent of the running tool with a clean brief and the spec-review checklist, never the author's context. The reviewer executes the checklist without resolving or dispatching again. If no fresh-context capability exists, report the blocker. Wait for its full verdict before changing the candidate. Apply Fatal and Significant findings, log Minor findings, re-save and update the issue. On no, record `spec review: not run (the user, YYYY-MM-DD)` and continue.
9. **Render for approval.** Select the resolved `review_hosting` binding first. Several tickets with `local-html`: render a standalone local HTML page directly using the one-to-one mapping below; retain the file and take approval in chat. Use `visual-review` as the settings-aware renderer when installed; otherwise render directly with the same mapping and neutral styles. The renderer must honor `local-html` and chat approval. Several tickets with a skill/command binding: follow that handler's complete rendering, hosting, submission, and approval protocol; if it delegates to `visual-review`, obey that workflow's requirements without subsequently forcing chat approval. Send the ask defined in §Spec approval ask inline (the surface adds the full spec; it never replaces the ask). Render sections one-to-one, without re-derivation; unchecked open questions, at most five, become decision cards. Name every case that stops working (§Spec approval ask, item 5). One ticket: approval remains in chat, with the same ask and the review recap or `spec review: not run (the user)` after the ticket line.

10. **Record the user's decision** on the issue and in any spec file as a dated Approval line. Answer each open checkbox on the same line. Only explicit user approval with no unanswered questions counts as approved. Apply the resolved tracker's approval protocol; with the generic default, record approval in the issue text/comment and follow any repository-mandated approval labels or transitions, without inventing a lifecycle vocabulary. Hand several tickets to the installed ticket-breakdown skill according to its invocation rules, or draft slices through the resolved tracker if none is installed. Hand one approved ticket to execution.

## Spec approval ask

Use this ask when the user is planning a feature with you or asks to execute a ticket.
Filing alone does not request approval. A ticket without a spec first needs grilling
and this skill; preserve unresolved decisions as open questions. Publication and
approval labels follow the resolved tracker's protocol, never a built-in vocabulary.

**Content, in this order, inline in the message** so the user never opens a link to decide:

1. The ticket: repo, link, and title.
2. Its purpose: the problem and who hits it.
3. The behavior change, before → after.
4. The acceptance criteria, verbatim.
5. Anything that stops working today: each case the spec refuses, removes, or restricts, in plain terms; a summary of the new rule is not enough. When nothing stops working, say so.
6. Each open question as a self-contained decision ask: context, options with tradeoffs, recommendation.
7. Your recommendation, and what "approve" does: their answers and approval are recorded through the resolved tracker (step 10).

## Spec Template

```markdown
# [Feature Name]

## Problem Statement
[The problem the user faces, from the user's perspective. 1-2 paragraphs.]

## Solution
[What the user gets, from the user's perspective. 1-2 paragraphs. No architecture.
Record the settled direction in one line, naming the directions not taken.]

## User Stories
### S1 — As a [user], I want to [action] so that [outcome]
- [ ] [Concrete, testable criterion, verifiable from the user's perspective]
- [ ] ...
### S2 — ...

## What stops working
[Each existing case this feature refuses, removes, or restricts, in plain terms.
When no existing case is affected, state "Nothing stops working."]

## Data Model
[What data the feature needs: entities, fields, relationships, the grain of each
("one row is one ___"). Shape, not schema. No SQL, no file paths.]

## Architecture Decisions (optional — omit the section when grilling settled none)
[Decisions grilling made that constrain the how: modules touched, interfaces changed,
schema changes, API contracts, integration points. Prose. No file paths, no code.
Exception: a snippet from a prototype that encodes a decision more precisely than
prose (a state machine, a type shape) may be inlined and labeled as such.]

## Testing Decisions
[The architecture seams from step 3; what makes a good test here (external behavior only);
prior art for similar tests in the codebase.]

## Out of Scope
[Explicitly what this feature does NOT include.]

## Evaluator Rubric
[Which platform rubric applies: ios-rubric, mac-rubric, backend-rubric, design-rubric,
runtime-rubric. Any feature-specific criteria beyond it.]

## Open questions
[Decisions only the user can make that the spec needs before work starts, one checkbox each.
Omit the section when there are none.]
- [ ] [Question, open]
- [x] [Question, answered] — [Answer, written on the same line] (the user YYYY-MM-DD)

## Further Notes
[Minor spec-review findings, deferred ideas, the Approval line.]
```

## How visual-review renders it (one-to-one, no re-derivation)

The direct local renderer uses this same section mapping without invoking a hosted workflow.
Read the table top to bottom: it owns the spec page's content headings and order;
the review page kit supplies building blocks, never extra sections. Keep all
stories and criteria as readable text, not just a diagram, count, recap or footer
reminder. A diagram or caption limit must never truncate the criteria. Existing
specs may put `### What stops working` inside User Stories; render it as the
separate mapped section below, without treating it as another story. If the
source omits it, name any restrictions the approved spec states; only say
"Nothing stops working." when there are none. Do not infer new restrictions.

| Spec section | Surface element |
|---|---|
| Problem Statement + Solution | "Why this exists" before/after strip |
| User Stories | "User Stories": every story heading and its acceptance-criteria checklist verbatim, in source order |
| What stops working | "What stops working": every refused, removed, or restricted case verbatim; when there are none, state "Nothing stops working." |
| Data Model, Architecture Decisions | "The shape" diagram |
| Testing Decisions | "Testing Decisions" section |
| Out of Scope | "Out of Scope" section |
| Evaluator Rubric | "Evaluator Rubric" section |
| Ticket breakdown (to-tickets output, after approval) | Slice dependency graph |
| Open questions (unchecked checkboxes) | Decision cards, at most five |
| Further Notes | Footer |

## Rules

- **No second interview.** Synthesize; do not ask. Missing decisions go back to `grilling`.
- **NO file paths, NO code structure, NO implementation instructions.** The generator decides.
- **Acceptance criteria are user-verifiable.** "User sees subscriptions sorted by recent activity", not "repository returns rows ordered by updated_at".
- **A stated existing contract is traced, not skimmed.** Before the spec asserts what current code accepts or returns, follow every validator and helper the entry point calls; the lines around it are not the contract (2026-10-24, session ade7529e: a verdict format stated from the code beside `spec_report` missed `_validate_content`, which requires numeric scores; spec review flagged it Fatal). The same applies to an external tool's loading behavior: when a spec states which file a tool reads or where it stops reading, cite that tool's validated docs or source, never another tool's behavior (2026-10-25: a spec revision claimed Codex reads a directory-level instruction file above the repository by discovery; Codex stops at the repository root, and the independent review missed it).
- **Data Model describes shape, not schema.** Every new entity answers "one row is one ___" in a sentence.
- **Architecture Decisions is optional and prose-only.** It records what grilling decided; it never designs.
- **The spec is the contract between the user and the generator.** It defines done. For one ticket the ticket body is that contract; nothing in the conversation supersedes it.
- **Data-model practice:** when a feature feeds a scoring or ranking algorithm, user intent is persisted as a first-class record, never reconstructed from structural proxies.

## Hard Gate

Do NOT dispatch gen-{platform} or begin any implementation until:
1. The user has decided whether `spec-review` runs; if they said yes, a fresh reviewer has checked the spec and Fatal/Significant findings are applied
2. The user has explicitly approved through the resolved approval flow (chat with the default settings)
