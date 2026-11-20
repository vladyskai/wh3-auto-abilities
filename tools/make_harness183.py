#!/usr/bin/env python3
"""Build harness183.lua from harness182.lua for round 184 (the rule-shut review, rows 10-19). Older harnesses are never
edited.

Rebases: see R and COUNTS (each names the pin and why)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut1_harness182\harness182.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut2_harness183\harness183.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h183_section.lua", encoding="utf-8").read()
CARDS = {
    "%CARD_SS%": "Fires below 75% health on the most valuable enemy infantry of 1+ men",
    "%CARD_WS%": "Fires on the most valuable enemy monster or character; flying targets only",
    "%CARD_RT%": "Fires when standing still, under the thickest melee of enemies",
}
LABELS = (
    '    enemy_area_drain_hurt = "When armed, at 75% health or less and standing still, fires on the enemy infantry in range worth the most per soldier, with enough soldiers for every strike",\n'
    '    enemy_ground_melee_cluster = "When armed and standing still, fires on the ground under the enemy in melee with the most enemy value fighting near it",\n')
BANNER = """-- ============================================================================
-- HARNESS 183 - ROUND 184: THE RULE-SHUT REVIEW, ROWS 10-19 (Flock of Doom x3, Sword of
--   Daith, Zefet-nebtar on enemy_area_drain; Ring of Corin, Warpstorm Scroll (flying) on
--   enemy_single_drain; Soul Stealer x2 on NEW enemy_area_drain_hurt; Raging Tornado on NEW
--   enemy_ground_melee_cluster).
--   Edited vs harness182: this banner, the rebases listed in tools/make_harness183.py,
--   run_h183 and its call.
--   RED control: H183_LIVE / H183_ANN on docs/backups/round184/pre184_*.lua.
-- ============================================================================
"""
R = [
    # the TIP mirror: the 2 new labels
    ('    melee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n',
     '    melee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n'
     '    -- HARNESS 183: the round-184 labels\n' + LABELS, 1),
    ("(it == 1890)   -- HARNESS 182: 2 x 945", "(it == 1910)   -- HARNESS 183: 2 x 955", 1),
    # the charge gate: 7 new multi-use keys (Flock of Doom x3, Sword of Daith, Zefet-nebtar, Ring of Corin, Raging Tornado)
    ("""cp103(blk, '"] = ') == (RED_MODE and 0 or 332))""", """cp103(blk, '"] = ') == (RED_MODE and 0 or 339))""", 1),
    # the cast gate: 3 new wind-up keys (the Runecaller's Flock of Doom 1 s, Zefet-nebtar 1.5 s, Raging Tornado 5 s)
    ("        blk ~= nil and nkeys == 333)", "        blk ~= nil and nkeys == 336)", 1),
    # 10 new range_real fields (every row 10-19 entry is aimed)
    ('"\\t\\trange_real = ") == 418)', '"\\t\\trange_real = ") == 428)', 2),
    ('"\\t\\trange_real = ") == (EXP.sum and 418 or 96))', '"\\t\\trange_real = ") == (EXP.sum and 428 or 96))', 1),
    # 1 new target_class field (Warpstorm Scroll: flying)
    ('cp(s, "\\t\\ttarget_class = ") == 54)', 'cp(s, "\\t\\ttarget_class = ") == 55)', 3),
    # enemy_single_drain 12 -> 14 (Ring of Corin, Warpstorm Scroll); enemy_area_drain 8 -> 13 (Flock of Doom x3, Sword
    # of Daith, Zefet-nebtar)
    ("""cp(s, 'trigger = "enemy_single_drain"') == 12""", """cp(s, 'trigger = "enemy_single_drain"') == 14""", 2),
    ("""cp(s, 'trigger = "enemy_area_drain"') == 8""", """cp(s, 'trigger = "enemy_area_drain"') == 13""", 1),
]
# the entry and key counts: 945 -> 955 entries, 998 -> 1008 keys (the 10 new entries, one key each)
COUNTS = [("945", "955", None), ("998", "1008", None)]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
for old, new, want in COUNTS:
    pat = r"(?<!\d)%s(?!\d)" % old
    got = len(re.findall(pat, src))
    assert want is None or got == want, (old, got)
    src = re.sub(pat, new, src)
    print(old, "->", new, ":", got)
sec = SECTION
for a, b in CARDS.items():
    assert sec.count(a) == 1, a
    sec = sec.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + sec + RUNNER_ANCHOR)
assert src.count("\nrun_h182()\n") == 1
src = src.replace("\nrun_h182()\n", "\nrun_h182()\nrun_h183()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
