#!/usr/bin/env python3
"""Review-ledger reference tool (framework measurement layer, D5b).

Single-file, stdlib-only, no network. Implements the review-ledger-spec.md
contract: capture a structured verdict per gate decision, validate it, and read
the ledger back into the spec's metric set + calibration weights.

Three-stage adoption path (spec §5), which this tool is built to serve:

  Stage 0 — capture only. Review/verify agents already emit structured output
    (review-output.schema.json). `project` turns that output into a decision row;
    `append` validates + writes it to review-ledger.jsonl. Nothing reads the
    ledger to change a verdict. Pure instrumentation.

  Stage 1 — dashboards at boot. `report` computes catch rate, false-hold rate,
    cost per merged unit, repeat-incident rate, time-to-merge, and evidence
    inflation from the ledger. The boot ritual surfaces them; a human acts by
    judgment. No automated weight changes a verdict. Metric behavior follows the
    ratified rulings R1-R6 (spec §2, §3.1, §3.3): catch rate counts unique
    (unit_id, stage) pairs that blocked a unit with a major/blocker finding AND
    resolved hold_substantiated=true; pairs still null on hold_substantiated are
    PENDING (excluded from the rate, reported per stage); the escaped side dedupes
    by (unit_id, escape_stage); malformed lines are quarantined loud and metrics
    refuse to render past a 10% malformed floor; and cost/wall-clock lines print
    "not captured" rather than a misleading zero when no row carries the field.

  Stage 2 — calibration live. `report` also emits per-role calibration weights
    (correlation of self-assessment vs verified outcome, >=20-sample floor,
    below floor -> weight 0.0). Gate time reads those weights to tune
    verification intensity only — never the done-ladder merge floor, never a
    compiled gate (spec §4 hard guardrail).

Subcommands: append | check | project | report. See `--help`.

Outcome back-fill: the outcome_* group is unknowable at decision time. It arrives
as a SEPARATE amendment row (row_kind="amendment", outcome_kind="outcome") keyed
to a decision row via outcome_ref_ledger_id. The reader folds amendment rows onto
their base decision row at read time; the file stays strictly append-only.
"""

import argparse
import json
import math
import sys
from collections import defaultdict

HERE = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."
DEFAULT_LEDGER = "./review-ledger.jsonl"
LADDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}
# Verdict severity as an ordinal for the calibration correlation (spec §4).
VERDICT_SEVERITY = {"pass": 0, "pass-with-required-changes": 1, "hold": 2, "fail": 3}


# --------------------------------------------------------------------------- #
# Minimal JSON Schema validator (subset: type, required, enum, const, oneOf,   #
# properties, items, minimum, additionalProperties, $ref/$defs). Deliberately  #
# NOT jsonschema — stdlib only.                                                #
# --------------------------------------------------------------------------- #

class SchemaError(Exception):
    pass


def _load_schema(path):
    with open(path) as fh:
        return json.load(fh)


def _type_ok(value, typ):
    if typ == "object":
        return isinstance(value, dict)
    if typ == "array":
        return isinstance(value, list)
    if typ == "string":
        return isinstance(value, str)
    if typ == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if typ == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if typ == "boolean":
        return isinstance(value, bool)
    if typ == "null":
        return value is None
    return False


def _resolve(schema, root):
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise SchemaError("only local #/ refs supported: %s" % ref)
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        return node
    return schema


