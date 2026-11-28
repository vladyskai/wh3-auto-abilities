#!/usr/bin/env python3
"""Round 218 (tuning, live copy only): the tracker (10.95) and CLAUDE.md."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.95 Round 218 (tuning, live copy only) - the timing probe measures the log itself (2026-11-28)

**Field, two battles on the round-217 build.**

Battle A (archive\\logs\\battle_20261128_r217_perf.txt, bytes 1,142,970,468-1,151,744,918; 158 s, 21 units, 4 active
abilities): 38.1 ms of every second (124, 71, 62 before). No whole-HUD walk on a group. The cards 10 to 14 ms per
second from the start. The 31 whole-HUD walks left are the 5 s safety net (18 to 43 ms each, the worst UI tick 45 ms).

Battle B (archive\\logs\\battle_20261128_r217_perf2.txt, bytes 1,151,744,918-1,172,897,502; 437 s, 40 units, 37
active abilities, 153 accepted casts): 76.4 ms of every second. The UI timer 33.9 ms (cards 15.1, the test log sweeps
9.8, the walks 5.5). **The polls 42.5 ms** (6 to 7 in the small battles), 30 to 90 ms per second during the fight,
the worst poll 70 ms, 254 seconds with a poll over 16 ms. In those 437 s the test build wrote 63,096 log lines,
about 35,000 from inside the polls (MAP 14,356, RAW 7,193, the readiness and target lines), each flushed to disk.
The PERF line could not say how much of the poll time is the log, so no conclusion about the Workshop build's poll
cost is possible from battle B.

**Change (live copy only, the Workshop build is unchanged apart from inert bookkeeping lines):** log() adds its own
time and line count to cast_gate.log_ms / log_n while the probe is on. The poll notes the log time spent inside it and
times the read-only map probe apart. The PERF line ends with
` | log X ms N lines (in polls Y) | probe Z ms (its log W)`. tools\\analyze_perf.py prints the polls without the
probes and the log writes.

**Proof:** harness 216 full suite **8,594 checks / 0 failures** (once). RED on the pre-round snapshot: the PERF lines
carry no log part. The cast trace (2,229 worlds, 1,781 casts) matches between the test build and the release build
apart from the 3 probe casts. No rebased harness pin. Two tool rebases: build_release.py cuts log() to its new last
line, the builder's round-214 gate allows the three cast_gate.log_ fields inside the probe's block. No workbook.

**Limit of the method:** the release still BUILDS the text of the readiness and target lines before the empty log()
drops it. That cost stays in 'polls without the log writes', which is what the Workshop build pays.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.95 Round 218" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `72c2931c3cffc8860b2167f88af77d12`" + nl
            + "  (round 217, 2026-11-28, tuning: no whole-HUD walk for a group's unshared abilities, the unit cards 5 times a second from the start).",
            "- Installed build: md5 `95ebdc969775690fe5234cc33b91aa44`" + nl
            + "  (round 218, 2026-11-28, tuning, live copy only: the timing probe measures the test build's own log).")
    s = one(s, "20261128_groupcards_harness215/build_and_install217.py", "20261128_logcost_harness216/build_and_install218.py")
    s = one(s, "(harness215: 8,588 checks; it takes about 2 minutes)", "(harness216: 8,594 checks; it takes about 2 minutes)")
    a = "- ROUND 217 (2026-11-28, TUNING, TEST PACK INSTALLED: md5 72c2931c...)."
    note = [
        "- ROUND 218 (2026-11-28, TUNING, LIVE COPY ONLY, TEST PACK INSTALLED: md5 95ebdc96...). FIELD on round 217, two",
        "  battles. A (archive\\logs\\battle_20261128_r217_perf.txt, 158 s, 21 units): 38 ms OF EVERY SECOND, no group",
        "  walk, cards 10-14 ms/s. LEFT: the 5 s safety net = 31 whole-HUD walks of 18-43 ms (worst tick 45 ms):",
        "  proposed to the user (the net walks the dial, the whole HUD only while a selected unit waits), NOT BUILT, no",
        "  answer yet. B (archive\\logs\\battle_20261128_r217_perf2.txt, bytes 1,151,744,918-1,172,897,502, 437 s, 40",
        "  units, 37 active abilities, 153 accepted casts): 76 ms/s, THE POLLS 42.5 ms/s (30-90 in the fight, worst poll",
        "  70 ms) against 6-7 in the small battles. UNKNOWN how much is the test log: 63,096 lines in 437 s, about",
        "  35,000 inside the polls (MAP, RAW, readiness / target lines), each flushed. BUILT: log() times itself into",
        "  cast_gate.log_ms / log_n while cast_gate.log_on (set by FOURTH.perf_now), the poll keeps perf.poll_log, the",
        "  map probe perf.probe / probe_log, the PERF line ends ' | log X ms N lines (in polls Y) | probe Z ms (its log",
        "  W)'. tools\\analyze_perf.py prints 'POLLS WITHOUT THE PROBES AND THE LOG WRITES'. Harness 216: 8,594 / 0",
        "  (once), cast trace matches apart from the 3 probe casts. TOOL REBASES: build_release.py's log() tail, the",
        "  builder's round-214 gate (the three cast_gate.log_ fields allowed in the probe's block). NEXT: the user",
        "  repeats the big battle, then decide: if the real poll cost is high, find the expensive evaluators (a per-",
        "  family timer), else publish. The WORKSHOP ITEM STILL CARRIES ROUND 212. Next battle from byte 1,172,897,502",
        "  (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
