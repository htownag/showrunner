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
    judgment. No automated weight changes a verdict.

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
    """Yield (lineno, row_dict). Raises on JSON error (loud)."""
    rows = []
    try:
        with open(ledger_path) as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                rows.append((i, json.loads(line)))
    except FileNotFoundError:
        return []
    return rows


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
    rows = _read_rows(args.ledger)
    if not rows:
        print("check: %s is empty or absent — nothing to validate." % args.ledger)
        return 0
    bad = 0
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
        print("check: FAILED — %d problem(s) across %d rows." % (bad, len(rows)), file=sys.stderr)
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


# --------------------------------------------------------------------------- #
# Subcommand: report                                                         #
# --------------------------------------------------------------------------- #

def cmd_report(args):
    rows = _read_rows(args.ledger)
    out = []
    W = out.append
    W("=" * 68)
    W("REVIEW LEDGER DASHBOARD  (source: %s)" % args.ledger)
    W("=" * 68)
    if not rows:
        W("Ledger is empty or absent. Nothing to report yet.")
        W("Stage-0 capture has produced no rows — wire the append adapter first")
        W("(see boot-integration.md). All metrics below become available once")
        W("decision rows and back-filled outcome rows exist.")
        print("\n".join(out))
        return 0

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
    W("   caught = stage raised blocker/major AND blocked (fail/hold);")
    W("   escaped = merged unit with defect_surfaced and escape_stage==S.")
    caught = defaultdict(int)
    escaped = defaultdict(int)
    for d in decisions:
        sev = d.get("findings_by_severity", {})
        raised_major = (sev.get("blocker", 0) + sev.get("major", 0)) > 0
        if raised_major and d.get("verdict") in ("fail", "hold"):
            caught[d["stage"]] += 1
    for d in decisions:
        if d.get("defect_surfaced") is True and d.get("escape_stage"):
            escaped[d["escape_stage"]] += 1
    stages = sorted(set(caught) | set(escaped))
    if not stages:
        W("   n/a — no caught defects and no attributed escapes yet.")
    for s in stages:
        c, e = caught[s], escaped[s]
        W("   %-16s catch_rate = %s" % (s, _pct(c, c + e)))
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
        W("   %-16s false_hold = %s" % (s, _pct(false_holds[s], holds[s])))
    W("")

    # ---- 3.3 cost per merged unit ----------------------------------------- #
    W("-- Cost per merged unit " + "-" * 44)
    merged_units = {d["unit_id"] for d in decisions if d.get("merged") is True}
    if not merged_units:
        W("   n/a — no merged units recorded yet.")
    else:
        usd_rows = [d for d in decisions if d["unit_id"] in merged_units and d.get("cost_usd") is not None]
        tok_rows = [d for d in decisions if d["unit_id"] in merged_units]
        total_usd = sum(d["cost_usd"] for d in usd_rows)
        total_tok = sum((d.get("cost_tokens_in") or 0) + (d.get("cost_tokens_out") or 0) for d in tok_rows)
        nmerged = len(merged_units)
        W("   merged units: %d" % nmerged)
        if usd_rows:
            W("   cost_usd / merged unit   = $%.4f  (over %d priced rows)" % (total_usd / nmerged, len(usd_rows)))
        W("   tokens   / merged unit   = %d" % (total_tok // nmerged))
        wc = [d.get("wall_clock_seconds") for d in tok_rows if d.get("wall_clock_seconds") is not None]
        if wc:
            W("   wall-clock / merged unit = %.0fs" % (sum(wc) / nmerged))
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
        if active_frac:
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
    pr.add_argument("--lane", required=True)
    pr.add_argument("--stage", required=True,
                    choices=["subagent-self", "lead-review", "design-advisor",
                             "code-advisor", "automated-gate", "merge", "human-final"])
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
