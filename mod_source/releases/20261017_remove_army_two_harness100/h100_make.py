# -*- coding: utf-8 -*-
"""HARNESS 100 build: assemble harness100.lua from the SHIPPED harness99.lua.

Round-100 job: Meat Feast (`wh3_main_prisoners_butcher`) and Massacre
(`wh3_main_prisoners_massacre`) are REMOVED from the mod. Both were implemented
but sit OUTSIDE the single in-wheel rule (source_type = army). The removal moves
the pins DOWN by exactly two entries / two keys and by one trigger each:

    entries            579 -> 577
    keys               605 -> 603
    melee_unwavering   363 -> 362   (Massacre removed)
    ushoran_health      34 ->  33   (Meat Feast removed; Gulyas stays)

Every pin that still names 579 / 605 / 363 / 34 as the CURRENT table is re-based
here and documented in the printed substitution log. Historical comments that
describe an EARLIER round's table size (573 -> 579, the harness-92 snapshot, the
harness-93 snapshot) are left untouched - they are history, not pins.

A new section 0x + the removal/red-control checks are appended after run_h99().
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)

def read(p):
    return io.open(p, encoding="utf-8", newline="").read()

def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)

src = read(HERE + "/../20261015_classgated_harness99/harness99.lua")

# Lines that describe an EARLIER round's table size (history, never a pin).
HIST_579 = {9125, 9127, 9129, 11269, 11603, 12005, 12141, 12462, 12805, 12841, 12986, 13318}
HIST_605 = {12005, 12462, 12805, 12986, 13318}
HIST_34 = {14167}  # "the audit's Class B (34 entries)" - history, not a pin

lines = src.split(NL)
n_579 = n_605 = n_363 = n_34 = 0
for i, line in enumerate(lines, 1):
    if i not in HIST_579 and re.search(r"(?<!\d)579(?!\d)", line):
        n_579 += len(re.findall(r"(?<!\d)579(?!\d)", line))
        line = re.sub(r"(?<!\d)579(?!\d)", "577", line)
    if i not in HIST_605 and re.search(r"(?<!\d)605(?!\d)", line):
        n_605 += len(re.findall(r"(?<!\d)605(?!\d)", line))
        line = re.sub(r"(?<!\d)605(?!\d)", "603", line)
    if re.search(r"(?<!\d)363(?!\d)", line):
        n_363 += len(re.findall(r"(?<!\d)363(?!\d)", line))
        line = re.sub(r"(?<!\d)363(?!\d)", "362", line)
    if i not in HIST_34 and re.search(r"(?<!\d)34(?!\d)", line):
        n_34 += len(re.findall(r"(?<!\d)34(?!\d)", line))
        line = re.sub(r"(?<!\d)34(?!\d)", "33", line)
    lines[i - 1] = line
print("re-based tokens: 579 x%d, 605 x%d, 363 x%d, 34 x%d" % (n_579, n_605, n_363, n_34))
src = NL.join(lines)

def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied (%d)" % (label, count))

# ---------------------------------------------------------------- env pair
sub('-- HARNESS 99 (this round): the env pair is now H99_LIVE / H99_ANN.',
    '-- HARNESS 100 (this round): the env pair is now H100_LIVE / H100_ANN.',
    "env comment")
sub('local LIVE = os.getenv("H99_LIVE")', 'local LIVE = os.getenv("H100_LIVE")', "env LIVE")
sub('local ANN  = os.getenv("H99_ANN")', 'local ANN  = os.getenv("H100_ANN")', "env ANN")
sub('local RED_MODE = (os.getenv("H99_LIVE") ~= nil) or (os.getenv("H99_ANN") ~= nil)',
    'local RED_MODE = (os.getenv("H100_LIVE") ~= nil) or (os.getenv("H100_ANN") ~= nil)',
    "env RED_MODE")

# ---------------------------------------------------------------- banner
sub('  print("   *** fails; the SILENT worlds pass by design.***")',
    NL.join(['  print("   *** fails; the SILENT worlds pass by design.***")',
             '  print("   *** REMOVAL (harness 100): the pre-edit snapshot still CARRIES Meat Feast and Massacre")',
             '  print("   *** (579 entries / 605 keys), so every 0x removal check is GREEN-only and flips RED there.***")']),
    "banner")

# ---------------------------------------------------------------- tail token list
sub("94, 95, 96, 97 AND 98's worlds included", "94, 95, 96, 97, 98 AND 99's worlds included", "tail list")

# ---------------------------------------------------------------- h99 red branch
# The harness-100 red snapshot (pre100) is POST-99: it carries every
# target-class-gated entry, so h99's 26/56 expectation is history. Match the
# project's own "N/A for a later round" pattern instead of failing an
# inapplicable red control.
OLD_RED99 = ('    check("RED CONTROL (harness 99): on the pre-edit snapshot every FIRE world fails (the snapshot self-casts or stays "\n'
             '      .. "silent - never on an ally) while the SILENT worlds pass by design. "\n'
             '      .. n_ok .. "/" .. #results .. " world results pass (want " .. WANT_RED_99 .. "), fires " .. RED99.fires\n'
             '      .. ", claims " .. RED99.claims, n_ok == WANT_RED_99)')
NEW_RED99 = ('    check("RED CONTROL (harness 99): N/A for the harness-100 round - the harness-100 red snapshot IS the "\n'
             '      .. "shipped harness-99 build, so it already carries every target-class-gated entry and all "\n'
             '      .. #results .. " world results pass by design. The removal red control lives in harness 100.", n_ok == #results)')
sub(OLD_RED99, NEW_RED99, "h99 red branch")

# ---------------------------------------------------------------- A4a iteration pin
sub("    a = (it == 1158)", "    a = (it == 1154)", "A4a iterations 2x579 -> 2x577")

# ---------------------------------------------------------------- append section
section = read(HERE + "/h100_section.lua").lstrip(NL)
sub(NL + "run_h99()" + NL, NL + "run_h99()" + NL + NL + section + NL, "append section")

write(HERE + "/harness100.lua", src)
print("wrote harness100.lua", len(src), "bytes")
