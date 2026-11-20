#!/usr/bin/env python3
"""Build harness184.lua from harness183.lua for round 185 (the rule-shut review, rows 20-64). Older harnesses are never
edited.

Rebases: see R and COUNTS (each names the pin and why)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut2_harness183\harness183.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut3_harness184\harness184.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h184_section.lua", encoding="utf-8").read()
CARDS = {
    "%CARD_BH%": "Fires when it or a nearby ally charges",
    "%CARD_OF%": "Fires on the most valuable ally of 30+ men in melee; no missile units; no Lords or Heroes; no large units",
    "%CARD_FG%": "Fires when standing still, under the thickest melee of enemies; no flying targets",
    "%CARD_MR%": "Fires below 10% health in melee, clear of allies",
}
LABELS = (
    '    aura_charge_only = "When armed, fires when this unit or a friendly unit within its aura charges",\n'
    '    ally_offering = "When armed, fires on the most valuable friendly unit of 30 or more soldiers in melee (no missile units), cast on it",\n')
BANNER = """-- ============================================================================
-- HARNESS 184 - ROUND 185: THE RULE-SHUT REVIEW, ROWS 20-64 (33 entries: 13 safe blasts on
--   melee_unwavering, 2 on melee_clear, Cellular Instability, Splode da Big 'Un!, the Battle
--   Howls and the Silver Horn on NEW aura_charge_only, Twilight Horn II, Swiftness of Itzl,
--   Bonecrusher, the Immolation rune (last stand), Beastlord's Gaze, Fog of the Damned, Locus
--   of Contagion, Mad Cap Mushrooms, Mirror of Knowledge, Offering to the Gods on NEW
--   ally_offering, the Seismic Snares, the Black Gem of Gnar).
--   Edited vs harness183: this banner, the rebases listed in tools/make_harness184.py,
--   run_h184 and its call.
--   RED control: H184_LIVE / H184_ANN on docs/backups/round185/pre185_*.lua.
-- ============================================================================
"""
R = [
    # the TIP mirror: the 2 new labels
    ('    melee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n',
     '    melee_or_self_shooting = "When armed, fires when this unit is in melee or shooting",\n'
     '    -- HARNESS 184: the round-185 labels\n' + LABELS, 1),
    ("(it == 1910)   -- HARNESS 183: 2 x 955", "(it == 1976)   -- HARNESS 184: 2 x 988", 1),
    # the charge gate: 7 new multi-use keys; the cast gate: 17 new wind-up keys
    ("""cp103(blk, '"] = ') == (RED_MODE and 0 or 339))""", """cp103(blk, '"] = ') == (RED_MODE and 0 or 346))""", 1),
    ("        blk ~= nil and nkeys == 336)", "        blk ~= nil and nkeys == 353)", 1),
    # 2 new range_real fields (Bonecrusher, Fog of the Damned); 3 new ally_range_real fields (Twilight Horn II,
    # Beastlord's Gaze, Offering to the Gods); 2 new target_class fields (both not_flying); 1 more unbounded entry
    # (Mirror of Knowledge)
    ('"\\t\\trange_real = ") == 428)', '"\\t\\trange_real = ") == 430)', 2),
    ('"\\t\\trange_real = ") == (EXP.sum and 428 or 96))', '"\\t\\trange_real = ") == (EXP.sum and 430 or 96))', 1),
    ('"\\t\\tally_range_real = ") == 68)', '"\\t\\tally_range_real = ") == 71)', 3),
    ('cp(s, "\\t\\ttarget_class = ") == 55)', 'cp(s, "\\t\\ttarget_class = ") == 57)', 3),
    ('cp102(s, "\\t\\tunbounded = true,") == 2', 'cp102(s, "\\t\\tunbounded = true,") == 3', 1),
    # family counts: charge_only 4 -> 5 (Swiftness of Itzl), self_recharging 5 -> 6 (Mad Cap Mushrooms), melee_clear
    # 4 -> 6, last_stand_clear 1 -> 3, enemy_blob_vortex 1 -> 2
    ("""(s, 'trigger = "charge_only"') == 4""", """(s, 'trigger = "charge_only"') == 5""", 5),
    ("""cp(s, 'trigger = "self_recharging"') == 5""", """cp(s, 'trigger = "self_recharging"') == 6""", 1),
    # enemy_fast_near_ally 19 -> 20 (Mirror of Knowledge)
    ("""cp(s, 'trigger = "enemy_fast_near_ally"') == 19""", """cp(s, 'trigger = "enemy_fast_near_ally"') == 20""", 2),
    ("""cp(s, 'trigger = "melee_clear"') == 4 and cp(s, 'trigger = "fly_dive"') == 2""",
     """cp(s, 'trigger = "melee_clear"') == 6 and cp(s, 'trigger = "fly_dive"') == 2""", 1),
    ("""cp(s, 'trigger = "last_stand_clear"') == 1 and cp(s, 'trigger = "enemy_blob_vortex"') == 1""",
     """cp(s, 'trigger = "last_stand_clear"') == 3 and cp(s, 'trigger = "enemy_blob_vortex"') == 2""", 1),
    # melee_clear_block is ridden twice now (Land Mine, Cellular Instability)
    ("""and cp(s, 'trigger = "melee_clear_block"') == 1 and   -- HARNESS 180: row 98 built (A)""",
     """and cp(s, 'trigger = "melee_clear_block"') == 2 and   -- HARNESS 180: row 98 built (A); HARNESS 184: + Cellular Instability""", 1),
    ("""      for _, fam in ipairs({ "melee_clear_block", "enemy_summon_blob" }) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') == 1 then""",
     """      for _, fam in ipairs({ "melee_clear_block", "enemy_summon_blob" }) do
        if cp(s, fam .. " = FOURTH.evaluate_" .. fam .. ",") == 1 and cp(s, 'trigger = "' .. fam .. '"') >= 1 then   -- HARNESS 184""", 1),
]
# the entry and key counts: 955 -> 988 entries, 1008 -> 1041 keys (the 33 new entries, one key each); melee_unwavering
# 268 -> 281 (13 safe blasts)
COUNTS = [("955", "988", None), ("1008", "1041", None), ("268", "281", 17)]
# the 1008 swap must not touch C6's unit ids (1001 ... 1010)
UID_FIX = ("(1001, 1002, 1003, 1004, 1005, 1006, 1007, 1041, 1009, 1010)",
           "(1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010)")
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
assert src.count(UID_FIX[0]) == 1
src = src.replace(UID_FIX[0], UID_FIX[1])
sec = SECTION
for a, b in CARDS.items():
    assert sec.count(a) == 1, a
    sec = sec.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + sec + RUNNER_ANCHOR)
assert src.count("\nrun_h183()\n") == 1
src = src.replace("\nrun_h183()\n", "\nrun_h183()\nrun_h184()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
