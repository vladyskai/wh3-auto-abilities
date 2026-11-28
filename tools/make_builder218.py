#!/usr/bin/env python3
"""Build the round-218 build script from the round-217 one (tuning, live copy only: the log's own cost).
ROUND 218 GATE: the log times itself only while the probe is on, and the PERF line carries the new fields."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_groupcards_harness215\build_and_install217.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_logcost_harness216\build_and_install218.py"
ANCHOR = ('print("ROUND 217 GATE OK: with several units selected the whole-HUD walk waits only for an ability every selected unit "\n'
          '      "owns; the unit cards are read 5 times a second once the game accepted a selection callback")\n')
ADD = ANCHOR + r'''# ROUND 218 (tuning, live copy only): the timing probe measures the test build's own log.
assert script_txt.count("\tif cast_gate.log_on == true then log_t0 = os.clock() end\n") == 1 \
    and script_txt.count("cast_gate.log_on = true") == 1 \
    and "\tif type(os) ~= \"table\" or type(os.clock) ~= \"function\" then return nil end\n\tcast_gate.log_on = true" in script_txt \
    and script_txt.count(" | log %.1f ms %d lines (in polls %.1f) | probe %.1f ms (its log %.1f)") == 1, \
    "BUILD REFUSED (round 218): the log's own timer is not behind the probe's switch"
print("ROUND 218 GATE OK: the log times itself only while the timing probe is on; the PERF line carries the log and probe cost")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    # REBASE: the round-214 gate forbade the word cast_gate inside the probe's block. Round 218 keeps the log's own
    # timer in three fields of that table (log_on, log_ms, log_n) because log() sits above the FOURTH table. Those
    # three names are allowed, every other use of cast_gate in the block still refuses the build.
    old = '_b214 = script_txt[_i214:script_txt.index("\\nlocal function poll()\\n", _i214)]\n'
    new = old + ('for _f218 in ("cast_gate.log_on", "cast_gate.log_ms", "cast_gate.log_n"):   # round 218\n'
                 '    _b214 = _b214.replace(_f218, "")\n')
    assert src.count(old) == 1, src.count(old)
    src = src.replace(old, new)
    src = src.replace(ANCHOR, ADD).replace("20261128_groupcards_harness215", "20261128_logcost_harness216")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
