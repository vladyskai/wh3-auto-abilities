# -*- coding: utf-8 -*-
"""Generate build_and_install95.py from the shipped build_and_install94.py.

Changes: the v95 docstring note; the moved range-constant asserts (GD 25->38,
VM/MT/WV 25->24, BS/EDR 25->70, ACC 75->52); and a new block asserting the
standing 70% range rule (FOURTH.RANGE_FRACTION + every derived constant + the
charge-window pair left alone). The build/pack/install machinery is unchanged.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)
src = io.open(os.path.join(HERE, "build_and_install94_base.py"),
              encoding="utf-8", newline="").read()


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# docstring: insert the v95 note just before the closing triple-quote
OLD_TAIL = "579 entries / 605 keys." + NL + '"""'
NEW_TAIL = ("579 entries / 605 keys." + NL
            + NL
            + "ROUND v95: THE STANDING 70% RANGE RULE (set by the user, ruled ABSOLUTE -" + NL
            + '\\"...No exceptions.\\"). EVERY trigger-range constant is re-derived as' + NL
            + "floor(0.70 * the ability's REAL game-data range): GLORIOUS DEATH 55->38," + NL
            + "VERMINKING / METALLURGY / WAVERING 35->24, BLOOD SACRIFICE / EAT DA RUNTS" + NL
            + "100->70 (target_intercept_range; no aura) and ACCUSATION 75->52. The old" + NL
            + "field-tuned 25 m Glorious Death gate is replaced by 38 m at the user's" + NL
            + "direction. The rule ships as FOURTH.RANGE_FRACTION = 0.70." + NL
            + '"""')
sub(OLD_TAIL, NEW_TAIL, "docstring")

sub('assert "local GLORIOUS_DEATH_RANGE_M = 25" in script_txt, "the tightened range constant is missing"',
    'assert "local GLORIOUS_DEATH_RANGE_M = 38" in script_txt, "the 70% Glorious Death range constant is missing"',
    "GD pin")
sub('assert "FOURTH.VERMINKING_RANGE_M = 25" in script_txt, "the Verminking range constant is missing"',
    'assert "FOURTH.VERMINKING_RANGE_M = 24" in script_txt, "the 70% Verminking range constant is missing"',
    "VM pin")
sub('assert "FOURTH.METALLURGY_RANGE_M = 25" in script_txt, "the metallurgy range constant is missing"',
    'assert "FOURTH.METALLURGY_RANGE_M = 24" in script_txt, "the 70% metallurgy range constant is missing"',
    "MT pin")
sub('assert "FOURTH.WAVERING_RANGE_M = 25" in script_txt, "the wavering range constant is missing"',
    'assert "FOURTH.WAVERING_RANGE_M = 24" in script_txt, "the 70% wavering range constant is missing"',
    "WV pin")
sub('assert "FOURTH.BLOOD_SACRIFICE_RANGE_M = 25" in script_txt, "the blood-sacrifice range constant is missing"',
    'assert "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70" in script_txt, "the 70% blood-sacrifice range constant is missing"',
    "BS pin")
sub('assert "FOURTH.EAT_DA_RUNTS_RANGE_M = 25" in script_txt, "the eat-da-runts range constant is missing"',
    'assert "FOURTH.EAT_DA_RUNTS_RANGE_M = 70" in script_txt, "the 70% eat-da-runts range constant is missing"',
    "EDR pin")
sub("assert 'FOURTH.ACCUSATION_RANGE_M = 75' in script_txt, \"the accusation range constant is missing\"",
    "assert 'FOURTH.ACCUSATION_RANGE_M = 52' in script_txt, \"the 70% accusation range constant is missing\"",
    "ACC pin")

# wording tokens in the h87/h88/h90 blocks that no longer appear (comment moved)
sub('assert "DELIBERATELY CONSERVATIVE" in script_txt, "the conservative-trigger comment is missing"',
    'assert "THE STANDING 70% RULE" in script_txt, "the standing-70%-rule comment is missing"',
    "conservative->rule comment token", count=3)
sub('assert "Effect range: 55m" in script_txt, "the wiki-sourced range reference comment is missing"',
    'assert "55 * 0.70 = 38.5 -> 38" in script_txt, "the Glorious Death 70%% derivation comment is missing"',
    "GD derivation token")
