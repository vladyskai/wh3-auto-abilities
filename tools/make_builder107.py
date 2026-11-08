# -*- coding: utf-8 -*-
"""Build build_and_install107.py from the harness-106 builder.

Only the CONTENT GATES move (the pack/install machinery is untouched):
  * the table pins: 675 -> 688 entries, 721 -> 741 keys, 193 -> 205 range_real
  * the melee_skip_commanders pin: 2 -> 3 entries (Call of Tor joins it)
  * a new ROUND 107 assertion block for the air-drop family and the per-unit
    serialisation window
"""
import hashlib
import os

REL106 = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_bombardment_harness106"
REL107 = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261019_bombardment_harness107"
SRC = os.path.join(REL106, "build_and_install106.py")
DST = os.path.join(REL107, "build_and_install107.py")


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def write(p, s):
    data = s.encode("utf-8")
    assert b"\r" not in data
    with open(p, "wb") as f:
        f.write(data)


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, "count %d (want %d): %r" % (c, n, old[:120])
    return s.replace(old, new)


s = read(SRC)

# ---------------------------------------------------------------- table pins
s = rep(s, 'assert script_txt.count("\\t{ marker = ") == 675, "the abilities table is not 675 entries"',
        'assert script_txt.count("\\t{ marker = ") == 688, "the abilities table is not 688 entries"',
        s.count('assert script_txt.count("\\t{ marker = ") == 675, "the abilities table is not 675 entries"'))
s = rep(s, 'assert script_txt.count("\\t\\trange_real = ") == 193, "the range_real fields are not 193"',
        'assert script_txt.count("\\t\\trange_real = ") == 205, "the range_real fields are not 205"')
s = rep(s, 'assert script_txt.count("\\t\\trange_real = ") == 193, "range_real count is not 193"',
        'assert script_txt.count("\\t\\trange_real = ") == 205, "range_real count is not 205"')
s = rep(s, """assert script_txt.count('trigger = "melee_skip_commanders"') == 2, \\
    "Soulfire + Arachneruption are not the two melee_skip_commanders entries\"""",
        """assert script_txt.count('trigger = "melee_skip_commanders"') == 3, \\
    "Soulfire + Arachneruption + Call of Tor are not the three melee_skip_commanders entries\"""")

