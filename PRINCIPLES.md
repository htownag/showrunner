# Principles

## What this layer is

This is the top of a three-layer framework for running a project where **one human directs
many disposable AI agents**. Below it sit the *mechanisms* (`mechanisms/`) — the operational
protocols, checklist-grade and copy-adaptable — and below those the *bindings* (`bindings/`),
where a specific project fills in its own tools, paths, and names. The principles are the layer
that survives when the protocols are re-implemented and the tools are swapped out: the
load-bearing ideas a reader should retain if they retain nothing else. Each one runs visibly
through one or more mechanisms, cited inline by relative path.

**Receipts convention.** Every principle carries one or more `CL-###` identifiers pointing to
[`CASE-LAW.md`](CASE-LAW.md), the register of real, dated incidents that earned it. Nothing here
was designed in the abstract; each principle is the generalization of a scar. A principle either
**passes the two-repo test** — the same law was earned independently in at least two of the five
proving grounds (the *studio project*, the *validation project*, the *production pipeline*, the
*client app*, the *orchestration platform*) — or it is **single-ground law**: earned from a
documented incident in one ground and adopted because the incident was decisive. Both are
legitimate law; the distinction is stated per principle so the reader knows how broadly each has
been proven. The proving grounds differ in domain — a game studio, a game-server mod, a
document-production pipeline, a desktop client, an orchestration backend — and converged on the
same rules anyway, which is the entire reason to extract them.

---

## 1. Human bandwidth is the clock

**Spend the human's attention on decisions, never on reconstruction.**

In a one-human-many-agents system the agents are elastic and the human is not: compute scales,
review bandwidth does not. The single scarcest resource in the whole apparatus is the human's
attention, so it sets the pace of everything — a studio can only ship as fast as its one human
can absorb what the swarm produced. This reframes the orchestrator's job from *maximizing agent
output* to *minimizing the human's decision cost per unit shipped*. Every decision therefore
arrives as a **ballot** — a one-line question, two-to-four options each with a one-line
consequence, a marked recommendation, and a statement of what executes on each pick — so the
human spends thirty seconds ratifying rather than an hour reconstructing an option space the
orchestrator already held. And a question posed to the human *ends the turn*: no speculative work
racing the answer, because that spends attention twice (once to ask, once to unwind the wrong
guess). Operationalized in [`mechanisms/ballots.md`](mechanisms/ballots.md) and, for merge
authority, [`mechanisms/lanes-and-autonomy.md`](mechanisms/lanes-and-autonomy.md).

**Receipts.** CL-011 (a decision surfaced as a ticket promising a memo instead of a pickable
ballot, stalling the decision and spending attention on process); CL-012 (an agent asked the
human where his install lived, then ran a multi-drive filesystem search before he answered — ask-
then-do-anyway). **Two-repo:** passes — CL-011 is studio-ground, CL-012 is validation-ground; the
same "protect the human's attention" law was earned independently in both.

**Anti-pattern it prevents.** Without it, the human becomes the bottleneck by drowning rather than
by count: agents surface open-ended "what do you think?" prompts that dump the analysis back onto
him, decisions accrete into long threads he must re-read to answer, and speculative work forks off
every unanswered question so that his eventual reply invalidates a tree of half-done work. The
studio's throughput collapses to the rate at which one person can untangle process, and the human
learns to dread opening the queue — the exact resource the system was built to conserve is the one
it burns fastest.

---

## 2. The human's observation is ground truth

**When the human reports what happened, instrument the system — never theorize the observation
away.**

The human is the only actor in the loop who touches reality directly: he sees the thing run, in
play, in the editor, on the shipped path. An agent sees logs, code, and its own priors, and a
capable model asked to reconcile a surprising report will readily generate a plausible theory for
why the human's test *must* have been wrong — which is the single most corrosive failure a
one-human-many-agents system can have, because it inverts the trust relationship and makes the
swarm gaslight its operator. The rule places the human's real-time observation at the *top* of the
trust order, above every stored surface and every model inference: his report is primary-source
data about runtime behavior; logs exist to *explain* what he saw, never to *overrule* it. One
clarifying question is allowed; after a second report, theory is dead and the only move is to
instrument the code and read what comes back. This is the apex of the trust order in
[`mechanisms/memory-trust-order.md`](mechanisms/memory-trust-order.md).

