#!/usr/bin/env python3
"""Make build_and_install117.py from the round-116 builder.

Rebases the gates the edge -> centre change flips (round 114's constant,
comparison, retired-token list, tooltip; round 115's separation branch) and
appends the round-117 gate block.
"""
SRC = (r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases"
       r"\20261018_airdrop_velocity_harness116\build_and_install116.py")
DST = (r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases"
       r"\20261018_airdrop_centredist_harness117\build_and_install117.py")


def rd(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "anchor %r matched %d (want %d)" % (old[:70], n, count)
    return s.replace(old, new)


s = rd(SRC)

DOC_TAIL = '''    visible in the field log. Counts UNCHANGED: 689 / 742, air-drop 12 / 19.
"""
'''
DOC_NEW = '''    visible in the field log. Counts UNCHANGED: 689 / 742, air-drop 12 / 19.

ROUND 117 (2026-10-18): THE DETECTION MOVES FROM THE EDGE TO THE CENTRE.
    The user's ruling, verbatim: "Let's keep our current calculation but just
    replace the detection on edge with detection on the distance to center.
    Let's say 6 meters for now. I'll test."
    THE ONE NUMBER THAT MOVED is the gap that decides UNDER. It was the engine's
    bounding-box EDGE gap (`unit:unit_distance(enemy)`, battle_unit.lua:160)
    against AIR_DROP_EDGE_M = 0.1 m; it is now the GROUND-PLANE
    CENTRE-to-CENTRE distance between the caster's and the enemy's own
    position() reads (x/z only - get_y is HEIGHT - via
    position():distance_xz with a sqrt(dx^2 + dz^2) fallback), against
    FOURTH.AIR_DROP_CENTER_M = 6.0 m. FOURTH.ad_centre_gap is BACK as the ONE
    measurement the rule makes; AIR_DROP_EDGE_M is RETIRED (nothing else in the
    file used it).
    RE-MEASURED EVERYWHERE THE OLD NUMBER WAS TAKEN: the candidate's measured
    gap for ranking, the UNDER test, the contact stamping, the dwell / waiting
    and separation lines, the short-crossing fallback, the pre-cast re-check,
    every decision log line (edge= -> centre=, 2 decimals), the family's
    inventory bound and the tooltip sentence.
    KEPT EXACTLY: the candidate filter, the velocity-aware delay MEASURED ONCE
    PER CONTACT, the short-crossing fallback (0.3 s), the 0.2 s fast pass, the
    250 ms poll, air_only / no_melee, the self-centred cast, the gates and the
    read-verification lines. Counts UNCHANGED: 689 / 742, air-drop 12 / 19.
"""
'''
s = must(s, DOC_TAIL, DOC_NEW)

# --- round 114 + 115: the constant, the comparison, the log field -----------
s = must(s, 'for _k, _v in (("EDGE_M", "0.1"), ("MIN_MEN", "10"), ("NEAR_M", "30"), ("FAST_S", "0.2")):',
         'for _k, _v in (("CENTER_M", "6.0"), ("MIN_MEN", "10"), ("NEAR_M", "30"), ("FAST_S", "0.2")):')
s = must(s, "if dist >= FOURTH.AIR_DROP_EDGE_M then",
         "if dist >= FOURTH.AIR_DROP_CENTER_M then", 2)
s = must(s, 'and "edge=" in script_txt and "need < "',
         'and "centre=" in script_txt and "need < "')

# --- the centre helper is BACK: it leaves the retired-token list ------------
s = must(s, '"function FOURTH.ad_dial_text", "function FOURTH.ad_centre_gap"):',
         '"function FOURTH.ad_dial_text"):')
s = must(s, 'for _dead in ("FOURTH.AIR_DROP_CENTER_M", "FOURTH.AIR_DROP_DELAY_S",',
         'for _dead in ("FOURTH.AIR_DROP_DELAY_S",')

# --- the tooltip sentence (round 114's gate and round 115's fragment) -------
s = must(s, 'models closes to 0.1 m" in script_txt,',
         'models comes within 6 m of this unit\'s centre" in script_txt,')
s = must(s, 'assert "after a wait measured from that enemy\'s velocity" in script_txt,',
         'assert "after a wait measured from that enemy\'s velocity" in script_txt,')

GATE = r"""print("\\n== round 116 content gates                : OK ==")

# ============================================================================
# ROUND 117 (2026-10-18): THE DETECTION MOVES FROM THE EDGE TO THE CENTRE.
#
#   UNDER = ad_centre_gap(caster, chosen) < AIR_DROP_CENTER_M (6.0 m)
#   ad_centre_gap = position():distance_xz (x/z ONLY - get_y is HEIGHT), with
#                   sqrt(dx^2 + dz^2) as the fallback, nil on any unreadable read
#
# RETIRED: AIR_DROP_EDGE_M (nothing else in the file used it).
# RE-MEASURED: the ranking gap, the UNDER test, the stamp, the dwell / waiting /
# separation lines, the short-crossing fallback, the pre-cast re-check, the
# family bound and the tooltip. Every decision line says centre=.
# KEPT: the candidate filter, the velocity-aware delay measured once per
# contact, the fallback (0.3 s), the 0.2 s fast pass, POLL_MS = 250, the gates.
# ============================================================================
assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6.0\n") == 1, \
    "the 6 m CENTRE constant is not defined exactly once"
assert script_txt.count("AIR_DROP_EDGE_M") == 0, "the retired edge constant survives"
assert script_txt.count("function FOURTH.ad_centre_gap(caster, enemy)") == 1, \
    "the centre-gap helper is missing"
assert script_txt.count("FOURTH.ad_centre_gap(") == 4, \
    "the centre-gap helper is not wired in (definition + doc + scan + re-check)"
_centre_gap = script_txt.split("function FOURTH.ad_centre_gap(caster, enemy)", 1)[1].split("\nend", 1)[0]
assert "caster:position()" in _centre_gap and "enemy:position()" in _centre_gap, \
    "the centre gap does not read BOTH units' position()"
assert "get_y" not in _centre_gap, "the centre gap reads the HEIGHT (get_y) - it must be x/z only"
for _tok in ("a:get_x()", "a:get_z()", "b:get_x()", "b:get_z()", "a:distance_xz(b)",
             "math.sqrt((dx * dx) + (dz * dz))"):
    assert _tok in _centre_gap, "the centre gap lost a read: " + _tok
assert _centre_gap.count("return nil") == 3, "the centre gap does not fail closed on every path"
assert "FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \
    "the candidate scan does not measure the centre"
_nearest = script_txt.split("function FOURTH.ad_nearest(unit)", 1)[1].split("\nfunction FOURTH.ad_pick", 1)[0]
assert "eg_enemy_gap" not in _nearest and "unit_distance" not in _nearest, \
    "the candidate scan still uses the edge gap"
assert script_txt.count('" centre="') >= 3, "the decision family does not print centre="
assert '" edge="' not in script_txt, "an air-drop line still prints edge="
assert "local centre_now = FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \
    "the pre-cast re-check does not re-measure the centre"
assert "centre_now < FOURTH.AIR_DROP_CENTER_M" in script_txt, \
    "the pre-cast re-check does not compare the centre against the 6 m line"
assert "local gap_ok = (centre_ok or (fallback_now and dwell_ok))" in script_txt, \
    "the pre-cast re-check gap test is not the centre test"
assert "function FOURTH.eg_enemy_gap(unit, enemy)" in script_txt, \
    "eg_enemy_gap was removed - the OTHER triggers still use it"
for _k, _v in (("DWELL_MID_S", "1.0"), ("DWELL_SWING_S", "1.0"), ("MIN_CONTACT_S", "0.3")):
    assert script_txt.count("\nFOURTH.AIR_DROP_" + _k + " = " + _v + "\n") == 1, \
        "a kept delay constant moved or vanished: " + _k
assert script_txt.count("FOURTH.ad_dynamic_delay(") == 2, \
    "the dynamic delay is no longer measured in exactly one place"
assert "local delay, proj, vsrc = FOURTH.ad_dynamic_delay(unit, enemy)" in script_txt, \
    "the delay is no longer taken at the contact stamp"
assert "if under >= FOURTH.AIR_DROP_MIN_CONTACT_S then" in script_txt, \
    "the short-crossing fallback is missing"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 689, "the abilities table is not 689 entries"
assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the family's inventory bound does not follow the 6 m line"
assert "comes within 6 m of this unit's centre" in script_txt, \
    "the tooltip sentence does not state the 6 m centre rule"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"
print("\\n== round 117 content gates                : OK ==")
"""
s = must(s, r'print("\\n== round 116 content gates                : OK ==")' + "\n", GATE)

with open(DST, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote", DST, len(s), "bytes")
