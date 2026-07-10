# Adversarial findings (verifier B) — REDACTED

*The independent adversarial verifier's findings on the same diff reviewer A had passed. Verifier B
re-read the craft path and its rulings from scratch, confirmed only what it could prove, and owned
the merge recommendation. Transcribed from the merge record and the sweep log of the studio
project; identifiers neutralized per PROVENANCE.md.*

## Merge recommendation

**HOLD → merge-after-fixes.** Two server-authority holes must close with covering tests before
this can merge. Both are exploitable from the client-controlled input-id list; both survived a
review that had passed the diff.

## Finding 1 — duplicate-lot double-weighting (fabricates output value)

The craft aggregates baseline quality as the **quantity-weighted mean** of the input lots, looping
over the caller-supplied id list. The list is never deduplicated. Supplying the same lot id twice
counts that lot's `quality * quantity` **twice** into `qualityTimesQty` and its `quantity` twice
into `quantityTotal`, biasing the weighted mean toward the duplicated lot — while the consume loop
issues an idempotent `DELETE ... WHERE lot_id = @id` that removes it **once**. Net effect: an actor
crafts a higher-quality item than their real inputs justify, paying materials only once. A value
exploit reachable with a client-shaped request.

**Fix required:** reject a duplicated input id before the read+lock loop (fail closed, lot
unconsumed), with a covering integration test.

## Finding 2 — foreign-owner lot consumption (consumes another owner's inventory)

The read+lock query filters on `WHERE l.lot_id = @id` with **no ownership predicate**. Any actor
can name a lot id belonging to another owner; the query returns and `FOR UPDATE`-locks that row,
and the transaction's consume loop then deletes it. Ownership is not part of the lot's identity at
the bench, so the server authorizes an actor to destroy inventory they do not own.

**Fix required:** bind the read to the acting owner — `WHERE l.lot_id = @id AND l.owner = @actor` —
so a foreign lot reads as not-found and is left untouched, with a covering integration test.

## Disposition

Both findings were accepted. The corrected state (`04-corrected-state.redacted.diff`) adds a
pre-loop duplicate guard, the `AND l.owner = @actor` predicate, and one covering test per hole;
the suite rose from 77 to **79** passing. This is the incident recorded as **CL-009** in
`CASE-LAW.md` and cited by Principle 6 in `PRINCIPLES.md`.
