# Planning settings contract

`dev-plan` and `to-spec` share this contract in Claude Code and Codex. A **planning
profile** holds personal entries and optional repo-fact defaults. **Repository
planning settings** hold repo facts only. Neither file is required.

## Files and entries

- Planning profile: `~/.config/development-planning/profile.json`, overridden by
  `PLANNING_PROFILE` (a file path). This location is outside the package and repo.
- Repository planning settings: `.planning.json` at the target git worktree root.
  Never read `docs/agents/` as settings. A linked worktree uses its own tracked file.
  Before reading a present file, verify that exact root path is tracked in the
  target worktree's Git index. Untracked or ignored files and Git lookup failures
  are errors that stop resolution without fallback. Read the working file, so
  edits to a tracked file are used; the resolver never stages settings itself.
  This tracking requirement does not apply to the per-user planning profile.
- Both files are JSON objects with the flat entries below. Omit an entry to inherit
  it; `null` is invalid. Unknown or duplicate entries and malformed/unreadable files
  are errors. There is no implicit configuration creation or migration.

| Entry | Meaning | Generic default |
|---|---|---|
| `tracker` | Publishes specs and tickets; repo fact | `{"builtin":"github-issues"}`; owner/repo from `origin` |
| `label_vocabulary` | An explicit list of allowed label names, or `{"builtin":"repository-policy"}` to use the target repo's current policy; repo fact | `[]` (no planning-imposed vocabulary; respect the target repo’s required labels) |
| `spec_location` | Durable spec destination; repo fact | `"issues"` (issue body); configurable as a repo-relative directory or ticket-count destinations |
| `user_name` | How to address the user; personal | `"the user"` |
| `review_hosting` | Performs review-page delivery; personal | `{"builtin":"local-html"}` |
| `spec_review_launch` | Performs an optional independent spec review; personal | `{"builtin":"fresh-subagent"}` |

A step binding (`tracker`, `review_hosting`, `spec_review_launch`) is exactly one of
`{"skill":"installed-skill-name"}`, `{"command":["executable","argument"]}`, or
its listed `builtin`. Commands are argv arrays, never shell text; resolve relative
executables from the target repo and expand `~` in the executable before invoking.
Commands perform the named step, taking the step's request as JSON on stdin
(`step`, resolved repo facts, and the step inputs: for publication, `title`,
`body_file`, and any existing `issue_url`; for review, `spec_path` and
`grilling_decisions_summary`; for hosting, the local HTML path). Run from the target
repo with the same argv used for availability checks. A failing command or a
rejected repo value stops that step: report its settings file path and entry,
including the returned error; never retry through a shadowed binding. Their
stdout must describe the result (including published URLs or review artifacts).
Do not execute a binding just to test availability. Read a mapped skill's complete
instructions before using it. Bindings may provide additional policy and approvals.

Example planning profile (illustrative, no private setup):

```json
{
  "user_name": "Taylor",
  "tracker": {"skill": "team-tracker"},
  "label_vocabulary": ["feature", "bug"],
  "spec_location": "docs/specs",
  "review_hosting": {"command": ["team-review-host"]}
}
```

Example repository planning settings overriding only one fact:

```json
{"spec_location":"docs/proposals"}
```

## Resolve before acting

Run `python3 <installed-dev-plan-dir>/scripts/planning_settings.py --repo <target>
--tool claude|codex` once at planning entry. Pass `--available-skill <name>` for
each relevant installed skill **from the running tool's current catalog**; a skill
installed in the other tool is not available. Do not infer availability from the
other tool's filesystem. The same script ships inside the shared skill directory.
`to-spec` entered directly performs the same resolution. When entered from
`dev-plan`, reuse its result and notice ledger rather than resolve/announce again.

The JSON output has `values`, `sources`, `notices`, and `errors`, keyed by entry
except `notices` (a list). Resolve repo facts independently: repo entry, then
planning profile entry, then generic default. Personal entries come only from the
planning profile. A present invalid override blocks its step, even if a lower
precedence value works. A well-formed planning profile binding naming an unavailable
skill or command uses the generic default, not any alternate mapping. An unavailable
repo binding is an error. A valid repo fact can shadow an invalid profile fact.

Say each returned notice once per planning run, naming the step and its default.
Keep that notice ledger in the conversation and pass it with the resolved settings
to downstream skills. Print errors verbatim (file, entry, cause); stop affected
steps and ask for correction. Do not publish while any tracker, label vocabulary,
or spec location error is unresolved. Other interview work may continue. Exit 2
means at least one blocked step; do not treat it as successful resolution. `--step`
can select specific entries without testing or stopping unrelated steps.
Repository-file parse or tracking errors block repo facts, not independently
resolved personal entries. A syntactically valid repo file containing a personal
entry still reports that prohibited entry and stops its affected step.

