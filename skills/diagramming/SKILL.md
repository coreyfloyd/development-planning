---
name: diagramming
description: "Author hand-built spatial diagrams for docs, specs, and reviews: architecture, topology, state, sequence, flow, data, or entity relationships. Use for inline SVG diagrams; not for claude.ai Artifact pages."
---

# Diagramming

The shared craft for **how diagrams get drawn**. A diagram earns its place only when
**position or flow carries meaning** — otherwise a table or prose is better and honest. When
a diagram IS warranted, it is a **hand-built, theme-aware, inline SVG** — never a mermaid dump
that collapses into boxes-in-a-column (the "lists of lists" failure).

Two consumers build on this skill:
- **`visual-review`** = this craft + decision cards + surface hosting (interactive approval).
- **Documentation diagrams** = this craft rendered directly and published via
  a configured review host or a local HTML file — no review attached.

The dividing line: **document/explain** (static, no response needed) → render + publish here.
**Review/decide** (the user must respond) → hand off to `visual-review`, which embeds these
diagrams inside decision cards.

## The craft (binds every diagram type)

These five hold for every archetype below. A violation is a downgrade, not a nit.

1. **No external anything.** Inline `<svg>` hand-authored, inline `<style>`. **NO mermaid**
   (renders nothing over `file://`, drifts to lists-of-lists), no CDN `<script src>`, no
   `<link rel=stylesheet>`, no remote fonts/images. The page must open correctly as a bare
   `file://` with the network off. **Declare `<meta charset="utf-8">` as the first line** of
   any standalone HTML file — without it a `file://` page renders UTF-8 punctuation as
   mojibake (`—`→`â€”`, `≤`→`â‰¤`, `·`→`Â·`). (Artifacts inject their own charset in the
   wrapped `<head>`, so this line is specifically for the standalone-file path.) If in
   doubt, prefer HTML entities — `&mdash;`, `&le;`, `&middot;` — over raw non-ASCII glyphs.
2. **Spatial-first, not a disguised list.** Use a diagram only where position/flow carries
   meaning. Use a **table** where the inventory is genuinely tabular (a vocabulary, a
   registry, counts). Do not draw a diagram that is secretly a bulleted list.
3. **Theme-aware via CSS vars.** Every stroke/fill uses `var(--…)`, never a hardcoded fill
   for a semantic element. Palette defined on `:root`, then re-defined under
   `@media (prefers-color-scheme: dark)` AND both `:root[data-theme="dark"]` /
   `:root[data-theme="light"]` so a viewer toggle wins in both directions. Give `body` an
   explicit token background. `assets/atlas-base.css` already ships this four-block palette
   plus the shared classes — **paste it verbatim; do not re-derive a palette.**
4. **A11y-labelled and responsive.** Standard accessible-SVG and responsive-container
   practice — the full rule text: [references/craft-baseline.md](./references/craft-baseline.md).
5. **Simple primitives only.** `rect`, `line`, `circle`, `path` (arcs) + `marker` arrowheads.
   No hand-authored complex bezier art. `ui-monospace` (`var(--mono)`) for every system term —
   state names, signals, paths, commands; system sans for prose; `tabular-nums` for numbers.

### Two correctness rules (enforced by eye)

- **No dangling edge.** Every `<path>` carrying a `marker-end` (arrowhead) must start AND end
  inside a drawn `<rect>`/node. Before shipping each SVG, list its arrow paths and confirm
  both endpoints land on a node. An arrow into empty space is the defect.
- **Cross-lane edges resolve to the correct lane.** An edge crossing a boundary must terminate
  in the node on the *right* lane. Host-qualify ambiguous cross-lane nodes (`name@host`).

### Source & honesty (when the diagram documents live state)

- **`source:` footnote per section.** Documentation diagrams of real systems carry a
  `<p class="src">` naming the command(s)/file(s) the content came from — run THIS pass, not
  copied from a prior render. A box with no traceable source does not go on the page.
- **Observed vs asserted must be visually distinct.** Something you probed this run = solid
  border; something claimed only by a registry/spec and not observed = dashed grey +
  explicit "NOT PROBED" / "claim" label. Never draw an assertion as observed state.

## Assets (copy, don't re-invent)

