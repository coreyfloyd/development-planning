# Changelog

## Unreleased

- `to-tickets` checks the breakdown against the spec before showing it: every
  ticket names an evaluation seam (a ticket without one is refused by name), the
  spec's seams map to evaluation seams, every story and criterion is covered, and
  blocking edges and shared contracts match the spec.
- Every published ticket body carries an `Evaluation seam:` line; publication
  refuses a ticket without one.
- Shared instructions for Claude Code and Codex.

## 0.1.9 — 2026-11-23

- Keep configuration as configuration in specs: when an existing setting owns a
  value, or the user asked for it to be configurable, `to-spec` writes the behavior
  as following that setting, lists current values and new defaults only in Further
  Notes, and adds a criterion that the behavior follows a non-default value.
- Grilling settles those decisions as "follows setting X" and adds a new setting
  only when an approved requirement needs the value to vary.
- Add the "Configuration not encoded" spec-review check; a configuration-owned
  value written as fixed behavior is Significant (`ITERATE`).
- Shared instructions for Claude Code and Codex.

## 0.1.8 — 2026-11-19

- Require a Simplest design spec section: the smallest design meeting the criteria,
  requirement traces for every part, state, setting and option, and a simpler
  alternative with why it falls short. Preserve the section on review pages.
- Ask “what breaks if we drop this?” for each added part during grilling.
- Check Simplicity in every requested spec review; missing justification or a
  skipped or unjustifiably rejected simpler alternative is Significant (`ITERATE`).
- Shared instructions for Claude Code and Codex.

## 0.1.7 — 2026-11-15

- Allow agents to invoke `to-tickets` in Claude Code and Codex, retaining
  approval of the ticket breakdown before publication.

## 0.1.6 — 2026-11-13

- Carry Guardrails and per-criterion check methods through grilling, specs,
  review pages and ticket breakdown.
- Require a Documentation consulted spec section with sources, decisions and
  documentation gaps, shared by Claude Code and Codex.

## 0.1.5 — 2026-11-12

- Settle migration and cutover choices during grilling, including applicable
  backup/recovery, measurements, verification, parallel testing, rollout and
  rollback provisions, with explicit not-applicable decisions and costs/delays.
- Carry those choices through a dedicated spec section, review pages, fidelity
  checks and ticket breakdown. Separate before-cutover blockers from after-deploy
  checks without adding unrequested waiting periods or rollout infrastructure.
- Shared guidance for Claude Code and Codex. No new mechanical gate.

This release includes the approved migration/cutover addition from
[development-planning#5](https://github.com/coreyfloyd/development-planning/issues/5).
The issue's original Guardrails and per-criterion check-method work remains open.
