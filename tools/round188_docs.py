#!/usr/bin/env python3
"""Round 188: the round document, the release notes, the open points (item 15 done; item 13 gains the line-of-sight
research), the tracker (section 10.66) and CLAUDE.md (rule 3 rewritten; build, harness, workbook lines)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
OPN = ROOT + r"docs\WH3_open_points.md"
TRK = ROOT + r"docs\WH3_ability_tracker.md"
CMD = ROOT + r"CLAUDE.md"
DOC = ROOT + r"docs\WH3_round188_rangerule.md"
REL = ROOT + r"mod_source\releases\20261121_rangerule_harness187\RELEASE_NOTES.md"
MD5 = "c478299540ea6704a364d16083145f57"
SIZE = "1,583,998"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


ROUND_DOC = """# Round 188: the range rule, max(70%, real - 20 m)

Date: 2026-11-21. Harness: `harness187.lua`. Release folder: `mod_source\\releases\\20261121_rangerule_harness187\\`.

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

**Rebases** (`tools\\make_harness187.py`): every pin that named an old bound names the new one; every edge world moved
its distance just past the new bound (71 -> 81 m, 150 -> 190 m, ...), so each keeps its meaning. **Section 187:** the
rule tokens; at load every bounded entry carries the new bound; Focused Shot fires at 229 m and stays silent at 231 m.
**Builder:** older gates that pinned a 70% value now pin the new one; the ROUND 188 gate checks every constant against
the rule.

## 4. Workbook and database

- `docs\\WH3_abilities_master_v70_2026-11-21.xlsx` (+ `.ods`): 359 trigger texts restate their bound (`make_xlsx_v70.py`,
  a deterministic rewrite); `verify_xlsx_v70.py` proves v70 = v69 + that rewrite cell by cell, v69 byte-unchanged.
- `docs\\WH3_ability_database_master.md` regenerated: only the bound column and the header changed
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
  Shot among them (checked in `gamedata\\wh3\\uieff\\unit_abilities_to_ui_effects_juncs.tsv`).
- **Other mods:** none found that checks it. Proactive Command (a WH3 auto-cast mod) gates on distance and hands the
  unit to the game's AI. A player report describes ranged units "running forward when their shots are obstructed",
  the same as Markus's walk. Patch-note pages about ranged units moving to a firing position could not be opened.
- **Not possible:** asking the engine for its own obstruction result; reading the kv rule
  `unit_firing_line_of_sight_considered_obstructed_ratio` (0.75) from a script.

## 6. Build, install

- **Installed pack:** md5 **`@MD5@`**, @SIZE@ bytes; `IDENTICAL True`; `MATCHES SOURCE: True` four times; the ROUND 123 to 188
  gates passed.
- **Archived:** `archive\\packs\\zz_test_deadly_onslaught_20261121_round188.pack`; `archive\\mod_source\\round188\\`
  (source md5 `9c189c7c04ffd2953a1b96c6e7caf32e`).
- **Not seen in game:** any cast at the new, longer distances.
""".replace("@MD5@", MD5).replace("@SIZE@", SIZE)
open(DOC, "w", encoding="utf-8", newline="\n").write(ROUND_DOC)
print("round doc")

open(REL, "w", encoding="utf-8", newline="\n").write("""# Round 188 release notes (2026-11-21)

