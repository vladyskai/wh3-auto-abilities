# Round 164: the friendly-fire breaths (sign-off round)

Date: 2026-11-16. Harness: `harness163.lua`. Release folder: `mod_source\releases\20261116_breaths_harness163\`.

## 1. The batch

The 28 in-wheel abilities under the 2026-10-09 family rule "breath / cone damage (friendly fire)". That was a RULE, never a
ruling on these abilities one by one. They are VORTEX breaths; the 77 projectile breaths already ride `enemy_blob`. Every
contact side effect was named in the proposal (the round-163 lesson):

| Abilities | Side effect on contact |
|---|---|
| Blue Fire of Chaos x2, Pink Fire of Tzeentch x2 | warpflame: armour -10, fire weakness 10 s |
| Stream of Corruption x2 | poison: speed and damage x0.85, 10 s |
| Tidecall | speed x0.75, 10 s |
| Wind Blast | speed and charge speed x0.6, acceleration x0.35, 12 s |
| Disembowelling Sweep | morale -6 |
| Flesh-eating Scarabs | morale -16 |

## 2. The rulings (user, 2026-11-16)

| Group | Ruling |
|---|---|
| 18 target-launched breaths | "Wave rule" |
| Tidecall, Wind Blast (slows, rule 10) | "Charge, clear path" |
| 5 breaths from the caster's front | "Clear cone, most value" |
| Disembowelling Sweep, Flesh-eating Scarabs, Da Boss' Loons | "Sweeps clear; Loons as wanderer" |
| Does the caster count in its own wave's corridor? | "Caster doesn't count" |

**Why the caster question came up:** these breaths start 12 to 36 m before the target, so for a close target the start
sits on the caster. With the caster counting, Bangstick (35 m) and Kovsh Breath (10 m) could never fire, and the rest only
at 55 to 70 m. The data does not say whether a caster is hurt by its own breath.

## 3. The change (what you will see in battle)

All new entries start on M.

**`enemy_wave` (+18):**
- **The breaths:** Bangstick, Black Dragon Egg, Blue Fire of Chaos x2, Fiery Ring of Thori, Gaze of Malice, Jade Lion's
  Breath, Kovsh Breath, Lash of Slaanesh x3, Pink Fire of Tzeentch x2, Scorch, Stream of Corruption x2, Sunfang, The Spear
  Slaupnir.
- **The rule:** the caster and the target stand still, and the path holds the most enemy value with none of our other
  units within radius + 10 m (none of these breaths turns).
- **Blue Fire:** ground-only, and the game refuses it while its caster fights (GENERATED `FOURTH.WW_NOMELEE_TEXT`), so it
  casts on the ground and waits while its caster is in melee.

**NEW `enemy_wave_charge` (Tidecall, Wind Blast):** a fast enemy closing on our units, with the wave's path from the
caster through it clear of ours; the most value on the path.

**NEW `enemy_cone` (Fishy Breath, Pestilent Breath x2, Shatter, Skabscrath):**
- **Conditions:** a standing enemy in range, and the caster standing.
- **The zone:** from the caster through the target, the launch offset + the breath's length (60 to 108 m), radius + 10 m
  wide, must hold none of our other units.
- **The pick:** the most value in that zone.

**NEW `enemy_sweep` (Disembowelling Sweep, Flesh-eating Scarabs):**
- **Conditions:** the caster in melee and not wavering, and none of our other units within the sweep's reach + 10 m
  (22 m and 46.5 m).
- **The target:** the closest enemy in melee in range.

**`enemy_wander` kind 6 (Da Boss' Loons):** released at the caster, so the ring is around the caster. The data gives no
turn schedule, so its reach is the full 84 m: 98 m clear.

**"Caster doesn't count":** a caster's own breath or wave never blocks its cast. This also applies to round 162's 12 waves
(their workbook texts are reworded).

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 6,947 | 0 | `h163_run1.txt` |
| FULL, run 2 | 6,947 | 0, byte-identical | `h163_run2.txt` |
| RED, pre-164 snapshot | 6,925 | 0; RED 16/16 | `h163_red.txt` |

**Section 163** (13 worlds, both files):
- **Sunfang:** fires at a standing target 40 m away, though the caster sits in its own corridor.
- **Kovsh Breath:** fires at 8 m.
- **Blue Fire:** holds while its caster fights, and casts on the ground when free.
- **Wrath of Manann (round 162):** now fires with its caster inside the old corridor; the RED build refused.
- **Wind Blast:** fires at a fast enemy, not at a standing one.
- **Pestilent Breath:** fires, and holds when our Swordsmen stand beside the cone.
- **Disembowelling Sweep:** fires in melee, and holds with our unit 15 m away.
- **Da Boss' Loons:** fires on a clear field, and holds with our unit 90 m away.

## 5. Pins rebased

| Pin | Old | New |
|---|---:|---:|
| entries (harness; builder 11 gates) | 918 | 946 |
| keys (harness; builder round-160 gate) | 975 | 1,003 |
| full-table iterations | 1,836 | 1,892 |
| multi-use charge-gate keys | 304 | 328 |
| wind-up keys | 310 | 334 |
| `range_real` fields | 389 | 417 |
| target classes | 47 | 56 |
| `enemy_wave` (harness 161; builder round-162 gate) | 12 | 30 |
| `enemy_wander` (harnesses 161, 162; builder round-162 gate) | 42 | 43 |
| WW keys (builder round-162 gate) | 56 | 84 |
| tooltip mirror | - | + 3 wordings |

## 6. Build and install

- **`build_and_install164.py`:** ROUND 123 to 164 gates OK. The new gate checks the three families, their wiring, that
  they start unarmed, the caster exclusion, the WW caster gate, and the WW_NOMELEE list regenerated from the game data.
  `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`b4ff0c03c8246166b426bb881c2012aa`**, 1,701,972 bytes, `IDENTICAL True`.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261116_round164.pack`;
  - `archive\mod_source\round164\` (source md5 `8a774c39e191f7508694b5490b52c847`, annotated md5
    `dde20f321ef3d8fbd59ed7c73b2e05f7`).

## 7. Roster documents and audits

- **Workbook:** `docs\WH3_abilities_master_v48_2026-11-16.xlsx` plus `.ods`; `XLSX v48 VERIFY OK`.
  - 1,003 implemented, 36 skipped, 95 families.
  - The 28 rows carry their texts, and the 12 round-162 waves are reworded.
  - v1 to v47 are byte-unchanged (90 files).
- **Tracker:** the 28 rows plus section 10.42.
- **Database:** three family texts; the wave text notes the caster rule; `DATABASE VERIFY OK`.
- **Audits:** `WHEEL-STATUS AUDIT OK`; trigger audit R1 to R8 all 0.
- **Progress page:** 1,003 automated, 65 decided by the user, 55 open (all shut by an old rule).

## 8. Not done, and honest notes

- **Not seen in the game.** Rounds 162 to 164 wait for a battle, from log byte 735,692,926.
- **Unchecked:**
  - that a caster is never hurt by its own breath (the ruling assumes it);
  - what the cones' 24 to 36 m "activator_front" offset is measured from (the zone covers the whole possible reach).
- **Loons and Scarabs** need 98 m and 46.5 m of clear ground around the caster, so they will fire rarely.
- **Still shut by an old rule (55):** 19 own-troop auras, 22 collection-time skips, 7 flanking, 5 mutually exclusive, 2
  bombardment. Also the user's own 9 "skipped (revisit)".
