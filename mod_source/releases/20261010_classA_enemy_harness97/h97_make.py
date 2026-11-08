# -*- coding: utf-8 -*-
"""HARNESS 97 build: assemble harness97.lua from the SHIPPED harness96.lua.

The round-97 job: THE REST OF CLASS A (enemy-targeted abilities). 97 of the 98
Class-A entries now fire at the ENEMY (88 unit form on enemy_engaged_or_shot,
9 enemy-GROUND on the new enemy_ground_area); each entry carries its own REAL
target_intercept_range -> ONE named 70% constant per real range. A NEW section
0u proves the state of the source and per-family worlds (12 real-range families)
prove INSIDE (fires at the enemy) / BEYOND (silent; the engine's own helper says
in-range - THE REGRESSION GUARD), plus missile / lapse / fresh-handle / self-cast
guards, and a red control.

Base: the shipped harness96.lua. Several earlier pins legitimately move with the
97 abilities (melee_unwavering 480 -> 383; enemy_engaged_or_shot 1 -> 89; a new
enemy_ground_area 9) and the marker-prefixed log tokens; those pins are RE-BASED
here (documented). One harness-91 world used a Class-A key (Whip of Agony) as its
melee_unwavering representative and is re-pointed at a still-melee_unwavering
ability.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
H96 = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261010_accusation_offer_harness96"
NL = chr(10)


def read(p): return io.open(p, encoding="utf-8", newline="").read()
def write(p, s): io.open(p, "w", encoding="utf-8", newline="").write(s)
def L(*ls): return NL.join(ls)

src = read(H96 + "/harness96.lua")


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# --------------------------------------------------------------------------
# 1. env pair H96 -> H97
# --------------------------------------------------------------------------
sub(L('-- HARNESS 96 (this round): the env pair is now H96_LIVE / H96_ANN.',
      'local LIVE = os.getenv("H96_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H96_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H96_LIVE") ~= nil) or (os.getenv("H96_ANN") ~= nil)'),
    L('-- HARNESS 97 (this round): the env pair is now H97_LIVE / H97_ANN.',
      'local LIVE = os.getenv("H97_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H97_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H97_LIVE") ~= nil) or (os.getenv("H97_ANN") ~= nil)'),
    "env pair")

# --------------------------------------------------------------------------
# 2. the red-mode banner
# --------------------------------------------------------------------------
sub('  print("   *** boundary-count pin is re-based to the N/A form here).***")',
    L('  print("   *** boundary-count pin is re-based to the N/A form here).***")',
      '  print("   *** THE REST OF CLASS A (harness 97): additionally every section-0u token, and every")',
      '  print("   *** INSIDE/missile/ground world (the 97 abilities are still melee_unwavering self-cast on")',
      '  print("   *** the snapshot, so nothing is fired at an enemy), fail; the BEYOND worlds pass by design.***")'),
    "banner")

# --------------------------------------------------------------------------
# 3. RE-BASE the trigger-count pins (melee_unwavering 480 -> 383)
# --------------------------------------------------------------------------
sub("'trigger = \"melee_unwavering\"') == 480", "'trigger = \"melee_unwavering\"') == 383",
    "mu count pins", count=6)
sub("      mu == 480)", "      mu == 383)", "mu var pin", count=1)
# the 0r moved-counts check gains the two enemy triggers
sub("cp(s, 'trigger = \"melee_unwavering\"') == 383 and cp(s, 'trigger = \"enemy_engaged_or_shot\"') == 1)",
    "cp(s, 'trigger = \"melee_unwavering\"') == 383 and cp(s, 'trigger = \"enemy_engaged_or_shot\"') == 89"
    " and cp(s, 'trigger = \"enemy_ground_area\"') == 9)",
    "0r moved counts")

# --------------------------------------------------------------------------
# 4. RE-BASE the 0r live source-token check (the log lines are marker-prefixed)
# --------------------------------------------------------------------------
sub(L('    raw_find(live_src94, "accusation target: \'", 1, true) ~= nil',
      '    and raw_find(live_src94, "accusation pre-cast re-check:", 1, true) ~= nil',
      '    and raw_find(live_src94, "accusation SKIPPED: the chosen enemy lapsed before the cast", 1, true) ~= nil)'),
    L('    raw_find(live_src94, "\\" target: \'", 1, true) ~= nil',
      '    and raw_find(live_src94, "\\" pre-cast re-check:", 1, true) ~= nil',
      '    and raw_find(live_src94, "\\" SKIPPED: the chosen enemy lapsed before the cast", 1, true) ~= nil)'),
    "0r live tokens")

# --------------------------------------------------------------------------
# 5. RE-BASE the 0t log tokens (the bound is now the per-ability local)
# --------------------------------------------------------------------------
sub('\'.. "m bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")\'',
    '\'.. "m bound=" .. tostring(bound) .. "m")\'',
    "0t choice-log token")
sub('\'.. " bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m) - cast not spent")\'',
    '\'.. " bound=" .. tostring(eg_bound_now) .. "m) - cast not spent")\'',
    "0t recheck-log token")

# --------------------------------------------------------------------------
# 6. the harness-93 tooltip wording map gains enemy_ground_area
# --------------------------------------------------------------------------
sub(L('    enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire",',
      "  }"),
    L('    enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire",',
      '    enemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",',
      "  }"),
    "h93 TIP map")

# --------------------------------------------------------------------------
# 7. the harness-91 O1/O2 world: re-point off the moved Whip of Agony key
# --------------------------------------------------------------------------
sub('  local M_MU1  = "wh2_twa03_weapon_abilities_whip_of_agony"',
    '  local M_MU1  = "wh_main_item_abilities_black_periapt"',
    "h91 M_MU1 key")
sub('"whip_of_agony", "O1"', '"black_periapt", "O1"', "h91 O1 marker")
sub('"whip_of_agony", "O2"', '"black_periapt", "O2"', "h91 O2 marker")

# --------------------------------------------------------------------------
# 8. append the new HARNESS-97 section after run_h96()
# --------------------------------------------------------------------------
section = read(HERE + "/h97_section.lua").lstrip(NL)
sub(NL + "run_h96()" + NL, NL + "run_h96()" + NL + NL + section + NL, "append section")

# --------------------------------------------------------------------------
# 9. extend the tail token list
# --------------------------------------------------------------------------
sub("92, 93, 94 AND 95's worlds included", "92, 93, 94, 95 AND 96's worlds included", "tail list")

write(HERE + "/harness97.lua", src)
print("wrote harness97.lua", len(src), "bytes")
