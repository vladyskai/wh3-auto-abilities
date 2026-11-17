#!/usr/bin/env python3
"""Build harness170.lua from harness169.lua for round 171 (the score 1-2 review, rows 1-15 and 21; 9 closures, 2 splits).
Older harnesses are never edited.

Rebases (user rulings 2026-11-17; every one is a count or a name the round changes on purpose):
  * the table: 946 -> 939 entries (every occurrence of the number), 1,003 -> 994 keys (the key-count comparisons);
  * melee_unwavering 298 -> 282 (7 moved out, 9 closed); ushoran_health 19 -> 18 (Necrotic Phylactery moved);
    when_ready 21 -> 22 (Wand of Jet); ally_range_real fields 58 -> 59 (Red Fury); start_armed 1 -> 8;
  * h101 0aa 'the neighbours of every removal survive': Hagtree Fetish is closed this round, so it leaves the list;
  * h91 O3 (twin keys ride one entry): Waaagh!'s two keys are split this round (the army-wide key has its own entry);
    the world now uses Ursun's Roar's pro twin keys, which still share one in-melee entry;
  * h93 TIP mirror: the six new family labels.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_foolhardiness_harness169\harness169.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_review_rows_harness170\harness170.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h170_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 170 - ROUND 171: THE SCORE 1-2 REVIEW, ROWS 1-15 AND 21 (six new
--   families, two split entries, nine closures, the contact list).
--   Edited vs harness169: this banner, the rebases listed in tools/make_harness170.py,
--   run_h170 and its call.
--   RED control: H170_LIVE / H170_ANN on docs/backups/round171/pre171_*.lua.
-- ============================================================================
"""
R = [
    ("    a = (it == 1892)\n", "    a = (it == 1878)   -- HARNESS 170: 2 x 939\n", 1),
    # the charge-gate table loses the closed Watched by the Watcher's hold row (3 uses)
    ("""cp103(blk, '"] = ') == (RED_MODE and 0 or 328))""",
     """cp103(blk, '"] = ') == (RED_MODE and 0 or 327))   -- HARNESS 170: Watched by the Watcher closed""", 1),
    ("n_mk == 1003", "n_mk == 994", 1),
    ("#AKEYS == 1003", "#AKEYS == 994", 1),
    ("n_k == 1003", "n_k == 994", 6),
    ("keys = 1003,", "keys = 994,", 3),
    ("== 298", "== 282", 15),
    ("mu = 298,", "mu = 282,", 2),
    ("""'trigger = "ushoran_health"') == 19""", """'trigger = "ushoran_health"') == 18""", 5),
    ("ush = 19,", "ush = 18,", 1),
    ("""ally_range_real = ") == 58)""", """ally_range_real = ") == 59)""", 3),
    ("""cp(s, 'trigger = "when_ready"') == 21""", """cp(s, 'trigger = "when_ready"') == 22""", 1),
    ('and cp(s, "\\t\\tstart_armed = true,\\n") == 1', 'and cp(s, "\\t\\tstart_armed = true,\\n") == 8', 1),
    ('        .. "frost_shard_glaive, hagtree_fetish, void_pendulum)",\n',
     '        .. "frost_shard_glaive, void_pendulum; HARNESS 170: Hagtree Fetish is closed)",\n', 1),
    ("        and raw_find(span, 'marker = \"hagtree_fetish\"', 1, true) ~= nil\n", "", 1),
    ('      { name = "waaagh", uid = 9203, owns = { M_MU2B }, melee = true, wavering = false },\n'
     '    }, cards = { { id = "9203", state = "active", vis = true } }, bar = { { id = "b1", key = M_MU2B } } })\n'
     '    print("== " .. TAG .. "O3. TWIN KEYS: the DLC/base twin key fires the SAME entry (Waaagh!) == ")\n'
     '    if not boot(W, PATH, TAG, 9203, "waaagh_in_combat", "O3") then return nil end\n'
     '    polln(W, 1)\n'
     '    local a = (#W.fires == 1 and W.fires[1].uid == 9203 and W.fires[1].key == M_MU2B)\n',
     '      -- HARNESS 170: Waaagh!\'s keys are split (round 171); Ursun\'s Roar\'s pro twin keys still share one entry\n'
     '      { name = "ursun", uid = 9203, owns = { "wh3_main_pro_character_abilities_ursuns_roar_1" }, melee = true, wavering = false },\n'
     '    }, cards = { { id = "9203", state = "active", vis = true } }, bar = { { id = "b1", key = "wh3_main_pro_character_abilities_ursuns_roar_1" } } })\n'
     '    print("== " .. TAG .. "O3. TWIN KEYS: a twin key fires the SAME entry (Ursun\'s Roar, round 171) == ")\n'
     '    if not boot(W, PATH, TAG, 9203, "ursuns_roar", "O3") then return nil end\n'
     '    polln(W, 1)\n'
     '    local a = (#W.fires == 1 and W.fires[1].uid == 9203 and W.fires[1].key == "wh3_main_pro_character_abilities_ursuns_roar_1")\n',
     1),
    ('    health_below_15 = "When armed, fires when this unit is below 15% health",\n  }\n',
     '    health_below_15 = "When armed, fires when this unit is below 15% health",\n'
     '    -- HARNESS 170: the six round-171 families\n'
     '    army_charge = "When armed, fires when 3 or more of our units charge or have just made contact",\n'
     '    aura_charge = "When armed, fires when this unit, or 2 or more units in its aura, charge or have just made contact",\n'
     '    self_or_ally_charge = "When armed, fires on this unit or the nearest charging ally, else when this unit is in melee",\n'
     '    slow_aura = "When armed, fires in melee, or when a fast enemy enters the aura",\n'
     '    winds_low = "When armed, fires when the winds pool is low with reserve left, the caster above 50% health",\n'
     '    contact_melee = "When armed, fires in melee against an enemy whose blows carry a contact effect",\n'
     '  }\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
n946 = len(re.findall(r"(?<!\d)946(?!\d)", src))
src = re.sub(r"(?<!\d)946(?!\d)", "939", src)
print("946 -> 939:", n946)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h169()\n") == 1
src = src.replace("\nrun_h169()\n", "\nrun_h169()\nrun_h170()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
