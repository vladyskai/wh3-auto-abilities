# Round 183: the rule-shut review, rows 1-9 (sign-off round)

Date: 2026-11-20. Harness: `harness182.lua`. Release folder: `mod_source\releases\20261120_ruleshut1_harness182\`.

## 1. The rulings

User, 2026-11-20: "I'm reviewing. You may start implementing #1-9 for now." The rulings were read from the Claude Docs
review "Rule-shut abilities review" at rev 44 (the Ruling dropdowns and the comment threads), not from memory:

| # | Ability | Ruling in the doc | Family |
|---|---|---|---|
| 1 | Defiling Deluge | Recommended (B) | `enemy_melee_near` |
| 2 | Murderous Exhortations | Recommended (B) | `enemy_melee_near` |
| 3 | Rod of Corruption | Recommended (B) | `enemy_melee_near` |
| 4 | Wail of Malice | Recommended (B) | `enemy_melee_near` |
| 5 | Plaguereaper | B; thread: "the heal is considerable, we shouldn't waste it" | `melee_health75` |
| 6 | Reaper of Souls | Recommended, changed to C in the thread: "just in melee and less that 75% health" | `melee_health75` |
| 7 | Shard Blade | A | `melee_unwavering` |
| 8 | Web of Shadows | A | `melee_unwavering` |
| 9 | Warp-Quake | Other: "Melee_unwavering" | `melee_unwavering` |

## 2. What changed (what you will see in battle)

- **The finding behind the rows:** the 2026-10-09 "own-troop damage" rule was wrong. Every damage phase of these
  abilities targets enemies only (`phase_junc`).
- **Defiling Deluge, Murderous Exhortations, Rod of Corruption, Wail of Malice** fire when the caster is in melee, or
  when an enemy within 24 m (70% of their 35 m aura) is in melee.
- **Plaguereaper, Reaper of Souls** fire in melee at 75% health or less, so their self-heal is not wasted.
- **Shard Blade, Web of Shadows, Warp-Quake** fire in melee unless the caster is wavering.
- **Default arming (the families' own rule, unchanged):** `melee_health75` and `melee_unwavering` start armed (A), so
  rows 5-9 start armed; `enemy_melee_near` starts unarmed (M), so rows 1-4 need a click on their badge.
- **Charge holds:** the 6 abilities with more than one use wait for their recharge between casts (Defiling Deluge,
  Murderous Exhortations, Rod of Corruption, Plaguereaper, Shard Blade: 120 s; Wail of Malice: 90 s).
- **Counts:** 945 entries / 998 keys / 136 families (no new family, no new code).

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,721 | 0 | `h182_run1.txt` |
| FULL, run 2 | 7,721 | 0, byte-identical | `h182_run2.txt` |
| RED, pre-183 snapshot | 7,719 | 0; RED 16/16 | `h182_red.txt` |

**Section 182 (both files):** Defiling Deluge casts with an enemy in melee 15 m away and holds at 40 m; Plaguereaper
casts in melee at 60% health and holds at 90%; Reaper of Souls casts at 60% in melee; Warp-Quake and Web of Shadows cast
in melee; the cards read "Fires when it or a nearby enemy is in melee", "Fires in melee below 75% health", "Fires in
melee unless wavering". RED: the pre-183 source fires none of them.

## 4. Pins rebased (harness 182 vs 181)

| Pin | Old | New | Why |
|---|---|---|---|
| entry counts (93 places) | 936 | 945 | the 9 new entries |
| key counts (11 places) | 989 | 998 | one key each |
| `melee_unwavering` (17 places) | 265 | 268 | Shard Blade, Web of Shadows, Warp-Quake |
| `melee_health75` (4 places) | 2 | 4 | Plaguereaper, Reaper of Souls |
| the badge walk (A4a) | 1872 | 1890 | 2 x 945 |
| the charge-gate table (0zz) | 326 | 332 | 6 multi-use keys |

**Builder:** the same three count families (936 -> 945 in 22 gates, 989 -> 998, 265 -> 268), the `melee_health75` gate
2 -> 4, and the ROUND 183 gate (the 9 entries on their ruled families, the 35 m auras, the 6 holds).

## 5. Build, install, documents

- **Installed pack:** md5 **`bde9bc18a104768c685084b70d274fa7`**, 1,554,974 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 183 gates passed; the 9 row markers are in the installed pack.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261120_round183.pack`; `archive\mod_source\round183\` (source
  md5 `4740c222bf781611e184949976d65584`).
- **Workbook:** `docs\WH3_abilities_master_v66_2026-11-20.xlsx` plus `.ods`; `XLSX v66 VERIFY OK` (9 rows; v1-v65
  byte-unchanged). Corrected on the way: the Numbers sheet's row 16 and carrier table had stayed at 1,003 implemented
  since an earlier version; v66 re-derives them from the rows (998).
- **Tracker:** section 10.61. **Database** (DATABASE VERIFY OK), **audits** (0 candidates, wheel audit OK, 0 range
  mismatches), **progress page** (998 automated, 46 open): regenerated.

## 6. Not done

- **Not seen in game.** The next battle starts from byte 822,999,135. No battle has been read since round 175.
- Rows 10-64 of the review wait for your rulings.
