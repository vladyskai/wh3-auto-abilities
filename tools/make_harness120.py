#!/usr/bin/env python3
"""Build harness120.lua from harness119.lua for round 121.

Round 121 removed 2 whole ABILITIES entries and 1 key from a third (all
army-bar / army_spec junction: no battle-wheel button, so they can never fire).
The table went 689 entries / 742 keys -> 687 / 738. This script:

  1. rebases every LIVE count pin (689 -> 687, 742 -> 738, and the stale
     "want 688" in B4a's message) on NON-comment lines only - historical
     comments that describe older rounds are left as history;
  2. removes the two Merciw's Monstrous Regiment worlds (MC1, MC2) and the K.merc
     key from run_h99, because the entry they exercised is gone;
  3. takes the `ally_infinite_buff` trigger count in run_h99's 0w check to 0
     (the family now has no member in the table);
  4. prepends the round-121 banner.

Older harnesses are never edited.
"""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_signoff_harness119\harness119.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261021_armybar_removal_harness120\harness120.lua"

BANNER = """-- ============================================================================
-- HARNESS 120 - ROUND 121, THE ARMY-BAR REMOVAL (user ruling, verbatim):
--   "The triggers will not work if the ability is not in the ability wheel on
--    the lower left corner of the battle screen, meaning 'you'd lose working
--    triggers' makes no sense. Therefore, ALL ARMY ABILITIES PLEASE EXCLUDE."
--
--   An army-bar ability (a key in the army_spec junction) has no button on the
--   battle ability wheel, so perform_special_ability can never be called for it:
--   an ABILITIES entry carrying one can never fire. THREE entries were found by
--   intersecting the mod's key set with the army_spec set (not from a report):
--     * merciws_monstrous_regiment - WHOLE ENTRY removed (2 keys, both army-bar)
--     * wardens_cage               - WHOLE ENTRY removed (1 key, army-bar)
--     * greater_gate_of_khorne     - ONE KEY removed (the cataclysm twin); the
--                                    entry KEEPS its in-wheel character key
--   Table: 689 entries / 742 keys -> 687 entries / 738 keys. No army-bar key
--   survives anywhere in either file (the dead per-key charge-pool / wind-up /
--   enemy-ground rows for those four keys are gone too).
--
--   Edited vs harness119: every LIVE count pin rebased (689 -> 687, 742 -> 738),
--   the h99 MC1/MC2 worlds and their K.merc constant removed (the entry they
--   exercised no longer exists), the h99 `ally_infinite_buff` trigger count
--   taken to 0, and this banner. Nothing else changed.
-- ============================================================================
"""

src = open(SRC, encoding="utf-8").read()

# ---------------------------------------------------------------- 1. count pins
# ONLY the pin shapes below are rebased. A bare "689"/"742" substitution would
# also hit world data (uid 9742, uid 8742, ...), which is NOT a count.
PIN_RULES = [
    ("== 689", "== 687"),
    ("== 742", "== 738"),
    ("entries = 689, keys = 742", "entries = 687, keys = 738"),
    ("FULL 689-entry table", "FULL 687-entry table"),
    ("689 abilities per pass", "687 abilities per pass"),
    ("has 689 entries", "has 687 entries"),
    ("has all 742 keys", "has all 738 keys"),
    ("table of 689 after round h105", "table of 687 after round h105"),
    ("(12 air-drop entries of 689)", "(12 air-drop entries of 687)"),
    ("want 688", "want 687"),
]
lines = src.split("\n")
changed = []
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue                      # history stays history
    new = ln
    for a, b in PIN_RULES:
        if a in new:
            new = new.replace(a, b)
    if new != ln:
        changed.append((i + 1, ln.strip()[:110], new.strip()[:110]))
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed))
for c in changed:
    print("  L%-6d %s" % (c[0], c[1]))
assert len(changed) >= 30, len(changed)

# ---------------------------------------------------------------- 2. the h99 worlds
K_MERC = '    merc = "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",\n'
assert src.count(K_MERC) == 1, src.count(K_MERC)
src = src.replace(K_MERC, "")

MC1 = ('  add(function(P, T) return world_cg(P, T, { wname = "MC1: Merciw\'s Monstrous Regiment CASTS ON AN ALLY 5 km away (NO bound)",\n'
       '    key = K.merc, marker = "merciws_monstrous_regiment", cuid = 9745,\n'
       '    allies = { { name = PLAIN, uid = 9746, dist = 5000 } }, expect = "fire_ally", target = 9746 }) end)\n')
