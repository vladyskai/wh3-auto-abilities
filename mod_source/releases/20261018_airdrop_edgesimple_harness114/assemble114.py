#!/usr/bin/env python3
"""Assemble harness114.lua from harness113.lua.

* renames nothing (harness 113's section is REMOVED wholesale: its whole subject -
  the path/frontage/single-entity design - was deleted by round 114, so the base
  suite is the harness-112 suite exactly: 4492 checks);
* teaches the mock the round's two new shapes: a NAME-KEYED repeat_callback (so
  polln() still drives the POLL and a new fastn() drives the fast pass) and a
  RAISING unit_distance (the fail-closed world);
* rebases the ~20 static "one poll + one ui registration" pins to 2 + 1;
* splices the round-114 section before the final summary.
"""
import io, sys

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261025_airdrop_pathtest_harness113\harness113.lua"
SEC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_edgesimple_harness114\h114_section.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_edgesimple_harness114\harness114.lua"


def rd(p):
    with open(p, "rb") as f:
        b = f.read()
    return b.decode("utf-8")


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "replace %r matched %d (want %d)" % (old[:60], n, count)
    return s.replace(old, new)


s = rd(SRC)

# ---- 1. CUT THE HARNESS-113 SECTION ---------------------------------------
mark = s.index("-- HARNESS 113 - THE PATH TEST, THE DERIVED FRONTAGE")
i = s.rindex("-- ============================================================================", 0, mark)
head = s[:i]
tail_marker = "run_h112()\nrun_h113()\n"
j = s.index(tail_marker)
tail = s[j + len("run_h112()\nrun_h113()\n"):]
assert head.rstrip().endswith("run_h111()"), head[-80:]

# ---- 2. THE MOCK: a NAME-KEYED repeat_callback ----------------------------
s = head + tail
s = must(s, """  function bm:repeat_callback(fn, ms, name)
    W.timer_regs = W.timer_regs + 1
    W.poll_fn = fn; W.poll_ms, W.poll_name = ms, name
  end""", """  function bm:repeat_callback(fn, ms, name)
    -- ROUND 114: the mod now registers TWO model timers - the global poll and
    -- the air-drop fast pass - so the mock keys them by NAME. polln() drives
    -- W.poll_fn (the poll) and fastn() drives W.fast_fn (the fast pass), exactly
    -- as the engine drives both.
    W.timer_regs = W.timer_regs + 1
    if name == "zz_test_deadly_onslaught_poll" then
      W.poll_fn = fn; W.poll_ms, W.poll_name = ms, name
    else
      W.fast_fn = fn; W.fast_ms, W.fast_name = ms, name
    end
  end""")

# ---- 3. THE MOCK: a RAISING unit_distance ---------------------------------
s = must(s, """    function u:unit_distance(o)
      touch()""", """    function u:unit_distance(o)
      touch()
      -- ROUND 114: def.dist_raises models a read the engine cannot answer; the
      -- mod's FOURTH.eg_enemy_gap pcalls it, so the candidate is NOT valid.
      if def.dist_raises then error("mock: unit_distance refused", 0) end""")

# ---- 4. REBASE THE TIMER-COUNT PINS ---------------------------------------
s = must(s, "timers_a == 1 and timers_b == 1", "timers_a == 2 and timers_b == 1", 9)
s = must(s, "ta == 1 and tb == 1", "ta == 2 and tb == 1")
s = must(s, 'count_plain(s, "bm:repeat_callback(") == 1',
         'count_plain(s, "bm:repeat_callback(") == 2', 6)
s = must(s, "ALL_TIMERS == 2 * ALL_WORLDS", "ALL_TIMERS == 3 * ALL_WORLDS")
s = must(s, "no new timers: exactly the poll and the ui tick registrations",
         "timers (round 114 adds the air-drop fast pass): the poll + the fast pass + the ui tick", 7)
s = must(s, "no new timers: still one poll + one ui registration",
         "timers: still the poll + the fast pass + the ui registration", 5)
s = must(s, "no new timers (one poll + one ui registration in each file)",
         "timers (round 114): the poll + the fast pass + the ui registration in each file")
s = must(s, "no new timers, anywhere: exactly 2 registrations per load (poll + ui), total ",
         "timers, anywhere: exactly 3 registrations per load (poll + fast pass + ui), total ")
s = must(s, "no new timers (bm:repeat_callback == 1, bm:repeat_real_callback == 1)",
         "timers (bm:repeat_callback == 2, bm:repeat_real_callback == 1)")

# ---- 5. THE SEAM ----------------------------------------------------------
old_tail = "\nprint(\"checks: \""
assert s.count(old_tail) == 1, s.count(old_tail)
sec = rd(SEC)
s = s.replace(old_tail, "\n" + sec + "\nrun_h112()\nrun_h114()\n\nprint(\"checks: \"")

_POST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_edgesimple_harness114\post114.py"
exec(compile(open(_POST, encoding="utf-8").read(), _POST, "exec"))

with open(OUT, "wb") as f:
    f.write(s.encode("utf-8"))
print("wrote %s  %d bytes  %d lines  checks-in-file %d" %
      (OUT, len(s.encode("utf-8")), s.count("\n") + 1, s.count("check(")))
