# Round 163: the placed areas and the expendable units (sign-off round)

Date: 2026-11-16. Harness: `harness162.lua`. Release folder: `mod_source\releases\20261116_placed_areas_harness162\`.

## 1. The batch

The 28 in-wheel abilities under the 2026-10-09 family rule "placed / static area damage (friendly fire)". That was a RULE,
never a ruling on these abilities one by one. The facts come from the game's vortex, phase and (NEW this round)
bombardment tables (`gamedata\wh3\projectile_bombardments.tsv`).

## 2. The rulings (user, 2026-11-16)

| Group | Ruling |
|---|---|
| 7 instant blasts (Acorns of the Oak of Ages, Blight Boil, Frost Fang, The Hammer of Smednir, Viletide, Crackleblaze, Lamprey's Bite) | "Like Dwellers Below" |
| 14 lingering areas (Boiling Cauldron, Simmering Pot, Brass Orb x3, Infernal Gateway, Pit of Shades x3, Rubric of Dark Dimensions, Irresistible Plague, Plaguemaster, Warp Junction, Magma Storm) | "Same as the blasts" |
| Arcane Vassal | "Most enemies around" |
| The other 6 | "Check one by one" |
| Befuddlement of Mischiefs | "charge only. Makes no sense to use it in melee as it would still be fighting while frozen"; then "Any fast enemy" |
| Winged Staff | "Area drain rule" |
| Chain Lightning (Regiment of Renown) | "Wanderer rule" |
| Siegebreaker | "Strike a standing large single" |
| The Rune and Master Rune of Wrath & Ruin | "Close the runes" |
| The Hammer of Smednir (raised by the audit) | "Keep the blast rule" |
| Expendable units (the user's own request mid-round) | "Game's set + cheap undead" |

**The user's two checks during the proposal:**
- **"Befuddlement only grounded?"** Nothing in the extracted tables says grounded-only: no flag, no flying rule on the
  effect. The user chose "Any fast enemy".
- **"Siegebreaker only on walls?"** Only partly true:
  - as a unit target, the game's flag refuses any unit not climbing, manning equipment or on a platform;
  - as a ground target, it accepts any point;
  - its stated purpose is "Destroys buildings and siege vehicles".

## 3. The change (what you will see in battle)

All new entries start on M (none of their families starts armed).

**On `enemy_wander` (22): the 7 instant blasts, the 14 lingering areas, Chain Lightning (RoR).**
- **Conditions:** the caster and the target stand still.
- **The target:** the blob rule: the enemy infantry blob worth the most.
- **The safety ring:** none of ours within radius + reach + 10 m.
- **The two exceptions:** Crackleblaze cannot hit our units (no test). Lamprey's Bite travels 24 m, so its ring is 59 m.

**Magma Storm:** besides its 20 m vortex it drops 60 bombs scattered over a 60 m radius, each a 5 m AP blast. The
WW table now reads bombardments, so its safety distance is 75 m. The 20 m vortex still scores the target, otherwise it
would need over 2,800 soldiers inside its circle.

**NEW `ally_blast` (Arcane Vassal):** our unit (or the caster) within 140 m whose 15 m blast circle covers the most enemy
value. The ability is cast on that unit, and the blast hits enemies only.

**NEW `enemy_strike` (Siegebreaker):** the most valuable standing single-entity enemy (Lord, Hero, monster) within 70 m,
with none of ours within 11 m. The strike lands on the ground under it.

**Existing families gain one each:**
- Befuddlement on `enemy_fast_near_ally`: a fast enemy closing on our units;
- Winged Staff on `enemy_area_drain`: 25 per tick.

**Expendable units:** every friendly-fire check reads one list of our units, and it now leaves out two kinds.
- **What's left out:**
  - our units the game marks expendable (48, GENERATED `FOURTH.EXPENDABLE_TEXT`, `tools\gen_expendable_keys.py`:
    Skavenslaves, Goblins, Night Goblins and Fanatics, Gnoblars, Ungors, Snotling Pump Wagons, Cathay peasants,
    Pigback Riders, Prisoners and others);
  - our units worth less than 2 per soldier (live value: Zombies, Skeletons and the like).
- **Every check is covered:** the blob attacks, the magic missiles, the round-159 blasts, the waves, the wanderers and
  this batch.
- **What it means in battle:** a blast is now allowed to land next to our Skavenslaves and will kill some of them.

**Correction:** Hell Hammer (round 162) also drops a 14 m, 24/24-damage bombardment blast. Its corridor radius is now
14.1 m. The old corridor (5 + 10 m) already covered that blast, by 1 m.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,892 | 0 | `h162_run1.txt` |
| FULL, run 2 | 6,892 | 0, byte-identical | `h162_run2.txt` |
| RED, pre-163 snapshot | 6,866 | 0; RED 16/16 | `h162_red.txt` |

**Section 162** (14 worlds, both files): Frost Fang casts with our Swordsmen 55 m away and holds them at 20 m. It casts
beside our Skavenslaves (expendable) and our Zombies (0.5 per soldier). Banishment casts beside our Skavenslaves; the RED
build refused that. Magma Storm holds ours at 55 m and casts at 115 m. Arcane Vassal casts on our Hero fighting inside
an enemy block, and not without enemies. Then Befuddlement on a fast enemy, Winged Staff on a standing block, Chain
Lightning, and Siegebreaker on a standing Vampire, but not on a moving one.

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 892 | 918 |
| keys (harness; builder round-160 gate) | 949 | 975 |
| full-table iterations | 1,784 | 1,836 |
| multi-use charge-gate keys | 287 | 304 |
| wind-up keys | 289 | 310 |
| `range_real` fields | 365 | 389 |
| target classes | 43 | 47 |
| `ally_range_real` fields (harness 98/99/104; builder) | 57 | 58 |
| unbounded entries (harness 102; builder) | 1 | 2 |
| `enemy_fast_near_ally` (harness 135/137; builder round-135 gate) | 8 | 9 |
| `enemy_area_drain` (harness 157; builder round-158 gate) | 7 | 8 |
| `enemy_wander` (harness 161; builder round-162 gate) | 20 | 42 |
| WW keys (builder round-162 gate) | 32 | 56 |
| SHOT keys (builder 3 gates) | 35 | 36 |
| tooltip mirror | - | + 2 wordings |

## 6. Build and install

- **`build_and_install163.py`:**
  - ROUND 123 to 163 gates OK. The first three builds were refused by older count gates (the round-135, ally-range and
    unbounded counts) and left the installed pack untouched.
  - `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`66cb4f7ca1ddde52d5af56937ec740d4`**, 1,681,383 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261116_round163.pack`;
  - `archive\mod_source\round163\` (source md5 `e7ef0be964d4b5f2c9fa0ecb164a5505`, annotated md5
    `ab6df467846fdd15d3679bc92decf250`).

## 7. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v47_2026-11-16.xlsx` plus `.ods`; `XLSX v47 VERIFY OK`.
  - 975 implemented, 36 skipped by the user, 92 families; v1 to v46 byte-unchanged (88 files).
  - **Correction recorded:** v46's prose says "206 - 34 = 172"; the right figure is 174, which v46's own cell shows.
- **Tracker:** the 28 rows plus section 10.41; the same slip was fixed in section 10.40.
- **Database:** two family texts; `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`.
- **Trigger audit:** it first raised R4 = 1. The Hammer of Smednir carries a x0.4 speed on its self slot, which I had not
  named in the proposal. The user kept the blast rule, and the audit records it as ruled. R1 to R8 are now all 0.
- **Progress page:** 975 automated, 65 decided by the user, 83 open (all shut by an old rule).

## 8. Not done, and honest notes

- **Not seen in the game.** Rounds 162 and 163 wait for a battle, from log byte 735,692,926.
- **The blob density line** (half a packed block) grows with the radius. The 20 m and 25 m areas (Blight Boil, Magma
  Storm, The Dwellers Below, Lamprey's Bite) need 265 to 414 soldiers inside, so they fire only on dense, multi-unit
  blobs.
- **Lingering areas:** the cast-time check cannot see our units that walk in later.
- **Still shut by an old rule (83):** 28 friendly-fire breaths, 19 own-troop auras, 22 collection-time skips, 7 flanking,
  5 mutually exclusive, 2 bombardment. Also the user's own 9 "skipped (revisit)".
