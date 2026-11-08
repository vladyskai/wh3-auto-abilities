# -*- coding: utf-8 -*-
"""Patch WH3_mod/tools/build_and_install.py for the FINAL ROSTER round (harness 92).

Moves the grown-table count gates (melee_unwavering 477 -> 481, abilities table
573 -> 579 entries) and adds a full FINAL ROSTER gate block for the 6 new
entries / 6 new keys. A backup + a release copy are written.
"""
import io, os, shutil, datetime

TOOLS = "C:/Users/vlady/Desktop/WH3_mod/tools/build_and_install.py"
HERE = os.path.dirname(os.path.abspath(__file__))

s = io.open(TOOLS, encoding="utf-8", newline="").read()
assert "\r" not in s


def sub(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    s = s.replace(old, new, count)
    print("patch %s: applied" % label)


# ---- grown-table count gates
sub('assert script_txt.count(\'trigger = "melee_unwavering"\') == 477, \\\n'
    '    "the melee_unwavering entry count is not 477"',
    'assert script_txt.count(\'trigger = "melee_unwavering"\') == 481, \\\n'
    '    "the melee_unwavering entry count is not 481"',
    "melee_unwavering count")
sub('assert script_txt.count("\\t{ marker = ") == 573, "the abilities table is not 573 entries"',
    'assert script_txt.count("\\t{ marker = ") == 579, "the abilities table is not 579 entries"',
    "entries count (573->579)", 2)

# ---- the FINAL ROSTER gate block, appended after the auto-327 key-count assert
lines = []
lines.append('')
lines.append('# ROUND v92: THE FINAL ROSTER BUILD - the SIX built individual abilities from')
lines.append('# the remaining-abilities triage (WH3_remaining_triage.md section 3 INDIVIDUAL')
lines.append('# table). TWO NEW ally-heal triggers, each its OWN evaluator: blood_sacrifice')
lines.append('# (cast on the lowest-health ally in range at or below 75%) and eat_da_runts')
lines.append('# (cast on self at or below 75%, ELSE the lowest-health ally in range). FOUR')
lines.append('# further entries ride the EXISTING shared melee_unwavering evaluator (in-melee')
lines.append('# self): Locus of Virulence, The Dance of Dreaming, The Waltz of Lethargy,')
lines.append('# Ultimate Verdict. Each new trigger casts on the CHOSEN ALLY, uses a')
lines.append('# conservative named 25 m range constant, and RE-CHECKS the gap and the ally\'s')
lines.append('# health before the cast (skip on drift). The table grows 573 -> 579 entries')
lines.append('# (599 -> 605 keys); melee_unwavering 477 -> 481. NO new chunk locals (the')
lines.append('# constant and state ride the FOURTH helper bag).')
lines.append('assert "THE FINAL ROSTER ROUND (this round)" in script_txt, "the final-roster block header is missing"')
lines.append('assert "function FOURTH.evaluate_blood_sacrifice(unit, routing)" in script_txt, "the blood-sacrifice evaluator is missing"')
lines.append('assert "function FOURTH.evaluate_eat_da_runts(unit, routing)" in script_txt, "the eat-da-runts evaluator is missing"')
lines.append('assert "function FOURTH.bs_ally_valid(unit, ally)" in script_txt, "the blood-sacrifice validity helper is missing"')
lines.append('assert "function FOURTH.edr_ally_valid(unit, ally)" in script_txt, "the eat-da-runts validity helper is missing"')
lines.append('assert "FOURTH.BLOOD_SACRIFICE_RANGE_M = 25" in script_txt, "the blood-sacrifice range constant is missing"')
lines.append('assert "FOURTH.EAT_DA_RUNTS_RANGE_M = 25" in script_txt, "the eat-da-runts range constant is missing"')
lines.append('assert "blood_sacrifice = FOURTH.evaluate_blood_sacrifice," in script_txt, "the blood-sacrifice map entry is missing"')
lines.append('assert "eat_da_runts = FOURTH.evaluate_eat_da_runts," in script_txt, "the eat-da-runts map entry is missing"')
lines.append('assert "blood_sacrifice SKIPPED:" in script_txt, "the blood-sacrifice drift skip is missing"')
lines.append('assert "eat_da_runts SKIPPED:" in script_txt, "the eat-da-runts drift skip is missing"')
lines.append('assert \'string.format("blood sacrifice: lowest-health ally %d%% (<= 75%%), cast on ally"\' in script_txt, "the blood-sacrifice reason is missing"')
lines.append('assert \'string.format("eat da runts: self health %d%% (<= 75%%), cast on self"\' in script_txt, "the eat-da-runts self reason is missing"')
lines.append('assert script_txt.count(\'trigger = "blood_sacrifice"\') == 1, "the blood_sacrifice entry count is not 1"')
lines.append('assert script_txt.count(\'trigger = "eat_da_runts"\') == 1, "the eat_da_runts entry count is not 1"')
lines.append('assert script_txt.count("FOURTH.bs_ally = nil") == 3, "the bs_ally clears are not exactly three"')
lines.append('assert script_txt.count("FOURTH.edr_ally = nil") == 3, "the edr_ally clears are not exactly three"')
lines.append('FINAL6 = [')
for marker, key in (("blood_sacrifice", "wh3_dlc26_lord_abilities_blood_sacrifice"),
                    ("eat_da_runts", "wh3_dlc26_unit_abilities_eat_da_runts"),
                    ("locus_of_virulence", "wh3_main_character_abilities_locus_of_virulence"),
                    ("the_dance_of_dreaming", "wh3_dlc27_lord_abilities_the_dance_of_dreaming"),
                    ("the_waltz_of_lethargy", "wh3_dlc27_lord_abilities_the_waltz_of_lethargy"),
                    ("ultimate_verdict", "wh3_cp1_character_abilities_terrifying_presence")):
    lines.append('    ("%s", "%s"),' % (marker, key))
lines.append(']')
lines.append('assert len(FINAL6) == 6, "the final-roster entry list is not 6"')
lines.append('assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"')
lines.append('_nk92 = 0')
lines.append('for _mk, _ky in FINAL6:')
lines.append('    assert \'marker = "%s"\' % _mk in script_txt, "final-roster marker missing: " + _mk')
lines.append('    assert \'badge = "zz_auto_badge_%s"\' % _mk in script_txt, "final-roster badge missing: " + _mk')
lines.append('    assert \'"%s"\' % _ky in script_txt, "final-roster key missing: " + _ky')
lines.append('    _nk92 = _nk92 + 1')
lines.append('assert _nk92 == 6, "the final-roster key count is not 6 (got %d)" % _nk92')
lines.append('')
block = "\n".join(lines)

ANCHOR = 'assert _nk327 == 327, "the auto-327 key count is not 327 (got %d)" % _nk327\n'
assert s.count(ANCHOR) == 1, "auto-327 tail anchor"
s = s.replace(ANCHOR, ANCHOR + block, 1)
print("patch FINAL ROSTER block: applied")

# ---- back up the current build script, then write
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(TOOLS, TOOLS + ".bak_%s_pre_v92" % stamp)
io.open(TOOLS, "w", encoding="utf-8", newline="").write(s)
io.open(os.path.join(HERE, "build_and_install92.py"), "w", encoding="utf-8", newline="").write(s)
print("build_and_install.py updated (%d bytes); release copy written" % len(s))
print("backup:", TOOLS + ".bak_%s_pre_v92" % stamp)