For a standalone review outside Git, explicitly select only personal entries:
`--repo <review-working-directory> --step review_hosting --step user_name` (or
`--step spec_review_launch --step user_name` for a requested spec review). This
reads the planning profile and defaults, never a `.planning.json` in that non-repo
directory. Profile errors and unavailable-handler notices retain their usual
behavior; relative command executables resolve from that working directory.
Requesting repo facts, including the default full planning resolution, still
requires a Git repository.

## Publishing through the generic tracker

For `github-issues`, use the resolved `repository`, never a folder-name map or a
hardcoded repo. Before a create or edit:

1. Read the target repo's applicable agent/contribution instructions and issue
   policy, including any mandatory label workflow or active gate's policy source.
   Follow a repository-mandated workflow when one exists; the generic publication
   recipe does not bypass it. Do not switch the resolved tracker or import another
   user's workflow merely because that workflow is installed.
2. Check `gh auth status` and read the target's issues and labels. Label existence
   alone does not establish which labels are required. Derive required labels and
   approval transitions from the target's authoritative policy, not from a built-in
   lifecycle vocabulary. If credentials, policy access, or a mandatory workflow are
   unavailable, report the blocker and retain the draft before any mutation.
3. When the vocabulary source is `default`, `[]` means planning adds no label
   restrictions; include the repo's required labels. An explicit
   `{"builtin":"repository-policy"}` likewise delegates label selection to the
   target repo's current policy (including a mandated or mapped tracker's policy),
   with no fallback notice. Both choices still require the policy and available
   labels to be read before publication; neither supplies labels itself or waives
   policy. With no repository label requirements, create without labels. When a
   planning profile or repository planning settings explicitly supplies a list,
   validate it against the target policy and available labels. An explicit `[]`
   allows no labels. If the list cannot satisfy required labels, report that file
   and its `label_vocabulary` entry and stop publication; never silently extend
   it, use a shadowed value, or omit required labels.
4. Use explicit `--repo` with every `gh issue` command. Read and update an existing
   issue when supplied; otherwise create with `gh issue create --repo <owner/repo>
   --title <title> --body-file <draft>` plus the policy-compliant label arguments,
   then read it back with `gh issue view`. Do not impose a private label family or
   project board on repos whose policy does not require it. Preserve the repo's
   approval protocol; the generic default records approval in issue text/comments
   and invents no lifecycle transitions.

A gate rejection is an explicit blocker: read its reason, correct the command
under the target's policy, and do not evade the gate through another tool or
transport. Resolve policy before issuing a create; a speculative failing create
is not a policy-discovery mechanism.

`spec_location` may also be an object with exactly `one_ticket` and
`several_tickets`, each holding `"issues"` or a repo-relative directory. After the
ticket-count call, select that destination. This preserves an existing policy
where a single ticket lives only in its issue and an epic also has a repo file.
Both destinations must be valid before the publication step proceeds.

With `spec_location: "issues"`, the full spec lives in the issue body regardless
of ticket count; for several tickets that issue is the epic. With a directory,
write `YYYY-MM-DD-<feature>.md` there and publish the same spec text to the issue,
linking the file. Do not let ticket count override a configured spec destination.
Use a scratch draft for publication/review until a durable destination exists.

For a mapped tracker, follow its publication, label, and approval protocol using
these resolved repo facts; its own documented workflow may supply additional
repository policy. Apply it only where the target repo or resolved binding requires it; do not make it a generic default.

## Adjacent steps

Review hosting and spec-review launch use their resolved bindings; their consumers
own delivery and fresh-context launch details. Select the resolved hosting binding
before choosing a renderer. For `local-html`, render a standalone local HTML page
directly, using the spec's one-to-one section mapping and approval in chat. Do not
invoke a hosted-review workflow just because it is installed: its mandatory server
or submission protocol may conflict with this builtin. The settings-aware
`visual-review` renderer supports this builtin and may render the local page while
reusing these resolved settings and notice ledger. For a skill/command binding,
follow that handler's complete rendering, hosting, and approval protocol; do not
subsequently force local delivery or chat approval. This keeps the generic local
renderer separate from configured hosted workflows. The builtins mean local HTML
with approval in chat, and (only after the user's yes) a fresh subagent of the running
tool. Never perform a spec review in the author's context. Missing native subagent
capability is an explicit blocker, never a self-review. Configured handlers own
any extra hosting/dispatch approval steps. Carry `spec_path` and
`grilling_decisions_summary` (settled direction and decisions) into a review request.
