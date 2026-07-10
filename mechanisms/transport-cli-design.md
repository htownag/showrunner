# The Transport CLI — Design for a Briefing-Kit Assembler (design only)

*This is a design document, not a shipped mechanism. **No implementation ships in v0.2**, by
ruling: building the transport before the measurement layer is a compiled, trustworthy gate
would optimize the throughput of a pipeline whose instruments still lie. The review ledger's
executable conformance (WORKPLAN H3 — golden fixtures + fixed `ledger.py` + CI gate) is the
precondition; until the gauges pass their own tests, a tool that moves more work through the
loop faster only ships more work past instruments that miscount catches, mix stages, and render
a `tokens/merged unit = 0` that reads as a measurement (WORKPLAN "Inputs and receipts," R1–R6).
Principle 5 (an LLM is never the last line of defense) applies to the measurement surface too: a
measurement that fails open is worse than none. This doc specifies the tool so it can be built
the moment that precondition lands, and names its own staged adoption path so the first cut is
emit-only. The `{{variables}}` convention below is the one from `bindings/boot-prompt-template.md`.*

## What it is

The transport CLI is a thin **briefing-kit assembler**: a stateless tool that renders, from the
bindings and the durable repository surfaces, exactly the payload the human currently assembles
by hand when relaying between a director session and a team session. Its one axiom follows
directly from the statefulness axiom (`mechanisms/boot-shutdown.md`, Principle 3): **the tool
holds no state of its own — state lives in the repo, never in the tool.** Every command is a
pure projection over durable surfaces that already exist; nothing the tool computes is
authoritative, nothing it produces is a new source of truth, and deleting the tool loses no
state because it never held any. It is the operating model's *relay-carries-three-things* rule
(`mechanisms/operating-model.md`, "The copy-paste relay protocol") delivered by tool instead of
by hand — "delivering it by hand instead of by harness changes the transport, not the contract."

It exists to remove one specific toil: the clipboard. In the human-as-message-bus mode
(`mechanisms/operating-model.md`, "The two message-bus modes"), the director session and each
team session run in separate chat surfaces that cannot see each other, and the human carries
state between them by copy-paste. That copy-paste is real friction, but it is not the same thing
as the human's *review*. The tool removes the toil and preserves the review: **it prints exactly
what the human would have pasted**, and the human still reads it, still edits it, still decides
whether to send it. Eyes-on every crossing is kept as law; only the clipboard mechanics are
removed.

Three constraints are stated here as binding law, not as options:

1. **The human still makes every ballot.** The tool never decides anything a ballot decides
   (`mechanisms/ballots.md`). It can *render* an open-ballot list into a `status` view; it can
   never mark one answered. Human decisions crossing the bus are recorded verbatim before
   execution (`mechanisms/ballots.md`, "Recording ratification" — a framework-law rule of the
   same family as CL-006's tree-dirty-until-verification), and the tool does no recording of
   its own.
2. **The human still sees every crossing.** Each command's default is emit-to-stdout for a human
   to read; there is no mode in which a payload crosses from one session to another without the
   human having seen the exact text. "Eyes-on-every-crossing remains a documented *mode*, chosen
   per work class" (WORKPLAN, "Rejected as written," on human-as-bus).
3. **Both bus modes remain supported, and human-as-bus is not debt.** The repo-as-message-bus
   (automated) and human-as-message-bus (hands-on) modes are both first-class
   (`mechanisms/operating-model.md`). The external review called human-as-bus "technical debt";
   that framing is rejected (WORKPLAN, "Rejected as written"). This doc reframes it as **the
   high-touch mode you choose for weighted or early-stage work** — the mode that gives the human
   eyes on every message that crosses, which is often exactly what weighted work wants. The tool
   serves that mode by making it cheaper, not by deprecating it.

## The protocol

**Four commands, each a projection over durable surfaces.**

1. **`boot`** — emit one session's *resolved* boot prompt. Reads the parameterized template
   (`bindings/boot-prompt-template.md`, director or team variant) and the project's bindings
   declaration (`bindings/<project>.md`), resolves every `{{variable}}` from the bindings, and
   prints the finished prompt. This is the "carry the boot prompt" leg of the relay
   (`mechanisms/operating-model.md`, relay item 1): never a bare ask into a cold session. The
   fill-discipline rule is enforced mechanically — an unresolved `{{variable}}` is a hard error,
   not a silent blank, because "a `{{variable}}` left unresolved is a boot prompt that reads a
   surface that does not exist — the session boots blind" (`bindings/boot-prompt-template.md`,
   "Fill discipline"). `boot` resolves the prompt from the *same* bindings values that generate
   the gate roster and lanes, so prompt and gates never disagree.

