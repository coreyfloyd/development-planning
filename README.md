# Development Planning

A planning package for Claude Code and Codex: settle a direction, work through
open decisions, write and approve a spec, and break it into executable tickets.
The review page kit gives the resulting review pages one offline, light/dark look.

## Install

Requires Python 3.9+, Git, and your chosen agent tool. The generic tracker uses
GitHub CLI (`gh`), authenticated for the repository where you plan work.

### Claude Code

Clone the package and load it as a local plugin:

```sh
git clone https://github.com/coreyfloyd/development-planning.git
claude --plugin-dir ./development-planning
```

The plugin uses Claude Code's standard `skills/` discovery. All eleven skills
are available under the `development-planning` namespace; start with
`/development-planning:dev-plan`. Keep the plugin directory for future sessions
and pass `--plugin-dir` each time you launch Claude Code with it.

### Codex

From the same clone:

```sh
python3 development-planning/scripts/install-codex.py
```

This links all eleven skills into `${CODEX_HOME:-~/.codex}/skills`. Restart the
Codex session to refresh discovery, then invoke `$dev-plan`. An alternate home
can be selected with `--codex-home <directory>`. Keep the clone in place: links
point to its skill directories. Reinstalling from the same clone is idempotent.
Existing foreign directories or links stop the install before any links change;
move conflicting skills aside yourself if you intend to replace them.
The installer does not change hooks, trust settings, or agent configuration.

## Skills

| Skill | Purpose |
|---|---|
| `dev-plan` | Coordinate direction, questions, spec, approval, and ticket breakdown |
| `strawman` | Compare rough directions before the interview |
| `grilling` | Resolve the decision frontier |
| `grill-me` | Stress-test an idea through questions |
| `grill-with-docs` | Resolve decisions while updating domain documents |
| `to-spec` | Turn settled decisions into a product spec |
| `spec-review` | Review a spec in a fresh context, only when requested |
| `to-tickets` | Derive demoable slices and verified tracker dependencies |
| `domain-modeling` | Maintain domain language and architecture decisions |
| `visual-review` | Render approval and design review pages using the kit |
| `diagramming` | Create hand-built spatial diagrams |

## Planning settings

No setup files are required. Without them, the defaults are GitHub issues in the
repository named by its `origin` remote, issue bodies for specs, no additional
label restrictions, “the user” as the name, local HTML with chat approval, and a
fresh native subagent for an optional spec review. The target repository's own
publication policy still applies. Each default is reported once per planning
run; downstream phases reuse the resolved values and notice ledger.
Optional reviews require native subagent support; unavailable support is reported
as a blocker. Publishing requires working GitHub authentication and repository access.

A **planning profile** holds personal bindings and optional repository defaults
at `~/.config/development-planning/profile.json` (or the file named by
`PLANNING_PROFILE`). For example:

```json
{
  "user_name": "Taylor",
  "spec_location": "docs/specs"
}
```

**Repository planning settings** are a tracked `.planning.json` at the target
worktree root. They override repository facts individually: `tracker`,
`label_vocabulary`, and `spec_location`. Personal entries (`user_name`,
`review_hosting`, `spec_review_launch`) belong only in the profile.

```json
{"spec_location": "docs/proposals"}
```

Track that file in Git before using it. Invalid or untracked repository settings
stop the affected step and name the file and entry. A configured handler's failure
does not silently fall back. See the full [settings contract](skills/dev-plan/references/planning-settings.md)
for precedence, available bindings, command inputs, and notice handling.

## Review page kit and examples

The kit ships its stylesheet inline, requires no server, and keeps approval in
chat by default. Open the [kit](skills/visual-review/kit.html) or either complete
worked example directly in a browser:

- [Continuity spec approval](skills/visual-review/examples/continuity-spec.html)
- [On-demand channel agents design review](skills/visual-review/examples/channel-agents.html)

The skills determine section order and content; the kit supplies the visual
building blocks. A configured review-hosting handler can deliver the same page.

## Tests

Run the complete package suite (including settings resolution in both tools,
private-reference checks, plugin discovery, sandboxed Codex installs, offline
examples, and review delivery):

```sh
uv run --with pytest python -m pytest -q -s tests
```

Only pytest is needed for tests; shipped scripts use Python's standard library.
All tests use temporary tool homes and repository settings.

## Public history gate

Before **every** push, scan the entire commit range being published, including
intermediate commits and commit messages. Run the following, using the remote
base commit as the argument (omit it for the first push of an empty repository):

```sh
python3 scripts/check-public-range.py <base>
```

A match stops publication. Correct the unpublished history, rerun the scan, and
push only after it reports zero matches. A scan of the final tree is insufficient.
The package test also reports a private-reference count for every shipped file.

## License and credit

Apache-2.0; see [LICENSE](LICENSE). Portions adapted from
[Matt Pocock's skills](https://github.com/mattpocock/skills) retain their MIT
license, full copyright and permission notice in [LICENSE-MIT](LICENSE-MIT),
and per-skill provenance records. See [NOTICE](NOTICE).
