# Round 177: the score-3 review, rows 1-22 (sign-off round)

Date: 2026-11-18. Harness: `harness176.lua`. Release folder: `mod_source\releases\20261118_score3_rows_harness176\`.

## 1. The ruling

User, 2026-11-18: "Implement all until item 22, except the number 3 that should stay the same."
(`docs\WH3_score3_review_2026-11-18.md`, rows 1-22.)

## 2. What changed (what you will see in battle)

| Row | Ability | Before | Now |
|---|---|---|---|
| 1 | Blood Omens | in melee | NEW **slow_army:** a visible fast enemy closing within 40 m of any unit of ours, or the caster in melee |
| 2, 18, 21 | Creature-Killer, Steppe Hunter's Horn, The Ostermark Runefang | in melee | NEW **melee_vs_large:** the caster, or a unit of ours within 24 m, fighting a LARGE enemy |
| 4 | Empowering Shrooms | in melee | NEW **ally_squig_melee:** cast on the nearest SQUIG ally within 70 m that is in melee |
| 5 | Everyone Has Their Price | in melee | NEW **enemy_melee_near:** the caster in melee, or a visible enemy within 24 m in melee |
| 6 | Fury of the Land | in melee | NEW **aura_charge_or_melee:** the caster or a unit within 38 m charging, just in contact, or in melee |
| 11 | Refuse to Die | in melee | NEW **melee_health25:** in melee at or below 25% health |
| 12 | Rune of Oath & Steel | in melee | **melee_or_under_fire** (exists) |
| 14, 19 | Shield of Aeons, The Armour of Morkar | in melee | NEW **guard_aura:** in melee or under fire, or a visible fast enemy moving inside the aura (38 m / 24 m) |
| 15, 16 | Shielding Swarm, Shielding Swarm Upgraded | in melee, on self | NEW **self_or_ally_fire_melee:** self in melee or under fire; else the most valuable ally within 70 m under fire; else the nearest ally in melee |
| 17 | Slayer for Chaos | in melee | **self_last_stand** (exists: 10%, in melee or under fire) |
| 20 | The Blood Price | in melee | NEW **melee_healthy:** in melee, not wavering, above 50% health |
| 3 | Daemonshield | in melee | **unchanged** (your word) |
| 7, 13 | Terrorgheist Skull, Seductive Glory | | unchanged (your rulings) |
| 8, 9, 10, 22 | Primal Roar, Rage Embodied, Rage Incarnate, Toad Rage | | unchanged (keep) |

- **The squig set** (GENERATED `FOURTH.SQUIG_TEXT`, `tools\gen_squig_keys.py`): the 10 land units whose attribute group
  carries the game's "squig" attribute (Squig Herd, Squig Hoppers x2, Mangler Squigs, Colossal Squig x2, Durkit's
  Squigs, Explosive Squigs x2, the summoned herd). ASSUMPTION: the game's unit_is_not_squig rule reads this attribute.
- **Defaults:** every moved entry rode melee_unwavering (starts armed) and keeps that default (start_armed where the new
  family does not start armed). The Blood Price still starts on M (self-damage).
- **Counts:** 937 entries / 992 keys; 120 families (+9); melee_unwavering 280 -> 265.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,403 | 0 | `h176_run1.txt` |
| FULL, run 2 | 7,403 | 0, byte-identical | `h176_run2.txt` |
| RED, pre-177 snapshot | 7,401 | 0; RED 38/38 | `h176_red.txt` |

**Section 176 (both files), 18 worlds:**
- Blood Omens fires on a fast enemy 30 m away.
- Creature-Killer: silent against Swordsmen; fires against a Terrorgheist, and when an ally 15 m away fights one.
- Empowering Shrooms: casts on a squig ally in melee; silent with a Swordsmen ally.
- Everyone Has Their Price fires on an enemy in melee 15 m away.
- Fury of the Land fires on an ally charging 20 m away.
- Refuse to Die: silent at full health in melee; fires at 20%.
- Rune of Oath & Steel fires under missile fire.
- Shield of Aeons fires on a fast enemy 20 m away.
- Shielding Swarm casts on the more valuable of two allies under fire.
- Slayer for Chaos: silent at full health; fires at 8%.
- The Ostermark Runefang: silent against Swordsmen.
- The Blood Price: silent at 40%; fires at 90%.
- The cards of four families.
- **RED:** the round-176 build behaves the old way in all of them (it fires on plain melee, never otherwise).

## 4. Pins rebased (harness 176 vs 175)

| Pin | Old | New | Why |
|---|---|---|---|
| melee_unwavering (15 + 2 EXP) | 280 | 265 | 15 moved |
| plain start_armed lines (2) | 9 | 21 | 12 moved entries keep their default |
| ally_range_real fields (3) | 59 | 62 | Empowering Shrooms, Shielding Swarm x2 |
| h82 C-worlds and C8 | Creature-Killer | Banespear | a clean in-melee stand-in (Creature-Killer moved) |
| h83 S1 | Everyone Has Their Price, Fury of the Land | Drakwald Runefang, Dragon's Fang | stand-ins |
| h93 TIP mirror | - | + 9 labels | new families |

**Builder:** melee_unwavering 280 -> 265; start_armed 9 -> 21; ally_range_real 59 -> 62; melee_or_under_fire 4 -> 5;
the ROUND 177 gate regenerates the squig set and checks the 9 families, the 15 moves and Daemonshield.

## 5. Build, install, documents

- **Installed pack:** md5 **`9efbf06698578da06329293ecdaee9b5`**, 1,514,434 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 177 gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261118_round177.pack`; `archive\mod_source\round177\` (source
  md5 `d1eede4f0d3e79a4cac2618bce2f705f`).
- **Workbook:** `docs\WH3_abilities_master_v60_2026-11-18.xlsx` plus `.ods`; `XLSX v60 VERIFY OK` (15 moved rows,
  earlier notes kept; The Blood Price's stale round-167 note removed: its new family starts unarmed anyway).
- **Tracker:** 15 rows, section 10.55. **Database, audits, progress page:** regenerated.

## 6. Not done

- **Not seen in game.** The next battle starts from byte 822,669,876.
- Rows 23-134 of the score-3 review wait for your rulings.
