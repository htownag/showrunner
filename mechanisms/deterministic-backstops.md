# Deterministic Backstops — an LLM never guards an invariant last

## What it is

The principle that any invariant the project must not violate is compiled into a **deterministic gate** — a lint, hook, or test that fails closed — and that an LLM is never the *last* line of defense for it. LLM judgment *proposes* (it drafts, it flags, it recommends); deterministic gates *dispose* (they decide pass/fail). The strongest form is the multi-consumer pattern: one canonical machine-readable table of the invariant, enforced at several points in the flow — auto-fix before the work is reviewed, validation of the reviewer's own claims, and a final backstop at the output boundary — so a stochastic model in the loop can never let a violation ship regardless of the roll. Carve-outs are first-class citizens of the table, because real invariants have exceptions: verbatim/quoted text must never be silently rewritten, and a regulated context can *invert* a prohibition into a requirement.

## The protocol

1. **For each invariant, name a deterministic gate.** If a rule matters, there is a lint/hook/test that fails closed when it breaks. "The reviewer will catch it" is not a gate — the reviewer is an LLM and may not.
2. **One canonical table, multiple enforcement points.** Put the invariant (the lexicon, the schema, the banned set) in one place and consume it at every enforcement point. The proven three-consumer shape:
   - **Draft post-process (auto-fix):** deterministically correct the LLM's draft *before* the review gate, so the reviewer never burns a rejection on something a regex fixes.
   - **Reviewer-claim validation:** when the LLM reviewer flags a violation, validate its claim against the same table — downgrade false positives instead of letting them gate good work.
   - **Output-boundary backstop:** a final idempotent check at the write/ship boundary, independent of everything upstream.
3. **Carve-outs are part of the table, not afterthoughts.**
   - **Never silently rewrite quoted/verbatim material** — carve quoted spans out before applying substitutions (rewriting a verbatim quotation in a legal or evidentiary artifact is itself the harm).
   - **A regulated context can invert a prohibition** — the same term that is banned in one document type is *required* in another; the gate keys the carve-out on the context (the document/report type) and skips or inverts accordingly.
4. **Schema and its guard change in the same diff.** When the invariant's data (a schema, an event registry, a banned list) changes, the test/guard that enforces it changes in the *same* commit — never schema-only, never guard-only.
5. **Verify the output artifact, not the code intent.** "Enforced in the core" is an overclaim until you grep for call sites — a named locus with zero callers is decorative. Confirm the gate actually runs on the real artifact and check the *output*, not what the code was meant to do.
6. **Idempotence on rerun.** A gate that mutates (an auto-fix, a register append) must be safe to re-run after a crash: a replacement must not re-create its own match pattern, and any idempotence guard keys on a unique fragment of the *new* text, not on an old-count alone. Re-verify entity counts after any rerun.
7. **Run the gate from inside the tree under review.** A repo-root-anchored lint invoked from another working tree silently validates the *wrong* tree — local green, CI red. Run gates inside the tree being gated; treat local green as advisory and the merge-ref CI run as the real gate.

## Why it exists

- The three-consumer pattern is implemented and documented in `pipeline:gateway/core/voice_lint.py` ("Three consumers, one table": REPORT_DRAFTING post-process auto-fix; ReviewerVerdict defect validation that downgrades false positives; DocxWriter final write-time backstop). Its module docstring records the earned reason both the auto-fix and the reviewer-claim validation exist: a 2026-06-10 run "rejected twice because the reviewer first prescribed 'biological growth' and then rejected it."
- The verbatim carve-out is in the same file: quoted spans are stripped before substitution because "silently rewriting a verbatim quotation in a litigation exhibit is impeachment material" (`pipeline:gateway/core/voice_lint.py`, `enforce_vocabulary` / `strip_quoted_spans`).
- The prohibition-inversion carve-out is in the same file: a regulated report type where the normally-prohibited term is the *required* term skips the mold-family substitutions (`report_type_allows_mold_terms`, `_MOLD_TERM_REPORT_TYPES`) — "the voice analogue of the legal cost/certainty carve-outs."
- Deterministic structural backstops guarding a stochastic writer *and* a stochastic reviewer are in the same file: `count_forensic_triplet_labels` / `letter_missing_opinions_section` exist because "run 20260619-143218 APPROVED a letter that was missing its Opinions section" — the LLM reviewer alone was insufficient, so the invariant was compiled.
- The invariants-as-gates posture across a different stack: `studio:tools/ip_lint.py` (franchise-term lint, fail-closed), `studio:tools/naming_register_check.py` (a shipped name with no complete knockout-search record fails the build; zero entries parsed = fail closed), and `studio:tools/telemetry_lint.py`.
- The same-diff rule is stated in `studio:docs/kb/director-handbook.md` §3: "`schema.yaml` and the exactly-these-events guard test change in the SAME diff… even schema-only rows (the #67 lesson)."
- "A named locus with zero callers is decorative" and "verify the OUTPUT asset, not the code intent" are both in `studio:docs/kb/director-handbook.md` §6, as is the idempotence receipt (a replacement whose output re-contains its match pattern double-applied on a crash-rerun; guard on a unique fragment of the new text — 2026-07-07, #117) and the wrong-tree-lint receipt (a repo-root-anchored lint invoked from another tree validated the wrong tree — local green, CI red — 2026-07-07, #117).

## Failure modes of the mechanism itself

- **Decorative gate.** The gate exists but nothing calls it, or it isn't wired into CI — pure theater. Grep for call sites; confirm it runs on the merge ref.
- **Intent-not-output validation.** The gate checks that the code *tried* to enforce the invariant, not that the artifact actually complies. Assert against the output.
- **Carve-out too broad.** An over-wide exemption silently permits the invariant to break (e.g. treating too much text as "quoted"). Carve-outs must be as narrow as the real exception.
- **Reviewer claim trusted blind.** If the LLM reviewer's flags aren't validated against the canonical table, its false positives gate good work and its false negatives ship violations. Validate both directions.
- **Schema/guard drift.** Changing the data and the enforcement in separate diffs lets them fall out of sync — the #67 class. Same diff, always.
- **Rerun double-apply.** A mutating gate that isn't idempotent corrupts on crash-rerun. Key guards on new-text fragments; re-verify counts.
- **Wrong-tree green.** A root-anchored gate run from the wrong tree gives false confidence. Run inside the tree; trust only the merge-ref run.

## What varies per project (bindings)

The set of invariants a project holds; the specific gates and their tool/command names; where the canonical table lives (a Python module, a YAML schema, a banned-terms file); the carve-out set (which contexts invert which rules, what counts as "verbatim"); which enforcement points exist in the flow (a two-process pipeline has different seams than a code repo); and whether gates run as pre-commit hooks, CI checks, or both. Declare the invariant→gate table in the project's bindings — the *shape* (compile invariants into fail-closed gates, one table many consumers, carve-outs first-class, same-diff schema+guard, verify the output, idempotent reruns, run inside the tree) is the mechanism.
