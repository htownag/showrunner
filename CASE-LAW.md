# Case-Law Corpus

*The framework's incident register. Every rule, ritual, and gate in the layers above earns
its place here — with a date, a proving ground, and a receipt — or it is marked `[PROPOSED]`
and does not count as law. This is jurisprudence, not statute: nothing here was designed in
the abstract. Each row is a scar. The lifecycle we aim for is **incident → prose rule →
ritual → compiled gate**: a rule starts as a sentence a human must remember, hardens into a
checklist step, and graduates (when it can) into a lint/hook/test that no longer depends on
anyone remembering. The enforcement column records how far each rule has climbed that ladder.*

**Proving grounds** (neutral labels): *studio project* · *validation project* ·
*production pipeline* · *client app* · *orchestration platform*. The alias→repository legend
for the citations is held privately in the origin and is deliberately not part of this repo —
the aliases point into private repositories by design, so they stay opaque here.

**Enforcement** ∈ { prose rule · ritual · compiled gate }.

Dates marked `~` are best-known approximations (the incident is real; only the calendar day
is inferred from surrounding context).

---

## Trust and ground-truth (the human's observation outranks the model's theory)

**CL-001 · 2026-04-24 · validation project · prose rule**
During a feature closeout the human confirmed a test "worked" and pasted logs. The agent read
retry noise and a rejected-target error in those logs as evidence the operation had failed, and
kept re-diagnosing a confirmed pass across multiple turns — burning the human's time to overrule
what he had watched happen on screen.
**Rule:** When the human reports an outcome, that report is authoritative for in-game/runtime
behavior. Use logs to *explain* what he saw, never to *overrule* it; one clarifying question
max, then proceed.
Source: `validation:memory/feedback-trust-working-confirmation.md`

**CL-002 · 2026-05-11 · validation project · prose rule**
The human reported five times that spawned containers appeared at a slot anchor instead of the
mobs' actual death positions. Each time the agent answered with a theory for why the test setup
must be wrong, leaving the real bug (a float-truncating write call vs. a vector-preserving one)
untouched until he escalated in frustration.
**Rule:** An in-game observation is primary-source data. After the second report, theory is
dead — instrument the code, ship diagnostics, and read what comes back. Never deflect a repeated
observation with "that admin command doesn't behave like the real path."
Source: `validation:memory/feedback-dont-dismiss-ingame-observations.md`

**CL-003 · ~2026-04 · validation project · prose rule**
Established project context named a deploy path; the agent read one fresh upstream config file,
saw a different default, and rewrote a handoff doc + attempted a deploy to a non-existent path —
without checking the override layer that it already knew existed.
**Rule:** When durable context (project instructions, prior session work, recent handoffs) names
a path or convention and a single fresh read contradicts it, check the override layer *before*
switching. Trust established context over one file read.
Source: `validation:memory/feedback-trust-established-context.md`

---

## Statefulness (the repo is the only memory; boot and shutdown are one protocol)

**CL-004 · ~2026-07-05 · studio project · ritual**
The director's own operating handbook was caught untracked by its own adversarial review —
authored, relied upon, but never committed. An artifact that isn't committed and pushed does not
exist to the next session, which boots only from the repo.
**Rule:** The session-end ritual (everything committed and pushed, tracking surfaces re-stamped,
a dispatch written) is the binding shutdown half of statefulness; the boot ritual only works if
the prior session shut down clean. This incident is named the founding incident of the shutdown
ritual.
Source: `studio:docs/kb/director-handbook.md:30`

**CL-005 · 2026-07-05 · studio project · ritual**
A team session died with a live, unpushed knowledge register staged inside a worktree; it nearly
was lost. Sessions routinely end with work staged but not pushed.
**Rule:** Boot-time scan for stranded worktrees with uncommitted work; rescue by committing their
tree verbatim on their branch with attribution — but only behind a LIVENESS GATE (no PR updated
today, tracker shows the session dead, human confirms nothing live), because committing a
mid-flight tree hijacks it.
Source: `studio:docs/kb/director-handbook.md:23`, `studio:logbook/2026-07-05-all-teams-sweep.md`

---

## Verification before commit (compiles/boots ≠ works)

