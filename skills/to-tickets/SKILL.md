---
name: to-tickets
description: Break a plan, spec, or the current conversation into the ticket breakdown, a set of tracer-bullet tickets each declaring its blocking edges, published to the configured tracker — edges as text in one file per ticket locally, or native blocking links on a real tracker.
disable-model-invocation: true
---

# To Tickets

Break a plan, spec, or conversation into the **ticket breakdown**: a set of tracer-bullet vertical slices, each declaring the tickets that **block** it. Approval of the ticket breakdown authorizes publication; it does not launch implementation.

## Planning settings (Claude Code and Codex)

Before drafting, locate `dev-plan` in the running tool's installed skill catalog and read its `references/planning-settings.md` in full. That contract owns the planning profile, repository planning settings, per-fact precedence, validation, command requests, and generic publication policy. Use the same resolver in both tools; do not read settings from the other tool's installation or from `docs/agents/`.

When entered from a planning run, reuse its resolved settings and notice ledger. When entered directly, run:

```text
python3 <installed-dev-plan-dir>/scripts/planning_settings.py --repo <target-repo> --tool <claude|codex> --step tracker --step label_vocabulary --step spec_location --step user_name
```

Supply `--available-skill <name>` for each relevant skill available in the running tool's current catalog. The resolver reads `.planning.json` at the target worktree root (only when tracked there), then the planning profile at `PLANNING_PROFILE` or `~/.config/development-planning/profile.json`, then defaults, independently for each repo fact. User identity comes only from the planning profile. If the resolver or contract is missing, report the missing dependency and retain the draft; do not improvise settings resolution.

Say each returned fallback notice once per planning run and retain the ledger for downstream steps. Default `tracker` is `github-issues`, with its `repository` discovered from the target's `origin` git remote. Default `label_vocabulary` is empty (no planning-imposed labels), `spec_location` is `issues`, and `user_name` is “the user”. Use the resolved name when addressing the user. Do not resolve or announce unrelated review steps here.

Print returned errors verbatim, including file, entry, and cause. An exit code of 2 blocks affected steps. Do not publish with unresolved tracker, label vocabulary, or spec location errors. Invalid settings never fall through to a shadowed value. An unavailable profile skill or command uses the resolver's generic fallback and notice; an unavailable repository binding stops publication.

Load the resolved tracker skill's complete instructions before drafting and publishing. It owns its label vocabulary, lifecycle transitions, milestones, parent relationships, project-board placement, and any approval requirements. A command binding performs publication with the resolved repo facts under the shared contract. Do not select another tracker merely because it is installed.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests) — vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges** — the other tickets that must complete before it can start. A ticket with no blockers can start immediately. Distinguish implementation order from closure dependencies. If shared evaluation or epic closure keeps an earlier slice open, record integrate-and-verify ordering in the ticket body; use native blockers only when closure can precede dependent work.

**Place every ticket under the resolved tracker's policy.** Before drafting, read the target repo's applicable agent/contribution instructions and issue policy, and inspect existing issues, labels, milestones, and epics. Respect required labels and approval transitions. Use the resolved `label_vocabulary` under the contract's validation rules; an explicit vocabulary that cannot satisfy repo policy blocks publication, naming its source file and entry. With the default empty vocabulary and no repo label requirements, publish without labels.

- Propose milestone and epic membership only when that milestone or epic needs the ticket to ship; related work stays out. Never create a milestone without approval.
- A breakdown of two or more tickets has a parent epic with native sub-issues where supported. Reuse an appropriate existing epic or include a new epic in the approved breakdown. Do not close or rescope an existing parent.
- GitHub does not inherit milestones. Carry the approved epic milestone to same-repository children. Ask which target-repo milestone applies for a cross-repository child; never guess from its title.
- Use area labels and evaluation groupings when the resolved handler or target repo requires them; do not invent a private label family or board for the generic default.

**Group tickets into the fewest evaluation seams that are each one demoable boundary.** Every evaluation seam costs an evaluator launch, so `self` is for a ticket with no natural seam-mate, not the starting assumption: tickets that are only meaningful when evaluated together share one evaluation seam. Keep a ticket in another repository on an evaluation seam of its own, because each evaluation seam is evaluated on one integrated diff.

**Acceptance criteria describe the deliverable, never a review step.** Do not write "the user reviews X before merge" or any "operator approves the diff" line as a criterion: the evaluator validates the output against the criteria, and decisions the user made during the spec are already settled. If a slice needs a decision only the user can make (a design choice the spec left open), write it as an open question under the ticket's `## Open questions`, one checkbox each: `- [ ]` is open, and `- [x]` is answered, with the answer written on the same line. Follow the resolved tracker's readiness and approval policy; do not treat an unresolved design question as authorization to implement.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket — green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work
- **Milestone and epic**: the milestone and the epic the ticket is required for, or "none" with the reason
- **Labels**: the labels required by the resolved handler and target repo, including area when required
- **Evaluation seam**: which evaluation seam the ticket belongs to (a demoable boundary evaluated as one unit: one admission path, one switch, one end-to-end story), naming its seam-mates; or `self` when the ticket is its own evaluation seam. Write the evaluation seam into the ticket body when the target workflow uses it so an executor can tell which tickets must be verified together.

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct — does each ticket only depend on tickets that genuinely block it?
- Should any tickets be merged or split further?

