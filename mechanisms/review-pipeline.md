# The Review Pipeline

## What it is

The review pipeline is the ordered sequence of gates a unit of work passes before it merges, arranged so that the cheapest and most mechanical checks run first and the scarcest resource — human attention — is spent last and least. Its organizing principle is that **verification outranks generation**: the strongest configuration, the most adversarial reading, and the highest-effort model are spent on *checking* work, not on producing it. A drafting agent that is wrong is caught; a verifier that is wrong ships the bug. The pipeline exists because quality collapses by default when one actor both writes and blesses its own work, so it structurally separates the author from the gate at every stage, and it treats the final human touch as a feature decision, not a diff review.

## The protocol

**The gate sequence (cheapest/most-automatable first; each stage can only be reached if the prior passed):**

1. **Author submits with a self-checklist + evidence.** The authoring agent opens the change with its Definition-of-Done rung claimed and the L2 evidence attached (see `done-ladder.md`). No evidence, no review.
2. **Peer/lead review — the diff review.** A different actor than the author reads the actual diff for correctness, lane-fit, and law compliance.
3. **Adversarial verification — the load-bearing stage.** An independent verifier *re-reads the diff and the relevant law from scratch*, confirms only what it can prove, disputes the rest, and owns the merge recommendation. This is not a second opinion; it is a hostile re-derivation. Spend the highest-effort configuration here.
4. **Automated gates.** Compile, tests, lint, schema/conformance, hygiene — the mechanical invariants (see `deterministic-backstops.md`). These are non-negotiable and run on the merge ref, not a local tree.
5. **Human merges.** For work in the human's reserved lane, the human makes the *feature decision* — presented as a lead summary + verdict + evidence, not a line-by-line diff. Green-lane classes merge on the orchestrator's signatures without a human touch (see `lanes-and-autonomy.md`).

**Rules that make each stage earn its cost:**

- **The verifier owns the recommendation.** Adversarial verification is not advisory garnish — the verifier independently re-reads, and its "merge / hold / required-changes" call is the gate's output. Confirm only what is provable from the diff + law; a named enforcement point with zero call sites is decorative, not enforcement.
- **Calibration cheapens the verifier, never removes it.** Measured reviewer reliability (the calibration loop in `measurement/review-ledger-spec.md` §4) may make the adversarial verifier cheaper — a lower effort tier, a cheaper model, a narrower context slice, shallower sampling — but it may never remove the independent verifier or let a trusted role's self-score stand in for it, because the author/gate role boundary outranks any measured correlation.
- **Evidence authenticity is a review step.** Re-download the CI artifact, re-extract the screenshot, re-run the math. Green CI proves the automated rung only; attached evidence must be real output consistent with code that exists.
- **Coverage adequacy over coverage count.** For each law clause the change claims to honor, name the test that would *fail* if the law broke. "No gap between claimed and tested; the remaining gap is scope" is the passing grade — not a coverage percentage.
- **Inject both law surfaces into every review/verifier prompt.** The verifier gets the decision-issue layer *and* the ruling files *and* the workplan *and* the specific gate list; an under-briefed verifier confidently reports stale law (see `context-injection.md` and `two-surface-rule.md`).
- **Delta-verify before believing a fix round.** Confirm the branch head *postdates* the review verdict before trusting that "the fixes are in" — a session may have ended before the verdict posted, so "new commits" can be old ones.
- **PASS-WITH-REQUIRED-CHANGES is the normal verdict.** Small, precisely specified fixes may be applied directly by the orchestrator when no author session is live — but author-and-merger being the same hands is a *flagged* state, recorded in the merge trail with a re-verify ordered at the next boot, never a silent one.
- **The reviewer's verdict line IS the gate; don't re-score prose.** When a reviewer emits an explicit APPROVED/REJECTED verdict, that line is the decision — do not feed a well-written rejection into a second quality judge that then passes it on eloquence. On rejection, loop back to the *author* stage (re-running the reviewer on the same draft just re-rejects it), carry the rework instructions along, and cap the loop: after a bounded number of redraft attempts, **ship flagged** for human attention rather than looping forever.

**Structured output for multi-item sweeps.** When reviewing many items at once, force every reviewer and verifier to a structured schema (gate results / findings / merge recommendation) so nothing arrives as prose to re-parse; run one reviewer + one adversarial verifier per item; let independent items proceed independently (never barrier-review them on each other); spend the highest-effort configuration on the verify stages, not the drafting stages.

