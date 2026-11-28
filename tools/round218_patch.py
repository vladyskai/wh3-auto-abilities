#!/usr/bin/env python3
"""Round 218 (2026-11-28, tuning, LIVE COPY ONLY: the timing probe learns what the test build's own log costs).
No cast decision changes, nothing changes in the Workshop build (it has no log and no probe).

FIELD (the round-217 build, archive/logs/battle_20261128_r217_perf2.txt, 437 s, 40 units, 37 active abilities): the
polls took 42.5 ms of every second (6 to 7 in the 21-unit battles), the worst poll 70 ms. In those 437 s the test
build wrote 63,096 log lines, about 35,000 of them from inside the polls (MAP 14,356, RAW 7,193, readiness / target
lines), each one flushed to disk. The PERF line could not say how much of the poll time is the log.

1. log() adds its own time and line count to cast_gate.log_ms / log_n while the probe is on (cast_gate.log_on).
2. The poll notes the log time spent inside it (perf.poll_log) and times the read-only map probe apart
   (perf.probe, perf.probe_log).
3. The PERF line ends with ' | log X ms N lines (in polls Y) | probe Z ms (its log W)'.
   The Workshop build's poll cost = poll - probe - (in polls - its log).
Backup: docs/backups/round218/pre218_live.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round218"

EDITS = [
    ("log head",
     "local function log(message)\n\tlocal line = LOG_TAG .. tostring(message)\n",
     "local function log(message)\n"
     "\tlocal log_t0 = nil   -- ROUND 218: the timing probe measures the log itself\n"
     "\tif cast_gate.log_on == true then log_t0 = os.clock() end\n"
     "\tlocal line = LOG_TAG .. tostring(message)\n"),
    ("log tail",
     "\tout(line)\nend\n",
     "\tout(line)\n"
     "\tif log_t0 ~= nil then\n"
     "\t\tcast_gate.log_ms = (cast_gate.log_ms or 0) + (os.clock() - log_t0) * 1000\n"
     "\t\tcast_gate.log_n = (cast_gate.log_n or 0) + 1\n"
     "\tend\n"
     "end\n"),
    ("probe",
     "\tpcall(FOURTH.map_tick, tick_count)\n",
     "\tFOURTH.perf_probe0 = FOURTH.perf_now()   -- ROUND 218: the read-only probes, timed apart\n"
     "\tFOURTH.perf_probe_log0 = cast_gate.log_ms or 0\n"
     "\tpcall(FOURTH.map_tick, tick_count)\n"
     "\tif FOURTH.perf_probe0 ~= nil then\n"
     "\t\tFOURTH.perf.probe = FOURTH.perf.probe + (os.clock() - FOURTH.perf_probe0) * 1000\n"
     "\t\tFOURTH.perf.probe_log = FOURTH.perf.probe_log + ((cast_gate.log_ms or 0) - FOURTH.perf_probe_log0)\n"
     "\tend\n"),
    ("perf table",
     "\tpoll = 0, poll_max = 0, polls = 0 }\n",
     "\tpoll = 0, poll_max = 0, polls = 0, poll_log = 0, probe = 0, probe_log = 0 }\n"),
    ("perf_now",
     "\tif type(os) ~= \"table\" or type(os.clock) ~= \"function\" then return nil end\n\treturn os.clock()\nend\n",
     "\tif type(os) ~= \"table\" or type(os.clock) ~= \"function\" then return nil end\n"
     "\tcast_gate.log_on = true   -- ROUND 218\n"
     "\treturn os.clock()\nend\n"),
    ("poll",
     "\tlocal perf_p0 = FOURTH.perf_now()   -- ROUND 214\n\tlocal ok, err = pcall(poll_body)\n"
     "\tFOURTH.perf_add(\"poll\", perf_p0)   -- ROUND 214\n",
     "\tlocal perf_p0 = FOURTH.perf_now()   -- ROUND 214\n"
     "\tlocal perf_l0 = cast_gate.log_ms or 0   -- ROUND 218\n"
     "\tlocal ok, err = pcall(poll_body)\n"
     "\tFOURTH.perf_add(\"poll\", perf_p0)   -- ROUND 214\n"
     "\tif perf_p0 ~= nil then FOURTH.perf.poll_log = FOURTH.perf.poll_log + ((cast_gate.log_ms or 0) - perf_l0) end\n"),
    ("line",
     "\t\t.. \"| badges %.1f ms | diag %.1f ms | poll %dx %.1f ms (worst %.1f)\", p.ticks, p.ui, p.ui_max, p.walks, p.walk,\n"
     "\t\tp.cards, p.select, p.badges, p.diag, p.polls, p.poll, p.poll_max))\n",
     "\t\t.. \"| badges %.1f ms | diag %.1f ms | poll %dx %.1f ms (worst %.1f)\"\n"
     "\t\t.. \" | log %.1f ms %d lines (in polls %.1f) | probe %.1f ms (its log %.1f)\", p.ticks, p.ui, p.ui_max, p.walks, p.walk,\n"
     "\t\tp.cards, p.select, p.badges, p.diag, p.polls, p.poll, p.poll_max,\n"
     "\t\tcast_gate.log_ms or 0, cast_gate.log_n or 0, p.poll_log, p.probe, p.probe_log))\n"
     "\tcast_gate.log_ms, cast_gate.log_n = 0, 0\n"
     "\tp.poll_log, p.probe, p.probe_log = 0, 0, 0\n"),
]


def main():
    os.makedirs(BK, exist_ok=True)
    dst = os.path.join(BK, "pre218_live.lua")
    if not os.path.exists(dst):
        shutil.copy2(LIVE, dst)
    elif "--again" in sys.argv:
        shutil.copy2(dst, LIVE)
    s = open(LIVE, encoding="utf-8", newline="").read()
    assert "ROUND 218" not in s, "already patched"
    for what, a, b in EDITS:
        assert s.count(a) == 1, (what, s.count(a))
        s = s.replace(a, b)
    open(LIVE, "w", encoding="utf-8", newline="").write(s)
    print("patched", LIVE)


if __name__ == "__main__":
    main()
