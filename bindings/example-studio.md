# Bindings — Worked Example: the studio project

*This is the fully-instantiated bindings declaration for the studio project (a Unity MMO-lite built by AI teams under one human lead). It is the designated home for this project's own vocabulary — team codenames, gate names, milestone labels — which the principles and mechanisms layers deliberately never use. Everything here maps back to a field in `bindings/TEMPLATE.md`. Read it beside the template to see how an abstract binding becomes a concrete one.*

*Hygiene note: even here, the human is referred to as "the human lead"; no hostnames, usernames, tokens, IPs, or protected-franchise terms appear. Source of truth for these bindings is the project constitution (`CLAUDE.md`) and the director's handbook (`docs/kb/director-handbook.md`).*

---

## 1. Project identity

- **Project name (internal):** the studio project — an AI-built game studio operating as a virtual studio under one human lead.
- **Design north star:** *A frontier civilization survives only through interdependent specialists taking risks together* — every system must teach it; systems that don't get demoted or cut.
- **Constitution path:** `CLAUDE.md` (root) — short, stable, pointer-indexed; the eight hard rules are absolute.
- **Canon / design-law home:** `design/canon/` (north-star GDD + working-layer addendum) and the ruling register `design/rulings/`.
- **IP posture:** original-IP clean-room. Protected-franchise terms are lint-enforced out of scoped paths; a provenance zone (`design/research/`) is exempt (internal-only, never shipped).

## 2. The human interface contract

- **How the human is referred to in-repo:** the human lead — lead designer and final quality gate.
- **Communication style in chat:** plain prose, no header/bold scaffolding in conversational replies; reports lead with the outcome.
- **Decision format:** BALLOT — what's being picked, 2–4 options each with a one-line consequence, a marked recommendation, and what happens after the pick. A ticket that merely *promises* a memo is not a ballot. One line from the human lead settles a ballot.
- **Ratification recording rule:** record ratifications VERBATIM (his words, quoted) on the decision issue and in the ruling file, then execute fully. Delegations ("go with your rec", "merge what's ready") are recorded as his and acted on decisively, never stretched past plain scope.
- **What the human's attention is reserved for:** feature merges, design ballots, in-editor / in-play work, and taste. The whole apparatus exists to spend his bandwidth only on these — his bandwidth is the studio clock.
- **Ground-truth rule:** the human lead's in-play observations are ground truth (hard rule 6). Instrument and investigate; never theorize his test was wrong. Trust "it worked" reports.
- **Availability rhythm:** touches are batched (merge-queue accumulates his decisions for one sitting). When he is absent multi-day: ballots queue on the board (never self-answered), the green lane keeps flowing, code merges wait unless a standing delegation covers them, teams keep working their workplans — the studio idles gracefully, it does not improvise law.
- **Adversarial-then-fold rule:** be adversarial when asked, then fold cleanly; his call stands without relitigating.

## 3. Autonomy lanes

| Artifact class | Trust level | Who may merge | Conditions to merge |
|---|---|---|---|
| docs / workplans / TDDs / briefs / logbook / memory | green lane | the director (Fable role) | on team-lead + advisor signatures; all five required checks green |
| code / assets / scenes / any weighted outcome | human lane | the human lead — unless delegated in words | passed review + adversarial advisor verification + green CI (L2 evidence) |
| records of an already-ratified decision (ruling files, register rows, supersession annotations) | orchestrator-under-ratification | the director | records only a decision the human already ratified; **new design law never rides this** (hard rule 8) |
| `*.unity` scene files | scenes are the human's | the human lead (the *commit* is his) | agents never write `*.unity`; generators create them via human-runnable menu items; authorization recorded verbatim in the commit message |

- **Delegation phrasing:** "merge what's ready" / "go with your rec" / "ok great do that" expand the director into the human lane. Under delegation: merge only what passed review + adversarial verification + green CI; anything short gets its required changes posted to the team and held. Never stretch the words past plain scope.

## 4. The gate roster

The automated half of the review pipeline (`.github/workflows/ci.yml`). Every PR passes these before a human looks at it.

| Gate / check name | Tool / invocation | Runs on | Invariant it compiles | Required? |
|---|---|---|---|---|
| `lint-gates` | `tools/ip_lint.py`, `tools/asmdef_lint.py`, `tools/scene_lint.py`, `tools/telemetry_lint.py`, `tools/naming_register_check.py` | hosted (stays live when the dev box is off) | no franchise terms in scoped paths; no cross-team asmdef refs outside Shared; no unregistered scenes; no telemetry schema drift; no shipped name without a complete knockout-search record | **yes** |
| `server-dotnet` | applies `server/db/001_schema.sql` to a `postgres:17` service, then `dotnet test` | hosted + postgres service | server .NET + DB-integration tests (persist, reset invariant, registry gate) pass in CI, not just locally | **yes** |
| `scene-gate` | `tools/scene_lint.py --changed` (exit 2 → label check) | hosted, PRs only | any changed `*.unity` blocks unless the PR carries the `scene-owner-approved` label (constitution rule 3) | **yes** |
| `unity-tests` | EditMode tests against the real licensed editor | self-hosted Windows/unity runner | EditMode test failures (PlayMode job scaffolded-but-disabled until the first PlayMode test lands) | **yes** |
| `combat-core-dotnet` | `dotnet test` on the combat-core project | hosted | combat state-language core test failures | **yes** |
| `build-client` | player build + artifact upload | self-hosted Windows/unity runner | broken player builds; runs on main pushes + `integration-*` tags only (the playtest-ritual build) | no (skips on PRs) |

