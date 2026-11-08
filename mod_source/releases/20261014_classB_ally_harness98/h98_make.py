# -*- coding: utf-8 -*-
"""HARNESS 98 build: assemble harness98.lua from the SHIPPED harness97.lua.

Round-98 job: CLASS B (ally-targeted effects cast on self). The round moves
melee_unwavering 383 -> 373, charge_or_melee 29 -> 26, ushoran_health 41 -> 38,
melee_health75 2 -> 1, and adds ally_melee_buff 11 / ally_heal 3 /
ally_heal_melee 1 / ally_wavering 2. Two harness-90 worlds legitimately move
(N8b/N8c: Stay Here, I'll Get Help! now casts on the picked ally). Those pins
are RE-BASED here (documented). A NEW section 0v + the ally worlds are appended.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)

def read(p): return io.open(p, encoding="utf-8", newline="").read()
def write(p, s): io.open(p, "w", encoding="utf-8", newline="").write(s)
def L(*ls): return NL.join(ls)

src = read(HERE + "/harness97_base.lua")

def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)

# ---------------------------------------------------------------- env pair
sub(L('-- HARNESS 97 (this round): the env pair is now H97_LIVE / H97_ANN.',
      'local LIVE = os.getenv("H97_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H97_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H97_LIVE") ~= nil) or (os.getenv("H97_ANN") ~= nil)'),
    L('-- HARNESS 98 (this round): the env pair is now H98_LIVE / H98_ANN.',
      'local LIVE = os.getenv("H98_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"',
      'local ANN  = os.getenv("H98_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H98_LIVE") ~= nil) or (os.getenv("H98_ANN") ~= nil)'),
    "env pair")

# ---------------------------------------------------------------- banner
sub('  print("   *** THE REST OF CLASS A (harness 97): additionally every section-0u token, and every")',
    L('  print("   *** THE REST OF CLASS A (harness 97): additionally every section-0u token, and every")',
      '  print("   *** CLASS B (harness 98): additionally every section-0v token, and every FIRE world of the")',
      '  print("   *** Class-B ally families (the snapshot has no ally triggers, so nothing is cast on an ally),")',
      '  print("   *** fail; the SILENT worlds pass by design.***")'),
    "banner")

# ---------------------------------------------------------------- trigger counts
sub("'trigger = \"melee_unwavering\"') == 383", "'trigger = \"melee_unwavering\"') == 373",
    "mu count pins", count=7)
sub("'trigger = \"charge_or_melee\"') == 29", "'trigger = \"charge_or_melee\"') == 26",
    "com count pins", count=5)
sub("mu == 383", "mu == 373", "mu var pin", count=1)
sub("cm == 29", "cm == 26", "cm var pin", count=1)
sub("'trigger = \"ushoran_health\"') == 41", "'trigger = \"ushoran_health\"') == 38",
    "ushoran count pins", count=2)
sub("and cp(s, 'trigger = \"melee_health75\"') == 2)",
    "and cp(s, 'trigger = \"melee_health75\"') == 1)",
    "melee_health75 pin", count=1)
sub("and cp(s, 'trigger = \"melee_health75\"') == 2 and cp(s, 'trigger = \"blood_sacrifice\"') == 1",
    "and cp(s, 'trigger = \"melee_health75\"') == 1 and cp(s, 'trigger = \"blood_sacrifice\"') == 1",
    "0o melee_health75 pin", count=1)
# the 0o message text is brought in line with the re-based counts
sub('"0o " .. nm .. ": the trigger counts grew to (melee_unwavering 480, ushoran_health 41, charge_or_melee 29, "',
    '"0o " .. nm .. ": the trigger counts grew to (melee_unwavering 373, ushoran_health 38, charge_or_melee 26, "',
    "0o message head", count=1)
sub('''      .. "melee_health75 2)",''', '''      .. "melee_health75 1)",''', "0o message tail", count=1)

# ---------------------------------------------------------------- Stay Here reason
sub('''raw_find(live_src90, 'reason = "wavering ally in range (self-cast)"', 1, true) ~= nil)''',
    '''raw_find(live_src90, 'reason = "wavering ally in range, cast on ally"', 1, true) ~= nil)''',
    "0n stay-here reason token")
# N8b: the cast target is now the ALLY (the Class-B cast-target fix)
sub(L('    local b = (fire_target_for(W, 9011) == unit_of(W, 9011))',
      '    check(TAG .. "N8b: the cast target is the OWNER itself (self-cast)", b)'),
    L('    local b = (fire_target_for(W, 9011) == unit_of(W, 9012))',
      '    check(TAG .. "N8b: CLASS B (h98) - the cast target is the WAVERING ALLY, not the owner", b)'),
    "N8b re-base")
sub(L('    local c = (count_log(W, "reason: wavering ally in range (self-cast)") == 1)',
      '    check(TAG .. "N8c: the reason is the wavering-ally-in-range reason [live log]", lg(TAG, c))'),
    L('    local c = (count_log(W, "reason: wavering ally in range, cast on ally") == 1)',
      '    check(TAG .. "N8c: CLASS B (h98) - the reason now says the cast is ON THE ALLY [live log]", lg(TAG, c))'),
    "N8c re-base")

# ---------------------------------------------------------------- h93 TIP map
sub(L('    enemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",',
      '  }'),
    L('    enemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",',
      '    ally_heal = "When armed, fires on the lowest-health ally in range when it is at or below 75% health",',
      '    ally_heal_melee = "When armed, fires when this unit is in melee, on the lowest-health ally in range at or below 75% health",',
      '    ally_wavering = "When armed, fires on a wavering ally in range",',
      '    ally_melee_buff = "When armed, fires when this unit is in melee, on an ally in range",',
      '  }'),
    "h93 TIP map")

# ---------------------------------------------------------------- append section
section = read(HERE + "/h98_section.lua").lstrip(NL)
sub(NL + "run_h97()" + NL, NL + "run_h97()" + NL + NL + section + NL, "append section")

# ---------------------------------------------------------------- tail token list
sub("94, 95 AND 96's worlds included", "95, 96 AND 97's worlds included", "tail list")
sub("93, 95, 96 AND 97's worlds included", "93, 94, 95, 96 AND 97's worlds included", "tail list fix")

write(HERE + "/harness98.lua", src)
print("wrote harness98.lua", len(src), "bytes")
