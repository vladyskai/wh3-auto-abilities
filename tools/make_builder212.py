#!/usr/bin/env python3
"""Build the round-212 build script from the round-211 one (a transformed unit is a new unit: the watch list comes from
the army's own unit list).
ROUND 212 GATE: cast_gate.raw_items exists once and feeds the watch-list loop, it falls back to the script units when
the army's list is unreadable or empty, a unit without a controller is left out, the two fresh-handle fetchers fall
back to the made script unit, and the poll re-lists 2 s after a cast."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_rawprobe_harness209\build_and_install211.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_transform_harness210\build_and_install212.py"
ANCHOR = 'print("ROUND 211 GATE OK: the raw unit probe is read-only and runs from the map probe")\n'
ADD = ANCHOR + r'''# ROUND 212: a transformed unit is a new unit, the watch list comes from the army's own unit list.
_i212 = script_txt.index("\nfunction cast_gate.raw_items(sunits, total)\n")
_b212 = script_txt[_i212:script_txt.index("\nlocal ALL_ABILITY_KEYS = {}\n", _i212)]
assert script_txt.count("\nfunction cast_gate.raw_items(sunits, total)\n") == 1 \
    and script_txt.count("cast_gate.raw_items(") == 2 \
    and "\tlocal items, revive = cast_gate.raw_items(sunits, total)\n\tfor r = 1, #revive do gone_units[revive[r]] = nil end\n" \
        "\tfor i = 1, #items do\n\t\tlocal script_unit = items[i]\n" in script_txt, \
    "BUILD REFUSED (round 212): the watch list is not built from cast_gate.raw_items"
assert "\tif raw == nil then return items, revive end\n" in _b212 and "\t\tif n >= 1 then raw = list end\n" in _b212 \
    and "\t\t\tif made ~= nil then\n\t\t\t\tout[#out + 1] = made\n" in _b212 \
    and "local uc = r.army:create_unit_controller()" in _b212 and "uc:add_units(r.unit)" in _b212, \
    "BUILD REFUSED (round 212): the army's list must fall back to the script units, and a unit without a controller stays out"
for _t212 in ("FOURTH.", "log(", "tick_count", "gone_units"):
    assert _t212 not in _b212, \
        "BUILD REFUSED (round 212): cast_gate.raw_items sits above '%s' in the file and must not name it" % _t212
assert script_txt.count("\treturn cast_gate.raw_sunits[want]   -- ROUND 212") == 2, \
    "BUILD REFUSED (round 212): the two fresh-handle fetchers must fall back to the made script unit"
assert script_txt.count("\tif FOURTH.relist_at ~= nil and tick_count >= FOURTH.relist_at then\n\t\tFOURTH.relist_at = nil\n"
                        "\t\trebuild_unit_list()\n\tend\n") == 1 \
    and script_txt.count("\tFOURTH.relist_at = tick_count + 8   -- ROUND 212") == 1, \
    "BUILD REFUSED (round 212): the poll must re-list 2 s after a cast"
print("ROUND 212 GATE OK: the watch list comes from the army's own unit list (a transformed unit is watched, its frozen "
      "copy dropped), with the script units as the fallback")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_rawprobe_harness209", "20261122_transform_harness210")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
