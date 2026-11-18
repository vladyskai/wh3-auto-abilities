# Round 172: rows 1, 3 and 5 of the review as RULED in the doc (sign-off round)

Date: 2026-11-18. Harness: `harness171.lua`. Release folder: `mod_source\releases\20261118_ruled_rows_harness171\`.

## 1. Why

Round 171 built the first proposals for rows 1, 3 and 5 of `docs\WH3_low_score_review_2026-11-17.md`. The doc already
carried the user's rulings (the "RULED 2026-11-17" lines); they were never read before building.
- User: "I feel like you ignored the current version of the WH_3_low_score_review."
- User: "Yes, fix them now."

## 2. What changed (what you will see in battle)

| Row | Ability | Round 171 (wrong) | Round 172 (the ruling) |
|---|---|---|---|
| 1 | Horn of the Wild Hunt | 3 units charging or just in contact; an army of 2 could never fire it | the same, **or every living unit when the army has fewer than 3** |
| 3 | Ursun's Roar (`wh3_main_character_abilities_ursuns_roar`) | the caster, or 2+ allies within 24 m, charging or just in contact | **ONE unit** (the caster or any unit within 24 m) charging, just in contact, **or wavering** |
| 5 | Waaagh! (`wh_main_character_abilities_waaagh`) | army charge only (as Horn) | NEW **army_charge_or_melee**: the army charge, **or 3 units in melee** (every living unit in a smaller army) |

- **The army count:** `FOURTH.army_moments()` counts the living units of ours, and how many are charging, in fresh
  contact or in melee. N = 3, or the number of living units when it is smaller.
  - A routing unit is living but never counts as charging or fighting. So an army of 3 with one unit routing needs
    all 3 and cannot fire. That follows the ruling's words ("every living unit"); say if you want routing units left
    out of the count instead.
- **The cards:**
  - Horn: "Fires when 3+ of your units charge at once (all of them in a smaller army)";
  - Waaagh!: "Fires when 3+ of your units charge or fight at once (all of them in a smaller army)";
  - Ursun's Roar: "Fires when it or a nearby ally charges or wavers".
- **Counts:** 939 entries / 994 keys unchanged; 102 trigger families (1 new).

**One wording gap left as it is (rows 6, 7):** the doc says "a fast enemy within 24 m **and closing**". The fast-enemy
read (`FOURTH.fast_enemy_near`, round 135) checks fast and moving, not the direction. The Rock of Inevitability and
The Wissenland Runefang use the same check. Not changed without a ruling.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,240 | 0 | `h171_run1.txt` |
| FULL, run 2 | 7,240 | 0, byte-identical | `h171_run2.txt` |
| RED, pre-172 snapshot | 7,238 | 0; RED 20/20 | `h171_red.txt` |

**Section 171 (both files):**
- **Horn:** AC4 an army of 2, both charging: ONE cast. AC5 an army of 2, one charging: no cast.
- **Waaagh!:** WA2 3 units in a melee older than 2 s: ONE cast. WA3 an army of 2 in an old melee: ONE cast. WA4 3
  units, 2 in an old melee: no cast.
- **Ursun's Roar:** UR3 one ally within 24 m charging: ONE cast. UR4 the caster wavering: ONE cast. UR5 an ally 15 m
  away wavering: ONE cast. UR6 an ally 40 m away wavering: no cast.
- **CA3:** the three cards.
- **RED:** the round-171 build fires none of AC4, WA2, WA3, UR3, UR4, UR5 (the in-game defect the user would have seen).

## 4. Pins rebased (harness 171 vs 170)

| Pin | Old | New | Why |
|---|---|---|---|
| h93 TIP mirror | army_charge / aura_charge round-171 labels | the round-172 labels + army_charge_or_melee | the rulings |
| h170 AC2 | the caster and 1 ally charging -> no cast | + a third, idle unit -> no cast | an army of 2 now fires (every living unit) |
| h170 CA2 | Horn and Ursun's Roar round-171 cards | the round-172 cards | the rulings |

**Builder:** no count moved. The ROUND 172 gate: Waaagh! on army_charge_or_melee, one entry per family, the
smaller-army fallback, Ursun's Roar reads wavering, the 2-ally rule and its card token gone, the three card sentences.

## 5. Build, install, documents

- **Installed pack:** md5 **`239b195b95d7734233d50a7ed1c75698`**, 1,447,876 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` for all four files; ROUND 123 to 172 gates OK.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261118_round172.pack`; `archive\mod_source\round172\`
  (source md5 `358662506dec1475f8a5b928ea04fd68`).
- **Workbook:** `docs\WH3_abilities_master_v55_2026-11-18.xlsx` plus `.ods`; `XLSX v55 VERIFY OK` (the three rows carry
  the ruled texts; v1 to v54 byte-unchanged, 104 files).
- **Tracker:** 3 inventory rows, section 10.50. **Database:** `DATABASE VERIFY OK`. **Audits:** wheel OK, trigger
  audit all 0. **Progress page:** 994 automated, 74 decided, 55 open.

## 6. Not done

- **Not seen in game.**
- **Ruled in the doc, not built (rows 23 onward, for the next session):** row 23 Executioner and section 7, the
  finishers (Executioner, Skjalandir's Fall, the Emperor's Executioner: the lowest health percentage first).
- **Waiting for rulings:** rows 16 (Rock Eye) and 18 (Null Stone); rows 24-50.
