# Ballots

## What it is

A ballot is the only sanctioned shape for a decision that must be made by the human at the top of the studio. It converts an open question into a bounded pick: a one-line statement of what is being decided, two to four options each with a one-line consequence, a marked recommendation, and a statement of what happens the instant an option is chosen. The ballot exists because the human's attention is the scarcest resource in the whole apparatus, and an unstructured "what do you think?" spends that resource badly — it forces the human to reconstruct the option space the orchestrator already holds. A ballot spends thirty seconds of human attention and returns a ratified decision the orchestrator can execute in full.

## The protocol

**Authoring a ballot.** Before surfacing any decision to the human, package it as:

1. **The question** — one sentence naming exactly what is being decided. If you cannot state it in one sentence, it is two decisions; split them.
2. **2–4 options** — no more. Each option is one line and carries a one-line consequence ("Option A: protect the trunk — no direct pushes for anyone, all changes go through review"). If the real option space is larger than four, you have not done the pre-work; collapse dominated options yourself and present only the live ones.
3. **A marked recommendation** — exactly one option flagged as your recommendation, with at most one clause of reasoning. Withholding a recommendation to "stay neutral" pushes analysis back onto the human and defeats the mechanism.
4. **What happens after the pick** — the concrete next action for each option, so the human knows they are authorizing execution, not opening a discussion. "On A, I apply branch protection this session and re-stamp the tracker; on B, I leave it and file a follow-up."

**Recording ratification.** When the human answers:

5. **Record their words VERBATIM**, quoted, on the durable decision surface (the tracking issue and the decision/ruling file) — not paraphrased, not summarized. A one-line answer settles a ballot; capture that line exactly.
6. **Then execute fully** under the recorded decision. The verbatim record is what lets a later session, or a review agent, distinguish a real ratification from a fabricated one.

**Delegation semantics.** The human will often answer with a delegation rather than a specific pick — "go with your rec", "merge what's ready", "ok do that". Treat a delegation as a real, recorded decision (quote it verbatim as above) and act decisively under it, but **never stretch a delegation past its plain scope.** "Merge what's ready" authorizes merging the items that already passed every gate; it does not authorize merging a borderline item, changing a gate, or making a new design decision that happened to be nearby. When the plain scope of a delegation does not cover the thing in front of you, that thing is a new ballot.

**Queueing when the human is absent.** Ballots are never self-answered. When the human is away:

7. Park each ballot on the durable board/queue surface where it is visible at the next check-in — never buried in a chat log that scrolls away.
8. Keep work that does not need the decision moving (green-lane changes, teams working their existing plans); hold work that does.
9. **Batch** accumulated ballots so the human can clear them in one sitting, rather than being interrupted once per decision.

## Why it exists

- A ticket that merely *promises a memo* is not a ballot — it defers the decision instead of making it pickable. Codified after a decision-issue that named a coming write-up rather than presenting the options (`studio:docs/kb/director-handbook.md` §1, the "#33 incident").
- Ratifications must be recorded verbatim because an unrecorded in-session ruling is *indistinguishable from a fabrication* to the review layer — a sound decision with no trail on any durable surface got held as suspect, and the fix was to make verbatim recording the first act after any ruling (`studio:docs/kb/director-handbook.md` §6, the #114/#115 incident; `studio:docs/kb/director-handbook.md` §1).
- Delegation-without-overreach was earned from the pattern where the human delegates often and rewards decisiveness, but scope-stretch turns a granted trust into an unauthorized act (`studio:docs/kb/director-handbook.md` §1).
- The "wait for answers" discipline — a question to the human ends the turn, no speculative work racing the reply — is a sibling rule to ballots: the orchestrator poses the ballot and stops, rather than branching the tree on a guessed answer (`validation:CLAUDE.md`, the wait-for-answer feedback rule; `studio:docs/kb/director-handbook.md` §1).
- Queue-don't-self-answer during multi-day human absence is explicit standing policy (`studio:docs/kb/director-handbook.md` §7).

## Failure modes of the mechanism itself

- **Ballot inflation.** Presenting five, six, seven options is a tell that the pre-work of collapsing dominated choices was skipped; the human now does that work. Cap at four, hard.
- **The neutral dodge.** Omitting the recommendation to appear even-handed re-imposes the analysis the ballot was meant to remove. Always mark one.
- **Fake ballots.** A "ballot" that promises a document, defers to a later meeting, or asks an open-ended question is a non-decision wearing the form. If there is no pickable set of options, it is not a ballot yet.
- **Paraphrase creep.** Recording the gist instead of the words erodes the audit trail; a later session cannot tell a soft summary from an invention. Quote.
- **Delegation laundering.** Reading a broad grant ("do what's right") as license for a specific contested act. When in doubt whether the delegation covers it, it does not — write the next ballot.
- **Chat burial.** Letting ballots accumulate only in conversation, where they vanish at the next session boundary, instead of on a durable queue.

## What varies per project

The bindings layer declares: the **durable surfaces** a ratification is written to (issue tracker, ruling/decision file, board field); the **queue surface** where absent-human ballots park; which **decision classes** are the human's alone versus delegable to the orchestrator; and any **standing delegations** that pre-authorize routine picks (e.g. "merge green-lane docs without a ballot"). See `bindings/TEMPLATE.md` → decision surfaces, autonomy grants, and standing delegations.
