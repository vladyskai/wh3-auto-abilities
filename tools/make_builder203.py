#!/usr/bin/env python3
"""Build the round-203 build script from the round-202 one (free aim for the straight waves, user 2026-11-22:
"A: but be careful. Dragon breaths always come from a caster. Other abilities might also, check individually to be
sure." and "All 30 placed").
ROUND 203 GATE (PERMANENT): every key on enemy_wave is PLACED by the game (battle_vortexs.launch_source =
target_near_edge) and has a ground form (target_ground true), checked key by key. Every enemy_cone key starts at the
caster (activator_front) and free aim never reaches the cone or the charge-wave evaluators. The free-aim code is wired
(24 headings, the oriented ground order, the per-entry reset, the fail-closed point)."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_waveprobe_harness200\build_and_install202.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_freeaim_harness201\build_and_install203.py"
ANCHOR = ('print("ROUND 202 GATE OK: the wave probe zz_wave (console only, called by nothing), the mod\'s own ground casts '
          'unchanged")\n')
ADD = ANCHOR + r'''# ROUND 203 (user rulings 2026-11-22): free aim for the straight waves, key by key.
import csv as _csv203
import re as _re203
import gamedata_paths as _gp203


def _tab203(name):
    with open(_gp203.GAMEDATA + "\\" + name, encoding="utf-8-sig") as _f:
        _r = list(_csv203.reader(_f, delimiter="\t"))
    return {x[0]: dict(zip(_r[0], x)) for x in _r[2:] if x}


_usa203, _vx203 = _tab203("unit_spec_abil.tsv"), _tab203("battle_vortexs.tsv")
_n203 = {"enemy_wave": 0, "enemy_wave_charge": 0, "enemy_cone": 0}
_e203 = {"enemy_wave": 0, "enemy_wave_charge": 0, "enemy_cone": 0}
for _fam203, _src203 in (("enemy_wave", "target_near_edge"), ("enemy_wave_charge", "target_near_edge"),
                         ("enemy_cone", "activator_front")):
    for _m203 in _re203.finditer(r'\{ marker = "([^"]+)", name = "[^"]*", trigger = "%s",(.*?)ox = 0' % _fam203,
                                 script_txt, _re203.S):
        _e203[_fam203] += 1
        for _k203 in _re203.findall(r'"(wh[^"]*)"', _m203.group(2).split("keys = {")[1].split("}")[0]):
            _a203 = _usa203[_k203]
            _v203 = _vx203.get(_a203["vortex"])
            assert _v203 is not None, "BUILD REFUSED (round 203): %s has no vortex row" % _k203
            assert _v203["launch_source"] == _src203, \
                "BUILD REFUSED (round 203): %s starts at '%s', its family %s needs '%s'" \
                % (_k203, _v203["launch_source"], _fam203, _src203)
            if _fam203 == "enemy_wave":
                assert _a203["target_ground"] == "true", \
                    "BUILD REFUSED (round 203): %s has no ground form, free aim cannot order it" % _k203
            _n203[_fam203] += 1
assert _e203 == {"enemy_wave": 30, "enemy_wave_charge": 2, "enemy_cone": 5}, \
    "BUILD REFUSED (round 203): the wave families moved: %s" % _e203
assert script_txt.count("\nFOURTH.FREE_AIM_STEPS = 24 ") == 1 \
    and script_txt.count("\nfunction FOURTH.ww_aim_value(unit, e, m, row, hx, hz)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.aim_cast(uc, ability_key, aim)\n") == 1 \
    and script_txt.count("uc:perform_special_ability_ground(ability_key, pos, aim.deg, 0)") == 1 \
    and script_txt.count('\telseif FOURTH.eg_arm == "ww" and FOURTH.ww_aim ~= nil then\n') == 1 \
    and script_txt.count("\tFOURTH.ww_aim = nil   -- ROUND 203: the free aim of a wave\n") == 1, \
    "BUILD REFUSED (round 203): the free-aim code is not wired"
# free aim is asked for in ONE place: the enemy_wave evaluator (never the charge waves, the cones, the wanderers)
assert script_txt.count("FOURTH.ww_aim_value(") == 3 and script_txt.count("ZZ_AUTO_TEST_NO_FREE_AIM") == 2, \
    "BUILD REFUSED (round 203): free aim is asked for outside the enemy_wave evaluator (%d, %d)" \
    % (script_txt.count("FOURTH.ww_aim_value("), script_txt.count("ZZ_AUTO_TEST_NO_FREE_AIM"))
_i203 = script_txt.index("\nfunction FOURTH.evaluate_enemy_wave(unit, routing)\n")
_b203 = script_txt[_i203:script_txt.index("\nfunction FOURTH.evaluate_enemy_wander(unit, routing)\n", _i203)]
assert "FOURTH.ww_aim_value(unit, e, m, row, hx, hz)" in _b203 and "FOURTH.ww_target_still(e)" in _b203 \
    and "local free = (ZZ_AUTO_TEST_NO_FREE_AIM ~= true)" in _b203, \
    "BUILD REFUSED (round 203): the enemy_wave evaluator does not test the free headings on standing targets"
_c203 = script_txt.index("\nfunction FOURTH.aim_cast(uc, ability_key, aim)\n")
_cb203 = script_txt[_c203:script_txt.index("\nend\n", _c203)]
assert "if pos == nil then return nil, nil, true end" in _cb203 and "bm:get_terrain_height(aim.x, aim.z)" in _cb203, \
    "BUILD REFUSED (round 203): the free-aim cast must fail closed on an unreadable point"
print("ROUND 203 GATE OK: free aim on %d placed wave keys (%d entries, each target_near_edge with a ground form); "
      "%d charge-wave keys and %d caster-front cone keys untouched" % (_n203["enemy_wave"], _e203["enemy_wave"],
                                                                      _n203["enemy_wave_charge"], _n203["enemy_cone"]))
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_waveprobe_harness200", "20261122_freeaim_harness201")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
