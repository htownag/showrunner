# Boot & Gate Integration — the review ledger in the loop

How the measurement layer plugs into the studio's existing rituals without adding
a manual step. This file is the operator's half of the D5 spec: the spec designs
*what* is measured; this describes *where the two touch points sit* in the boot
ritual (Stage 1) and at gate time (Stage 2), and the capture path that keeps the
ledger fed for free (Stage 0). It follows the spec's staged adoption path (§5) —
nothing here turns on a stage before its entry criteria are met.

The three artifacts this file wires together:

- `ledger.schema.json` — the row contract (decision rows + amendment rows).
- `review-output.schema.json` — what a review/verify agent is forced to emit.
- `ledger.py` — `append` / `check` / `project` / `report`.

---

## Stage 0 — capture rides the existing workflow (no manual step)

The spec's binding rule (§2): *every decision-time ledger field must map 1:1 onto
a field the review agent already emits.* That is enforced structurally here —
`review-output.schema.json` **is** the review agent's forced output shape, and a
decision ledger row is a pure projection of it. The capture path:

```
review/verify agent  ──emits──▶  review-output.json  (forced structured output)
                                        │
                                        ▼
        ledger.py project  --ledger-id … --unit-id … --stage … --lane …
        (adds the context the reviewer can't know; derives the findings roll-up)
                                        │
                                        ▼
                             a decision ledger row
                                        │
                                        ▼
        ledger.py append  --ledger measurement/review-ledger.jsonl
        (validates against ledger.schema.json; rejects loudly on any drift)
```

Concretely, the capture adapter runs at the one moment the director already
records a verdict (posting the merge trail / advisor signature). Worked example —
a lead-review verdict captured end to end:

```bash
echo '{"verdict":"pass-with-required-changes","reviewer_role":"lead",
       "reviewer_effort":"high","evidence_claimed":"L2","evidence_verified":"L2",
       "findings":[{"id":"F-1","severity":"major","summary":"missing null-guard","file":"x.py","line":88},
                   {"id":"F-2","severity":"minor","summary":"rename for clarity"}],
       "merge_recommendation":"merge-after-required-changes"}' \
| python3 ledger.py project \
    --ledger-id RL-0042 --unit-id 1234 --unit-kind code --lane platform-role \
    --stage lead-review --round 0 --reviewer-model opus \
    --timestamp 2026-07-08T14:03:00Z --cost-usd 0.83 --wall-clock-seconds 240 \
| python3 ledger.py append --ledger measurement/review-ledger.jsonl
```

The `findings_count`, `findings_by_severity`, and `finding_ids` are **derived**
from the `findings[]` array by `project` — never hand-counted, so they cannot
drift from the findings the reviewer actually reported. Deterministic gates (CI,
lints) emit the same `review-output` shape from their serializer with
`reviewer_effort: deterministic` and `reviewer_model: null`, so they capture for
free too.

**Back-fill (the outcome group).** Outcomes are unknowable at decision time, so
they arrive as separate amendment rows (never edits). Two hooks, both riding
existing rituals:

