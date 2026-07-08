# Bindings Declaration — TEMPLATE

*The bindings layer is where the framework meets one concrete project. Principles (layer 1) and mechanisms (layer 2) are project-agnostic and carry no proper nouns; **this file is where the names, paths, tool invocations, and grants live.** A new project instantiates the framework by copying this template and filling every field. A field left as a `<placeholder>` is an unbound binding — the framework's gates and rituals will reference a surface that does not exist.*

**How to use:** copy this file to your project's bindings location (e.g. `bindings/<project>.md` or the project's operating-handbook), fill every REQUIRED field, and delete or fill each optional field. Each field carries a one-line instruction and a `<placeholder>`. See `bindings/example-studio.md` for a fully worked instance.

**Legend:** `[REQUIRED]` — the framework does not function without it. `[OPTIONAL]` — fill if the project has this surface; delete the field if it does not.

---

## 1. Project identity

- `[REQUIRED]` **Project name (internal):** the name sessions use for this project. → `<project-name>`
- `[REQUIRED]` **Design north star (one sentence):** the single lesson every system must teach or serve; the demotion test for any feature. → `<one-sentence north star>`
- `[REQUIRED]` **Constitution path:** the short, stable, pointer-indexed root document that governs (hard rules live here). → `<path/to/CONSTITUTION.md>`
- `[OPTIONAL]` **Canon / design-law home:** where settled design law lives, if the project has a design layer distinct from code. → `<path/to/canon/>`
- `[OPTIONAL]` **Public-name / IP posture:** whether the project has an IP firewall (original-IP clean-room) or inherits an ecosystem's vocabulary. → `<firewall | ecosystem-native | none>`

## 2. The human interface contract

The one human is the scarce resource; this section declares how sessions spend their attention. (Mechanism: see `mechanisms/lanes-and-autonomy.md` and the interface-contract in `mechanisms/boot-shutdown.md`.)

- `[REQUIRED]` **How the human is referred to in-repo:** a neutral role label, never a personal name in shareable artifacts. → `<the human lead>`
- `[REQUIRED]` **Communication style in chat:** the prose register for conversational replies (e.g. plain prose, no markdown scaffolding, outcome first). → `<style rule>`
- `[REQUIRED]` **Decision format:** the structure every decision request must take before it reaches the human. → `<e.g. BALLOT: what's being picked, 2–4 options with one-line consequences, a marked recommendation, what happens after the pick>`
- `[REQUIRED]` **Ratification recording rule:** how the human's decisions are captured so they are distinguishable from fabrication. → `<e.g. record verbatim on the decision surface before executing>`
- `[REQUIRED]` **What the human's attention is reserved for:** the short list of things only the human does. → `<e.g. feature merges, design ballots, in-editor/in-play work, taste>`
- `[REQUIRED]` **Ground-truth rule:** the standing rule that the human's direct observation outranks agent theory. → `<e.g. the human's in-play/in-use observations are ground truth; instrument, never theorize the test was wrong>`
- `[REQUIRED]` **Availability rhythm:** the cadence of human touches and what the apparatus does when the human is absent for days. → `<rhythm; absent-behavior: ballots queue, green lane flows, weighted merges wait>`
- `[OPTIONAL]` **Adversarial-then-fold rule:** whether the human wants pushback and how overrides settle. → `<e.g. be adversarial when asked, fold cleanly when overridden, never relitigate>`

## 3. Autonomy lanes (artifact class → trust level → merge authority)

Graduated autonomy: different artifact classes carry different trust and different merge authority. (Mechanism: `mechanisms/lanes-and-autonomy.md`.) Fill one row per artifact class.

`[REQUIRED]` — at least the two canonical lanes (a low-stakes "green" lane the orchestrator may merge, and a high-stakes lane reserved to the human).

| Artifact class | Trust level | Who may merge | Conditions to merge |
|---|---|---|---|
| `<e.g. docs / workplans / memory / logbook>` | `<green lane>` | `<orchestrator on lead + advisor signatures>` | `<all required gates green>` |
| `<e.g. code / assets / weighted outcomes>` | `<human lane>` | `<the human lead — unless delegated in words>` | `<passed review + adversarial verification + green CI>` |
| `<e.g. records of an already-ratified decision>` | `<orchestrator-under-ratification>` | `<orchestrator>` | `<only records a decision the human already made; new law never rides this>` |
| `<add rows as needed>` | `<...>` | `<...>` | `<...>` |

- `[REQUIRED]` **Delegation phrasing:** the words that expand the orchestrator's authority into the human lane, and the standing rule not to stretch them past plain scope. → `<e.g. "merge what's ready" / "go with your rec"; act decisively, never over-read>`

## 4. The gate roster (every automated check → its tool → the invariant it compiles)

Every invariant that can be a machine check IS one; an LLM is never the last line of defense (principle: invariants compile into gates). List every automated gate. (Mechanism: `mechanisms/deterministic-backstops.md`.) Mark which gates are **required** (block merge) vs advisory.

`[REQUIRED]` — the gate table, and the list of exactly which check names are merge-blocking.

| Gate / check name | Tool / invocation | Runs on | What invariant it compiles | Required? |
|---|---|---|---|---|
| `<gate name>` | `<path/to/tool + how CI invokes it>` | `<CI runner / hosted>` | `<the one-sentence invariant>` | `<yes/no>` |
| `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

