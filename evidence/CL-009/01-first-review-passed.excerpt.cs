// REDACTED RECONSTRUCTION — the server-authoritative craft path AS THE FIRST REVIEW PASSED IT.
// The pre-fix file state does not survive as an artifact (the work item merged squashed, after
// the fix — see PROVENANCE.md). This excerpt is the surviving fixed source with exactly the two
// documented guards inverted, per the reconstruction rule in PROVENANCE.md; every inverted line
// is pinned by the dated findings record (03). Identifiers neutralized; elisions marked [ ... ].
// The two holes are called out with >>> markers that are NOT in the original.
//
// The claim this excerpt proves: reviewer A read this exact control flow and passed it as
// "core verified correct ... atomicity, persistence" (see 02-first-review-verdict.md). Two
// server-authority holes survive in it.

namespace App.Persistence;

/// The server-authoritative bench craft path: read + lock the input lots, aggregate their quality
/// and binding tier, resolve the craft, then in ONE transaction consume the lots (the material
/// sink), persist the permanent crafted item, and write the registered telemetry witness. All
/// outcomes are computed from the server-held craft seed, never from client input.
public sealed class CraftService
{
    public async Task<CraftedItem> CraftAsync(
        Guid actor,
        string itemClass,
        IReadOnlyList<Guid> inputLotIds,
        IReadOnlyList<TuningDecision> decisions,
        long craftSeed,
        double skill,
        double facility,
        CancellationToken ct = default)
    {
        if (inputLotIds.Count == 0)
        {
            throw new ArgumentException("a craft needs at least one input lot", nameof(inputLotIds));
        }

        // >>> HOLE #1 (duplicate double-weighting): the caller-supplied inputLotIds list is trusted
        // >>> verbatim. There is NO dedup guard here. The aggregate loop below sums each id it is
        // >>> given; the consume loop deletes by id (idempotent). Pass the same lot id twice and its
        // >>> quality/quantity is counted twice into the weighted mean while it is consumed once.

        await using var conn = new NpgsqlConnection(_connectionString);
        await conn.OpenAsync(ct);
        await using var tx = await conn.BeginTransactionAsync(ct);

        // 1. Read + lock the input lots with their tier caps.
        long qualityTimesQty = 0;
        long quantityTotal = 0;
        int inputCap = int.MaxValue;
        string bindingTier = string.Empty;

        foreach (Guid lotId in inputLotIds)
        {
            await using var cmd = new NpgsqlCommand(
                """
                SELECT l.quality, l.quantity, l.tier, t.quality_cap
                FROM db.material_lot l
                JOIN db.material_tier t ON t.tier = l.tier
                WHERE l.lot_id = @id
                FOR UPDATE OF l;
                """, conn, tx);
            //  >>> HOLE #2 (foreign-owner consumption): the WHERE clause matches on lot_id ALONE.
            //  >>> There is no `AND l.owner = @actor`. Any actor can name any other owner's lot id
            //  >>> and this query returns + locks it, and the consume loop below then deletes it.
            cmd.Parameters.AddWithValue("id", lotId);

            await using var reader = await cmd.ExecuteReaderAsync(ct);
            if (!await reader.ReadAsync(ct))
            {
                throw new InvalidOperationException($"input lot {lotId} not found (harvest it before crafting).");
            }

            int quality = reader.GetInt32(0);
            int quantity = reader.GetInt32(1);
            string tier = reader.GetString(2);
            int cap = reader.GetInt32(3);

            qualityTimesQty += (long)quality * quantity;   // each supplied id contributes here...
            quantityTotal += quantity;
            if (cap < inputCap)
            {
                inputCap = cap;
                bindingTier = tier;
            }
        }

        // Quantity-weighted mean input quality, clamped to the binding (lowest) tier cap.
        int itemQuality = (int)Math.Clamp(qualityTimesQty / Math.Max(1, quantityTotal), 1, inputCap);

        // 2. Resolve the craft server-side (shared distribution model; the output clamp holds).
        var (stats, band, flawCount, marked) = /* [ resolver call — unrelated to the holes ] */ default;

        // [ ... construct the crafted item ... ]

        // 3. Consume the input lots — they become the item (the material sink).
        foreach (Guid lotId in inputLotIds)
        {
            await using var del = new NpgsqlCommand(
                "DELETE FROM db.material_lot WHERE lot_id = @id;", conn, tx);   // ...but is deleted once here.
            del.Parameters.AddWithValue("id", lotId);
            await del.ExecuteNonQueryAsync(ct);
        }

        // 4. Persist the permanent crafted item.   [ INSERT ... — unrelated to the holes ]
        // 5. Emit the registered, shape-gated telemetry witness.   [ ... ]

        await tx.CommitAsync(ct);
        return item;
    }
}