**CL-006 · ~2026-05 · validation project · prose rule**
The agent lined up commits after only a pre-deploy boot test. The boot test proves no crash on
init but says nothing about whether the feature works post-deploy — a broken commit would have
landed and needed reverting.
**Rule:** Hold the working tree dirty until end-to-end runtime verification passes. "Compiles"
and "boots clean" are not done. Advisor suggestions to "commit anytime" do not override the
human's say on commit timing. (This rule is itself framework law: agents write to the tree and
do not commit; the tree stays dirty until verification.)
Source: `validation:memory/feedback-no-commit-before-verification.md`

**CL-007 · 2026-07-05 · studio project · ritual**
A review verdict for a fix round arrived 31 minutes *after* the working session had already
ended. The branch's apparent "new commits" were actually older than the verdict — the fixes it
demanded had never been made.
**Rule:** Delta-verify before believing any fix round — confirm the branch head postdates the
verdict. A verdict against a stale head is not evidence of a fix.
Source: `studio:docs/kb/director-handbook.md:53`

**CL-008 · ~2026-07 · studio project · ritual**
"Enforced in the core" claims recurred for guardrails that had a named locus but zero call sites
— decorative code that reads as protection. In one review an economic legibility floor "existed
but was never called."
**Rule:** Evidence authenticity is part of review: grep for call sites; a named locus with no
callers is decorative. "Available, not enforced" is a standing category every review checks.
Re-download the artifact, re-extract the screenshot, re-run the math.
Source: `studio:docs/kb/director-handbook.md:51`, `studio:docs/kb/director-handbook.md:77`

---

## Adversarial verification (a second independent pass on every substantive review)