The range rule: every cast-range bound is max(floor(real x 0.70), real - 20 m) (user ruling 2026-11-21, "C. Your rule,
the larger of 70% and real minus 20 m, everywhere."). Above a 66 m real range the mod now casts from further away
(100 m: 70 -> 80, 200 m: 140 -> 180, 250 m: 175 -> 230). Auras unchanged.

- Harness: `harness187.lua`, 7,876 checks / 0 failures twice (byte-identical); RED on `docs\\backups\\round188\\`.
- Builder: `build_and_install188.py` (`tools\\make_builder188.py`); log `build188_log.txt`.
- Installed pack md5 `@MD5@`, @SIZE@ bytes.
- Workbook v70; round document `docs\\WH3_round188_rangerule.md`.
""".replace("@MD5@", MD5).replace("@SIZE@", SIZE))
print("release notes")

o = open(OPN, encoding="utf-8").read()
o = sub(o, "| NEEDS A RULING | Options: A keep 70%; B 90% for single-entity targets (as the Executioner); C max(70%, real - 20 m) everywhere. |",
        "| DONE (round 188) | User 2026-11-21: \"C. Your rule, the larger of 70% and real minus 20 m, everywhere.\" Built: 21 "
        "cast constants and 3 named bounds (391 of 489 bounded entries reach further; Focused Shot 230 m, the Executioner "
        "230 m). Auras unchanged. Watch Accusation (52 -> 55 m): its old bound came from a field walk. |")
o = sub(o, " Options: A our-units-across-the-line geometry (no terrain); B only at the enemy the caster's own weapon is "
        "already shooting (covers terrain and our units; needs a missile weapon; Markus's bow reaches 180 m); C B where "
        "possible, else A (recommended). |",
        " RESEARCH 2026-11-21 (web, CA's script dump, other mods; docs\\WH3_round188_rangerule.md section 5): no script read "
        "answers 'can this unit hit that one'; CA's own scripts use is_visible_to_alliance() only; no mod checks it; "
        "bm:get_terrain_height(x, z) exists (unproven; bare heightmap assumed: no trees, buildings, units); the game's own "
        "data tags 56 keys 'Requires line of sight to the target', 35 of them ours (Focused Shot included): a data-driven "
        "set instead of the 61 flat shots. Options (updated): A our-units-across-the-line geometry on the 35 tagged keys; B "
        "only at the enemy the caster's own weapon is already shooting (current_target); C B where the caster has a "
        "missile weapon, else A; D C plus a terrain sightline from get_terrain_height samples every 2-3 m (needs a "
        "read-only probe first). Recommended: C, with a read-only terrain probe logged at each tagged cast so D can be "
        "decided on evidence. |")
open(OPN, "w", encoding="utf-8", newline="").write(o)
print("open points")

SECTION = """
### 10.66 Round 188 - the range rule, max(70%%, real - 20 m) (2026-11-21)

**Ruling (user, 2026-11-21):** "C. Your rule, the larger of 70%% and real minus 20 m, everywhere." Round document
`docs\\WH3_round188_rangerule.md`.

**Change:** every cast-range bound is `max(floor(real x 0.70), real - 20)` (`FOURTH.range_bound`,
`FOURTH.RANGE_MARGIN_M = 20`): 21 named constants and 3 hand-named bounds (Blood Sacrifice / Eat da Runts! 80,
Accusation 55); the Executioner 230 m (the larger of its 90%% and the rule). 391 of the 489 bounded entries reach further
(100 m: 70 -> 80; 250 m: 175 -> 230). Auras, blasts and the air drop unchanged. No roster change.

**Workbook v70:** 359 trigger texts restate their bound. **Database:** the bound column regenerated.

**Line of sight (open point 13):** researched; no script read exists; the game tags 35 of our keys "Requires line of
sight to the target"; a terrain-height read exists (unproven). The ruling is still the user's.

**Proof:** harness 187 full suite **7,876 checks / 0 failures**, twice byte-identical; RED on the pre-188 snapshot. Pack
md5 `@MD5@`.
""".replace("%%", "%").replace("@MD5@", MD5)
t = open(TRK, encoding="utf-8").read()
assert "### 10.66 " not in t
open(TRK, "w", encoding="utf-8", newline="\n").write(t.rstrip("\n") + "\n" + SECTION)
print("tracker: section 10.66")

c = open(CMD, encoding="utf-8").read()
for a, b in (
    ("3. **The 70% range rule.** Every trigger range constant is `floor(real_range * 0.70)`, where\n"
     "   the real range is `target_intercept_range` from the game's own tables (an aura's\n"
     "   `effect_range` gives the radius; 0 means self-only). No exceptions. It overruled a 25 m\n"
     "   value the user had field-tuned himself. Shipped as `FOURTH.RANGE_FRACTION = 0.70`; the\n"
     "   build asserts `constant == floor(real * 0.70)`. The single documented override is a metre\n",
     "3. **The range rule** (round 188, user ruling 2026-11-21: \"C. Your rule, the larger of 70% and real minus 20 m,\n"
     "   everywhere.\"). Every cast-range bound is `max(floor(real_range * 0.70), real_range - 20)`, where the real\n"
     "   range is `target_intercept_range` from the game's own tables. AURAS keep `floor(effect_range * 0.70)` (0 means\n"
     "   self-only); below 67 m the two rules agree. It overruled a 25 m value the user had field-tuned himself (the\n"
     "   70% era). Shipped as `FOURTH.RANGE_FRACTION = 0.70` + `FOURTH.RANGE_MARGIN_M = 20` (`FOURTH.range_bound`); the\n"
     "   build asserts every ENEMY_CAST / ALLY_CAST constant equals the rule. The single documented override is a metre\n"),
    ("   (`FOURTH.SINGLE_RANGE_FRACTION`, entry field `range_frac = 0.90`); the build refuses it on any other entry.\n",
     "   (`FOURTH.SINGLE_RANGE_FRACTION`, entry field `range_frac = 0.90`); the build refuses it on any other entry.\n"
     "   Since round 188 it takes the larger of its 90% and the rule (250 m: 230).\n"),
    ("- Installed build: md5 `816abe086cd75efbb8297bd237a8470e`, 1,582,433 bytes\n"
     "  (round 187, 2026-11-21: the badges follow the wheel at any resolution or UI scale).",
     "- Installed build: md5 `%s`, %s bytes\n"
     "  (round 188, 2026-11-21: the range rule, max(70%%, real - 20 m))." % (MD5, SIZE)),
    ("../mod_source/releases/20261121_uiscale_harness186/build_and_install187.py",
     "../mod_source/releases/20261121_rangerule_harness187/build_and_install188.py"),
    ("(harness186: 7,863 checks; it takes about 10 s)", "(harness187: 7,876 checks; it takes about 10 s)"),
    ("| `docs\\WH3_abilities_master_v69_2026-11-20.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v69.py`, verified by `tools\\verify_xlsx_v69.py`;",
     "| `docs\\WH3_abilities_master_v70_2026-11-21.xlsx` | the current master spreadsheet (versioned; newest wins); built by "
     "`tools\\make_xlsx_v70.py`, verified by `tools\\verify_xlsx_v70.py` (v70 = v69 + a deterministic bound rewrite);"),
    ("Wheel audit (workbook v69):", "Wheel audit (workbook v70):"),
    ("- ROUND 187 (2026-11-21): the badges follow the wheel",
     "- ROUND 188 (2026-11-21): THE RANGE RULE is max(70%, real - 20 m) (rule 3; open point 15 DONE). 391 of 489 bounded\n"
     "  entries reach further (Focused Shot 230 m, the Executioner 230 m, Accusation 55 m: its old 52 m came from a field\n"
     "  walk, watch it). Workbook v70 restates 359 trigger texts. LINE OF SIGHT researched (open point 13, waiting for\n"
     "  a ruling): no script read; the game's UI effect wh3_main_projectile_requires_line_of_sight tags 56 keys, 35 ours;\n"
     "  bm:get_terrain_height(x, z) exists (unproven). build_ability_database.py now reads a constant with a trailing\n"
     "  comment (round 188 dropped two). Next battle from byte 852,232,729.\n"
     "- ROUND 187 (2026-11-21): the badges follow the wheel"),
):
    c = sub(c, a, b)
open(CMD, "w", encoding="utf-8", newline="").write(c)
print("CLAUDE.md updated")
