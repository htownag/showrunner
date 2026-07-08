# STATUS — the studio project

*Last refreshed: 2026-07-08 by the director (Fable role), session end. Commit `a1b9f3c`.*

*This page is the human lead's dashboard — a plain-English projection over the machine surfaces (the Project board, `ROADMAP.md`, the `GW-R-###` ruling register, `measurement/review-ledger.jsonl`). It is **regenerated every shutdown and read first at every boot** (see `mechanisms/status-page.md`). It is a render, not a source: **do not hand-edit it — regenerate it from the surfaces**, and if it disagrees with them, they win. Skim target: under a minute.*

---

## 1. Your queue — what needs the human lead

**Decisions awaiting your ballot (2):**
- **Mounted-lance combat state (Lexicon).** Lexicon hit a case the 36-state combat language doesn't cover: a lance strike from a moving mount. Mint a 37th state, or express it as an existing state plus a modifier? → *Recommendation: express as `charge` + a mount modifier — no new state; minting reopens the closed 36-state cap ratified in GW-R-012.* One line settles it; parks Lexicon's registry work until you do.
- **Resource quality-band curve (Charter).** Should harvested-resource quality map to yield linearly or in stepped bands? Linear is smoother; stepped is more legible to players and easier to balance. → *Recommendation: stepped, 5 bands.* Blocks Charter's faucet-ledger work below.

**Awaiting your test / sign-off (1 — L4):**
- **Console onboarding flow.** The first-session tutorial is L2-verified — an agent walked it end-to-end against a local server; log excerpt + screenshot attached to PR #218. It needs your play-through to reach L4 / milestone-done. ~10 min.

## 2. Where we are

M3 — the steel thread (first end-to-end playable: log in → harvest → craft → fight → persist), ~80% done. Health: trunk green, all five required checks passing on `main`; the quality-band ballot above is the one thing blocking a team (Charter) from finishing.

## 3. What each team is doing

| Team | Current task | Status | Last update |
|---|---|---|---|
| **Spine** (platform) | persistence reset-invariant + manual backup runbook | active | 2026-07-08 |
| **Lexicon** (combat) | combat-state registry | waiting-on-human (mounted-lance ballot) | 2026-07-08 |
| **Charter** (economy) | faucet ledger | waiting-on-human (quality-band ballot) | 2026-07-07 |
| **Console** (ui) | onboarding flow — L2 done | waiting-on-human (your play-test) | 2026-07-08 |
| **Frontier** (world) | — | idle (spins up at M4) | 2026-07-05 |
| **Chronicle** (narrative) | — | idle | 2026-07-04 |

*(Active-team cap: two steady-state. Spine is the one fully-active builder right now; Lexicon and Charter are parked on your queue, Console on your test.)*

## 4. What's next

**M4 — the first planet loop.** Done-criteria: one full planet (Frontier) with POIs, a working harvest → market → craft economy loop (Charter), and the combat language exercised in a live encounter (Lexicon) — all L4-stamped by you in a tagged integration build. *Kill/pivot trigger: if the steel thread doesn't hold under your M3 play-test — i.e. the login → persist loop drops state — M4 is deferred and Spine re-opens persistence before any new content lands.*

## 5. Where the work lives

| Branch / PR | Team | State |
|---|---|---|
| PR #218 `ui/t-0151-onboarding` | Console | open — awaiting your L4 test |
| `platform/t-0148-persist-reset` | Spine | in progress (no PR yet) |
| `combat/t-0142-state-registry` | Lexicon | parked — branch alive, work paused on the ballot |
| `economy/t-0139-faucet-ledger` | Charter | parked — blocked on the ballot |

No stranded worktrees; no uncommitted work in a dead session.

## 6. Recently landed

- **PR #215 merged** — Spine: world-state persistence write path (L2). *(2026-07-08)*
- **GW-R-012 ratified** — the 36-state combat cap holds; no states mint below a ruling. *(2026-07-07)*
- **PR #211 merged** — Console: combat-log pipe to the UI (L2). *(2026-07-06)*
- **Branch protection applied** — no direct-to-main push for anyone, admins included; everything lands via PR + five green checks. *(2026-07-05)*