# ------------------------------------------------- the ROUND 107 gate block
BLOCK = r'''

# ---------------------------------------------------------------------------
# ROUND 107 (2026-10-18): THE REMAINING BOMBARDMENT WORK.
#   (1) Call of Tor joins Soulfire's trigger: melee_skip_commanders now has
#       THREE entries (Soulfire 2 keys, Arachneruption, Call of Tor).
#   (2) The "on top of" family: 12 entries / 19 keys on the NEW
#       air_drop_on_infantry evaluator - an enemy INFANTRY unit inside the
#       row's 70% bound (7 m of its 10 m), airborne where the row says so,
#       out of melee where the row says so, self-centred cast, logged
#       pre-cast re-check.
#   (3) The PER-UNIT serialisation window: after any successful cast no OTHER
#       ability may be issued on that unit for wind-up + 2 s (min 2.5 s), so
#       two ready abilities fire in sequence instead of replacing each other.
# ---------------------------------------------------------------------------
AIR = [
    ("death_from_above", "wh2_dlc09_unit_abilities_death_from_above"),
    ("drop_rocks", "wh2_main_unit_abilities_drop_rocks"),
    ("drop_rocks", "wh2_dlc12_unit_abilities_drop_rocks_character"),
    ("drop_rocks", "wh2_dlc12_unit_abilities_drop_rocks_of_chotec"),
    ("drop_rocks", "wh2_dlc12_unit_abilities_drop_rocks_of_sundering"),
    ("drop_sphere_of_tepok", "wh2_dlc12_lord_abilities_drop_sphere_of_tepok"),
    ("drop_sphere_of_tepok", "wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded"),
    ("fire_bombs", "wh3_dlc25_unit_abilities_gyrobomber_fire_bomb"),
    ("fire_bombs", "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb"),
    ("gyrobomber_bomb", "wh_main_unit_abilities_gyrobomber_bomb"),
    ("gyrobomber_bomb", "wh_main_unit_abilities_gyrocopter_bomb"),
    ("gyrocopter_bomb_anti_large", "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large"),
    ("sky_junk_bomb", "wh3_main_unit_abilities_sky_junk_bomb"),
    ("skyhammer_bomb", "wh_dlc06_unit_abilities_skyhammer_bomb"),
    ("skyhammer_bomb", "wh_dlc06_unit_abilities_skyhammer_fire_bomb"),
    ("wake_of_fire", "wh2_main_unit_abilities_wake_of_fire"),
    ("searing_torrent", "wh3_twa07_unit_abilities_searing_torrent"),
    ("nan_gau_grenades", "wh3_dlc24_unit_abilities_nan_gau_grenades"),
    ("undeath_from_above", "wh3_dlc29_unit_abilities_undeath_from_above"),
]
assert len(AIR) == 19, "the air-drop key list is not 19"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is not 12 entries"
for _mk, _ky in AIR:
    assert 'marker = "%s"' % _mk in script_txt, "air-drop marker missing: " + _mk
    assert '"%s"' % _ky in script_txt, "air-drop key missing: " + _ky
assert script_txt.count("\t\trange_real = 10,") == 12, "the air-drop range_real fields are not 12"
assert "FOURTH.ENEMY_CAST_R10  = 7" in script_txt, "the 10 m -> 7 m 70% constant is missing"
assert "\t[10]  = FOURTH.ENEMY_CAST_R10," in script_txt, "the 10 m map entry is missing"
assert "FOURTH.AIR_DROP_BOUND_M = 7" in script_txt, "the air-drop bound constant is missing"
assert 'air_only = true,' in script_txt and 'air_only = false,' in script_txt, "the air_only flags are missing"
assert script_txt.count('air_only = false,') == 2, \
    "the two documented NON-air-gated entries are not exactly two (Drop Sphere, Searing Torrent)"
assert 'no_melee = true,' in script_txt and 'no_melee = false,' in script_txt, "the no_melee flags are missing"
assert 'function FOURTH.ad_pick(unit, routing)' in script_txt, "the air-drop picker is missing"
assert 'function FOURTH.evaluate_air_drop_on_infantry(unit, routing)' in script_txt, \
    "the air-drop evaluator is missing"
assert "air_drop_on_infantry = FOURTH.evaluate_air_drop_on_infantry," in script_txt, \
    "the air-drop trigger is not wired"
assert 'air_drop_on_infantry = "When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it",' in script_txt, \
    "the air-drop tooltip sentence is missing"
assert "unit:is_currently_flying()" in script_txt, "the flight read is missing"
assert "FOURTH.enemy_is_infantry(enemy)" in script_txt, "the infantry read is missing from the picker"
assert "FOURTH.eg_enemy_gap(unit, enemy)" in script_txt, "the overlap proxy is missing"
assert "SKIPPED: the drop lapsed before the cast" in script_txt, "the air-drop lapse line is missing"
assert "pre-cast re-check: still over an INFANTRY enemy" in script_txt, "the air-drop re-check line is missing"
assert "if FOURTH.ad_enemy ~= nil then" in script_txt, "the air-drop pre-cast block is missing"
assert "FOURTH.ad_air_only = (ability.air_only == true)" in script_txt, "the poll does not set the air_only flag"
assert "FOURTH.ad_no_melee = (ability.no_melee == true)" in script_txt, "the poll does not set the no_melee flag"
# the air-drop keys are SELF-CENTRED - they must NEVER be in the ground-key set
_g0 = script_txt.find("enemy_ground_keys = {")
_g1 = script_txt.find("\t},\n", _g0)
assert _g0 > 0 and _g1 > _g0
for _mk, _ky in AIR:
    assert ('["%s"] = true,' % _ky) not in script_txt[_g0:_g1], \
        "an air-drop key is in enemy_ground_keys: " + _ky

# CALL OF TOR
assert 'marker = "call_of_tor", name = "Call of Tor", trigger = "melee_skip_commanders"' in script_txt, \
    "Call of Tor is not on Soulfire's trigger"
assert '"wh3_twa07_spell_bound_call_of_tor"' in script_txt, "Call of Tor's key is missing"
assert '["wh3_twa07_spell_bound_call_of_tor"] = 90,' in script_txt, "Call of Tor's charge-gate row is missing"
assert '["wh3_twa07_spell_bound_call_of_tor"] = 1,' in script_txt, "Call of Tor's 1 s wind-up is missing"

# THE PER-UNIT SERIALISATION WINDOW
assert "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5" in script_txt, "the stagger constant is missing"
assert "unit_until = {}," in script_txt, "the per-unit window slot is missing"
assert "unit_marker = {}," in script_txt, "the per-unit marker slot is missing"
assert "unit_logged = {}," in script_txt, "the per-unit log slot is missing"
assert "and cast_gate.unit_marker[ui_id] ~= ability.marker" in script_txt, \
    "the gate does not read the per-unit marker"
assert "local unit_hold_s = ((ability.wind_up_s or 0) + IN_FLIGHT_SETTLE_SECONDS)" in script_txt, \
    "the per-unit hold arithmetic is missing"
assert "if unit_hold_s < FOURTH.SERIAL_MIN_HOLD_SECONDS then" in script_txt, \
    "the per-unit stagger clamp is missing"
assert "cast_gate.unit_until[ui_id] = tick_count + math.floor((unit_hold_s * 1000) / POLL_MS)" in script_txt, \
    "the per-unit window is never armed"
assert "cast_gate.unit_until[id_slot] = nil" in script_txt, "the per-unit window is not purged"
assert "per-unit cast gate " in script_txt, "the per-unit wait/arm log lines are missing"
assert "if cast_gate.unit_marker[ui_id] ~= ability.marker then" in script_txt, \
    "a same-marker repeat would re-arm the window (starvation)"
'''

anchor = "\n\n# ============================================================================\n# ROUND 106 - THE BOMBARDMENT ROUND (two approved families). The gates below"
assert anchor in s, "the v106 block anchor is missing"
s = s.replace(anchor, BLOCK + anchor, 1)

# --------------------------------------------------------------- provenance
s = rep(s, "Counts: 643 -> 675 entries, 687 -> 721 keys, 43 -> 45 evaluators.",
        "Counts: 643 -> 675 entries, 687 -> 721 keys, 43 -> 45 evaluators.\n"
        "\n"
        "ROUND 107 (2026-10-18): Call of Tor joins melee_skip_commanders; the 11\n"
        "\"on top of\" abilities (12 entries / 19 keys) ride the NEW\n"
        "air_drop_on_infantry evaluator (enemy INFANTRY inside the row's 70%\n"
        "bound, airborne / out of melee where the row says so, self-centred\n"
        "cast, logged pre-cast re-check); the PER-UNIT serialisation window\n"
        "(wind-up + 2 s, min 2.5 s) stops two ready abilities on one unit from\n"
        "replacing each other. Counts: 675 -> 688 entries, 721 -> 741 keys,\n"
        "45 -> 46 evaluators.")

write(DST, s)
print("build_and_install107.py", len(s), "bytes", hashlib.md5(s.encode("utf-8")).hexdigest())
