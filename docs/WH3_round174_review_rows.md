# Round 174: the score 1-2 review, rows 24-50 (sign-off round)

Date: 2026-11-18. Harness: `harness173.lua`. Release folder: `mod_source\releases\20261118_review_rows_harness173\`.

## 1. The rulings

- User, 2026-11-18: "You may implement items 24 to 50" (`docs\WH3_low_score_review_2026-11-17.md`). The doc was re-read
  from disk first: rows 24-50 carry the proposals as written (no RULED lines); row 23 and section 7 (the finishers) are
  RULED but were not in this instruction, so they are not built.
- Read F, the spellcaster class, ruled in a side session (2026-11-18): "Okay, then let's use the caster list."

## 2. What changed (what you will see in battle)

| Row | Ability | Before | Now |
|---|---|---|---|
| 24, 25 | Amber Bow, Gaze of Nagash | blob | **enemy_large_shot:** the most valuable large enemy, else the most armoured infantry |
| 26-29 | Hand of Gods, Shem's Burning Gaze, Goggly Glare, Vindictive Glare | blob | NEW **enemy_large_value_shot:** the most valuable large enemy, else the most valuable infantry per soldier (never the armour fallback) |
| 30, 31 | Don't Even Try It, Muster of Malevolents | enemy in melee or under fire | **enemy_single_drain:** the most valuable single-entity enemy in range |
| 32-34, 39 | Cube of Darkness, Scroll of Leeching, The Vortex Shard, The Black Tongue | enemy in melee or under fire | NEW **enemy_spellcaster:** the most valuable visible enemy spellcaster in range |
| 35, 36 | The Trickster's Pendant, Trickster's Shard | ground under an enemy in melee or under fire | NEW **enemy_ground_spellcasters:** the ground under the enemy spellcaster with the most other spellcasters within 24 m |
| 37, 38 | Silence the Prey, Power Siphon | enemy in melee or under fire | **enemy_commander_value:** the most valuable visible enemy Lord or Hero |
| 40 | Pageant of Shrikes | enemy in melee or under fire | NEW **enemy_missile_value:** the most valuable enemy missile unit that is shooting |
| 41 | Chalice of Dark Rain | ground under an enemy in melee or under fire | NEW **enemy_ground_shooters:** the ground under the shooting enemy with the most shooting value within 24 m |
| 42 | Transfix (`wh3_dlc29`) | an enemy Lord / Hero in melee | NEW **enemy_commander_wavering:** a wavering or routing enemy Lord or Hero, one in melee first, then the most valuable |
| 43 | The Hammer of Smednir | blob on a standing enemy | unchanged (your round-163 ruling) |
| 44 | Fury of Khaine | the nearest ally while the caster fights | NEW **ally_charge_melee:** the nearest charging ally, else one that just made contact; never a missile unit |
| 45 | Verminous Fury | the nearest ally while the caster fights | NEW **ally_wavering_melee:** the most valuable ally in melee and wavering; never a missile unit |
| 46 | Helping Hand | the caster in melee, the nearest Lord / Hero ally | NEW **ally_lord_melee:** the nearest Lord or Hero ally in melee, whether or not the caster fights |
| 47 | Inspired Marksmanship I-III | the closest missile ally, at once | NEW **ally_missile_shooting:** the most valuable missile ally that is shooting past its cast point |
| 48 | Overseer of the Unseen | the closest eligible ally, at once | NEW **ally_melee_risk:** the most valuable eligible ally in melee that wavers or is at or below 50% health |
| 49 | Whiplash! | the closest beast ally, at once | NEW **ally_beast_charge:** the nearest charging beast ally, else one that just made contact |
| 50 | Iron-Handed Captain | a broken ally, but routing allies were skipped (it likely never fired) | NEW **ally_routing:** the most valuable routing (or morale-broken) ally; routing allies are kept for this family only |

**New reads and rules:**
- **The spellcaster list** (GENERATED `FOURTH.SPELLCASTER_TEXT`, `tools\gen_spellcaster_keys.py`, 865 land units): a spell
  lore in the game's unit junction, or a campaign skill tree that grants a lore or a lore spell. Never the game's
  `is_caster` flag (it marks 27 non-casters).
- **Ally scores:** charging 2, fresh contact 1 (the closest wins a tie), or the live strategic value (the most valuable
  wins).
- **The cluster radius:** 24 m (70% of the 35 m spot of the Trickster items and the Chalice).
- **Defaults:** Helping Hand keeps its default (armed); Fury of Khaine and Verminous Fury still start on M (Rampage); every
  other moved entry started unarmed and still does.

**Counts:** 937 entries / 992 keys (unchanged); 111 families (+13 new; ally_overseer, ally_beast, ally_broken and
ally_missile now carry no entry).

## 3. A defect found and fixed during the round (be aware)

Six blob attacks left `enemy_blob`, so its three GENERATED tables had to be regenerated. My first regeneration script cut
each block at the text `FOURTH.load_X()`, which also appears in the function's own header line. The old body stayed
behind: **a Lua syntax error**. Every builder gate compares text, so the build passed and **that pack was installed for a
few minutes** (it would have failed to load in game). The full harness caught it (the files did not load).
- Repaired (`tools\round174_blob_repair.py`), the regeneration script fixed, and the pack rebuilt and reinstalled.
- **NEW permanent gate:** the builder now COMPILES the script (lupa) and refuses one that does not compile. Proven: it
  rejects exactly this error. The build command now needs `--with lupa`.

## 4. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,304 | 0 | `h173_run1.txt` |
| FULL, run 2 | 7,304 | 0, byte-identical | `h173_run2.txt` |
| RED, pre-174 snapshot | 7,288 | 0; RED 40/40 | `h173_red.txt` |

**Section 173 (both files), 22 worlds:** Amber Bow and Hand of Gods hit a Terrorgheist; Hand of Gods with no large enemy
picks the Swordsmen over the better-armoured Grave Guard; Don't Even Try It drains an idle Vampire; Cube of Darkness hits
the Fire Wizard over a more valuable Captain and stays silent with only a Captain; The Black Tongue at 120 m; the
Trickster's Pendant lands under the two clustered Wizards, not the lone valuable one; Silence the Prey hits the Captain;
Pageant of Shrikes picks the more valuable of two shooting units; the Chalice lands under the shooting pair; Transfix hits
the wavering Captain and stays silent with none wavering; Fury of Khaine skips a charging missile ally and prefers a
charging ally over a closer one in fresh contact; Verminous Fury picks the most valuable wavering melee ally (never the
missile one); Helping Hand fires on a Lord ally in melee while the caster idles; Inspired Marksmanship picks the more
valuable shooting ally and stays silent with an idle one; Overseer picks the hurt ally over the closer healthy one;
Whiplash stays silent with an idle beast; Iron-Handed Captain fires on a routing ally. Plus the cards and Helping Hand's
default. RED: the round-173 build misses every one of these targets.

## 5. Pins rebased (harness 173 vs 172)

| Pin | Old | New | Why |
|---|---|---|---|
| enemy_engaged_or_shot (5 + 1 EXP) | 46 | 37 | 9 left |
| enemy_ground_area (3) | 9 | 6 | 3 left |
| ally_melee_buff (2) | 14 | 11 | 3 left |
| enemy_melee (3) | 35 | 34 | Transfix |
| target_class fields (3) | 56 | 58 | Silence the Prey, Power Siphon |
| enemy_blob / large_shot / single_drain / commander_value | 77 / 5 / 10 / 3 | 71 / 7 / 12 / 5 | the moves |
| ally_overseer / beast / broken / missile | 1 / 1 / 1 / 3 | 0 | emptied |
| h93 TIP mirror | - | + 13 labels | new families |
| h97 FAM r500 (Trickster's Shard) | an orc block in melee | Arkhan (a spellcaster), visible, with a position | its new target |
| h99 CG1 / CG4 / RM1 / RM2 | idle allies | contact / melee at 40% / contact / wavering in melee | their new rules |
| h99 CG9 Inspired Marksmanship | fires on an idle missile ally | stays silent (the firing world is h173 IM1) | its new rule |
| boundaries h102-h118 (11 pins) | N | N - 2 | CG9 now makes one check per file instead of two |
| h122 E-worlds | 76 (Transfix included) | 66 | Transfix left enemy_melee (h173 TX1/TX2) |
| h131 O2 Overseer | idle ally | ally wavering in melee | its new rule |
| h149 0zr | `fireball=5;` | `fireball=5"` | Shem's Burning Gaze, the blast table's last row, left it |
| h165 SC2 Helping Hand card | "Fires in melee unless wavering, on the nearest ally in range; ..." | "Fires on the nearest ally in melee; Lord or Hero allies only" | its new family |

