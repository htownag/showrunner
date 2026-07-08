# Lanes and Graduated Autonomy

## What it is

Graduated autonomy is the rule that **different classes of artifact get different trust levels and different merge authorities** — the orchestrator is not equally trusted to change everything, and it should not be. Work is sorted into lanes by how reversible and how consequential a mistake in that lane is, and each lane is assigned the lightest merge authority that is still safe: fully reversible, low-stakes classes (docs, plans, memory, logbook) merge on the orchestrator's own signatures; irreversible or competitively/economically weighted classes (code, assets, and anything the human has reserved as taste-bearing) require the human's decision or an explicit standing delegation. The same graduation applies to *automated pipelines*, not just repositories: a pipeline stage earns more autonomy the more its output is checkable and reversible, and the least-reversible stage keeps a human-visible flag. Lanes exist because treating every change as equally dangerous wastes the human's scarce attention on reversible trivia, and treating every change as equally safe lets an agent quietly ship the one thing only the human should decide.

## The protocol

**Sort every unit of work into a lane by two questions:** How reversible is a mistake here? How consequential (economically, competitively, or to taste) is it? Then assign the lightest safe authority.

**The lane classes (adapt the names; the trust gradient is the invariant):**

1. **Green lane — orchestrator-merges-on-signatures.** Fully reversible, low-stakes classes: docs, workplans, design briefs, logbook, memory, knowledge-base articles. These merge on the review signatures (lead + adversarial verifier) without a human touch, *provided* they still pass the automated gates on the merge ref. Batch them so the runner/human cost stays low.
2. **Recorded-decision lane — orchestrator's hands under explicit ratification.** Changes that merely *record* a decision the human already ratified (writing the ruling file, adding the register row, annotating a supersession) ride the orchestrator's hands *under the recorded ratification* — but **new law never does.** Minting a decision is always the human's; transcribing a minted decision is the orchestrator's.
3. **Reserved lane — human decides (or explicit standing delegation).** Irreversible or weighted classes: code, assets, and any class the human has claimed as taste-bearing. These merge only on the human's decision, presented as a feature decision (summary + verdict + evidence), *unless* the human has delegated in words ("merge what's ready") — and a delegation is honored only within its plain scope (see `ballots.md`). Under delegation, merge only what passed review + adversarial verification + green gates; anything short is held with its required changes posted.
4. **Human-only lane — never delegated.** Classes the human has declared theirs absolutely (e.g. the taste-bearing scene/experience files, and the minting of new design law). Agents never author these; generators may *produce* them for the human to run, but the *commit* is the human's unless authorized in words, recorded verbatim.

**Autonomy is earned and revocable, not static.** A lane's authority can be *raised* once a class has proven low-incident under review, and *lowered* the moment a lane produces a bad merge. Record every autonomy grant explicitly on a durable surface (see `bindings`); an unwritten grant is not a grant.

**Graduated autonomy for pipelines (the same idea, applied to stages):**

- An **internal/optional stage** whose output never reaches the deliverable may pass through freely (no quality gate) — over-gating an internal triage stage can abort the whole run and ship raw upstream output as the "result."
- A **deliverable-affecting stage** is gated, and the gate is calibrated to its real failure cost (a generic quality judge systematically under-scores terse-but-correct output and burns rework).
- The **least-reversible stage** (the one that finalizes the human-facing artifact) never silently self-approves: on failure it loops back to the *author* stage a bounded number of times, then **ships flagged** for a human rather than either blocking forever or passing silently.

**Absolute floor across all lanes:** destructive operations on persistent state (wiping databases, live world state, accounts, history — anything a human spent real time creating) are *never* autonomous, in any lane, under any delegation. Each destructive op needs its own same-session human greenlight; back up first; take the smallest surgical scope. A past authorization for "something similar" does not carry.

## Why it exists

