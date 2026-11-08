#!/usr/bin/env python3
"""Generate build_and_install118.py from the round-117 builder.

The only edits:
  * the module docstring gains the ROUND 118 paragraph;
  * the round-115 / 116 / 117 CONTENT GATE blocks (which assert the delay
    machinery exists) are replaced by the round-118 gates (which assert it is
    GONE and that the centre rule, the fast pass, the gates and the re-check
    survive).
Everything else - the pack contents, the WebSocket session, the byte checks,
the install and the md5 report - is byte-identical to round 117.
"""
SRC = "mod_source/releases/20261018_airdrop_centredist_harness117/build_and_install117.py"
DST = "mod_source/releases/20261018_airdrop_immediate_harness118/build_and_install118.py"

s = open(SRC, encoding="utf-8").read()
assert "\r" not in s

DOC = '''ROUND 118 (2026-10-18): THE AIR-DROP DELAY IS GONE. THE CENTRE STAYS.
The user's ruling, verbatim: "I tried it. Let's keep the distance to center and
remove the delay we had completely." The trigger now casts on the evaluation
that first measures the nearest valid enemy's CENTRE inside 6 m: no dwell, no
dynamic velocity delay, no cosine, no per-pair contact row, no timestamps, no
short-crossing fallback, no raw movement/heading read-verification log. The
centre helper, the candidate filter, the 0.2 s fast pass (30 m gate), the
250 ms poll, air_only / no_melee, the self-centred cast, every fail-closed read,
the gates and the pre-cast re-check are KEPT.

'''
anchor = '"""\nimport hashlib'
assert s.count(anchor) == 1
s = s.replace(anchor, DOC + anchor)