**Builder:** the same counts, the shot families 36 -> 53 keys; the ROUND 174 gate regenerates the spellcaster list and
checks the 13 families, the 27 moved entries, the class gate, the routing allowance and the cluster's 70% rule; the
COMPILE gate.

**Generated tables:** the SHOT table now covers the new shot-picker families (53 keys); the three blob tables were
regenerated (71 blob keys); RECHARGE, ANIM, USAGE, ATARGET and RISKY unchanged.

## 6. Build, install, documents

- **Installed pack:** md5 **`c012cfbddab5240cb080b712d5217c0c`**, 1,499,237 bytes; `IDENTICAL True`; `MATCHES SOURCE:
  True` four times; ROUND 123 to 174 gates and the COMPILE gate OK.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261118_round174.pack`; `archive\mod_source\round174\` (source md5
  `0cfb1efa474c20679e0c465dab493b9c`).
- **Workbook:** `docs\WH3_abilities_master_v57_2026-11-18.xlsx` plus `.ods`; `XLSX v57 VERIFY OK` (28 moved rows with
  their family and text, earlier notes kept; the trigger table 111 families; v1 to v56 byte-unchanged, 108 files).
- **Tracker:** 28 rows, section 10.52. **Database:** `DATABASE VERIFY OK`. **Audits:** wheel OK; trigger audit all 0 (the
  audit now knows the new shooting and morale families). **Progress page:** 992 automated, 76 decided, 55 open.

## 7. Not done

- **Not seen in game.**
- **Ruled but not built:** row 23 (Executioner) and section 7 (the finishers: Executioner, Skjalandir's Fall, the
  Emperor's Executioner). Waiting for your go-ahead.
- **ASSUMPTIONS:** Transfix's "half morale" is read as wavering or routing; a routing ally's morale counts as broken for
  Iron-Handed Captain.
