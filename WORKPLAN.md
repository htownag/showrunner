# Showrunner v0.2 Hardening — Workplan

*Authored 2026-07-10 by the review-feedback session, at the human lead's direction, in response
to an external adversarial review of the v0.1 public artifact (an independent frontier model's
full-repo read, delivered 2026-07-10) plus the first real usage evidence: the studio project's
live review ledger (18 decision rows + 16 amendment rows, 2026-07-07/08). Verdict adopted from
the review: **PASS-WITH-REQUIRED-CHANGES** — the normal verdict. This plan is the required
changes.*

## Goal

Make the framework satisfy its own law. The external review found two places where Showrunner
currently violates itself — a constitutional conflict between the review pipeline and the
calibration spec, and a measurement implementation that diverges from its spec with nothing
compiled to catch it — plus three adoption/positioning weaknesses. Real usage independently
surfaced schema gaps the review could not see. v0.2 closes the self-violations first, then the
adoption gaps, and defers new platform surface (the transport CLI) until the measurement layer
it would feed is trustworthy.

## Inputs and receipts

1. **The external review** (independent model, full-repo read, 2026-07-10). Its two checkable
   claims were verified against the tree line-by-line before this plan was written; both are
   real (see H1, H3 below). Its recommendations are adopted where they survived verification
   and amended where the framework's own law argues otherwise (see "Adjudications" and
   "Rejected as written").
