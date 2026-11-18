#!/usr/bin/env python3
"""GENERATE the spellcaster class (review read F; user ruling 2026-11-18: "Okay, then let's use the caster list").

A land unit is a spellcaster when
  (a) the game gives it a spell lore: special_ability_groups_to_units_junctions, or
  (b) it is the battle unit (agent_subtypes.associated_unit_override, plus its numbered / mount variants in land_units)
      of a character whose campaign skill tree grants a lore or a lore spell:
      character_skill_node_sets -> character_skill_node_set_items -> character_skill_nodes ->
      character_skill_level_to_effects_junctions -> effect_bonus_value_special_ability_group_junctions (a lore) /
      effect_bonus_value_unit_ability_junctions (a spell of a lore, via special_ability_groups_to_unit_abilities_junctions).
The same method as tools/list_casters.py (the side session's list). agent_subtypes.is_caster is NOT used (it flags 27
non-casters: Dwarf lords, thanes, engineers, slayers, Gotrek).

  derive() -> sorted land unit keys;  text(keys) -> the ';'-joined FOURTH.SPELLCASTER_TEXT value
"""
import collections
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402


def rows(name):
    with open(os.path.join(GP.GAMEDATA, name), encoding="utf-8", newline="") as f:
        r = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    head = r[0]
    return [dict(zip(head, x)) for x in r[2:] if x]


def derive():
    junction = rows("special_ability_groups_to_units_junctions.tsv")
    units_a = {r["unit"] for r in junction}
    lore_groups = {r["ability_group"] for r in junction}
    lore_groups |= {r["special_ability_groups"] for r in rows("special_ability_groups_to_unit_abilities_junctions.tsv")
                    if "_lore_" in r["special_ability_groups"]}
    spell_lore = {}
    for r in rows("special_ability_groups_to_unit_abilities_junctions.tsv"):
        if r["special_ability_groups"] in lore_groups:
            spell_lore[r["unit_special_abilities"]] = r["special_ability_groups"]
    eff = set()
    for r in rows("effect_bonus_value_special_ability_group_junctions.tsv"):
        if r["special_ability_group"] in lore_groups:
            eff.add(r["effect"])
    for r in rows("effect_bonus_value_unit_ability_junctions.tsv"):
        if r["unit_ability"] in spell_lore:
            eff.add(r["effect"])
    skills = {r["character_skill_key"] for r in rows("character_skill_level_to_effects_junctions.tsv")
              if r["effect_key"] in eff}
    node_skill = {r["key"]: r["character_skill_key"] for r in rows("character_skill_nodes.tsv")}
    set_sub = {r["key"]: r["agent_subtype_key"] for r in rows("character_skill_node_sets.tsv") if r["agent_subtype_key"]}
    subs_b = set()
    for r in rows("character_skill_node_set_items.tsv"):
        sub = set_sub.get(r["set"])
        if sub and node_skill.get(r["item"]) in skills:
            subs_b.add(sub)
    land = sorted(r["key"] for r in rows("land_units.tsv"))

    def variants(u):
        m = re.match(r"^(.*_)\d+$", u)
        stem = m.group(1) if m else u
        return [k for k in land if k == u or (m and k.startswith(stem) and re.fullmatch(r"\d+", k[len(stem):]))
                or (not m and k.startswith(u + "_"))]

    units_b = set()
    for r in rows("agent_subtypes.tsv"):
        if r["key"] in subs_b and r["associated_unit_override"]:
            units_b.update(variants(r["associated_unit_override"]))
    land_set = set(land)
    return sorted((units_a | units_b) & land_set)


def text(keys):
    return ";".join(keys)


if __name__ == "__main__":
    k = derive()
    print(len(k), "spellcaster land units")