- `[REQUIRED]` **The required-checks set (exact names):** the checks that must be green before any merge — named exactly as the VCS host reports them. → `<check-a, check-b, check-c, ...>`
- `[OPTIONAL]` **Human-applied gate labels:** any gate that a machine flags but only the human can clear (e.g. a scene-owner-approved label). → `<label name + who applies it + which rule>`
- `[REQUIRED]` **Failure-catalog location + lifecycle rule:** where recurring failure modes are logged, and the rule that every row aspires to graduate into a lint/hook/test (graduated rows archive out). → `<path; lifecycle rule>` (see `mechanisms/failure-catalog.md`)

## 5. Done-ladder evidence classes (as instantiated here)

The Definition of Done ladder and what counts as authentic evidence at each rung. (Mechanism: `mechanisms/done-ladder.md`.) Evidence must be authentic, not plausible.

`[REQUIRED]` — the full ladder with each rung's evidence class, and the merge/milestone rungs.

| Rung | Meaning | Evidence class required | How it's verified |
|---|---|---|---|
| `<L0>` | `<e.g. compiles>` | `<none / build log>` | `<...>` |
| `<L1>` | `<e.g. CI tests pass>` | `<green CI run>` | `<re-read the run>` |
| `<L2>` | `<e.g. agent-verified in use, evidence attached>` | `<log excerpt / rows / screenshot>` | `<re-extract the artifact, re-run the math>` |
| `<L3>` | `<e.g. verified in the integration build>` | `<...>` | `<...>` |
| `<L4>` | `<e.g. the human saw it work>` | `<human confirmation>` | `<the human's word>` |

- `[REQUIRED]` **Merge threshold:** the minimum rung to merge. → `<e.g. L2>`
- `[REQUIRED]` **Milestone-done threshold:** the minimum rung to call a milestone done. → `<e.g. L4>`
- `[REQUIRED]` **Evidence-authenticity rule:** the standing rule that evidence is re-verified, not trusted on sight. → `<e.g. re-download the artifact, re-extract the screenshot, re-run the math>`

## 6. Tracking surfaces + the authoritative-surface-per-fact-class table

State lives in the repo, never in the model — and for each class of fact, exactly one surface is authoritative. Memory goes stale between sessions and is a pointer, not a source. (Mechanisms: `mechanisms/knowledge-system.md`, `mechanisms/memory-trust-order.md`, `mechanisms/two-surface-rule.md`.)

- `[REQUIRED]` **Tracking surfaces (list each and its role):**
  - Issue/ticket tracker: → `<host + project board + how lanes/queues are modeled>`
  - Roadmap / state file: → `<path>`
  - Decision/ruling register: → `<path + ID scheme>`
  - Logbook: → `<path + cadence>`
  - Memory index: → `<path>`

`[REQUIRED]` — the authoritative-surface table. For each fact class, name the ONE surface that wins when surfaces disagree.

| Fact class | Authoritative surface | Why (and where the stale copy lives) |
|---|---|---|
| `<design law / decisions>` | `<the ruling register + closed decision issues + VCS log>` | `<memory is a pointer that goes stale between sessions>` |
| `<current project state>` | `<roadmap file + VCS log>` | `<the log is ground truth when tracking surfaces lag>` |
| `<collaboration patterns / gotchas>` | `<memory index>` | `<trusted over a single fresh file read>` |
| `<what changed this session>` | `<logbook studio dispatch + VCS log>` | `<team-level notes do not substitute>` |
| `<add fact classes as needed>` | `<...>` | `<...>` |

- `[REQUIRED]` **Two-surface rule for decisions:** which two surfaces every decision lands on, and the rule to inject BOTH into any review/advisor agent's prompt. → `<surface A + surface B; inject both>` (see `mechanisms/two-surface-rule.md`)
- `[REQUIRED]` **Same-commit index rule:** the rule that the KB index updates in the same commit as any KB content change. → `<index path; a stale index is a broken build of the KB>`

## 7. Destructive-operation rules (sacred state → approval required)

Some state took a human real time to create and is never wiped on an agent's initiative. (Case law: this rule is typically earned from a real wipe incident — cite it.)

`[REQUIRED]` — the sacred-state list and the approval protocol.

- `[REQUIRED]` **Sacred state (never destructively modified without same-session human approval):** enumerate concretely. → `<e.g. production/test databases, persistent user/world state, VCS history, human-authored assets>`
- `[REQUIRED]` **Approval protocol:** the exact steps before any destructive op. → `<e.g. STOP and surface options with scope; wait for explicit greenlight; back up first; execute smallest scope; each op needs its own greenlight>`
- `[REQUIRED]` **Scope-of-permission rule:** the standing rule that past approval never authorizes a new op. → `<e.g. "authorized something similar before" does NOT count; each session + each op needs its own greenlight>`
- `[OPTIONAL]` **Backup procedure location:** where the backup/restore commands live. → `<path>`

