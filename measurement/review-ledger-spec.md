# Measurement Spec — The Review Ledger & Calibration Loop

*Design only. No implementation. This spec defines the missing quantitative half of the
framework's improvement loop: the framework already turns incidents into rules (qualitative),
but nothing measures whether the review pipeline actually catches defects, whether it over-blocks,
what it costs per merged unit, or whether the failure catalog reduces repeat incidents. The
ledger records one structured row per gate decision; the metrics read those rows; the calibration
loop feeds measured reviewer reliability back into how much a reviewer's self-assessment is
trusted at gate time.*

## What this ports, and from where

The precedent is the orchestration platform's Synchronized Gate System. Two artifacts are lifted:

1. **The per-decision diagnostic record.** The platform already emits one structured record per
   gate evaluation (`platform:gateway/core/phase_models.py:76-95`, `GateDiagnostic`: gate id, run
   id, stage, verdict, score, per-agent scores, evidence, evaluator tokens/cost, timestamp) and
   persists it append-style to a per-run repo file (`platform:gateway/core/phase_engine.py:1276`,
   `_persist_phase_result`). The review ledger is that same idea lifted from the automated
   phase-gate layer up to the human/agent PR-review layer, and extended with the one field the
   platform lacks: **outcome-after-merge** (the platform's gate decision is terminal within a run;
   a studio review decision has a life after merge that only becomes knowable later).

2. **Self-score correlation weighting.** The platform measures, per agent-role, the empirical
   correlation between the agent's self-score and an external quality evaluation, then blends the
   self-score into the gate score by a weight derived from that correlation
   (`platform:gateway/core/sgs.py:38-46` — `SELF_SCORE_CALIBRATION`: researcher r=0.747→weight
   0.15, analyst r=0.614→0.12, fact-checker r=0.556→0.10, writer r=0.101 *noise*→0.0,
   game-researcher r=-0.181 *inverted*→0.0; blend at `platform:gateway/core/sgs.py:85-135`,
   `final = (1-w)·evidence_score + w·self_score`; unknown roles default to 0.0). The studio's
   external truth is richer than the platform's synthetic evaluator: it is the ledger's
   back-filled outcome-after-merge (did a defect actually surface?). That makes the correlation a
   measurement of real reviewer reliability, not agreement with another model.

The studio side the ledger records: the review pipeline
(`studio:docs/kb/director-handbook.md` §4 — subagent PR → lead review → advisor gates → automated
gates → merge per lane; verdicts include PASS-WITH-REQUIRED-CHANGES as the normal outcome), the
done-ladder L0–L4 (`studio:CLAUDE.md` hard rule 2 — L0 compiles, L1 CI green, L2 agent-verified
with evidence, L3 integration build, L4 human saw it work; merge requires L2), and the living
failure catalog whose efficacy is the whole point (`studio:docs/kb/director-handbook.md` §6 the
catalog, §7 "the failure catalog is LIVING").

---

## 1. The ledger row

**Granularity.** One row per *gate decision*: a single verdict rendered by one reviewing actor at
one pipeline stage on one unit, in one rework round. A unit that passes cleanly through the
pipeline produces several rows (one per stage); a unit that reworks produces more (stage × round).
Rows are grouped by `unit_id`; a full unit's history is all rows sharing it.

**Write-once vs knowable-later.** Every field except the `outcome_*` group is written at decision
time and never mutated. The `outcome_*` group is unknowable at decision time and is supplied later
by the back-fill protocol (§1.3). Append-only integrity is preserved by writing outcomes as a
*separate amendment row* keyed to the original `ledger_id` (§2), never by editing the original.

### 1.1 Field list