def validate(value, schema, root, path="$"):
    """Return a list of human-readable error strings ([] == valid)."""
    schema = _resolve(schema, root)
    errors = []

    if "oneOf" in schema:
        branch_errors = [validate(value, sub, root, path) for sub in schema["oneOf"]]
        matches = [i for i, errs in enumerate(branch_errors) if not errs]
        if len(matches) != 1:
            errors.append("%s: matched %d of %d oneOf branches (need exactly 1)"
                          % (path, len(matches), len(schema["oneOf"])))
            if len(matches) == 0:
                # Surface the closest branch's reasons so rejection is loud.
                closest = min(branch_errors, key=len)
                for e in closest:
                    errors.append("  (closest branch) %s" % e)
        return errors

    if "const" in schema and value != schema["const"]:
        errors.append("%s: expected const %r, got %r" % (path, schema["const"], value))

    if "enum" in schema and value not in schema["enum"]:
        errors.append("%s: %r not in enum %r" % (path, value, schema["enum"]))

    if "type" in schema:
        types = schema["type"]
        types = [types] if isinstance(types, str) else types
        if not any(_type_ok(value, t) for t in types):
            errors.append("%s: type mismatch, expected %r, got %s"
                          % (path, types, type(value).__name__))
            return errors  # further checks assume the type held

    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema["minimum"]:
            errors.append("%s: %r < minimum %r" % (path, value, schema["minimum"]))

    if isinstance(value, dict) and "properties" in schema:
        props = schema["properties"]
        for req in schema.get("required", []):
            if req not in value:
                errors.append("%s: missing required field %r" % (path, req))
        for key, sub in props.items():
            if key in value:
                errors += validate(value[key], sub, root, "%s.%s" % (path, key))
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append("%s: additional property %r not allowed" % (path, key))
    elif isinstance(value, dict) and "required" in schema:
        for req in schema["required"]:
            if req not in value:
                errors.append("%s: missing required field %r" % (path, req))

    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], root, "%s[%d]" % (path, i))

    return errors


# --------------------------------------------------------------------------- #
# Ledger IO + fold                                                             #
# --------------------------------------------------------------------------- #

def _read_rows(ledger_path):
    """Read a ledger file, separating parseable rows from malformed lines.

    Returns (rows, malformed):
      rows      -- list of (lineno, row_dict) for every line that parsed as JSON.
      malformed -- list of (lineno, error_message) for every non-empty line that
                   did NOT parse as JSON.

    Blank lines are ignored entirely; a missing file yields ([], []). This
    function NEVER raises on a bad JSON line (ruling R1): malformed input is
    surfaced as data so each caller applies its own fail-closed policy. `check`
    treats any malformed line as a hard failure and exits 1 (it is a compiled
    gate); `report` quarantines each malformed line loudly, counts it in the
    dashboard header, and refuses to render metrics once malformed lines exceed
    10% of the non-empty lines. Silent skipping is never permitted on a
    measurement surface — a silently dropped line corrupts every denominator
    invisibly (spec §2, the fail-open sin Principle 5 exists to prevent)."""
    rows = []
    malformed = []
    try:
        with open(ledger_path) as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append((i, json.loads(line)))
                except json.JSONDecodeError as exc:
                    malformed.append((i, str(exc)))
    except FileNotFoundError:
        return [], []
    return rows, malformed


def _row_kind(row):
    return row.get("row_kind") or ("amendment" if row.get("outcome_kind") == "outcome" else "decision")


def _fold(rows):
    """Fold amendment rows onto their base decision rows.

    Returns dict ledger_id -> enriched decision dict (a copy of the decision row
    with any outcome_* fields from amendments referencing it merged in).
    """
    decisions = {}
    amendments = []
    for _, row in rows:
        if _row_kind(row) == "amendment":
            amendments.append(row)
        else:
            decisions[row.get("ledger_id")] = dict(row)
    for am in amendments:
        base_id = am.get("outcome_ref_ledger_id")
        base = decisions.get(base_id)
        if base is None:
            continue  # dangling amendment; surfaced by `check`, ignored here
        for field in ("merged", "merge_timestamp", "defect_surfaced",
                      "linked_incident_id", "escape_stage", "hold_substantiated",
                      "outcome_backfilled_at"):
            if field in am and am[field] is not None:
                base[field] = am[field]
    return decisions


# --------------------------------------------------------------------------- #
# Subcommand: append                                                          #
# --------------------------------------------------------------------------- #

def cmd_append(args):
    schema = _load_schema(args.schema)
    raw = args.row_json if args.row_json else sys.stdin.read()
    try:
        row = json.loads(raw)
    except json.JSONDecodeError as exc:
        print("append: input is not valid JSON: %s" % exc, file=sys.stderr)
        return 2
    errors = validate(row, schema, schema)
    if errors:
        print("append: row REJECTED, %d schema error(s):" % len(errors), file=sys.stderr)
        for e in errors:
            print("  - %s" % e, file=sys.stderr)
        return 1
    with open(args.ledger, "a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    print("append: 1 row appended to %s (ledger_id=%s)"
          % (args.ledger, row.get("ledger_id")))
    return 0


# --------------------------------------------------------------------------- #
# Subcommand: check                                                          #
# --------------------------------------------------------------------------- #

