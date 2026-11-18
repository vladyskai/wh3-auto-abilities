# Round 180: the score-3 review, rows 87-114 and 128 (sign-off round)

Date: 2026-11-18. Harness: `harness179.lua`. Release folder: `mod_source\releases\20261118_score3_rows4_harness179\`.

## 1. The ruling

User, 2026-11-18: "Row 128 set A / Rows 57-86 do not touch / Rows 87-90 implement without melee / Row 91-96 implement as
in the doc / Row 98 improve / Rows 99-114 implement / 107 Mantra of Invigoration I like the option". Every row's current
text was printed from the file on disk first (rows 102, 103, 110, 111, 112, 114 carried new RULED text). Two readings
are mine and are stated here:
- **Rows 91-96 "as in the doc":** for the RULED rows the doc's only change is its Option, so the Options were built (the
  80% simulated reach), and row 92 (Heaven's Gate: "CLOSE IT") was closed.
- **Row 97** was not in the ruling and is untouched.

## 2. What changed (what you will see in battle)

| Row | Ability | Before | Now |
|---|---|---|---|
| 87-90 | Entangle, Get 'Em!, Hunter's Snare, Hunter's Trap | the ground under an enemy in melee or under fire, within 10 / 24 m | the ground under a fast enemy closing within 40 m of our units (the existing fast-enemy pick), within 70 m; no melee arm |
| 91, 93, 95, 96 | Sandstorm, Lamprey's Bite, The Burning Head x2, Arnzipal's Black Horror | the 95% simulated reach | the 80% simulated reach: Sandstorm 46 -> 41 m, Burning Head 109 -> 78 m, Arnzipal's 64 -> 44 m; Lamprey's Bite unchanged at 24 m (a straight path keeps its whole length) |
| 92, 100, 101 | Heaven's Gate, Snowflake Pendant, Stave of Avelorn | automated | CLOSED (cast by hand) |
| 99 | Shield of Thorns (2 keys) | charge or melee, on self | **melee_self_or_ally:** itself in melee, else the nearest ally in melee within 140 m |
| 104 | Blood Chalice of Bathori | itself at 75% | NEW **health_aura_ally_rule:** the most hurt Lord or Hero (itself included) at 75% or less within 42 m |
| 105 | Breath of Darkness (2 keys) | itself at 75% | the same rule: the most hurt UNDEAD unit within 140 m |
| 107 | Mantra of Invigoration | itself at 75% | the same rule: the most hurt TIGER WARRIOR unit within 70 m (your "I like the option") |
| 106 | Bugman's XXXXXX | itself at 75% (the game refuses it with an enemy near) | NEW **self_heal_clear:** at 75% or less AND no visible enemy within 38 m |
| 108, 110 | Potion of Charoi, Skar's Kraken-Killer | itself at 75% | NEW **self_hurt_attacked:** at 75% or less AND in melee or under missile fire |
| 111 | Foe-Seeker (3 keys) | tired | NEW **charge_or_tired:** charging, or tired or worse; no melee arm |
| 112 | Rock Bottom | out of ammunition | out of ammunition AND above 50% health (the refill costs 350 damage) |
| 114 | Eat da Runts! | itself at 75% (cast on itself), else the most HURT ally | itself at 75% or less, cast on the CHEAPEST HEALTHY ally (expendable first, then the lowest value per soldier); no self arm |
| 128 | Cold-Blooded | the nearest wavering ally | the nearest wavering LIZARDMEN ally (set A: the 133 '_lzd_' units) |
| 94, 97, 102, 103, 109, 113 | | | unchanged |

- **Defaults:** the 9 entries that left a family which starts armed keep their default (start_armed).
- **Counts:** 935 entries / 989 keys (3 closed); 133 families (+4).
- **New GENERATED sets** (`tools\gen_rule_sets.py`): lizard (133) and tiger (the game's 'tiger_warrior' attribute, 9);
  the game's ally target rules `unit_is_not_a_lizard_unit` (code Z) and `unit_is_not_tiger_warrior` (code T).

## 3. Found on the way

- **The 4 ground roots carried their AREA as their cast range** (Entangle 15 m, the others 35 m; the game's cast range
  is 100 m), so they only ever looked 10 / 24 m around the caster. Fixed with rows 87-90 (rule 3: target_intercept_range).
  A scan of every entry (`tools\scan_range_real.py`) finds 4 more mismatches, NOT touched: Curse of Khsar (the same slip,
  35 m vs 100 m; its row is in 57-86, which you said not to touch), Dispatch the Swarm x2 (30 m vs 100 m), Lord of
  Undeath (200 m vs 50 m).
- **Row 94:** the doc's option was "a smaller ring if the fanatics do not hit our units". The game data marks them as
  hitting our units, so the option does not apply: kept.

## 4. Row 98 (Land Mine): NOT BUILT

The doc's option was "half a packed block of enemies inside the blast". The game data gives Land Mine a 25 m blast, so
half a packed block is round(0.5 x pi x 25^2 / 2.368) = 415 soldiers: more than three full infantry units packed into
the blast. It would almost never fire. The option was written with 5-10 m blasts in mind; I missed the radius. Land Mine
keeps "in melee, none of our other units within 35 m". Options:
- **A. An enemy count inside the blast:** at least 60 enemy soldiers (about half a 120-man unit) inside the 25 m blast.
- **B. Two enemy units:** the blast touches at least two enemy units (so a charge does not go into one small fight).
- **C. Keep** as it is.

My recommendation: A. It keeps the doc's intent (no charge wasted on a small fight) with a number that a real melee
reaches.

## 5. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,622 | 0 | `h179_run1.txt` |
| FULL, run 2 | 7,622 | 0, byte-identical | `h179_run2.txt` |
| RED, pre-180 snapshot | 7,620 | 0; RED 42/42 | `h179_red.txt` |

**Section 179 (both files), 20 worlds and the cards:** Entangle casts on the ground under a fast enemy closing (pre-180:
none) and not on one only in melee; Get 'Em! casts at 50 m (beyond the old 24 m); Shield of Thorns casts on an ally in
melee while the caster idles; the rule heals pick the Captain, the skeletons and the Tiger Warriors over a more hurt
Swordsmen unit; Bugman's is silent with an enemy 20 m away and casts with it 60 m away; Potion of Charoi is silent while
idle and casts in melee; Skar's casts under missile fire; Foe-Seeker casts on a charge (pre-180: none); Rock Bottom is
silent at 40% and casts at 90%; Eat da Runts! picks the Skavenslaves, is silent with only a hurt ally and with a healthy
ally 75 m away; Cold-Blooded ignores a wavering Swordsmen unit and casts on wavering Saurus Warriors.

## 6. Pins rebased (harness 179 vs 178)

| Pin | Old | New | Why |
|---|---|---|---|
| entries / keys (every 938 / 992) | 938 / 992 | 935 / 989 | 3 closed |
| charge_or_melee (9 + 0h) | 37 | 36 | Shield of Thorns |
| enemy_fast_near_ally (2) | 15 | 19 | the 4 roots |
| enemy_ground_area (3) | 6 | 2 | the 4 roots |
| enemy_wander (3) | 43 | 42 | Heaven's Gate |
| melee_self_or_ally (1) | 2 | 3 | Shield of Thorns |
| tired (3) | 2 | 1 | Foe-Seeker |
| ushoran_health (5 + EXP) | 18 | 11 | 7 heals moved |
| when_ready (1) | 22 | 20 | 2 closed |
| range_real (2 + EXP) / ally_range_real (3) / start_armed (3) | 418 / 63 / 33 | 417 / 68 / 42 | closed / 5 new ranges / 9 defaults |
| the wind-up table (1) | 334 | 333 | Heaven's Gate |
| h92 P6 / P7 / P9, h95 E-range world | the old Eat da Runts rule | the new rule (P7 now proves the cast on the healthy ally; P9 still proves the drift skip) | row 114 |
| h97 the r15 ground family | Entangle | Amulet of Pha-Stah (100 m) | Entangle moved |
| h137 G1 | 1 cast | 0 | fast enemies only now (firing world RT1) |
| h162 WN3, h165 SC2 | Heaven's Gate | closed | row 92 |
| h104 0w | Foe-Seeker on tired | charge_or_tired | row 111 |
| h92 0p | `edr_ally = best_ally` | `edr_ally = best` | the rewrite |

**Builder:** the same counts; the AUTO327 list drops the 2 closed items (as round 173 did); the Eat da Runts reason; the
ROUND 180 gate.

## 7. Build, install, documents

- **Installed pack:** md5 **`6fbdf834e0a2e7cee83d529d7a3c3700`**, 1,543,625 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; the COMPILE gate and the ROUND 123 to 180 gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261118_round180.pack`; `archive\mod_source\round180\` (source
  md5 `5d25bf9e48d293e86b8635efe894ae15`).
- **Workbook:** `docs\WH3_abilities_master_v63_2026-11-18.xlsx` plus `.ods`; `XLSX v63 VERIFY OK` (16 rows, 3 closed, 5
  WW notes; v1-v62 byte-unchanged).
- **Tracker:** 27 rows, section 10.58. **Database, audits (0 candidates), progress page:** regenerated.

## 8. Not done

- **Not seen in game.** The next battle starts from byte 822,999,135.
- Row 98 (Land Mine): your pick of A / B / C. Row 28 (Surprise Squig): a new proposal. The last review's row 23 and its
  finishers section: not built.
