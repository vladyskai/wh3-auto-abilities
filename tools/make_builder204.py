#!/usr/bin/env python3
"""Build the round-204 build script from the round-203 one (user ruling 2026-11-22: an exact wave needs no safety
distance, only very few of our soldiers under it, our single entities ignored. Tidecall and Wind Blast too).
Drift: the wave family 30 -> 32 entries and the charge family 2 -> 0 (Tidecall, Wind Blast moved), the free-aim
function gained the sideways shift.
ROUND 204 GATE: the soldiers rule is wired for exact waves only (the WW row's drift is 0), single entities of ours are
skipped, the limit is 5, the shifts are the seven, the search is throttled. The game's data still says which waves are
exact: 27 keys without drift, 5 with (checked against the generated WW table)."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_freeaim_harness201\build_and_install203.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_exactwave_harness202\build_and_install204.py"
R = [
    ("""assert script_txt.count('trigger = "enemy_wave"') == 30 and script_txt.count('trigger = "enemy_wander"') == 42, \\""",
     """assert script_txt.count('trigger = "enemy_wave"') == 32 and script_txt.count('trigger = "enemy_wander"') == 42, \\""", 1),
    ("""for _f164, _n164 in (("enemy_wave_charge", 2), ("enemy_cone", 5), ("enemy_sweep", 2)):""",
     """for _f164, _n164 in (("enemy_wave_charge", 0), ("enemy_cone", 5), ("enemy_sweep", 2)):   # ROUND 204: Tidecall, Wind Blast moved""", 1),
    ("""assert _e203 == {"enemy_wave": 30, "enemy_wave_charge": 2, "enemy_cone": 5}, \\""",
     """assert _e203 == {"enemy_wave": 32, "enemy_wave_charge": 0, "enemy_cone": 5}, \\""", 1),
    ("""    and script_txt.count("\\nfunction FOURTH.ww_aim_value(unit, e, m, row, hx, hz)\\n") == 1 \\""",
     """    and script_txt.count("\\nfunction FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shift)\\n") == 1 \\""", 1),
    ("""assert script_txt.count("FOURTH.ww_aim_value(") == 3 and script_txt.count("ZZ_AUTO_TEST_NO_FREE_AIM") == 2, \\""",
     """assert script_txt.count("FOURTH.ww_aim_value(") == 3 and script_txt.count("ZZ_AUTO_TEST_NO_FREE_AIM") == 3, \\""", 1),
    ("""assert "FOURTH.ww_aim_value(unit, e, m, row, hx, hz)" in _b203 and "FOURTH.ww_target_still(e)" in _b203 \\""",
     """assert "FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shifts[q])" in _b203 and "FOURTH.ww_target_still(e)" in _b203 \\""", 1),
]
ANCHOR_HEAD = 'print("ROUND 203 GATE OK: free aim on %d placed wave keys'
ADD = r'''# ROUND 204 (user ruling 2026-11-22): an exact wave drops the safety distance for a count of OUR SOLDIERS under it.
assert script_txt.count("\nFOURTH.WAVE_OWN_MAX = 5 ") == 1 \
    and script_txt.count("\nFOURTH.FREE_AIM_SHIFTS = { 0, 6, -6, 12, -12, 18, -18 }") == 1 \
    and script_txt.count("\nFOURTH.FREE_AIM_EVERY = 4 ") == 1 \
    and script_txt.count("\nfunction FOURTH.wave_cover(s, sx, sz, ex, ez, r)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.ww_exact(row)\n\treturn row.buf == 0 and ZZ_AUTO_TEST_NO_FREE_AIM ~= true\nend\n") == 1, \
    "BUILD REFUSED (round 204): the soldiers rule's constants or functions moved"
_i204 = script_txt.index("\nfunction FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)\n")
_b204 = script_txt[_i204:script_txt.index("\n-- ROUND 164: the enemy value a path touches", _i204)]
assert _b204.index("if FOURTH.ww_exact(row) then") < _b204.index("local need = row.r + FOURTH.SHOT_SAFE_M + row.buf * math.min(1, tmax)") \
    and "if o.men > 1 then" in _b204 and "own = own + o.men * FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)" in _b204 \
    and "if own > FOURTH.WAVE_OWN_MAX then return nil end" in _b204 and "if oid == nil or oid ~= self_id then" in _b204, \
    "BUILD REFUSED (round 204): an exact wave must count our soldiers (never single entities, never the caster) and " \
    "a drifting wave must keep the safety distance"
_ww204 = _re203.search(r'FOURTH\.WW_TEXT = "([^"]*)"', script_txt).group(1)
_rows204 = dict(x.split("=", 1) for x in _ww204.split(";") if "=" in x)
_exact204, _drift204 = [], []
for _m204 in _re203.finditer(r'\{ marker = "([^"]+)", name = "[^"]*", trigger = "enemy_wave",(.*?)ox = 0', script_txt, _re203.S):
    for _k204 in _re203.findall(r'"(wh[^"]*)"', _m204.group(2).split("keys = {")[1].split("}")[0]):
        _f204 = _rows204[_k204].split(",")
        assert _f204[0] == "1", "BUILD REFUSED (round 204): %s is on enemy_wave but its table row is not a wave" % _k204
        (_exact204 if float(_f204[4]) == 0 else _drift204).append(_k204)
assert len(_exact204) == 27 and len(_drift204) == 5, \
    "BUILD REFUSED (round 204): the exact / drifting split moved (%d exact, %d drifting)" % (len(_exact204), len(_drift204))
for _k204 in ("wh2_dlc11_spell_bound_tidecall", "wh2_dlc11_spell_bound_wind_blast", "wh_main_item_abilities_fiery_ring_of_thori"):
    assert _k204 in _exact204, "BUILD REFUSED (round 204): %s is not an exact wave" % _k204
print("ROUND 204 GATE OK: %d exact waves count our soldiers under the wave (limit 5, single entities and the caster not "
      "counted), %d drifting waves keep the safety distance; Tidecall and Wind Blast ride enemy_wave" % (len(_exact204), len(_drift204)))
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    for a, b, n in R:
        assert src.count(a) == n, (a[:80], src.count(a))
        src = src.replace(a, b)
    i = src.index(ANCHOR_HEAD)
    j = src.index("_n203[\"enemy_wave_charge\"], _n203[\"enemy_cone\"]))\n", i) + len("_n203[\"enemy_wave_charge\"], _n203[\"enemy_cone\"]))\n")
    src = src[:j] + ADD + src[j:]
    src = src.replace("20261122_freeaim_harness201", "20261122_exactwave_harness202")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