## Why it exists

- The pipeline shape — author PR with DoD + evidence → lead review → adversarial verification → automated gates → human merges per lane — is the operating handbook's §4 (`studio:docs/kb/director-handbook.md` §4), matching the constitution's review-pipeline section (`studio:CLAUDE.md`, "The review pipeline").
- Adversarial verification earns its cost with a receipt list: it caught "two server-authority exploits (duplicate-lot weighting, foreign-lot consumption), an inverted seam contract (percentile direction), and a guardrail that existed but was never called" — the "available, not enforced" standing category (`studio:docs/kb/director-handbook.md` §4).
- Injecting both law surfaces exists because "an advisor with only the register called three ratified decisions nonexistent" — the stale-advisor-read incident (`studio:docs/kb/director-handbook.md` §3, §5).
- Delta-verify exists because a fix round was believed when "the session had ended before the verdict posted; 'new commits' were old ones" (`studio:docs/kb/director-handbook.md` §4, the no-delta incident).
- Reviewer-verdict-as-gate + loop-to-author + ship-flagged-after-bounded-retries is the pipeline project's own design: "the technical-reviewer's explicit VERDICT: APPROVED|REJECTED line IS the gate decision — no meta-judge re-scoring the reviewer's prose (a well-written REJECTION used to pass a completeness gate)"; on rejection it loops to the *writer*, "one redraft attempt; then ship-but-flag" (`pipeline:brain/phases/forensics-report.yaml`, TECHNICAL_REVIEW gate + REPORT_DRAFTING).
- Structured multi-item review with one verifier per item and effort spent on verify stages is the orchestration guidance (`studio:docs/kb/director-handbook.md` §5).
- The human touch as a *feature decision, not a diff review* — "each PR = lead summary + advisor verdict + L2 evidence" — is the human-rhythm design (`studio:docs/kb/studio-operations.md`, evening merge-queue).
- Two-repo test: separation-of-author-from-gate with a reviewer verdict that is itself the gate appears independently in the studio handbook and the production pipeline; the validation project's "the agent drafts; the human reviews and tests — the review/test loop is the actual quality gate" is the same shape (`validation:CLAUDE.md`, operating style).

## Failure modes of the mechanism itself

- **The rubber stamp.** Adversarial verification degrades into agreeable second-opinioning; the verifier confirms rather than re-derives. The cure is forcing "prove or dispute" and making the verifier own the recommendation.
- **Stale-law confidence.** A verifier briefed with only one law surface authoritatively declares ratified decisions nonexistent. Defeated only by injecting *both* surfaces every time.
- **Fabricated-evidence pass-through.** Reviewing the claim instead of re-deriving the evidence; a fluent log passes. Authenticity checking must be an actual step, not an assumption.
- **Verdict re-scoring.** Piping a clear reviewer verdict into a downstream quality judge that overturns a correct rejection on prose quality — the exact failure the reviewer-verdict-as-gate rule was written against.
- **Infinite rework loops.** Looping author↔reviewer forever on a draft that will not converge. Bounded retries + ship-flagged is the escape valve; without the cap the pipeline hangs.
- **Author-is-merger drift.** The orchestrator applying its own required-changes and merging silently, collapsing the separation. Legal only as a *flagged* state with a re-verify ordered — never silent.
- **Barrier-review coupling.** Gating independent items on each other so one slow item holds green ones hostage. One verifier per item; merge each on its own green.
- **Coverage-count theater.** Reporting a coverage percentage instead of naming the test that would fail if the law broke — a high number that proves nothing about the specific invariant.

## What varies per project

The bindings layer declares the **concrete gate set** (which compile/test/lint/schema/hygiene checks are required and their names), **who or what fills each review role** (lead, advisor, verifier — human or agent), **which lanes merge on which signatures** (the human's reserved lane vs. green lane; see `lanes-and-autonomy.md`), the **structured-output schema** used for sweeps, and the **retry cap** before ship-flagged. The *ordering, the author/gate separation, adversarial verification, and evidence authenticity* are framework law. See `bindings/TEMPLATE.md` → gates, review roles, lane merge authorities, and retry bounds.