2. **`dispatch`** — assemble the full relay payload for one unit: the three things every hop
   must carry (`mechanisms/operating-model.md`, relay items 1–3), concatenated into one
   self-sufficient message. That is: (a) the resolved boot prompt from `boot`, so the receiving
   session reconstructs its lane's state from the repo before acting; (b) **the specific ask** —
   the one unit of work, its target Definition-of-Done rung (`mechanisms/done-ladder.md`), and
   the exact gate list it must pass (`bindings/boot-prompt-template.md`, `{{GATE_LIST}}`),
   drawn from the unit's row on the team workplan/tracker; and (c) **the return format** — the
   structured-output schema the director will gate on (`{{OUTPUT_SCHEMA}}`, concretely
   `measurement/review-output.schema.json` and the project's findings / gate-results /
   merge-recommendation shape). "One relayed message should carry one decidable unit, not a
   discussion" — `dispatch` refuses to bundle more than one unit, encoding that rule.

3. **`collect`** — validate a returned structured output against its schema and stage it for the
   director. Takes the reply text (pasted back by the human, or read from a file in Stage 1),
   validates it against the return-format schema `dispatch` named, and on pass stages it where
   the director's next boot reads it; on fail, prints the schema violation and stages nothing.
   This makes the reply "arrive as something to gate, not prose to re-parse"
   (`mechanisms/operating-model.md`, relay item 3). `collect` **validates and stages; it does
   not gate** — it never renders a merge verdict, never records a ratification, never counts a
   catch into the ledger. It hands a schema-valid object to the director, who verifies
   adversarially (Principle 6; `mechanisms/review-pipeline.md`). Schema-valid is not correct
   (Principle 8, compiles is not done): passing `collect` means well-formed, nothing more.

4. **`status`** — render the durable tracking surfaces for a human read. Projects over the same
   surfaces the status page draws from — roadmap, board, ruling register, measurement ledger —
   and prints the human-facing consolidation (`mechanisms/status-page.md`). It is a *read*: "a
   read-only human consolidation of the tracking surfaces, not a new source of truth; the
   surfaces win when they disagree" (`mechanisms/boot-shutdown.md`, "What varies per project").
   `status` never writes `STATUS.md` — regenerating that file is a shutdown act bound to the
   session that changed shared state (`mechanisms/boot-shutdown.md`, shutdown step 2), not a
   thing a stateless transport tool owns.

**The no-state rule, made concrete.** The tool reads bindings and durable surfaces on every
invocation and writes only to stdout (Stage 0) or to a staging path inside the repo that the
director already reads (Stage 1). It keeps no database, no cache of "what was dispatched," no
record of "what came back" — because the repo already is that record. If the tool were deleted
and rebuilt, the next `status` would render the identical view, because the view lives in the
surfaces, not the tool. This is the statefulness axiom applied one level up: just as a session
is disposable because state lives in the repo, the *tool* is disposable for the same reason.

**Both modes, one tool.** In repo-as-message-bus (automated) runs, `dispatch` writes its payload
to a durable path and the next session's boot reads it — no human between sessions. In
human-as-message-bus (hands-on) runs, `dispatch` prints to stdout, the human reads it, and pastes
it into the team surface; `collect` takes the pasted reply. Same command, same payload contract;
the only difference is whether stdout goes to a file the harness reads or to a human who relays.
Naming which bus is in force is still required before relying on either (`mechanisms/operating-model.md`,
"Mode confusion") — the tool does not remove that discipline, and a `--mode` flag makes the
choice explicit rather than assumed.

