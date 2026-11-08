import os, shutil, hashlib

SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261020_airdrops_wlr_harness108/build_and_install108.py"
DSTDIR = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261021_airdrop_centre_harness109"
DST = DSTDIR + "/build_and_install109.py"

os.makedirs(DSTDIR, exist_ok=True)
s = open(SRC, "rb").read().decode("utf-8")

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:120])
    s = s.replace(old, new)

# --- older gate block (the general air-drop one)
rep('''assert "FOURTH.AIR_DROP_BOUND_M = 1" in script_txt, "the air-drop bound constant is not the 1 m user value"
assert "FOURTH.AIR_DROP_BOUND_M = 7" not in script_txt, "the old 7 m air-drop bound is still in the file"''',
'''assert "FOURTH.AIR_DROP_CENTER_M = 6" in script_txt, "the air-drop bound constant is not the 6 m centre value"
assert "AIR_DROP_BOUND_M" not in script_txt, "the retired edge-to-edge bound is still in the file"''')

# --- round-108 block -> round-109 block
rep('''assert script_txt.count("\\nFOURTH.AIR_DROP_BOUND_M = 1\\n") == 1, \\
    "the 1 m air-drop bound constant is not defined exactly once"''',
'''assert script_txt.count("\\nFOURTH.AIR_DROP_CENTER_M = 6\\n") == 1, \\
    "the 6 m air-drop CENTRE constant is not defined exactly once"''')

rep('''assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_BOUND_M") == 1, \\
    "the air-drop entries do not take the one constant"
assert "MUCH TIGHTER" in script_txt and "USER-CHOSEN TEST" in script_txt, \\
    "the source does not state that 1 m is a user-chosen test value"
assert "EDGE-TO-EDGE" in script_txt and "0-5 m" in script_txt, \\
    "the source does not state the edge-to-edge read (a unit on top reads 0-5 m)"
assert "never fires in the field" in script_txt and "ONE constant" in script_txt, \\
    "the source does not say the 1 m value is one constant to bump"''',
'''assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \\
    "the air-drop entries do not take the one centre constant"
assert "the user's own test value, NOT the 70% rule" in script_txt, \\
    "the source does not state that 6 m is the user's own test value"
assert "EDGE-TO-EDGE" in script_txt and "CENTRES are 15 m apart" in script_txt, \\
    "the source does not explain the edge-to-edge failure (boxes near, CENTRES far)"
assert "ONE value to tune" in script_txt and "LOWER FOURTH.AIR_DROP_CENTER_M" in script_txt, \\
    "the source does not say the 6 m value is ONE value to tune"''')

# --- new round-109 content gates, appended to the round-108 section
anchor = '''assert "wh2_main_unit_abilities_drop_rocks" in script_txt, \\
    "the field-tested row (Drop Rocks) is missing from the air-drop family"'''
new = anchor + '''

# ============================================================================
# ROUND 109 (2026-10-18): THE AIR DROP IS A HORIZONTAL CENTRE TEST.
#
#   unit_distance() is EDGE-TO-EDGE (battle_unit.lua:160): two bounding boxes
#   can be half a metre apart while their CENTRES are 15 m apart, so the 1 m
#   edge bound still fired while the flyer was nowhere near over the target.
#   The rule is now |centre(caster) - centre(enemy)| on the GROUND PLANE
#   (x/z - get_y is HEIGHT, so a 3D read would be 30-60 m from a unit directly
#   underneath) against FOURTH.AIR_DROP_CENTER_M = 6 m, ONE documented
#   constant standing in for the formation footprint (the API has no per-unit
#   radius / bbox / size read at all).
# ============================================================================
assert script_txt.count("FOURTH.ad_centre_gap(unit, enemy)") == 3, \\
    "the centre-gap helper is not defined once and called twice (picker + re-check)"
assert "function FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \\
    "the centre-gap helper is missing"
assert "function FOURTH.ad_pos(x, z)" in script_txt, \\
    "the x/z position formatter is missing"
_gap0 = script_txt.find("function FOURTH.ad_centre_gap(unit, enemy)")
_gap1 = script_txt.find("\\nend", _gap0)
_gap = script_txt[_gap0:_gap1]
assert "get_x()" in _gap and "get_z()" in _gap, "the helper does not read the ground-plane x/z"
assert "get_y()" not in _gap, "the helper reads HEIGHT (get_y) - a 3D distance would fire never"
assert "distance_xz" in _gap and "math.sqrt" in _gap, \\
    "the helper does not use distance_xz with an x/z fallback"
assert "' is UNDER the caster" in script_txt, "the target line does not say UNDER"
assert "radius=none" in script_txt, "the target line does not state that no radius read exists"
assert "watch: nearest INFANTRY " in script_txt, \\
    "the why-it-did-not-fire line is missing"
assert "gap <= bound" in script_txt, "the picker does not gate on the centre distance"
_rech0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rech1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rech0)
assert _rech0 > 0 and _rech1 > _rech0
_rech = script_txt[_rech0:_rech1]
assert "FOURTH.ad_centre_gap" in _rech and "FOURTH.eg_enemy_gap" not in _rech, \\
    "the pre-cast re-check does not use the same CENTRE test"'''
rep(anchor, new, 1)

open(DST, "wb").write(s.encode("utf-8"))
print("written", DST, len(s))
print("md5", hashlib.md5(s.encode()).hexdigest())
