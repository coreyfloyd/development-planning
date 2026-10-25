---
name: visual-review
description: Render a spec, plan, design, or decision as a diagram-first review page for the user to judge, using resolved planning settings for delivery.
---

# Visual Review

Render the artifact for understanding and decisions. Text remains the source of
truth. Use this for spec/design approval, explanations with several moving parts,
and decisions with enumerable options. Use the review page kit below for every page.

## Resolve delivery first

Read [the planning settings contract](../dev-plan/references/planning-settings.md).
Reuse the resolved settings and notice ledger from the planning run. When entered
directly, run its resolver with `--step review_hosting --step user_name`, the
running tool's catalog and `--tool claude|codex`. Use the planning target repo when
one is available; for a standalone design or decision outside Git, pass the review
working directory as `--repo` instead. Personal-only resolution still reads the
planning profile and defaults without requiring a repository or reading local
repository settings there. Address the user through `user_name`.
Report each default notice once per run. Print settings errors with their file,
entry and cause, and stop the affected step; never use a shadowed value.

If the selected hosting handler calls this skill as a rendering substep, reuse
its settings, render only, and return the local file to that handler. Do not
resolve or dispatch hosting again; the caller owns delivery and approval.

Otherwise select `review_hosting` before rendering:

- `local-html`: write a standalone local HTML file, retain it, and provide its
  absolute path as a clickable file link. Approval happens in chat. Put reply codes
  at the top (`APPROVE`, `APPROVE Q1B Q2A`, `CHANGES: <notes>`). No server, remote
  account, response submission endpoint or background watcher is required.
- A skill binding: read the mapped skill's complete instructions, then use its
  rendering, hosting and approval protocol with the local HTML path and resolved
  settings. The handler may add on-page response controls using the same kit and
  stylesheet. Do not invoke this hosting binding recursively if its handler calls this renderer.
- A command binding: follow the shared contract's argv and JSON-stdin protocol;
  pass the local HTML path, step and resolved repo facts. Read the result and use
  its delivery and approval instructions. A command failure stops hosting; report
  the originating file and `review_hosting` entry with the error.

Unavailable profile bindings fall back through the resolver with its notice.
Configured handlers own additional approval requirements; do not force chat
approval after a handler supplies another protocol. Do not submit for the user.

## Structure (in order)

0. **Review receipt.** Carry the artifact's review choice onto the page. If the
   user requested `spec-review`, show its recap and applied Fatal/Significant
   findings; if declined, show `spec review: not run (the user)`. Do not require a
   review the user declined, or invent another review requirement for other pages.
1. **Approval bar at the top.** For local delivery, show the chat reply codes.
   For a configured handler, use its response affordance. Record decisions only
   after an explicit response through the selected protocol.
2. **Why this exists.** Before/after panes, at most five bullets each.
3. **Diagram-first sections.** One diagram per concept, at most three caption
   sentences. Render the artifact one-to-one, without re-deriving its decisions.
   For specs, use `to-spec`'s section mapping in its defined order and headings:
   **Why this exists → User Stories → What stops working → The shape →
   Testing Decisions → Out of Scope → Evaluator Rubric**, then any ticket graph,
   open-question decision cards and footer. Omit optional source sections that
   are absent. Show every user story heading and its acceptance criteria verbatim
   as readable text in source order, without a bullet cap. Neither a diagram nor
   the footer's acceptance reminder replaces them. Show every existing case that
   stops working; when there are none, state "Nothing stops working." Render a
   nested `What stops working` subsection separately, not as a user story.
   The review page kit adds no content sections of its own.
4. **Dependency graph for multi-ticket approval.** Show tickets with repo-qualified
   links and titles, native blocked-by edges, topological ordering, and visibly
   blocked nodes. Query the tracker's actual dependencies before drawing; do not
   invent edges. Follow the resolved tracker's protocol to correct dependencies
   when authorized. Distinguish true blockers from suggested build order.
5. **Decision cards.** At most five open questions. Each has at least two
   substantive options, benefits and costs, reply codes, and a marked recommended
   default with rationale. Put FYI items outside Decisions. Include the mechanism,
   consequence and evidence needed to decide without reading the conversation.
   Embed the judged artifact or a working link and its author/date/source.
   Put the discriminating fact first; use a diagram where the choice has structure.
   For handlers with on-page responses, add per-card comments, deselectable options
   and a need-more-info escape; an info request is not an approval.
6. **Footer.** Full text location and revision, acceptance-criteria reminder,
   and originating epic and scope when applicable.

## Diagram craft and styles

Read the running tool's installed `diagramming` skill before drawing. Use this
skill's **review page kit** in local and configured hosting modes alike:

- `assets/review-page.css` is the one stylesheet: the neutral
  `diagramming/assets/atlas-base.css` copied verbatim, then the review-page layer.
  Paste the entire file into one inline `<style>` block. Do not load the base a
  second time, re-derive its palette, or replace it with a hosting palette.