**Its own Stage-0/1/2 adoption path** (the framework's own graduated-adoption jurisprudence
applied to the tool, mirroring the measurement layer's staged path in
`measurement/boot-integration.md`):

- **Stage 0 — emit-only; the human still pastes.** `boot` and `dispatch` print to stdout; the
  human reads the payload, edits if needed, and copy-pastes it across surfaces exactly as today.
  `collect` validates a pasted-back reply against the schema and prints pass/fail. The tool holds
  no state and touches no file. This stage removes the *assembly* toil (resolving the boot prompt,
  gathering the ask + gates + schema into one message) while keeping the human on every crossing
  and every ratification. It ships first and can ship the moment H3 lands, because it changes the
  transport of a payload the human still fully reads — the lowest-risk possible cut.

- **Stage 1 — `dispatch`/`collect` against files.** The payload is written to and read from
  durable repo paths rather than the clipboard: `dispatch` writes the assembled kit to a staging
  file, `collect` reads a returned structured-output file, validates it, and stages it for the
  director. Still no harness; still human-initiated per hop; still eyes-on (the human reads the
  file). This stage removes the clipboard mechanics while preserving the review, and it is the
  first stage that materially serves the repo-as-message-bus mode.

- **Stage 2 — harness integration.** The tool becomes a step the session harness can invoke:
  `dispatch` hands the payload to a spawned team session and `collect` receives its structured
  reply, under the repo-as-message-bus mode, with the human reviewing at the ballot and merge
  points rather than every hop. This stage is gated on the measurement layer being a trustworthy
  compiled gate (H3 green) *and* on the human explicitly choosing the lower-touch mode for a given
  work class — high-touch human-as-bus remains available and correct for weighted work. Stage 2 is
  the only stage where a crossing can happen without a per-hop human read, and it is reached by a
  deliberate mode choice, never by default.

## Why it exists

- The relay payload the tool assembles is a contract that already exists and is already carried
  by hand every day: "the relay payload *is* the agent briefing kit, delivered by hand instead of
  by harness" (`mechanisms/operating-model.md`, relay item 3). Every director-to-team hop already
  carries the boot prompt, the ask + its gate list, and the required structured-output schema
  (`bindings/example-studio.md` §8; the studio project's director handbook §5, via the
  operating-model receipts). The tool changes who does the assembling, not what is assembled.
- The copy-paste toil is real and repetitive, and repetitive relay is exactly where context gets
  dropped by hand: "pasting a bare ask into a cold team session with no boot prompt, or pasting a
  reply back with no return-format structure" is a named failure mode
  (`mechanisms/operating-model.md`, "Relay context drop"). A tool that always assembles all three
  things closes that failure by construction — the assembler cannot emit a payload missing a leg.
- Eyes-on-every-crossing is worth preserving on its own merits, not merely tolerated: the
  human-as-bus mode "gives the human eyes on every message that crosses — which is often exactly
  what the human wants for weighted or early-stage work" (`mechanisms/operating-model.md`, "The two
  message-bus modes"). The validation project's whole cadence is a human relaying between a
  drafting agent and ground truth, "the review/test loop is the actual quality gate"
  (`mechanisms/operating-model.md` "Why it exists," citing the validation project). The tool must
  not erode this; it removes clipboard mechanics, not human judgment.
