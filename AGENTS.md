# Planning package development

All eleven skills are shared by Claude Code and Codex. Keep their behavior equal.
Keep the review page kit offline and retain upstream provenance and MIT notices.
Run the complete suite before committing:

```sh
uv run --with pytest python -m pytest -q -s tests
```

Before each public push, run `python3 scripts/check-public-range.py <base>` over
the full range to publish; omit the base only for a first push. A match stops the
push. Keep private settings outside the package.
