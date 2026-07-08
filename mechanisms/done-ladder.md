# The Definition-of-Done Ladder

## What it is

The done-ladder is a fixed, ordered set of evidence classes that a unit of work climbs before anyone is allowed to call it done, plus the rule for which rung gates which action. Its founding claim is one sentence: **compiles is not done.** "It builds" and "it boots clean" are the weakest possible evidence and the easiest to fake to yourself, so the ladder refuses to let either count as completion. Each rung is a strictly stronger *class of evidence* than the one below it, the merge gate and the milestone gate are pinned to specific rungs, and the evidence attached at each rung must be authentic — real output produced by the code that actually exists, not a plausible-sounding reconstruction.

## The protocol

**The five rungs (generalize the labels to your stack; the classes are invariant):**

- **L0 — Compiles / builds.** The code compiles or the artifact assembles. This is the floor, not a milestone. L0 alone is never "done" of anything.
- **L1 — Automated checks pass.** The CI suite — unit tests, linters, schema/conformance gates — is green on the change's merge ref. Evidence class: a green run on the actual ref, not a local "worked on my machine."
- **L2 — Agent-verified with authentic evidence.** The change was exercised in play or against a running instance, and concrete evidence is attached: a log excerpt, event/ledger rows, a screenshot, quoted command output. The evidence must be *real and consistent with code that exists* — re-derivable, not narrated.
- **L3 — Integration-verified.** The change was verified in the assembled integration build / the deployed environment, not just in isolation. This rung is where "works in the module" becomes "works in the whole."
- **L4 — Human saw it work.** The human lead observed the behavior directly — in play, in the editor, in the shipped path. This is ground truth and the top rung.

**The gating rules:**

1. **Merge requires L2.** Nothing merges on L0 or L1 alone. A green CI run proves L1; it does not prove the behavior is correct, only that the tests that exist passed. L2 evidence — the change doing the thing, witnessed and captured — is the merge floor.
2. **Milestone-done requires L4.** A milestone is complete only when the human has seen the milestone behavior work. L2/L3 can carry day-to-day merges; they cannot close a milestone.
3. **Evidence authenticity is part of the gate, not a courtesy.** At review, re-run the math, re-download the artifact, re-extract the screenshot. L2 evidence that cannot be reproduced from the code as written fails the rung — a well-formed but fabricated log is worse than no log.
4. **A named enforcement point with zero call sites does not count as any rung.** "Enforced in the core" is an L0 claim until you grep the call sites; a guard that exists but is never invoked is decorative, not done.
5. **Hold the tree at the rung the human's own test defines.** Do not advance a change to "merged/committed" ahead of the rung the human's verification sits at. If the human has not yet confirmed the runtime behavior, the change stays uncommitted — "compiles" and "boots clean" do not license the commit.

**How to climb, per unit:**

- Attach the DoD rung to the work item as a first-class field, and advance it only as evidence lands — do not pre-mark a rung you have not reached.
- The review pipeline checks the *claimed* rung against the *attached* evidence; a rung claim with no matching evidence is a review hold, not a rounding error.
- The top rung (L4) is stamped at a recurring human-in-the-loop ritual (a playtest / acceptance pass), not opportunistically — see `boot-shutdown.md` and the weekly rhythm.

## Why it exists

- The ladder is constitutional law in the studio project: L0→L4 with "merge requires L2, milestone-done requires L4" is a hard rule, born from the general truth that self-reported completion inflates (`studio:CLAUDE.md`, hard rule 2 "Compiles is not done").
- "No commit before end-to-end verification" is the same law earned independently in the validation project: compiling and booting clean are explicitly *not enough*, the working tree is held dirty until the human confirms the runtime behavior, and an advisor's "commit anytime" does not override the human's say on commit timing (`validation:CLAUDE.md`, no-commit-before-verification feedback rule; `validation:.claude/skills/end-session/SKILL.md` hard rules).
- Evidence-authenticity-as-part-of-review — re-download the artifact, re-extract the screenshot, re-run the math, "L2 evidence must be REAL (quoted output consistent with code that exists)" — is the review layer's own rule (`studio:docs/kb/director-handbook.md` §4).
- The "named locus with zero callers is decorative" rung-floor was earned from "enforced in the core" overclaims that a call-site grep dissolved (`studio:docs/kb/director-handbook.md` §6, the "enforced in the core" row).
- The top rung decays without ritual: the ladder is explicitly noted to rot without the recurring human-verification pass that produces L4 stamps (`studio:docs/kb/director-handbook.md` §7, the playtest ritual "the DoD ladder decays without it").
- The two-repo test is satisfied: the ladder appears independently in `studio:CLAUDE.md` (hard rule 2) and `validation:CLAUDE.md` (no-commit-before-verification), and the pipeline's ship-flagged-on-unresolved-review pattern is the same evidence-gating instinct (`pipeline:brain/phases/forensics-report.yaml`, TECHNICAL_REVIEW ships flagged rather than silently passing).

## Failure modes of the mechanism itself

- **Rung inflation.** Marking L2 because the code "should" work, without attaching the evidence. The cure is to make the rung field require the evidence artifact, not a self-attestation.
- **Fabricated evidence.** The most dangerous failure: plausible logs, invented row counts, a screenshot from a different run. This is why authenticity checking is a review step, not an honor system.
- **Green-CI-as-done.** Treating L1 as the finish line because it is the most automatable rung. CI proves only that the tests that exist passed; it says nothing about tests that should exist and don't.
- **L4 starvation.** If the human-verification ritual lapses, work piles up at L2/L3 and the top of the ladder silently stops being enforced — the ladder collapses to "merge-grade" and milestones close on weaker evidence than the law demands.
- **Decorative enforcement.** Counting a guard/gate that has no call sites as a completed rung; defeated by grepping call sites during review.
- **Commit-ahead-of-rung.** Committing on "it compiles" pressure before the human's verification, which is exactly the rung the commit was supposed to wait for.

## What varies per project

The bindings layer maps each abstract rung to concrete tooling and names: what **build/compile** means (L0), the exact **CI check set** that constitutes L1 green, what **"running instance" and evidence class** L2 accepts (log excerpt vs. ledger rows vs. screenshot), what the **integration build/deploy target** is for L3, and the **cadence and form of the human-verification ritual** that produces L4 stamps. It also declares which rung gates **merge** and which gates **milestone-done** if a project chooses different pins than L2/L4. See `bindings/TEMPLATE.md` → check names, evidence classes, integration target, and acceptance ritual.
