# Round 202: the wave probe (2026-11-22)

## 1. Why

Two battles on 2026-11-22: the Fiery Ring of Thori never fired. The mod tests one line per enemy, from the caster through
that enemy, and one of our units stood within 16 m of every such line. The user's screenshot shows that the game lets the
player place a wave and rotate it. His question: "are we considering that this ability (and many others) we can choose
the start of the wave and its direction? Or are we checking it just from the casters direction?"

Answer: only the caster's direction. The game's script call for ground casts has an orientation argument
(`perform_special_ability_ground(key, position, orientation, width)`). The mod has always sent 0. Whether that argument
steers a wave has never been tried. Ruling: "Yes, build the probe".

## 2. What was built

A console command in the TEST build only. Nothing in the mod calls it, and no trigger changed.

    zz_wave(deg, fwd, side, key)

| Argument | Meaning | When left out |
|---|---|---|
| deg | the orientation sent to the game, in compass degrees | the bearing from the caster to the target |
| fwd | metres to move the point further along the caster-to-target line | 0 (the enemy's own position) |
| side | metres to move the point to the right of that line | 0 |
| key | an ability key | the first ready wave ability the unit owns |

It needs exactly one selected unit. It takes the nearest enemy we can see, orders the cast in the ground form, and
answers one line that is also written to the log:

    WAVE PROBE: <key> by unit <id> at (x,z) -> <enemy> at (x,z), <d> m away; point (x,z) = ...;
    bearing caster->target <b>; ORIENTATION SENT <deg>; order accepted

The release build removes the command (`tools\build_release.py`, DEBUG_GLOBALS).

## 3. How to run the test (the user)

Army: a Master Engineer with the Fiery Ring of Thori (3 uses) against any slow infantry. Keep our other units away.
Put the ring on M so the mod does not spend a use. Stand the Engineer 50 to 70 m from a standing enemy unit, select him,
open the Lua Console (Shift+F3) and run one line per use:

1. `zz_wave()` : the direction is the line from the Engineer to the enemy. This is the reference.
2. `zz_wave(B + 90)` : B is the bearing the first answer printed. If the wave now runs sideways, the argument works.
3. `zz_wave(B + 90, 0, 30)` : the same direction, the point moved 30 m to the right. This shows where the wave starts
   relative to the point.

What to report for each: where the wave started, which way it travelled, and whether the Engineer walked first.

## 4. Proof

- RED control on the pre-round source (`h200_red.txt`): the command does not exist, no order in any world.
- GREEN: harness 200, full suite, **8,272 checks / 0 failures** (`h200_run1.txt`). The section's six worlds: the
  orientation sent is the one asked for, the default is the bearing (37 degrees for a target at 30, 40), nothing selected
  means no order, a point that cannot be built means no order, a built point lands where computed (40, 45), and the probe
  orders nothing by itself.
- A defect found by the test and fixed before the build: the first version could pick a wave ability the unit does not
  own. It now reads the unit's own ability list.
- Installed test pack: md5 `529eb5cc2e6e72c6a01de1df54f11de2`, 1,629,275 bytes. Release pack rebuilt: md5
  `e926788ec15e5d29fe7e2cff70e0067b` (the command is removed there).

## 5. Skipped, stated plainly

- No workbook version: the roster did not change (982 entries / 1,035 keys). v79 stays current.
- The suite ran once, not twice.
- The cast trace between the test build and the release build was not repeated (the transform is unchanged apart from
  one more removed console command).

## 6. Not verified

- Everything this probe exists to find out: whether the orientation steers the wave, where the wave starts, whether a
  built point (the game's `v(x, height, z)` constructor with `bm:get_terrain_height`) is accepted.
- The mock has no vector constructor of its own. The harness supplies one for one world.
