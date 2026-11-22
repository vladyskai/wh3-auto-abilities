#!/usr/bin/env python3
"""Build the round-209 build script from the round-208 one (the user's replies to the afternoon code review).
Rebased counts: 33 enemy_wave / 41 enemy_wander entries, 28 exact waves, 20 growing waves. The round-203 launch-source
gate now also accepts a GROUND-ONLY wave launched from the target centre (Lamprey's Bite).
ROUND 209 GATE: the Loons carry ring_clear and the generated ring table equals the game data. Lamprey's Bite is an
exact, growing, ground-only wave. The player's own cast arms the per-unit window. The poll guards each unit."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_searchcost_harness206\build_and_install208.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies_harness207\build_and_install209.py"
ANCHOR = 'print("ROUND 208 GATE OK: the free-aim search is spread over the polls by unit id and skipped while the ability cannot be cast")\n'
ADD = ANCHOR + r'''# ROUND 209 (the user's replies to the afternoon code review).
import gen_ww_tables as _g209
_rk209 = _g209.ring_keys(script_txt)
assert sorted(_rk209) == ["wh_dlc06_unit_abilities_the_loons_of_eight_peaks", "wh_main_unit_abilities_spinning_loons"], \
    "BUILD REFUSED (round 209): ring_clear is not on exactly the two Loons entries: %s" % _rk209
assert _g209.ring_block(_g209.ring_rows(_rk209)) in script_txt, \
    "BUILD REFUSED (round 209): FOURTH.RING_TEXT differs from the game data (tools/gen_ww_tables.py)"
assert script_txt.count("\nfunction FOURTH.ring_wrap(f, reach)\n") == 1 \
    and "\t\tability.evaluate = FOURTH.ring_wrap(ability.evaluate, FOURTH.RING[ability.keys[1]])\n" in script_txt \
    and "\t\tlocal ok, txt = FOURTH.self_clear(unit, reach)\n\t\tif not ok then return nil end\n" in script_txt \
    and "\t\tif reach == nil then return nil end   -- no table row: fail closed\n" in script_txt, \
    "BUILD REFUSED (round 209): the Loons' friendly-fire ring is not wired or does not fail closed"
_lamp209 = "wh3_dlc24_unit_abilities_lampreys_bite"
assert _lamp209 in _exact204 and _lamp209 in _cone205 and _rows204[_lamp209] == "1,14.1,24,0,0,1,1", \
    "BUILD REFUSED (round 209): Lamprey's Bite is not an exact, growing, ground-only wave"
assert script_txt.count("\nfunction FOURTH.player_cast(key)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.note_own_order(key)\n") == 1 \
    and script_txt.count("\t\t\t\t\tFOURTH.note_own_order(ready_key)") == 1 \
    and script_txt.count("pcall(FOURTH.player_cast, key)") == 1 \
    and script_txt.count('bm:register_command_handler_callback("Special Ability", function(context)') == 1, \
    "BUILD REFUSED (round 209): the player's own cast is not protected (the note, the listener or the window moved)"
assert script_txt.count("\t\tlocal ok_unit, routing, ui_id, ability_key, unit_abilities = pcall(function()\n") == 1 \
    and script_txt.count("\t\t\t\tlocal ok_ab, res_ab = pcall(function()\n") == 1 \
    and script_txt.count('\t\t\t\tif not ok_ab then FOURTH.unit_error(res_ab) elseif res_ab == "gone" then break end\n') == 1, \
    "BUILD REFUSED (round 209): the poll does not guard each unit and each ability step"
print("ROUND 209 GATE OK: the Loons need none of our other units within %s m + 10 m of the caster; Lamprey's Bite is an "
      "aimed wave; the player's own cast holds the selected units; one bad unit no longer ends the poll"
      % _g209.fmt(_g209.ring_rows(_rk209)["wh_main_unit_abilities_spinning_loons"]))
'''
REBASE = [
    ('''assert script_txt.count('trigger = "enemy_wave"') == 32 and script_txt.count('trigger = "enemy_wander"') == 42, \\''',
     '''assert script_txt.count('trigger = "enemy_wave"') == 33 and script_txt.count('trigger = "enemy_wander"') == 41, \\'''),
    ('''            assert _v203["launch_source"] == _src203, \\''',
     '''            assert _v203["launch_source"] == _src203 or (_fam203 == "enemy_wave"
                                                         and _v203["launch_source"] == "target_centre"
                                                         and _a203["target_enemies"] != "true"
                                                         and _a203["target_ground"] == "true"), \\'''),
    ('''assert _e203 == {"enemy_wave": 32, "enemy_wave_charge": 0, "enemy_cone": 5}, \\''',
     '''assert _e203 == {"enemy_wave": 33, "enemy_wave_charge": 0, "enemy_cone": 5}, \\'''),
    ('''assert len(_exact204) == 27 and len(_drift204) == 5, \\''', '''assert len(_exact204) == 28 and len(_drift204) == 5, \\'''),
    ('''assert len(_cone205) == 19, "BUILD REFUSED''', '''assert len(_cone205) == 20, "BUILD REFUSED'''),
    # round 198's count of the waiting-slot uses: FOURTH.player_cast clears it too (5 -> 6)
    ('''    and script_txt.count("cast_gate.unit_waiting[") == 5, \\''',
     '''    and script_txt.count("cast_gate.unit_waiting[") == 6, \\'''),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    for old, new in REBASE:
        assert src.count(old) == 1, (old, src.count(old))
        src = src.replace(old, new)
    src = src.replace(ANCHOR, ADD).replace("20261122_searchcost_harness206", "20261122_replies_harness207")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
