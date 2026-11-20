# Round 185: the rule-shut review, rows 20-64 (sign-off round)

Date: 2026-11-20. Harness: `harness184.lua`. Release folder: `mod_source\releases\20261120_ruleshut3_harness184\`.

## 1. The rulings

User, 2026-11-20: "Review ended, implement pls". Read from the Claude Docs review "Rule-shut abilities review" at rev 127
(the Ruling dropdowns and the threads: "set all as recomended" on rows 25-36, "rule as recommended" on rows 42-48 and
49-53):

| Rows | Ruling | Built as |
|---|---|---|
| 20-32 (13 safe blasts) | Recommended | `melee_unwavering` |
| 33-34 Glacial Blast, Thundermace | Recommended | `melee_clear` |
| 35 Cellular Instability | Recommended | `melee_clear_block` (60 soldiers in the 25 m blast) |
| 36 Splode da Big 'Un! | Recommended | `last_stand_clear` |
| 37-38 Battle Howl x2 | B | NEW `aura_charge_only` (55 m aura: 38 m) |
| 39 Twilight Horn II | B | `self_or_ally_charge` (140 m) |
| 40 Silver Horn of Vengeance | B | NEW `aura_charge_only` (35 m aura: 24 m) |
| 41 Swiftness of Itzl | Recommended | `charge_only` |
| 42-48 (stealth) | Recommended | CLOSED (keep shut) |
| 49-53 (mutual exclusivity) | Recommended | CLOSED (parked with the stances) |
| 54 Bonecrusher | Recommended | `enemy_blob_vortex`, not on flying targets |
| 55 Master Rune of Immolation | "Last stand" (option B) | `last_stand_clear` |
| 56 Beastlord's Gaze | Recommended | `ally_melee_risk` (140 m) |
| 57 Fog of the Damned | A | `enemy_ground_melee_cluster`, not on flying targets, ground cast |
| 58 Locus of Contagion | Recommended | `enemy_melee_near` (38 m) |
| 59 Mad Cap Mushrooms | Recommended | `self_recharging` |
| 60 Mirror of Knowledge | Recommended | `enemy_fast_near_ally`, unbounded, ground cast |
| 61 Offering to the Gods | Recommended | NEW `ally_offering` (30+ men) |
| 62-63 Seismic Snare x2 | Recommended | `slow_aura` (24 m) |
| 64 The Black Gem of Gnar | Recommended | `self_last_stand` |

Row 18 (Warpstorm Scroll, round 184) keeps its build: the rule-10 question has no answer in the doc yet.

## 2. What changed (what you will see in battle)

- **33 abilities fire automatically** on the triggers above.
- **Master Rune of Immolation:** its blast is a bombardment, not a vortex, so the radius table could not see it.
  `tools\gen_vortex_tables.py` now reads a self-centred bombardment too: 6 m shells + 4 m spread = 10 m, which hits our
  units. The war machine fires it at 10% health or less in melee, with none of our other units within 20 m. Your option
  text said 15%; the shared last-stand line is 10% (`LAST_STAND_PCT`, your Hag's Denial ruling), so it uses that.
- **Mirror of Knowledge:** the game gives it no range (-1), so the entry is `unbounded = true` (the precedent of The
  Tallyman's Blades Upgraded and Magma Storm): it fires on a fast enemy closing on our units anywhere on the map.
- **Fog of the Damned and Mirror of Knowledge** are ground-only abilities, so both joined `enemy_ground_keys` (the lesson
  of round 184's Raging Tornado).
- **Arming at battle start:** the family defaults hold. Cellular Instability and Splode da Big 'Un! hurt their own
  caster, so the round-167 rule keeps them unarmed (M) whatever the family says.
- **Counts:** 988 entries / 1,041 keys / 140 families (+2). The progress page now shows **0 open**: every in-wheel ability
  is either automated or decided by you.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,831 | 0 | `h184_run1.txt` |
| FULL, run 2 | 7,831 | 0, byte-identical | `h184_run2.txt` |
| RED, pre-185 snapshot | 7,829 | 0; RED 34/34 | `h184_red.txt` |

**Section 184 (both files), 16 worlds:** Venom Wave in melee; Glacial Blast holds with our Swordsmen 15 m away and casts
with none near; the Immolation rune casts at 8% and holds at 50%; Battle Howl casts for an ally charging 30 m away and
the Silver Horn holds for one at 30 m (beyond 24 m); Offering to the Gods takes the 120-man ally worth 600 over the
20-man one worth 900; Fog of the Damned skips a flying enemy worth 2,000 and lands under the pair in melee; Mirror of
Knowledge casts on the ground under a fast enemy 300 m away; the Black Gem at 8%; Locus of Contagion with an enemy in melee
30 m away; Twilight Horn II on a charging ally; Beastlord's Gaze on a wavering ally in melee; Seismic Snare in melee;
Swiftness of Itzl on the charge. The cards are pinned. RED: the pre-185 source fires none of them.

## 4. Pins rebased (harness 184 vs 183)

| Pin | Old | New | Why |
|---|---|---|---|
| entry counts (93 places) | 955 | 988 | 33 new entries |
| key counts (11 places) | 1008 | 1041 | one key each (C6's unit id 1008 kept) |
| `melee_unwavering` (17 places) | 268 | 281 | 13 safe blasts |
| the badge walk (A4a) | 1910 | 1976 | 2 x 988 |
| the charge gate / the cast gate | 339 / 336 | 346 / 353 | 7 multi-use keys, 17 wind-ups |
| `range_real` / `ally_range_real` / `target_class` | 428 / 68 / 55 | 430 / 71 / 57 | the new aimed / ally / class fields |
| `unbounded` entries | 2 | 3 | Mirror of Knowledge |
| `charge_only`, `self_recharging`, `enemy_fast_near_ally` | 4, 5, 19 | 5, 6, 20 | Itzl, Mad Cap, Mirror |
| `melee_clear`, `last_stand_clear`, `enemy_blob_vortex`, `melee_clear_block` | 4, 1, 1, 1 | 6, 3, 2, 2 | the new blasts |
| the TIP mirror | - | + 2 labels | the new families |

**Builder:** the same counts, the VORTEX gate 10 -> 16 rows, `enemy_ground_keys` 126 -> 128, the round-181 gate allows
`melee_clear_block` twice, and the ROUND 185 gate (it reads `tools\round185_rows.py`, so the gate and the source share one
list).

## 5. Build, install, documents

- **Installed pack:** md5 **`0779eb3ef6eaf41e929b86d890270e4e`**, 1,577,941 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 185 gates passed; the 33 row markers are in the installed pack.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261120_round185.pack`; `archive\mod_source\round185\` (source
  md5 `8a9e8aa0d78f406545beb7c53dab8327`).
- **Workbook:** `docs\WH3_abilities_master_v68_2026-11-20.xlsx` plus `.ods`; `XLSX v68 VERIFY OK` (33 built, 12 closed;
  v1-v67 byte-unchanged).
- **Tracker:** section 10.63. **Database** (DATABASE VERIFY OK), **audits** (0 candidates, wheel audit OK, 0 range
  mismatches, friendly-fire gate 0 violations), **progress page** (1,041 automated, 82 decided, 0 open).

## 6. Not done

- **Not seen in game.** Nothing since round 175 has been fought; the next battle starts from byte 822,999,135.
- **Warpstorm Scroll and rule 10** (round 184) still waits for your answer.