sub('assert "effect_range =" in script_txt, "the game-data range source note is missing"',
    'assert "35.0000 m = effect_range" in script_txt, "the game-data range source note is missing"',
    "VM source-note token")
# the stale v87 comment block (states the constant reads 25)
sub("# Glorious Death trigger range is tightened from the ability's 55 m wiki aura to" + NL
    + "# a DELIBERATELY CONSERVATIVE 25 m (the user's field test showed 55 m fired too" + NL
    + "# early). The single settings constant GLORIOUS_DEATH_RANGE_M now reads 25; the" + NL
    + '# wiki\'s real "Effect range: 55m" stays in the comment for reference. The gate',
    "# Glorious Death trigger range is the STANDING 70% RULE value: floor(0.70 x the" + NL
    + "# ability's 55 m game-data aura) = 38 m. The user ruled the rule ABSOLUTE, so the" + NL
    + "# old field-tuned 25 m gate is gone. The gate",
    "GD comment block")

# the new standing-rule assert block (inserted right before the table-count assert)
ANCHOR = ('assert "is_firing" not in script_txt and "is_shooting" not in script_txt, \\\n'
          '    "an invented firing predicate is in the mod"\n'
          'assert script_txt.count("\\t{ marker = ") == 579, "the abilities table is not 579 entries"')
NEW = (
"# ---------------------------------------------------------------------------\n"
"# ROUND v95: THE STANDING 70% RANGE RULE (the user ruled it ABSOLUTE -\n"
"# \"...No exceptions.\"). Every trigger-range constant == floor(real * 0.70),\n"
"# where real is the ability's own game-data range (unit_spec_abil.tsv\n"
"# effect_range for an aura, else target_intercept_range).\n"
"# ---------------------------------------------------------------------------\n"
"assert \"FOURTH.RANGE_FRACTION = 0.70\" in script_txt, \"the standing range-rule constant is missing\"\n"
"_RULE95 = ((\"local GLORIOUS_DEATH_RANGE_M\", 55, 38),\n"
"           (\"FOURTH.VERMINKING_RANGE_M\", 35, 24),\n"
"           (\"FOURTH.METALLURGY_RANGE_M\", 35, 24),\n"
"           (\"FOURTH.WAVERING_RANGE_M\", 35, 24),\n"
"           (\"FOURTH.BLOOD_SACRIFICE_RANGE_M\", 100, 70),\n"
"           (\"FOURTH.EAT_DA_RUNTS_RANGE_M\", 100, 70),\n"
"           (\"FOURTH.ACCUSATION_RANGE_M\", 75, 52))\n"
"for _tok, _real, _want in _RULE95:\n"
"    assert int(_real * 0.70 + 1e-9) == _want, \"the documented 70%% target is wrong for \" + _tok\n"
"    assert (\"%s = %d\" % (_tok, _want)) in script_txt, \"the 70%% range constant is missing: \" + _tok\n"
"for _old_zero in (\"local GLORIOUS_DEATH_RANGE_M = 25\",\n"
"                  \"FOURTH.VERMINKING_RANGE_M = 25\", \"FOURTH.METALLURGY_RANGE_M = 25\",\n"
"                  \"FOURTH.WAVERING_RANGE_M = 25\", \"FOURTH.BLOOD_SACRIFICE_RANGE_M = 25\",\n"
"                  \"FOURTH.EAT_DA_RUNTS_RANGE_M = 25\", \"FOURTH.ACCUSATION_RANGE_M = 75\"):\n"
"    assert _old_zero not in script_txt, \"an old (non-70%) range constant is still present: \" + _old_zero\n"
"# the charge-window pair is NOT an ability range and is deliberately untouched\n"
"assert \"CHARGE_MIN_DISTANCE_M    = 12\" in script_txt and \"CHARGE_MAX_DISTANCE_M    = 60\" in script_txt, \\\n"
"    \"the charge-window constants changed (they are not 70%-rule ranges)\"\n\n" + ANCHOR)
sub(ANCHOR, NEW, "standing-rule asserts")

io.open(os.path.join(HERE, "build_and_install95.py"), "w", encoding="utf-8", newline="").write(src)
print("wrote build_and_install95.py", len(src), "bytes")
