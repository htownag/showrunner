# Bindings — MINIMAL (Showrunner Lite)

*The smallest legal binding. `bindings/TEMPLATE.md` is the full declaration — eleven sections, dozens of REQUIRED fields — and a project does not need most of it on day one. This profile is five questions that expand into the least apparatus the framework's law will accept, plus a table telling you, for everything MINIMAL leaves out, the exact scar that earns it back. **Graduation-by-scar is Principle 4 (`PRINCIPLES.md` §4, "no rule is law until an incident earns it") applied to adoption:** you do not pre-install the full template any more than you pre-write case law — you add each surface in the same session as the incident that makes it real. If this file itself ever feels heavy, it has failed its own point. Target: a cold reader stands up a working binding from here alone in under fifteen minutes.*

---

## The five questions

Answer these five. Everything below is generated from the answers — you fill five blanks, not fifty.

1. **What are you building?** The north star, one sentence — the single lesson every part must serve, and the demotion test for any feature. → `<one-sentence north star>`
2. **Which files are human-taste / decision territory?** The classes an agent must never author or merge on its own — the taste-bearing, the irreversible, the competitively weighted. → `<e.g. the scene/experience files, the released schema, generated assets>`
3. **What must never be destroyed?** The persistent state a human spent real time creating — wiping it is never an agent's call. → `<e.g. the live/test database, world+account state, VCS history, human-authored assets>`
4. **What one command proves health?** The single deterministic check whose green is the floor of "it works." → `<e.g. `make check` / `python -m unittest` / `npm test`>`
5. **What are your 2–3 work lanes?** At minimum the two canonical ones below; a third only if you already know you need it. → `<green: docs/plans/notes · reserved: everything in Q2/Q3>`

## What the answers expand into (the profile)

These defaults are **RULED framework defaults** — blessed as drafted by the human lead in one pass (`WORKPLAN.md`, "Ballots — RULED 2026-07-10" §4: *"H5 defaults — RULED: blessed as drafted (merge floor L2, verifier always independent, destructive-op floor absolute)"*). They are not tunable in the Lite profile; a project that needs to move one has graduated past MINIMAL.

- **Two canonical lanes** (from Q5; mechanism: `mechanisms/lanes-and-autonomy.md`, Principle 9). The trust gradient is the invariant — the names adapt, the gradient does not:

  | Lane | Class (from your answers) | Who merges | Condition |
  |---|---|---|---|
  | **green** | docs, plans, notes, logbook — fully reversible, low-stakes | the orchestrator, on review signatures | the one health command (Q4) is green |
  | **reserved** | Q2 taste/decision files + Q3 sacred state + **all new law** | the human lead — unless delegated in words | passed review + independent verification + green health command (L2) |

  When unsure which lane, use **reserved** — lane creep (quietly reclassifying reserved as green to skip the wait) is the mechanism's own first failure mode. New law never rides the green lane, regardless of how small it looks.