- **The required-checks set (exact names):** `lint-gates`, `server-dotnet`, `scene-gate`, `unity-tests`, `combat-core-dotnet`. `build-client` is deliberately not required — it skips on PRs.
- **Human-applied gate labels:** `scene-owner-approved` — the human lead applies it; it clears the scene-gate hold (constitution rule 3).
- **Failure-catalog location + lifecycle rule:** director's handbook §6. LIVING — any new earned incident is promoted the same session it happens; every row aspires to graduate into a lint/hook/test, and graduated rows archive out. (A repo-root-anchored lint invoked from the wrong tree once passed locally while CI went red — #117; the day-old naming gate caught it.)

## 5. Done-ladder evidence classes

| Rung | Meaning | Evidence class | How it's verified |
|---|---|---|---|
| L0 | compiles | build success | — |
| L1 | CI tests pass | green CI run | re-read the run; green proves L1 only |
| L2 | agent-verified in play / against a local server | log excerpt, chronicle rows, or screenshot attached | re-download the artifact, re-extract the screenshot, re-run the math — evidence must be REAL and consistent with code that exists |
| L3 | verified in the integration build | integration-tagged build evidence | delta-verify branch head postdates the verdict |
| L4 | the human lead saw it work | his confirmation | his word (ground-truth rule) |

