# Round 203: free aim for the straight waves (2026-11-22)

## 1. What the user saw

Two battles: the Fiery Ring of Thori never fired with a good target in range. The mod tested one line per enemy, from the
caster through that enemy, and one of our units stood within 16 m of every such line. In the game the player can place a
wave and rotate it.

## 2. The rulings (user, 2026-11-22)

- "Yes, build the probe" (round 202). Its result: a ground-form order starts the wave at the point and sends it along the
  orientation (three casts, one real turn, judged by eye).
- "A: but be careful. Dragon breaths always come from a caster. Other abilities might also, check individually to be
  sure." A = free aim on standing targets only.
- "All 30 placed" (the scope).

## 3. The individual check

`tools\list_wave_sources.py` reads, for every key, where the game starts the effect (`battle_vortexs.launch_source`).

| Group | Keys | The game's launch source | Free aim |
|---|---|---|---|
| enemy_wave | 30 | target_near_edge (placed at the target) | yes |
| enemy_wave_charge (Tidecall, Wind Blast) | 2 | target_near_edge | no (not in scope) |
| enemy_cone (Fishy Breath, Pestilent Breath x2, Shatter, Skabscrath) | 5 | activator_front (from the caster) | no |
| real dragon breaths | 77 | projectiles from the caster (the blob family) | no, not touched |

The build now refuses a key on enemy_wave that is not placed by the game or has no ground form, and a cone key that does
not start at the caster.

17 of the 30 are labelled "breath" by the game. Only the Fiery Ring of Thori has been seen rotating in a battle. For the
other 29 the placement is read from the data.

## 4. The change

For each enemy that is in range, visible, allowed by the game's target rule and standing still:

1. The caster's own line is tested first, exactly as before.
2. Then 24 compass headings (one every 15 degrees). Each path starts the ability's own offset plus the target's half
   extent before the enemy's centre and rolls the ability's path length along the heading.
3. A free path counts only when its START is inside the ability's cast bound from the caster (the caster never walks)
   and none of our other units stands within the round-162 distance (radius + 10 m, growing with the drift).
4. The path with the most enemy value wins. The caster's line keeps a tie.

The order:

- The caster's line wins: the old order, at the enemy unit (`perform_special_ability`).
- Another heading wins: `perform_special_ability_ground(key, start point, heading, 0)`. The point is built with the
  game's `v(x, height, z)` on `bm:get_terrain_height`. A point that cannot be built means no order (fail closed).
- Blue Fire of Chaos (2 keys) has no unit form. It is now ordered at its path's start with the bearing to the target.
  Before, it was ordered on the enemy's centre with orientation 0, which the probe shows was misaimed.

The pre-cast re-check repeats the test on a fresh map with the same heading. A new log line names the aim:
`FREE AIM: the wave starts at (x,z) and rolls on bearing B` and `free-aim cast : perform_special_ability_ground(...)`.

New code: `FOURTH.FREE_AIM_STEPS`, `FOURTH.ww_aim`, `FOURTH.ww_bearing`, `FOURTH.ww_aim_value`, `FOURTH.ww_line_value`,
`FOURTH.ww_aim_text`, `FOURTH.aim_cast`. `FOURTH.ww_aim` is cleared in `FOURTH.entry_reset`. TEST-ONLY switch
`ZZ_AUTO_TEST_NO_FREE_AIM` (the harness sets it for older worlds, the release reads it as nil).

The hover card is unchanged: "Fires when the target stands still, down the path with the most enemies, clear of allies".

## 5. Proof

- RED control on the pre-round source (`h201_red.txt`): Zombies at (0,60), our Miners at (0,30) on the caster's line, no
  order at all. Two Zombie units side by side: one unit-form order through one of them. Blue Fire: orientation 0.
- GREEN, harness 201, full suite: **8,301 checks / 0 failures** (`h201_run1.txt`). No older pin moved.
  - FA1 the user's battle: ONE ground order, start 69 m from the caster, bearing 75, through the Zombies' centre, 29 m
    from the Miners' centre.
  - FA2 nothing in the way: the old unit-form order.
  - FA3 two units side by side: ONE ground order across both.
  - FA4 no vector constructor: no order.
  - FA5 Blue Fire: ONE ground order at the path's start, orientation 37.
  - FA6 a walking enemy: no order.
- Installed test pack: md5 `14e1d8cf6e1882279556c0a1bf80e2ee`, 1,635,145 bytes.
- Release pack rebuilt: md5 `e6d6b983aeda3234ea3e81e3ea48afa9`. Cast trace of the whole suite on both builds: 2,107
  worlds, 1,670 casts on the test build. The release differs in exactly 3, the round-202 probe casts it removes.
- Workbook v80 verified (14 checks): the 30 wave rows carry the FREE AIM sentence, nothing else changed.

## 6. Skipped, stated plainly

- The full suite ran once, not twice.

## 7. Not verified

- Nothing of this round has been seen in a battle.
- That the wave starts exactly at the ordered point (the probe showed it by eye, one real turn).
- That the 29 other placed keys accept an oriented ground order like the Fiery Ring.
- The cost of 24 headings per enemy per poll in a large battle (each test walks our units and the visible enemies).
- The half extent used for the start is one number per unit, whatever the heading.
