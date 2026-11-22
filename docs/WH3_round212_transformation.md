# Round 212: a transformed unit is a new unit (2026-11-22)

## 1. What the probe showed

The user transformed Malus Darkblade once more with the round-211 probe installed.

| Time | The army's own list | The list the mod read |
|---|---|---|
| before Tz'arkan | unit 1001, Malus Darkblade, Deadly Onslaught and his other abilities | unit 1001 |
| after Tz'arkan | unit 1002, "malus_darkblade_tzarkan", Bloodstorm and Reaper of Souls, moving, in melee, losing health | unit 1001, frozen: same place, full health, not in melee |

So the game replaces the unit. The transformed Malus is a new unit with a new number. The old one stays in the list
the mod used, as a frozen copy.

## 2. The change, in plain words

- Every 10 seconds (and now also 2 seconds after any ability is cast) the mod rebuilds its list of units to watch. It
  now takes that list from the army's own unit list.
- A unit that both lists know is handled exactly as before.
- A unit that only the army's list knows (the transformed Malus) is added. The mod creates the order handle it needs
  to cast for that unit. If the game refuses that handle, the unit is left out and nothing is ordered.
- A unit that the army's list no longer has (the frozen old Malus) is dropped. It no longer casts and no longer counts
  as one of your units in the friendly-fire tests.
- If the army's own list cannot be read or is empty, the mod uses the old list, as before.

In battle: about 2 seconds after Tz'arkan, Bloodstorm and Reaper of Souls belong to a unit the mod watches, with their
letters and their normal triggers (Bloodstorm in melee, Reaper of Souls in melee below 75% health).

## 3. Proof

- RED control (the pre-round snapshot, `docs\backups\round212\`): the new unit never casts, the frozen copy keeps
  casting.
- GREEN: harness 210, full suite, 8,510 checks, 0 failures.
- The cast trace: 2,200 worlds, 1,771 casts, the two builds differ only in the 3 probe casts.
- Test pack md5 `c0cff66cf0cf511028f31f492334c590` (1,665,749 bytes), release pack md5
  `17d703e53634735c64fc87ddee57f744`. No workbook version: the roster and every trigger text are unchanged.

## 4. Rebased pins (old value, new value, why)

| Where | Old | New | Why |
|---|---|---|---|
| harness 66, the count of `rebuild_unit_list()` in the file | 3 (annotated), 4 (live) | 4, 5 | the poll also re-lists 2 s after a cast |
| harness 66, world H2 (a unit the game stops listing) | still read 39 times and 5 casts before the re-list at 10 s | read 8 times, 1 cast | it cast at the first poll, so the re-list 2 s later drops it |

## 5. What is not verified

- Nothing of this round has been seen in a battle.
- `army:create_unit_controller()` and `uc:add_units(unit)` are the calls the game's own script library uses to make
  its script units. The mod has never called them in a battle. If they fail, the transformed unit is left out.
- Whether the letters on the transformed unit's buttons react to clicks (the selection callback is registered for the
  new unit the same way as for every unit).
- What happens when the transformation runs out: if the game brings back unit 1001, the mod watches it again through
  the army's own list. If it makes yet another new unit, that one is added the same way. Neither has been seen.
- Summons that join the player's own army are now watched too, when they own abilities of ours.
