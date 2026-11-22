#!/usr/bin/env python3
"""Build the round-205 build script from the round-204 one (the growing waves are cones, enemy single entities are not
counted; user 2026-11-22).
ROUND 205 GATE: FOURTH.WW_CONE_TEXT equals what tools/gen_wave_cone.py derives from the game data (19 growing waves),
the point test uses the wave's radius at that point, an exact wave's value skips enemy single entities."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_exactwave_harness202\build_and_install204.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_cone_harness203\build_and_install205.py"
ANCHOR_HEAD = 'print("ROUND 204 GATE OK: %d exact waves count our soldiers under the wave'
ADD = r'''# ROUND 205 (user 2026-11-22): the growing waves are cones (GENERATED), enemy single entities are not counted.
import gen_wave_cone as _gc205
_cone205 = _gc205.derive(script_txt)
assert len(_cone205) == 19, "BUILD REFUSED (round 205): the growing-wave set moved (%d)" % len(_cone205)
assert ('\nFOURTH.WW_CONE_TEXT = "%s"\n' % _gc205.text(_cone205)) in script_txt, \
    "BUILD REFUSED (round 205): FOURTH.WW_CONE_TEXT differs from the game data (run tools/gen_wave_cone.py)"
for _k205 in _cone205:
    assert _k205 in _exact204, "BUILD REFUSED (round 205): the growing wave %s is not an exact wave" % _k205
assert script_txt.count("\nfunction FOURTH.ww_in_wave(px, pz, sx, sz, ex, ez, r)\n") == 1 \
    and "if cone ~= nil then rr = math.min(r, cone.r0 + cone.grow * t * math.sqrt(l2)) end" in script_txt \
    and script_txt.count("FOURTH.ww_in_wave(") == 3 \
    and script_txt.count("\t\tFOURTH.ww_cone = (row.r0 ~= nil) and row or nil   -- ROUND 205") == 1, \
    "BUILD REFUSED (round 205): the cone test is not wired"
assert "\t\t\tif o.men > 1 then\n\t\t\t\tlocal c = FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)\n" in _b204, \
    "BUILD REFUSED (round 205): an exact wave's value must skip enemy single entities"
print("ROUND 205 GATE OK: %d growing waves carry their real cone (start radius, growth per metre from the game data); "
      "an exact wave's value counts enemy soldiers only" % len(_cone205))
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    i = src.index(ANCHOR_HEAD)
    j = src.index("% (len(_exact204), len(_drift204)))\n", i) + len("% (len(_exact204), len(_drift204)))\n")
    src = src[:j] + ADD + src[j:]
    src = src.replace("20261122_exactwave_harness202", "20261122_cone_harness203")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
