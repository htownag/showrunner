# STATUS — `<project name>`

*Last refreshed: `<YYYY-MM-DD>` by `<orchestrator role>`, session end. Commit `<short-sha>`.*

*This page is the human lead's dashboard — a plain-English projection over the machine surfaces (`<the board>`, `<ROADMAP path>`, `<ruling register + ID scheme>`, `<measurement ledger path>`). It is **regenerated every shutdown and read first at every boot** (see `mechanisms/status-page.md`). It is a render, not a source: **do not hand-edit it — regenerate it from the surfaces**, and if it disagrees with them, they win. Skim target: under a minute.*

*Day-one setup: seed this file by copying `bindings/STATUS-template.md` to your project root as `STATUS.md` — the first boot reads it for orientation; the orchestrator regenerates it every shutdown thereafter.*

---

## 1. Your queue — what needs the human lead

**Decisions awaiting your ballot (`<n>`):**
- **`<ballot ID / short title>`** — `<one-line statement of what's being picked>`. → *Recommendation: `<the marked recommendation>`.* `<one line settles it / what it blocks>`
- `<add one row per open ballot; keep each to a line or two; always include the recommendation>`

**Awaiting your test / sign-off (`<n>` — L4):**
- **`<item>`** — `<what it is>`; L2-verified (`<evidence pointer — PR # / log / screenshot>`). Needs your `<play-through / use>` to reach L4 / milestone-done. `<~time estimate>`
- `<add one row per L4-pending item>`

*(If either list is empty, say so explicitly — "No open ballots." / "Nothing awaiting your test." — never leave it blank.)*

## 2. Where we are

`<current milestone/phase, in one sentence, with rough % done>`. Health: `<one-line health note — trunk green/red, required checks, anything blocking>`.

## 3. What each team is doing

| Team | Current task | Status | Last update |
|---|---|---|---|
| **`<team>`** | `<current task>` | `<active / blocked / waiting-on-human / idle>` | `<YYYY-MM-DD>` |
| `<one row per team>` | `<...>` | `<...>` | `<...>` |

*(Active-team cap per project: `<cap>`.)*

## 4. What's next

**`<next milestone>`.** Done-criteria: `<the criteria that call it done, and who L4-stamps them>`. *Kill/pivot trigger: `<the pre-written condition under which this milestone is deferred or the plan pivots>`.*

## 5. Where the work lives

| Branch / PR | Team | State |
|---|---|---|
| `<PR # / branch name>` | `<team>` | `<open — awaiting X / in progress / parked — blocked on Y>` |
| `<one row per in-flight branch, PR, or live session>` | `<...>` | `<...>` |

`<stranded-worktree note — "No stranded worktrees." or the rescue candidates>`

## 6. Recently landed

- **`<PR # merged / ruling ratified>`** — `<one-line what it was + team + DoD rung>`. *(`<YYYY-MM-DD>`)*
- `<the last few merges/rulings, condensed — a changelog, not a log; cap it>`