- `kit.html` is the standalone, offline component sheet. Copy the building blocks
  needed by the calling skill; replace all fixture content before delivery. It is
  a component source, not a new section mapping. Its inline CSS is exactly the
  stylesheet. When changing the stylesheet, refresh that inline copy too.

| Building block | Classes and contract |
|---|---|
| Approval bar | `.approval-bar`, `.reply-codes`: show `APPROVE`, `APPROVE Q1B Q2A`, `CHANGES: <notes>` at the top, including when a host adds response controls. Explain what approval authorizes. |
| Section | `.review-section`, `.pair`, `.pane`: retain the calling skill's headings and order. |
| Diagram frame | `.diagram-frame`: scroll horizontally on narrow screens; use labelled inline SVG and neutral `.node` / `.edge` primitives. |
| Decision card | `.decision-card`, `.options`, `.option`, `.option-title`: context, options with gain/cost, recommendation and rationale, reply codes, comments. |
| Ticket graph | `.ticket-graph` inside `.diagram-frame`: topological order, linked ticket titles, solid blocker edges and visibly labelled `.blocked` nodes; dashed annotations for suggested order only. |
| Footer | `.review-footer`: full source and revision, acceptance reminder, approval scope, originating epic and exclusions. |

Use native radio inputs inside `.option` labels and wrap each option's title in
`.option-title`. The checked input drives the green border and ring, check mark and bold title in
both themes and print. A recommendation is a text label, never a preselected
answer. Give each question a clear-selection button (the kit includes its inline
handler) and a need-more-info option. Keep radio names unique per question and
label comment fields. Match approval-bar reply codes to the actual questions and
options on the page. Picking an option is not submission or approval.

All pages must be one file usable offline. Inline CSS, scripts and SVG; never
load remote fonts, stylesheets, scripts or images. The kit adds no server or
submission endpoint. Local pages show reply codes; configured handlers own their
response protocol while retaining those codes as a fallback.

Use accessible SVG (`role="img"`, `aria-label`), theme-aware variables and horizontal
overflow containers. Reserve accent colors for decisions and controls; ordinary
nodes use neutral colors. Use state pills and tabular numbers for status/counts.

## Delivery and decisions

Verify that the local file exists and opens as standalone HTML before linking it.
For a configured host, perform that handler's delivery checks before linking its
result. Include a one-line ask using the selected response protocol. Retain the
page until the verdict is recorded in the source-of-truth artifact. Apply the
user's explicit decision, including open-question answers; an unanswered question
or request for information is not approval.

Avoid prose walls, diagrams as decoration, raw diagram-language dumps, and a page
that makes the user consult the chat to understand the decision. One page per
concept; split an artifact that cannot be read coherently.

## Worked examples

- [Continuity spec approval](examples/continuity-spec.html): package boundaries,
  checklist extension, story coverage and three specification decisions.
- [On-demand channel agents](examples/channel-agents.html): message
  delivery, controller lifecycle, migration and three design decisions.

These sanitized historical reviews demonstrate the review page kit inside the
planning package. Their review receipts describe the source reviews, not a new
review of these adaptations. Replies are practice only; selections do not submit.

## Page assembly and delivery helper

After authoring the HTML body from the mapping above, use
`scripts/review_delivery.py` relative to this installed skill in either tool.
It wraps the body with the review page kit stylesheet verbatim. The body owns
all headings, review receipt, approval bar with chat reply codes, diagrams,
criteria, decision cards and footer; copy the kit's inline clear-selection
handler when using its radio controls. This helper does not summarize or invent
content. First assemble with `--render-only` and inspect the local page. Then
run without that flag for delivery through the selected binding. A hosting
handler already in progress keeps render-only mode and owns delivery itself.

```sh
python3 <installed-visual-review>/scripts/review_delivery.py \
  --body <authored-body.html> --out <retained-review.html> --title <review-title> \
  --repo <target-repo> --settings <resolved-settings.json> \
  --settings-file <originating-planning-profile.json> --render-only
```

Pass the existing resolver result as `--settings`, including any resolved repo
facts, and the planning profile's actual path as `--settings-file` for error
reports. Report its notices once using the shared run ledger before invoking.
A resolution error stops the affected step before page delivery. Builtin local
HTML returns `local_html_path` and chat approval; a command receives that path,
`step`, `repo` and `repo_facts` as JSON on stdin, with its resolved argv and the
target repo as working directory. Follow its returned delivery/approval protocol.
A skill binding returns the named skill and the same request: read that skill
and perform its protocol in the running tool. Do not treat a returned skill
request as completed hosting. Failure stops hosting and reports the originating
settings file and `review_hosting` entry; retain the page and never retry through
a default or shadowed binding. A handler calling this renderer uses
`--render-only` to obtain the local page without another hosting invocation.
