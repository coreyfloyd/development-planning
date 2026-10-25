---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Ask the user about user-visible outcomes, authority, and failure behavior. Resolve internal mechanics from those decisions. Before asking a question, test whether an implementation agent could choose the answer from approved acceptance criteria; if so, do not ask it. Summarize proposed mechanics by identifying existing coverage, genuinely new behavior, and stall risk. Batched questions must cover independent decisions rather than facets of one mechanism.

Word every question so **"yes" accepts the recommended answer**. Put the recommendation in the question itself (for example, "Should we keep drafts until you publish?"), then explain the alternatives and their tradeoffs. Separate questions in a round with a horizontal rule (`---`).

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer and why it beats the alternatives>

---
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.


When called by `dev-plan`, build the first round on the settled direction from `strawman`. Standalone grilling does not invoke `strawman`.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
