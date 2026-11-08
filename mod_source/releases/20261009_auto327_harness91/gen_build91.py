# -*- coding: utf-8 -*-
"""Patch WH3_mod/tools/build_and_install.py for the harness-91 round.

Moves the grown-table count gates (262->573 entries, melee_unwavering 216->477,
charge_or_melee 15->29, ushoran_health 5->41) and adds a full AUTO327 gate block
for the 311 new entries / 327 new keys. A backup + a release copy are written.
"""
import io, os, json, shutil, datetime

TOOLS = "C:/Users/vlady/Desktop/WH3_mod/tools/build_and_install.py"
HERE = os.path.dirname(os.path.abspath(__file__))
ENTRIES = json.load(io.open(os.path.join(HERE, "h91_entries.json"), encoding="utf-8"))
assert len(ENTRIES) == 311, len(ENTRIES)
assert sum(len(e["keys"]) for e in ENTRIES) == 327

s = io.open(TOOLS, encoding="utf-8", newline="").read()
assert "\r" not in s


def sub(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    s = s.replace(old, new, count)
    print("patch %s: applied" % label)


# ---- grown-table count gates
sub('assert script_txt.count(\'trigger = "melee_unwavering"\') == 216, \\\n'
    '    "the melee_unwavering entry count is not 216"',
    'assert script_txt.count(\'trigger = "melee_unwavering"\') == 477, \\\n'
    '    "the melee_unwavering entry count is not 477"',
    "melee_unwavering count")
sub('assert script_txt.count(\'trigger = "charge_or_melee"\') == 15, \\\n'
    '    "the charge_or_melee entry count is not 15"',
    'assert script_txt.count(\'trigger = "charge_or_melee"\') == 29, \\\n'
    '    "the charge_or_melee entry count is not 29"',
    "charge_or_melee count")
sub('assert script_txt.count("\\t{ marker = ") == 262, "the abilities table is not 262 entries"',
    'assert script_txt.count("\\t{ marker = ") == 573, "the abilities table is not 573 entries"',
    "entries count (402)", 2)
sub('assert script_txt.count(\'trigger = "ushoran_health"\') == 5, "the ushoran_health entry count is not 5"',
    'assert script_txt.count(\'trigger = "ushoran_health"\') == 41, "the ushoran_health entry count is not 41"',
    "ushoran_health count")

# ---- the AUTO327 gate block
lines = []
lines.append('')
lines.append('# ROUND v91: THE 327 AUTO-ACCEPTED ABILITIES - a BULK DATA APPEND riding the THREE')
lines.append('# EXISTING evaluators (no new trigger types). 311 new entries / 327 new keys;')
lines.append('# the table grows 262 -> 573 entries (272 -> 599 keys). The rows were derived')
lines.append('# programmatically from WH3_ability_tracker.md section 3a (every `approved')
lines.append('# (auto: <trigger>)` row). Base + DLC/summoned twin keys ride ONE entry; two')
lines.append('# NAME-collision entries take a name-derived marker (horn_of_vaul, whip_of_misery).')
lines.append('assert "THE 327 AUTO-ACCEPTED ABILITIES (this round)" in script_txt, "the auto-327 block header is missing"')
lines.append('assert "311 entries /" in script_txt and "327 database keys" in script_txt, "the auto-327 counts note is missing"')
lines.append('AUTO327 = [')
for e in ENTRIES:
    ks = ", ".join('"%s"' % k for k in e["keys"])
    lines.append('    ("%s", { %s }),' % (e["marker"], ks))
lines.append(']')
lines.append('assert len(AUTO327) == 311, "the auto-327 entry list is not 311"')
lines.append('_nk327 = 0')
lines.append('for _mk, _kys in AUTO327:')
lines.append('    assert \'marker = "%s"\' % _mk in script_txt, "auto-327 marker missing: " + _mk')
lines.append('    assert \'badge = "zz_auto_badge_%s"\' % _mk in script_txt, "auto-327 badge missing: " + _mk')
lines.append('    for _ky in _kys:')
lines.append('        assert \'"%s"\' % _ky in script_txt, "auto-327 key missing: " + _ky')
lines.append('        _nk327 = _nk327 + 1')
lines.append('assert _nk327 == 327, "the auto-327 key count is not 327 (got %d)" % _nk327')
lines.append('')
block = "\n".join(lines)

ANCHOR = 'assert _nk789 == 73, "the block-7-9 key count is not 73 (got %d)" % _nk789\n'
assert s.count(ANCHOR) == 1, "block789 anchor"
s = s.replace(ANCHOR, ANCHOR + block, 1)
print("patch AUTO327 block: applied")

# ---- back up the current build script, then write
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(TOOLS, TOOLS + ".bak_%s_pre_v91" % stamp)
io.open(TOOLS, "w", encoding="utf-8", newline="").write(s)
io.open(os.path.join(HERE, "build_and_install91.py"), "w", encoding="utf-8", newline="").write(s)
print("build_and_install.py updated (%d bytes); release copy written" % len(s))
print("backup:", TOOLS + ".bak_%s_pre_v91" % stamp)
