# Craft baseline: accessibility and responsiveness

Extracted verbatim from `SKILL.md` (generic-known accessible-SVG and responsive-container
practice; a frontier model applies this unprompted, but it stays available for a session
that wants the full rule text).

4. **Every diagram is labelled for a11y.** `role="img"` + a real `aria-label` describing the
   flow, not the shapes ("dispatch flows from governor to two workers", not "three boxes").
5. **Responsive.** Wrap each SVG in `<div class="scroll">` (`overflow-x:auto`); `viewBox`
   + `max-width:100%` so it survives a phone. The page body must never scroll horizontally.