def cmd_check(args):
    schema = _load_schema(args.schema)
    rows, malformed = _read_rows(args.ledger)
    if not rows and not malformed:
        print("check: %s is empty or absent — nothing to validate." % args.ledger)
        return 0
    bad = 0
    # Ruling R1: `check` is a compiled gate — any malformed line is fatal, and
    # every bad line number is named (never silently skipped).
    for lineno, msg in sorted(malformed):
        print("check: line %d: malformed JSON (not parseable): %s" % (lineno, msg),
              file=sys.stderr)
        bad += 1
    ids = set()
    for lineno, row in rows:
        errors = validate(row, schema, schema)
        for e in errors:
            print("check: line %d: %s" % (lineno, e), file=sys.stderr)
            bad += 1
        lid = row.get("ledger_id")
        if lid in ids:
            print("check: line %d: duplicate ledger_id %r" % (lineno, lid), file=sys.stderr)
            bad += 1
        ids.add(lid)
    # Referential integrity: amendments must point at a known decision row.
    decision_ids = {r.get("ledger_id") for _, r in rows if _row_kind(r) == "decision"}
    for lineno, row in rows:
        if _row_kind(row) == "amendment":
            ref = row.get("outcome_ref_ledger_id")
            if ref not in decision_ids:
                print("check: line %d: amendment references unknown decision row %r"
                      % (lineno, ref), file=sys.stderr)
                bad += 1
    if bad:
        print("check: FAILED — %d problem(s) across %d parsed row(s) + %d malformed line(s)."
              % (bad, len(rows), len(malformed)), file=sys.stderr)
        return 1
    print("check: OK — %d rows valid, no duplicate ids, all amendments resolve." % len(rows))
    return 0


# --------------------------------------------------------------------------- #
# Subcommand: project (review-output -> decision ledger row)                  #
# --------------------------------------------------------------------------- #

def cmd_project(args):
    ro_schema = _load_schema(args.review_output_schema)
    raw = args.review_json if args.review_json else sys.stdin.read()
    try:
        ro = json.loads(raw)
    except json.JSONDecodeError as exc:
        print("project: review-output is not valid JSON: %s" % exc, file=sys.stderr)
        return 2
    errors = validate(ro, ro_schema, ro_schema)
    if errors:
        print("project: review-output REJECTED, %d error(s):" % len(errors), file=sys.stderr)
        for e in errors:
            print("  - %s" % e, file=sys.stderr)
        return 1

    # Derive findings roll-up from the findings array (never hand-counted).
    findings = ro.get("findings", [])
    by_sev = {"blocker": 0, "major": 0, "minor": 0, "nit": 0}
    finding_ids = []
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        finding_ids.append(f["id"])

    row = {
        "row_kind": "decision",
        "ledger_id": args.ledger_id,
        "schema_version": args.schema_version,
        "unit_id": args.unit_id,
        "unit_kind": args.unit_kind,
        "lane": args.lane,
        "stage": args.stage,
        "round": args.round,
        "reviewer_role": args.reviewer_role or ro.get("reviewer_role"),
        "reviewer_model": args.reviewer_model if args.reviewer_model is not None else ro.get("reviewer_model"),
        "reviewer_effort": args.reviewer_effort or ro.get("reviewer_effort"),
        "timestamp": args.timestamp,
        "verdict": ro["verdict"],
        "verdict_reason": ro.get("verdict_reason"),
        "findings_count": len(findings),
        "findings_by_severity": by_sev,
        "finding_ids": finding_ids,
        "evidence_claimed": ro["evidence_claimed"],
        "evidence_verified": ro.get("evidence_verified"),
        "cost_tokens_in": args.cost_tokens_in if args.cost_tokens_in is not None else ro.get("cost_tokens_in"),
        "cost_tokens_out": args.cost_tokens_out if args.cost_tokens_out is not None else ro.get("cost_tokens_out"),
        "cost_usd": args.cost_usd if args.cost_usd is not None else ro.get("cost_usd"),
        "wall_clock_seconds": args.wall_clock_seconds if args.wall_clock_seconds is not None else ro.get("wall_clock_seconds"),
    }
    # Ruling R5 passthrough: the project's own stage / unit-kind label rides
    # through from a flag or from the review-output object ("map to canonical,
    # preserve raw", spec §1.1). Emitted only when present so v1 projections stay
    # unchanged; the schema (v2) accepts either field as optional.
    stage_raw = args.stage_raw if args.stage_raw is not None else ro.get("stage_raw")
    unit_kind_raw = args.unit_kind_raw if args.unit_kind_raw is not None else ro.get("unit_kind_raw")
    if stage_raw is not None:
        row["stage_raw"] = stage_raw
    if unit_kind_raw is not None:
        row["unit_kind_raw"] = unit_kind_raw
    # Validate the projected row before emitting (fail loud, don't emit garbage).
    led_schema = _load_schema(args.schema)
    perr = validate(row, led_schema, led_schema)
    if perr:
        print("project: projected row failed ledger schema, %d error(s):" % len(perr), file=sys.stderr)
        for e in perr:
            print("  - %s" % e, file=sys.stderr)
        return 1
    print(json.dumps(row, sort_keys=True))
    return 0


