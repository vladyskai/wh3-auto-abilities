#!/usr/bin/env python3
"""Round 121 - remove every army-bar (army_spec junction) ability from the mod.

THE USER'S RULING (round 121, verbatim): "The triggers will not work if the
ability is not in the ability wheel on the lower left corner of the battle
screen, meaning 'you'd lose working triggers' makes no sense. Therefore, ALL
ARMY ABILITIES PLEASE EXCLUDE."

An army-bar ability is not on the battle ability wheel, so perform_special_ability
can never be called for it: an ABILITIES entry carrying such a key can never
fire. The set is derived from the DATA (the army_spec.tsv first column), never
from a hand-kept list.

Applied to BOTH files (the shipped source and the annotated reading copy):

  1. the whole entry `merciws_monstrous_regiment` (2 keys, both army-bar)  -> REMOVED
  2. the whole entry `wardens_cage`               (1 key, army-bar)        -> REMOVED
  3. the army-bar key `wh3_main_cataclysm_khorne_greater_gate_of_khorne` is
     removed from the `greater_gate_of_khorne` entry, which KEEPS its in-wheel
     key `wh3_main_character_abilities_greater_gate_of_khorne`              -> KEY REMOVED
  4. the now-dead per-key data lines (charge pools / wind-up table / enemy-ground
     set) for those four keys, so NO occurrence of an army-bar key survives
     anywhere in either file.
"""
import sys

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

ENTRY_MERCIW = (
    '\t{ marker = "merciws_monstrous_regiment", name = "Merciw\'s Monstrous Regiment", trigger = "ally_infinite_buff",\n'
    '\t\tbadge = "zz_auto_badge_merciws_monstrous_regiment",\n'
    '\t\tkeys = { "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",\n'
    '\t\t\t"wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment" },\n'
    '\t\tox = 0, oy = 0 },\n')

ENTRY_WARDEN = (
    '\t{ marker = "wardens_cage", name = "Warden\'s Cage", trigger = "enemy_engaged_or_shot",\n'
    '\t\tbadge = "zz_auto_badge_wardens_cage",\n'
    '\t\tkeys = { "wh2_dlc15_character_abilities_wardens_cage" },\n'
    '\t\trange_real = 100,\n'
    '\t\tox = 0, oy = 0 },\n')

GG_OLD = ('\t\tkeys = {\n'
          '\t\t\t"wh3_main_cataclysm_khorne_greater_gate_of_khorne",\n'
          '\t\t\t"wh3_main_character_abilities_greater_gate_of_khorne" },\n')
GG_NEW = ('\t\t-- ROUND 121: the ARMY-BAR cataclysm key was REMOVED from this entry (army_spec\n'
          '\t\t-- junction - it is not on the battle ability wheel, so it can never be cast).\n'
          '\t\t-- The in-wheel character key stays.\n'
          '\t\tkeys = { "wh3_main_character_abilities_greater_gate_of_khorne" },\n')

DEAD_LINES = [
    '\t\t["wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment"] = 120,\n',
    '\t\t["wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment"] = 5,\n',
    '\t\t["wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment"] = 5,\n',
    '\t\t["wh3_main_cataclysm_khorne_greater_gate_of_khorne"] = 5,\n',
    '\t\t["wh3_main_cataclysm_khorne_greater_gate_of_khorne"] = true,\n',
]
WIND_OLD = "-- is listed (136 keys); entries with wind_up_time = 0 keep the plain 2 s guard"
WIND_NEW = "-- is listed (134 keys after round 121 removed 2 army-bar keys); entries with wind_up_time = 0 keep the plain 2 s guard"

ARMY_KEYS = [
    "wh2_dlc15_character_abilities_wardens_cage",
    "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_main_cataclysm_khorne_greater_gate_of_khorne",
]

for path in (SRC, ANN):
    s = open(path, encoding="utf-8").read()
    assert s.count(ENTRY_MERCIW) == 1, (path, "merciws entry", s.count(ENTRY_MERCIW))
    assert s.count(ENTRY_WARDEN) == 1, (path, "warden entry", s.count(ENTRY_WARDEN))
    assert s.count(GG_OLD) == 1, (path, "greater gate keys", s.count(GG_OLD))
    assert s.count(WIND_OLD) in (0, 1), (path, "wind-up comment", s.count(WIND_OLD))
    for ln in DEAD_LINES:
        assert s.count(ln) == 1, (path, "dead line", ln, s.count(ln))

    s = s.replace(ENTRY_MERCIW, "")
    s = s.replace(ENTRY_WARDEN, "")
    s = s.replace(GG_OLD, GG_NEW)
    for ln in DEAD_LINES:
        s = s.replace(ln, "")
    s = s.replace(WIND_OLD, WIND_NEW)

    for k in ARMY_KEYS:
        assert k not in s, (path, "army-bar key still present", k)

    open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("edited", path, "bytes", len(s))

sys.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import build_ability_database as bd
entries, consts, tips = bd.mod_entries()
keys = [k for e in entries for k in e["keys"]]
print("entries", len(entries), "keys", len(keys), "distinct", len(set(keys)))
army = set()
with open(r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv", encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            army.add(c[0].strip())
bad = [k for k in keys if k in army]
print("army_spec keys left in the ABILITIES table:", len(bad), bad)
