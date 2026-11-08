#!/usr/bin/env python3
"""Build build_and_install114.py from the round-113 builder.

The round-113 builder's CONTENT gates describe the evaluator the task replaced
(the four dials, the 6 m bound, the derived frontage, the segment test, the
single-entity exclusion). Those assertions are kept for the history and gated
off behind ROUND114 = True; a new ROUND 114 block asserts the shipped state.
"""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261025_airdrop_pathtest_harness113\build_and_install113.py"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_edgesimple_harness114\build_and_install114.py"

SUPERSEDED = (
    "AIR_DROP_CENTER_M", "AIR_DROP_DELAY_S", "AIR_DROP_ENEMY_LEAD",
    "AIR_DROP_CASTER_DELAY_S", "AIR_DROP_CASTER_LEAD", "AIR_DROP_INHERIT",
    "AIR_DROP_MODEL_RADIUS_M", "AIR_DROP_RANKS", "AIR_DROP_FRONTAGE_MIN_M",
    "AIR_DROP_FRONTAGE_MAX_M", "AIR_DROP_BOUND_M",
    "ad_frontage", "ad_seg_dist", "ad_lead", "ad_project", "ad_dial_text",
    "ad_centre_gap", "ad_single_say", "ad_single_clear", "ad_vec_text",
    "ad_velocity", "initial_number_of_men", "over an infantry unit in range",
    "FOURTH.ad_tag(unit)\") == 6", "perpendicular", "perp", "frontage",
    "AIR_DROP_CENTER_M = 6",
    "ad_pos", "ad_sep", "drop lapsed", "still over an INFANTRY", "nearest INFANTRY",
    "AIR_DROP_CASTER_", "FOURTH.ad_tag(unit)", "_tok in _vel", "_vel =",
    "for _tok in", "ad_velocity", "_vel", "ad_lead(", "ad_pick(", "AIR_DROP",
)

STALE_MSGS = (
    "the source does not state that 6 m is the user's own test value",
    'the source does not explain the edge-to-edge failure (boxes near, CENTRES far)',
    'the helper does not read the ground-plane x/z',
    'the helper does not use distance_xz with an x/z fallback',
    'the target line does not say UNDER',
    'the target line does not name the per-model radius constant',
    'the velocity helper does not read is_moving()',
    'the velocity helper does not read is_moving_fast()',
    'the velocity helper does not read slow_speed()',
    'the velocity helper does not read fast_speed()',
    'the velocity helper does not read ordered_position()',
    'the velocity helper does not read bearing()',
    'a unit that is not moving does not get a ZERO velocity',
    'an unreadable velocity source is not named: "moving-unreadable"',
    'an unreadable velocity source is not named: "no-speed"',
    'an unreadable velocity source is not named: "no-heading"',
    'the degenerate-ordered-point gate is missing',
    'the bearing fallback is not caster-gated',
    'the projection does not add v*t on both axes',
    'the no-momentum assumption is not documented once, in the rule comment',
    'the single-flag escape hatch is not documented',
    'the 1.5 s delay is not documented as a tunable constant (not a game value)',
    'the caster-position fail-closed branch is missing',
    'the target line does not announce the projection',
    'the target line does not print the projected separation',
    'the target line does not print the instant separation',
    'the watch line does not print EXACT metres below 15 m (and a band above it)',
    'the target line does not name the momentum mode',
    'the round-111 constant comment is missing',
    'the tuning guide does not state the 0.5 -> 0.3 -> 0.0 order for an early release',
    'the three-symptom tuning guide is not in the source',
    'the source does not say to change one dial per test',
    'the projection helper is missing',
    "the caster's lead time/factor locals are missing",
    'the caster is not projected as position + v * caster_delay * lead (x axis)',
    'the caster is not projected as position + v * caster_delay * lead (z axis)',
    'the ENEMY projection is no longer the shared v*t on both axes',
    'the dials are not applied to the caster alone',
    'an unreadable caster delay does not fall back to the shared delay',
    'an unreadable caster lead does not fall back to full lead (never to a guess)',
    'the moving-caster log fragment is missing',
    'the projection helper is missing',
    'the enemy lead is not read on the enemy arm',
    'the enemy is not projected as position + v * delay * enemy_lead',
    'an unreadable enemy lead does not fall back to the full carry (never to a guess)',
    "the caster's lead locals are missing",
    'the caster is no longer projected by its own delay x lead (x axis)',
    'the caster is no longer projected by its own delay x lead (z axis)',
    'the dial text does not name the enemy lead and the shared delay',
    'the dial text does not name both caster dials',
    'the moving-caster log fragment is missing',
    'the watch line does not print the EXACT projected distance below 15 m',
    'the watch line does not print the EXACT instant distance below 15 m',
    'the 5 m band above 15 m is gone (the log must not grow per 0.1 m there)',
    'the four-dial tuning table is not in the source',
    'the source does not say to change one dial per test',
    'the caster-lead tuning order is gone',
    'the symptom tuning guide is not in the source',
    'the clamp branch is missing',
    'the point-to-segment helper is missing',
    'the segment helper does not project the point onto the segment',
    'the segment parameter is not clamped to 0..1 (an END-point miss would read as a hit)',
    'the formation assumption / the radius evidence is not documented in the source',
    'the clamp is not documented in the source',
    'the source does not state that the commander key set is not consulted',
    'the once-per-episode single-entity skip line is missing',
    'the once-per-episode skip bookkeeping is missing',
)

