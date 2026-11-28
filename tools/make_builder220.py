#!/usr/bin/env python3
"""Build the round-220 build script from the round-219 one (sign-off: placed effects do not wait for their caster,
the polls' speed fixes).
ROUND 220 GATE: no placed effect in the ANIM set and every animated projectile still in it (the set itself is compared
with the generator by the round-168 gate), the lock test wired once before the evaluator call, the two caches used by
the blob picker and the wanderer."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_cover_harness217\build_and_install219.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_placed_harness218\build_and_install220.py"
ANCHOR_HEAD = 'print("ROUND 219 GATE OK: the placed blasts need the density line OR half of the target unit\'s own soldiers (never "\n'
ADD = r'''# ROUND 220 (sign-off): a placed effect does not wait for its caster, the polls' speed fixes.
import gen_anim_keys as _ga220
_anim220 = set(_ga220.derive(script_txt))
_placed220 = _ga220.placed_keys(script_txt)
assert len(_placed220) >= 40 and not (_anim220 & set(_placed220)), \
    "BUILD REFUSED (round 220): a placed effect (a vortex, no projectile, no bombardment) is in the ANIM set"
for _k220 in ("wh2_dlc13_weapon_abilities_amber_bow", "wh2_main_unit_abilities_soporific_breath",
              "wh2_main_character_abilities_volley_of_high_arrows"):
    assert _k220 in _anim220, "BUILD REFUSED (round 220): the projectile %s left the ANIM set (it stopped its caster in battle)" % _k220
for _k220 in ("wh2_dlc12_character_abilities_brass_orb", "wh2_main_lord_abilities_gaze_of_malice"):
    assert _k220 not in _anim220, "BUILD REFUSED (round 220): %s is in the ANIM set (it did not stop its caster in battle)" % _k220
assert script_txt.count("\nfunction FOURTH.locked_now(ui_id, ability)\n") == 1 \
    and script_txt.count("\t\t\t\t\tif FOURTH.locked_now(ui_id, ability) then return nil end") == 1 \
    and script_txt.count("FOURTH.locked_now(") == 2 \
    and "\t\t\tlocal ready = FOURTH.charge_hold_ready_on_screen(ui_id, ability, held)\n\t\t\tif ready then return false end\n" in script_txt \
    and script_txt.count("\nfunction FOURTH.blob_score_c(e, m, r)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.blob_friend_gap_c(e, m, reach)\n") == 1 \
    and "\t\t\tlocal g = FOURTH.blob_friend_gap_c(e, m, reach)" in script_txt \
    and "\t\t\t\tlocal sc, un = FOURTH.blob_score_c(e, m, r)\n" in script_txt \
    and "\tlocal sc = FOURTH.blob_score_c(e, m, row.r)" in script_txt \
    and "\tif c == nil or c[1] ~= m or c[2] ~= r then\n" in script_txt \
    and "\tif c == nil or c[1] ~= m or c[2] ~= reach then\n" in script_txt, \
    "BUILD REFUSED (round 220): the lock test or the per-map caches are not wired as tested"
print("ROUND 220 GATE OK: %d placed effects fire on the move (the ANIM set holds %d keys, every animated projectile "
      "among them); no evaluator call while the cast cannot go out; a target's blast numbers once per map"
      % (len(_placed220), len(_anim220)))
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    i = src.index(ANCHOR_HEAD)
    j = src.index("\n", src.index("% len(_g219.cav_spacing_table()))", i)) + 1
    src = src[:j] + ADD + src[j:]
    src = src.replace("20261128_cover_harness217", "20261128_placed_harness218")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
