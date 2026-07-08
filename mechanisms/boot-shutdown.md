# Boot and Shutdown — Statefulness as One Protocol

## What it is

Boot and shutdown are two halves of a single protocol built on one axiom: **state lives in the repo, never in the model.** Because any orchestrator or team session is disposable — it can be replaced by a fresh session, or a different model, at any moment — everything the next session needs to resume must be written to durable surfaces before the current one ends, and re-read from those surfaces before the next one acts. Boot is the read half: reconstruct the full state of the world from the repo in a fixed order, then run self-checks that catch what drifted while no one was watching. Shutdown is the write half: commit, stamp, and record so that the world the next boot reads is true. The two are one mechanism because boot only works if the previous shutdown was clean; a session that shuts down dirty silently breaks the next session's boot.

## The protocol

**Boot ritual (run every session, in this order — order matters because later surfaces can be ahead of earlier ones):**

1. **Read the constitution first** — the root rules doc (hard rules are absolute), then the operating handbook for your role, then the roadmap/status doc.
2. **Read the law surfaces** — the decision/ruling register (it can be ahead of the roadmap) and the closed decision items. Rulings live on *two* surfaces; read both (see `two-surface-rule.md`).
3. **Read the trackers** — each team/lane's tracking surface named in the roadmap.
4. **Read the newest narrative** — the most recent studio/logbook entries, *and* any per-team logbook entries newer than the last studio dispatch.
5. **Read the ground truth** — `git log` since the last dispatch's commit. The commit log is authoritative when tracking surfaces lag it.
6. **Run the boot self-checks:**
   - **Open work needing adjudication** — anything open (PRs, requests) needs a decision or a nudge.
   - **Trunk health** — the latest main-branch CI run is green. A red trunk is a drop-everything fix (it can break silently for hours after a bad direct push).
   - **Stranded work** — list worktrees + status; uncommitted work in a dead session's tree is a rescue candidate (see `session-rescue.md`), but apply the liveness gate before touching one.
   - **Tooling reachable** — any external tool the session will need (editor bridge, live server, MCP connection) is actually connected, not just configured.
