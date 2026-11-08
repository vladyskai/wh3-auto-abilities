"""Generate build_and_install110.py from the round-109 builder.

Only the round-110 assertion block and a docstring paragraph are added; every
earlier gate is carried over untouched (nothing above is loosened).
"""
import io
import os

OLD = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261021_airdrop_centre_harness109/build_and_install109.py"
NEW = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/build_and_install110.py"

with open(OLD, "rb") as f:
    b = f.read()
assert b.count(b"\r") == 0
s = b.decode("utf-8")

ANCHOR = "# the main mod must be byte-identical (untouched by this work)\n"
assert s.count(ANCHOR) == 1

BLOCK = '''# ============================================================================
# ROUND 110 (2026-10-18): THE AIR DROP IS PREDICTED, NOT SAMPLED.
#
#   The user's third field report: firing on Drop Rocks (Terradon Riders) is still
#   early or misses - the rocks take about 1-2 s to fall and the flier keeps
#   moving. TWO-BODY RELATIVE-MOTION PREDICTION now ships, under the user's own
#   assumption ("I think the rocks don't keep the momentum, so let's work with
#   that assumption. Let's implement it and I'll test it."): the ordnance lands
#   STRAIGHT DOWN from the caster's position at RELEASE, so
#       caster(t+d) = caster(t) + v_caster * d      <- the impact point
#       enemy (t+d) = enemy (t)  + v_enemy  * d
#   and the drop fires when the PROJECTED horizontal centre separation is inside
#   the SAME 6 m bound. d = FOURTH.AIR_DROP_DELAY_S = 1.5 s, a TUNABLE constant
#   between the 1 s and 2 s the user observed - NOT a game value: no ability row
#   carries a fall time. The velocity is REBUILT from the only reads the API
#   has - is_moving(), is_moving_fast(), slow_speed() / fast_speed() (m/s) and a
#   heading from ordered_position() (normalise(ordered - current)); bearing()
#   ("the current orientation ... in degrees") is the documented CASTER-ONLY
#   fallback, since the dump never states how its degrees map onto x/z. Every
#   unreadable read is ZERO velocity with a NAMED source, never invented motion.
#   FOURTH.AIR_DROP_INHERIT = false is the ONE FLAG that adds v*d a SECOND time
#   (impact = caster + v*d*2) if the field shows the rocks DO keep the momentum.
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19,
#   46 evaluators - behaviour only.
# ============================================================================
assert script_txt.count("\\nFOURTH.AIR_DROP_DELAY_S = 1.5\\n") == 1, \\
    "the 1.5 s fall-delay constant is not defined exactly once"
assert script_txt.count("\\nFOURTH.AIR_DROP_INHERIT = false\\n") == 1, \\
    "the momentum flag is not defined exactly once, or it does not ship FALSE"
assert script_txt.count("\\nFOURTH.AIR_DROP_CENTER_M = 6\\n") == 1, \\
    "the 6 m centre bound moved (it must stay exactly one definition)"
assert "FOURTH.ad_velocity" in script_txt and "function FOURTH.ad_velocity(unit, allow_bearing)" in script_txt, \\
    "the velocity helper is missing"
_vel0 = script_txt.find("function FOURTH.ad_velocity(unit, allow_bearing)")
_vel1 = script_txt.find("\\nend", _vel0)
_vel = script_txt[_vel0:_vel1]
for _tok in ("is_moving()", "is_moving_fast()", "slow_speed()", "fast_speed()",
             "ordered_position()", "bearing()"):
    assert _tok in _vel, "the velocity helper does not read " + _tok
assert 'if moving ~= true then return 0, 0, 0, "stationary" end' in _vel, \\
    "a unit that is not moving does not get a ZERO velocity"
for _src in ('"moving-unreadable"', '"no-speed"', '"no-heading"'):
    assert _src in _vel, "an unreadable velocity source is not named: " + _src
assert "len >= 0.5" in _vel, "the degenerate-ordered-point gate is missing"
assert "if allow_bearing then" in _vel, "the bearing fallback is not caster-gated"
assert script_txt.count("if allow_bearing then") == 2, \\
    "the bearing fallback must be offered in exactly one place (ad_velocity)"
assert "function FOURTH.ad_lead(unit, t, allow_bearing)" in script_txt, \\
    "the two-body state/projection helper is missing"
assert "local px, pz = x + vx * t, z + vz * t" in script_txt, \\
    "the projection does not add v*t on both axes"
assert "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then" in script_txt, \\
    "the ONE momentum flag is not wired to the second v*t"
assert "function FOURTH.ad_project(unit, t)" in script_txt, \\
    "the projected-position helper is missing"
assert "FOURTH.ad_lead(unit, t, false)" in script_txt, \\
    "ad_project does not project an enemy through ad_lead"
assert script_txt.count("does NOT inherit the caster's velocity") == 2, \\
    "the no-momentum assumption is not documented in both places"
assert "ONE FLAG" in script_txt and "impact = caster + v*d*2" in script_txt, \\
    "the single-flag escape hatch is not documented"
assert "TUNABLE CONSTANT" in script_txt, \\
    "the 1.5 s delay is not documented as a tunable constant (not a game value)"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
assert "FOURTH.ad_lead(unit, ad_t, true)" in _pk and "FOURTH.ad_lead(enemy, ad_t, false)" in _pk, \\
    "the picker does not project BOTH bodies"
assert "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)" in _pk and "pgap <= bound" in _pk, \\
    "the picker does not gate on the PROJECTED separation against the bound"
assert "FOURTH.AIR_DROP_DELAY_S" in _pk, "the picker does not read the fall delay"
assert "caster position UNREADABLE" in _pk, "the caster-position fail-closed branch is missing"
assert "FOURTH.ad_centre_gap(unit, enemy)" in _pk, "the instant cross-check left the picker"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc and "FOURTH.ad_project(enemy, ad_t_now)" in _rc, \\
    "the pre-cast re-check does not RE-PROJECT both bodies"
assert "local gap_now = pgap_now" in _rc and \\
    "local in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)" in _rc, \\
    "the re-check's bound test does not run on the projected separation"
assert '" (PROJECTED "' in script_txt, "the target line does not announce the projection"
assert '" v=" .. FOURTH.ad_vec_text(best_uvx, best_uvz, best_uspd, best_usrc)' in script_txt, \\
    "the target line does not print the caster's velocity + source"
assert '" v=" .. FOURTH.ad_vec_text(best_evx, best_evz, best_espd, best_esrc)' in script_txt, \\
    "the target line does not print the enemy's velocity + source"
assert '" proj=" .. FOURTH.ad_pos(best_ipx, best_ipz)' in script_txt, \\
    "the target line does not print the caster's projected point"
assert '" proj=" .. FOURTH.ad_pos(best_epx, best_epz)' in script_txt, \\
    "the target line does not print the enemy's projected point"
assert '" centre=" .. string.format("%.1f", best_gap)' in script_txt, \\
    "the target line does not print the projected separation"
assert '" now="' in script_txt, "the target line does not print the instant separation"
assert '" [projected sep=~"' in script_txt and '"m after delay="' in script_txt, \\
    "the watch line does not print the projected band / delay"
assert "momentum=" in script_txt, "the target line does not name the momentum mode"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \\
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\\t{ marker = ") == 689, "the abilities table is not 689 entries"
assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \\
    "the 70% bypass lost its single wiring"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"

'''

s = s.replace(ANCHOR, BLOCK + ANCHOR)

# the docstring: one paragraph naming the round (inserted before the closing """)
DOC_ANCHOR = '''- an engine unit_in_range call is back'''
if DOC_ANCHOR in s:
    pass

with open(NEW, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote", NEW, os.path.getsize(NEW))
