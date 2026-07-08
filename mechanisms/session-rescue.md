# Session Rescue

## What it is

Session rescue is the procedure for recovering work when a session dies with its output staged or uncommitted in a working tree — a cloud session that timed out, a team session that ended before its shutdown ritual, a crash mid-task. Because state lives in the repo and not in the model, work that never reached a durable branch is invisible to the next boot and one bad checkout away from destruction. Rescue exists to get that orphaned work safely onto its branch, under review, *without hijacking a session that is actually still alive.* Its two hard edges are the **liveness gate** (never touch a tree that a live session is mid-flight in) and **verbatim preservation** (never rewrite the dead session's work while rescuing it).

## The protocol

**Detection (part of every boot; see `boot-shutdown.md`).** List worktrees and their status; a worktree with uncommitted or unpushed work whose owning session is gone is a rescue candidate.

**The liveness gate — clear ALL of these before touching a candidate tree:**

1. Its branch has **no open change/PR updated today** (recent activity means the session may be live).
2. Its tracker/board shows the session **done or dead**, not in-progress.
3. The human **confirms nothing is live on it.**
   If any check fails, do not touch it — committing a mid-flight session's tree *hijacks* it, turning its next push into a conflict and stealing its authorship. When in doubt, leave it and ask.

**The rescue itself (only after the liveness gate passes):**

4. **Commit the staged/working tree VERBATIM on its own branch**, with attribution to the original session/author. Do not reformat, refactor, "clean up," or complete the work — the rescue commit preserves exactly what was there.
5. **Push** the branch.
6. **Open the change for review** and run it through the normal review pipeline (see `review-pipeline.md`) — rescue gets the work *onto a durable surface under review*; it does not skip the gates.
7. **Record the rescue** in the merge trail: what was rescued, from which dead session, and that it enters review unmodified. A re-verify by the owning lane is ordered at next boot if the author-and-rescuer are different hands.

**The prevention half.** Rescue is the safety net; the shutdown ritual is the real fix. Every session's shutdown commits and pushes everything before ending (see `boot-shutdown.md`), and every boot prompt carries the shutdown ritual so disposable sessions close clean. Rescue frequency is a health metric: frequent rescues mean shutdown discipline is slipping.

**Adjacent hazard — never let a rescue destroy live assets.** When reconciling trees, do not check out a branch that *removes tracked assets* under an open editor/live environment — merge the trunk *into* the branch first so the switch is add-only, and move-aside backups before any reconcile. A rescue that triggers a destructive checkout has made things worse than the orphaned work it was saving.

## Why it exists

- The core procedure — "teams' sessions die with work staged/unpushed. Rescue = commit their staged tree VERBATIM on their branch with attribution, push, PR, review normally. Never rewrite their work in the rescue commit" — is the orchestration handbook's session-rescue rule (`studio:docs/kb/director-handbook.md` §5).
- The liveness gate is a scar: a stranded worktree "nearly died" and was rescuable, but the gate exists because "committing a mid-flight session's tree hijacks it" — rescuable only if the branch has no open change updated today, the tracker shows the session done/dead, and the human confirms nothing is live (`studio:docs/kb/director-handbook.md` §2, the stranded-worktree self-check).
- The prevention half is the founding incident of the shutdown ritual: work left uncommitted "does not exist to the successor," earned when a governance session left "its entire governance output uncommitted" and had to be recovered (`studio:docs/kb/director-handbook.md` §2b; `studio:docs/kb/studio-operations.md`, session-end ritual).
- The destructive-checkout hazard during reconciliation is a catalog row: "editor-open tree swaps → add-only checkouts (merge main into branch first); move-aside backups before reconciles" (`studio:docs/kb/director-handbook.md` §6).
- The no-commit-before-verification discipline reinforces why trees are often left deliberately dirty (held pending human verification), which is exactly the state rescue must handle without assuming abandonment (`validation:CLAUDE.md`, no-commit-before-verification).
- Two-repo test: the disposable-session model that makes rescue necessary is stated in both the studio operations doc ("Sessions are disposable by design") and the validation project's per-phase session model; the "commit each session, don't accumulate to audit-shock" rule is the validation project's independent version of the same statefulness law (`validation:CLAUDE.md`, two-repos section).

## Failure modes of the mechanism itself

- **Hijacking a live session.** Skipping the liveness gate and committing a tree whose session is still working — the worst failure, because it steals authorship and creates a conflict where none existed. All three gate checks are mandatory.
- **Rewriting during rescue.** "Improving" the dead session's work while committing it, which destroys the record of what actually existed and blurs the review's subject. Commit verbatim; fixes go through normal review afterward, attributed to the fixer.
- **Rescue-as-merge.** Treating the rescue commit as a merge and skipping the gates because "it was already done." Rescue only makes the work *visible and reviewable*; it does not confer any Definition-of-Done rung.
- **Destructive reconcile.** Letting the rescue's checkout remove tracked assets under a live environment. Add-only checkouts and move-aside backups, always.
- **Silent author-is-rescuer.** The orchestrator rescuing and merging without flagging that the same hands did both. Record it; order a re-verify.
- **Rescue as a crutch.** Relying on rescue instead of fixing shutdown discipline, so orphaned trees become routine. Track rescue frequency; a rising count means the prevention half is failing.

## What varies per project

The bindings layer declares the **worktree/branch topology** (how sessions map to trees and branches), the **liveness signals** for this project (what "updated today," "session done," and "live environment" concretely mean here), the **attribution convention** for rescue commits, and the **reconcile-safety rules** for the project's live environment (whether an open editor or server makes certain checkouts destructive). The *liveness gate, verbatim preservation, review-not-skip, and prevention-via-shutdown* are framework law. See `bindings/TEMPLATE.md` → worktree topology, liveness signals, and destructive-op rules.