MC2 = ('  add(function(P, T) return world_cg(P, T, { wname = "MC2: Merciw\'s stays SILENT with NO ally at all",\n'
       '    key = K.merc, marker = "merciws_monstrous_regiment", cuid = 9747, expect = "silent" }) end)\n')
for blk in (MC1, MC2):
    assert src.count(blk) == 1, (blk[:60], src.count(blk))
    src = src.replace(blk, "")

# ---------------------------------------------------------------- 3. the family count
OLD_CNT = "      and cp99(s, 'trigger = \"ally_infinite_buff\"') == 1"
NEW_CNT = "      and cp99(s, 'trigger = \"ally_infinite_buff\"') == 0"
assert src.count(OLD_CNT) == 1, src.count(OLD_CNT)
src = src.replace(OLD_CNT, NEW_CNT)

# the headline prose that named the removed ability
OLD_P = ('      .. "pair and Daemonic Whispers ride the plain in-melee buff family; Merciw\'s Monstrous Regiment has NO distance "\n'
         '      .. "bound (infinite range per the wiki); Grut\'s Sickle picks the ally with the MOST hit points. The offer test is "')
NEW_P = ('      .. "pair and Daemonic Whispers ride the plain in-melee buff family; Merciw\'s Monstrous Regiment\'s two worlds "\n'
         '      .. "were REMOVED in round 121 (army-bar: no wheel button, so it can never be cast); Grut\'s Sickle picks the ally "\n'
         '      .. "with the MOST hit points. The offer test is "')
assert src.count(OLD_P) == 1, ("h99 headline prose", src.count(OLD_P))
src = src.replace(OLD_P, NEW_P)
print("h99 headline prose updated")

assert "K.merc" not in src and "merciws_monstrous_regiment" not in src.replace(
    "Merciw's Monstrous Regiment", ""), "a Merciw reference survived"

src = BANNER + src

# ---------------------------------------------------------------- 4. follow-on pins
# Removing 2 entries and 1 key also moves: the A4 bootstrap iteration pin (2 per
# entry), the per-family trigger counts (enemy_engaged_or_shot -1), the
# range_real counts (-1: Warden's Cage), the charge-gate key count (-1), the
# wind-up table key count (-3: both Merciw keys and the cataclysm gate key), and
# every suite-boundary running count after the h99 section (-10: the two removed
# worlds' checks no longer run).
FIXES = [
    ("a = (it == 1378)", "a = (it == 1374)"),
    ("cp(s, 'trigger = \"melee_unwavering\"') == 360 and cp(s, 'trigger = \"enemy_engaged_or_shot\"') == 86",
     "cp(s, 'trigger = \"melee_unwavering\"') == 360 and cp(s, 'trigger = \"enemy_engaged_or_shot\"') == 85"),
    ("cp97(s, 'trigger = \"enemy_engaged_or_shot\"') == 86",
     "cp97(s, 'trigger = \"enemy_engaged_or_shot\"') == 85"),
    ("cp97(s, \"\\t\\trange_real = \") == 205", "cp97(s, \"\\t\\trange_real = \") == 204"),
    ("cp102(s, \"\\t\\trange_real = \") == (EXP.sum and 205 or 96)",
     "cp102(s, \"\\t\\trange_real = \") == (EXP.sum and 204 or 96)"),
    ("cp103(blk, '\"] = ') == (RED_MODE and 0 or 162)", "cp103(blk, '\"] = ') == (RED_MODE and 0 or 161)"),
    ("nkeys == 173", "nkeys == 170"),
    ("687, keys = 738, mu = 360, es = 86", "687, keys = 738, mu = 360, es = 85"),
    ("want 3445)\", pre102 == 3445", "want 3435)\", pre102 == 3435"),
    ("want 3528)\", pre103 == 3528", "want 3518)\", pre103 == 3518"),
    ("want 3572)\", pre104 == 3572", "want 3562)\", pre104 == 3562"),
    ("want 3653)\", pre105 == 3653", "want 3643)\", pre105 == 3643"),
    ("want 3705)\", pre106 == 3705", "want 3695)\", pre106 == 3695"),
    ("want 3815)\", pre107 == 3815", "want 3805)\", pre107 == 3805"),
    ("want 4492)\", pre114 == 4492", "want 4482)\", pre114 == 4482"),
    ("pre115 == 4614", "pre115 == 4604"),
    ("pre116 == 4686", "pre116 == 4676"),
    ("pre117 == 4702", "pre117 == 4692"),
    ("pre118 == 4718", "pre118 == 4708"),
]
for a, b in FIXES:
    assert src.count(a) == 1, ("fix target not unique", a, src.count(a))
    src = src.replace(a, b)
print("follow-on pins fixed:", len(FIXES))

import os
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