| Field | Type | Allowed values | Written by | When |
|---|---|---|---|---|
| `ledger_id` | string | stable unique, e.g. `RL-<seq>` or uuid | capture adapter | at decision |
| `schema_version` | int | ≥ 1 | capture adapter | at decision |
| `unit_id` | string | PR number / branch / task id | from review context | at decision |
| `unit_kind` | enum | `code` `spec` `asset` `doc` `pack` `config` | from review context | at decision |
| `lane` | string | project's lane/team label (neutral role, not a codename) | from review context | at decision |
| `stage` | enum | `subagent-self` `lead-review` `design-advisor` `code-advisor` `automated-gate` `merge` `human-final` | capture adapter | at decision |
| `round` | int | 0 = first pass, 1+ = rework round | capture adapter | at decision |
| `reviewer_role` | string | neutral role label (`lead`, `advisor`, `director`, submitting subagent role) | capture adapter | at decision |
| `reviewer_model` | string \| null | model/tier label; null for deterministic gates | capture adapter | at decision |
| `reviewer_effort` | enum | `low` `medium` `high` `max` `deterministic` | capture adapter | at decision |
| `timestamp` | string | ISO-8601 UTC | capture adapter | at decision |
| `verdict` | enum | `pass` `pass-with-required-changes` `fail` `hold` | reviewing actor | at decision |
| `verdict_reason` | string \| null | short coded/free reason | reviewing actor | at decision |
| `findings_count` | int | ≥ 0 | reviewing actor | at decision |
| `findings_by_severity` | object | `{blocker:int, major:int, minor:int, nit:int}` | reviewing actor | at decision |
| `finding_ids` | array\<string\> | stable per-finding ids (for later cross-reference) | reviewing actor | at decision |
| `evidence_claimed` | enum | `L0`–`L4` (done-ladder) | from submitter/prior stage | at decision |
| `evidence_verified` | enum \| null | `L0`–`L4`; null if this stage did not re-verify | reviewing actor | at decision |
| `cost_tokens_in` | int | ≥ 0 | capture adapter | at decision |
| `cost_tokens_out` | int | ≥ 0 | capture adapter | at decision |
| `cost_usd` | float \| null | ≥ 0 | capture adapter | at decision |
| `wall_clock_seconds` | float \| null | active review duration for this stage | capture adapter | at decision |
| `outcome_kind` | enum | `outcome` (marks an amendment row) | back-fill ritual | later |
| `outcome_ref_ledger_id` | string | the `ledger_id` this outcome amends | back-fill ritual | later |
| `merged` | bool \| null | did the unit merge | back-fill ritual / merge stage | at merge |
| `merge_timestamp` | string \| null | ISO-8601 UTC | merge stage | at merge |
| `defect_surfaced` | bool \| null | did a defect attributable to this unit surface post-merge | back-fill ritual / horizon sweep | later |
| `linked_incident_id` | string \| null | id of the later incident (case-law / catalog / issue) | back-fill ritual | later |
| `escape_stage` | enum \| null | which stage *should* have caught it | back-fill ritual | later |
| `hold_substantiated` | bool \| null | for `hold`/`fail` rows: did the block prove real | back-fill ritual | later |
| `outcome_backfilled_at` | string \| null | ISO-8601 UTC | back-fill ritual | later |

### 1.2 Notes on the load-bearing fields

- **`verdict`** separates `fail` (substantive reject — a real defect) from `hold` (blocked pending
  external input or an unverifiable claim — no substantive defect asserted). The distinction is not
  cosmetic: `hold` feeds the false-hold metric, `fail` feeds catch rate. The studio has a real
  false-hold on record — two *sound* PRs held on an unrecorded ruling stamp
  (`studio:docs/kb/director-handbook.md` §6, the phantom-ruling row) — which is exactly a `hold`
  that later resolved `hold_substantiated=false`.
