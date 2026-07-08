# Knowledge System — raw → report → index

## What it is

A three-tier discipline for turning session exhaust into durable, queryable project knowledge without letting the knowledge base rot. Unprocessed captures (logs, transcripts, research dumps) land in a **raw** tier that is never cited directly; distilled **reports** are synthesized from raw and are the only citable surface; a machine-readable **index** enumerates every report with controlled tags and a freshness state. Alongside sit two lighter stores: **memory** (single-fact files with YAML frontmatter, surfaced through a one-line-per-entry index) and a **logbook** (dated retrospectives). The binding invariant is that the index is updated in the *same commit* as any content change — a stale index is a broken build of the KB. This system was proven over roughly five months of shipped phases in the validation project before being ported wholesale into the studio project; it is not a fresh idea, it is a survivor.

## The protocol

1. **Three content tiers, one-directional flow.**
   - Raw captures go to a `raw/` area. Raw is *never cited* by any deliverable — it is provenance, not reference. Distill it, then cite the distillate.
   - Synthesized reports (one topic/subsystem per file) are the citable layer. Each report records what it was `derived_from` (the raw sources) so provenance survives even after raw is pruned.
   - A machine-readable index (one entry per report) carries: path, kind, one-line summary, controlled tags, and a per-file freshness state + last-verified date.
2. **Same-commit index rule (the load-bearing one).** Any addition, edit, or deletion of KB content updates the index *in the same commit*. Bump the index's `last_updated`. CI or review may enforce this; at minimum it is a stated rule with an owner. A KB change that ships without its index change is a defect, not a follow-up.
3. **Controlled tag vocabulary.** Tags come from a short, enumerated list at the top of the index. Add a new tag only when two or more entries need it — casual tag minting fragments queryability. Freshness is itself an enumerated field (e.g. `fresh` / `aging` / `stale` / `unverified`), each with a written definition tied to a verification date.
4. **Memory tier — single-fact files.** Durable single facts (a gotcha, a path, a collaboration rule, a decided convention) become their own small file with YAML frontmatter (name, description, type, origin). A separate index file holds one line per fact, hard-capped short (e.g. <200 chars); detail lives in the named file, never in the index line. Keep the index line a pointer, not a summary.
5. **Logbook tier — dated retrospectives.** Session/weekly retrospectives and dispatches, low ceremony (date + bullets). This is the narrative layer the next boot reads first; it is not a substitute for memory or reports.
6. **Fail closed on format drift.** Parsers that read these surfaces (index, register, memory index) must treat "zero entries parsed" as a failure, not an empty pass — a renamed block or broken format should turn the gate red, not silently green.
7. **Freshness is re-stamped, not assumed.** When a source a report was built from drifts (a symbol moved, a path renamed), flip its freshness to `stale` and record why. A report that is never re-verified does not stay `fresh` by default.

## Why it exists

- The system's own provenance is the strongest receipt: `studio:CLAUDE.md` ("Knowledge system (raw → report → index)") states it was **ported from the validation project, which proved it over five months of shipped phases** — adoption was earned by a track record, not asserted.
- The same-commit index rule is written into the machine-readable manifest itself: `validation:docs/knowledge-base/INDEX.yaml` (`maintenance_rule`: "Update this file in the SAME commit as any addition or change… Bump last_updated") and reinforced as a durable rule in `validation:CLAUDE.md` ("update in the same commit as any KB content change").
- The controlled vocabulary and freshness states are concrete in `validation:docs/knowledge-base/INDEX.yaml` (`tag_vocabulary`, `freshness: [fresh, aging, stale, unverified]`, and the instruction "keep this short. Add terms only when two+ entries need them").
- The single-fact memory format with a short index line is codified in `studio:CLAUDE.md` ("single-fact files with YAML frontmatter; one-line entries (<200 chars)") and `validation:CLAUDE.md` ("Keep MEMORY.md entries to one line under ~200 chars; detail goes in named topic files").
- Fail-closed-on-drift is demonstrated in `studio:tools/naming_register_check.py` ("zero entries parsed - format drift… Failing closed") — the same defensive posture the index parsers take.

## Failure modes of the mechanism itself

- **Silent index staleness.** The index and content drift apart when the same-commit rule is treated as aspirational. The countermeasure is a gate that diffs content changes against index changes; absent that, it is the single most common way this system decays.
- **Raw cited directly.** Under time pressure an agent cites a raw capture instead of distilling it, and the citation rots when raw is pruned. Enforce "raw is never cited" as a review check.
- **Memory-index bloat.** One-line entries grow into paragraphs; the index stops being scannable. The size cap must be enforced, and detail pushed back into the named file.
- **Freshness theater.** Everything stays `fresh` forever because re-verification never happens. Freshness is only meaningful if `stale`/`aging` transitions actually get made when sources drift.
- **Tag sprawl.** New tags minted per-entry destroy the query surface the vocabulary exists to provide. Gate additions on the two-entries-minimum rule.
- **Report/raw provenance loss.** Distilling a report and then deleting raw *without* recording `derived_from` severs the audit trail. The report must name its sources before raw is pruned.

## What varies per project (bindings)

The tier directory paths; the index file format and its exact field names; the enumerated tag vocabulary (wholly project-specific); the freshness-state names and their day thresholds; the memory index-line character cap; whether the same-commit rule is CI-enforced, hook-enforced, or review-enforced; and which additional stores exist (per-team mirrors, dispatch logbooks). Declare these in the project's bindings file — the *shape* (three one-directional tiers + same-commit index + single-fact memory + fail-closed parsing) is the mechanism; the names and paths are bindings.