GATES = '''# ============================================================================
# ROUND 118 (2026-10-18): THE AIR-DROP DELAY IS GONE. THE CENTRE STAYS.
#
#   candidate = ALIVE, number_of_men_alive() > AIR_DROP_MIN_MEN (10)
#   chosen    = the NEAREST valid candidate by ad_centre_gap
#   FIRE      = ad_centre_gap(caster, chosen) < AIR_DROP_CENTER_M (6.0 m),
#               on the evaluation that measured it (subject only to the armed
#               state, air_only / no_melee, the gates and the pre-cast re-check)
#
# DELETED (nothing outside the air-drop evaluator, its pre-cast re-check and
# the drop routine's purge hook ever named any of it):
#   AIR_DROP_DWELL_MID_S, AIR_DROP_DWELL_SWING_S, AIR_DROP_MIN_CONTACT_S,
#   FOURTH.ad_pair + ad_pair_key / ad_pair_stamp / ad_pair_need / ad_pair_drop
#   / ad_under / ad_purge_unit / ad_contact_clear, the purge hook
#   zz_ad_dwell_purge (its one call site lived in drop_unit_by_ui_id),
#   ad_enemy_velocity + ad_vread / ad_vread_px / ad_vread_pz, ad_proj_text,
#   ad_dynamic_delay, ad_event, the short-crossing fallback and every
#   dwell / hold / delay / cosine log line, INCLUDING the raw movement and
#   heading read-verification block (it existed only to check the cosine).
# KEPT: the CENTRE detection and ad_centre_gap, the candidate filter (no
#   infantry test), the 0.2 s fast pass with its 30 m near gate, POLL_MS = 250,
#   air_only / no_melee, the self-centred cast, every fail-closed read, the
#   gates in try_pair and the pre-cast re-check on FRESH handles.
# ============================================================================
assert script_txt.count("\\nFOURTH.AIR_DROP_CENTER_M = 6.0\\n") == 1, \\
    "the 6 m CENTRE constant is not defined exactly once"
for _k, _v in (("MIN_MEN", "10"), ("NEAR_M", "30"), ("FAST_S", "0.2")):
    assert script_txt.count("\\nFOURTH.AIR_DROP_" + _k + " = " + _v + "\\n") == 1, \\
        "a kept air-drop constant moved or vanished: " + _k
for _dead in ("AIR_DROP_DWELL_MID_S", "AIR_DROP_DWELL_SWING_S", "AIR_DROP_MIN_CONTACT_S",
              "FOURTH.ad_pair", "ad_pair_key", "ad_pair_stamp", "ad_pair_need",
              "ad_pair_drop", "ad_under", "ad_purge_unit", "ad_contact_clear",
              "zz_ad_dwell_purge", "ad_enemy_velocity", "ad_proj_text",
              "ad_dynamic_delay", "ad_vread", "FOURTH.ad_event", "ad_fired",
              "dwell", "short crossing", "proj="):
    assert script_txt.count(_dead) == 0, \\
        "the deleted delay machinery is back in the script: " + _dead
assert script_txt.count("function FOURTH.ad_centre_gap(caster, enemy)") == 1, \\
    "the centre-gap helper is missing"
assert script_txt.count("FOURTH.ad_centre_gap(") == 4, \\
    "the centre-gap helper is not wired in (definition + doc + scan + re-check)"
_centre_gap = script_txt.split("function FOURTH.ad_centre_gap(caster, enemy)", 1)[1].split("\\nend", 1)[0]
assert "caster:position()" in _centre_gap and "enemy:position()" in _centre_gap, \\
    "the centre gap does not read BOTH units' position()"
assert "get_y" not in _centre_gap, "the centre gap reads the HEIGHT (get_y) - it must be x/z only"
for _tok in ("a:get_x()", "a:get_z()", "b:get_x()", "b:get_z()", "a:distance_xz(b)",
             "math.sqrt((dx * dx) + (dz * dz))"):
    assert _tok in _centre_gap, "the centre gap lost a read: " + _tok
assert _centre_gap.count("return nil") == 3, "the centre gap does not fail closed on every path"
assert "FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \\
    "the candidate scan does not measure the centre"
_nearest = script_txt.split("function FOURTH.ad_nearest(unit)", 1)[1].split("\\nfunction FOURTH.ad_pick", 1)[0]
assert "eg_enemy_gap" not in _nearest and "unit_distance" not in _nearest, \\
    "the candidate scan still uses the edge gap"
_pick = script_txt.split("function FOURTH.ad_pick(unit, routing)", 1)[1].split(
    "\\nfunction FOURTH.evaluate_air_drop_on_infantry", 1)[0]
assert _pick.count("if dist >= FOURTH.AIR_DROP_CENTER_M then") == 1, \\
    "the evaluator is not ONE comparison against the 6 m line"
assert "-> NOT YET" in _pick, "the NOT YET decision line is missing"
assert "-> FIRING" in _pick and "FOURTH.ad_enemy = enemy" in _pick, \\
    "the UNDER branch does not go straight to the cast"
for _read in ("is_moving", "slow_speed", "fast_speed", "ordered_position", "tick_count"):
    assert _read not in _pick, "the evaluator still consults a movement/clock read: " + _read
assert script_txt.count('" centre="') >= 3, "the decision family does not print centre="
assert '" edge="' not in script_txt, "an air-drop line still prints edge="
assert "local centre_now = FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \\
    "the pre-cast re-check does not re-measure the centre"
assert "centre_now < FOURTH.AIR_DROP_CENTER_M" in script_txt, \\
    "the pre-cast re-check does not compare the centre against the 6 m line"
assert "and (not melee_now) and enemy_alive and men_ok and centre_ok) then" in script_txt, \\
    "the pre-cast re-check's gate list is not the centre test"
assert "function FOURTH.eg_enemy_gap(unit, enemy)" in script_txt, \\
    "eg_enemy_gap was removed - the OTHER triggers still use it"
assert 'bm:repeat_callback(poll, POLL_MS, POLL_NAME)' in script_txt, \\
    "the 250 ms poll is no longer registered"
assert script_txt.count("bm:repeat_callback(") == 2, \\
    "the poll + the 0.2 s fast pass are no longer both registered"
assert "zz_test_deadly_onslaught_air_drop_fast" in script_txt, \\
    "the fast pass registration is missing"
assert "local POLL_MS = 250" in script_txt, "POLL_MS moved"
assert "dist < FOURTH.AIR_DROP_NEAR_M" in script_txt, "the 30 m fast-pass gate is missing"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \\
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\\t{ marker = ") == 689, "the abilities table is not 689 entries"
assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \\
    "the family's inventory bound does not follow the 6 m line"
assert "comes within 6 m of this unit's centre" in script_txt, \\
    "the tooltip sentence does not state the 6 m centre rule"
assert "casts immediately on that evaluation - no delay at all" in script_txt, \\
    "the tooltip does not say the cast is immediate"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"
print("\\\\n== round 118 content gates                : OK ==")
'''

START = "# ROUND 115 (2026-10-18): THE TRIGGER WAITS"
END_KEY = "round 117 content gates"
i = s.index(START)
j = s.index("\n", s.index(END_KEY, i)) + 1
# keep the "# ===" separator line that opened the round-115 block out of the cut
seg = s[i:j]
assert "ROUND 117" in seg and "ROUND 116" in seg and "ROUND 115" in seg
s = s[:i] + GATES + s[j:]

assert "\r" not in s
open(DST, "w", encoding="utf-8", newline="").write(s)
print("wrote", DST, len(s), "bytes")
