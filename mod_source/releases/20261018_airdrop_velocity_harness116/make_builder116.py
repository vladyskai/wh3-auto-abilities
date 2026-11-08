#!/usr/bin/env python3
"""Make build_and_install116.py from the round-115 builder.

The builder is a straight-line RPFM session script with one content-gate block
per round.  This round adds the round-116 gates and rebases the two round-115
gates the change flips (the retired fixed constant and the tooltip sentence).
"""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_dwell_harness115\build_and_install115.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_velocity_harness116\build_and_install116.py"


def rd(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "anchor %r matched %d (want %d)" % (old[:70], n, count)
    return s.replace(old, new)


s = rd(SRC)

# ---- 0. the docstring: the round's own paragraph ---------------------------
DOC_TAIL = '''    KEPT EXACTLY: the four dials, the 6 m bound, AIR_DROP_INHERIT, air_only /
    no_melee, the self-centred cast and every fail-closed read. Counts UNCHANGED:
    689 entries / 742 keys, air_drop_on_infantry 12 / 19.
"""
'''
DOC_NEW = '''    KEPT EXACTLY: the four dials, the 6 m bound, AIR_DROP_INHERIT, air_only /
    no_melee, the self-centred cast and every fail-closed read. Counts UNCHANGED:
    689 entries / 742 keys, air_drop_on_infantry 12 / 19.

ROUND 116 (2026-10-18): THE WAIT IS MEASURED, NOT FIXED - THE ENEMY'S VELOCITY.
    The user's ruling, verbatim: "if the enemy unit is running away, then it is
    too soon. If the enemy moving is running towards, then it is too late. ...
    But it must be calculated the moment the edge to edge distance is below our
    theshold. Then, if the unit is running towards the caster, then the delay
    would be 0. If running away, then the delay would be 2. If stationary or
    perpedicular, then should be 1. ... the delay is dynamic in this way."
    THE FORMULA:
        axis  = normalise(caster.position - enemy.position)      (x/z)
        v     = speed * normalise(ordered_position - position)
        proj  = dot(v, axis) / (speed * |axis|)   clamped to +-1
        delay = AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj, floor 0
    with MID = 1.0 s and SWING = 1.0 s (closing 0 s / across 1 s / receding 2 s).
    MEASURED ONCE at the first contact of a pair, stored on the pair row with
    the cosine and the velocity source, NEVER re-measured inside that contact;
    a re-contact measures again. The 0.2 s fast pass, the 250 ms poll, the
    candidate filter, air_only / no_melee, the self-centred cast, the
    short-crossing fallback and the re-verifying pre-cast re-check are kept.
    THE READ-VERIFICATION LOG: every contact episode prints the RAW answers
    (is_moving, is_moving_fast, slow_speed, fast_speed, position,
    ordered_position, |h|), the cosine, the delay and the velocity source, with
    UNREADABLE where a read failed, so ordered_position()'s real behaviour is
    visible in the field log. Counts UNCHANGED: 689 / 742, air-drop 12 / 19.
"""
'''
s = must(s, DOC_TAIL, DOC_NEW)

# ---- 1. the round-114 tooltip gate ----------------------------------------
s = must(s,
         'assert "air_drop_on_infantry = \\"When armed, fires when the nearest enemy unit with more than 10 models stays within 0.1 m" in script_txt, \\\n'
         '    "the tooltip sentence does not state the dwell"',
         'assert "air_drop_on_infantry = \\"When armed, fires when the nearest enemy unit with more than 10 models closes to 0.1 m" in script_txt, \\\n'
         '    "the tooltip sentence does not state the measured wait"')

# ---- 2. the round-115 block: the constants it pinned ----------------------
s = must(s,
         'for _k, _v in (("DWELL_S", "1.0"), ("MIN_CONTACT_S", "0.3")):',
         'for _k, _v in (("DWELL_MID_S", "1.0"), ("DWELL_SWING_S", "1.0"), ("MIN_CONTACT_S", "0.3")):')
s = must(s,
         'assert "stays within 0.1 m of this unit\'s edge for 1 second" in script_txt, \\\n'
         '    "the tooltip sentence does not state the dwell"',
         'assert "after a wait measured from that enemy\'s velocity" in script_txt, \\\n'
         '    "the tooltip sentence does not state the measured wait"')

# ---- 3. the round-116 gates ----------------------------------------------
GATE = '''print("\\\\n== round 115 content gates                : OK ==")

# ============================================================================
# ROUND 116 (2026-10-18): THE WAIT IS MEASURED - THE ENEMY'S OWN VELOCITY.
#
#   proj  = cos(angle between the enemy's velocity and the enemy -> caster axis)
#   delay = AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj, floored at 0
#
# ADDED: FOURTH.ad_enemy_velocity (the five documented reads + position and
# ordered_position, each pcall'd, failing closed to a ZERO velocity with a
# named source), FOURTH.ad_dynamic_delay (the cosine and the delay),
# FOURTH.ad_proj_text (the cosine as the log prints it), FOURTH.ad_pair_need
# (the delay a pair was given), the delay/proj/src evidence on the pair row,
# and the two log lines the user asked for.
# THE FIXED CONSTANT IS RETIRED: AIR_DROP_DWELL_S must appear NOWHERE.
# UNCHANGED: the candidate filter, the nearest-by-unit_distance pick, air_only /
# no_melee, the self-centred cast, the fail-closed reads, the 0.2 s fast pass,
# POLL_MS = 250, the short-crossing fallback and every gate in FOURTH.try_pair.
# ============================================================================
for _k, _v in (("DWELL_MID_S", "1.0"), ("DWELL_SWING_S", "1.0")):
    _line = "\\nFOURTH.AIR_DROP_" + _k + " = " + _v + "\\n"
    assert script_txt.count(_line) == 1, "the round-116 constant is not defined exactly once: " + _k
assert script_txt.count("\\nFOURTH.AIR_DROP_DWELL_S = ") == 0, \\
    "the retired fixed dwell constant is still defined"
import re as _re116
assert _re116.search(r"AIR_DROP_DWELL_S(?![A-Z_])", script_txt) is None, \\
    "a reference to the retired AIR_DROP_DWELL_S survives"
for _fn in ("ad_enemy_velocity", "ad_dynamic_delay", "ad_proj_text", "ad_pair_need"):
    assert script_txt.count("function FOURTH." + _fn + "(") == 1, \\
        "the round-116 helper is missing: " + _fn
assert script_txt.count("FOURTH.ad_dynamic_delay(") == 2, \\
    "the delay must be COMPUTED ONCE: one definition and one call site"
assert "local delay = FOURTH.AIR_DROP_DWELL_MID_S - (FOURTH.AIR_DROP_DWELL_SWING_S * proj)" in script_txt, \\
    "the delay formula is not the user's"
assert "if delay < 0 then delay = 0 end" in script_txt, "the delay is not floored at 0"
assert "local proj = ((vx * ax) + (vz * az)) / (speed * alen)" in script_txt, \\
    "the cosine is not the projection on the enemy -> caster axis"
assert "local ax, az = cx - FOURTH.ad_vread_px, cz - FOURTH.ad_vread_pz" in script_txt, \\
    "the axis does not run from the enemy to the caster"
assert "if hlen == nil or hlen < 0.5 then" in script_txt and \\
    'return 0, 0, speed, "no-heading"' in script_txt, \\
    "the heading floor / no-heading fallback is missing"
for _src in ('"stationary"', '"moving-unreadable"', '"speed-unreadable"',
             '"pos-unreadable"', '"no-heading"', '"axis-degenerate"'):
    assert _src in script_txt, "the velocity source vocabulary is missing: " + _src
assert "per[eid] = { first = tick_count, delay = delay, proj = proj, src = src }" in script_txt, \\
    "the pair row does not carry the measurement"
assert "local delay, proj, vsrc = FOURTH.ad_dynamic_delay(unit, enemy)" in script_txt and \\
    "FOURTH.ad_pair_stamp(cid, eid, delay, proj, vsrc)" in script_txt, \\
    "the measurement is not taken at the stamp"
assert "need_s = FOURTH.ad_pair_need(st)" in script_txt and \\
    "if (under + 0.000001) >= need_s then" in script_txt, \\
    "the fire test does not use the pair's own delay"
assert '"reads: " .. FOURTH.ad_vread' in script_txt, "the read-verification line is missing"
assert '"reads(hold): " .. FOURTH.ad_vread' in script_txt, "the hold read line is missing"
for _fld in ('put_bool("moving", ok_m, moving)', 'put_bool("is_moving_fast", ok_f, fast)',
             'put_num("slow_speed", ok_s, slow)', 'put_num("fast_speed", ok_q, fastsp)',
             'put_xy("pos", ok_p, pos)', 'put_xy("ordered", ok_o, ord)',
             '"|h|=UNREADABLE"', '"=UNREADABLE"'):
    assert _fld in script_txt, "a read-verification field is missing: " + _fld
assert "local floor_s = FOURTH.AIR_DROP_DWELL_MID_S" in script_txt and \\
    "if type(fired.delay) == \\"number\\" then floor_s = fired.delay end" in script_txt, \\
    "the pre-cast re-check does not verify the measured delay"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \\
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\\t{ marker = ") == 689, "the abilities table is not 689 entries"
print("\\\\n== round 116 content gates                : OK ==")
'''
s = must(s, 'print("\\\\n== round 115 content gates                : OK ==")\n', GATE)

with open(DST, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote", DST, len(s), "bytes")
