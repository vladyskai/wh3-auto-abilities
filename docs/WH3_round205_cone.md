# Round 205: the growing waves are cones, enemy single entities are not counted (2026-11-22)

## 1. What the user saw

- The Fiery Ring of Thori: "it worked perfectly this time with the dwarves". Round 204 is field-confirmed for it.
- "I tested with Sunfang and it casted on the terrain, not on the enemy unit" (a screenshot: a triangle of fire on empty
  ground beside the enemy line).
- A new ruling in the same message: "we should also ignore enemy single entities as the damage to them would be
  negligible".

## 2. The cause

The log line of the cast (bytes 1,027,314,867 to 1,036,362,003, `archive\logs\battle_20261122_r204_exact.txt`):
`FREE AIM: the wave starts at (-133.1,-124.8) and rolls on bearing 135 (moved 12 m sideways)`.

Sunfang in the game's `battle_vortexs` table: start_radius 0.1, goal_radius 12, expansion_speed 6 m/s, movement_speed
24 m/s, duration 2 s. It is a cone that grows 0.25 m per metre over its 48 m path. The mod used one radius, 12 m, from
start to end. To keep our soldiers out of a 12 m band it moved the path 12 m sideways, and the real cone, thin for most of
its length, missed.

The Fiery Ring is a cone too (0.1 m to 6 m at 0.0833 m per metre). Its error was half as large, so it worked.

## 3. The change

- `tools\gen_wave_cone.py` GENERATES `FOURTH.WW_CONE_TEXT`: for each of the 19 exact waves that grow, the start radius
  and the growth per metre. Only waves whose table radius is the vortex's own goal radius are taken (Hell Hammer's 14.1 m
  is its bombardment's, so it stays a band). The build compares the table with the game data.
- `FOURTH.ww_in_wave` tests a point against the radius the wave has at that point: min(table radius, start radius +
  growth x distance rolled). `FOURTH.wave_cover` uses it for our soldiers and for the enemy's.
- An exact wave's value skips enemy units of one man. A path with only single entities under it is worth nothing and is
  never ordered.
- The live reason line of an exact wave names its rule (it still printed the round-162 distances).

The 19 growing waves: Fiery Ring of Thori, Sunfang, Black Dragon Egg, Scorch, Stream of Corruption x2, Pink Fire of
Tzeentch x2, Blue Fire of Chaos x2, Lash of Slaanesh x3, Bangstick, Kovsh Breath, Jade Lion's Breath, Gaze of Malice,
Tidecall, Wind Blast.

## 4. Proof

- RED control on the round-204 source (`h203_red.txt`): Sunfang in a melee, the order puts 27 of 120 enemy soldiers under
  the real cone. A lone enemy Lord draws a cast.
- GREEN, harness 203, full suite: **8,320 checks / 0 failures** (`h203_run1.txt`).
  - CN1 Sunfang in the melee: 0 of our soldiers and 104 of 120 enemy soldiers under the real cone.
  - SE1 a lone enemy Lord: no order.
  - SE2 a Lord and a block: the wave goes to the block (119 of 120 soldiers).
- One rebased pin: harness 202 EX5, 120 to 100. It measured the chosen path with a band, and the path chosen for the real
  cone has 114 Zombies under that band measure.
- Installed test pack: md5 `c613f8a1338a6fce6fd87158bd2de72a`, 1,642,218 bytes. The first install was refused with
  WinError 32 (the game was running), the user closed the game. Release pack: md5 `0555626463e4e2da8f9b597a6872d4d0`.
- Cast trace of the whole suite: 2,115 worlds, 1,674 casts on the test build. The release differs in exactly the 3 probe
  casts it removes.
- Workbook v82 verified (13 checks): the 27 exact wave rows carry the new sentences.

## 5. Skipped, stated plainly

- The full suite ran once, not twice.

## 6. Not verified

- Nothing of this round has been seen in a battle.
- That the cone grows in a straight line as the table's numbers suggest (start, goal, expansion speed).
- Whether the fire's visible edge is the damage edge.
- The 5 drifting waves and Hell Hammer are still modelled as bands.
