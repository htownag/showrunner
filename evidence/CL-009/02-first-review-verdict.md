# First-review verdict (reviewer A) — REDACTED

*The verdict the build session recorded for the crafting-bench work item, on the code excerpted
in `01-first-review-passed.excerpt.cs`. Transcribed from the team's durable build log; identifiers
neutralized per PROVENANCE.md. This is the artifact that makes CL-009 checkable: reviewer A did
not merely fail to look — it affirmatively vouched for the exact path that carried both holes.*

## Verdict as recorded

> **Code review gate: PASS-WITH-CHANGES — all applied.** Core verified correct (honest-preview
> math reproduced bit-for-bit, output clamp, determinism, **atomicity, persistence**). Fixes
> landed before commit: (MAJOR) the Tuning Round budget is now enforced server-side —
> `ResolveCraft` rejects an over-budget decision list (a client can't buy extra rounds; hard
> rule 4); (MINOR) the critical-success predicate no longer marks a zero-gain success /
> degenerates on narrow ranges; (NITs) the honest-preview statistical test gained a chi-square
> uniformity bound, away-from-zero rounding, a documented clamp, and a server-derived-seed remark.

Test evidence at this verdict: the suite passed at **77 tests** (unit + live-database
integration, 0 skipped).

## Why this verdict is the proof, not just the setup

Reviewer A ran under the same "hard rule 4" server-authority frame that the holes violate, and
under that frame it *did* catch and fix a third server-authority issue (the Tuning-Round budget:
a client buying extra resolution rounds). So the reviewer was actively hunting client-side-trust
defects on this exact diff — and still passed:

- a lot-read query with **no owner predicate** (any actor could name a foreign owner's lot id and
  the transaction would lock and consume it), and
- a quantity-weighted quality aggregate that **trusts the caller's input-id list without dedup**
  (the same id twice double-weights its quality while being consumed once — value fabricated from
  a duplicated reference).

Reviewer A's own words vouch for the surface both holes live on: *"Core verified correct ...
atomicity, persistence."* The consume/persist transaction it called correct is the transaction
that deletes a foreign owner's row and banks the double-weighted item. A single competent review,
even one explicitly looking for server-authority violations, passed both. That is the gap
Principle 6 exists to close — see `README.md`.
