Spec — 2026-10-24, spec review: ITERATE (round 1; F1, F2, F3 applied; no open items), approved by Corey 2026-10-24

Part of the "Visual review release" milestone: this epic, [the harness repository#674](https://github.com/coreyfloyd/development-planning), publishes the planning and visual-review skills as a public package and switches Corey's fleet to it. It absorbs [the harness repository#322](https://github.com/coreyfloyd/development-planning), narrowed from a template library to one review page kit. It builds on the de-personalization epic [the harness repository#1568](https://github.com/coreyfloyd/development-planning) (closed). Outside this spec: social-media posts, a review page server, decision-round and row-triage page shapes, and migrating old review pages.

# The planning package ships publicly with one review page standard

## Problem Statement

Corey wants his planning pipeline (strawman, grilling, spec writing, spec review, ticket breakdown, review pages and diagrams) available to anyone. The 11 skills are now generic, but they still live inside his private dotfiles and the execution repository repositories, so nobody else can install them, and his own copies have no release or version.

The review pages that pipeline produces have no standard. Each of the 20 pages on Corey's MacBook was hand-built by the session that needed it, with its own inline styles, so no two look alike, and a split of the diagram palette on 2026-10-24 changed the look again. The rendering instructions also leave out the part of a spec Corey is approving: a spec's page never shows its user stories with acceptance criteria or what stops working, although the chat approval ask must include both.

## Solution

One public planning package, `coreyfloyd/development-planning` under Apache-2.0, holds all 11 skills: `dev-plan`, `strawman`, `grilling`, `grill-me`, `grill-with-docs`, `to-spec`, `spec-review`, `to-tickets`, `domain-modeling`, `visual-review` and `diagramming`. It installs as a Claude Code plugin, with an installer that links the same skills into Codex, and publishes as a signed GitHub release the way continuity does. Corey's machines install it from a pinned release, and his private copies are removed, so there is one source. His personal planning settings stay private.

`visual-review` gains a review page kit: one stylesheet and a set of building blocks (approval bar, section, diagram frame, decision card, ticket graph, footer). The skills keep deciding a page's structure; the kit fixes its look. Every review page, public or Corey's own, uses the kit, and spec pages show acceptance criteria and what stops working. Two of Corey's real reviews ship as worked examples. The run is unattended except for two stops: Corey approves the kit's look before anything builds on it, and Corey signs the release.

Settled direction: move the skills into one public package installed from a pinned release (the continuity pattern), building the kit first; chosen over exporting a copy from the private repos on each release, and over releasing first and adding the kit later.

## User Stories

### S1 — As Corey, I want one standard look for every review page, so that pages stop differing and I judge content, not layout

- [ ] The package's `visual-review` ships a review page kit: one stylesheet and the building blocks approval bar, section, diagram frame, decision card, ticket graph and footer.
- [ ] The kit's stylesheet is the neutral diagram base plus a review-page layer, readable in light and dark themes and in print, with a selected option shown as filled, checked and bold.
- [ ] The kit replaces the skill's previous single example page.
- [ ] A page built with the kit works as one local file opened offline, with no remote stylesheet, script or font, and its approval bar shows the chat reply codes.
- [ ] Corey's own review pages, delivered through his private hosting, use the same kit and stylesheet; Atlas styling appears only on fleet architecture maps.
- [ ] Before any later story starts, Corey has approved the kit's look on a re-rendered continuity spec approval page; his approval is recorded on the epic.

### S2 — As anyone approving a spec, I want the review page to show what I am approving, so that the page and the chat ask agree

- [ ] A spec's review page shows every user story with its acceptance criteria verbatim.
- [ ] A spec's review page shows what stops working, or states that nothing does.
- [ ] Sections keep the order and headings the skills define; the kit adds no sections of its own.
- [ ] Open questions still appear as decision cards, at most five.

### S3 — As someone new to the package, I want worked examples, so that I can see what a finished review looks like

- [ ] The package includes two complete example pages built with the kit: the continuity spec approval and the on-demand Slack channel agents design review.
- [ ] Neither example contains Corey's hosts, network addresses, private repository names, home paths, ticket links into private repositories, or people other than Corey.
- [ ] Both examples open standalone, offline.
- [ ] The 20 existing review pages on Corey's MacBook are unchanged.

### S4 — As someone outside Corey's setup, I want to install the planning package in my tool of choice, so that I can plan features with it

- [ ] `coreyfloyd/development-planning` is a public GitHub repository under Apache-2.0, containing exactly the 11 skills listed in Solution.
- [ ] The skills forked from Matt Pocock's skills carry his MIT notice and credit.
- [ ] Installing it as a Claude Code plugin makes all 11 skills available; its Codex installer makes all 11 available in Codex.
- [ ] With no planning profile and no repository planning settings, `dev-plan` runs end to end and reports each default it used, once.
- [ ] The README explains installation in both tools, the planning profile and repository planning settings, and links both examples.
- [ ] No pushed commit, at any point in the repository's history, contains Corey's hosts, network addresses, private repository names or home paths.

### S5 — As someone installing a release, I want to verify it, so that I know it is what Corey published

- [ ] A GitHub release `v0.1.0` publishes the archive, its checksum, the checksum's signature, the public key and the verification script, matching continuity's release contract.
- [ ] The signing key is the one continuity and Hippocampus releases use.
- [ ] Corey signs the release himself; no agent signs or handles the key's passphrase.
- [ ] The verification script, run on the downloaded assets alone, confirms the archive.
- [ ] Run on an altered archive, a mismatched checksum, or a missing or invalid signature, the verification script fails, names the check that failed, and reports the archive as not verified.

### S6 — As Corey, I want my machines to use the released package, so that there is one source for every planning skill

- [ ] Before the switch, one recorded `dev-plan` run on a small real idea with Corey's profile captures: where the spec and tickets were published, their labels, how the review page was delivered, the approval flow, the spec-review launch path, and any default notices.
- [ ] After the signed release exists, an install on any of Corey's machines provides all 11 skills from the pinned release in both Claude Code and Codex.
- [ ] When the pinned release cannot be downloaded or fails verification, the install stops with an error naming the release and the failed check, and that machine keeps the planning skills it had before, in both tools.
- [ ] An install interrupted during the switch leaves each tool on either its previous planning skills or the new release, never without them; running the install again completes the switch.
- [ ] The skills' private copies no longer exist in the harness repository or the execution repository.
- [ ] Changing the pinned release is a one-line change that moves every machine to another release.
- [ ] Corey's planning settings stay in his private setup. After the switch, the recorded idea run again matches every captured item: publication destination, labels, review page delivery, approval flow and spec-review launch path, with no default notice. Spec and ticket wording may differ.
- [ ] Every catalog, link, and role or agent file that names one of the 11 skills still resolves, and the the harness repository and the execution repository suites pass.
- [ ] The "Visual review release" milestone's exit goal no longer requires a gate server.

### What stops working

- Editing a planning skill directly in the harness repository or the execution repository. Edits become a pull request to the planning package plus a pinned-release change in the harness repository.
- The visual-review skill's previous single example page; the kit's examples replace it.
- Review pages styled ad hoc per session, and Corey's review pages styled with Atlas.

## Data Model

- **Planning package**: one release is one signed, versioned archive of the 11 skills; the repository holds the source, and Corey's fleet records which release it installs.
- **Review page kit**: one stylesheet plus a fixed set of building blocks; one kit per package release.
- **Example page**: one example is one complete review page built with the kit from a real review, with private details removed.

## Architecture Decisions

- The planning package follows continuity's distribution pattern: a public repository, a Claude Code plugin, a Codex installer, signed releases, and the harness repository installing a pinned release.
- The package ships no server. Pages are local files with approval in chat; hosted delivery stays a personal planning-profile binding.
- Structure stays in the skills (`visual-review`'s page parts and `to-spec`'s section mapping); the kit holds only the stylesheet and building blocks.
- New terms enter the the execution repository glossary before the skills or code use them: **planning package** and **review page kit** (the glossary's existing **Template** means a job definition and is not reused).
- The repository is public from its first push. Every push is preceded by a scan of the full pushed commit range for private names and home paths; a match stops the run.
- Order: glossary terms → review page kit → Corey's look approval → mapping fix and examples → package repository, plugin, installer and README → release build → Corey signs → fleet switch.

## Testing Decisions

Tests check external behavior: what a user installs, sees and verifies.

- **Setup references (existing seam, `test_planning_skill_setup_refs`):** moves into the package and also covers the kit, its stylesheet and both examples; every shipped file reports 0 private references.
- **Settings resolution (existing seam, `test_planning_settings`):** moves into the package unchanged; it covers which review-hosting and spec-review binding is chosen, not page delivery.
- **Review delivery (new seam):** with the kit, local-file mode writes a standalone page with chat reply codes; a configured hosting binding receives the local page; a failing binding stops hosting and reports its settings file and entry. (`test_review_planning_settings` only scans for private references and is not delivery coverage.)
- **Pinned install (continuity install test pattern):** a sandboxed install of the pinned planning package links all 11 skills in both Claude Code and Codex; an unavailable or unverifiable release, and an interrupted install, leave the previous skills in place.
- **Release contract (continuity release test pattern):** archive, checksum, signature, public key and fingerprint agree, and each altered or missing asset fails verification by name.
- **Rendered pages (new):** each example opens standalone with no remote resource, and a spec page rendered from a real approved spec contains every acceptance criterion verbatim and its what-stops-working list.
- **Live run:** the recorded pre-switch `dev-plan` run (S6) is the baseline; the post-switch run is compared item by item against it, not by wording.

## Out of Scope

- Social-media posts about the workflow (Corey's curation).
- A review page server, and the gate server named in the milestone's original exit goal.
- Decision-round and row-triage page shapes.
- Migrating the 20 existing review pages.
- Changes to continuity or the `surface` plugin.

## Evaluator Rubric

`runtime-rubric` for the package, install and fleet switch; `design-rubric` for the review page kit and examples. Feature-specific: no private reference in any pushed commit; both tools behave identically.

## Further Notes

- Decisions: Corey, 2026-10-24, this planning session (D1–D12), plus the 2026-10-23 repository, license, scope and membership decisions recorded on [the harness repository#674](https://github.com/coreyfloyd/development-planning).
- Spec review round 1 (Codex `eval-spec`, 2026-10-25 UTC, verdict ITERATE): F1 added failure and recovery criteria for verification and install; F2 replaced the live comparison with a recorded baseline; F3 corrected a wrongly named test seam. No Minor findings.
- A row-triage page shape may come back as its own ticket if Corey builds more such reviews; two exist today.
- Approval: approved by Corey 2026-10-24 in the planning session (chat reply "approve"); no open questions.
