#!/usr/bin/env python3
"""Build the round-219 build script from the round-218 one (sign-off: the cover rule and cavalry for the placed blasts,
the per-family timer).
ROUND 219 GATE: the cavalry spacing table equals the one generated from the game data, the cover rule and the wander
map are wired once, the user's two numbers are named constants, the timer sits behind the probe's switch."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_logcost_harness216\build_and_install218.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_cover_harness217\build_and_install219.py"
ANCHOR = ('print("ROUND 218 GATE OK: the log times itself only while the timing probe is on; the PERF line carries the log '
          'and probe cost")\n')
ADD = ANCHOR + r'''# ROUND 219 (sign-off): the placed blasts hit most of the target unit, standing cavalry is a target.
import gen_blob_tables as _g219
_cav219 = _g219.lua_block_cav(_g219.cav_spacing_table())
assert script_txt.count(_cav219) == 1, \
    "BUILD REFUSED (round 219): the cavalry spacing table differs from the game data (tools/gen_blob_tables.py)"
assert len(_g219.cav_spacing_table()) >= 150, "BUILD REFUSED (round 219): the cavalry spacing table is nearly empty"
assert script_txt.count("\nfunction FOURTH.cover_need(line, men)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.cover_own(e, r)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.ww_map(m)\n") == 1 \
    and script_txt.count("FOURTH.COVER_FRACTION = 0.50\n") == 1 and script_txt.count("FOURTH.COVER_MIN_MEN = 20\n") == 1 \
    and script_txt.count("\tif sc < FOURTH.blob_need(row.r) and own < FOURTH.cover_need(FOURTH.blob_need(row.r), e.men) "
                         "then return nil end\n") == 1 \
    and script_txt.count("\tm = FOURTH.ww_map(m)   -- ROUND 219: infantry and cavalry\n") == 1 \
    and script_txt.count("FOURTH.ww_map(") == 5 \
    and script_txt.count("m.cav[#m.cav + 1] = s") == 1, \
    "BUILD REFUSED (round 219): the cover rule or the wander map is not wired as tested"
# the cavalry list is read by the wander map only: every other blob family keeps the infantry list
assert script_txt.count("m.cav") == 5, \
    "BUILD REFUSED (round 219): m.cav is read outside FOURTH.ww_map (%d uses)" % script_txt.count("m.cav")
assert script_txt.count("\nfunction FOURTH.perf_trig(name, t0)\n") == 1 \
    and script_txt.count("\t\t\t\t\tFOURTH.perf_trig(ability.trigger, perf_e0)\n") == 1 \
    and "\tif t0 == nil then return end\n\tlocal row = FOURTH.perf_t[name]\n" in script_txt, \
    "BUILD REFUSED (round 219): the per-family timer is not behind the probe's switch"
print("ROUND 219 GATE OK: the placed blasts need the density line OR half of the target unit's own soldiers (never "
      "fewer than 20) under the blast; enemy cavalry is a target of the wanderers only; %d cavalry spacings from the "
      "game data; the evaluators are timed by family in the development build" % len(_g219.cav_spacing_table()))
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    # REBASE: the round-197 gate (the wanderers keep the plain trash rule) pinned the line that held both tests.
    # Round 219 splits it: the density-or-cover test first, the plain trash rule on its own line.
    old = '"if sc < FOURTH.blob_need(row.r) or not FOURTH.blob_trash_ok(e, sc, row.r) then return nil end" in script_txt'
    new = '"\\tif not FOURTH.blob_trash_ok(e, sc, row.r) then return nil end\\n" in script_txt'
    assert src.count(old) == 1, src.count(old)
    src = src.replace(old, new)
    src = src.replace(ANCHOR, ADD).replace("20261128_logcost_harness216", "20261128_cover_harness217")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
