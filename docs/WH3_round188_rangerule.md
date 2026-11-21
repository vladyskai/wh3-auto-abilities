# Round 188: the range rule, max(70%, real - 20 m)

Date: 2026-11-21. Harness: `harness187.lua`. Release folder: `mod_source\releases\20261121_rangerule_harness187\`.

## 1. The ruling

User, 2026-11-21: "the 70% that we have is actually too much for large instances ... maybe just the range minus 20
meters". Options given (open point 15): A keep 70%; B 90% for single-entity targets; C the larger of 70% and real - 20 m
everywhere. Ruling: "C. Your rule, the larger of 70% and real minus 20 m, everywhere." / "This one, thanks".

## 2. What changed (what you will see)

Every cast-range bound is now `max(floor(real x 0.70), real - 20)` (`FOURTH.range_bound`, `FOURTH.RANGE_MARGIN_M =
20`). Below 67 m nothing changes (70% is the larger there); above it, abilities fire from further away:

| Real range | Old bound | New bound |
|---:|---:|---:|
| 70 m | 49 | 50 |
| 75 m | 52 | 55 |
| 80 m | 56 | 60 |
| 90 m | 63 | 70 |
| 100 m | 70 | 80 |
| 120 m | 84 | 100 |
| 130 m | 91 | 110 |
| 150 m | 105 | 130 |
| 180 m | 126 | 160 |
| 200 m | 140 | 180 |
| 250 m | 175 | 230 |
| 300 m | 210 | 280 |
| 350 m | 245 | 330 |
| 400 m | 280 | 380 |
| 500 m | 350 | 480 |
| 600 m | 420 | 580 |

- 21 named constants (16 enemy, 5 ally) and 3 hand-named bounds: Blood Sacrifice and Eat da Runts! 70 -> 80, Accusation
  52 -> 55. 391 of the 489 bounded entries now fire from further away; Focused Shot 175 -> 230 m.
- **The Executioner** keeps its 90% exception but takes the larger value: 225 -> 230 m.
- **Unchanged:** the auras (`aura_m` stays 70%: 15, 35, 55 m reaches), the 24 / 38 m named constants, the blast and
  dive reaches, the cluster and mist areas, the air drop's own test constant.
- **Watch:** Accusation's 52 m was set in round 96 after an observed walk at 81.3 m; 55 m is still well inside that,
  but it is the one bound that came from a field report.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness186 on the new source (the old pins) | 7,863 | 83 (every one a changed bound) | scratch |
| FULL, run 1 | 7,876 | 0 | `h187_run1.txt` |
| FULL, run 2 | 7,876 | 0, byte-identical | `h187_run2.txt` |
| RED, pre-188 snapshot | 7,876 | 0; the section sees 21 constants and 391 of 489 entries on 70%, Focused Shot silent at 229 m | `h187_red.txt` |

**Rebases** (`tools\make_harness187.py`): every pin that named an old bound names the new one; every edge world moved
its distance just past the new bound (71 -> 81 m, 150 -> 190 m, ...), so each keeps its meaning. **Section 187:** the
rule tokens; at load every bounded entry carries the new bound; Focused Shot fires at 229 m and stays silent at 231 m.
**Builder:** older gates that pinned a 70% value now pin the new one; the ROUND 188 gate checks every constant against
the rule.

## 4. Workbook and database

- `docs\WH3_abilities_master_v70_2026-11-21.xlsx` (+ `.ods`): 359 trigger texts restate their bound (`make_xlsx_v70.py`,
  a deterministic rewrite); `verify_xlsx_v70.py` proves v70 = v69 + that rewrite cell by cell, v69 byte-unchanged.
- `docs\WH3_ability_database_master.md` regenerated: only the bound column and the header changed
  (`build_ability_database.py` now prints the new rule and reads a constant with a trailing comment).

## 5. The line-of-sight research (open point 13, for the Focused Shot walks)

Asked 2026-11-21: "check online if some other mods detect somehow if the shot is blocked or not. Or maybe the AI
scripts have some way of doing it."

- **No battle script read answers "can this unit hit that one".** The full battle_unit list (110 functions), the
  unit controller, the AI planner and `battle` were checked (chadvandy's WH3 modding docs). CA's own scripts (the WH3
  script dump) decide between attacking and moving with `is_visible_to_alliance()` alone; no sight, raycast or
  obstruction call exists in them.
- **`battle:is_area_clear(...)`** answers about walking (pathfinding), not sight.
- **`bm:get_terrain_height(x, z)`** exists (CA uses it to put markers on the ground). Sampling it along the caster-target
  line could estimate a hill in the way. ASSUMPTION: it is the bare heightmap (no trees, buildings or units). Unproven
  in our battles.
- **The game's own data tags line-of-sight abilities:** the UI effect "Requires line of sight to the target"
  (`wh3_main_projectile_requires_line_of_sight`) sits on 56 ability keys; 35 of them are automated by the mod, Focused
  Shot among them (checked in `gamedata\wh3\uieff\unit_abilities_to_ui_effects_juncs.tsv`).
- **Other mods:** none found that checks it. Proactive Command (a WH3 auto-cast mod) gates on distance and hands the
  unit to the game's AI. A player report describes ranged units "running forward when their shots are obstructed",
  the same as Markus's walk. Patch-note pages about ranged units moving to a firing position could not be opened.
- **Not possible:** asking the engine for its own obstruction result; reading the kv rule
  `unit_firing_line_of_sight_considered_obstructed_ratio` (0.75) from a script.

## 6. Build, install

- **Installed pack:** md5 **`c478299540ea6704a364d16083145f57`**, 1,583,998 bytes; `IDENTICAL True`; `MATCHES SOURCE: True` four times; the ROUND 123 to 188
  gates passed.
- **Archived:** `archive\packs\zz_test_deadly_onslaught_20261121_round188.pack`; `archive\mod_source\round188\`
  (source md5 `9c189c7c04ffd2953a1b96c6e7caf32e`).
- **Not seen in game:** any cast at the new, longer distances.
