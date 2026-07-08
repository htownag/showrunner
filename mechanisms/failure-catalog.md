# The Failure-Modes Catalog

## What it is

The failure catalog is a living table of every failure the studio has actually hit, each paired with the fix that now prevents it. It is not a postmortem archive and not a wiki of best practices — it is a **backlog of missing enforcement.** Every row is a place where the system currently relies on a human or an agent remembering a rule, and every row therefore aspires to stop being a row: to graduate into a lint, a hook, or a test that makes the failure impossible rather than merely known. A catalog read before improvising is the cheapest bug-prevention the studio has; a catalog frozen at its authoring date decays into history and stops paying for itself.

## The protocol

**Reading it.** Before improvising through anything that smells like a known-hard area (a merge race, an asset regeneration, a stranded worktree, a stale-context agent, a destructive op), scan the catalog first. The whole point is that these were paid for once already.

**Writing a row.** When a real failure is hit and diagnosed:

1. **Promote it the same session it happens.** The incident goes into the catalog in the same session it was earned — not "later," not batched into a future cleanup. A catalog that lags its incidents by weeks is already decaying.
2. Write the row as **`| Failure (concrete, recognizable) | Fix (the rule that now prevents it) |`**, dated, with the originating incident/issue reference where one exists. The failure column must be specific enough that a future session recognizes the situation *before* repeating it.
3. Only real, earned failures go in. No speculative "this could theoretically break" rows — the catalog's authority comes from every row being a scar.

**The graduation lifecycle (the core rule).** Each row has a target: become mechanical enforcement.

4. For every row, ask "what lint, hook, or test would make this failure impossible?" That answer is the row's aspiration, recorded with it.
5. When that enforcement is built and proven, **the row graduates**: it moves out of the live table into a **"Compiled / graduated" archive section** that records what the failure was, what now enforces it, and where that enforcement lives. The live table shrinks as enforcement grows.
6. A row that *cannot* be mechanized (it needs lived judgment, cross-context reconciliation) stays in the live table permanently and is flagged as such — that is a legitimate terminal state, not a backlog item.
7. **The live table's length is a metric.** A long live table means a lot of load-bearing discipline is still riding on memory; a growing archive means the system is compiling its lessons into gates. The direction of travel — live rows graduating to archive — is the health signal.

## Why it exists

- The catalog is explicitly declared LIVING, with same-session promotion as the rule: "any new earned incident is promoted into it the same session it happens — a catalog frozen at its codification date decays into history" (`studio:docs/kb/director-handbook.md` §7; the catalog itself is §6).
- The graduation instinct — turn a remembered rule into an executable gate — is the studio's whole enforcement philosophy: rows like "advisor calls ratified law open" graduated into *inject decision issues + register into every agent prompt*; "direct-to-main push breaks trunk silently" graduated into a boot-time main-CI check *and then* into branch protection, a compiled gate (`studio:docs/kb/director-handbook.md` §6 and §9, "Branch protection RATIFIED + APPLIED").
- Several rows are visibly mid-graduation, which is exactly the intended lifecycle: "session ends with work unpushed" is enforced today by a boot-time stranded-worktree scan and a session-end ritual line (ritual), aspiring toward automation (`studio:docs/kb/director-handbook.md` §6, §2, §2b).
- The validation project runs the same pattern under a different name: its end-of-session checklist encodes "the drift that the pre-commit hook can't" catch yet — index staleness, missing memory pointers, manifest-additive audit — each a catalog row waiting for the hook that would retire it, and each earned from a specific incident (a manifest overwrite caught in review; a rename that lived a day in data) (`validation:.claude/skills/end-session/SKILL.md`; `studio:docs/kb/studio-operations.md` rename-hygiene section).
- The pipeline's inline gate-threshold comments are a catalog in code form: each threshold carries the dated incident that set it ("lowered 0.58→0.45: … scored an adequate forensic run 0.235 → wasted rework"), which is a failure row that graduated into a config value plus a comment explaining why touching it re-opens the wound (`pipeline:brain/phases/forensics-report.yaml`, the INVESTIGATION and REPORT_DRAFTING gate comments).
- Two-repo test: same-session incident capture appears in the studio catalog and in the validation project's churn checklist; the graduation-to-gate direction appears in all three grounds.

## Failure modes of the mechanism itself

- **Freezing.** The catalog stops being updated and becomes a historical document; new sessions re-earn old scars. Prevented only by the same-session promotion rule being itself a ritual line.
- **Never graduating.** Rows accumulate but none are ever compiled into gates, so the catalog becomes a giant checklist that everything depends on humans remembering — the exact fragility it was meant to reduce. The archive should grow over time; if it never does, mechanization has stalled.
- **Speculative bloat.** Adding "could-happen" rows dilutes the signal that every row is a real scar; readers stop trusting that a row means "this bites."
- **Graduation without archival.** Building the lint but leaving the prose row live creates double enforcement and drift between the row and the gate (which one is authoritative?). Move the row to the archive when the gate lands.
- **Over-mechanization pressure.** Trying to compile a genuinely judgment-bound row (one needing cross-context reconciliation) into a brittle regex that then misfires. Some rows are permanent; forcing them into gates creates false positives that erode trust in all gates.

## What varies per project

The bindings layer declares **where the catalog lives** (which doc), **what the local enforcement targets are** (the specific lint/hook/test harness a row can graduate into), and **the project-specific rows** themselves — those are bindings, not framework law, because they name a project's own tools and paths. The framework contributes the *shape and lifecycle* (living, same-session promotion, aspire-to-gate, archive-on-graduation); the rows are the project's own. See `bindings/TEMPLATE.md` → catalog location and enforcement harnesses, and `bindings/example-studio.md` for a populated live table and compiled archive.