Draft list positions identify slices only within this review; they are not GitHub issue numbers. Keep them out of published GitHub dependency declarations.

Iterate until the user approves the ticket breakdown.

### 5. Publish the tickets to the configured tracker

Publish only the approved breakdown through `values.tracker`:

- **`github-issues` builtin:** follow the generic tracker recipe in the shared contract. Check authentication and repository policy before any mutation. Use the resolved `repository` explicitly with every `gh issue` command. Create each slice with `gh issue create --repo <owner/repo> --title <title> --body-file <draft>` and policy-compliant label and milestone arguments, or edit a supplied existing issue after reading it. Read each issue back. No fixed board or label set is added by this skill.
- **Skill binding:** use that handler's sanctioned publication commands, full required label set, milestone rules, native parent/dependency commands, and project board. Follow its additional policy and approval requirements in full; do not also run the builtin publication path.
- **Command binding:** invoke the exact resolved argv from the target repo, expanding the executable as specified in the contract, never as shell text. For each ticket send JSON on stdin with `step: "tracker"`, resolved repo facts (`tracker`, `label_vocabulary`, `spec_location`), `title`, `body_file`, and `issue_url` when updating. Include approved parent, blockers, milestone, and evaluation seam as ticket inputs. Require returned published identities/URLs in stdout and verify the result before publishing dependents. A failing command stops the step with its settings file, `tracker` entry, and returned error; do not retry through a lower-precedence handler.

If the selected handler supports local files, write one file per ticket under its chosen directory, in dependency order, using the local template below. Local files are an explicitly mapped tracker option, never the no-setup default. Keep local filenames/numbers distinct from real tracker identities.

When an existing ticket covers a slice, rescope it instead of creating a duplicate, preserving its original ask at the bottom. Read its parent relationship first. If it already has another parent, retain that parent and record the proposed parent's dependency on the reused ticket, with native blocking links. Report any relationship error; do not silently replace the existing parent.

**GitHub publication checks (both tools, for builtin and mapped handlers):**

1. Create blockers before their dependents. Capture each created issue's repository, number, and URL from the create response and map the draft slice to that returned identity. For reused issues, read their actual identities from the tracker first. Never predict the next issue number: concurrent filing can assign it to unrelated work. If a required identity is unavailable or creation fails, stop publishing affected dependents rather than guessing.
2. Before creating or rescoping a dependent, replace its draft dependency references with the captured blocker identities. Every prose GitHub dependency declaration must be a plain line in the dependent's body in the exact form `Blocked by: owner/repo#N`, one blocker per line, with the real owner, repository, and positive issue number substituted. Do not publish draft list positions, bare `#N`, local filenames, literal `[ref]`, or other unresolved placeholders as dependency declarations. If using native links alone, omit the prose dependency section rather than publishing a temporary declaration. For no blockers, omit it or write "None — can start immediately".
3. Publish the body, then use the captured identities for native parent and blocking links through the mapped handler's native relationship commands, or directly through GitHub's issue dependency and sub-issue APIs for the builtin. Native blocking links are required on GitHub even when the body declares them. Read back the published body and the native blocking and parent relationships; compare the actual endpoints to the captured identities and approved edges. A successful write response alone is not verification. Report any mismatch or failed readback as incomplete and stop publishing affected dependents.
4. Set each ticket's milestone as the approved breakdown names it, including the epic's milestone on every sub-issue in the same repository. Read back the milestone, all required labels, and any handler-required project-board membership, and compare them to the approved breakdown. Missing required placement is an incomplete publication.

The same checks apply to new and reused tickets in both tools. Local-file tracker numbering stays local; moving those tickets to GitHub requires this identity mapping and publication sequence.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN> — <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective — not a layer-by-layer implementation list.

**Blocked by (local files):** the local filenames/numbers and titles of the tickets that block this one, or "None — can start immediately". These are local-file tracker references only.

**Ticket status:** use the mapped tracker's readiness policy

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

**Open questions:** (omit when there are none)

- [ ] A decision only the user can make, still open
- [x] A decision the user made — the answer, on the same line

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective — not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Open questions

Decisions only the user can make that this ticket needs before work starts, one checkbox each. Omit this section when there are none.

- [ ] An open question
- [x] An answered question — the answer, on the same line

## Blocked by

For GitHub, insert one plain `Blocked by:` declaration line per blocker using its captured, fully qualified real identity as specified above. Omit this section when relying only on verified native links; for no blockers, write "None — can start immediately". This guidance is template text: replace it before publishing, never copy it into an issue body. For other trackers, use their real blocker identifiers.

</issue-template>

In either form, avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.