- **Merge floor L2** (mechanism: `mechanisms/done-ladder.md`, Principle 8). Nothing merges on "it compiles" (L0) or "the health command is green" (L1) alone: merge requires the change *witnessed doing the thing* with authentic, re-derivable evidence attached (a log excerpt, rows, quoted output). A green run proves only that the checks that exist passed.
- **Independent verifier always required** (mechanism: `mechanisms/review-pipeline.md`, Principle 6). Author and gate are never the same actor. The reserved lane's second signature is a *hostile re-read* of the diff and the relevant law from scratch, confirming only what it can prove — not an agreeable second opinion. A self-score never substitutes for it, and never buys out of it.
- **Destructive-op floor, absolute** (mechanism: `mechanisms/lanes-and-autonomy.md`, Principle 9; earned from CL-013, a database wiped during a rename). Any destructive operation on the Q3 state is *never* autonomous, in any lane, under any delegation: STOP and surface the scope, wait for a **same-session human greenlight**, **back up first**, execute the **smallest surgical scope**. A past "authorized something similar" never carries — each op needs its own greenlight.
- **One STATUS surface + two flat dated directories.** `STATUS.md` at the root folds roadmap, current state, and what-changed-this-session into the one surface a fresh session reads first (state lives in the repo, never the model — Principle 3). Ratified decisions land as flat dated files in `.decisions/` (`YYYY-MM-DD-slug.md`, the ballot + the human's verbatim words); incidents land as flat dated files in `.incidents/` (the proto-failure-catalog). No index, no tracker, no per-team mirror until you outgrow this.
- **Authoring agents write the tree, never the merge ref** (CL-006). A dispatched agent returns content; the orchestrator or human lands it. Sweep `git status` for rogue writes after any content workflow.

## The instantiation (copy this, fill the five blanks — you have a binding)

```
# Bindings — <project>

North star (Q1): <...>
Health command (Q4): <...>          # green = L1; L2 (witnessed + evidence) merges

Lanes:
  green    → docs / plans / notes / STATUS / logbook   → orchestrator merges on review signatures
  reserved → <Q2 taste files> + <Q3 sacred state> + new law → the human lead merges (L2 + independent verify)
  (delegation: the human's words — "merge what's ready" / "go with your rec" — expand the
   orchestrator into reserved, honored only within plain scope; anything short is held.)

Sacred state (Q3, never destroyed without same-session greenlight; back up first; smallest scope):
  <...>

Decisions:  ballot → the human's verbatim pick recorded in .decisions/<date>-<slug>.md before executing
Incidents:  every diagnosed failure → .incidents/<date>-<slug>.md (this is your case law, growing)
State:      STATUS.md is authoritative for project state; the VCS log is ground truth when it lags
```

That is a legal binding. It runs the pipeline: sort work into a lane, author in the tree, verify independently, prove L2, land it per lane, record decisions and incidents as flat files.

## Graduation by scar (Principle 4 applied to adoption)

Everything MINIMAL omits from the full template, and the named trigger that adds it. You do not add a row until its scar is real — an un-earned rule is a best-practice with no authority, the exact dilution Principle 4 exists to prevent. When the trigger fires, open the cited `TEMPLATE.md` section and fill only that field.

| Omitted from MINIMAL | The scar that earns it | Lands in TEMPLATE |
|---|---|---|
| Canon / design-law home | Your first design ruling that is *not* a code change — settled law now needs a home distinct from the code. | §1 |
| IP / public-name posture | Your first franchise-vocabulary or identifier leak risk (you inherit an ecosystem's terms, or must clean-room around them). | §1 |
| Communication-style field | The first time a chatty, scaffolded agent report burns a human sitting on reconstruction instead of a decision. | §2 |
| Availability rhythm | Your first multi-day human absence where what the apparatus should do — queue, flow, or wait — was ambiguous. | §2 |
| Adversarial-then-fold rule | Your first override that got relitigated instead of folded cleanly. | §2 |
| Recorded-decision lane (3rd lane) | The first time transcribing an *already-ratified* decision stalled on the human — you need the minting-vs-recording split so the orchestrator may write the record but never mint the law. | §3 |
| Explicit human-only / taste-file rows | Your first taste-bearing artifact an agent authored that only the human should have touched (the CL-013 lineage: the class that must be human-authored, not just human-merged). | §3 |
| Full gate roster (table) | The moment you have **more than one** compiled check — one command was Q4's floor; two need a roster. | §4 |
| Required-checks exact-name set | The first time a check-name mismatch let a red PR read as green at the merge button (CL-033 lineage). | §4 |
| Human-applied gate labels | Your first gate a machine can flag but only the human can clear. | §4 |
| Failure-catalog + lifecycle rule | Your **first repeated** incident — `.incidents/` graduates from a dated-file pile into a living catalog whose rows aspire to become lints (Principle 4's own incident→rule→gate lifecycle). | §4 |
| L3 rung (integration-verified) | Your first integration build where "works in the module" stops guaranteeing "works in the whole." | §5 |
| L4 rung + milestone threshold + ritual | Your first milestone you must *call done* — L4 needs a recurring human-verification ritual, and the ladder decays without it. | §5 |
| Authority-per-fact-class table | Your first **two-surfaces-disagree** incident — you now must name the one surface that wins per fact class. | §6 |
| Two-surface rule for decisions | Your first stale-advisor miss — an advisor briefed with one surface calling ratified decisions nonexistent (CL-034). | §6 |
| KB + same-commit index rule | When knowledge outgrows one `STATUS.md` and flat `.decisions/` and needs a searchable base — a stale index is then a broken build of memory. | §6, §10 |
| Named sacred-state list + backup location | The floor is already absolute; the *concrete enumeration* is earned at your first near-wipe (CL-013), and the backup runbook at the first backup you actually needed. | §7 |
| Full briefing kit + structured-output contract + boot-prompt generator | Your first under-briefed-agent confident-wrong return (CL-034 / CL-035) — the failure is the briefing, not the model. (No-write-to-main is already in the profile.) | §8 |
| Explicit VCS / branch-protection / CI bindings + tool-gotcha register | Branch protection is earned at your first direct-to-main break (CL-033); each tool gotcha is earned by its own incident and bound to it. | §9 |
| Escalation ladder + advisor-gate definitions | Your first standing advisor role, or first escalation that went to the wrong level — until then "when genuinely unsure whose call it is, write the ballot" is the entire ladder. | §11 |

When in doubt about anything not listed here: it is the human's call, so write the ballot. That single rule stands in for §11 until a scar earns you a longer chain.
