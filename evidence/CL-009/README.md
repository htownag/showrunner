# CL-009 — pilot redacted evidence packet

*The framework's first published evidence packet. It exists to make one case-law row externally
checkable without exposing the private repository it came from. CL-009 is the flagship scar behind
[Principle 6, "Verification outranks generation"](../../PRINCIPLES.md) — the receipt that
adversarial verification is the load-bearing form of review, not an agreeable second opinion.
Every artifact here is redacted per [`PROVENANCE.md`](PROVENANCE.md); read that first to know what
transformation stands between you and the original.*

## What CL-009 claims (from [`CASE-LAW.md`](../../CASE-LAW.md))

> **CL-009 · 2026-07-05 · studio project · ritual** — Adversarial advisor re-review of a
> crafting-bench PR independently re-read the diff and caught two server-authority exploits a
> single review had passed: a duplicate-lot double-weighting and a foreign-lot consumption hole (a
> query that could consume another owner's inventory). **Rule:** Every substantive review gets an
> adversarial verifier that re-reads the diff and rulings independently, confirms only what it can
> prove, disputes the rest, and owns the merge recommendation. Spend the highest-effort model
> configuration on VERIFY stages, not drafting.

This packet proves each checkable half: **a single review passed this**, and **an independent
adversarial verifier caught these** — with the relevant redacted lines.

## The incident timeline (one morning, the studio project, 2026-07-05)

1. **Build.** A team session built the server-authoritative crafting bench: read and lock the
   input material lots, aggregate their quality, resolve the craft, then in one transaction consume
   the lots, persist the crafted item, and emit a telemetry witness. The control flow as built is
   in [`01-first-review-passed.excerpt.cs`](01-first-review-passed.excerpt.cs) — an honest
   reconstruction, since the pre-fix state was never merged and does not survive as an artifact
   (see [`PROVENANCE.md`](PROVENANCE.md)). Two server-authority holes are present in it.

2. **First review passed (reviewer A).** The build's own review gate returned **PASS-WITH-CHANGES**
   and vouched for the path: *"Core verified correct ... atomicity, persistence."* It was actively
   hunting server-authority defects on this exact diff — it caught and fixed a *third* one (a client
   buying extra tuning rounds) under the same "hard rule 4" frame — and still passed both holes. The
   verdict is in [`02-first-review-verdict.md`](02-first-review-verdict.md). Suite: 77 passing.

3. **Adversarial re-review caught two (verifier B).** An independent verifier re-read the same diff
   from scratch and returned a **HOLD**, disputing the merge with two proven server-authority
   findings ([`03-adversarial-findings.md`](03-adversarial-findings.md)):
   - **Duplicate-lot double-weighting.** The quantity-weighted quality aggregate loops over the
     caller-supplied input-id list with no dedup. The same lot id twice counts its quality twice
     into the mean while the idempotent delete consumes it once — an item crafted better than its
     real inputs justify, materials paid once.
   - **Foreign-owner lot consumption.** The read+lock query filters on `WHERE l.lot_id = @id` with
     no ownership predicate. Any actor could name another owner's lot id; the transaction locks and
     then deletes it — the server authorizing destruction of inventory the actor does not own.

4. **Resolution (same session).** Both findings were accepted and fixed before merge
   ([`04-corrected-state.redacted.diff`](04-corrected-state.redacted.diff)): a pre-loop duplicate
   guard (fail closed, lot unconsumed), the `AND l.owner = @actor` predicate on the read (a foreign
   lot reads as not-found), and one covering integration test per hole — each written so it would
   fail if its guard were removed. The suite rose 77 → **79** passing, then the work merged.

## Why this is the flagship scar

Reviewer A was competent and was *specifically* looking for client-trust / server-authority
defects — and demonstrably found one. It was not a lazy review. It still shipped two exploitable
holes, because a single pass that both reads and blesses a diff inflates toward "looks correct."
The independent adversarial pass — one that re-derives from scratch, confirms only what it can
prove, and owns the merge call — is what caught them. That asymmetry (a wrong drafter is caught
downstream; a wrong verifier *ships* the bug) is the entire argument of Principle 6, and CL-009 is
its receipt. The same lesson recurred at the governance layer three days later, when an external
adversarial review of the framework repo itself caught a constitutional conflict the internal
reviews had passed ([CL-043](../../CASE-LAW.md)).

## Contents

| File | What it is |
|---|---|
| [`README.md`](README.md) | This timeline. |
| [`01-first-review-passed.excerpt.cs`](01-first-review-passed.excerpt.cs) | The craft path as reviewer A passed it (reconstruction — see PROVENANCE.md), with the two holes marked. |
| [`02-first-review-verdict.md`](02-first-review-verdict.md) | Reviewer A's PASS-WITH-CHANGES verdict. |
| [`03-adversarial-findings.md`](03-adversarial-findings.md) | Verifier B's HOLD and the two proven findings. |
| [`04-corrected-state.redacted.diff`](04-corrected-state.redacted.diff) | The fix and its two covering tests. |
| [`PROVENANCE.md`](PROVENANCE.md) | Exactly what was redacted and by what rule. |

## What you can and cannot verify from here

You can verify the **shape** of the incident end to end: the vulnerable control flow (an honest
reconstruction, every inverted line pinned by the dated records — `PROVENANCE.md`), the passing
verdict that vouched for it (a transcription), the independent findings (a transcription), and the
corrective diff with its tests are all present and internally consistent. You **cannot** reconstruct
the source repository, its owner, the product, the team, the models, or the exact identifiers from
this packet — those are redacted by design. Per the framework's public-epistemology posture, public receipts are summaries and the
alias→repository legend is private; this packet is a summary built to preserve the proof while
withholding the identity. See [`PROVENANCE.md`](PROVENANCE.md) for the precise transformation.
