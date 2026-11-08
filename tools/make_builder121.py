#!/usr/bin/env python3
"""Build tools/build_and_install121.py from the round-118 build script (the one
that built the installed pack).

Round 121 removed two whole ABILITIES entries (merciws_monstrous_regiment,
wardens_cage) and one key from greater_gate_of_khorne - 4 army-bar keys in 3
entries - so every count pin in the builder follows the table: 689 -> 687
entries, the AUTO327 list 307 -> 305 entries / 323 -> 320 keys,
enemy_engaged_or_shot 86 -> 85, range_real 205 -> 204, ally_infinite_buff
1 -> 0, enemy_ground_keys 116 -> 115. Plus the permanent gate.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_airdrop_immediate_harness118\build_and_install118.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_and_install121.py"

GATE = '''
# =====================================================================
# ROUND 121 GATE - REFUSE TO BUILD IF ANY ARMY-BAR (army_spec) KEY IS IN THE
# ABILITIES TABLE.
#
# The user's ruling, round 121, verbatim: "The triggers will not work if the
# ability is not in the ability wheel on the lower left corner of the battle
# screen, meaning 'you'd lose working triggers' makes no sense. Therefore, ALL
# ARMY ABILITIES PLEASE EXCLUDE."
#
# An army-bar ability (a key in the army_spec junction) has no button on the
# battle ability wheel, so perform_special_ability can never be called for it:
# such an entry can never fire. It is dead weight by definition, not a roster
# choice. This assertion has NO exceptions list and runs BEFORE any stale pack
# is deleted or any WebSocket command is sent - a violating table does not
# build at all.
# =====================================================================
ARMY_SPEC_TSV = r"C:/Users/vlady/AppData/Local/Temp/wh3/army_spec.tsv"
MOD_LUA = FILES[0][0]


def _army_bar_keys():
    with open(ARMY_SPEC_TSV, encoding="utf-8", errors="replace") as f:
        f.readline()
        out = set()
        for line in f:
            if line.startswith("#"):
                continue
            c = line.rstrip("\\n").split("\\t")
            if c and c[0].strip():
                out.add(c[0].strip())
        return out


def _abilities_keys(path):
    src = open(path, encoding="utf-8").read()
    a = src.index("local ABILITIES = {")
    b = src.index("\\n}", a)
    region = re.sub(r"--[^\\n]*", "", src[a:b])   # a commented-out key is not a key
    keys = []
    for m in re.finditer(r"keys = \\{(.*?)\\}", region, re.S):
        keys += re.findall(r'"([^"]+)"', m.group(1))
    return keys


_army = _army_bar_keys()
_mod_keys = _abilities_keys(MOD_LUA)
_hits = sorted(set(k for k in _mod_keys if k in _army))
assert not _hits, (
    "BUILD REFUSED (round 121 army-bar gate): %d ABILITIES key(s) are in the army_spec junction. "
    "An army-bar ability is NOT on the battle ability wheel, so perform_special_ability can never "
    "be called for it and the entry can never fire - it must not ship (user ruling: ALL ARMY "
    "ABILITIES EXCLUDE). Offending keys: %s" % (len(_hits), _hits))
print("ARMY-BAR GATE OK: %d ABILITIES keys, none of them in the %d-key army_spec junction"
      % (len(_mod_keys), len(_army)))

for p in (OUT_PACK, GAME_PACK):'''

src = open(SRC, encoding="utf-8").read()

MERCIW = ('    ("merciws_monstrous_regiment", { "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment", '
          '"wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment" }),\n')
WARDEN = '    ("wardens_cage", { "wh2_dlc15_character_abilities_wardens_cage" }),\n'
for blk in (MERCIW, WARDEN):
    assert src.count(blk) == 1, (blk[:50], src.count(blk))
    src = src.replace(blk, "")

REPS = [
    ('assert len(AUTO327) == 307, "the auto-327 entry list is not 307 (4 boss-only removed in 101)"',
     'assert len(AUTO327) == 305, ("the auto-327 entry list is not 305 (4 boss-only removed in 101; '
     '2 army-bar entries removed in round 121)")'),
    ('assert _nk327 == 323, "the auto-327 key count is not 323 (got %d)" % _nk327',
     'assert _nk327 == 320, ("the auto-327 key count is not 320 (got %d; 3 army-bar keys removed '
     'in round 121)" % _nk327)'),
    ('assert script_txt.count("\\t{ marker = ") == 689, "the abilities table is not 689 entries"',
     'assert script_txt.count("\\t{ marker = ") == 687, "the abilities table is not 687 entries"'),
    ('assert script_txt.count(\'trigger = "enemy_engaged_or_shot"\') == 86',
     'assert script_txt.count(\'trigger = "enemy_engaged_or_shot"\') == 85'),
    ('assert script_txt.count("\\t\\trange_real = ") == 205',
     'assert script_txt.count("\\t\\trange_real = ") == 204'),
    ("assert script_txt.count('trigger = \"ally_infinite_buff\"') == 1",
     "assert script_txt.count('trigger = \"ally_infinite_buff\"') == 0"),
    ('count(\'"] = true,\') == 116, "enemy_ground_keys is not 116 entries"',
     'count(\'"] = true,\') == 115, "enemy_ground_keys is not 115 entries (the cataclysm Gate key '
     'left in round 121)"'),
]
counts = {}
for a, b in REPS:
    counts[a[:48]] = src.count(a)
    assert src.count(a) >= 1, ("missing", a[:70])
    src = src.replace(a, b)

src = src.replace("is not 86 (3 boss-only removed)",
                  "is not 85 (3 boss-only removed; Warden's Cage removed in round 121)")
src = src.replace("the range_real fields are not 205", "the range_real fields are not 204")
src = src.replace("range_real count is not 205", "range_real count is not 204")
src = src.replace('"enemy_engaged_or_shot moved"', '"enemy_engaged_or_shot moved (85 after round 121)"')

ANCHOR = "for p in (OUT_PACK, GAME_PACK):"
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, GATE.lstrip("\n"))

head = src.split("class Client")[0]
if "\nimport re\n" not in head:
    src = src.replace("import json\n", "import json\nimport re\n", 1)

src = src.replace('"""Build the mod pack, verify it, install it. One WebSocket session, then done.',
                  '"""Build the mod pack, verify it, install it. One WebSocket session, then done.\n\n'
                  'ROUND 121: the ABILITIES table is 687 entries / 738 keys (two whole army-bar entries\n'
                  'and one army-bar key removed). The ARMY-BAR GATE below refuses the build outright if\n'
                  'any army_spec key is in the table; every count pin in this script follows the table.', 1)

open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
for k, v in counts.items():
    print("  %-50s x%d" % (k, v))