7. **Load the collaboration layer** — project memory loads automatically; trust it for collaboration patterns over a single fresh read, but for law and state the trust order inverts (see `memory-trust-order.md`).
8. **Confirm the read** — read the human-facing status page (`STATUS.md`, per `status-page.md`) first for orientation (if it is absent — the first boot of a freshly-instantiated project, before any shutdown has run — note that and proceed; the first shutdown creates it), then emit a one-paragraph state-of-the-world that *reconciles it against* `git log` and the trackers (a prior dirty shutdown may have left it stale — verify it, don't trust it), surface anything needing the human today starting from STATUS.md's Your-queue, *then* begin working the queue. The status page is the durable materialization of this one-paragraph state-of-the-world; shutdown regenerates it (the STATUS.md sub-step under shutdown step 2).

**Shutdown ritual (run before any session ends, or when the human says wrap up, in this order):**

1. **Everything committed and pushed** — including edits to the handbook, KB, memory, roadmap, and logbook made this session. An uncommitted artifact does not exist to the successor.
2. **Roadmap/status re-stamped** to the session's final state, in the same push.
   - **STATUS.md regenerated** — the human-facing dashboard (see `status-page.md`), rebuilt from the trackers, roadmap, ruling register, and measurement ledger, and stamped in this same push. Regenerate it, never hand-edit it. Its **Your-queue** section (open ballots + awaiting-human-test items) is the half that is *never* allowed to ship stale — it is what the human reads first at the next boot.
3. **Dispatch written** — a studio/session logbook entry for any session that changed shared state (merges, rulings, incidents). Team-level logs do not substitute for the studio-level surface the next boot reads first.
4. **Memory pointers updated** — the state pointer and law index reflect this session's rulings and changes (this is *why* a fresh boot may find memory one session behind; see `memory-trust-order.md`).
5. **Board/queue current** — trackers ticked, new work filed as items, open questions to the human queued as ballots (never buried in chat).
6. **One orchestrator at a time** — if the newest dispatch is *fresher than your own boot*, another session is live; stop and reconcile before writing anything.

**The knowledge-surface churn check (fold into shutdown when the session touched knowledge surfaces):** before the closing commit, verify the index is fresh for every touched KB article (same-commit rule), every new memory file has a one-line pointer in the memory index, and any structured side-logs the change implies were updated. Surface gaps; do not auto-fix persistent state.

## Why it exists

- "State lives IN THE REPO, never in the model" and the ordered boot read are the opening of the director's boot ritual (`studio:docs/kb/director-handbook.md` §2); the same ordered read is compressed into the pasteable boot prompt (`studio:docs/kb/director-handbook.md` §10).
- The three boot self-checks are each an earned scar: the trunk-health check exists because a direct-to-main push "broke the trunk silently for hours"; the stranded-worktree scan exists because a naming-register session's work "nearly died" uncommitted; the tooling check exists because the editor MCP registration "is known to vanish" (`studio:docs/kb/director-handbook.md` §2, §6).
- Shutdown is binding and is itself an incident: the operating handbook "was caught untracked by its own adversarial review — the founding incident" of the session-end section; "an uncommitted artifact does not exist to the successor" (`studio:docs/kb/director-handbook.md` §2b).
- The team-level session-end ritual was added after "the first two team sessions each missed part of it" — one left "its entire governance output uncommitted" and had to be recovered; another "skipped" its logbook (`studio:docs/kb/studio-operations.md`, the session-end ritual section).
- "One orchestrator at a time" (stop if a fresher dispatch exists) prevents two directors clobbering each other's state (`studio:docs/kb/director-handbook.md` §2b).
- The churn-check half — index freshness, memory pointers, side-logs — is the validation project's independent shutdown discipline, itself a set of dated incidents (an index left stale; a memory file with no pointer; a manifest overwrite) (`validation:.claude/skills/end-session/SKILL.md`).
- Two-repo test: the commit-everything-then-stamp shutdown appears in the studio handbook, the studio operations doc, *and* the validation project's end-session skill, independently.

## Failure modes of the mechanism itself

- **Dirty shutdown.** The single most damaging failure: work left uncommitted, roadmap unstamped, or no dispatch written. The next boot reads a false world and acts on it. Everything in shutdown exists to prevent this.
- **Boot skimming.** Skipping the ordered read (especially the `git log` ground-truth pass) and trusting a lagging tracker, then acting on stale state. The order exists precisely because surfaces disagree.
- **Self-checks as theater.** Running the boot checks but not acting on a red trunk or a stranded worktree — the check without the drop-everything response is worthless.
- **Two live orchestrators.** Missing the fresher-dispatch signal and running two sessions that overwrite each other's state. The check is cheap; the collision is expensive.
- **Churn drift.** Committing knowledge-surface content but not its index/pointer, so the next session's automated reads point at nothing — a stale index is a broken build of the knowledge base.
- **Ritual bloat.** Letting the boot read grow until it no longer fits a session's context budget; the surfaces must stay small enough that a full boot is cheap (this is what makes sessions disposable).
- **Stale status page.** The human-facing dashboard not regenerated at shutdown (the STATUS.md sub-step under shutdown step 2), so the human boots into a false world and decides against where things stood a session — or a week — ago, the exact confusion the page exists to end. Its Your-queue section (pending decisions + awaiting-test items) is the half that must never lag a session; bind the refresh to shutdown, never to "when I get to it." (Full mechanism: `status-page.md`.)

## What varies per project

The bindings layer names the **actual files read at boot and in what order** (constitution, roadmap, registers, trackers, logbook paths), the **concrete self-check commands** (how to query trunk CI, how to list worktrees, how to confirm the tooling bridge), the **memory-pointer files** updated at shutdown, and the **churn-check harness** (index format, memory-index conventions, side-logs). The *shape* — ordered read, self-checks, commit-stamp-dispatch-update-current, one-orchestrator guard — is framework law; the paths and commands are bindings. See `bindings/TEMPLATE.md` → boot read list, self-check commands, tracking surfaces, and `bindings/boot-prompt-template.md` for the parameterized boot prompt.

The bindings layer also names the **human-facing status page** — its path (project root `STATUS.md` by convention) and its regeneration source (which roadmap, board, register, and ledger it projects over) — and seeds it once at project setup from `bindings/STATUS-template.md` so the very first boot's read resolves to a real file. The page is a read-only human consolidation of the tracking surfaces, not a new source of truth; the surfaces win when they disagree. See `bindings/TEMPLATE.md` (tracking surfaces), `bindings/example-status.md`, and the mechanism in `status-page.md`.
