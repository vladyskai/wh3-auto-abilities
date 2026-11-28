#!/usr/bin/env python3
"""Build the round-214 build script from the round-213 one.
1. THE TEST PACK IS A NORMAL MOD PACK (user 2026-11-28: "Yes, set it up that way"): type Mod, not Movie, so it has a
   checkbox in the mod manager. Ticked = the test build runs and the Workshop build stands down by itself. Unticked =
   the Workshop build alone. The build refuses any other type.
2. ROUND 214 GATE: the timing probe exists, runs only in the development build, and times nine places."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_selectcost_harness211\build_and_install213.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_perfprobe_harness212\build_and_install214.py"
ANCHOR = 'print("ROUND 213 GATE OK: a unit whose button never came in a whole window retries once on later selections")\n'
ADD = ANCHOR + r'''# ROUND 214 (tuning, test build only): the timing probe.
assert script_txt.count("\nfunction FOURTH.perf_now()\n") == 1 \
    and script_txt.count("\tif ZZ_AUTO_TEST_NO_PERF == true or zz_badge_set == nil then return nil end\n") == 1 \
    and script_txt.count("FOURTH.perf_add(") == 9 and script_txt.count("\tFOURTH.perf_end_ui(perf_u0)   -- ROUND 214\n") == 1, \
    "BUILD REFUSED (round 214): the timing probe is not wired, or it could run outside the development build"
_i214 = script_txt.index("\nfunction FOURTH.perf_now()\n")
_b214 = script_txt[_i214:script_txt.index("\nlocal function poll()\n", _i214)]
for _t214 in ("perform_special_ability", "cast_gate", "armed[", "owned_keys_by_unit"):
    assert _t214 not in _b214, "BUILD REFUSED (round 214): the timing probe touches '%s' (it must only measure and log)" % _t214
print("ROUND 214 GATE OK: the timing probe measures nine places, in the development build only")
'''
REBASE = [
    ('step("4 type = Movie", {"SetPackFileType": [key, "Movie"]})',
     'step("4 type = Mod", {"SetPackFileType": [key, "Mod"]})   # ROUND 214: a normal mod pack (a checkbox in the mod manager)'),
    ('print("   container:", container["pfh_file_type"], "| files:", in_pack_paths)\n',
     'print("   container:", container["pfh_file_type"], "| files:", in_pack_paths)\n'
     'assert container["pfh_file_type"] == "Mod", "BUILD REFUSED (round 214): the test pack must be type Mod, got %s" '
     '% container["pfh_file_type"]\n'),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for old, new in REBASE:
        assert src.count(old) == 1, (old, src.count(old))
        src = src.replace(old, new)
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261128_selectcost_harness211", "20261128_perfprobe_harness212")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
