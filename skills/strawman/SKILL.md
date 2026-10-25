---
name: strawman
description: Offer rough design directions and a recommendation before grilling in dev-plan. Use to settle the overall product shape from existing context, before detailed decisions.
---

# Strawman

A strawman is the step before grilling that offers two or three rough design directions and a recommendation, drawn from existing context without new research. A direction is one rough design shape with its key choice and tradeoffs.

Use only the conversation, existing specs and docs, the repo's `CONTEXT.md`, existing codebase patterns, and any applicable repository guidance. No web research. Use at most one exploration subagent if needed; aim for about five minutes. Read local glossary terms before naming concepts.

Present two or three directions, each in at most six lines:

- One-line shape in user-visible terms.
- The key choice that sets it apart.
- Two or three benefits and costs in total, with both sides represented.

Follow with a recommendation of at most three lines explaining why it wins. The entire output, including the choice prompt, is at most 25 lines. Stay at the level of shape and user-visible behavior; omit internal mechanics.

The user can pick one, merge several, or supply his own. Wait for that decision, then pass the settled direction and directions not taken into grilling's first round. `to-spec` records them in one line of Solution.

If only one shape is sensible, or the conversation already settled the direction, say so and name the direction in at most two lines, then start grilling without a choice prompt. `dev-plan` always invokes this step; standalone `grilling` does not.
