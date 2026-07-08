# Context Injection — the failure point is the briefing, not the agent

## What it is

The load-bearing observation that in multi-agent work, the dominant failure mode is **under-briefing**, not weak agents. A capable model handed an incomplete context will confidently produce a wrong answer — an advisor missing the decision surfaces reports ratified law as open; a reviewer missing the gate list misses the gap. The mechanism is a **briefing kit**: a checklist of exactly what every dispatched agent's prompt must carry, plus a hard requirement that review/verify agents return *structured* output (a schema) so nothing arrives as prose to re-parse. This is where effort is spent — not on picking a stronger model, but on assembling the context the model needs to be right, and on running the workflow as structure rather than improvisation (which matters most when the executing model is weaker or simply different from the one the pattern was written on).

## The protocol

### The briefing kit — every dispatched agent's prompt carries:

1. **The decision layer — both surfaces.** The closed decision records (issue/ticket identifiers) *and* the canonical ruling files. One surface is not enough; an agent with only the register will call ratified decisions nonexistent (see the two-surface-rule mechanism).
2. **The relevant rulings/law** for the lane the agent is working — not the whole corpus, the slice that bears on its task.
3. **The workplan** the team/task is executing, so the agent knows the intended scope and can distinguish "gap" from "out of scope."
4. **The specific gate list** the work is checked against — the exact checks that must be green, by name — plus the Definition-of-Done / evidence standard the deliverable must meet.
5. **A structured-output schema.** Review and verify agents are *forced* to a schema (e.g. `gate_results` / `findings` / `merge_recommendation` as JSON), so results arrive machine-readable and nothing has to be re-parsed from prose. Prose review output is a re-parsing tax and a drift source.

### Running the workflow:

6. **Spend the highest-effort configuration on VERIFY stages, not drafting stages.** One reviewer per item plus an adversarial verifier per item; independent items proceed independently (never barrier them on each other).
7. **Structure over improvisation.** Run the workflow patterns as written; verify adversarially by default; take smaller batches per turn. This is explicit compensation for running the role on a weaker or different model than the one the patterns were authored on.
8. **When established context conflicts with a fresh read, STOP and reconcile explicitly** — do not silently pick one. (This is the override rule from the memory-trust-order mechanism, applied inside a dispatched agent.)
9. **After any content workflow, check the shared/main tree for rogue writes.** Authoring agents return content to be landed through the normal path; they do not write to the main tree. Verify they didn't.

## Why it exists

- The core claim is stated verbatim in `studio:docs/kb/director-handbook.md` §5: "Context injection is the failure point, not agent quality. Every agent prompt carries: the decision-issue layer… the ruling files, the team's workplan, and the specific gate list. An under-briefed advisor confidently reports stale law."
- The both-surfaces injection requirement and its earning incident are in `studio:docs/kb/director-handbook.md` §3 and the §6 failure catalog: an advisor given only the register "called three ratified decisions nonexistent" — the fix was to inject decision records *and* register into every agent prompt.
- The structured-output requirement is in `studio:docs/kb/director-handbook.md` §5: agents are "forced to STRUCTURED output (a JSON schema of gate_results / findings / merge_recommendation, so nothing arrives as prose to re-parse)," with a committed worked example of the multi-agent shape referenced there.
- Highest-effort-on-verify and independent-items-proceed-independently are in the same §5.
- The structure-over-improvisation guidance and the stop-and-reconcile rule are the model-delta compensations in `studio:docs/kb/director-handbook.md` §8, written because the one observed miss-class when the role was run mid-stream on a different model was "improvised judgment under incomplete context."
- The rogue-write check is in `studio:docs/kb/director-handbook.md` §5: "Agents may not write to the main tree… After any content workflow, `git status` the main tree for rogue writes (it has happened twice)."

## Failure modes of the mechanism itself

- **Incomplete kit.** Any one item omitted (usually one of the two decision surfaces, or the gate list) reproduces the confident-stale-law failure. The kit is a checklist precisely so nothing is dropped under momentum.
- **Prose slips back in.** A review agent returns findings as prose "just this once," and the re-parse introduces drift. The schema is mandatory for verify stages, not a nicety.
- **Briefing bloat.** Injecting *everything* (the whole ruling corpus, every workplan) dilutes the signal and blows the context budget — the agent skims. Inject the relevant slice, not the archive.
- **Barrier coupling.** Making independent items review each other holds green work hostage to unrelated work. One verifier per item; independent items independent.
- **Silent conflict resolution.** An agent that hits an established-context-vs-fresh-read conflict and picks one silently propagates a wrong choice downstream. The stop-and-reconcile branch must be a hard stop.
- **Effort inverted.** Spending the strongest model on drafting and a weak one on verification gets it backwards — verification is where the strongest configuration belongs.

## What varies per project (bindings)

The exact surfaces and paths injected (which register, which tracker, which workplan location); the schema field names for structured review output; the named gate list per lane; the harness's actual workflow/orchestration tool (or parallel subagent dispatch if it lacks one); the DoD/evidence standard; and the command used to check the shared tree for rogue writes. Declare the injectable surfaces and the review schema in the project's bindings — the *shape* (a complete briefing kit + forced-schema verify output + structure-over-improvisation + stop-and-reconcile + rogue-write check) is the mechanism.
