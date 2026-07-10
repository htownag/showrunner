#!/usr/bin/env python3
"""Golden-fixture conformance suite for ledger.py (workplan H3).

Stdlib-only (`python3 -m unittest discover -s measurement/tests -t .`). Each test
pins EXACT metric behavior against a small fixture ledger under fixtures/, one per
ratified ruling behavior (R1-R6). Where a metric value is the subject, the test
asserts on the exact computed number (dict equality on caught/escaped/pending
ints, or the exact rate string like "100.0% (2/2)"), never a loose substring.

The suite is the framework's first compiled gate: deliberately break any ruling in
ledger.py (drop the hold_substantiated gate, stop deduping, silently skip a
malformed line, render a zero cost) and a test here turns red.
"""

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MEASUREMENT_DIR = os.path.dirname(TESTS_DIR)
FIX = os.path.join(TESTS_DIR, "fixtures")
sys.path.insert(0, MEASUREMENT_DIR)

import ledger  # noqa: E402

SCHEMA = os.path.join(MEASUREMENT_DIR, "ledger.schema.json")
RO_SCHEMA = os.path.join(MEASUREMENT_DIR, "review-output.schema.json")
EXAMPLE_LEDGER = os.path.join(MEASUREMENT_DIR, "example-ledger.jsonl")


def fix(name):
    return os.path.join(FIX, name)


def catch_of(name):
    """Return (catch_metrics, malformed, decisions) for a fixture ledger."""
    rows, malformed = ledger._read_rows(fix(name))
    decisions = list(ledger._fold(rows).values())
    return ledger._catch_metrics(decisions), malformed, decisions


