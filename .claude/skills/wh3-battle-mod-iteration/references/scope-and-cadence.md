# Scope rule and iteration cadence

## Hard scope rule: only what is on the battle ability wheel

An ability absent from the battle ability wheel cannot be cast: `perform_special_ability`
has no button to press, so the entry can never fire, and shipping it inflates the coverage
number with triggers the user will never see. Army-bar abilities (`army_spec` junction,
often `source_type = bound`) are the trap: they look in-wheel to any classifier that reads
`source_type` alone, which is exactly how they got counted as in-wheel for several rounds.

- Before adding or counting any ability, intersect the mod's key set with the `army_spec`
  key set. A non-empty intersection is a bug, not a judgement call.
- Keep the check in the BUILD (refuse to build, naming the offending keys) and in the
  sheet audit, with **no exceptions list** - a hand-kept exception is how the bug returns.
- Removing such an entry loses nothing. Never argue "we would lose working triggers":
  there were never working triggers.

## Iteration cadence (user's standing preference)

- **Tuning rounds:** run ONLY the affected harness section; skip the versioned workbook,
  the tracker rewrite and the release docs.
- **Sign-off rounds:** full suite plus the workbook regenerated, then reconcile the
  bookkeeping rounds that were deferred.
- Deferring bookkeeping is fine; deferring it *silently* is not. Name in the hand-off what
  stays unverified and which documents are now stale.
- When the rule itself is unsettled, print the candidate code and explain it in plain words
  BEFORE implementing. This user does not read Lua fluently: he approves the logic, not the
  syntax, so the explanation must state the numbers, the units and what happens in each case.

## Explaining a rule back to the user

He does not keep a running memory of round numbers. When a rule is referenced by round,
restate it in full sentences with the actual constant, or he will have to ask what it means.
