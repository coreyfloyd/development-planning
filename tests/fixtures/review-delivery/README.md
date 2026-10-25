# Approved spec review fixture

This is a redacted capture of the planning package release spec approved by
Corey on 2026-10-24, source revision `93b6a582`. Private repository names and
links have been replaced with generic descriptions and the public package URL.
It is retained source material, rather than invented test data.

`spec-review-body.html` follows that redacted source's section mapping, including
six stories, 34 criteria, and three cases that stop working. Tests compare its
wording verbatim with `approved-spec.md`. The source has no open questions, so
its decision-card controls are absent. The delivery helper wraps this body with
the current kit stylesheet; tests inspect the resulting standalone HTML and
exercise isolated command bindings in both tool modes. The public worked
examples live separately under `skills/visual-review/examples/`.