- **`evidence_claimed` vs `evidence_verified`** are both done-ladder levels. Evidence inflation is
  `claimed > verified`. `evidence_verified` is null when the stage did not independently re-check
  (a lint gate does not re-run the human's screenshot); it is only meaningful when the stage
  actually re-verified per §4's "evidence authenticity is part of review."
- **`escape_stage`** attributes a post-merge defect to the earliest stage that had the information
  to catch it. It is the denominator hinge for catch rate and is a judgment call — flagged as a
  failure mode in §3.

### 1.3 Back-fill protocol (the outcome group)

The `outcome_*` fields are knowable only after merge, so they cannot be written at decision time
without leaving the denominator of every catch-based metric permanently unknown. The protocol:

1. **At merge.** The merge-stage row (or an amendment row) sets `merged`, `merge_timestamp`.
2. **On any later incident.** The framework already logs earned incidents into the failure catalog
   and case-law the session they happen (`studio:docs/kb/director-handbook.md` §7 "promoted... the
   same session it happens"). Extend that existing ritual by one step: when an incident is logged,
   find the ledger row(s) for the unit that introduced it (join on `unit_id`) and append an
   `outcome` amendment row setting `defect_surfaced=true`, `linked_incident_id`, `escape_stage`.
3. **The absence case (critical).** "No defect surfaced" must be recorded *affirmatively*, or catch
   rate has no denominator (a null is not a clean unit — it is an unknown one). A periodic **horizon
   sweep** finds merged units older than a horizon with no linked incident and appends an `outcome`
   row setting `defect_surfaced=false`. The horizon is a project binding; the natural choice is the
   next integration build / milestone review (done-ladder L3/L4, when the human has exercised the
   merged work) — past L4 with no incident is the strongest "clean" signal the framework produces.
4. **Hold resolution.** When a held/failed unit later merges essentially unchanged for that finding,
   append `hold_substantiated=false`; when it merges only after the finding was addressed,
   `hold_substantiated=true`.

The back-fill rides an existing ritual (incident logging) plus one cheap periodic sweep; it adds
no per-decision manual step.

---

## 2. Storage and capture

**Format: JSONL (one JSON object per line, append-only), recommended.** Rationale against the
alternatives:

- **vs CSV** — the row has nested fields (`findings_by_severity`, `finding_ids[]`); CSV forces a
  lossy flatten-and-escape. Rejected.
- **vs YAML** — a single malformed row breaks parsing of the *whole document*; append means
  hand/agent-written edits, so malformed rows are a when-not-if. JSONL degrades gracefully — one
  bad line is skipped, the rest still parse. Rejected.
- **JSONL wins** on three counts that matter to this framework specifically: (a) **append is a pure
  line-add**, so two concurrent sessions never conflict on existing rows and the git diff is
  additions-only — this fits trunk-based development and "state lives in the repo"; (b) nested
  fields are native; (c) it is the same shape the platform already persists per gate
  (`platform:gateway/core/phase_engine.py:1276`), so the port is faithful.

**Append-only + knowable-later, reconciled.** Outcomes would seem to require mutating an old row,
which breaks append-only. They do not: outcomes are written as *separate amendment rows*
(`outcome_kind="outcome"`, `outcome_ref_ledger_id=<original>`). The metrics reader folds amendment
rows onto their base rows at read time. The file stays strictly append-only; history is never
rewritten (event-sourced, like the platform's incremental progress file).

**Location.** `<repo>/measurement/review-ledger.jsonl`, checked in. It is durable repo state that
travels with the project on promotion, versioned like the logbook and memory surfaces the boot
ritual already reads. The derived metrics are computed at read time and are **not** stored as
source of truth — the same discipline the platform states for its SQLite ("Not the source of
truth — derived from brain files", `platform` project overview).

**Capture must be a byproduct, never a step.** The framework already mandates that review and
advisor agents emit **structured** output — "a JSON schema of gate_results / findings /
merge_recommendation, so nothing arrives as prose to re-parse"
(`studio:docs/kb/director-handbook.md` §5). The ledger row is a *projection* of that structured
verdict. The capture adapter runs at the one moment the director already records a verdict (posting
the merge trail / advisor signature) and serializes the already-structured object into a ledger
line. **Binding design rule: every decision-time ledger field must map 1:1 onto a field the review
agent already emits in its structured output.** If capture ever requires re-typing something not
already in the structured verdict, it will rot and the whole measurement effort dies — so the field
names above are chosen to be the review-agent schema, minus the back-filled `outcome_*` group. This
is why the deterministic/automated gates (which emit machine output already) and the model reviewers
(which emit structured JSON already) both capture for free.

---

## 3. The metrics

Each metric: definition (formula over ledger fields), the decision it informs, its failure mode as
a metric. The framework's rule is applied ruthlessly — cut metrics are named in §3.7.

### 3.1 Reviewer catch rate (per stage / per reviewer role)

- **Definition.** `catch_rate(S) = caught(S) / (caught(S) + escaped(S))`, where `caught(S)` = count
  of units where stage S raised a `major`/`blocker` finding on a real defect (later
  `defect_surfaced`-consistent), and `escaped(S)` = count of merged units with `defect_surfaced=true`
  and `escape_stage == S`. Computed over a window, per `stage` and per `reviewer_role`.
- **Decision.** Where to spend the strongest model/effort configuration, and which stage to cut.
  Operationalizes "verification outranks generation, gets the strongest configuration" and "spend
  the highest-effort configuration on VERIFY stages" (`studio:docs/kb/director-handbook.md` §5) with
  *evidence* instead of a flat rule: a low-catch, high-cost stage is a candidate to upgrade
  (`reviewer_model`/`reviewer_effort`) or restructure; a stage that never catches anything is a
  candidate to cut.
- **Failure mode as a metric.** (a) The denominator depends on `escape_stage` attribution, which is
  a judgment call — misattribution silently moves catch rate between stages. (b) **Gameable**: a
  reviewer raises apparent catch rate by flagging trivially; catch rate must never be read without
  false-hold beside it (recall is meaningless without precision). (c) **Survivorship** — latent
  defects that no stage caught and that never surfaced are invisible; the metric measures
  caught+surfaced, not the true defect population.

### 3.2 False-hold rate (per stage / per reviewer role)

- **Definition.** `false_hold_rate(S) = holds_and_fails_unsubstantiated(S) / all_holds_and_fails(S)`,
  where the numerator counts `hold`/`fail` rows at S with `hold_substantiated=false` (the unit later
  merged without substantively addressing the finding).
- **Decision.** Whether a stage over-blocks. Over-blocking spends the scarce resource — the human's
  clock — and slows merge; high false-hold means loosen or clarify the stage's hold criteria, and is
  a signal to *lower* that role's calibration weight. The studio's phantom-ruling incident
  (`studio:docs/kb/director-handbook.md` §6) is a recorded false hold with a concrete cause (missing
  trail), exactly the class this metric surfaces.
- **Failure mode as a metric.** (a) "Substantively unchanged" is a judgment call — a true hold that
  needed a one-line fix can be miscoded as false. (b) **Gameable in reverse**: a reviewer drives
  false-hold to zero by never holding, collapsing catch rate — so this and catch rate are a
  precision/recall pair and are only meaningful read together.

### 3.3 Cost per merged unit

- **Definition.** `sum(cost_usd or cost_tokens across all rows for merged units) / count(merged
  units)`, over a window, optionally bucketed by `unit_kind`. A parallel `wall_clock` variant sums
  `wall_clock_seconds`.
- **Decision.** Is the review apparatus affordable per unit of throughput, and which stage dominates
  cost (→ move that stage to a cheaper model or a deterministic gate). Directly informs the runner-
  cycle economics behind PR batching (`studio:docs/kb/director-handbook.md` §7).
- **Failure mode as a metric.** (a) Cost-per-*merged* unit ignores spend on units that failed or
  were abandoned — a pipeline can look cheap per merge while burning budget on rejects; pair with
  cost-per-attempt. (b) Cheapness is not the goal — driving it down by cutting verification raises
  escape rate; only meaningful beside catch rate. (c) Token cost and the human's clock diverge — per
  "human bandwidth is the clock," token cost can look fine while time-to-merge is the real
  bottleneck.

### 3.4 Repeat-incident rate (failure-catalog efficacy — the central metric)

- **Definition.** Requires a **join** from ledger outcome rows to failure-catalog entries. Each
  incident, when logged, is tagged with the catalog entry (signature) it instantiates, or `novel`
  if it is a new class; that tag is carried on `linked_incident_id` (or a companion signature field
  on the catalog side). For a catalog entry `C` codified at date `D_C`:
  `repeat_rate(C, window) = count(outcome rows after D_C whose incident matches C's signature) /
  count(units merged after D_C in C's lane)`. Track the series over time and across C's graduation
  from prose rule → compiled gate.
- **Decision.** *This is the quantitative half the framework was missing.* It informs (a) **which
  catalog entries to graduate** into a lint/hook/test — a repeat rate that does not decline under
  prose enforcement is an entry that needs a compiled gate (the failure-catalog lifecycle rule:
  "every row aspires to graduate into a lint/hook/test"); and (b) **which graduated gates to trust
  enough to archive** — a repeat rate that goes to zero after graduation is a proven gate whose row
  can archive out. Without this metric, the incident→rule loop is asserted to work but never
  measured.
- **Failure mode as a metric.** (a) **Signature matching is fuzzy** — over-broad signatures merge
  distinct root causes (hiding repeats), over-narrow signatures never match (every incident looks
  `novel`, repeat rate sits at ~0 and *falsely declares victory*). (b) **Low base rates** — rare
  classes have too few post-codification samples to conclude anything; zero repeats over three
  merges is not proof. (c) **Gaming at logging time** — relabeling a repeat as `novel` makes the
  loop look effective while the same bug recurs.

### 3.5 Time-to-merge

- **Definition.** `merge_timestamp − timestamp(first review row for the unit)`, per unit; report
  median and p90 over a window, by `unit_kind`. Split **active review time** (sum of
  `wall_clock_seconds`) from **waiting time** (elapsed minus active).
- **Decision.** Is pipeline latency spending the human's clock well, and which stage/gap is the
  bottleneck (informs batching cadence and whether a stage stalls). Ties directly to "human
  bandwidth is the clock."
- **Failure mode as a metric.** (a) Dominated by waiting-on-the-human, which is outside the
  pipeline's control — a long time-to-merge during a human's multi-day absence
  (`studio:docs/kb/director-handbook.md` §7) is not a pipeline problem, which is why active/waiting
  must be split. (b) Optimizing it directly incentivizes rubber-stamping — trades against catch
  rate. (c) A few long-tail units dominate the mean — use median/p90.

### 3.6 Evidence-inflation rate (per submitting role / per stage)

- **Definition.** `inflation_rate = count(rows with evidence_claimed > evidence_verified) /
  count(rows with both fields set)`, grouped by the submitting `reviewer_role`/`stage`.
- **Decision.** Whether a submitting role habitually overclaims its done-ladder level (→ tighten its
  briefing, require the artifact attached, and *lower its calibration weight*). Serves hard rule 2
  ("compiles is not done") and §4 evidence authenticity — a role with high inflation is precisely
  where "L2 evidence must be REAL" is being violated.
- **Failure mode as a metric.** (a) `evidence_verified` is capped by what the reviewer bothered to
  check — a lazy reviewer sets verified=claimed and inflation reads zero not because submissions are
  honest but because nobody looked; low inflation is confounded between good submitters and lazy
  verifiers, so pair with catch rate. (b) Asymmetric — catches over-claiming only, and only when the
  reviewer independently re-verifies.

### 3.7 Metrics considered and CUT (the ruthless rule applied)

- **Raw findings-count / findings-per-review volume** — tempting as "reviewer productivity," but
  informs no decision: a high count is equally consistent with a thorough reviewer and a nitpicky
  one, with buggy code and clean code. Kept only as an *input* to severity-weighted catch rate;
  cut as a standalone metric.
- **Pass rate (fraction of reviews that pass)** — a rising pass rate is ambiguous by construction
  (better submissions or a softening gate?), so it points to no action. The actionable signal is
  already carried by catch rate + evidence-inflation. Cut.
- **Mean gate score** — the platform emits a 0–1 score, but the studio verdict is categorical
  (`pass`/`PWRC`/`fail`/`hold`); a mean over an ordinal scale is a fabricated aggregate that informs
  nothing the verdict distribution doesn't. Does not port. Cut for the studio ledger.
- **Inter-rater reliability / reviewer agreement** — the studio runs one reviewer + one adversarial
  verifier per item, not redundant raters at scale, so no decision hangs on agreement statistics at
  this size. Cut; revisit only if multiple independent reviewers per unit becomes standard.

### 3.8 Metric → decision table (brief)

| Metric | Formula (over ledger fields) | Decision it informs |
|---|---|---|
| Reviewer catch rate | `caught(S) / (caught(S)+escaped(S))` | where to put the strongest model/effort; which stage to cut |
| False-hold rate | `unsubstantiated_holds(S) / all_holds_fails(S)` | whether a stage over-blocks; loosen criteria; lower its weight |
| Cost per merged unit | `Σ cost(merged rows) / count(merged)` | affordability; which stage to cheapen or make deterministic |
| Repeat-incident rate | `repeat_matches(C) / merged_in_lane(C)` after `D_C` | which catalog entries to graduate to a gate; which to archive |
| Time-to-merge | `merge_ts − first_review_ts` (median/p90; active vs wait) | pipeline latency; bottleneck stage; batching cadence |
| Evidence-inflation rate | `count(claimed>verified) / count(both set)` | which role overclaims DoD; re-brief; lower its weight |

---

## 4. The calibration loop

Port the platform's self-score-correlation weighting (`platform:gateway/core/sgs.py:38-135`) to the
review layer, with the ledger's back-filled outcomes as the external truth.

**The correlation.** Periodically, per reviewing `reviewer_role`, compute the correlation between
the role's self-assessment and the verified outcome:

- *For a reviewer role* — correlate its verdict severity (`pass` … `fail`, ordinal) against whether
  a defect actually surfaced (`defect_surfaced`). A role whose `pass` reliably predicts no defect and
  whose `fail`/`hold` reliably predicts a real one has high correlation → its verdict is trustworthy.
- *For a submitting role* — correlate `evidence_claimed` against `evidence_verified` (is its
  self-reported done-ladder level trustworthy).

**The feedback (what the weight changes).** The weight `w` derived from the correlation (same
mapping shape as the platform: strong positive r → small positive w; noise or inverted r → 0) tunes
**verification intensity**, not the merge bar:

- High-correlation role → lighter, cheaper verification (e.g. its solo pass may clear a unit without
  the mandatory adversarial re-read; its `evidence_claimed` may be provisionally accepted).
- Low / noise / inverted role → full adversarial verification stays mandatory (weight 0.0 — its
  self-assessment counts for nothing, exactly as the platform zeroes the noise/inverted agents).

This is the platform's `final = (1-w)·external + w·self` blend, applied to *how much scrutiny a
verdict buys itself out of* rather than to a numeric score.

**Hard guardrail.** Calibration may only ever *reduce* discretionary re-review for a proven role or
keep it full — it may **never** let a unit merge below the done-ladder floor (L2 for merge, hard
rule 2) and never lets a high self-score substitute for a compiled gate (CI, lints). This keeps "an
LLM is never the last line of defense" intact: calibration tunes the *adversarial re-read* budget,
never the deterministic gates.

**Recompute cadence.** At a batching boundary, not per decision (a decision's outcome isn't known
until back-fill): recompute at the weekly dispatch (`studio:docs/kb/director-handbook.md` §7 weekly
rhythm) or every N newly-back-filled outcomes per role, whichever comes first.

**Minimum sample size — flagged honestly.** The platform's precedent used **small samples**: the
r-values in `platform:gateway/core/sgs.py:38-46` are quoted to three digits with **no n and no
confidence interval** reported — a real weakness to name, not to imitate. This spec requires a floor
of **≥ 20 verified-outcome samples per role**, spanning more than one session and more than one
`unit_kind`, before a computed weight is trusted — and states plainly that even 20 is thin and a
single outlier can swing a correlation at that size. Treat the weight as provisional and re-derive it
every cadence; never freeze it.

**Below the floor → conservative default.** A role with `< 20` verified outcomes gets **weight 0.0**
— self-assessment ignored, full independent verification applies (exactly the platform's
`SELF_SCORE_CALIBRATION_DEFAULT = 0.0` for unknown agents). New roles start at default. **A model
change to a role resets it to default** until outcomes re-accumulate — the role is a role, not a
model (`studio:docs/kb/director-handbook.md` §8), so a model swap invalidates the prior correlation.
A master enable switch (the platform's `SELF_SCORE_CALIBRATION_ENABLED`) governs the whole loop; it
is the Stage-2 gate and the rollback lever. The safe failure mode throughout: **uncalibrated =
fully verified, never less.**

**Anti-pattern.** Weights are always *derived* from the ledger, never hand-tuned — hand-editing a
calibration weight is the same error as hand-editing the platform's programmatic
`performance_history` (`platform` conventions: "updated programmatically... don't hand-edit it").

---

## 5. Staged adoption path

Each stage has entry criteria; nothing advances until the prior stage's exit is met. The staging
exists so that a metric never changes a decision before its denominator is trustworthy.

### Stage 0 — capture only (no decision changed)

The ledger is written on every gate decision; nothing reads it to change a verdict. Pure
instrumentation.

- **Entry.** Schema fixed at `schema_version 1`; every decision-time field maps 1:1 to the review
  agents' existing structured output (§2 binding rule); the append adapter rides the existing
  merge-trail recording; the back-fill protocol is wired into the incident-logging ritual and the
  horizon sweep exists.
- **Exit → Stage 1.** N weeks of rows with < X% failing schema validation, **and back-fill is
  actually happening** — merged units past the horizon have non-null `defect_surfaced`. If back-fill
  is not happening, every catch-based metric is a denominator-of-unknown and Stage 1 is worthless;
  this is the gate that matters most.

### Stage 1 — dashboards at session boot (read, don't gate)

The boot ritual (`studio:docs/kb/director-handbook.md` §2) surfaces the metrics: catch rate by
stage, false-hold, cost-per-merge, repeat-incident by catalog entry, time-to-merge, evidence-
inflation by role. The director reads them and acts by **judgment** (upgrade a stage's model,
graduate a catalog entry, re-brief a role). No automated weight changes any verdict.

- **Entry.** Stage 0 exit met; each metric has a named owner-decision (the §3.8 table); at least one
  full milestone of back-filled outcomes exists so the dashboards show *trends*, not single points.
- **Exit → Stage 2.** The metrics have already driven **≥ 1 real decision** (a catalog entry
  graduated, or a stage upgraded/cut), **and** per-role correlation has ≥ 20 samples for the roles
  that would receive non-default weights — i.e. calibration has real ground to stand on.

### Stage 2 — calibration weights live (metrics change gate configuration)

Per-role calibration weights, derived from accumulated correlation, feed back into verification
intensity per §4. The master switch defaults ON; any role below the sample floor stays at default
(0.0).

- **Entry.** Stage 1 exit met; the ≥ 20-sample floor is met for every role being weighted; a
  documented rollback is tested (flip the master switch → revert to Stage 1 flat-verification
  behavior); weights are re-derived every cadence, never hand-tuned; a model change to any role
  resets that role to default.
- **Standing guardrail.** The §4 hard guardrail holds at all times: calibration never lowers the
  done-ladder merge floor and never substitutes a self-score for a compiled gate.

---

## Appendix A — Final ledger-row field list (quick reference)

**Identity/context:** `ledger_id`, `schema_version`, `unit_id`, `unit_kind`, `lane`, `stage`,
`round`, `reviewer_role`, `reviewer_model`, `reviewer_effort`, `timestamp`.
**Verdict:** `verdict`, `verdict_reason`.
**Findings:** `findings_count`, `findings_by_severity`, `finding_ids`.
**Evidence (done-ladder):** `evidence_claimed`, `evidence_verified`.
**Cost:** `cost_tokens_in`, `cost_tokens_out`, `cost_usd`, `wall_clock_seconds`.
**Outcome (back-filled, written as amendment rows):** `outcome_kind`, `outcome_ref_ledger_id`,
`merged`, `merge_timestamp`, `defect_surfaced`, `linked_incident_id`, `escape_stage`,
`hold_substantiated`, `outcome_backfilled_at`.

## Appendix B — Self-checklist against the workplan extraction tests

- **Test 1 — two-repo / earned-from-incident.** PASS. The two ported mechanisms each appear in one
  proving ground and are adopted from documented artifacts: the per-decision record and its
  append-to-repo persistence from the orchestration platform (`platform:gateway/core/phase_models.py`,
  `platform:gateway/core/phase_engine.py:1276`); the self-score-correlation weighting from the same
  (`platform:gateway/core/sgs.py:38-135`). The studio side (review pipeline §4, done-ladder, living
  failure catalog §6/§7) supplies the second ground for the *loop this measures*. This is a
  measurement spec (a bindings-adjacent design), not a layer-1/2 principle, so the two-repo bar is
  met by "documented artifact adopted as design," not by inventing a pattern.
- **Test 2 — no proper nouns.** PASS. Only neutral labels used ("studio project"/"the studio",
  "orchestration platform"/"the platform", "the director role", "the human"). No game names, team
  codenames, client names, or model product names as identifiers.
- **Test 3 — receipts.** PASS. Every mechanism and metric cites a dated/locatable source: platform
  code paths with line numbers for the ported artifacts and the r-values; studio handbook sections
  (§2, §4, §5, §6, §7, §8) and `studio:CLAUDE.md` hard rule 2 for the pipeline, done-ladder,
  structured-output capture, failure-catalog lifecycle, and false-hold precedent (the phantom-ruling
  incident).
- **Test 4 — hygiene (absolute).** PASS. No client names, case identifiers, personal data, tokens,
  hostnames, IP addresses, or protected-franchise proper nouns anywhere in the file. Citations use
  the `studio:` / `platform:` alias form only.
</content>
</invoke>