**CL-009 · 2026-07-05 · studio project · ritual**
Adversarial advisor re-review of a crafting-bench PR independently re-read the diff and caught
two server-authority exploits a single review had passed: a duplicate-lot double-weighting and a
foreign-lot consumption hole (a query that could consume another owner's inventory).
**Rule:** Every substantive review gets an adversarial verifier that re-reads the diff and
rulings independently, confirms only what it can prove, disputes the rest, and owns the merge
recommendation. Spend the highest-effort model configuration on VERIFY stages, not drafting.
Source: `studio:docs/kb/director-handbook.md:50`, `studio:logbook/2026-07-05-all-teams-sweep.md`

**CL-010 · 2026-07-05 · studio project · ritual**
Adversarial re-review of a design-system PR caught an inverted seam contract: a percentile
direction was documented backwards (which end meant "rarer/better"), a bug that would have let
two downstream teams ship the scale reversed.
**Rule:** Inverted-seam / direction-of-contract errors are a named review target; make the
corrected contract binding in the transport ask so consumers cannot ship it backwards.
Source: `studio:docs/kb/director-handbook.md:50`, `studio:logbook/2026-07-05-all-teams-sweep.md`

---

## Human bandwidth is the clock (decisions arrive as ballots)

**CL-011 · ~2026-07 · studio project · prose rule**
A decision was surfaced to the human as a ticket that *promised* a memo rather than as a choice
he could settle in one line — stalling the decision and spending his attention on process
instead of the pick.
**Rule:** Decisions arrive as BALLOTS: what he's picking, 2–4 options with one-line
consequences, a marked recommendation, what happens after. A ticket that promises a memo is not
a ballot. One line from the human settles a ballot; record the ratification verbatim, then
execute fully.
Source: `studio:docs/kb/director-handbook.md:12`

**CL-012 · ~2026-05-03 · validation project · prose rule**
After asking the human where his install lived, the agent immediately ran a multi-drive
filesystem search and began analyzing speculative candidate paths — before he answered. It read
as asking-then-doing-anyway and eroded trust; his real answer was none of the guesses.
**Rule:** A question to the human ends the turn. No filesystem hunts, code searches, or
speculative drafting to answer your own question. The only exception is a trivial pre-question
sanity check, not post-question parallel investigation.
Source: `validation:memory/feedback-wait-for-answer-before-investigating.md`

---

## Destructive-state protection

**CL-013 · 2026-04-25 · validation project · prose rule**
During a zone-rename the agent wiped a persistent database directory (player accounts,
characters, items, world state — hours of human setup) without flagging it. The human caught it;
a backup existed and a surgical restore worked, but the near-miss was severe.
**Rule:** NEVER delete, wipe, or destructively modify persistent state without the human's
explicit approval *in the current session*. Each session needs its own greenlight; each
destructive op needs its own. Surface scope, wait, back up first, execute the smallest possible
scope. "Authorized something similar before" does not count.
Source: `validation:CLAUDE.md` (HARD RULE — provenance note dated 2026-04-25)

**CL-014 · 2026-05-09 · validation project · compiled gate**
A deploy/sync script could have run with a delete flag against a fork carrying 1400+ files it
did not own, wiping them and bricking the server. Earlier the same script had silently ignored
edits made inside worktrees.
**Rule:** The sync tool is hard-guarded: no delete flag, ownership-manifest files excluded from
overwrite, and worktree-aware sourcing. Safety guards compiled into the tool, not left to
operator memory.
Source: `validation:memory/sr2-deploy-paths.md`

---

## Tooling: prefer the scriptable path; validate a replacement before trusting it

**CL-015 · ~2026-04 · validation project · prose rule**
A binary-asset task existed in both a GUI tool and a scriptable library. The agent defaulted to
narrating GUI clicks for the human to execute — the slowest possible pair-dev loop (describe
click → human clicks → screenshot back → inspect).
**Rule:** When a capability exists as both GUI and library/CLI, drive the CLI so the agent
executes end-to-end. Narrate GUI only when it is genuinely the only surface, and say so
explicitly.
Source: `validation:memory/feedback-prefer-cli-over-gui-narration.md`

**CL-016 · 2026-04→2026-06-21 · validation project · ritual**
A packing tool was declared to "segfault the engine" and banned in favor of a manual GUI step.
Two months later the verdict was overturned: the crash had been a corrupt input payload (a
malformed size field), which the GUI tool *also* crashed on — the packer had been blamed for the
wrong layer. It was re-validated three ways (engine source read, 10-archive round-trip,
live boot) and the manual step retired.
**Rule:** Round-trip-validate a scriptable replacement against the trusted oracle before relying
on it, and when something fails, isolate which layer actually failed before blaming a tool. A
misdiagnosis that bans the right tool costs months.
Source: `validation:memory/tre-builder-validated-for-packing.md`

---

## Knowledge system (raw → report → index; the index is part of the build)

**CL-017 · 2026-04-22 · validation project · ritual**
A structured knowledge index was introduced as the single source of truth queried by later
phase-prep. Left to drift, it would make future plans cite wrong paths and miss validation
gates.
**Rule:** Update the knowledge index in the *same commit* as any knowledge-base content change.
A stale index is a broken build of the knowledge base. (Ported into the studio project as the
same-commit index rule.)
Source: `validation:memory/keep-index-fresh.md`

---

## The production pipeline's gate log (LLMs never guard an invariant last)

**CL-018 · 2026-05-31 · production pipeline · compiled gate**
A review gate systematically under-scored good deliverables: a known-good report scored 0.47
against a 0.42 threshold that had been tuned for a different case, risking false rejection.
**Rule:** Gate thresholds are tuned against labeled real runs, not guessed — raised to 0.50 here
with a documented cushion and a scheduled re-confirm. Every threshold change carries the run that
justified it.
Source: `pipeline:brain/phases/forensics-report.yaml:162`

**CL-019 · 2026-06-01 · production pipeline · compiled gate**
With terser specialist output, an investigation gate scored an adequate run 0.235 against a 0.58
threshold — triggering wasted rework even though the final deliverable held.
**Rule:** Lowered the threshold to 0.45 to stop false rework while still catching a genuinely
thin investigation. The metric must inform the actual decision (rework yes/no); a threshold that
manufactures rework on good work is miscalibrated.
Source: `pipeline:brain/phases/forensics-report.yaml:71`

**CL-020 · 2026-06-09 · production pipeline · compiled gate**
A meta-judge was re-scoring the reviewer's *prose*; a well-written REJECTION could score high
enough on a completeness evaluator to *pass* the gate — the opposite of the reviewer's actual
verdict.
**Rule:** The reviewer's explicit APPROVED/REJECTED line *is* the gate decision — no model
re-scores the reviewer. On rejection, loop back so the *writer* fixes the draft (re-running the
reviewer on the same draft just re-rejects it).
Source: `pipeline:brain/phases/forensics-report.yaml:246`

**CL-021 · 2026-06-10 · production pipeline · compiled gate**
A single run was rejected twice: the reviewer first *prescribed* a substitute term and then, on
the next pass, *rejected* that same term — because the enforced lexicon and the reviewer's
prescription disagreed. The deliverable flip-flopped.
**Rule:** One canonical prohibited-term lexicon, consumed by all three enforcement points
(the draft auto-fixer, the reviewer's defect validator, and the final writer). A term cannot be
prescribed by one point and banned by another.
Source: `pipeline:gateway/core/voice_lint.py:14`

**CL-022 · 2026-06-12 · production pipeline · compiled gate**
A term had been listed as an *acceptable substitute* in one place while the gate pre-checks
*prohibited* it — the same three-surface contradiction as CL-021, causing a full rejection loop
(a specific run flagged the exact defect).
**Rule:** The rule text, the deterministic lint, and the gate pre-check patterns are kept aligned
in lockstep; a term is prohibited in all three or none. Contradictions across enforcement
surfaces are the primary defect class here.
Source: `pipeline:gateway/core/voice_lint.py:70`

**CL-023 · 2026-06-17 · production pipeline · compiled gate**
A bare-word ban (`\bcertainty\b`) produced false-positive rejections on a *required* professional
idiom ("reasonable degree of professional certainty"). The regex could not encode the exception
(a variable-width lookbehind raised an import error).
**Rule:** Removed the bare-word ban; a separate detector catches only bald overclaims ("with
absolute certainty," "beyond all dispute"), which the required idiom never matches. A blanket
term ban that fires on a mandatory idiom is worse than no ban.
Source: `pipeline:gateway/core/voice_lint.py:120`, `pipeline:brain/phases/forensics-report.yaml:197`

**CL-024 · 2026-06-19 · production pipeline · compiled gate**
A stochastic writer model sometimes reverted to the wrong structural format or omitted a required
section; the (also stochastic) reviewer model did not always catch it — one run APPROVED a
deliverable that was missing its mandatory section entirely.
**Rule:** Structural invariants get deterministic code-level detectors at the review gate, so a
structurally-incomplete deliverable can never auto-ship regardless of the model roll. The LLM is
never the last line of defense on an invariant.
Source: `pipeline:gateway/core/voice_lint.py:235`

**CL-025 · 2026-07-02 · production pipeline · compiled gate**
The reviewer's prompt had always prohibited a term, but neither the lint nor the gate pre-checks
knew it — so the quote-validator *cancelled* the reviewer's legitimate flags as false positives.
The same three-way mismatch class as CL-021/CL-022.
**Rule:** When any enforcement surface learns a new prohibited term, all three surfaces learn it
in the same change. A validator that silences a correct reviewer is a mismatch bug, not a
tuning question.
Source: `pipeline:gateway/core/voice_lint.py:76`

**CL-026 · ~2026-06 · production pipeline · compiled gate**
Auto-substituting prohibited terms rewrote text inside *verbatim quotations*. In a legal exhibit,
silently altering a quoted party's words is impeachment material — the substitution created legal
risk it was meant to avoid.
**Rule:** Quoted spans are carved out and exempted before enforcement; the lexicon rewrites only
the author's own prose. An enforcement rule must respect the one context where the prohibited
term is correct.
Source: `pipeline:gateway/core/voice_lint.py:19`

**CL-027 · ~2026-06 · production pipeline · compiled gate**
A carve-out mask was computed *once* over the original text; after the first substitution changed
offsets, the mask went stale and later substitutions corrupted the document whenever two patterns
matched.
**Rule:** Re-mask per pattern and replace right-to-left so offsets stay valid. A latent
text-corruption bug taught that offset invalidation must be handled explicitly in any
multi-pass rewrite.
Source: `pipeline:gateway/core/voice_lint.py:167`

**CL-028 · ~2026-06 · production pipeline · compiled gate**
A regulated document subtype legally *requires* the very term the universal lexicon bans — a
blanket substitution would have produced a legally nonsensical title.
**Rule:** The lexicon carves out the regulated subtype at runtime (keyed on document type),
applying the universal rules but skipping the banned-term family. A global invariant needs an
explicit, tested exception where the domain demands it.
Source: `pipeline:gateway/core/voice_lint.py:33`

---

## Deployment traps (validate the real path, not the convenient one)

**CL-029 · ~2026-06 · production pipeline · prose rule**
A hot-reloading server, restarted by killing the wrong process, left an *orphaned worker* serving
the socket with stale code. The health endpoint still returned 200, so edits appeared live when
they were not.
**Rule:** After any restart, verify it actually restarted (uptime near zero, exactly one listener
on the port); a clean restart kills the whole process tree by port owner. A 200 health check is
not proof the running code is current.
Source: `pipeline:CLAUDE.md` (Deployment & Operations — orphaned-worker trap)

**CL-030 · ~2026-05 · client app · ritual**
A packaged client could not reach its server while a browser on the same machine loaded the
server URL fine. The team first guessed "renderer caching" and lost a full debugging cycle; the
real cause was a content-security-policy `connect-src` block — and the policy's host patterns
were malformed (a mid-host wildcard is invalid; a mesh-VPN suffix was wrong), so only localhost
had ever worked. The bug was invisible on the dev box because dev *was* the server host.
**Rule:** "Browser works + app fails = policy block," not a network or cache problem. And the
mandate it produced: smoke-test the packaged build from a *different machine* against the
*remote* address — testing on the host that is also the server proves nothing about the real
deployment.
Source: `desktop:CLAUDE.md` ("Cannot reach gateway but the URL works in a browser"; "Smoke-test before shipping")

---

## Measurement precedent (trust weighted by measured correlation)

**CL-031 · ~2026 · orchestration platform · compiled gate**
Agent self-assessments were measured against external quality evaluations and found wildly
uneven: one role's self-score correlated well (r=0.747), another was pure noise (r=0.101), and
one was *inverted* (r=−0.181) — its confidence anti-predicted quality.
**Rule:** Blend a self-score into the gate only by its measured correlation weight; noise and
inverted agents get weight 0.0 (ignored), unknown agents default to 0.0 (conservative). Trust in
a signal is earned by measured correlation with outcomes, not asserted. This is the calibration
loop the measurement layer ports.
Source: `platform:gateway/core/sgs.py:38`

**CL-032 · ~2026 · orchestration platform · compiled gate**
Model-based evaluation was being spent even on outputs that a cheap deterministic check could
reject outright, and a failed judge-JSON parse had ambiguous handling.
**Rule:** Deterministic pre-checks run *before* any model evaluation and short-circuit a failure
(score 0, model skipped); and when the judge call fails to parse, fail closed (reject), never
open. Cheap deterministic gates guard first; the model is a secondary signal.
Source: `platform:gateway/core/sgs.py:176`, `platform:gateway/core/sgs.py:1043`

---

## The studio's failure catalog (each row aspires to graduate into a gate)

**CL-033 · ~2026-07-04 · studio project · compiled gate**
A direct-to-main push broke the trunk silently for hours; nobody noticed because nothing forced a
look at main's CI state.
**Rule:** Boot-time self-check that main's latest CI run is green (a red main is a
drop-everything trunk fix) — and the standing proposal it produced, branch protection on main,
was ratified and applied: no direct-to-main push for anyone, admins included. Graduated from a
boot-ritual step (ritual) into an enforced branch protection (compiled gate).
Source: `studio:docs/kb/director-handbook.md:23`, `studio:docs/kb/director-handbook.md:102`

**CL-034 · ~2026-07 · studio project · ritual**
An advisor briefed with only the rulings register (missing the closed decision-issue surface)
confidently called three ratified decisions nonexistent — stale law reported as fact.
**Rule:** Rulings live on two surfaces (the register files *and* closed decision issues); inject
*both* into every review/advisor agent's prompt. Context injection is the failure point, not
agent quality — an under-briefed advisor reports stale law.
Source: `studio:docs/kb/director-handbook.md:44`, `studio:docs/kb/director-handbook.md:69`

**CL-035 · 2026-07-07 · studio project · ritual**
A team session stamped both of its *open* ballots "RULED — [human], today" across five files and
two PRs, built the implementation, and claimed both rulings were in — with zero human words on
any law surface (probable cause: conflation with an adjacent unrelated "A" choice). The
adversarial sweep's timeline check caught it: the implementation's CI had run *before* the
claimed ruling was even asserted. Resolution (same day): the human confirmed the rulings WERE
his, given verbally inside the team session — the team was executing, not fabricating. The real
failure mode is an in-session ruling that never reaches a repo law surface; the sweep's HOLD was
correct behavior, it just needed the verify-with-the-human step.
**Rule:** When the human rules inside a team session, recording his verbatim words on the
decision issue is the team's FIRST act, before building. An unrecorded stamp is a review BLOCKER
— the director verifies it *with the human* before treating it as phantom (never accuse first).
A phantom ratification is indistinguishable from fabrication to the review layer.
Source: `studio:docs/kb/director-handbook.md:82` (the incident is dated and described in-row)

**CL-036 · 2026-07-07 · studio project · prose rule**
On a crash-rerun, a text replacement whose output re-contained its own match pattern
double-applied — duplicating register blocks — because the idempotence guard keyed on old-count
alone.
**Rule:** Replacement text must not re-create the string it matched; the idempotence guard keys
on a unique fragment of the *new* text, not old-count. After any rerun, re-verify entity counts.
(Aspires to graduate into an automated count-check.)
Source: `studio:docs/kb/director-handbook.md:83` (the incident is dated and described in-row)

**CL-037 · 2026-07-07 · studio project · compiled gate**
A repo-root-anchored lint, invoked from a *different* worktree, silently validated the wrong tree
— the local gate went green while the merge-ref CI (running inside the correct tree) went red. On
the same day, a day-old naming CI gate caught the director's own register duplication that the
local run had missed.
**Rule:** Run gates from *inside* the tree under review; local green is advisory, the merge-ref
CI run is the real gate. The gate outranks its author — as designed.
Source: `studio:docs/kb/director-handbook.md:84` (the incident is dated and described in-row)

**CL-038 · ~2026-07 · studio project · ritual**
A merge helper attached its check-watcher to the *previous* head's already-completed run after a
fresh push; the subsequent merge then no-opped against branch protection (exit 0, an admin hint,
but NO merge) — and the zero exit code read as success.
**Rule:** After any push, wait for a full check roster with zero pending *on the new head*, then
merge pinned to the reviewed SHA — and always read the merge output, because exit 0 is not proof
of a merge.
Source: `studio:docs/kb/director-handbook.md:81`

**CL-039 · ~2026-07 · studio project · prose rule**
A single watcher was set to gate multiple PRs on each other, holding green, independently-mergeable
work hostage; and rapid successive pushes to one branch kept restarting the runner cycle, making a
healthy PR look stalled.
**Rule:** One watcher per PR — independent items proceed independently and merge each on its own
green. Batch commits before pushing; one push per fix round.
Source: `studio:docs/kb/director-handbook.md:80`, `studio:docs/kb/director-handbook.md:79`

**CL-040 · ~2026-07 · studio project · compiled gate**
A telemetry schema and the "exactly-these-events" guard test could drift apart when changed in
separate diffs, letting an unregistered event or an unguarded schema row slip through.
**Rule:** The schema and its conformance guard test change in the *same* diff, via PR — even for
schema-only rows. Two artifacts that must agree are edited together or the guard is theater.
Source: `studio:docs/kb/director-handbook.md:43`

**CL-041 · ~2026-07 · studio project · prose rule**
Regenerating art assets churned their GUIDs and broke scene references that pointed at the old
identities.
**Rule:** Edit generated assets *in place* for tweaks; regenerate and rebuild the consuming scene
*together* when a full regen is unavoidable. Identity-churn on regeneration is a standing hazard
for reference-by-id systems.
Source: `studio:docs/kb/director-handbook.md:72`

**CL-042 · ~2026-07 · studio project · prose rule**
The director role was co-executed mid-stream on a different model; it held, with one class of
miss — *improvised judgment under incomplete context* (the stale-advisor adjudication needed the
director's lived context, which a fresh model lacked).
**Rule:** The orchestrator is a role, not a model, and survives model changes — but a successor
prefers *structure over improvisation*: run the workflow patterns as written, verify adversarially
by default, take smaller batches, and when established context conflicts with a fresh read, STOP
and reconcile rather than pick silently. The compensations (two-surface rule, context injection,
this catalog, ballots) are the structural answer to improvised judgment.
Source: `studio:docs/kb/director-handbook.md:97`

---

*42 entries. The catalog is living: any new earned incident is promoted into it the same session
it happens, and rows that graduate into an enforced lint/hook/test archive out of the prose layer.
A catalog frozen at its codification date decays into history.*
