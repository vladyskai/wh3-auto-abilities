# Round 184: the rule-shut review, rows 10-19 (sign-off round)

Date: 2026-11-20. Harness: `harness183.lua`. Release folder: `mod_source\releases\20261120_ruleshut2_harness183\`.

## 1. The rulings

User, 2026-11-20: "Up to #19 ruled". Read from the Claude Docs review "Rule-shut abilities review" at rev 83 (the Ruling
dropdowns and the comment threads):

| # | Ability | Ruling in the doc | Built as |
|---|---|---|---|
| 10-12 | Flock of Doom x3 | Recommended = A2 (the enemy need not stand still) | `enemy_area_drain` |
| 13 | Sword of Daith | Recommended (A) | `enemy_area_drain` |
| 14 | Zefet-nebtar | Recommended (A); thread: "if not damage, then no need for clearance check" | `enemy_area_drain` |
| 15 | Ring of Corin | Recommended (A) | `enemy_single_drain` |
| 16 | Soul Stealer (RoR) | B "with the 75% gate" | NEW `enemy_area_drain_hurt` |
| 17 | Soul Stealer (Druchii Anointed) | "same as #16" | NEW `enemy_area_drain_hurt` |
| 18 | Warpstorm Scroll | Recommended (A) | `enemy_single_drain`, `target_class = "flying"` |
| 19 | Raging Tornado | Recommended (A) | NEW `enemy_ground_melee_cluster` |

## 2. What changed (what you will see in battle)

- **Flock of Doom, Sword of Daith, Zefet-nebtar** fire on the visible enemy infantry block within 70 m with the most
  value per soldier and enough soldiers for every strike. The enemy may be moving. Our units near the target do not
  stop Zefet-nebtar (its knockback pushes them but does no damage).
- **A correction about A2:** a reply in the doc's Flock of Doom thread said `enemy_area_drain` requires the enemy to
  stand still. It never did: its standing-still gate is the CASTER's, and only for a cast with an animation (round 168).
  So A2 is the shipped rule, unchanged. Also, row 10's effect line in the doc missed the Runecaller key's 1 s wind-up;
  the other two keys have none.
- **Ring of Corin** fires on the most valuable enemy Lord, Hero or monster within 140 m; **Warpstorm Scroll** on the most
  valuable flying one within 70 m (the game refuses ground units).
- **Soul Stealer x2** fire on the area-drain pick only while the caster is at 75% health or less (`FOURTH.DRAIN_HURT_PCT`).
- **Raging Tornado** is placed on the ground under the enemy in melee with the most enemy value fighting within 24 m of
  it, the Hurricanum standing still for its 5 s cast. Its key joined `enemy_ground_keys` (the game accepts a ground cast
  only): the harness world RT1 caught a unit-form cast before that fix.
- **Moving casters:** Ring of Corin, Warpstorm Scroll and Sword of Daith have no cast animation, so they may fire while
  their caster moves (your round-168 ruling); the other seven wait for a standing caster.
- **Arming at battle start:** the drain families start unarmed (M), as they did before.
- **Counts:** 955 entries / 1,008 keys / 138 families (+2). The SHOT table covers 70 keys, the AREA table 18.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,762 | 0 | `h183_run1.txt` |
| FULL, run 2 | 7,762 | 0, byte-identical | `h183_run2.txt` |
| RED, pre-184 snapshot | 7,760 | 0; RED 20/20 | `h183_red.txt` |

**Section 183 (both files):** Flock of Doom casts at a MOVING block; Sword of Daith and Zefet-nebtar cast (Zefet with our
Swordsmen next to the target); Ring of Corin reaches a hero 130 m away; Soul Stealer casts at 60% health and holds at
90%; Warpstorm Scroll takes the flying hero worth 300 over the ground hero worth 900; Raging Tornado is placed under the
pair in melee (worth 1,000 together) rather than the lone one worth 900, and holds with no enemy in melee. RED: the
pre-184 source fires none of them.

## 4. Pins rebased (harness 183 vs 182)

| Pin | Old | New | Why |
|---|---|---|---|
| entry counts (93 places) | 945 | 955 | 10 new entries |
| key counts (11 places) | 998 | 1008 | one key each |
| the badge walk (A4a) | 1890 | 1910 | 2 x 955 |
| the charge-gate table (0zz) | 332 | 339 | 7 multi-use keys |
| the cast-gate table (0a) | 333 | 336 | 3 wind-up keys |
| `range_real` fields (3 places) | 418 | 428 | every new entry is aimed |
| `target_class` fields (3 places) | 54 | 55 | Warpstorm Scroll |
| `enemy_single_drain` (2 places) | 12 | 14 | Ring of Corin, Warpstorm Scroll |
| `enemy_area_drain` | 8 | 13 | Flock of Doom x3, Sword of Daith, Zefet-nebtar |
| the TIP mirror | - | + 2 labels | the new families |

**Builder:** the same counts, the SHOT key gates 61 -> 70, the AREA gate 11 -> 18 (its regex gained the new family),
`enemy_ground_keys` 125 -> 126, and the ROUND 184 gate.

## 5. Build, install, documents

- **Installed pack:** md5 **`18aac090ab99114b1ac3c83eb483dd8c`**, 1,562,718 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 184 gates passed; the 10 row markers are in the installed pack.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261120_round184.pack`; `archive\mod_source\round184\` (source
  md5 `bbce4440c06830cd4bf598766f744515`).
- **Workbook:** `docs\WH3_abilities_master_v67_2026-11-20.xlsx` plus `.ods`; `XLSX v67 VERIFY OK` (10 rows; v1-v66
  byte-unchanged; the 3 non-animated rows carry the round-168 'may fire while moving' note).
- **Tracker:** section 10.62. **Database** (DATABASE VERIFY OK), **audits** (0 candidates; the audit now knows
  `enemy_ground_melee_cluster` as a melee trigger), **progress page** (1,008 automated, 36 open): regenerated.

## 6. Not done, and one question

- **Warpstorm Scroll and rule 10:** its x0.55 slow now fires on a flying enemy with no melee or charge condition. My
  proposal did not flag this; it is recorded as your ruling (audit R4, ruled) and put to you.
- **Not seen in game.** The next battle starts from byte 822,999,135.
- Rows 20-64 of the review wait for your rulings.