- The green-lane / code-lane / scenes split is the constitution and the handbook: green-lane docs "merge on lead + advisor signatures"; "Code / assets / scenes: [the human] merges — unless he delegates in words"; "Scenes are [the human]'s … agents never write them; the commit is [the human]'s unless he authorizes it in words" (`studio:CLAUDE.md`, review pipeline + hard rule 3; `studio:docs/kb/director-handbook.md` §3).
- The recorded-decision lane is explicit: additions "that merely RECORD a [human]-ratified decision (ruling files, register rows, supersession annotations) ride the [orchestrator]'s hands under the explicit ratification; **new design law never does**" (`studio:docs/kb/director-handbook.md` §3; `studio:CLAUDE.md`, hard rule 8 "never settled below [the human], never settled twice").
- Delegation-within-scope for the reserved lane: "merge only what passed review + adversarial advisor verification + green CI; anything short gets its required changes posted and held" (`studio:docs/kb/director-handbook.md` §3).
- Autonomy is earned and written down: branch protection was *raised to a compiled gate* only after a ballot, and green-lane sign-offs are a standing proposal to make the trail queryable (`studio:docs/kb/director-handbook.md` §3, §9).
- The pipeline-autonomy gradient is the production pipeline's actual gate design: an internal triage phase set to always-pass because "the generic LLM quality judge systematically underrates a correct 1-2 sentence triage … aborted the whole pipeline … so the export shipped raw investigation output as the 'report'"; a deliverable phase gated at a cost-calibrated threshold; and the final review phase that loops to the author once "then ship-but-flag" (`pipeline:brain/phases/forensics-report.yaml`, REMEDIATION PassThrough, REPORT_DRAFTING threshold, TECHNICAL_REVIEW loop).
- The destructive-op floor is a hard rule in two grounds independently: "NEVER wipe persistent state without … explicit same-session approval … each destructive op needs its own greenlight" (`studio:CLAUDE.md`, hard rule 1) and the validation project's HARD RULE with the same protocol — stop, surface scope, wait for greenlight, back up, smallest scope, "'authorized something similar in a past chat' does NOT count" (`validation:CLAUDE.md`, HARD RULE).
- Two-repo test: graduated autonomy by artifact class appears in the studio project (green/code/scene lanes) and in the production pipeline (per-stage gate autonomy); the destructive-op floor appears in the studio and validation projects independently.

## Failure modes of the mechanism itself

- **Lane creep.** Quietly reclassifying a reserved-lane change as green to avoid waiting for the human. The reversibility/consequence test is the guard; when unsure which lane, use the more restrictive one.
- **Delegation overreach.** Reading "merge what's ready" as license for a borderline or new-decision merge. Plain scope only; anything past it is a ballot.
- **Minting-as-recording.** Dressing a *new* decision as a mere transcription so it rides the orchestrator's hands. New law is always the human's, regardless of how small it looks.
- **Static autonomy.** Never revisiting grants — neither raising trust for a proven-safe lane (wasting human attention) nor lowering it after a bad merge (repeating the incident). Grants are revocable and should move.
- **Unwritten grants.** Acting on a remembered "he said it was fine once" — an autonomy grant that is not on a durable surface does not exist, same as an unrecorded ratification.
- **Over-gating internal stages.** Applying deliverable-grade gates to an internal pipeline stage, which can abort the run and ship raw upstream output. Gate the deliverable, pass the internal triage.
- **Silent finalization.** Letting the least-reversible stage self-approve instead of looping-then-flagging. The flag is the human's window; removing it re-hides the one thing autonomy should surface.
- **Floor erosion.** Treating a prior destructive-op approval as standing, or letting a delegation "cover" a wipe. The destructive floor is absolute and per-operation.

## What varies per project

The bindings layer is where the lanes are *actually drawn*: which artifact classes are green vs. reserved vs. human-only for this project, **who holds merge authority per lane**, the **standing delegations** in force, the **autonomy-grant ledger** (what was raised/lowered and when), the **pipeline stage map** with each stage's gate policy, and — most important — the project's **destructive-op list** and its per-op greenlight protocol. The *trust gradient, the earned-and-revocable rule, the record-every-grant rule, and the absolute destructive floor* are framework law. See `bindings/TEMPLATE.md` → lanes, merge authorities, autonomy grants, and destructive-op rules, and `bindings/example-studio.md` for a fully drawn lane map.