## 8. The agent briefing kit (what every dispatched prompt carries)

Context injection is the failure point, not agent quality — an under-briefed agent confidently reports stale state. (Mechanism: `mechanisms/context-injection.md`.)

`[REQUIRED]` — the checklist of what every dispatched agent prompt must include.

- `[REQUIRED]` **Standard context payload every agent prompt carries:**
  - `<the relevant decision-issue numbers / IDs>`
  - `<the ruling/law files in scope>`
  - `<the team/workstream's workplan>`
  - `<the specific gate list the work must pass>`
  - `<the required output format — structured schema, not prose, for anything that feeds a downstream gate>`
- `[REQUIRED]` **Structured-output contract:** the schema fields agents must return so nothing arrives as prose to re-parse. → `<e.g. gate_results / findings / merge_recommendation>`
- `[REQUIRED]` **No-write-to-main rule:** the rule that authoring agents return content and never write the main tree; the orchestrator lands it. → `<rule + the post-workflow git-status sweep for rogue writes>`
- `[OPTIONAL]` **Boot-prompt generator:** pointer to the parameterized boot prompt for orchestrator and team sessions. → `<bindings/boot-prompt-template.md>`

## 9. Tooling bindings

The concrete tools, their invocations, and the known gotchas. (Case law captures each gotcha's incident.)

- `[REQUIRED]` **VCS + host:** the version-control host and its CLI. → `<e.g. git + gh CLI; branch-naming convention; trunk-based, short-lived task branches>`
- `[REQUIRED]` **Branch protection posture:** whether direct-to-trunk push is allowed (usually not). → `<e.g. protected main, no direct push for anyone, everything via PR>`
- `[REQUIRED]` **CI system:** where CI runs and any self-hosted runner facts. → `<CI provider; runner labels; hosted-vs-local split>`
- `[OPTIONAL]` **Editor / engine integration:** any live-editor or engine MCP/tool binding and its self-check. → `<tool + connection self-check + re-registration command>`
- `[REQUIRED]` **Known tool gotchas (bind each to its incident):** the traps this project has hit. → `<gotcha → fix → case-law ID>` (see `mechanisms/failure-catalog.md`)
- `[OPTIONAL]` **Binary-asset / specialized tooling:** any CLI for domain-specific asset formats, preferred over GUI narration. → `<tool + invocation>`

## 10. Memory / KB locations and index rules

(Mechanism: `mechanisms/knowledge-system.md`.)

- `[REQUIRED]` **Raw captures location:** unprocessed logs/transcripts/dumps; never cited directly. → `<path/to/raw/>`
- `[REQUIRED]` **Synthesized reports location:** distilled KB articles. → `<path/to/kb/>`
- `[REQUIRED]` **KB index file + rule:** the machine-readable index and the same-commit update rule. → `<path/to/INDEX.yaml; update in the same commit as any content change>`
- `[REQUIRED]` **Memory store:** single-fact files + the one-line index. → `<path/to/memory/ + MEMORY.md; entry size cap>`
- `[OPTIONAL]` **Per-team / per-workstream mirrors:** whether memory/logbook mirror per team. → `<path pattern>`

## 11. Escalation ladder

Design law is never settled below the human, and never settled twice. (Principle: the orchestrator is a role, not a model; law is jurisprudence.)

`[REQUIRED]` — the ordered escalation chain and the ruling-record scheme.

- `[REQUIRED]` **Escalation chain (bottom → top):** → `<e.g. subagent → team lead → advisor gates → orchestrator → the human lead>`
- `[REQUIRED]` **Where rulings land:** the register and its numbered ID scheme. → `<path + ID format>`
- `[REQUIRED]` **The "when uncertain, it's the human's call" rule:** → `<when genuinely unsure whose call it is, write the ballot>`
- `[OPTIONAL]` **Advisor gate definitions:** the named advisory roles that gate before the human. → `<e.g. design advisor pre-build, code advisor post-lead>`

---

## Instantiation checklist

Before declaring these bindings live, confirm:

- [ ] Every `[REQUIRED]` field is filled with a real path/name/rule (no `<placeholder>` remains).
- [ ] Every gate name in §4's required-set matches exactly what the VCS host reports.
- [ ] Every path in §6, §9, §10 resolves to a real file/surface.
- [ ] Every tool gotcha in §9 cites a real incident (case-law ID or dated source).
- [ ] The sacred-state list in §7 is concrete, not abstract.
- [ ] The boot prompts (`bindings/boot-prompt-template.md`) are generated from these same values.
- [ ] Hygiene: no client names, hostnames, tokens, IPs, or franchise terms leaked into any field intended to be shareable.