# --------------------------------------------------------------------------- #
# Metric helpers                                                              #
# --------------------------------------------------------------------------- #

def _pct(n, d):
    return "n/a (0 samples)" if d == 0 else "%.1f%% (%d/%d)" % (100.0 * n / d, n, d)


def _median(xs):
    if not xs:
        return None
    s = sorted(xs)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2.0


def _percentile(xs, p):
    if not xs:
        return None
    s = sorted(xs)
    idx = min(len(s) - 1, int(math.ceil(p / 100.0 * len(s))) - 1)
    return s[max(0, idx)]


def _pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None  # no variance -> correlation undefined
    return num / (dx * dy)


CALIB_FLOOR = 20        # spec §4 minimum-sample floor
CALIB_R_THRESHOLD = 0.30  # below this |r| is treated as noise -> weight 0.0


def _weight_from_r(r):
    """Map correlation -> verification-intensity weight, platform mapping shape
    (r=0.747->0.15, 0.614->0.12, 0.556->0.10; noise/inverted->0.0)."""
    if r is None or r <= CALIB_R_THRESHOLD:
        return 0.0
    return round(min(0.20 * r, 0.20), 2)


BLOCKED_VERDICTS = ("fail", "hold")
COST_FIELDS = ("cost_tokens_in", "cost_tokens_out", "cost_usd")


def _catch_metrics(decisions):
    """Per-stage catch/escaped/pending counts over folded decision rows.

    Implements rulings R2/R3/R4 (spec §3.1). Returns
    {stage: {"caught": int, "escaped": int, "pending": int}}:

      caught  — unique (unit_id, stage) pairs that BLOCKED the unit (a `fail` or
                `hold` verdict) carrying a major/blocker finding AND resolved
                hold_substantiated=true. A blocked unit never merges, so
                defect_surfaced is unobservable for exactly these rows;
                hold_substantiated is the observable outcome-consistency signal.
      pending — the same blocked+major pairs whose hold_substantiated is still
                null: excluded from the rate entirely (never a catch, never a
                miss), reported separately per stage (R3). hold_substantiated
                false is NOT counted here — it is not a catch, and feeds the
                (unchanged) false-hold metric.
      escaped — unique (unit_id, escape_stage) pairs among merged units with
                defect_surfaced=true (R4 dedup on the escaped side).

    Both sides count units, not decision rows, so a rework round that repeats a
    finding is one pair, never double-counted."""
    caught_pairs = set()
    pending_pairs = set()
    for d in decisions:
        sev = d.get("findings_by_severity", {}) or {}
        raised_major = (sev.get("blocker", 0) + sev.get("major", 0)) > 0
        if raised_major and d.get("verdict") in BLOCKED_VERDICTS:
            pair = (d.get("unit_id"), d.get("stage"))
            hs = d.get("hold_substantiated")
            if hs is True:
                caught_pairs.add(pair)
            elif hs is None:
                pending_pairs.add(pair)
            # hs is False -> not a catch; feeds false-hold, not counted here.
    # A (unit, stage) resolved as caught in any round overrides a pending pair
    # for the same key (the outcome resolved).
    pending_pairs.difference_update(caught_pairs)

    escaped_pairs = set()
    for d in decisions:
        if d.get("defect_surfaced") is True and d.get("escape_stage"):
            escaped_pairs.add((d.get("unit_id"), d.get("escape_stage")))

    stages = {s for _, s in caught_pairs} | {s for _, s in escaped_pairs} \
        | {s for _, s in pending_pairs}
    metrics = {}
    for s in stages:
        metrics[s] = {
            "caught": sum(1 for _, st in caught_pairs if st == s),
            "escaped": sum(1 for _, st in escaped_pairs if st == s),
            "pending": sum(1 for _, st in pending_pairs if st == s),
        }
    return metrics


