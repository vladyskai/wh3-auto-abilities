# Scope gates and verification cadence

Two rules that decide WHAT ships and HOW MUCH to verify each round. Both are standing user
rulings, not per-round judgement calls.

## Only what the battle wheel can cast

`perform_special_ability` fires only abilities present in the unit's battle ability wheel
(bottom-left of the battle screen). An ability absent from the wheel is dead weight: it will
never fire, whatever its trigger says. Prove an ability is wheel-side before implementing it.

Army-bar is the trap. It is expressed as an `army_spec` junction, and `source_type` alone does
NOT reveal it - several army-bar keys are `source_type = bound`, so a `source_type`-only
classifier reports them as in-wheel. Join the `army_spec` key set explicitly and exclude every
key in it, with no exceptions list. Use one reason string so the reason column and the status
column can never disagree:

    excluded (army-bar ability - army_spec junction - not in the battle ability wheel,
    so it can never be cast)

Enforce the roster rule as a BUILD gate, not a manual cleanup:

- refuse to build if any key in the shipped ability table is in the army-bar set;
- make the wheel-status audit fail on any row marked in-wheel whose provenance says army-bar;
- make the database verifier run the same check.

A rule that lives only in the spreadsheet drifts back within two rounds.

Never argue for keeping an army-bar entry because it "works" - a non-wheel ability cannot
have been firing at all. When a status column and its own reason column contradict each other,
the status is usually the lie; reconcile against the game's provenance tables, not the sheet.

Related roster rules already settled elsewhere: no army-bar, no boss-only (`_boss` grant),
no illusions (`spawn_is_decoy`), no out-of-wheel spells.

## Verification cadence: light while tuning, full at sign-off

Roughly halves round time, and the user explicitly approved it:

- **TUNING round** (one constant, one measurement, one threshold): run only the affected
  harness section, and do not regenerate the workbook. State plainly that the full suite and
  workbook were skipped and what that leaves unverified - never imply a green full suite.
- **SIGN-OFF** ("update the spreadsheet", or any roster/scope change): run the FULL suite and
  produce the workbook version, reconciling every light round since the last one.

Keep every earlier harness section in the file with its boundary pin, so a full run stays one
command after a string of light rounds. Light mode keeps floors; raise the floors to exact
values at sign-off.

### Pin forensics: stale mirror vs regression

When a full run fails, discriminate before fixing. A failure whose content is byte-equal to a
pre-change backup is a STALE MIRROR PIN - a hand-kept copy of a tip, table or status string
that the round did not update - not a regression. Fix the pin and report it as a pin. A real
regression shows content the backup does not contain.

Hand-kept mirrors are the usual culprit: any test that re-quotes a tooltip, a trigger table or
a count instead of reading it from the source will drift every time the source changes. Prefer
asserting on the source; when a mirror is unavoidable, diff it against the pre-change snapshot
before believing a failure.

## What a light round must still say

Even when skipping the suite, report:

- which section ran and its counts;
- how many assertions were retouched, and why;
- that the full suite and workbook were skipped, and the specific things left unverified
  (other families against this source, exact suite totals, any engine read only exercised by a
  mock).

A light round that reports "green" without those qualifiers is indistinguishable from a broken
one.
