# -*- coding: utf-8 -*-
"""HARNESS 99 build: assemble harness99.lua from the SHIPPED harness98.lua.

Round-99 job: the 15 audit rows tagged NEEDS A RULING (the 10 target-class-gated
Class-B entries, the 2 Rampage entries, Merciw's Monstrous Regiment, and the two
mid-flight entries Daemonic Whispers + Grut's Sickle) are now ally-targeted.
The round moves melee_unwavering 373 -> 363, charge_or_melee 26 -> 25,
ushoran_health 38 -> 34; ally_melee_buff 11 -> 14; adds the ten new ally triggers
(overseer 1 / beast 1 / broken 1 / missile 3 / warmachine_heal 1 / hellforged_heal
1 / monster_heal 1 / construct_heal 1 / infinite_buff 1 / winds 1) and grows
ally_range_real 18 -> 32. The harness-97/98 pins that read those counts are
RE-BASED here (documented). A new section 0w + the world set are appended.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)

def read(p): return io.open(p, encoding="utf-8", newline="").read()
def write(p, s): io.open(p, "w", encoding="utf-8", newline="").write(s)
def L(*ls): return NL.join(ls)

src = read(HERE + "/harness98_base.lua")

def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied (%d)" % (label, count))

# ---------------------------------------------------------------- env pair
sub(L('-- HARNESS 98 (this round): the env pair is now H98_LIVE / H98_ANN.',
      'local LIVE = os.getenv("H98_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H98_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H98_LIVE") ~= nil) or (os.getenv("H98_ANN") ~= nil)'),
    L('-- HARNESS 99 (this round): the env pair is now H99_LIVE / H99_ANN.',
      'local LIVE = os.getenv("H99_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H99_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H99_LIVE") ~= nil) or (os.getenv("H99_ANN") ~= nil)'),
    "env pair")

# ---------------------------------------------------------------- banner
sub('  print("   *** fail; the SILENT worlds pass by design.***")',
    L('  print("   *** fail; the SILENT worlds pass by design.***")',
      '  print("   *** TARGET-CLASS (harness 99): additionally every section-0w token, and every FIRE world of the")',
      '  print("   *** class-gated / Rampage / Merciw / winds families (the snapshot self-casts, so every FIRE world)")',
      '  print("   *** fails; the SILENT worlds pass by design.***")'),
    "banner")

# ---------------------------------------------------------------- trigger counts
sub("== 373", "== 363", "mu 373 pins", count=9)
sub("charge_or_melee\"') == 26", "charge_or_melee\"') == 25", "charge_or_melee 26 pins", count=6)
sub("ushoran_health\"') == 38", "ushoran_health\"') == 34", "ushoran_health 38 pins", count=3)
sub("ally_melee_buff\"') == 11", "ally_melee_buff\"') == 14", "ally_melee_buff 11 pin", count=1)
sub('ally_range_real = ") == 18)', 'ally_range_real = ") == 32)', "ally_range_real 18 pin", count=1)
# the two count-bearing message strings
sub('": the trigger counts grew to (melee_unwavering 373, ushoran_health 38, charge_or_melee 26, "',
    '": the trigger counts grew to (melee_unwavering 363, ushoran_health 34, charge_or_melee 25, "',
    "0o message")
sub('": the trigger counts moved (melee_unwavering 373, charge_or_melee 26, ushoran_health 38, melee_health75 1)"',
    '": the trigger counts moved (melee_unwavering 363, charge_or_melee 25, ushoran_health 34, melee_health75 1)"',
    "0v message")
sub('": the four ally triggers are wired (11 buff / 3 heal / 1 heal_melee / 2 wavering)"',
    '": the four ally triggers are wired (14 buff / 3 heal / 1 heal_melee / 2 wavering)"',
    "0v ally message")

# ---------------------------------------------------------------- tail token list
sub("94, 95, 96 AND 97's worlds included", "94, 95, 96, 97 AND 98's worlds included", "tail list")

# ---------------------------------------------------------------- 0h charge pin
sub("\n      cm == 26)", "\n      cm == 25)", "0h charge_or_melee pin")

# ---------------------------------------------------------------- h93 TIP table
TIP_ANCHOR = '    ally_melee_buff = "When armed, fires when this unit is in melee, on an ally in range",\n  }'
TIP_NEW = ('    ally_melee_buff = "When armed, fires when this unit is in melee, on an ally in range",\n'
           '    ally_overseer = "When armed, fires on a non-commander, non-large ally in range",\n'
           '    ally_beast = "When armed, fires on a beast ally in range",\n'
           '    ally_broken = "When armed, fires on a broken-morale ally in range",\n'
           '    ally_missile = "When armed, fires on a missile-capable ally in range",\n'
           '    ally_warmachine_heal = "When armed, fires on the lowest-health war machine ally in range that is at or below 75% health",\n'
           '    ally_hellforged_heal = "When armed, fires on the lowest-health Hell-Forged ally in range that is at or below 75% health",\n'
           '    ally_monster_heal = "When armed, fires on the lowest-health monster ally in range that is at or below 75% health",\n'
           '    ally_construct_heal = "When armed, fires on the lowest-health construct ally in range that is at or below 75% health",\n'
           '    ally_infinite_buff = "When armed, fires on an ally anywhere on the field (infinite range), cast on that ally",\n'
           '    ally_winds = "When armed, fires on the ally with the most hit points remaining, cast on that ally",\n'
           '  }')
sub(TIP_ANCHOR, TIP_NEW, "h93 TIP table")

# ---------------------------------------------------------------- 0v picker-log token
TOK_OLD = '.. "m bound=" .. tostring(FOURTH.ab_range_m) .. "m")'
TOK_NEW = '.. "m bound=" .. FOURTH.ab_bound_text())'
sub(TOK_OLD, TOK_NEW, "0v picker log token")

# ---------------------------------------------------------------- append section
section = read(HERE + "/h99_section.lua").lstrip(NL)
sub(NL + "run_h98()" + NL, NL + "run_h98()" + NL + NL + section + NL, "append section")

write(HERE + "/harness99.lua", src)
print("wrote harness99.lua", len(src), "bytes")
