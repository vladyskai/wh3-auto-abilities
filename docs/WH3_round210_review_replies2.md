# Round 210: the second replies to the afternoon code review (2026-11-22)

## 1. The rulings

| Topic | The user's reply | What happened |
|---|---|---|
| The Loons | "I would like to change them completely." Caster standing, enemy infantry approaching between 25 and 15 m, cast in that direction, no friendly unit of more than one man in the path | BUILT |
| The caster-front breaths | "I tested Skarbscrath and it always starts at the caster" | BUILT for all five |
| Empty orders after the last use | "no" | Closed, nothing built |
| A transformed unit's new abilities | "it's true that they never fire. you can see the log" | BUILT |
| The lag before the transformation | "Please check if the mod might be the cause" | Found in the test build's logging, trimmed |
| Slow units and charging, option B | "okay, do it" | BUILT |
| The grid behind "at most 5 soldiers" | "then leave it" | Left |

## 2. What changed in battle

1. **Spinning Loons, The Loons of Eight Peaks.** They fire when all of this is true: the Night Goblins stand, an
   enemy infantry unit of more than one man is moving and coming closer, its edge is 15 to 25 m away, and none of your
   units of more than one man stands in the fanatics' path. The path runs from the Goblins towards that enemy, 84 m
   long. It is 4 m wide each side at the start and 60 m each side at the end, because the fanatics turn at random (the
   width is simulated from the game's own numbers). Your Lords and Heroes on foot do not block it. The order goes on
   the ground in the enemy's direction. They no longer fire at an enemy that is already in melee.
2. **Shatter, Pestilent Breath x2, Fishy Breath, Skabscrath.** The mod now treats the breath as what you saw: it
   starts at the caster, thin, and widens. Before, it was a band of the full width starting at the caster and reaching
   36 m too far. So it stops holding for your units that stand beside the breath or beyond its end, and it fires only
   when enemy soldiers really stand under the cone, with at most 5 of yours.
3. **Charging.** A unit counts as charging when it runs at a target, will hit within 4 seconds, and still has a
   run-up left. The run-up was 12 m for everybody. It is now the smaller of 12 m and what the unit runs in 2 seconds.
   Skeleton Warriors (2.8 m/s) need 5.6 m. A unit of 6 m/s or faster is exactly as before.
4. **Transformation.** Malus Darkblade keeps his unit number and his unit type when he transforms, so the mod never
   noticed. Now, 2 and 10 seconds after any ability is cast on a unit (by you or by the mod), the mod reads that unit's
   ability list again. If it changed, the unit's new abilities fire, and from then on the unit is read again every 4
   seconds, so the change back is seen too.
5. **The lag.** In the test build only: while a unit that owns Deadly Onslaught was selected, the mod wrote one log
   line per ability, 982 lines, every second (31,392 lines in the 34 seconds before your transformation). It now
   writes only the lines of badges that exist. The Workshop build never had this code.

## 3. Proof

- RED control (the pre-round snapshot, `docs\backups\round210\`): every new world behaves the old way.
- GREEN: harness 208, full suite, 8,479 checks, 0 failures (`mod_source\releases\20261122_replies2_harness208\h208_run1.txt`).
- The cast trace of the whole suite: 2,187 worlds, 1,718 casts, the two builds differ only in the 3 probe casts.
- Test pack md5 `8760b82d91ec7feaff51eaf39a0f5ea1` (1,659,510 bytes), release pack md5 `9a1e8f9a812e06c2168157d256e1a9e4`. Workbook v84.

## 4. Rebased pins (old value, new value, why)

| Where | Old | New | Why |
|---|---|---|---|
| harness 97, 98, 101, 102 count pins | 74 enemy_ground_melee entries | 72 | the Loons left the family |
| harness 142 (0zn) | the two Loons entries on enemy_ground_melee | on enemy_wave_charge | the same |
| harness 142, worlds LO1 and LE1 | an enemy in melee 10 m away: one cast | no cast | the Loons no longer fire at an enemy in melee |
| harness 162 (0zz11), harness 202 (0zz50) | 0 enemy_wave_charge entries | 2 | the Loons |
| harness 207 (0zz55) | ring_clear on 2 entries, a ring table | on none, an empty table | round 209's ring is superseded |
| harness 207, world LN2 | a clear 98 m ring: one cast | no cast | the same |
| harness 66 (H1i), harness 73 (I2d) | 1 and 2 reads of a unit's ability list | 2 and 4 | the list is read again 2 s after a cast |
| builder, rounds 162 and 164 | 83 keys in the WW table, 0 enemy_wave_charge entries | 85, 2 | the Loons |
| builder, round 203 | enemy_wave_charge keys launch from the target's near edge, 0 entries | from the caster's front, 2 | the Loons |
| builder, round 205 | 20 growing rows, each an exact wave | 25, each an exact wave or a caster-front breath | the five breaths |
| builder, round 209 | the ring on the two Loons | on no entry | superseded |
| builder | 74 enemy_ground_melee entries | 72 | the Loons |

## 5. What is not verified

- Nothing of this round has been seen in a battle.
- The Loons: whether the game aims the fanatics along the ordered direction. They are released "at the caster's
  front" in the game's table. If they always leave along the unit's facing, the Goblins must face the enemy.
- The Loons' path has no extra 10 m margin: the rule says "in the path". The path's width is the simulated drift.
- "Approaching" is Claude's number: the gap shrinks at least 1 m per second, measured over one second.
- The four other breaths start at the caster by the same table entry as Skabscrath. Only Skabscrath was seen.
- The transformation fix rests on the game returning the new abilities in the unit's ability list. The log line
  "owned abilities changed: unit" in the next battle confirms it.
- The lag: the dump is the only heavy thing the log shows. Whether it was the whole cause is not measured.

## 6. Still open from the review

Chain Lightning, the area blasts counting walkers (left by the user). Hell Hammer, the fliers under an exact wave,
Flesh-eating Scarabs, the delayed self blasts, the Frost Dragon Scale, the pause and selection case, the three
neighbour measurements, the late start of the "running at us" test (never ruled).
