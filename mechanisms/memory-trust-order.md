# Memory Trust Order — which surface is authoritative for which fact class

## What it is

A written ranking that says, for each *class* of fact, which stored surface is authoritative — and, critically, when auto-loaded project memory is *not* the one to believe. Memory (the auto-loaded collaboration layer) is trustworthy for the things it updates continuously and owns: collaboration patterns, gotchas, human preferences, a pointer-index of where law lives. But for **project law and current state**, the trust order inverts: the durable law surfaces (a rulings register, closed decision records, the git log) beat memory, because memory is refreshed at *session end* — a fresh boot can therefore find it one session stale. The mechanism is to classify fact classes up front, assign each an authoritative surface, write the order down where every session reads it, and define the narrow conditions under which a single fresh file read may override established context.

## The protocol

1. **Classify fact classes and assign each an authoritative surface. Two default classes:**
   - **Collaboration layer** (how the human works, gotchas, conventions, the index of where law lives): **memory is authoritative.** Trust it over a single fresh file read.
   - **Law & state layer** (ratified decisions, current project/roadmap state, what shipped): **the durable surfaces beat memory** — the rulings register + closed decision records + `git log`. The log is ground truth when tracking surfaces lag it.
2. **Write the trust order down** in the operating handbook / boot doc, not just in one memory file. Every session must be able to read the order at boot without deriving it.
3. **State *why* memory goes stale, in the doc.** Memory is a pointer updated as a session-end duty; a boot that happens before the previous session shut down clean will read memory one session behind. This is a designed property, not a bug — the doc must name it so no one over-trusts memory for state.
4. **Override rule for a conflicting fresh read.** When established context (memory, the handbook, prior handoff docs, recent commits) says X and a single fresh file read says Y:
   - **Do not silently switch to Y.**
   - Ask: is this file the *override layer* or a *stale upstream default*? Many systems have a base file overridden by a local file (config → config-local, env vars, an overlay).
   - Check the override layer *before* changing course or propagating the change into docs.
   - If still genuinely in conflict, **stop and reconcile explicitly** (surface it) rather than picking one silently.
5. **Human observation outranks all stored surfaces.** A report from the human that something behaved a certain way in play is ground truth; instrument and investigate, never theorize the observation away. (This is the top of the trust order and belongs in it.)
6. **Keep the pointers current at shutdown.** The state-pointer and law-index memory entries are updated in the session-end ritual, so the next boot's "memory is one session stale" window stays exactly one session, never more.

## Why it exists

- The inverted trust order is stated verbatim in `studio:docs/kb/director-handbook.md` §2 item 3: "trust it for COLLABORATION PATTERNS over fresh single-file reads. For design law and studio state the trust order INVERTS: the rulings register + closed decision issues + git log beat memory — memory is a pointer that goes stale between sessions; updating it is a session-end duty, so a fresh boot may find it one session behind."
- The override rule was earned from a concrete incident: `validation:memory/feedback-trust-established-context.md` records that on 2026-04-28 a single fresh read of an upstream `config` default overrode a path that established context (the constitution's hard rule + the session's own handoff doc) already had correct; the agent rewrote the handoff doc and tried to deploy to a non-existent path, when the known override layer (`config-local`) held the truth. Cost: the human's time and eroded trust.
- The rule is carried as a durable feedback rule (not only a memory) so it loads every session: `validation:CLAUDE.md` ("Trust established context over a single fresh read… check the override layer BEFORE switching").
- Human-observation-as-ground-truth is a hard rule in both proving grounds: `studio:CLAUDE.md` hard rule 6 and `validation:CLAUDE.md` ("Don't dismiss in-game observations").

## Failure modes of the mechanism itself

- **Over-trusting memory for state.** Treating the auto-loaded pointer as authoritative for law/state and acting on a ruling that has since changed. The fix is the written inversion — for law, go to the register/decisions/log.
- **Over-correcting into distrust.** The opposite failure: never trusting memory, re-deriving everything from fresh reads every session, which is exactly the time-waste the override incident produced. Collaboration facts *should* be trusted from memory.
- **No written order.** If the trust order lives only in one person's head (or one model's context), each session guesses, and the guess flips with model changes. It must be a document.
- **Reconcile-skipping.** The "stop and reconcile" branch is the safety valve; under momentum an agent skips it and silently picks one surface. Weaker or different models are especially prone to this — structure it as a hard stop.
- **Stale-window creep.** If the session-end ritual is skipped, memory falls *more* than one session behind and the "one session stale" assumption underlying the whole order breaks. The order depends on a clean shutdown.

## What varies per project (bindings)

The exact authoritative surfaces per fact class (a rulings register vs. an issue tracker vs. a decisions log; git log always qualifies); the override-layer chain to check before believing a fresh read (which base/local file pair, which env vars, which overlay); the names of the state-pointer and law-index memory entries; and the session cadence that sets the stale window. Declare the surface-per-class table in the project's bindings — the *shape* (classify, assign, write it down, define the override condition, human observation on top) is the mechanism.
