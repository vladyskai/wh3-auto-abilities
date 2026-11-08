---
name: review-findings-verification
description: "Use when handed a critique/review: verify each finding."
---

# Verifying review findings before implementing them

The user (often with another AI's help) produces a critique/review document about
existing work and hands it over with a standing workflow: analyze every item,
then implement them one by one, high priority + low difficulty first.

The failure mode this skill prevents: implementing from the document's wording.
Reviewers work from a reading copy or an older revision, inflate numbers, and
propose fixes that contradict facts the project already measured.

## Procedure

1. **Verify against the artifact at its CURRENT state.** For each load-bearing
   claim, grep the live/installed copy: constant values, call sites and their
   guards, loop bounds, what a function actually iterates. Cite line numbers
   from the live file, not from the copy the reviewer read.
2. **Check each proposed fix in three layers before accepting it:**
   - the live artifact - does the described problem exist as described?
   - the project's own measured history - field logs, harness outputs, past
     experiments. A fix that contradicts a measured fact is a REJECT, not a task.
   - the platform's own code/API - where a fix depends on a capability
     ("call X instead"), verify X EXISTS in extracted API dumps/headers first.
3. **Treat suspicious numbers as a red flag; find the real ones.** Reviewers
   quote safety caps as observed costs and mix figures from different code
   paths (a walk cap stated as the node count; one function's figure attributed
   to another). Grep for the measured number or re-measure before believing it.
4. **Verdict scale + two-axis ranking.** Verdicts: Confirmed / Partly (real but
   wrong description or inflated numbers) / Wrong (the code does not do that) /
   Reject (the fix would hurt or is proven infeasible). Priority separates
   "changes current behaviour" from "only matters at the stated future scale" -
   say which for every item. Difficulty is its own axis (H/M/L).
5. **Deliverable shape.** A report FILE (for this user: Desktop; also put the
   substance inline in chat - file cards do not open for them). Per item:
   verdict, what the code actually does (line refs), what was measured,
   pros/cons, priority, difficulty, recommended action - no item without a next
   action. Plus a summary table, a proposed implementation order (high priority
   + low difficulty first), and the field questions only the user can answer.
6. **Implement ONE item per round after sign-off.** Minimal diff, harness/smoke
   proof, build/install, report the md5 plus a one-line check the user can run
   themselves where possible ("the log line X must now appear zero times").
   Implement the semantics-correct fix, not the shortcut that merely passes -
   this user states they are striving for perfection and accepts
   harness-verified changes without a field test when the change cannot alter
   user-visible behaviour (say so explicitly when that applies). Mirror every
   accepted functional change into any derived copy (annotated/reading version)
   in the same round, and state which items are done and which is next.
7. **Rejected items keep their reason.** State the measurement that rejects an
   item in one clause, or it resurfaces in the next review. An item describing
   code that was already fixed or removed is Moot - say so plainly; that is a
   fine outcome, not a failure to act.

## Implementation-quality rules (for the rounds themselves)

- When a finding is "some code path forgot to do X", fix the class, not the
  instance: COLLAPSE the call sites onto a single primitive that performs X
  internally, so no caller can skip it - do not just instrument every site and
  hope future edits remember. Then assert the ordering invariant mechanically
  (e.g. every write is immediately followed by its required follow-up call,
  violations == 0).
- **"All checks green" can be vacuous.** Validate every new invariant check
  with a MUTATION control: deliberately break the invariant in an in-memory
  variant and require the check to fail loudly. Note: a red control (pre-fix
  build) showing zero violations can be legitimately correct when the round is
  about ENFORCEMENT (the old code satisfied the invariant site-by-site; the gap
  was the missing primitive) - that is not proof the new check discriminates.
- **Diagnose from logs only after checking the log format's semantics.** A bare
  line can be a deliberate no-write marker for a no-op, not a missing action;
  check the format's markers before concluding a path skipped a step. A
  misread of format-as-absence costs whole build rounds. When a marker is
  ambiguous, make the writer disambiguate it (add an explicit '(no write)'
  style suffix) as part of the fix.
- A fix that "releases what it never took" or otherwise pairs setup/teardown:
  guard teardown on the SETUP'S SUCCESS FLAG (a real per-attempt flag), never by
  AND-ing the two configuration constants - a failed setup must also block
  teardown.
- A cap/limit that exists for safety should be set above any real value and
  documented as a runaway guard, not left as a working limit that silently
  truncates; prove a raised cap costs nothing by counting the affected work
  before and after (identical counts = the guard, not the cap, was bounding it).

## Pitfalls

- Do not implement from the document alone: reviewers cite a reading copy
  (logs stripped) or an older revision; verify against the live artifact first.
- "Reads plausible" is not "is true": for each claimed mechanism find the exact
  line; for each claimed cost find the measured number.
- Do not bundle several items into one round even when they look small - the
  loop is one-by-one; bundling defeats attribution and the user's sign-off.
- When the user challenges one of your own technical claims, test it against
  community sources AND the platform's own code before defending it; correct
  yourself openly when the claim was wrong. Do not assert a number (latency,
  limit, cost) you have not measured at the layer the user actually feels - and
  when stating a limit, give the platform's DELIVERED resolution, not the
  interval you requested.
