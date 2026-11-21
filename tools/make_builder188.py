#!/usr/bin/env python3
"""Build the round-188 build script from the round-187 one (the range rule: every cast-range bound is
max(floor(real x 0.70), real - 20 m); user ruling 2026-11-21: "C. Your rule, the larger of 70% and real minus 20 m,
everywhere.").

Gate rebases (code only; the history docstring at the top keeps its words): every older gate that pinned a 70% value
now pins the new bound (TOKENS), and every gate that computed floor(real x 0.70) computes the new rule (FORMULAS).
The aura gates (aura_m = floor(aura_real x 0.70)), the 24 / 38 m named constants and the 25 m and smaller bounds are
untouched: there 70% is the larger value.
ROUND 188 GATE: FOURTH.RANGE_MARGIN_M = 20, FOURTH.range_bound, EVERY ENEMY_CAST / ALLY_CAST constant equals the rule,
the three named bounds, the Executioner takes the larger of its 90% and the rule."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_uiscale_harness186\build_and_install187.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_rangerule_harness187\build_and_install188.py"


def rb(real):
    return max((real * 70) // 100, real - 20)


TOKENS = []
for side, real in ([("ENEMY", r) for r in (70, 75, 80, 90, 100, 120, 130, 150, 180, 200, 250, 300, 350, 400, 500, 600)]
                   + [("ALLY", r) for r in (75, 100, 150, 200, 250)]):
    name = "FOURTH.%s_CAST_R%-3d" % (side, real) if real < 100 else "FOURTH.%s_CAST_R%d" % (side, real)
    TOKENS.append(("%s = %d" % (name, (real * 70) // 100), "%s = %d" % (name, rb(real))))
TOKENS += [
    ("FOURTH.BLOOD_SACRIFICE_RANGE_M = 70", "FOURTH.BLOOD_SACRIFICE_RANGE_M = 80"),
    ("FOURTH.EAT_DA_RUNTS_RANGE_M = 70", "FOURTH.EAT_DA_RUNTS_RANGE_M = 80"),
    ("FOURTH.ACCUSATION_RANGE_M = 52", "FOURTH.ACCUSATION_RANGE_M = 55"),
]
FORMULAS = [
    ("int(_r * 0.70 + 1e-9)", "max(int(_r * 0.70 + 1e-9), _r - 20)"),
    ("int(120 * 0.70 + 1e-9)", "max(int(120 * 0.70 + 1e-9), 120 - 20)"),
    ("int(_r165 * 0.70 + 1e-9)", "max(int(_r165 * 0.70 + 1e-9), _r165 - 20)"),
    ("int(250 * 0.70 + 1e-9) == 175", "max(int(250 * 0.70 + 1e-9), 250 - 20) == 230"),
    ('           ("FOURTH.BLOOD_SACRIFICE_RANGE_M", 100, 70),\n           ("FOURTH.EAT_DA_RUNTS_RANGE_M", 100, 70),\n'
     '           ("FOURTH.ACCUSATION_RANGE_M", 75, 52))',
     '           ("FOURTH.BLOOD_SACRIFICE_RANGE_M", 100, 80),   # ROUND 188: max(70%, real - 20)\n'
     '           ("FOURTH.EAT_DA_RUNTS_RANGE_M", 100, 80),\n           ("FOURTH.ACCUSATION_RANGE_M", 75, 55))'),
    ("assert int(_real * 0.70 + 1e-9) == _want,", "assert max(int(_real * 0.70 + 1e-9), _real - 20) == _want,"),
]
ANCHOR = 'print("ROUND 187 GATE OK: the badges and the ALL button follow the wheel (live shift, 2 s)")\n'
ADD = ANCHOR + r'''# ROUND 188: the range rule (user 2026-11-21: "C. Your rule, the larger of 70% and real minus 20 m, everywhere.").
assert "\nFOURTH.RANGE_MARGIN_M = 20 " in script_txt and "\nfunction FOURTH.range_bound(real)\n" in script_txt \
    and "math.max(math.floor(real * FOURTH.RANGE_FRACTION + 1e-9), real - FOURTH.RANGE_MARGIN_M)" in script_txt, \
    "BUILD REFUSED (round 188): the range rule's margin or helper is missing"
_c188 = re.findall(r"\nFOURTH\.(ENEMY|ALLY)_CAST_R(\d+)\s*=\s*(\d+)", script_txt)
_bad188 = [c for c in _c188 if int(c[2]) != max(int(c[1]) * 70 // 100, int(c[1]) - 20)]
assert len(_c188) >= 25 and not _bad188, "BUILD REFUSED (round 188): cast bounds off the rule: %s" % _bad188
for _t188 in ("FOURTH.BLOOD_SACRIFICE_RANGE_M = 80 ", "FOURTH.EAT_DA_RUNTS_RANGE_M = 80 ", "FOURTH.ACCUSATION_RANGE_M = 55 "):
    assert script_txt.count("\n" + _t188) == 1, "BUILD REFUSED (round 188): missing %r" % _t188
assert "\t\t\tability.range_m = math.max(ability.range_m or 0,\n\t\t\t\tmath.floor(ability.range_real * FOURTH.SINGLE_RANGE_FRACTION + 1e-9))" \
    in script_txt, "BUILD REFUSED (round 188): the Executioner must take the larger bound"
assert "ability.aura_m = math.floor(ability.aura_real * FOURTH.RANGE_FRACTION + 1e-9)" in script_txt, \
    "BUILD REFUSED (round 188): the aura bound must stay 70%"
print("ROUND 188 GATE OK: %d cast bounds on max(70%%, real - 20); named 80/80/55; the Executioner 230" % len(_c188))
'''
src = open(SRC, encoding="utf-8").read()
end_doc = src.index('"""', src.index('"""') + 3) + 3
head, code = src[:end_doc], src[end_doc:]
for a, b in TOKENS:   # a bound no older gate pinned is simply absent
    code = code.replace(a, b)
for a, b in FORMULAS:
    assert code.count(a) >= 1, (a, code.count(a))
    code = code.replace(a, b)
src = head + code
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
assert "import re" in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
