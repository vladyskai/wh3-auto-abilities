"""Generate build_and_install111.py from the round-110 builder.

Only the round-111 assertion block and the docstring paragraph are added; every
earlier gate is carried over untouched (nothing above is loosened).
"""
import io
import os

OLD = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/build_and_install110.py"
NEW = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/build_and_install111.py"

with open(OLD, "rb") as f:
    b = f.read()
assert b.count(b"\r") == 0
s = b.decode("utf-8")

ANCHOR = "# the main mod must be byte-identical (untouched by this work)\n"
assert s.count(ANCHOR) == 1

BLOCK = r'''# ============================================================================
# ROUND 111 (2026-10-18): THE MOVING-CASTER DIALS - ONLY THE CASTER'S LEAD.
#
#   The user's fourth field report: "It seems to work okay when the caster is
#   stationary, but it definitely drops the rocks too soon when in movement."
#   A stationary caster is RIGHT, so the ENEMY projection and the 6 m bound are
#   right; the error exists only while the caster moves and fires TOO SOON, so
#   the caster's lead term is OVER-STATED. Two dials now qualify the CASTER only:
#       caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S
#                                          * AIR_DROP_CASTER_LEAD
#       enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S
#   shipped as (AIR_DROP_CASTER_DELAY_S = 1.5, AIR_DROP_CASTER_LEAD = 0.5).
#   0.0 is a caster treated as stationary (the field-correct case); 1.0 is the
#   round-110 behaviour that over-leads. The enemy term, the 6 m bound, the
#   INHERIT flag, air_only / no_melee, the self-centred cast, the fail-closed
#   reads and the re-projecting pre-cast re-check are ALL unchanged - the
#   re-check calls the same helper, so it reads the same two dials.
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.
# ============================================================================
assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\n") == 1, \
    "the caster's own lead time is not defined exactly once at 1.5 s"
assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n") == 1, \
    "the caster lead factor is not defined exactly once at 0.5"
assert script_txt.count("\nFOURTH.AIR_DROP_DELAY_S = 1.5\n") == 1, \
    "the shared fall delay moved (the ENEMY term must stay exactly as it was)"
assert script_txt.count("\nFOURTH.AIR_DROP_INHERIT = false\n") == 1, \
    "the momentum flag moved or no longer ships FALSE"
assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1, \
    "the 6 m centre bound moved (it must stay exactly one definition)"
assert "THE MOVING-CASTER DIALS" in script_txt, "the round-111 constant comment is missing"
assert "LOWER the lead: 0.5 -> 0.3 -> 0.0" in script_txt, \
    "the tuning guide does not state the 0.5 -> 0.3 -> 0.0 order for an early release"
assert "fires EARLY while MOVING" in script_txt and "NEVER fires while MOVING" in script_txt \
    and "still EARLY while STATIONARY" in script_txt, \
    "the three-symptom tuning guide is not in the source"
assert "Only ONE dial changes per test" in script_txt, \
    "the source does not say to change one dial per test"
_ld0 = script_txt.find("function FOURTH.ad_lead(unit, t, allow_bearing)")
_ld1 = script_txt.find("\nend", _ld0)
_ld = script_txt[_ld0:_ld1]
assert _ld0 > 0 and _ld1 > _ld0, "the projection helper is missing"
assert "local t_caster, lead_caster = t, 1" in _ld, \
    "the caster's lead time/factor locals are missing"
assert "px = x + vx * t_caster * lead_caster" in _ld, \
    "the caster is not projected as position + v * caster_delay * lead (x axis)"
assert "pz = z + vz * t_caster * lead_caster" in _ld, \
    "the caster is not projected as position + v * caster_delay * lead (z axis)"
assert "local px, pz = x + vx * t, z + vz * t" in _ld, \
    "the ENEMY projection is no longer the shared v*t on both axes"
assert "if allow_bearing == true then" in _ld, \
    "the dials are not applied to the caster alone"
assert 'if type(d_caster) == "number" and d_caster >= 0 then t_caster = d_caster end' in _ld, \
    "an unreadable caster delay does not fall back to the shared delay"
assert 'if type(l_caster) == "number" and l_caster >= 0 then lead_caster = l_caster end' in _ld, \
    "an unreadable caster lead does not fall back to full lead (never to a guess)"
assert "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then" in _ld and \
    "px = px + vx * t_caster * lead_caster" in _ld, \
    "the ONE momentum flag no longer adds the lead term a second time"
assert script_txt.count("FOURTH.AIR_DROP_CASTER_DELAY_S") >= 3, \
    "the caster delay is not read in the source"
assert "function FOURTH.ad_dial_text(moving)" in script_txt, "the dial-text helper is missing"
assert script_txt.count("FOURTH.ad_dial_text") == 5, \
    "the dial-text helper must be defined once and called four times (target, watch, skip, re-check)"
assert '.. " from " .. FOURTH.ad_dial_text(best_uspd > 0)' in script_txt, \
    "the decision line does not print the two dials after the caster projection"
assert '" moving caster: lead="' in script_txt, \
    "the moving-caster log fragment is missing"
assert script_txt.count("FOURTH.ad_dial_text(uc_spd2 ~= nil and uc_spd2 > 0)") == 2, \
    "the pre-cast re-check does not print the dials on BOTH its lines"
assert '.. " (" .. FOURTH.ad_dial_text(best_uspd > 0) .. "); enemy v="' in script_txt, \
    "the why-not line does not print the dials beside the caster velocity"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
assert "FOURTH.ad_lead(unit, ad_t, true)" in _pk and "FOURTH.ad_lead(enemy, ad_t, false)" in _pk, \
    "the picker no longer projects both bodies"
assert "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)" in _pk and "pgap <= bound" in _pk, \
    "the picker no longer gates on the projected separation"
assert "FOURTH.AIR_DROP_CASTER_DELAY_S" not in _pk, \
    "the picker reaches for a dial directly instead of the one helper"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc and "FOURTH.ad_project(enemy, ad_t_now)" in _rc, \
    "the pre-cast re-check no longer re-projects both bodies"
assert "FOURTH.AIR_DROP_CASTER_LEAD" not in _rc and "FOURTH.AIR_DROP_CASTER_DELAY_S" not in _rc, \
    "the re-check re-derives the dials instead of using the shared helper"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 689, "the abilities table is not 689 entries"
assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the 70% bypass lost its single wiring"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"

'''

s = s.replace(ANCHOR, BLOCK + ANCHOR)

with open(NEW, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote", NEW, os.path.getsize(NEW))