- **Merge threshold:** L2.
- **Milestone-done threshold:** L4 (weekly tagged integration build → the human lead's L4 stamps; the ladder decays without the playtest ritual).
- **Evidence-authenticity rule:** evidence authenticity is part of review — re-download the CI artifact, re-extract the screenshot, re-run the math. "Enforced in the core" overclaims get a call-site grep (a named locus with zero callers is decorative).

## 6. Tracking surfaces + authoritative-surface table

- **Tracking surfaces:**
  - Issue/ticket tracker: the VCS host's Project board — milestones `M0`–`M8` as board milestones; work as issues; a `type:decision` morning queue; per-team lane rows.
  - Roadmap / state file: `ROADMAP.md`.
  - Decision/ruling register: `design/rulings/` with IDs `GW-R-###`, PLUS closed `type:decision` issues (two surfaces).
  - Logbook: `logbook/` (studio dispatches + retrospectives); per-team mirrors `teams/<team>/logbook/`.
  - Memory index: `MEMORY.md` + linked single-fact files under `memory/`.

| Fact class | Authoritative surface | Why (where the stale copy lives) |
|---|---|---|
| design law / decisions | the ruling register (`GW-R-###`) + closed `type:decision` issues + git log | memory is a pointer that goes stale between sessions; a fresh boot may find it one session behind |
| current project state | `ROADMAP.md` + `git log` since the last dispatch | the log is ground truth when tracking surfaces lag it |
| collaboration patterns / gotchas | `MEMORY.md` (+ linked files) | trusted over single fresh reads; verify before overriding |
| what changed this session | studio dispatch in `logbook/` + git log | team logbooks do not substitute — the boot ritual reads the studio layer first |

- **Two-surface rule:** rulings live on `design/rulings/GW-R-###` files AND closed `type:decision` issues; check both before calling any question open, and inject BOTH into every review/advisor agent's prompt (the stale-advisor incident: an advisor with only the register called three ratified decisions nonexistent).
- **Same-commit index rule:** `docs/kb/INDEX.yaml` updates in the same commit as any KB content change — a stale index is a broken build of the KB.

## 7. Destructive-operation rules

- **Sacred state (never destructively modified without same-session human approval):** the test server's PostgreSQL databases, tester world state, tester accounts, LFS history, and anything that took a human real time to create.
- **Approval protocol:** if diagnosis suggests a destructive op, STOP and surface the option(s) with clear scope (what state, what's recoverable); wait for explicit greenlight; back up first whenever feasible; execute the smallest surgical scope. There is always a surgical alternative — take it even if slower.
- **Scope-of-permission rule:** "authorized something similar in a past session" does NOT count. Each session needs its own greenlight; each destructive op needs its own greenlight.
- **Backup procedure location:** `docs/kb/ops-runbook.md` (backup/reset/incident procedures; automated backups are a Spine deliverable — until it lands, manual backup before any destructive op).

## 8. The agent briefing kit

- **Standard context payload every agent prompt carries:**
  - the decision-issue layer (the `type:decision` issue numbers, viewed live);
  - the ruling files in scope (`design/rulings/GW-R-###`);
  - the team's workplan;
  - the specific gate list the work must pass;
  - the required structured-output schema.
- **Structured-output contract:** anything feeding a downstream gate returns a JSON schema of `gate_results` / `findings` / `merge_recommendation` — nothing arrives as prose to re-parse. Spend the highest-effort configuration on VERIFY stages, not drafting stages; one reviewer + one adversarial verifier per item, independent items proceed independently.
- **No-write-to-main rule:** authoring agents return content; the director lands it via worktree → lints → PR. After any content workflow, `git status` the main tree for rogue writes (it has happened twice).
- **Boot-prompt generator:** `bindings/boot-prompt-template.md` (director + team boot prompts from one variable set).

## 9. Tooling bindings

- **VCS + host:** git + the host's CLI. Trunk-based development; short-lived task branches named `<team>/t-####-slug` (hours-to-days); one worktree per session; no long-lived team branches.
- **Branch protection posture:** protected trunk (ratified 2026-07-05) — no direct-to-main push for anyone, admins included. Everything lands via PR with the five required checks green. Host review-approval is deliberately NOT required (all actors push as one account and cannot approve their own PRs — review lives in the advisor trail, not host review objects).
- **CI system:** the host's Actions. Lint gates run hosted (stay live when the dev box is off); Unity jobs run on a self-hosted Windows runner (labels `self-hosted, Windows, X64, unity`) using the locally installed licensed editor — no containerized engine (the local editor is already licensed and version-exact). CI checks out a fresh repo copy so it never collides with the interactively open editor's asset-database lock.
- **Editor / engine integration:** the live editor is driven over an MCP bridge. Self-check: `claude mcp list` shows the bridge Connected, and the editor must be OPEN (a status heartbeat file confirms). The registration is known to vanish (the plugin's config-rewrite behavior) — restore via the documented `claude mcp add --scope user` recipe and start a fresh session. Note: the Code surface and the desktop-chat surface read SEPARATE MCP configs.
- **Known tool gotchas (bound to incidents):**
  - Direct-to-main push broke the trunk silently for hours (`a39229d`) → boot-check main CI green; branch protection now enforces it.
  - Sessions end with work staged/unpushed → boot-time stranded-worktree scan under a liveness gate; session-end ritual in every boot prompt.
  - Synchronous heavy asset-database ops over MCP wedge the editor's command pump after a domain reload → prefer filesystem moves + editor rescan for bulk ops; keep MCP `execute_code` calls short-running.
  - A replacement whose output re-contains its own match pattern double-applies on a crash-rerun (#117) → replacement text must not re-create the matched string; idempotence guards key on a unique fragment of the NEW text.
  - Telemetry schema + the exactly-these-events guard test must change in the SAME diff (#67).
- **Binary-asset / specialized tooling:** prefer a CLI/library over GUI narration whenever a tool exists as both — drive it end-to-end rather than narrating clicks.

## 10. Memory / KB locations and index rules

- **Raw captures:** `docs/kb/raw/` — unprocessed logs/transcripts/research dumps; never cited directly.
- **Synthesized reports:** `docs/kb/*.md` — distilled from raw.
- **KB index + rule:** `docs/kb/INDEX.yaml` — updated in the same commit as any KB content change.
- **Memory store:** `memory/` single-fact files (YAML frontmatter) + `MEMORY.md` one-line entries (<200 chars).
- **Per-team mirrors:** `teams/<team>/memory/` and `teams/<team>/logbook/`.

## 11. Escalation ladder

- **Escalation chain (bottom → top):** subagent → team lead → advisor gates (Design Advisor pre-build against the guardrail checklist; Code Advisor post-lead on the PR) → the director (Fable role) → the human lead.
- **Where rulings land:** `design/rulings/` as numbered `GW-R-###` entries within the beat.
- **The "when uncertain, it's the human's call" rule:** design law is never settled below the human lead, and never settled twice. When genuinely uncertain whose call it is, it's his — write the ballot.
- **Advisor gate definitions:** Design Advisor (pre-build, on specs); Code Advisor (post-lead, on the PR). Both re-read the diff and rulings independently, confirm only what they can prove, dispute the rest, and own the merge recommendation.

---

## Team roster (project vocabulary)

The studio runs six standing teams + one dormant, capped at two active steady-state / three burst (the human lead's review bandwidth is the clock):

| Dir | Codename | Lane |
|---|---|---|
| `teams/platform/` | **Spine** | netcode, persistence, server authority, CI, telemetry schema, ops |
| `teams/combat/` | **Lexicon** | the combat state-language; no state-minting below a ruling |
| `teams/economy/` | **Charter** | resources, quality bands, markets, faucet ledger |
| `teams/world/` | **Frontier** | the planets, POI pipeline, VFX, scene ownership |
| `teams/narrative/` | **Chronicle** | lore, origins, naming register, IP hygiene |
| `teams/ui/` | **Console** | design system, onboarding, combat-log pipe, market UI |
| `teams/modes/` | **Geometries** (dormant) | professions, combo grammar, endgame geometries, seasons |

Team boundaries are asmdefs and charters, not branches. Cross-team features run as temporary strike teams that count against the active budget.