ROUND114 = r'''
# ============================================================================
# ROUND 114 (2026-10-18): THE AIR-DROP RULE IS ONE COMPARISON + A FAST PASS.
#
#   candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
#   valid     = its unit_distance() is readable
#   chosen    = the NEAREST valid candidate
#   FIRE      = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
#
# RETIRED WITH THE OLD RULE: the infantry filter, the single-entity exclusion, the
# four projection dials, AIR_DROP_CENTER_M, AIR_DROP_INHERIT, the derived frontage
# (radius / ranks / min / max) and the segment test with every helper that served
# them (ad_frontage, ad_frontage_text, ad_seg_dist, ad_velocity, ad_lead,
# ad_project, ad_dial_text, ad_single_say, ad_single_clear, ad_centre_gap, ad_pos,
# ad_sep, ad_vec_text). NOTHING else in the file used any of them.
#
# ADDED: FOURTH.ad_nearest (one candidate scan), FOURTH.ad_fast_pass (the same
# evaluator, same gate+cast path via FOURTH.try_pair, every 0.2 s, for armed
# air-drop units with a valid enemy inside 30 m), its own bm:repeat_callback.
# The global poll keeps POLL_MS = 250 and every other ability's cadence.
# ============================================================================
for _k, _v in (("EDGE_M", "0.1"), ("MIN_MEN", "10"), ("NEAR_M", "30"), ("FAST_S", "0.2")):
    _line = "\nFOURTH.AIR_DROP_" + _k + " = " + _v + "\n"
    assert script_txt.count(_line) == 1, "the round-114 constant is not defined exactly once: " + _k
assert script_txt.count("function FOURTH.ad_nearest(unit)") == 1, \
    "the candidate scan (FOURTH.ad_nearest) is missing"
assert script_txt.count("function FOURTH.ad_fast_pass()") == 1, \
    "the air-drop fast pass is missing"
assert script_txt.count("function FOURTH.try_pair(") == 1, \
    "the shared gate+cast function is missing"
assert script_txt.count("FOURTH.try_pair(") == 3, \
    "the shared gate+cast function is not called by both timers"
assert script_txt.count("bm:repeat_callback(") == 2, \
    "the air-drop fast timer is not registered beside the global poll"
assert script_txt.count("local POLL_MS = 250") == 1, \
    "the global poll interval moved (it must stay 250 ms)"
assert "math.floor(FOURTH.AIR_DROP_FAST_S * 1000)" in script_txt, \
    "the fast timer is not keyed on AIR_DROP_FAST_S"
assert 'zz_test_deadly_onslaught_air_drop_fast' in script_txt, \
    "the fast timer has no name"
assert 'if dist >= FOURTH.AIR_DROP_EDGE_M then' in script_txt, \
    "the decision is not the single edge comparison"
assert "alive > FOURTH.AIR_DROP_MIN_MEN" in script_txt, \
    "the > 10 entity filter is missing"
assert 'FOURTH.ad_say(unit, marker, "nearest valid:\'' in script_txt, \
    "the decision line does not name the enemy / distance"
assert "nearest valid:'" in script_txt and "edge=" in script_txt and "need < " in script_txt, \
    "the decision line lost one of its fields"
assert "-> SKIPPED at re-check" in script_txt, \
    "the pre-cast re-check no longer names its skip"
assert "fast poll: ON (nearest valid " in script_txt and 'fast poll: OFF' in script_txt, \
    "the fast-poll transition lines are missing"
assert script_txt.count("FOURTH.ad_fast_abilities") >= 3, \
    "the fast pass is not driven by the air-drop entry list"
for _dead in ("FOURTH.AIR_DROP_CENTER_M", "FOURTH.AIR_DROP_DELAY_S",
              "FOURTH.AIR_DROP_ENEMY_LEAD", "FOURTH.AIR_DROP_CASTER_DELAY_S",
              "FOURTH.AIR_DROP_CASTER_LEAD", "FOURTH.AIR_DROP_INHERIT",
              "FOURTH.AIR_DROP_MODEL_RADIUS_M", "FOURTH.AIR_DROP_RANKS",
              "FOURTH.AIR_DROP_FRONTAGE_MIN_M", "FOURTH.AIR_DROP_FRONTAGE_MAX_M",
              "function FOURTH.ad_frontage", "function FOURTH.ad_seg_dist",
              "function FOURTH.ad_lead", "function FOURTH.ad_project",
              "function FOURTH.ad_dial_text", "function FOURTH.ad_centre_gap"):
    assert _dead not in script_txt, "a retired air-drop token is back: " + _dead
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 689, "the abilities table is not 689 entries"
assert "air_drop_on_infantry = \"When armed, fires when the nearest enemy unit with more than 10 models is within 0.1 m" in script_txt, \
    "the tooltip sentence does not state the new rule"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"
print("\\n== round 114 content gates                : OK ==")
'''

