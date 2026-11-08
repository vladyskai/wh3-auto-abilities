"""Build harness105.lua from harness104.lua: rename the env pair, re-pin the
table-size counts this round's new entry moves, and splice the Tz'arkan section
before the final find check. Older harnesses are never edited.
"""
import os
import re

T = os.path.expandvars(r"%LOCALAPPDATA%\Temp")
SRC = os.path.join(T, "harness104.lua")
DST = os.path.join(T, "harness105.lua")
SECTION = os.path.join(T, "harness105_section.lua")

s = open(SRC, encoding="utf-8").read()
orig = s

# ---------------------------------------------------------------- env pair
assert s.count("H104_LIVE") == 8 and s.count("H104_ANN") == 8
s = s.replace("H104_LIVE", "H105_LIVE").replace("H104_ANN", "H105_ANN")

# ---------------------------------------------------------------- pins
EXACT = [
    ("a = (it == 1284)", "a = (it == 1286)", 1),
    ("b = ((it / 2) == 642)", "b = ((it / 2) == 643)", 1),
    ('check(TAG .. "A4b: 642 abilities per pass', 'check(TAG .. "A4b: 643 abilities per pass', 1),
    ('.. it .. " iterations, 642 per pass - ROUND h92 grew the table again)"',
     '.. it .. " iterations, 643 per pass - ROUND h105 grew the table again)"', 1),
    ('"A4a: with no information the badge paths walked the FULL 642-entry table ("',
     '"A4a: with no information the badge paths walked the FULL 643-entry table ("', 1),
    ("a = (POLL_ITERS == 642)", "a = (POLL_ITERS == 643)", 1),
    ('.. ", want 642 - the FULL 642-entry table after round h92)"',
     '.. ", want 643 - the FULL 643-entry table after round h105)"', 1),
    ("(ABIL and #ABIL or -1) .. \" entries)\", ABIL ~= nil and #ABIL == 642)",
     "(ABIL and #ABIL or -1) .. \" entries)\", ABIL ~= nil and #ABIL == 643)", 1),
    ("MK ~= nil and n_mk == 682)", "MK ~= nil and n_mk == 687)", 1),
    ("AKEYS == nil or #AKEYS == 682)", "AKEYS == nil or #AKEYS == 687)", 1),
    ('.. ", table of 642 after round h92)", ABIL ~= nil and wired_n == 642 and total == 642)',
     '.. ", table of 643 after round h105)", ABIL ~= nil and wired_n == 643 and total == 643)', 1),
    ("wired_n == 642 and two and four", "wired_n == 643 and two and four", 1),
    ("(n_e == 642) and (n_k == 682)", "(n_e == 643) and (n_k == 687)", 3),
    ("n_e == 642)", "n_e == 643)", 3),
    ("n_k == 682)", "n_k == 687)", 3),
    ("EXP = { entries = 642, keys = 682,", "EXP = { entries = 643, keys = 687,", 3),
    ("nkeys == 136", "nkeys == 141", 1),
    ('": the cast-gate table exists and lists all 136 wind-up keys ("',
     '": the cast-gate table exists and lists all 141 wind-up keys ("', 1),
    ("total == 642)", "total == 643)", 5),
]
for old, new, want in EXACT:
    got = s.count(old)
    assert got == want, "pin %r found %d times, want %d" % (old[:60], got, want)
    s = s.replace(old, new)

# the 0o/0p/0r/0s/0t/0u/0v/0w/0c label lines and the cp*(...) assertions
LABELS = [
    "the grown table is 642 entries",
    "the table stays 642 entries / 642 badges",
    "the ability table is UNCHANGED (642 entries)",
    "the whole 642-entry table and the 70% rule are untouched",
    "the table is still 642 entries",
]
changed = 0
out = []
for line in s.split("\n"):
    if any(lab in line for lab in LABELS):
        line = line.replace("642", "643")
        changed += 1
    out.append(line)
s = "\n".join(out)
print("  label lines re-pinned:", changed)

# the per-file cp*(...) count assertions (the lines carrying a cp helper)
out = []
changed = 0
for line in s.split("\n"):
    if ("cp95(s, " in line or "cp96(s, " in line or "cp97(s, " in line or "cp98(s, "
            or "cp99(s, " in line or "cp104(s, " in line or "cp(s, " in line) and "== 642" in line:
        line = line.replace("== 642", "== 643")
        changed += 1
    out.append(line)
s = "\n".join(out)
print("  cp assertion lines re-pinned:", changed)

# the tooltip wording table gains the new trigger's sentence
anchor = ('    health_aura_self = "When armed, fires when this unit or a friendly unit in its aura '
          'is at or below 75% health, cast on itself",\n')
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + '    health_below_15 = "When armed, fires when this unit is below 15% health",\n')

# ---------------------------------------------------------------- the section
sec = open(SECTION, encoding="utf-8").read()
tail = '\n\n\n\n\ncheck("ZERO search calls by the mod across everything'
assert s.count(tail) == 1, "final anchor not unique"
s = s.replace(tail, "\n" + sec + tail)

# the previous suite's green total is INLINED: this chunk sits at Lua's 200-local
# ceiling, so the section must add ZERO chunk locals (a global function only).
assert s.count('ZERO search calls by the mod across everything, harness 71 to 100 AND 101-102') == 1
assert s.count("local function run_h105()") == 0
assert s.count("function run_h105()") == 1

open(DST, "wb").write(s.encode("utf-8"))
print("wrote", DST, len(s.encode("utf-8")), "bytes (from", len(orig.encode("utf-8")), ")")
print("changed lines:", sum(1 for a, b in zip(orig.split("\n"), s.split("\n")) if a != b))