Canonical assets live in the `assets/` directory of this installed skill in the running tool (resolve relative to
this `SKILL.md`, in either Claude Code or Codex):

- **`assets/atlas-base.css`** — the complete `<style>` body: four-block theme palette
  (`:root`, `@media dark`, `[data-theme=dark|light]`) with semantic vars (`--ink`, `--bg`,
  `--panel`, `--line`; state colors `--ok`/`--warn`/`--hot`/`--off`; neutral node fill `--node`
  and border `--nodeline`), plus `.src`, `.card`, `.pill`, `.legend`, `.grid`, `.scroll`,
  and `ul.find`. The filename is retained for existing callers; the palette is neutral.
  Paste verbatim inside `<style>`.
- **`assets/svg-lane-example.svg`** — the worked exemplar: `<defs><marker id="ar">` arrowhead,
  a solid probed lane with a label chip, node rows stroked by neutral border vars, a **dashed grey
  "NOT PROBED" lane**, and cross-lane edges. Model new SVGs on its structure and scale
  (viewBox width ~1080–1120).

## Semantic color convention

Use neutral `--node` fills and `--nodeline` strokes for ordinary nodes, `--ink` for text,
and `--line` or `--dim` for edges. Reserve `--ok` (green), `--warn` (amber), and `--hot`
(red) for success, caution, and failure states; `--off` marks inactive or unobserved state.
Labels and border styles must also convey state so color is never the only signal.
Domain-specific colors belong in an optional consumer stylesheet, pasted **after** the
base, never in this shared palette. The generic example needs only the base.

## Archetype catalog

Pick by what the reader must extract. Each entry: when → the spatial recipe → primitives.
All obey the craft rules above; the exemplar SVG is a **system map** — the others are the
same primitives arranged differently.

| Archetype | Reach for it when the reader must see… | Spatial recipe |
|---|---|---|
| **System / topology map** | what talks to what, where things run | host **lanes** → nodes → labeled edges; cross-host edges land in the right lane. *(the exemplar)* |
| **State machine** | how a thing moves between statuses | **pill** nodes, directed `path` transitions each carrying its trigger label; entry dot; terminal double-stroke |
| **Timeline** | when things happen / deadlines / grace windows | horizontal axis, event **dots**, duration/grace **bars**; "now" marker; labels above/below to avoid collision |
| **Swimlane** | a process split across actors, or concurrency/survival | one horizontal lane per actor; steps as boxes in their lane; vertical hand-off edges between lanes |
| **Communication flow (fan-in/out)** | many producers → few channels → consumers | source column → channel column → sink column; edges labeled with what flows; group channels by kind |
| **Dependency graph** | blocked-by edges and a legal order | DAG left→right in topological order; blocked edges distinct; annotate the critical path |
| **Sequence** | ordered messages between a few actors over time | actor headers across top, **lifelines** down; numbered request/response arrows top-to-bottom; activation bars |
| **Process / flowchart** | decision branches and outcomes | start/end pills, step rects, **diamond** decisions with labeled yes/no out-edges; keep one primary path vertical |
| **Data pipeline** | a transform chain ingest→…→sink | stages left→right, each a box; edges labeled with the artifact/shape passed; mark the writer/reader of any queue separately |
| **Entity-relationship** | data model shape (for a spec's Data Model) | entity boxes with a field list header; relationship edges with cardinality (`1`, `∞`) at each end; no SQL |

**Anti-patterns (all archetypes):** mermaid; emoji section markers; a diagram used as decoration
under prose that already says everything; a "diagram" that is one column of boxes (that's a
list — use `<ul>`); unbounded scope (one screen-page per concept — if it needs 10 sections the
source is the problem, not the diagram).

## Delivery

- **Documentation / explain-only** (no decision attached): render self-contained HTML
  beside the document it illustrates. If review hosting is configured, use that host;
  otherwise deliver the local HTML file. State once which default was used.
- **A decision is attached** (the user must approve/pick): hand off to **`visual-review`**,
  which wraps these diagrams in decision cards and handles approval and delivery.
  This skill draws; `visual-review` decides.
- **An embedded artifact page** is the target: follow that medium's delivery instructions;
  the accessible SVG and theme rules here still apply.