s = open(SRC, "rb").read().decode("utf-8")
assert s.count("SRC_ROOT = r\"C:/Users/vlady/Desktop/WH3_mod/mod_source\"") == 1
s = s.replace("SRC_ROOT = r\"C:/Users/vlady/Desktop/WH3_mod/mod_source\"",
              "SRC_ROOT = r\"C:/Users/vlady/Desktop/WH3_mod/mod_source\"\nROUND114 = True", 1)

lines = s.split("\n")
out = []
i = 0
gated = 0
while i < len(lines):
    l = lines[i]
    st = l.lstrip()
    if st.startswith("assert "):
        ind = l[:len(l) - len(st)]
        j = i
        blk = [l]
        while lines[j].rstrip().endswith("\\") and j + 1 < len(lines):
            j += 1
            blk.append(lines[j])
        text = "\n".join(blk)
        if any(t in text for t in SUPERSEDED) or any(m in text for m in STALE_MSGS):
            out.append(ind + "if not ROUND114: " + st)
            out.extend(blk[1:])
            gated += 1
        else:
            out.extend(blk)
        i = j + 1
        continue
    out.append(l)
    i += 1
s = "\n".join(out)

assert s.count('step("7 save to disk"') == 1
s = s.replace('step("7 save to disk"', ROUND114 + '\nstep("7 save to disk"', 1)

with open(OUT, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote %s (gated %d superseded asserts)" % (OUT, gated))