- Deferring implementation is the framework's own graduated-adoption jurisprudence (Principle 4;
  Principle 9): a mechanism proves itself as a document before it earns code, exactly as the
  minimal binding profile ships as a document and defers `showrunner init` (WORKPLAN H5, "Rejected
  as written"). The transport CLI earns its first line of code only after the measurement layer it
  would feed is a trustworthy compiled gate (WORKPLAN H7 done-condition; H3).
- The tool is disposable for the same reason its sessions are: state lives in the repo, never in
  the model (Principle 3; `mechanisms/boot-shutdown.md`) — extended to say state lives in the repo,
  never in the *tool*. A stateful transport would recreate, one layer up, the exact failure the
  statefulness axiom exists to prevent: a successor that cannot reconstruct the world because part
  of it lived somewhere ephemeral.

## Failure modes of the mechanism itself

- **The tool becomes an orchestrator.** The gravest failure: a briefing-kit assembler that
  quietly starts *deciding* — auto-answering a ballot, auto-merging a `collect`-passed reply,
  spawning the next unit without a human touch — collapses the author/gate separation and the
  human-makes-every-ballot rule the whole pipeline rests on (`mechanisms/operating-model.md`,
  "Director drafting instead of gating"; `mechanisms/ballots.md`). The guard is definitional:
  `collect` validates and stages but never gates or records; no command marks a ballot answered;
  the director (a session, adversarially verifying — Principle 6) is the only thing that gates.
  Any feature request that would let the tool decide is a design ballot, not a tool change.
- **Payloads drift from the briefing-kit contract.** If `dispatch` starts emitting payloads that
  omit a leg (an ask with no gate list, a boot prompt with unresolved `{{variables}}`, a reply
  with no return schema), it silently reintroduces the relay-context-drop failure it existed to
  close (`mechanisms/operating-model.md`, "Relay context drop"). The guard: the assembler treats
  a missing leg as a hard error, resolves from the same bindings values that generate the gates so
  prompt and gates cannot disagree (`bindings/boot-prompt-template.md`, "Fill discipline"), and
  `collect` refuses any reply that does not validate against the exact schema `dispatch` named.
  The payload contract is the three-things rule; drift from it is a defect, caught by the tool's
  own conformance fixtures (which, like the measurement layer's, must be compiled gates before
  Stage 2 — H3's pattern applied to the transport).
- **State accretes in the tool.** Any cache, database, or "what did I dispatch / what came back"
  memory inside the tool violates the no-state axiom and creates a second, ephemeral source of
  truth that the repo does not know about — the successor reads a false or partial world exactly
  as a dirty shutdown makes it (`mechanisms/boot-shutdown.md`, "Dirty shutdown"). The guard: every
  command is a pure projection over durable surfaces, writing only to stdout or to a repo path the
  director already reads; the tool is deletable-and-rebuildable with zero state loss, and that
  property is itself a test.
- **Relay as decision laundering, tool-assisted.** A `collect`-passed structured reply that
  carries a human "ok" is not a ratification until it is recorded verbatim on the durable decision
  surface (`mechanisms/ballots.md`, "Delegation laundering"; the verbatim-recording rule). The
  tool must never let a schema-valid reply *stand in for* a recorded ratification — validation is
  well-formedness, not authorization. The director records the human's words verbatim before
  executing; the tool does no recording.
- **Mode confusion, mechanized.** Assuming repo-as-bus autonomy while actually running siloed
  desktop sessions the human must relay is a live failure (`mechanisms/operating-model.md`, "Mode
  confusion"); a tool that guesses the mode would automate the confusion. The guard is an explicit
  `--mode` and the same name-the-bus discipline the operating model already requires — the tool
  makes the choice explicit, never implicit.

## What varies per project

The bindings layer supplies everything the assembler resolves against: the **bindings declaration**
(`bindings/<project>.md`) that resolves every `{{variable}}` in the boot-prompt template; the
**return-format schema(s)** `dispatch` names and `collect` validates against (the project's
findings / gate-results / merge-recommendation shape, atop `measurement/review-output.schema.json`);
the **gate list** and **Definition-of-Done rung** vocabulary a `dispatch` ask carries
(`bindings/boot-prompt-template.md`, `{{GATE_LIST}}`, `{{DoD_MERGE_RUNG}}`); the **durable surfaces**
`status` projects over (roadmap, board, ruling register, measurement ledger — `mechanisms/status-page.md`);
the **staging paths** Stage 1 writes dispatched payloads and collected replies to; and **which bus
mode(s)** are in force per work class, which the `--mode` flag makes explicit. The *shape* — four
stateless commands assembling the three-things relay payload from bindings and durable surfaces,
eyes-on preserved, the human making every ballot, both bus modes first-class, and the Stage-0/1/2
adoption path — is the framework-law design; the schemas, gate vocabulary, surface paths, and mode
policy are bindings. None of it is code in v0.2: this document is the mechanism until the
measurement layer it would feed earns the tool its first line (WORKPLAN H7; H3).