def _stage_raw_map(decisions):
    """canonical stage -> sorted list of distinct non-null stage_raw labels seen
    (ruling R5). Used to annotate per-stage report lines only where a project
    recorded its own raw stage label."""
    raw = defaultdict(set)
    for d in decisions:
        sr = d.get("stage_raw")
        if sr:
            raw[d.get("stage")].add(sr)
    return {s: sorted(v) for s, v in raw.items()}


def _stage_label(stage, raw_map):
    """Render a stage with a `(raw: X, Y)` aggregation note where raw labels
    exist for it, else the bare canonical stage (ruling R5)."""
    raws = raw_map.get(stage)
    if raws:
        return "%s (raw: %s)" % (stage, ", ".join(raws))
    return stage


# --------------------------------------------------------------------------- #
# Subcommand: report                                                         #
# --------------------------------------------------------------------------- #

def cmd_report(args):
    rows, malformed = _read_rows(args.ledger)
    out = []
    W = out.append
    W("=" * 68)
    W("REVIEW LEDGER DASHBOARD  (source: %s)" % args.ledger)
    W("=" * 68)
    total_nonempty = len(rows) + len(malformed)
    if total_nonempty == 0:
        W("Ledger is empty or absent. Nothing to report yet.")
        W("Stage-0 capture has produced no rows — wire the append adapter first")
        W("(see boot-integration.md). All metrics below become available once")
        W("decision rows and back-filled outcome rows exist.")
        print("\n".join(out))
        return 0

    # Ruling R1: quarantine malformed lines LOUD in the header, and refuse to
    # render metrics past a 10% malformed floor (a corrupt denominator is worse
    # than no dashboard). `report` skips the bad line but never silently.
    if malformed:
        frac = len(malformed) / total_nonempty
        W("!! QUARANTINE: %d malformed line(s) skipped, of %d non-empty line(s)."
          % (len(malformed), total_nonempty))
        W("   malformed line number(s): %s"
          % ", ".join(str(ln) for ln, _ in sorted(malformed)))
        W("   malformed fraction = %.1f%% (refusal threshold: >10%%)." % (100.0 * frac))
        if frac > 0.10:
            W("   REFUSING to render metrics: more than 10% of non-empty lines are")
            W("   malformed, so every denominator below would be untrustworthy")
            W("   (ruling R1). Fix the ledger and re-run; `check` names each bad line.")
            W("=" * 68)
            print("\n".join(out))
            return 1
        W("")

    enriched = _fold(rows)
    decisions = list(enriched.values())
    n_decision = len(decisions)
    n_amend = sum(1 for _, r in rows if _row_kind(r) == "amendment")
    with_outcome = [d for d in decisions if d.get("defect_surfaced") is not None]

    W("Rows: %d decision, %d amendment. Decision rows with a back-filled"
      % (n_decision, n_amend))
    W("outcome: %d/%d (%.0f%%)." % (len(with_outcome), n_decision,
      100.0 * len(with_outcome) / n_decision if n_decision else 0))
    if len(with_outcome) < n_decision:
        W("  NOTE: catch-based metrics have an unknown denominator for the")
        W("  %d rows without an outcome. Back-fill / horizon sweep is the gate"
          % (n_decision - len(with_outcome)))
        W("  that makes Stage 1 trustworthy (spec §5 Stage-0 exit).")
    W("")

    # ---- 3.1 catch rate (per stage) --------------------------------------- #
    W("-- Reviewer catch rate (per stage) " + "-" * 33)
    W("   caught = unique (unit_id, stage) blocked (fail/hold) with a major/")
    W("   blocker finding AND hold_substantiated=true (rulings R2/R3/R4);")
    W("   pending = same but hold_substantiated null — excluded from the rate;")
    W("   escaped = merged unit, defect_surfaced, escape_stage==S, deduped by")
    W("   (unit_id, escape_stage).")
    catch = _catch_metrics(decisions)
    raw_map = _stage_raw_map(decisions)
    if not catch:
        W("   n/a — no caught defects, pending blocks, or attributed escapes yet.")
    for s in sorted(catch):
        c = catch[s]["caught"]
        e = catch[s]["escaped"]
        p = catch[s]["pending"]
        label = _stage_label(s, raw_map)
        if c + e == 0:
            W("   %-16s catch_rate = n/a (0 resolved samples)" % label)
        else:
            W("   %-16s catch_rate = %s" % (label, _pct(c, c + e)))
        if p:
            W("   %-16s   pending (excluded from rate): %d unit(s) awaiting"
              % ("", p))
            W("   %-16s   hold_substantiated back-fill (ruling R3)." % "")
    W("")

    # ---- 3.2 false-hold rate (per stage) ---------------------------------- #
    W("-- False-hold rate (per stage) " + "-" * 37)
    holds = defaultdict(int)
    false_holds = defaultdict(int)
    for d in decisions:
        if d.get("verdict") in ("hold", "fail"):
            holds[d["stage"]] += 1
            if d.get("hold_substantiated") is False:
                false_holds[d["stage"]] += 1
    if not holds:
        W("   n/a — no hold/fail rows yet.")
    for s in sorted(holds):
        W("   %-16s false_hold = %s" % (_stage_label(s, raw_map), _pct(false_holds[s], holds[s])))
    W("")

    # ---- 3.3 cost per merged unit ----------------------------------------- #
    W("-- Cost per merged unit " + "-" * 44)
    merged_units = {d["unit_id"] for d in decisions if d.get("merged") is True}
    if not merged_units:
        W("   n/a — no merged units recorded yet.")
    else:
        merged_rows = [d for d in decisions if d["unit_id"] in merged_units]
        nmerged = len(merged_units)
        W("   merged units: %d" % nmerged)
        # Ruling R6: when NO decision row for merged units carries a cost field,
        # print a not-captured line rather than computing a zero that reads as a
        # measurement of a cheap pipeline (Principle 5). Graduates the moment a
        # row first carries cost data.
        cost_rows = [d for d in merged_rows
                     if any(d.get(f) is not None for f in COST_FIELDS)]
        if not cost_rows:
            W("   cost: not captured (no rows carry cost fields)")
        else:
            usd_rows = [d for d in cost_rows if d.get("cost_usd") is not None]
            total_tok = sum((d.get("cost_tokens_in") or 0) + (d.get("cost_tokens_out") or 0)
                            for d in cost_rows)
            if usd_rows:
                total_usd = sum(d["cost_usd"] for d in usd_rows)
                W("   cost_usd / merged unit   = $%.4f  (over %d priced rows)"
                  % (total_usd / nmerged, len(usd_rows)))
            W("   tokens   / merged unit   = %d" % (total_tok // nmerged))
        wc_rows = [d for d in merged_rows if d.get("wall_clock_seconds") is not None]
        if not wc_rows:
            W("   wall-clock: not captured (no rows carry wall_clock_seconds)")
        else:
            W("   wall-clock / merged unit = %.0fs"
              % (sum(d["wall_clock_seconds"] for d in wc_rows) / nmerged))
    W("")

    # ---- 3.4 repeat-incident rate (join to failure catalog / CL-IDs) ------ #
    W("-- Repeat-incident rate (failure-catalog efficacy) " + "-" * 16)
    by_incident = defaultdict(int)
    for d in decisions:
        if d.get("defect_surfaced") is True and d.get("linked_incident_id"):
            by_incident[d["linked_incident_id"]] += 1
    total_linked = sum(by_incident.values())
    if total_linked == 0:
        W("   n/a — no defects linked to catalog/CL entries yet.")
    else:
        repeats = sum(v - 1 for v in by_incident.values() if v > 1)
        W("   linked incidents: %d across %d distinct catalog entries" % (total_linked, len(by_incident)))
        for cl, cnt in sorted(by_incident.items()):
            flag = "  <-- REPEAT" if cnt > 1 else ""
            W("     %-10s x%d%s" % (cl, cnt, flag))
        W("   repeat-incident rate = %s of linked defects are recurrences" % _pct(repeats, total_linked))
    W("   NOTE: the spec's full formula (repeats after a catalog entry's")
    W("   codification date / units merged in that lane) needs per-entry")
    W("   codification dates + a signature field on the catalog side — not")
    W("   derivable from ledger fields alone. Shown here: the ledger-computable")
    W("   recurrence count by linked_incident_id.")
    W("")

    # ---- 3.5 time-to-merge ------------------------------------------------ #
    W("-- Time-to-merge (per merged unit) " + "-" * 32)
    ttm = []
    active_frac = []
    per_unit_first = {}
    for d in decisions:
        u = d["unit_id"]
        ts = d.get("timestamp")
        if ts and (u not in per_unit_first or ts < per_unit_first[u]):
            per_unit_first[u] = ts
    for u in merged_units:
        merge_ts = next((d.get("merge_timestamp") for d in decisions
                         if d["unit_id"] == u and d.get("merge_timestamp")), None)
        first_ts = per_unit_first.get(u)
        if merge_ts and first_ts:
            dt = _iso_delta_seconds(first_ts, merge_ts)
            if dt is not None:
                ttm.append(dt)
                active = sum(d.get("wall_clock_seconds") or 0 for d in decisions if d["unit_id"] == u)
                if dt > 0:
                    active_frac.append(active / dt)
    if not ttm:
        W("   n/a — no merged unit has both a first-review and merge timestamp.")
    else:
        med, p90 = _median(ttm), _percentile(ttm, 90)
        W("   median = %s   p90 = %s   (n=%d merged units)"
          % (_fmt_dur(med), _fmt_dur(p90), len(ttm)))
        # Ruling R6: the active/waiting split needs wall_clock_seconds; when no
        # row carries it, say so rather than implying an active fraction.
        any_wc = any(d.get("wall_clock_seconds") is not None
                     for d in decisions if d["unit_id"] in merged_units)
        if not any_wc:
            W("   active-review fraction: not captured (no rows carry wall_clock_seconds)")
        elif active_frac:
            af = sum(active_frac) / len(active_frac)
            W("   mean active-review fraction = %.0f%% (rest is waiting — often on"
              % (100 * af))
            W("   the human; spec §3.5 says split these, don't optimise waiting).")
    W("")

    # ---- 3.6 evidence-inflation rate (per submitting role) ---------------- #
    W("-- Evidence-inflation rate (per reviewer_role) " + "-" * 20)
    infl_num = defaultdict(int)
    infl_den = defaultdict(int)
    for d in decisions:
        ec, ev = d.get("evidence_claimed"), d.get("evidence_verified")
        if ec in LADDER and ev in LADDER:
            role = d.get("reviewer_role", "?")
            infl_den[role] += 1
            if LADDER[ec] > LADDER[ev]:
                infl_num[role] += 1
    if not infl_den:
        W("   n/a — no rows where both evidence_claimed and evidence_verified set.")
    for role in sorted(infl_den):
        W("   %-16s inflation = %s" % (role, _pct(infl_num[role], infl_den[role])))
    W("")

    # ---- 4. calibration weights (per reviewer_role) ----------------------- #
    W("-- Calibration weights (per reviewer_role) " + "-" * 24)
    W("   correlate verdict severity (pass<PWRC<hold<fail) vs defect_surfaced;")
    W("   floor = %d verified-outcome samples; below floor -> weight 0.0." % CALIB_FLOOR)
    role_rows = defaultdict(list)
    role_models = defaultdict(set)
    for d in decisions:
        if d.get("defect_surfaced") is not None and d.get("verdict") in VERDICT_SEVERITY:
            role_rows[d.get("reviewer_role", "?")].append(d)
            role_models[d.get("reviewer_role", "?")].add(d.get("reviewer_model"))
    if not role_rows:
        W("   n/a — no role has any verified outcomes yet. All roles: weight 0.0")
        W("   (uncalibrated = fully verified, never less — spec §4 safe default).")
    for role in sorted(role_rows):
        drows = role_rows[role]
        n = len(drows)
        xs = [VERDICT_SEVERITY[d["verdict"]] for d in drows]
        ys = [1 if d.get("defect_surfaced") else 0 for d in drows]
        r = _pearson(xs, ys)
        if n < CALIB_FLOOR:
            W("   %-16s weight = 0.0  [BELOW FLOOR: n=%d < %d; self-assessment"
              % (role, n, CALIB_FLOOR))
            W("   %-16s               ignored, full verification applies]" % "")
        else:
            w = _weight_from_r(r)
            rtxt = "undefined" if r is None else "%.3f" % r
            note = "" if w > 0 else "  (noise/inverted -> 0.0)"
            W("   %-16s weight = %.2f  [n=%d, r=%s]%s" % (role, w, n, rtxt, note))
        if len(role_models[role]) > 1:
            W("   %-16s               CAVEAT: >1 reviewer_model seen (%s) — a model"
              % ("", ", ".join(str(m) for m in sorted(role_models[role], key=str))))
            W("   %-16s               change resets calibration (spec §4); this weight" % "")
            W("   %-16s               mixes models and must not be trusted as-is." % "")
    W("")
    W("Not computable from ledger fields alone (stated per spec, not silently")
    W("skipped): the master calibration enable-switch state (a project binding);")
    W("model-change reset timing beyond detecting >1 model per role; and the")
    W("repeat-rate lane denominator (needs catalog codification dates).")
    W("=" * 68)
    print("\n".join(out))
    return 0


def _iso_delta_seconds(a, b):
    """Seconds between two ISO-8601 timestamps, stdlib-only."""
    import datetime
    try:
        da = datetime.datetime.fromisoformat(a.replace("Z", "+00:00"))
        db = datetime.datetime.fromisoformat(b.replace("Z", "+00:00"))
        return (db - da).total_seconds()
    except (ValueError, AttributeError):
        return None


def _fmt_dur(seconds):
    if seconds is None:
        return "n/a"
    h = seconds / 3600.0
    if h >= 1:
        return "%.1fh" % h
    return "%.0fm" % (seconds / 60.0)


# --------------------------------------------------------------------------- #
# CLI                                                                        #
# --------------------------------------------------------------------------- #

def build_parser():
    p = argparse.ArgumentParser(description="Review-ledger reference tool (framework D5b).")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_schema_defaults(sp):
        sp.add_argument("--schema", default=HERE + "/ledger.schema.json",
                        help="path to ledger.schema.json")
        sp.add_argument("--ledger", default=DEFAULT_LEDGER, help="ledger .jsonl path")

    a = sub.add_parser("append", help="validate one row and append to the ledger")
    add_schema_defaults(a)
    a.add_argument("--row-json", help="row as a JSON string (else read stdin)")
    a.set_defaults(func=cmd_append)

    c = sub.add_parser("check", help="validate every row in the ledger")
    add_schema_defaults(c)
    c.set_defaults(func=cmd_check)

    pr = sub.add_parser("project", help="project a review-output into a decision row")
    pr.add_argument("--schema", default=HERE + "/ledger.schema.json")
    pr.add_argument("--review-output-schema", default=HERE + "/review-output.schema.json")
    pr.add_argument("--review-json", help="review-output as JSON string (else stdin)")
    pr.add_argument("--ledger-id", required=True)
    pr.add_argument("--schema-version", type=int, default=1)
    pr.add_argument("--unit-id", required=True)
    pr.add_argument("--unit-kind", required=True,
                    choices=["code", "spec", "asset", "doc", "pack", "config"])
    pr.add_argument("--unit-kind-raw", default=None,
                    help="ruling R5: project's own unit-kind label, preserved verbatim "
                         "when the canonical map is lossy (also read from review-output)")
    pr.add_argument("--lane", required=True)
    pr.add_argument("--stage", required=True,
                    choices=["subagent-self", "lead-review", "design-advisor",
                             "code-advisor", "automated-gate", "merge", "human-final"])
    pr.add_argument("--stage-raw", default=None,
                    help="ruling R5: project's own stage label, preserved verbatim "
                         "when the canonical map is lossy (also read from review-output)")
    pr.add_argument("--round", type=int, default=0)
    pr.add_argument("--reviewer-role", default=None)
    pr.add_argument("--reviewer-model", default=None)
    pr.add_argument("--reviewer-effort", default=None,
                    choices=["low", "medium", "high", "max", "deterministic", None])
    pr.add_argument("--timestamp", required=True, help="ISO-8601 UTC of the decision")
    pr.add_argument("--cost-tokens-in", type=int, default=None)
    pr.add_argument("--cost-tokens-out", type=int, default=None)
    pr.add_argument("--cost-usd", type=float, default=None)
    pr.add_argument("--wall-clock-seconds", type=float, default=None)
    pr.set_defaults(func=cmd_project)

    r = sub.add_parser("report", help="compute the metric set from the ledger")
    r.add_argument("--ledger", default=DEFAULT_LEDGER)
    r.set_defaults(func=cmd_report)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