def run_main(argv):
    """Run ledger.main(argv), capturing (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = ledger.main(argv)
    return code, out.getvalue(), err.getvalue()


def report_text(path):
    code, out, _ = run_main(["report", "--ledger", path])
    return code, out


class TrueCatch(unittest.TestCase):
    """R2/R3: a fail carrying a blocker AND hold_substantiated=true is a catch."""

    def test_metrics(self):
        metrics, malformed, _ = catch_of("true_catch.jsonl")
        self.assertEqual(malformed, [])
        self.assertEqual(metrics, {"code-advisor": {"caught": 1, "escaped": 0, "pending": 0}})

    def test_report_rate_is_one_over_one(self):
        code, out = report_text(fix("true_catch.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("catch_rate = 100.0% (1/1)", out)


class SubstantiatedHold(unittest.TestCase):
    """R2: a substantiated hold counts as a catch (the falsified spec routing)."""

    def test_metrics(self):
        metrics, _, _ = catch_of("substantiated_hold.jsonl")
        self.assertEqual(metrics["code-advisor"]["caught"], 1)
        self.assertEqual(metrics["code-advisor"]["pending"], 0)


class FalseHold(unittest.TestCase):
    """R2/R3: hold_substantiated=false is not a catch; it feeds false-hold."""

    def test_excluded_from_catch(self):
        metrics, _, _ = catch_of("false_hold.jsonl")
        # No caught, no pending — a false hold is neither.
        self.assertEqual(metrics, {})

    def test_counted_in_false_hold(self):
        code, out = report_text(fix("false_hold.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("false_hold = 100.0% (1/1)", out)


class PendingOutcome(unittest.TestCase):
    """R3: blocked+major with hold_substantiated null is PENDING, excluded."""

    def test_metrics(self):
        metrics, _, _ = catch_of("pending.jsonl")
        self.assertEqual(metrics, {"code-advisor": {"caught": 0, "escaped": 0, "pending": 1}})

    def test_report_excludes_and_reports(self):
        code, out = report_text(fix("pending.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("catch_rate = n/a (0 resolved samples)", out)
        self.assertIn("pending (excluded from rate): 1 unit(s)", out)


class RepeatedRound(unittest.TestCase):
    """R4: two rounds, same unit+stage -> one catch, not two."""

    def test_dedup_to_one(self):
        metrics, _, decisions = catch_of("repeated_round.jsonl")
        self.assertEqual(len(decisions), 2)  # two decision rows folded
        self.assertEqual(metrics["code-advisor"]["caught"], 1)


class EscapedDefect(unittest.TestCase):
    """R4: escaped dedupes by (unit_id, escape_stage) at unit level."""

    def test_dedup_to_one(self):
        metrics, _, _ = catch_of("escaped.jsonl")
        self.assertEqual(metrics["lead-review"]["escaped"], 1)


class UnknownOutcome(unittest.TestCase):
    """A merged unit with defect_surfaced null is unknown, not clean/caught."""

    def test_excluded_from_catch(self):
        metrics, _, _ = catch_of("unknown_outcome.jsonl")
        self.assertEqual(metrics, {})

    def test_report_header_shows_unknown_denominator(self):
        code, out = report_text(fix("unknown_outcome.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("outcome: 0/1 (0%)", out)
        self.assertIn("unknown denominator", out)


class MalformedRowQuarantine(unittest.TestCase):
    """R1: report quarantines a malformed line LOUD; check is fatal on it."""

    def test_report_quarantines_and_still_renders(self):
        code, out = report_text(fix("malformed_report.jsonl"))
        self.assertEqual(code, 0)  # under the 10% floor -> renders
        self.assertIn("QUARANTINE: 1 malformed line(s)", out)
        self.assertIn("malformed line number(s): 6", out)
        self.assertIn("Reviewer catch rate", out)  # metrics still rendered

    def test_read_rows_surfaces_line_number(self):
        rows, malformed = ledger._read_rows(fix("malformed_report.jsonl"))
        self.assertEqual([ln for ln, _ in malformed], [6])
        self.assertEqual(len(rows), 10)

    def test_check_is_fatal(self):
        code, _, err = run_main(["check", "--schema", SCHEMA,
                                 "--ledger", fix("malformed_report.jsonl")])
        self.assertEqual(code, 1)
        self.assertIn("line 6: malformed JSON", err)


class MalformedOverFloor(unittest.TestCase):
    """R1: >10% malformed -> report REFUSES to render metrics, exit 1."""

    def test_report_refuses(self):
        code, out = report_text(fix("malformed_fatal.jsonl"))
        self.assertEqual(code, 1)
        self.assertIn("REFUSING to render metrics", out)
        self.assertNotIn("Reviewer catch rate", out)

    def test_check_fatal_both_lines(self):
        code, _, err = run_main(["check", "--schema", SCHEMA,
                                 "--ledger", fix("malformed_fatal.jsonl")])
        self.assertEqual(code, 1)
        self.assertIn("line 2: malformed JSON", err)
        self.assertIn("line 4: malformed JSON", err)


class DanglingAmendment(unittest.TestCase):
    """An amendment referencing an unknown decision: fold ignores, check flags."""

    def test_fold_ignores(self):
        metrics, _, decisions = catch_of("dangling_amendment.jsonl")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(metrics, {})  # dangling escape not folded onto anything

    def test_report_survives(self):
        code, _ = report_text(fix("dangling_amendment.jsonl"))
        self.assertEqual(code, 0)

    def test_check_flags(self):
        code, _, err = run_main(["check", "--schema", SCHEMA,
                                 "--ledger", fix("dangling_amendment.jsonl")])
        self.assertEqual(code, 1)
        self.assertIn("references unknown decision row", err)


class ModelChangeCaveat(unittest.TestCase):
    """A role seen under >1 reviewer_model draws the calibration-reset caveat."""

    def test_report_caveat(self):
        code, out = report_text(fix("model_change.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("CAVEAT: >1 reviewer_model", out)


class StageRawMapping(unittest.TestCase):
    """R5: a v2 stage_raw row validates, annotates its per-stage line, and
    round-trips through `project`."""

    def test_fixture_validates(self):
        code, _, _ = run_main(["check", "--schema", SCHEMA,
                               "--ledger", fix("stage_raw.jsonl")])
        self.assertEqual(code, 0)

    def test_report_annotates_stage(self):
        code, out = report_text(fix("stage_raw.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("code-advisor (raw: adversarial-sweep)", out)
        self.assertIn("catch_rate = 100.0% (1/1)", out)

    def test_project_round_trips_raw_fields(self):
        with open(fix("review_output_stage_raw.json")) as fh:
            ro_json = fh.read()
        code, out, err = run_main([
            "project",
            "--schema", SCHEMA,
            "--review-output-schema", RO_SCHEMA,
            "--review-json", ro_json,
            "--ledger-id", "RL-RT-1",
            "--schema-version", "2",
            "--unit-id", "u-rt",
            "--unit-kind", "doc",
            "--lane", "framework",
            "--stage", "code-advisor",
            "--round", "0",
            "--timestamp", "2026-07-01T00:00:00Z",
        ])
        self.assertEqual(code, 0, err)
        row = json.loads(out)
        # Raw labels flowed from the review-output object into the row verbatim.
        self.assertEqual(row["stage_raw"], "adversarial-sweep")
        self.assertEqual(row["unit_kind_raw"], "framework-deliverable")
        # And the projected row validates against the (v2) ledger schema.
        schema = ledger._load_schema(SCHEMA)
        self.assertEqual(ledger.validate(row, schema, schema), [])

    def test_project_flag_overrides_raw(self):
        # A --stage-raw flag round-trips even when the review-output omits it.
        ro_json = json.dumps({
            "verdict": "pass", "reviewer_role": "advisor", "reviewer_effort": "high",
            "evidence_claimed": "L2", "findings": [], "merge_recommendation": "merge",
        })
        code, out, err = run_main([
            "project", "--schema", SCHEMA, "--review-output-schema", RO_SCHEMA,
            "--review-json", ro_json, "--ledger-id", "RL-RT-2", "--schema-version", "2",
            "--unit-id", "u-rt2", "--unit-kind", "code", "--lane", "lane-a",
            "--stage", "code-advisor", "--stage-raw", "director-verification",
            "--round", "0", "--timestamp", "2026-07-01T00:00:00Z",
        ])
        self.assertEqual(code, 0, err)
        row = json.loads(out)
        self.assertEqual(row["stage_raw"], "director-verification")
        self.assertNotIn("unit_kind_raw", row)  # omitted when neither flag nor RO set it


class CostSuppression(unittest.TestCase):
    """R6: no cost/wall-clock fields -> 'not captured', never a zero."""

    def test_not_captured_when_absent(self):
        # pending.jsonl carries no cost fields on any merged-unit row.
        code, out = report_text(fix("pending.jsonl"))
        self.assertEqual(code, 0)
        self.assertIn("cost: not captured (no rows carry cost fields)", out)
        self.assertIn("wall-clock: not captured", out)
        self.assertNotIn("tokens   / merged unit   = 0", out)

    def test_computed_when_present(self):
        # The bundled example ledger DOES carry cost -> real numbers, no suppression.
        code, out = report_text(EXAMPLE_LEDGER)
        self.assertEqual(code, 0)
        self.assertIn("cost_usd / merged unit", out)
        self.assertNotIn("cost: not captured", out)


class BundledExampleLedger(unittest.TestCase):
    """The CI gate runs `check` on the bundled example ledger; it must pass."""

    def test_check_passes(self):
        code, out, _ = run_main(["check", "--schema", SCHEMA, "--ledger", EXAMPLE_LEDGER])
        self.assertEqual(code, 0)
        self.assertIn("check: OK", out)


if __name__ == "__main__":
    unittest.main()