1. *Incident-logging ritual.* When an incident is logged into the failure catalog
   / case-law (already same-session per the catalog's living rule), append one
   amendment row for the ledger row(s) of the unit that introduced it, setting
   `defect_surfaced=true`, `linked_incident_id` (the CL-###), and `escape_stage`.
2. *Horizon sweep.* A periodic pass finds merged units past the horizon (the next
   integration build / milestone review — a project binding) with no linked
   incident and appends an amendment row setting `defect_surfaced=false`. This is
   what gives every catch-based metric a real denominator; a null is an *unknown*
   unit, not a clean one.

**Stage-0 exit gate (the one that matters most):** run `ledger.py check` clean on
the ledger for N weeks *and* confirm back-fill is actually happening — merged
units past the horizon have non-null `defect_surfaced`. The `report` header prints
the back-fill coverage precisely so this gate is checkable at a glance (see the
`43%` line in the worked output below).

---

## Stage 1 — the boot dashboard (read, don't gate)

The boot ritual adds one line: run `ledger.py report` and read it. The director
acts by **judgment** — upgrade a low-catch/high-cost stage's model, graduate a
catalog entry whose repeat rate won't decline under prose, re-brief a role with
high evidence inflation. No automated weight changes any verdict at this stage.

Boot ritual line:

```bash
python3 measurement/ledger.py report --ledger measurement/review-ledger.jsonl
```

Each block maps to the owner-decision in spec §3.8: catch rate → where to spend
the strongest configuration / which stage to cut; false-hold → whether a stage
over-blocks; cost-per-merge → affordability / which stage to cheapen; repeat-
incident → which catalog entries to graduate or archive; time-to-merge → latency
and batching cadence; evidence-inflation → which role overclaims DoD.

**Stage-1 exit gate:** the metrics have driven ≥1 real decision, *and* per-role
correlation has ≥20 verified-outcome samples for the roles that would receive a
non-zero weight — i.e. calibration has ground to stand on before it goes live.

### Worked dashboard example (real output of the bundled synthetic ledger)

Produced by `python3 ledger.py report --ledger example-ledger.jsonl` against the
10-row synthetic `example-ledger.jsonl` (all rows marked synthetic via the
`example-` unit-id prefix). Pasted verbatim:

```
====================================================================
REVIEW LEDGER DASHBOARD  (source: example-ledger.jsonl)
====================================================================
Rows: 7 decision, 3 amendment. Decision rows with a back-filled
outcome: 3/7 (43%).
  NOTE: catch-based metrics have an unknown denominator for the
  4 rows without an outcome. Back-fill / horizon sweep is the gate
  that makes Stage 1 trustworthy (spec §5 Stage-0 exit).

-- Reviewer catch rate (per stage) ---------------------------------
   caught = stage raised blocker/major AND blocked (fail/hold);
   escaped = merged unit with defect_surfaced and escape_stage==S.
   design-advisor   catch_rate = 100.0% (1/1)
   lead-review      catch_rate = 50.0% (1/2)

-- False-hold rate (per stage) -------------------------------------
   design-advisor   false_hold = 100.0% (1/1)
   lead-review      false_hold = 0.0% (0/1)

-- Cost per merged unit --------------------------------------------
   merged units: 3
   cost_usd / merged unit   = $0.7833  (over 5 priced rows)
   tokens   / merged unit   = 44116
   wall-clock / merged unit = 248s

-- Repeat-incident rate (failure-catalog efficacy) ----------------
   linked incidents: 1 across 1 distinct catalog entries
     CL-024     x1
   repeat-incident rate = 0.0% (0/1) of linked defects are recurrences
   NOTE: the spec's full formula (repeats after a catalog entry's
   codification date / units merged in that lane) needs per-entry
   codification dates + a signature field on the catalog side — not
   derivable from ledger fields alone. Shown here: the ledger-computable
   recurrence count by linked_incident_id.

-- Time-to-merge (per merged unit) --------------------------------
   median = 1.2h   p90 = 6.0h   (n=3 merged units)
   mean active-review fraction = 5% (rest is waiting — often on
   the human; spec §3.5 says split these, don't optimise waiting).

-- Evidence-inflation rate (per reviewer_role) --------------------
   director         inflation = 0.0% (0/1)
   lead             inflation = 25.0% (1/4)

-- Calibration weights (per reviewer_role) ------------------------
   correlate verdict severity (pass<PWRC<hold<fail) vs defect_surfaced;
   floor = 20 verified-outcome samples; below floor -> weight 0.0.
   advisor          weight = 0.0  [BELOW FLOOR: n=1 < 20; self-assessment
                                  ignored, full verification applies]
   director         weight = 0.0  [BELOW FLOOR: n=2 < 20; self-assessment
                                  ignored, full verification applies]

Not computable from ledger fields alone (stated per spec, not silently
skipped): the master calibration enable-switch state (a project binding);
model-change reset timing beyond detecting >1 model per role; and the
repeat-rate lane denominator (needs catalog codification dates).
====================================================================
```

Reading this synthetic run the way a director would: the `43%` back-fill line says
Stage 0's exit gate is **not yet met** (four rows still have unknown outcomes) —
so every catch-based number below it is provisional, exactly as the header warns.
`lead-review` shows one real catch (a `fail` with a blocker) and one escape (a
defect that reached merge with `escape_stage=lead-review`, linked to `CL-024`),
giving a 50% catch rate — a signal to look at what that stage missed. The
`design-advisor` false-hold of 100% is the phantom-hold class the spec calls out:
a sound unit blocked on a stamp that already existed, later resolved
`hold_substantiated=false`. Evidence inflation of 25% on the `lead` role is one
row that claimed L2 while only L1 was verified. Both calibration weights sit at
0.0 because neither role has cleared the 20-sample floor — the honest,
safe-by-default state (uncalibrated = fully verified, never less).

---

## Stage 2 — calibration weights at gate time (metrics change gate config)

Only after Stage 1's exit gate. Per-role weights from `report`'s calibration block
feed back into **verification intensity only** — never the merge bar. A role that
has cleared the 20-sample floor with a strong positive correlation earns a small
positive weight, which buys its solo verdict *out of some discretionary
adversarial re-read*; a role at noise/inverted/below-floor keeps full verification
(weight 0.0). The blend is the platform's `final = (1-w)·external + w·self` applied
to *how much scrutiny a verdict buys itself out of*, not to a numeric score.

**Standing guardrail (holds at all times):** calibration may only ever reduce
discretionary re-review for a proven role or keep it full. It never lowers the
done-ladder merge floor (L2 for merge) and never lets a self-score substitute for
a compiled gate (CI, lints). A master enable switch is the Stage-2 gate and the
rollback lever — flip it and behaviour reverts to Stage-1 flat verification. A
model change to a role resets that role to default (0.0) until outcomes
re-accumulate; `report` flags any role seen with more than one `reviewer_model`
as a mixed-model weight that must not be trusted until reset. Weights are always
*derived* from the ledger, never hand-tuned.

---

## Operator quick reference

| Task | Command |
|---|---|
| Capture a verdict | `… project … \| ledger.py append --ledger measurement/review-ledger.jsonl` |
| Validate the whole ledger | `ledger.py check --ledger measurement/review-ledger.jsonl` |
| Boot dashboard | `ledger.py report --ledger measurement/review-ledger.jsonl` |
| Back-fill an outcome | append an amendment row (`row_kind":"amendment"`, `outcome_kind":"outcome"`, `outcome_ref_ledger_id`) |

`ledger.py` is stdlib-only and self-contained — it runs in any repo that adopts
the framework, no install step.

---

## Spec-change notes

Deviations from `review-ledger-spec.md`, per the D5b contract (record, don't
silently diverge). Two, both additive and non-behavioural:

1. **`row_kind` discriminator added.** The spec models the decision-row vs
   amendment-row distinction implicitly, via the presence of `outcome_kind="outcome"`
   on amendment rows (§1.1, §2). The schema and tool add an explicit
   `row_kind` field (`"decision"` / `"amendment"`) as the discriminator, so a
   validator can branch cleanly with `oneOf` and so a reader never has to infer a
   row's kind from which fields happen to be present. `outcome_kind="outcome"` is
   **retained** on amendment rows exactly as the spec requires — `row_kind` is a
   strict superset marker, not a replacement. The workplan explicitly permits this
   ("oneOf or a row_kind discriminator — your call, document it"). Rows written
   without `row_kind` are still classified correctly by the tool's fallback
   (`_row_kind`: presence of `outcome_kind` ⇒ amendment), so the field is
   forward/backward tolerant.

2. **Repeat-incident rate: ledger-computable subset implemented; full formula
   flagged in output.** Spec §3.4's full formula divides repeats-after-codification
   by units-merged-in-lane after a catalog entry's codification date `D_C`. Neither
   `D_C` nor a per-entry catalog *signature* lives in the ledger — they live on the
   failure-catalog side. `report` therefore computes what the ledger alone supports
   (recurrence count grouped by `linked_incident_id`, and the fraction of linked
   defects that are recurrences) and prints an explicit NOTE naming the missing
   inputs, rather than silently emitting a partial number as if it were the spec's
   metric. Wiring the lane denominator is a per-project step once the catalog grows
   a codification-date + signature field.

No other deviations. All decision-time field names, the outcome-as-amendment-row
model, the JSONL storage choice, the metric set, the ≥20-sample calibration floor,
the below-floor→0.0 default, the model-change reset, and the three-stage adoption
path are implemented as specified.
