# Two-Surface Rule — a decision must land on two surfaces, and both get injected

## What it is

A discipline that a ratified decision is not "recorded" until it exists on **two** durable surfaces — a canonical register/law file *and* the closed decision record (issue/ticket/PR) that produced it — and that *both* surfaces are injected into every agent that reasons about whether the question is settled. The rule has a sharp corollary: a decision that lands on **zero** surfaces is indistinguishable from a fabrication to the review layer, so recording the human's verbatim words is the *first* act after a ruling, before any building on it. Two surfaces give redundancy (one can lag), queryability (the register is scannable, the decision record has the reasoning), and a fabrication check (a claimed ruling with no trail is held, not trusted).

## The protocol

1. **Every ratified decision is written to two surfaces:** the canonical law file (the register entry) *and* the closed decision record (the issue/ticket where it was decided). Neither alone counts as recorded.
2. **Record the human's words verbatim, first.** The moment the human rules — including when they rule *inside* a working session — quoting their exact words onto the decision record is the team's **first** act, before building on the ruling. A ruling you build on but never record is, to every downstream reviewer, a phantom.
3. **Check both surfaces before calling a question open.** Before an agent declares a design question unsettled, it must consult *both* the register and the closed decision records. The register can lag the decisions, or vice versa; a question is only open if *neither* surface answers it.
4. **Inject both surfaces into every review/advisor agent prompt.** Any agent asked to reason about what is settled receives the register files *and* the decision-record identifiers in its briefing (see the context-injection mechanism). An advisor holding only one surface will confidently report ratified law as nonexistent.
5. **An unrecorded stamp is a HOLD, not an accusation.** If a team stamps "RULED" with no trail on any law surface, the reviewer treats it as a review hold until a trail exists — and *verifies with the human* before treating it as fabricated. Never accuse first; the ruling may be real and merely unrecorded. Once confirmed, backfill both surfaces.
6. **Keep the two surfaces reconciled at shutdown.** The session-end ritual re-stamps the register to the session's final state and updates the pointer that indexes the decision records, so the two surfaces do not drift apart between sessions.

## Why it exists

- The rule is stated in `studio:docs/kb/director-handbook.md` §3: "Rulings live on TWO surfaces: `design/rulings/…` files AND closed `type:decision` issues. Check both before calling any question open — and inject both into every review/advisor agent's prompt."
- The injection half was earned from the **stale-advisor incident**, recorded in the same handbook's §6 failure catalog: "Advisor calls ratified law 'open' → inject decision issues + register into every agent prompt" — an advisor given only the register "called three ratified decisions nonexistent" (§3).
- The zero-surfaces corollary is earned from a dated incident in `studio:docs/kb/director-handbook.md` §6: a team stamped "RULED — [human]" with no record on any repo law surface, "indistinguishable from fabrication to the review layer (the sweep held two sound PRs)"; the resolution codified that recording the human's verbatim words on the decision record is the team's FIRST act, the director verifies an unrecorded stamp *with the human* before treating it as phantom, and the stamp stays a review HOLD until a trail exists (2026-07-07; the human confirmed the rulings were his; resolved same day).
- The verbatim-recording discipline is reinforced project-wide in `studio:CLAUDE.md` hard rule 8 ("Rulings land in `design/rulings/` as numbered … entries") and the director's contract in `studio:docs/kb/director-handbook.md` §1 ("Record ratifications VERBATIM… then execute fully").

## Failure modes of the mechanism itself

- **Surface drift.** The two surfaces disagree because one was updated and the other wasn't — now *which* is truth is itself ambiguous. Reconcile at shutdown; when they conflict mid-session, the human's verbatim quote on the decision record is the tiebreaker.
- **Ritual without injection.** Teams dutifully write both surfaces but the review agents still get only one in their prompt — the stale-advisor failure recurs despite the records existing. Injection is not optional; it is half the rule.
- **Delayed recording.** Building first and recording "later" opens the exact phantom-ruling window the rule closes. First act, before building.
- **Over-application.** Treating a genuinely open question as settled because *one* surface has a stray stamp. The "check both" clause guards this — one surface is not enough to *close* a question either.
- **Accuse-first.** Jumping to "fabricated" on an unrecorded stamp damages trust and may be wrong. The mechanism mandates verify-with-human-first; the stamp is held, not condemned.

## What varies per project (bindings)

Which two surfaces a project uses (a rulings register file + a `type:decision` issue tracker; or a decisions log + merged PRs; or an ADR file + a ticket); the identifier scheme for decision records; the label/status that marks a decision "closed"; and the exact prompt fields that carry both surfaces into agents. Declare the two named surfaces in the project's bindings — the *shape* (two surfaces, both injected, verbatim-first, zero-surfaces-is-a-hold) is the mechanism.