2. **First real-usage ledger** (`studio:measurement/review-ledger.jsonl`, 34 rows). Evidence it
   contributes, verified by running `ledger.py check` (passes) and `ledger.py report` against it:
   - **The catch-rate divergence manifests on real data.** `code-advisor catch_rate = 100% (3/3)`
     counts a hold (RL-0006 / pr-116) whose outcome is still unknown — no amendment row exists —
     as a full catch. Spec §3.1 requires outcome consistency; the implementation requires none.
   - **The stage enum failed in the field on day one.** Real usage needed stages
     `adversarial-sweep` and `director-verification` and unit_kind `framework-deliverable`; all
     were lossy-mapped into `code-advisor`/`doc` with the mapping recorded as *prose inside
     `verdict_reason`* (e.g. RL-0001, RL-0010). Per-stage metrics now silently mix distinct
     review kinds, and the mapping is invisible to every reader that isn't a human.
   - **Cost capture is dead on arrival.** Zero real rows carry `cost_tokens_*`, `cost_usd`, or
     `wall_clock_seconds`; the report renders `tokens/merged unit = 0` and an active-review
     fraction of 0%. Metric 3.3 and the active/waiting split of 3.5 are currently theater.
   - **The schema already drifted past the spec.** Amendment rows carry `outcome_kind_note`
     (present in `ledger.schema.json`, absent from spec §1.1's field list).
   - **What works:** append-only + amendment fold held up; the false-hold pair (two CL-035
     holds, both `hold_substantiated=true`) is exactly the precision/recall pairing the spec
     designed; the dashboard honestly reports its own unknown denominator (1/18 outcomes
     back-filled, horizon sweep pending). Stage-0 discipline is functioning.

## Adjudications required before code is written

The external review's maxim was "the spec is law — don't let the implementation explain what
the spec probably meant." **That maxim is rejected as a standing rule.** The framework's own
jurisprudence applies instead: a spec/code conflict is *adjudicated*, the ruling is recorded,
and the fixture encodes the ruling. Proof it matters: on malformed ledger lines the spec is the
wrong side (see R1). Each ruling below ships as a ballot with the marked recommendation; the
fixtures in H3 are written against the ratified rulings, not against the spec as-is.

- **R1 — malformed ledger line.** Spec §2 says JSONL degrades gracefully ("one bad line is
  skipped, the rest still parse"); `ledger.py:_read_rows` deliberately raises loud. For a
  *measurement* surface, silent skipping is failing open — it corrupts denominators invisibly,
  the exact sin Principle 5 exists to prevent. **Recommendation:** `check` fails loud on any
  malformed line (compiled gate); `report` skips the line but prints a loud per-line quarantine
  count in the dashboard header, and refuses to render metrics if >X% of lines are bad. Amend
  spec §2 to say this; the "graceful skip" rationale survives only as format-resilience, never
  as silence.
- **R2 — do `hold` verdicts feed the catch numerator?** Spec §1.2 says "`hold` feeds the
  false-hold metric, `fail` feeds catch rate"; spec §3.1's formula is silent; the implementation
  counts both. Real usage argues for counting substantiated holds: both CL-035 holds were real
  law-surface defects caught by review. **Recommendation:** a `hold` row counts as a catch
  *only* when `hold_substantiated=true`; a `fail` row counts when outcome-consistent per R3.
  Amend §1.2's sentence — it was wrong as written, and the real ledger proves it.
- **R3 — outcome consistency for catches.** Spec §3.1 requires a catch be "later
  `defect_surfaced`-consistent," but a caught-and-blocked defect never merges, so
  `defect_surfaced` is *unobservable* for exactly the rows that matter — the spec's requirement
  is epistemically broken as written. The observable proxy is `hold_substantiated`.
  **Recommendation:** caught = the unit was blocked at stage S with a major/blocker finding AND
  `hold_substantiated` is `true`; rows with `hold_substantiated` null are **pending**, reported
  as a separate count and excluded from the rate (never counted as catches — the current
  implementation's behavior — and never as misses). Amend §3.1.
- **R4 — unit-level counting.** Spec §3.1 counts *units*; the implementation counts *decision
  rows*, so a rework round that repeats a finding double-counts, on both the caught and the
  escaped side. **Recommendation:** dedupe both sides by (`unit_id`, `stage`); no spec change
  needed — the spec was right, the code is wrong.
- **R5 — stage vocabulary.** The canonical stage enum stays fixed (cross-project comparability
  is the point), but real usage proves projects need their own stage names.
  **Recommendation:** add optional `stage_raw` (free string, the project's own label) alongside
  the canonical `stage`; the capture rule becomes "map to canonical, preserve raw." Same
  pattern for `unit_kind_raw`. Ratify `outcome_kind_note` into spec §1.1 while in there
  (schema-side it already exists). Schema bumps to `schema_version: 2`; v1 rows remain valid
  (new fields optional).
- **R6 — cost capture.** Decide: either the capture adapter is extended to pull token/cost
  figures from the session harness at verdict-recording time (preferred if the harness surfaces
  them), or metric 3.3 is honestly marked *not yet capturable* in the spec and the dashboard
  suppresses the misleading `tokens/merged unit = 0` line. **Recommendation:** the latter now,
  the former when a harness hook exists; never render a zero that reads as a measurement.

## Deliverables

| ID | Deliverable | Path | Wave |
|---|---|---|---|
| H1 | Constitutional amendment — the calibration boundary | `measurement/review-ledger-spec.md` §4, `mechanisms/review-pipeline.md` | A |
| H2 | Metric rulings R1–R6 ratified + recorded | ballots → spec amendments + `CASE-LAW.md` | A |
| H3 | Executable measurement conformance — golden fixtures + fixed `ledger.py` + CI gate | `measurement/tests/`, `measurement/ledger.py`, `.github/workflows/` | B (needs H2) |
| H4 | Schema v2 from real usage | `measurement/ledger.schema.json`, `measurement/review-output.schema.json`, spec §1.1 | B (needs R5, R6) |
| H5 | Minimal binding profile ("Showrunner Lite") | `bindings/MINIMAL.md`, README adoption path | B |
| H6 | Public epistemology — receipts note + one pilot evidence packet | `README.md`, `evidence/` | C (ballot-gated) |
| H7 | Transport CLI — design doc only | `mechanisms/transport-cli-design.md` | C |
| H8 | Canonical-home + downstream sync rule; studio adopts fixed tooling | `README.md` provenance note; studio repo follow-ups | C |

## Acceptance criteria

**H1 — the calibration boundary (the load-bearing fix).** Spec §4 currently says a
high-correlation role's "solo pass may clear a unit without the mandatory adversarial re-read."
`mechanisms/review-pipeline.md` says adversarial verification is framework law; Principle 6
calls it the load-bearing form. These are incompatible, and §4 loses — on the spec's *own
precedent*: the ported calibration mechanism blends self-score at a weight capped at ~0.2
(`final = (1-w)·evidence + w·self`), i.e. the source system never let a self-assessment buy out
of external evaluation, and `ledger.py`'s docstring and `_weight_from_r` cap already implement
the narrower reading. The offending sentence is the outlier. Amendment:

> Calibration may tune the verifier's effort tier, model, context breadth, and sampling depth.
> It may never remove the independent verifier, collapse author/gate separation, lower the
> done-ladder merge floor, or substitute a self-score for a compiled gate. The trust ladder
> bottoms out at "author → deterministic prechecks → cheap independent verifier" — never
> "author → author's trusted self-score → merge."

Done when: §4's example sentence is replaced; the guardrail paragraph carries the four "never"s;
`review-pipeline.md` gains one sentence making the floor explicit from the pipeline side; a new
case-law row records the incident (an external adversarial review caught a law conflict the
internal reviews passed — dated, real, and itself a vindication of CL-009's lesson at the
governance layer). New law = human lane: ships as a ballot, merges on ratification.

**H2 — rulings ratified.** Each of R1–R6 goes to the human as one ballot line with the marked
recommendation above. Done when: each ruling is recorded verbatim on the decision surface, the
corresponding spec sections are amended citing the ruling, and H3's fixture list is updated to
match. (Estimated: one ballot message, six picks, thirty seconds each — this is what ballots
are for.)

**H3 — executable conformance (the spec graduates to a compiled gate).** A `measurement/tests/`
suite, stdlib-only (`python -m unittest`), with one golden fixture ledger per metric behavior:
TRUE CATCH · SUBSTANTIATED HOLD · FALSE HOLD · PENDING OUTCOME (excluded, reported) ·
REPEATED ROUND (deduped) · ESCAPED DEFECT (unit-level) · UNKNOWN OUTCOME · MALFORMED ROW
(quarantined loud) · DANGLING AMENDMENT · MODEL CHANGE (calibration reset caveat) ·
STAGE-RAW MAPPING (v2). Each fixture asserts exact metric output. `ledger.py` is fixed to pass
them (unit-dedup both sides, hold-substantiation logic, quarantine counter, zero-suppression per
R6). A CI workflow runs the suite + `ledger.py check` on the bundled example ledger on every PR
— the framework repo gets its first deterministic gate, which is the incident→rule→gate
lifecycle applied to the framework itself. Done when: CI is green, and deliberately breaking any
ruling in `ledger.py` turns it red.

**H4 — schema v2.** Adds `stage_raw`, `unit_kind_raw`, ratifies `outcome_kind_note` into the
spec field list; `schema_version: 2`; v1 rows still validate (all new fields optional);
`review-output.schema.json` extended so capture stays a pure projection (the binding design
rule: no field that isn't already in the structured verdict). Done when: the studio's real
34-row ledger passes `check` unmodified, and a synthetic v2 row exercising every new field
passes both schemas and appears in the example ledger.

**H5 — minimal binding profile.** `bindings/MINIMAL.md`: the five-question instantiation (what
are you building; which files are human-taste territory; what must never be destroyed; what
command proves health; what are your 2–3 lanes) that expands into the smallest legal binding —
two lanes, L2 merge floor, independent verifier required, destructive-op floor absolute, one
STATUS surface, `.decisions/` + `.incidents/` as flat files. Every omitted TEMPLATE section gets
one line stating **what scar earns it** (e.g. "add the authority-per-fact-class table after your
first two-surfaces-disagree incident") — graduation into the full apparatus is the framework's
own jurisprudence applied to adoption. README's adoption path leads with MINIMAL and
demotes TEMPLATE to "the full declaration." Done when: a cold reader can instantiate a project
from MINIMAL alone in under fifteen minutes. **Not** a CLI — `showrunner init` is deferred; the
profile must prove itself as a document first, same as every other mechanism here did.

**H6 — public epistemology.** Two parts. (a) A short README section stating plainly what an
external reader can and cannot verify: public receipts are summaries; the alias→repo legend is
private by design; here is what that means for "receipts or it isn't law" externally. Honest
epistemology is cheap and ships immediately. (b) **One** pilot redacted evidence packet for a
flagship scar (candidate: CL-009 — before-diff excerpt, first-review verdict, adversarial
findings, corrected-diff excerpt, all redacted), gated by an adversarial hygiene review *of the
packet itself* before publish — redacted diffs are the highest-leak-risk artifact class this
repo could carry (identifier names and domain vocabulary survive naive redaction). Which case,
and whether to publish at all, is a human ballot; five packets only after the pilot survives.
Done when: (a) is merged, and (b) has a ballot verdict recorded — either a published packet or
a recorded decision not to.

**H7 — transport CLI, design only.** A one-file design doc for the thin briefing-kit assembler:
`boot` / `dispatch` / `collect` / `status`, assembling the relay payload (boot prompt + specific
ask + return format) from the bindings and durable surfaces — the operating model's
relay-carries-three-things rule, delivered by tool instead of by hand. Constraints stated as
law: the human still makes ballots, still sees every crossing (the CLI prints what it would have
had the human paste), and both bus modes remain supported — the doc reframes human-as-bus as
the *high-touch mode you choose*, not debt to eliminate. No implementation in v0.2: building
transport before H3 makes the gauges trustworthy would optimize throughput of a pipeline whose
instruments lie. Done when: the doc exists and names its own Stage-0/1/2 adoption path.

**H8 — canonical home + downstream sync.** This repo is canonical; the studio's vendored
`framework/` copy has already diverged (it predates the operating-model and status-page
mechanisms and still carries the extraction-era WORKPLAN/SOURCES). Done when: README states the
canonical-home rule and the sync direction (downstream copies pull from here; ledger *data*
stays project-side, never framework-side); and two studio-side follow-ups are filed there, not
here: adopt the H3-fixed `ledger.py`, and run the first **horizon sweep** at the next
integration milestone — 17 of 18 real decision rows still have unknown defect outcomes, and
that sweep is the Stage-0 exit gate that makes every catch-based metric real. The sweep's
output doubles as the first *real-data* regression fixture for H3.

## Rejected as written (from the external review, with reasons)

- **"The spec is law."** Replaced by adjudication (see above). R1 is the counterexample: the
  code's loud failure is more Showrunner than the spec's graceful skip.
- **Skip-malformed-lines as the fix for `_read_rows`.** Silent skip fails open on a measurement
  surface; quarantine-loud per R1 instead.
- **`showrunner init` in this cut.** The Lite profile ships as a document (H5); code that
  generates the document is v0.3 at the earliest, and only if the document proves insufficient.
- **Five evidence packets.** One pilot, hygiene-gated, ballot-gated (H6). The review treated
  packet redaction as straightforwardly safe; it is the riskiest artifact in the plan.
- **"Human-as-message-bus is technical debt."** Half-adopted: the CLI design (H7) removes the
  copy-paste toil, but eyes-on-every-crossing remains a documented *mode*, chosen per work
  class — the operating model already names this tradeoff correctly.

## Sequencing and authority

Wave A is law (H1, H2): ballots to the human, nothing merges without ratification, and H3 must
not start until the rulings land — fixtures encode rulings, not guesses. Wave B (H3, H4, H5) is
buildable by team sessions in parallel once A ratifies; all three merge through the standard
pipeline (author → diff review → adversarial verification → gates), and H3's CI gate should be
the first thing merged so H4 lands under it. Wave C (H6, H7, H8) is independent and low-risk
except H6(b), which is ballot-gated by design. The active-work cap applies as always: this plan
is a queue, not a burst authorization.

## Ballots — RULED 2026-07-10

All four ballots were put to the human lead and ratified in one pass. His words, verbatim:
*"open ballots, read them, go with your recommended approach on each. Launch a dynamic
workflow, assigned out to opus 4.8 max sub agents to execute the workplan, reporting back to
you for review and verification. Follow our own showrunner goals here, proceed"*
(2026-07-10, review-feedback session). Recorded here before execution, per the
ratification-recording rule. The rulings:

1. **H1 amendment text** — RULED: adopt as drafted in H1 above.
2. **R1–R6** — RULED: the marked recommendation on each of the six.
3. **H6 posture** — RULED: the epistemology note ships; one pilot packet (CL-009),
   hygiene-gated; the packet lands on the working branch only if its hygiene gate passes, and
   the merge/publish decision remains the human's at PR time.
4. **H5 defaults** — RULED: blessed as drafted (merge floor L2, verifier always independent,
   destructive-op floor absolute).

**Execution note.** Units are authored by opus-tier max-effort worker sessions under this
plan, each unit adversarially verified by an independent session (bounded rework, cap 2, then
ship-flagged), with final verification, gates, and the commit performed by the director
session. Workers write to the tree and never commit (CL-006).
