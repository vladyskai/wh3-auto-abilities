# Round 179: the score-3 review, rows 115-134 (sign-off round)

Date: 2026-11-18. Harness: `harness178.lua`. Release folder: `mod_source\releases\20261118_score3_rows3_harness178\`.

## 1. The ruling

User, 2026-11-18: "Items 115-134 approved" (`docs\WH3_score3_review_2026-11-18.md`). Every row's CURRENT text was
printed from the file on disk before any code (the round-178 lesson). The rows' own rulings:

- Row 126 Horn of Vaul: "RULED, KEEP ... 'no need of at least 3'". Row 132 Hunter's Call: KEEP (no minimum count).
- Row 129 Star of Avelorn: the hurt unit of ours, "the caster included".
- Row 133 Grut's Sickle: "on expendable ally first (highest hp), then on the ally with lowest value above 75%".
- Rows 125, 128, 134: your earlier rulings (row 128 adds a Lizardmen-only restriction, see section 6).

## 2. What changed (what you will see in battle)

| Row | Ability | Before | Now |
|---|---|---|---|
| 115-117 | Inspired Assault I-III | the caster in melee, the closest ally | NEW **ally_charge_or_melee:** the nearest ally within 70 m charging, else just in contact, else in melee; never a missile unit; the caster need not fight |
| 118-121 | Inspired Defence I-III, Da Boss 'as a Plan! | the caster in melee, the closest ally | NEW **ally_melee_wavering_first:** the nearest ally in melee (70 m / 105 m), a wavering one first |
| 122 | Favour of the Fay | the caster in melee, the closest ally | **melee_self_or_ally** (exists): the caster in melee (on itself), else the nearest ally in melee |
| 123 | Orcs are da Best! | the caster in melee, the closest ally | NEW **ally_value_melee:** the most valuable ally in melee within 105 m, never a missile unit |
| 124 | Hellish Vigour | the caster in melee, the closest ally | NEW **ally_in_melee:** the nearest ally in melee within 52 m |
| 127 | Berry Wine | the lowest unit at 75% | NEW **health_aura_ally_deep:** the lowest unit at or below 55% |
| 129 | Star of Avelorn | a hurt unit within 10 m of the caster | NEW **heal_ground_best:** the ground under the hurt unit of ours (75% or less, the caster included) within 140 m with the most other hurt units within 10 m of it |
| 130, 131 | Commanding Presence, Fury of Ulric | the caster wavering, or an ally IN MELEE wavering | the caster wavering, or an ally within 24 m wavering, in melee or not (your ruling) |
| 133 | Grut's Sickle | when ready, the ally with the most hit points | only when the winds pool is below 30 with reserve 20+; an EXPENDABLE ally first (the most hit points), else the cheapest ally above 75% health |
| 125, 126, 132, 134 | | | unchanged (your rulings) |
| 128 | Cold-Blooded | | trigger unchanged (your ruling); the Lizardmen-only restriction is NOT built yet (section 6) |

- **Defaults:** the 12 moved entries came from families that start armed; each keeps its default (start_armed).
- **Counts:** 938 entries / 992 keys; 129 families (+6); ally_melee_buff 11 -> 1 (Daemonic Whispers).

## 3. A bug found on the way (in the new code, before it shipped)

The shared heal re-check (the last test before a heal cast) tested the chosen ally against the AREA radius. Star of
Avelorn's area is 10 m, so the new ground pick could never cast past 10 m. Berry Wine's re-check also still used 75%.
Both now have their own re-check rule (`ah_mode` "spot": the 140 m cast bound; "deep": 55%). The old harness world S3
(a hurt ally 12 m away) caught it: it stayed silent where the new rule says cast.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,537 | 0 | `h178_run1.txt` |
| FULL, run 2 | 7,537 | 0, byte-identical | `h178_run2.txt` |
| RED, pre-179 snapshot | 7,535 | 0; RED 32/32 | `h178_red.txt` |

**Section 178 (both files), 15 worlds and the cards:**
- Inspired Assault I casts on an ally in melee while the caster stands idle (pre-179: none); never on a Handgunner ally.
- Inspired Defence I takes the wavering ally in melee at 40 m over a steady one at 15 m.
- Orcs are da Best! takes the ally worth 900 over the one worth 300.
- Hellish Vigour casts on an ally in melee, not on one standing idle; Favour of the Fay casts on an ally in melee.
- Berry Wine: silent at 65% (pre-179: it cast), casts at 50%.
- Star of Avelorn: casts under a hurt ally 60 m away (pre-179: none); between a lone hurt ally and two hurt allies 5 m
  apart, it lands under the pair.
- Commanding Presence casts for a wavering ally that is not in melee (pre-179: none).
- Grut's Sickle: silent while the winds are not low (pre-179: it cast); with low winds it takes Skavenslaves over
  Swordsmen with more hit points, and with no expendable unit the cheapest ally above 75%.
- The cards: "Fires on an ally charging, else just in contact, else in melee; no missile units", "Fires on the nearest
  ally in melee, a wavering one first", "Fires on the most valuable ally in melee; no missile units", "Fires on the
  nearest ally in melee", "Fires on the most hurt unit nearby, below 55% health", "Fires under the hurt unit with the most
  hurt units around it", "Fires when the winds run low, on an expendable ally, else the cheapest healthy one".

## 5. Pins rebased (harness 178 vs 177)

| Pin | Old | New | Why |
|---|---|---|---|
| ally_melee_buff (2) | 11 | 1 | 10 moved |
| health_aura_ally (5) / health_aura_ground (5) | 9 / 3 | 8 / 2 | Berry Wine, Star of Avelorn moved |
| melee_self_or_ally (1) | 1 | 2 | Favour of the Fay |
| ally_range_real (3) | 62 | 63 | Star of Avelorn's 200 m cast range |
| plain start_armed lines (2) | 21 | 33 | the 12 moved entries keep their default |
| h98 AB-U worlds, AB-L2 | Da Boss (105 m) | Daemonic Whispers (140 m; AB-U3 at 160 m) | the family's last entry stands in |
| h99 GS1, GS2 | cast on the most hit points | silent | no winds read in those worlds; low winds needed (firing worlds GR2, GR3) |
| h104 S1c, S1d, S3, S4c, S11 | the 10 m reach and its log texts | the 140 m cast bound, the spot log texts; S3 casts; S11 drifts to 150 m | the new ground pick |
| suite boundaries after h99 (11) | | -4 each | GS1/GS2 have 1 check each instead of 2, in both files |
| h93 TIP mirror | - | + 6 labels; Grut's label | new families |

**Builder:** the same counts; the ROUND 179 gate checks the 6 families, the moves with their defaults, the 5 ranked
modes, the spot/deep re-checks, the wavering pair and Grut's winds gate.

## 6. Row 128: the Lizardmen set needs your look

Cold-Blooded's own game rule is `unit_is_not_a_lizard_unit`. The game data has no "lizard" attribute, so I cannot read
the engine's set directly. Two candidates:
- **A. The key prefix `lzd`:** 133 land units, every Lizardmen unit including Carnosaurs, Salamanders and Razordons.
- **B. The Lizardmen voice culture:** 107 units; it leaves out the beasts that have their own voices (Carnosaurs,
  Salamanders ...).

My recommendation is A: the game already refuses an invalid target. A wider set only means the mod may try a cast the
game refuses, never a wasted one; a narrower set would skip valid targets. Until you pick, Cold-Blooded keeps its
current trigger.

## 7. Build, install, documents

- **Installed pack:** md5 **`d7588fbfd32a951c9c65b4b1b052c284`**, 1,531,016 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 179 gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261118_round179.pack`; `archive\mod_source\round179\` (source
  md5 `8eb56431b4994f2326872f959b68da91`).
- **Workbook:** `docs\WH3_abilities_master_v62_2026-11-18.xlsx` plus `.ods`; `XLSX v62 VERIFY OK` (15 rows, earlier notes
  kept; v1-v61 byte-unchanged).
- **Tracker:** 15 rows, section 10.57. **Database, audits (the new families added to the audit's sets; 0 candidates),
  progress page:** regenerated.

## 8. Not done

- **Not seen in game.** The next battle starts from byte 822,999,135.
- Rows 57-114 of the score-3 review wait for your rulings (row 92 already says "CLOSE IT": Heaven's Gate). Row 28
  (Surprise Squig) needs a new proposal. Row 23 of the last review and its finishers section are not built.