**Receipts.** CL-001 (the human confirmed a test worked and pasted logs; the agent read retry
noise as failure and re-diagnosed a confirmed pass across turns); CL-002 (the human reported five
times that containers spawned at the wrong position; each time the agent answered with a theory
for why the test setup was wrong, leaving the real float-truncation bug untouched until he
escalated). **Two-repo:** passes — the vivid incidents are validation-ground (CL-001, CL-002), and
the same law is independently constitutional in the studio project as a standing hard rule
("in-play observations are ground truth; instrument and investigate, never theorize the test was
wrong").

**Anti-pattern it prevents.** Without it, the swarm defends its model of the world against the
human's experience of the world. A reported bug is met with an essay on why the admin command
"doesn't behave like the real path," the real defect sits untouched while the human repeats
himself, and each repetition costs him more trust than the last. Eventually he stops reporting
bugs because reporting them produces argument instead of investigation — and the system loses its
only reliable signal about whether it actually works.

---

## 3. State lives in the repo, never in the model

**Because every session is disposable, boot and shutdown are two halves of one protocol.**

Any session — orchestrator or worker — can be replaced by a fresh one, or a different model, at
any instant. Nothing a session "knows" persists; only what it wrote to a durable surface does.
That single axiom forces statefulness into a two-phase ritual. **Shutdown** is the write half:
everything committed and pushed, the roadmap re-stamped, a dispatch written, memory pointers and
indexes updated — because an uncommitted artifact does not exist to the successor. **Boot** is the
read half: reconstruct the world from the repo in a fixed order (constitution, law surfaces,
trackers, newest narrative, then the commit log as ground truth), then run self-checks that catch
what drifted while no one was watching. The two are one mechanism because boot only works if the
prior shutdown was clean; a session that ends dirty silently breaks the next session's boot. The
same axiom is why work stranded in a dead session's tree must be *rescued* onto a durable branch,
and why the knowledge base's index must be updated in the *same commit* as its content — a stale
index is a broken build of the repo's memory. See
[`mechanisms/boot-shutdown.md`](mechanisms/boot-shutdown.md),
[`mechanisms/session-rescue.md`](mechanisms/session-rescue.md),
[`mechanisms/memory-trust-order.md`](mechanisms/memory-trust-order.md), and
[`mechanisms/knowledge-system.md`](mechanisms/knowledge-system.md).

**Receipts.** CL-004 (the operating handbook itself was caught untracked by its own review —
authored, relied upon, never committed; the founding incident of the shutdown ritual); CL-005 (a
team session died with a live, unpushed knowledge register staged in a worktree; it nearly was
lost); CL-007 (a fix round was believed on a branch head that predated the review verdict — the
demanded fixes had never been made). **Two-repo:** passes — earned primarily in the studio ground
(CL-004, CL-005, CL-007); the identical commit-everything-then-stamp discipline is independent law
in the validation project (its end-of-session ritual and its same-commit index rule, CL-017).

**Anti-pattern it prevents.** Without it, knowledge lives in context windows that evaporate at the
session boundary. The next session boots into a false world: it trusts a lagging tracker, misses a
ruling made yesterday, re-earns a scar already paid for, or acts on state a dead session never
committed. Work stranded in an abandoned worktree is one bad checkout from destruction, two
sessions quietly overwrite each other's state because neither checked who was live, and the
project's actual history becomes unknowable — you cannot tell what shipped from what was merely
attempted, because the record was never written down.

---

## 4. Jurisprudence, not statute

**No rule is law until an incident earns it, and every rule cites that incident.**

Rules invented in the abstract are cheap to write, cheap to ignore, and impossible to prioritize —
a hundred equally-weighted "best practices" is the same as none. This framework instead treats its
own rules the way case law treats precedent: a rule enters the corpus only when a real,
diagnosed failure earns it, and it carries the citation forever. That gives every rule three
things a decreed rule lacks: *authority* (a reader who doubts it can read the scar), *priority*
(the incidents that actually bite are the ones with rows), and a *lifecycle* — incident → prose
rule → ritual → compiled gate, so a rule climbs from "a sentence someone must remember" toward
"a check no one can forget." The living record of this is the failure catalog, whose length is
itself a health metric: a long live table means much discipline still rides on memory, a growing
archive means the system is compiling its lessons into gates. See
[`mechanisms/failure-catalog.md`](mechanisms/failure-catalog.md) and the corpus this layer sits
on, [`CASE-LAW.md`](CASE-LAW.md).

**Receipts.** CL-033 (a direct-to-main push broke the trunk silently for hours; the rule graduated
from a boot-time CI self-check into enforced branch protection — the full incident→ritual→gate
arc in one row); CL-016 (a packing tool was banned on a *misdiagnosis* that cost two months; the
lesson was to round-trip-validate against the trusted oracle and isolate which layer actually
failed before blaming a tool); CL-018/CL-019 (gate thresholds carrying the dated run that
justified each change, so touching one re-opens a known wound). **Two-repo:** passes — same-session
incident capture and the graduate-into-a-gate direction appear in the studio catalog, the
validation project's churn checklist, and the production pipeline's inline threshold comments.

**Anti-pattern it prevents.** Without it, the rulebook is a wall of undifferentiated shoulds that
no one can rank and everyone quietly overrides under pressure, because none of them visibly costs
anything to break. New sessions re-earn old scars because the lesson was never written where they
read; a rule that could have been a lint stays a prose reminder forever because nobody tracked its
graduation; and the catalog, if it exists at all, freezes into a historical document that decays
into trivia. Worse, speculative "this could break" entries dilute the real ones until readers stop
believing that a rule means "this bites" — and the whole corpus loses its authority.

---

## 5. An LLM is never the last line of defense

**Compile every invariant into a gate that fails closed; the model proposes, the gate disposes.**

A large language model is stochastic: on the wrong roll it will revert to the wrong format, drop a
mandatory section, prescribe a term it elsewhere bans, or approve a deliverable that violates a
rule it was told to enforce. Any invariant the project genuinely must not break therefore cannot
have an LLM as its final guard — "the reviewer will catch it" is not a gate, because the reviewer
is also a model and may not. The rule is to place a *deterministic* check (a lint, hook, or test
that fails closed) at the last position before an invariant could ship, and to let LLM judgment do
only what it is good at: drafting, flagging, recommending — proposing, never disposing. The
strongest form is one canonical machine-readable table of the invariant consumed at several points
(auto-fix before review, validation of the reviewer's own claims, and a final backstop at the
output boundary), with carve-outs treated as first-class citizens because real invariants have
exceptions. Fully specified in
[`mechanisms/deterministic-backstops.md`](mechanisms/deterministic-backstops.md).

**Receipts.** CL-024 (a stochastic writer omitted a mandatory section and the stochastic reviewer
approved it anyway — until a deterministic structural detector was compiled in); CL-032 (cheap
deterministic pre-checks run before any model evaluation and fail *closed* on a parse failure,
never open); CL-020 (the reviewer's explicit verdict line *is* the gate — no model re-scores the
reviewer's prose); CL-033 (a remembered rule graduating into enforced branch protection).
**Two-repo:** passes — earned in the production pipeline (CL-024, CL-020, CL-021–CL-028), the
orchestration platform (CL-032), and the studio project (CL-033 and its fail-closed lints).

**Anti-pattern it prevents.** Without it, correctness is a dice roll dressed up as a process. A
guardrail "exists in the core" but has zero call sites and enforces nothing; a well-written
rejection sails through a downstream quality judge that scores it on eloquence and passes the
opposite of the verdict; a structurally broken deliverable auto-ships because both the writer and
the reviewer happened to miss it on that run. Everyone believes the invariant is protected, the
demos all pass, and then the one output that matters violates the one rule that mattered — because
nothing deterministic ever actually stood at the door.

---

## 6. Verification outranks generation

**Separate the author from the gate, and spend the strongest configuration on checking, not
producing.**

Quality collapses by default when one actor both writes work and blesses it — self-review reliably
inflates. The structural fix is to make *checking* the privileged activity: the pipeline separates
the author from the gate at every stage, and the scarcest, highest-effort configuration (the most
capable model, the most adversarial reading, the human's own attention) is spent on verification
rather than generation. The asymmetry is the justification: a drafting agent that is wrong gets
caught downstream, but a *verifier* that is wrong ships the bug — so the verify stage carries more
consequence per token than the draft stage and deserves more resource. The load-bearing form is
**adversarial verification**: an independent pass that re-reads the diff and the relevant law from
scratch, confirms only what it can prove, disputes the rest, and *owns* the merge recommendation —
a hostile re-derivation, not an agreeable second opinion. Trust in any signal (including an agent's
own self-score) is earned by *measured correlation with outcomes*, not asserted. See
[`mechanisms/review-pipeline.md`](mechanisms/review-pipeline.md) and, for effort allocation,
[`mechanisms/context-injection.md`](mechanisms/context-injection.md).

**Receipts.** CL-009 (adversarial re-review independently caught two server-authority exploits — a
duplicate-lot double-weighting and a foreign-lot consumption hole — that a single review had
passed); CL-010 (adversarial re-review caught an inverted seam contract, a percentile direction
documented backwards, before two downstream teams shipped the scale reversed); CL-031 (agent
self-scores blended into a gate only by measured correlation weight — one role r=0.747, one pure
noise, one *inverted* — trust earned, not asserted). **Two-repo:** passes — earned in the studio
project (CL-009, CL-010), the orchestration platform (CL-031), and independently the production
pipeline (the reviewer's verdict as the gate).

**Anti-pattern it prevents.** Without it, the system spends its best resources writing and its
worst resources checking — the exact inversion. Reviews degrade into rubber stamps where the
verifier confirms rather than re-derives; the author quietly becomes the merger and blesses its
own work; the strongest model drafts a confident, subtly-wrong change and a weak model waves it
through. Exploits, inverted contracts, and decorative guardrails ship not because no one looked but
because looking was treated as the cheap step — and the one place a mistake is unrecoverable (the
gate) is the place least resource was spent.

---

## 7. The failure point is the briefing, not the agent

**A capable model handed an incomplete context is confidently wrong; assemble the context, don't
just pick a stronger model.**

The intuitive response to a bad agent output is to reach for a better model. In multi-agent work
that is usually the wrong lever: the dominant failure mode is *under-briefing*, and a strong model
with a missing surface fails more dangerously than a weak one, because it fills the gap with a
fluent, confident, wrong answer. An advisor handed only one of two law surfaces will declare
ratified decisions nonexistent; a reviewer handed no gate list will miss the gap it was dispatched
to find. The mechanism is therefore a **briefing kit** — a checklist of exactly what every
dispatched agent's prompt must carry (both decision surfaces, the relevant law slice, the
workplan, the named gate list, the evidence standard) plus a forced structured-output schema so
review results arrive machine-readable rather than as prose to re-parse. Effort goes into
assembling context and running the workflow *as written* rather than improvising — which matters
most exactly when the executing model is weaker than, or simply different from, the one the pattern
was authored on. Specified in
[`mechanisms/context-injection.md`](mechanisms/context-injection.md) and its sibling
[`mechanisms/two-surface-rule.md`](mechanisms/two-surface-rule.md).

**Receipts.** CL-034 (an advisor briefed with only the rulings register — missing the closed
decision surface — confidently called three ratified decisions nonexistent); CL-035 (a phantom
ratification: an in-session ruling that never reached any repo law surface was, to the review
layer, indistinguishable from fabrication — a briefing/recording gap, not an agent-quality one).
**Single-ground law:** earned from documented studio-ground incidents (CL-034, CL-035) and adopted
because the failure was decisive and recurring; the briefing-kit discipline has not yet been
independently re-earned in a second proving ground, so it is honestly marked single-ground rather
than two-repo.

**Anti-pattern it prevents.** Without it, teams chase model upgrades to fix what is really a
context bug. Agents are dispatched with a terse prompt and a vibe, then return confident nonsense —
stale law reported as current, gaps missed, out-of-scope work flagged as defects — and the
diagnosis lands on "the model isn't smart enough" instead of "we never told it what it needed."
Review output comes back as prose that must be re-parsed by hand, introducing drift at every hop;
the same under-briefing failure recurs across a dozen agents because the missing surface was never
turned into a checklist item — and the org spends its budget on capability it already had rather
than on the briefing it lacked.

---

## 8. Compiles is not done

**"It built" and "it boots clean" are the weakest possible evidence; doneness must be proven by
authentic, reproducible evidence.**

Self-reported completion inflates, and the easiest evidence to fake — to yourself most of all — is
that the code compiled. So the framework refuses to let compilation, or a clean boot, count as
completion of anything. Done is defined by a fixed ladder of strictly stronger *evidence classes*
(builds → automated checks green on the real merge ref → agent-verified with attached authentic
evidence → integration-verified → the human saw it work), with the merge gate and the milestone
gate each pinned to a specific rung. The load-bearing word is **authentic**: the evidence attached
at each rung must be real output, re-derivable from the code that actually exists — a well-formed
but fabricated log is worse than no log, because it launders a failure into an apparent pass. This
is why evidence authenticity is a *review step* (re-run the math, re-download the artifact,
re-extract the screenshot) and why a named enforcement point with zero call sites counts as no
rung at all. See [`mechanisms/done-ladder.md`](mechanisms/done-ladder.md).

**Receipts.** CL-006 (commits lined up after only a pre-deploy boot test, which proves no
crash-on-init but nothing about post-deploy behavior — hold the tree dirty until end-to-end
verification passes); CL-008 ("enforced in the core" claims for guardrails with a named locus but
zero call sites — decorative code reading as protection; a call-site grep is part of review).
**Two-repo:** passes — "no commit before end-to-end verification" is validation-ground law (CL-006)
and "compiles is not done" with L2-evidence-to-merge is independently constitutional in the studio
project (CL-008 and its Definition-of-Done ladder).

**Anti-pattern it prevents.** Without it, "done" means "the last thing I tried didn't error," and
the project accumulates a backlog of work that compiles and does nothing. Broken changes merge on a
green build and get reverted downstream; agents mark work complete on evidence they narrated rather
than produced, so a plausible-sounding log covers a feature that never ran; guardrails that were
never wired in are counted as shipped because the class exists in the tree. The milestone closes,
the human believes the behavior works, and the first real exercise of the code reveals that no rung
above "it compiled" was ever actually reached.

---

## 9. Autonomy is graduated by lane

**Different classes of work get different trust and different merge authority — earned, revocable,
written down, and floored absolutely at destructive operations.**

The orchestrator is not equally trustworthy across everything it can touch, and pretending
otherwise fails in both directions: treating every change as dangerous wastes the human's scarce
attention on reversible trivia, while treating every change as safe lets an agent quietly ship the
one thing only the human should decide. Work is therefore sorted into **lanes** by two questions —
how reversible is a mistake here, and how consequential is it — and each lane gets the *lightest
merge authority that is still safe*: fully reversible, low-stakes classes (docs, plans, memory,
logbook) merge on the orchestrator's review signatures; irreversible or economically/competitively
weighted classes (code, assets, taste-bearing artifacts, and the *minting* of new law) require the
human's decision or an explicit, recorded standing delegation. Autonomy is *earned and revocable*
— raised once a lane proves low-incident, lowered the moment it produces a bad merge — and every
grant is written to a durable surface, because an unwritten grant is not a grant. Beneath all lanes
sits one absolute floor: **destructive operations on persistent state are never autonomous**, under
any delegation; each needs its own same-session human greenlight, a backup first, and the smallest
surgical scope. See [`mechanisms/lanes-and-autonomy.md`](mechanisms/lanes-and-autonomy.md).

**Receipts.** CL-013 (an agent wiped a persistent database — accounts, characters, world state,
hours of human setup — during a zone-rename, without flagging it; the near-miss produced the
absolute destructive-op floor); CL-033 (branch-protection autonomy *raised* to a compiled gate only
after an explicit ballot — autonomy earned and written down); CL-019 (an internal pipeline stage
over-gated at a deliverable-grade threshold aborted the run and shipped raw output — autonomy must
match a stage's real reversibility). **Two-repo:** passes — the destructive-op floor is independent
hard-rule law in the studio and validation projects (CL-013), and graduated per-lane / per-stage
autonomy appears in the studio project and the production pipeline.

**Anti-pattern it prevents.** Without it, one of two failures is guaranteed. Either every change
waits on the human — including reversible doc edits — and the queue clogs with trivia that trains
him to stop reviewing carefully; or nothing waits on the human, and an agent merges a
competitively-weighted design decision, regenerates assets that churn every reference, or — worst —
executes a destructive wipe on the strength of a delegation that never covered it or an
authorization from a past session. Grants live only in someone's memory, so trust can be neither
audited nor revoked, and the one irreversible operation in the whole system runs without the one
confirmation that would have stopped it.

---

## 10. The orchestrator is a role, not a model

**Succession is designed for: the role survives a model change by running structure, not by
improvising judgment.**

The directing role must outlive any particular model — because models change, sessions die, and no
single context can be the seat of authority in a system built on disposable sessions. The role is
therefore defined entirely by its durable artifacts: the constitution, the handbook, the case law,
the mechanisms, the trackers. A successor — a fresh session, or a different model mid-stream —
reconstitutes the role by *reading* those surfaces, not by inheriting anyone's context. This has a
sharp operating consequence: a successor prefers **structure over improvisation**. It runs the
workflow patterns as written, verifies adversarially by default, takes smaller batches, and when
established context conflicts with a fresh read it *stops and reconciles* rather than picking
silently — precisely because the one thing a fresh model reliably lacks is the lived context that
would let it improvise well. The framework's other mechanisms (the two-surface rule, context
injection, the failure catalog, ballots) exist in part to make this substitution safe: they are
the structural answer to improvised judgment. See
[`mechanisms/boot-shutdown.md`](mechanisms/boot-shutdown.md),
[`mechanisms/context-injection.md`](mechanisms/context-injection.md), and
[`mechanisms/failure-catalog.md`](mechanisms/failure-catalog.md).

**Receipts.** CL-042 (the directing role was co-executed mid-stream on a different model; it held,
with exactly one class of miss — *improvised judgment under incomplete context*, where a stale-
advisor adjudication needed lived context the fresh model lacked; the compensation was to prefer
structure over improvisation). **Single-ground law:** earned from a single documented studio-ground
incident (CL-042) and adopted because succession is a foundational requirement of the whole model;
it is honestly marked single-ground, not two-repo, until the role is re-earned across a model
change in a second proving ground.

**Anti-pattern it prevents.** Without it, authority is seated in a context window — so when the
session ends or the model is swapped, the role does not survive: the successor either freezes for
lack of the predecessor's memory or, worse, confidently improvises against half the picture and
makes an unrecoverable call the durable record would have prevented. The system becomes silently
dependent on one continuous session that can never be replaced, which in a world of disposable
sessions means it is one timeout away from losing its own director — and the "keep the same person
in the chair" workaround is exactly the single point of failure a many-agents system is supposed to
engineer out.

---

## Editorial notes

Refinements against the workplan's ten-item seed list, with reasons:

- **Merged seeds "state lives in the repo, never the model" and "boot and shutdown are one
  protocol" into a single Principle 3.** These are one idea, not two: the boot-shutdown mechanism
  is explicitly built as "two halves of a single protocol on one axiom — state lives in the repo."
  Keeping them apart would split an axiom from its own operationalization and leave two thinner
  statements where one strong one belongs. The merged principle carries both the axiom (the
  memorable half) and the two-phase ritual (the operational half), and it becomes the principle
  above four mechanisms at once (boot-shutdown, session-rescue, memory-trust-order, knowledge-
  system), which is the right altitude for it.

- **Added Principle 2, "the human's observation is ground truth,"** which was not in the seed list.
  It earns its place independently: it is constitutional hard-rule law in the studio project *and*
  earned from vivid validation-ground incidents (CL-001, CL-002), so it passes the two-repo test;
  and it is uniquely load-bearing for *one-human-many-agents* work specifically, because it is the
  rule that stops a confident swarm from theorizing away its operator's lived experience. Omitting
  it would leave the framework silent on the single most corrosive trust failure the model has. The
  net count stays at ten (one merge frees the slot the addition fills).

- **Kept "verification outranks generation" (6) and "evidence must be authentic" (8) separate,
  though the workplan floated merging them.** They sit above different mechanisms and answer
  different questions. Principle 6 (above `review-pipeline.md`) is *organizational* — who checks,
  and with what resource. Principle 8 (above `done-ladder.md`) is *epistemic* — what standard of
  proof "done" requires. Evidence authenticity is a shared thread between them, but folding 8 into 6
  would strand the Definition-of-Done ladder — constitutional law in one ground and independently
  earned in another — with no principle above it. They are corollaries of a common instinct, not
  the same rule.

- **Two principles are marked single-ground, not two-repo:** Principle 7 (context injection /
  under-briefing) and Principle 10 (orchestrator is a role, not a model). Both were earned from
  decisive, documented studio-ground incidents (CL-034/CL-035 and CL-042) and adopted as law under
  the framework's own rule that single-ground incident-earned patterns may enter the layers. They
  are flagged honestly so a reader knows they have been proven once, hard, rather than twice,
  independently — and so a second proving ground's confirmation can be recorded when it comes.

- **No seed was dropped.** The remaining eight seeds map one-to-one to Principles 1, 3, 4, 5, 6, 8,
  9, and 10; nothing was padded to hit a count.
