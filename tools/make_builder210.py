#!/usr/bin/env python3
"""Build the round-210 build script from the round-209 one (the user's second replies to the afternoon code review).
Rebased: 72 enemy_ground_melee / 2 enemy_wave_charge entries (the Loons, launched from the caster's front), 85 keys in
the WW table, 25 growing rows (the 5 caster-front breaths joined), the ring on no entry.
ROUND 210 GATE: the Loons' rule (the user's 15 to 25 m, standing caster, approaching infantry, the path), the breaths
as cones from the caster, the 2-second run-up, the re-read of a unit's abilities after a cast."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies_harness207\build_and_install209.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies2_harness208\build_and_install210.py"
ANCHOR = '''      "aimed wave; the player's own cast holds the selected units; one bad unit no longer ends the poll")\n'''
ADD = ANCHOR + r'''# ROUND 210 (the user's second replies to the afternoon code review).
_loons210 = ["wh_dlc06_unit_abilities_the_loons_of_eight_peaks", "wh_main_unit_abilities_spinning_loons"]
for _k210 in _loons210:
    assert _rows204[_k210].split(",")[0] == "8" and _rows204[_k210].split(",")[5] == "1", \
        "BUILD REFUSED (round 210): %s is not a kind-8 row that hits allies" % _k210
    assert _usa203[_k210]["target_ground"] == "true", "BUILD REFUSED (round 210): %s has no ground form" % _k210
assert script_txt.count('\t{ marker = "spinning_loons", name = "Spinning Loons", trigger = "enemy_wave_charge",\n') == 1 \
    and script_txt.count('\t{ marker = "loons_of_eight_peaks", name = "The Loons of Eight Peaks", trigger = "enemy_wave_charge",\n') == 1, \
    "BUILD REFUSED (round 210): the Loons are not on enemy_wave_charge"
# the two distances are the user's own metre values (named constants, outside the range rule)
assert script_txt.count("\nFOURTH.LOONS_MIN_M = 15 ") == 1 and script_txt.count("\nFOURTH.LOONS_MAX_M = 25 ") == 1, \
    "BUILD REFUSED (round 210): the user's 15 to 25 m band moved"
_i210 = script_txt.index("\nfunction FOURTH.ww_loons_ok(unit, e, m, row, closing)\n")
_b210 = script_txt[_i210:script_txt.index("\nfunction FOURTH.evaluate_loons(unit, routing, row)\n", _i210)]
assert "if not closing then return nil end" in _b210 and "if not (ok_c and c_mv == false) then return nil end" in _b210 \
    and "not FOURTH.enemy_is_infantry(e.unit)" in _b210 and "if e.men <= 1" in _b210 \
    and "gap < FOURTH.LOONS_MIN_M or gap > FOURTH.LOONS_MAX_M" in _b210 and "if o.men > 1 then" in _b210 \
    and "local need = row.r + row.buf * math.min(1, tmax)" in _b210, \
    "BUILD REFUSED (round 210): the Loons' rule lost a condition (standing caster, approaching infantry, the band, the path)"
assert "\tif row ~= nil and row.kind == 8 then return FOURTH.evaluate_loons(unit, routing, row) end   -- ROUND 210\n" in script_txt \
    and "\t\t\tif row.kind == 8 then   -- ROUND 210: the Loons, the same rule on the fresh map\n" in script_txt, \
    "BUILD REFUSED (round 210): the Loons' evaluator or its pre-cast re-check is not wired"
# the five caster-front breaths are cones from the caster
_c210 = script_txt.index("\nfunction FOURTH.ww_cone_value(unit, e, m, row)\n")
_cb210 = script_txt[_c210:script_txt.index("\nend\n", _c210)]
assert "if FOURTH.ww_exact(row) and row.r0 ~= nil then" in _cb210 \
    and "FOURTH.ww_line_value(unit, m, row, cx, cz, cx + dx / len * row.path, cz + dz / len * row.path)" in _cb210, \
    "BUILD REFUSED (round 210): a caster-front breath is not tested as a cone from the caster"
for _m210 in _re203.finditer(r'\{ marker = "([^"]+)", name = "[^"]*", trigger = "enemy_cone",(.*?)ox = 0', script_txt, _re203.S):
    for _k210 in _re203.findall(r'"(wh[^"]*)"', _m210.group(2).split("keys = {")[1].split("}")[0]):
        assert _k210 in _cone205 and float(_rows204[_k210].split(",")[4]) == 0, \
            "BUILD REFUSED (round 210): the breath %s has no cone row or is not exact" % _k210
# the run-up and the re-read
assert script_txt.count("\t\t\tif m.speed ~= nil and m.speed * 2 < run_up then run_up = m.speed * 2 end\n") == 1 \
    and script_txt.count("\t\t\tenough_run_up = (m.target_dist >= run_up)\n") == 1, \
    "BUILD REFUSED (round 210): the run-up is not the smaller of 12 m and 2 s of the unit's run speed"
assert script_txt.count("\nfunction FOURTH.reread_unit(unit, ui_id, periodic)\n") == 1 \
    and script_txt.count("FOURTH.rescan_soon(") == 3 \
    and script_txt.count("\t\t\t\tlocal changed210, found210 = FOURTH.reread_unit(unit, ui_id, do_redetect)\n") == 1, \
    "BUILD REFUSED (round 210): a unit's abilities are not read again after a cast"
print("ROUND 210 GATE OK: the Loons fire at approaching infantry 15 to 25 m away down a clear path; the 5 breaths are "
      "cones from the caster; slow units can charge; a unit's abilities are read again after a cast")
'''
REBASE = [
    ('''assert len(_kf162) == 83 and _g162.lua_block''', '''assert len(_kf162) == 85 and _g162.lua_block'''),
    ('''assert len(_kf164) == 83 and _g164.nomelee_block''', '''assert len(_kf164) == 85 and _g164.nomelee_block'''),
    ('''for _f164, _n164 in (("enemy_wave_charge", 0), ("enemy_cone", 5), ("enemy_sweep", 2)):''',
     '''for _f164, _n164 in (("enemy_wave_charge", 2), ("enemy_cone", 5), ("enemy_sweep", 2)):   # ROUND 210: the Loons'''),
    ('''for _fam203, _src203 in (("enemy_wave", "target_near_edge"), ("enemy_wave_charge", "target_near_edge"),''',
     '''for _fam203, _src203 in (("enemy_wave", "target_near_edge"), ("enemy_wave_charge", "activator_front"),'''),
    ('''assert _e203 == {"enemy_wave": 33, "enemy_wave_charge": 0, "enemy_cone": 5}, \\''',
     '''assert _e203 == {"enemy_wave": 33, "enemy_wave_charge": 2, "enemy_cone": 5}, \\'''),
    ('''assert len(_cone205) == 20, "BUILD REFUSED''', '''assert len(_cone205) == 25, "BUILD REFUSED'''),
    ('''    assert _k205 in _exact204, "BUILD REFUSED (round 205): the growing wave %s is not an exact wave" % _k205''',
     '''    assert _k205 in _exact204 or _rows204[_k205].split(",")[0] == "5", \\
        "BUILD REFUSED (round 205): the growing wave %s is not an exact wave or a caster-front breath" % _k205'''),
    ('''assert sorted(_rk209) == ["wh_dlc06_unit_abilities_the_loons_of_eight_peaks", "wh_main_unit_abilities_spinning_loons"], \\''',
     '''assert sorted(_rk209) == [], \\'''),
    ('''print("ROUND 209 GATE OK: the Loons need none of our other units within %s m + 10 m of the caster; Lamprey's Bite is an "''',
     '''print("ROUND 209 GATE OK: the ring code stays, on no entry since round 210; Lamprey's Bite is an "'''),
    ('''      % _g209.fmt(_g209.ring_rows(_rk209)["wh_main_unit_abilities_spinning_loons"]))\n''', ''''''),
    ('''      "aimed wave; the player's own cast holds the selected units; one bad unit no longer ends the poll"\n''',
     '''      "aimed wave; the player's own cast holds the selected units; one bad unit no longer ends the poll")\n'''),
    ('''assert script_txt.count('trigger = "enemy_ground_melee"') == 74, \\''',
     '''assert script_txt.count('trigger = "enemy_ground_melee"') == 72, \\'''),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for old, new in REBASE:
        assert src.count(old) == 1, (old, src.count(old))
        src = src.replace(old, new)
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_replies_harness207", "20261122_replies2_harness208")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
