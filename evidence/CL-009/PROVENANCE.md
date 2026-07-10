# Provenance and redaction record — CL-009 packet

*What stands between a reader and the original. This packet is a **redacted derivative** of the
studio project's surviving records — and its artifacts are not all of one evidentiary class. Two
are direct transcriptions of real, dated records. Two are **honest reconstructions**: the pre-fix
code state does not survive as an artifact (see below), so it is derived — mechanically and
checkably — from the surviving fixed source plus the prose records that pin exactly what was
missing. This file exists so a reader knows which is which and what was changed, and can calibrate
trust accordingly — a redaction that hides the transformation is worse than none.*

## Surviving source records (real, in the private repo, all dated 2026-07-05)

- **The team's durable build log**, which recorded the first-review verdict verbatim and the
  77-test evidence at that verdict → transcribed, under substitution, as
  `02-first-review-verdict.md`. *Transcription of a real record.*
- **The studio's all-teams sweep log row and the operating handbook's adversarial-verification
  receipt**, which recorded the two findings, the exact ownership predicate of the fix, the
  covering tests, and the 79/79 suite → transcribed, under substitution, as
  `03-adversarial-findings.md`. *Transcription of real records.*
- **The current, fixed craft-service source**, which carries the pre-loop duplicate guard, the
  ownership predicate, and the covering tests to this day → the *after* state; basis, by
  inversion, of `01-first-review-passed.excerpt.cs` and the `-` side of
  `04-corrected-state.redacted.diff`. *Real as the corrected state.*

**What does not survive, stated plainly:** the pre-fix file state and any discrete fix commit.
The work item merged as a single squashed commit *after* the adversarial findings were fixed, so
the vulnerable head never reached the mainline and its branch-side commits were not preserved.
There is no recoverable artifact of the code exactly as reviewer A passed it.

## Derived artifacts (the reconstruction rule)

`01-first-review-passed.excerpt.cs` and the `-` lines of `04-corrected-state.redacted.diff` are
**reconstructions**: the surviving fixed source with exactly the two documented guards inverted —
the pre-loop duplicate rejection removed, and the ownership predicate removed from the read+lock
query. Nothing else was altered. Every inverted line is pinned by a surviving dated prose record
that names precisely what was missing (the findings in `03` specify the absent dedup and the
absent `owner` predicate verbatim), so the reconstruction adds no degrees of freedom of its own.
The `+` side of `04`, and every non-`>>>` line of `01` that the before/after states share, are
the real source under the substitutions below.

An earlier revision of this packet presented the reconstruction as a preserved artifact, quoting
a fix-commit subject and diffstat that correspond to no surviving commit. That overclaim was
caught at director verification and corrected to this record — an evidence packet does not get to
launder a derivation into an artifact (Principle 8: a plausible fabrication is worse than no log).

## What was withheld entirely (never appears in this packet)

- The source repository name, owner, hosting URL, and file paths.
- Source commit hashes, author identity, and the pull-request / issue / work-item numbers.
- The product / franchise name and any franchise-specific vocabulary.
- All team, project, module, and internal-ruling codenames.
- Personal names, account handles, and email addresses.
- The model / agent identities of the reviewer and verifier (see substitution below).

## Substitution rules applied (identifier → neutral)

| Rule | Original class | Replaced with |
|---|---|---|
| R-proj | product / franchise name and its initialism | *"the studio project"*; removed from code |
| R-ns | source namespaces and module codenames (a franchise-initial + module codename) | `App.Persistence`, `App.Core` |
| R-schema | database schema prefix (a team codename) | `db.` |
| R-tbl | domain-flavored table/column names (materials/tiers/telemetry event) | generic: `material_lot`, `material_tier`, `tier`, `quality_cap`, `crafted_item`, `craft_resolved` |
| R-actor | the crafting-actor parameter and the owner column term | `@actor` / `actor` / `owner` |
| R-people | personal name, account handle, email of the committer | *"the director"* (who applied the fixes) / removed |
| R-agents | the reviewing agent and the adversarial verifying agent | *"reviewer A"* (the review that passed) / *"verifier B"* (the adversarial re-review) |
| R-refs | internal ruling ids, PR/issue/work-item numbers, milestone ids | generalized to *"the crafting-bench work item"*, *"a prior review"*, or dropped |
| R-stats | game-flavored stat / cosmetic field names | collapsed to neutral placeholders or elided as unrelated |
| R-fixture | test fixture item label | `"test-item"`; seed constant call sites elided as `[ ... ]` |

## Transformations that are NOT redaction (so you can trust the substance)

- **Elision, marked `[ ... ]`.** Regions unrelated to the two holes (the resolver call, the INSERT
  column list, the telemetry payload builder, test seed/probe boilerplate) are elided, not altered.
  Nothing load-bearing to either exploit was removed.
- **Annotation, marked `>>>`.** In `01-first-review-passed.excerpt.cs`, `>>>` comment blocks point
  at the two holes. These annotations are **added by this packet** and are not present in the
  original source; every non-`>>>` line is the original logic under the substitutions above,
  subject to the reconstruction rule for the two inverted guards.
- **Diff reformatting.** `04-corrected-state.redacted.diff` uses hunk headers rewritten as prose
  anchors (`@@ ... @@`) because real line numbers and file paths are withheld; the `+` body lines
  are the real change under substitution, and the `-` body lines follow the reconstruction rule.

## Faithfulness statement

The redaction preserves the full proof of CL-009: (1) the vulnerable control flow — as an honest
reconstruction whose every inverted line is independently pinned by the dated prose records, (2)
the first-review verdict that vouched for it — a transcription, (3) the two independent
adversarial findings — a transcription, and (4) the corrective state with a fail-if-removed test
per hole — real, surviving source. No claim in this packet depends on an artifact that was
withheld, and no claim rests on the reconstruction beyond what the transcribed records
independently establish. If any substitution above were reversed, the technical meaning of the
exploit and its fix would be unchanged — only the source's identity would be exposed.
