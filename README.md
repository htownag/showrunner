# Showrunner — a framework for the solo developer running a multi-agent studio

*Status: **draft** — extracted 2026-07-08 from three proving grounds; name ratified **Showrunner** and promoted to its own repository (2026-07-08, the human lead). Publication ruling still open (see Ballots below).*

A showrunner is one person with final creative authority over a large production — a room drafting under them, departments executing, and the showrunner as the single taste-and-quality gate the whole thing answers to. That is exactly this role: one human directing many disposable AI agents, and the machinery that keeps their output honest.

One person directing a swarm of capable AI agents fails in a predictable way: plausible output at scale, evidence that lies, sessions that die, decisions that evaporate. This framework is the apparatus that bends that trajectory — extracted from several real projects (a game studio run as a virtual multi-agent studio, a five-month game-server modding project, a production document pipeline serving a real business, a desktop client, and an orchestration platform) that converged independently on the same fixes.

Its distinguishing property: **nothing here was designed in the abstract.** Every rule cites the dated, real incident that earned it. This is case law, not legislation.

## The three layers

| Layer | File(s) | What it is | Stability |
|---|---|---|---|
| **Principles** | [`PRINCIPLES.md`](PRINCIPLES.md) | Ten load-bearing ideas, each with incident receipts and a two-repo verdict | Survives everything |
| **Mechanisms** | [`mechanisms/`](mechanisms/) | Twelve checklist-grade protocols (ballots, done-ladder, failure catalog, boot/shutdown, review pipeline, session rescue, lanes, knowledge system, memory trust order, two-surface rule, deterministic backstops, context injection) | Survives tool swaps |
| **Bindings** | [`bindings/`](bindings/) | What each project fills in: [`TEMPLATE.md`](bindings/TEMPLATE.md), a worked example, and parameterized boot-prompt generators | Per-project |

Supporting surfaces:

- [`CASE-LAW.md`](CASE-LAW.md) — **the casebook**: the incident register (CL-001..CL-042) across all proving grounds — what happened, the rule it earned, and its enforcement status (prose rule → ritual → compiled gate). It is the spine; every principle and mechanism cites back to it.
- [`measurement/`](measurement/) — the quantitative loop: a review-ledger [spec](measurement/review-ledger-spec.md), JSON Schemas for ledger rows and forced review output, a stdlib-only [`ledger.py`](measurement/ledger.py) (append / check / project / report, with outcome-correlation calibration weights), a synthetic example ledger, and [boot integration](measurement/boot-integration.md). **Live at stage 0/1 in the studio project since 2026-07-08** (first real ledger: 34 rows from two days of documented gate decisions at `measurement/review-ledger.jsonl`, dashboard wired into the director boot ritual); armed at stage 0 in the validation project.
- [`essay/one-human-studio.md`](essay/one-human-studio.md) — the public-facing narrative telling: the problem, the five load-bearing ideas, three worked incidents, what gets measured next.

> The alias→repository key (`SOURCES.md`) and the build record (`WORKPLAN.md`) live only in the private origin and are deliberately omitted here — the artifact stands on its own without them.

## The extraction tests (how content earned its place)

1. **Two-repo test** — a pattern enters principles/mechanisms only if it was earned independently in ≥2 proving grounds, or from one decisive documented incident (marked as single-ground).
2. **No proper nouns in layers 1–2** — principles and mechanisms are fully project-agnostic; project vocabulary lives only in the bindings worked example.
3. **Receipts or it isn't law** — every rule cites its incident; unearned rules are marked `[PROPOSED]` (currently: none).
4. **Publication hygiene by construction** — no client names, case identifiers, personal data, hostnames, tokens, or protected-franchise terms anywhere; the one de-anonymizing file (`SOURCES.md`) is held privately in the origin and is not part of this repo.

Citation conventions: `PRINCIPLES.md` cites `CL-###` entries; `mechanisms/*.md` cite `<alias>:<path>` source receipts directly. CL-IDs resolve within [`CASE-LAW.md`](CASE-LAW.md); the `<alias>`→repository key is held privately in the origin (the aliases point into private repos by design, so they stay opaque here — which is the intended posture for a shareable artifact).

## Adopting this framework in a new project

1. Copy this repository.
2. Fill in [`bindings/TEMPLATE.md`](bindings/TEMPLATE.md) — identity, human contract, lanes, gate roster, tracking surfaces, destructive-op floor, tooling.
3. Generate the orchestrator and team boot prompts from [`bindings/boot-prompt-template.md`](bindings/boot-prompt-template.md).
4. Start your own failure catalog at incident #1 — the framework's catalog is precedent, not your project's history. Promote your incidents the same session they happen.
5. When ready to measure, adopt [`measurement/`](measurement/) at stage 0 (capture only) and graduate per the staged path.

## Ballots (for the human lead)

1. ~~**Name**~~ — **ratified Showrunner** (2026-07-08); the case-law register keeps the name *casebook*.
2. ~~**Home**~~ — **resolved 2026-07-08**: promoted to this standalone repository.
3. **Publication** *(open)* — publish the essay + artifact publicly, and where.
