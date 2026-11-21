#!/usr/bin/env python3
"""Build the round-193 build script from the round-192 one.

Drift: entries 984 -> 985, keys 1037 -> 1038, when_ready 20 -> 21 (Scry-Orb).
ROUND 193 GATE: Scry-Orb on when_ready with its 120 s hold row (= the game's recharge_time, 3 uses); the pre-shot probe
is present, called once per ranged unit while not firing and at the first shot, and READ-ONLY (none of its three
functions issues an order)."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_closing_harness191\build_and_install192.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_preshot_harness192\build_and_install193.py"
COUNTS = [("984", "985"), ("1037", "1038")]
ANCHOR = ('print("ROUND 192 GATE OK: running + closing; 5 runes gone; Grombrindal Has No Fear (55 m); Moulder rule (%d units)"\n'
          '      % len(_gr192.derive_moulder()))\n')
ADD = ANCHOR + r'''# ROUND 193 (user 2026-11-21): Scry-Orb on when_ready ("implement"); the read-only pre-shot probe ("implement
# recommendation and propose a test battle").
assert ('{ marker = "scry_orb", name = "Scry-Orb", trigger = "when_ready",\n\t\tbadge = "zz_auto_badge_scry_orb",\n'
        '\t\tkeys = { "wh3_dlc29_item_abilities_scry_orb" },') in script_txt, "BUILD REFUSED (round 193): Scry-Orb is not on when_ready"
import csv as _csv193
import gamedata_paths as _gp193
with open(_gp193.GAMEDATA + r"\unit_spec_abil.tsv", encoding="utf-8-sig") as _f193:
    _r193 = list(_csv193.reader(_f193, delimiter="\t"))
_h193 = _r193[0]
_row193 = next(r for r in _r193[2:] if r and r[0] == "wh3_dlc29_item_abilities_scry_orb")
_rec193 = int(float(_row193[_h193.index("recharge_time")]))
_use193 = int(float(_row193[_h193.index("num_uses")]))
assert _use193 > 1 and ('\t\t["wh3_dlc29_item_abilities_scry_orb"] = %d,\n' % _rec193) in script_txt, \
    "BUILD REFUSED (round 193): Scry-Orb's hold row is not its recharge (%d s, %d uses)" % (_rec193, _use193)
for _fn193 in ("preshot_now", "preshot_probe", "preshot_first_shot"):
    _i193 = script_txt.index("\nfunction FOURTH.%s(" % _fn193)
    _j193 = script_txt.index("\nend\n", _i193)
    _b193 = script_txt[_i193:_j193]
    assert "perform_special_ability" not in _b193 and "attempt_activation" not in _b193, \
        "BUILD REFUSED (round 193): FOURTH.%s issues an order (the probe must be read-only)" % _fn193
assert script_txt.count("if not st.firing then FOURTH.preshot_probe(u, st, now_s, inr, d, r) end   -- ROUND 193: read-only") == 1 \
    and script_txt.count("FOURTH.preshot_first_shot(u, st, now_s)   -- ROUND 193: the read-only pre-shot probe") == 1, \
    "BUILD REFUSED (round 193): the pre-shot probe is not called where it belongs"
print("ROUND 193 GATE OK: Scry-Orb on when_ready (hold %d s, %d uses); the pre-shot probe is read-only" % (_rec193, _use193))
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    for old, new in COUNTS:
        got = len(re.findall(r"(?<!\d)%s(?!\d)" % old, src))
        src = re.sub(r"(?<!\d)%s(?!\d)" % old, new, src)
        print(old, "->", new, ":", got)
    pat = r"""(\.count\('trigger = "when_ready"'\) == )20(?!\d)"""
    print("when_ready 20 -> 21 :", len(re.findall(pat, src)))
    src = re.sub(pat, r"\g<1>21", src)
    assert src.count(ANCHOR) == 1
    src = src.replace(ANCHOR, ADD)
    src = src.replace("20261121_closing_harness191", "20261121_preshot_harness192")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
