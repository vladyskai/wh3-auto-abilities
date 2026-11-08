# -*- coding: utf-8 -*-
"""Emit the derived class-key tables as a Lua fragment (FOURTH.class_keys)."""
import csv, os

W = os.path.expandvars(r"%LOCALAPPDATA%/Temp/wh3")
HERE = os.path.dirname(os.path.abspath(__file__))

def load(p):
    with open(W + "/" + p, encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t"); hdr = next(r)
        return [dict(zip(hdr, x + [""] * (len(hdr) - len(x)))) for x in r]

lu = load("db_land_units.tsv")
mu = load("db_main_units.tsv")
ent = {r["key"]: r for r in load("db_battle_entities.tsv")}
junc = load("db_unit_attributes_to_groups_junctions.tsv")

attr_by_group = {}
for r in junc:
    attr_by_group.setdefault(r["attribute_group"], set()).add(r["attribute"])
attr_of = {r["key"]: attr_by_group.get(r["attribute_group"], set()) for r in lu}
caste_of = {}
for r in mu:
    if r["land_unit"]:
        caste_of.setdefault(r["land_unit"], set()).add(r["caste"])

keys = [r["key"] for r in lu]
size = {r["key"]: ent.get(r["man_entity"], {}).get("size", "") for r in lu}
cls = {r["key"]: r["class"] for r in lu}

def by_caste(*names):
    ns = set(names)
    return sorted(k for k in keys if caste_of.get(k, set()) & ns)

tables = [
    ("beast",        by_caste("war_beast")),
    ("monster",      by_caste("monster")),
    ("warmachine",   by_caste("warmachine")),
    ("construct",    sorted(k for k in keys if "construct" in attr_of.get(k, ()))),
    ("hellforged",   sorted(k for k in keys if "hellforged" in attr_of.get(k, ()))),
    ("missile",      sorted(r["key"] for r in lu if r.get("primary_missile_weapon", "").strip() != "")),
    ("overseer",     sorted(k for k in keys if cls[k] != "com" and size[k] not in ("large", "very_large"))),
]

out = []
out.append("-- ============================================================================")
out.append("-- THE TARGET-CLASS KEY LISTS (harness 99). Every list is DERIVED FROM THE")
out.append("-- GAME'S OWN DATA - never hand-written - by exact whole-key matching, and")
out.append("-- copied here VERBATIM (the same method the Slayer list above uses). NOTHING")
out.append("-- here is a name guess: each entry states the source table + column and the")
out.append("-- match rule. Membership is EXACT WHOLE-KEY equality (ONE table read; the")
out.append("-- banned substring finder never runs), so a near-miss key is correctly NOT a")
out.append("-- member. LIMITED: an unreadable type() read is treated as NOT-a-member")
out.append("-- (fail-safe: such a unit is simply not offered to the engine).")
out.append("--")
out.append("--   beast      : main_units_tables.caste == \"war_beast\"  (the land_unit key")
out.append("--                of each such main_units row).  [kind = beast]")
out.append("--   monster    : main_units_tables.caste == \"monster\"    (land_unit key).")
out.append("--   warmachine : main_units_tables.caste == \"warmachine\" (land_unit key).")
out.append("--   construct  : the unit's unit_attributes group carries the \"construct\"")
out.append("--                attribute (unit_attributes_to_groups_junctions_tables joined")
out.append("--                to land_units_tables.attribute_group).")
out.append("--   hellforged : the same join, attribute \"hellforged\" (the Hell-Forged units).")
out.append("--   missile    : land_units_tables.primary_missile_weapon is NON-EMPTY (the")
out.append("--                unit can perform missile attacks) - the flag the game's")
out.append("--                cannot_perform_missile_attack invalid-target test mirrors.")
out.append("--   overseer   : land_units_tables.class != \"com\" (NOT commander-class) AND the")
out.append("--                battle entity size (battle_entities_tables.size, reached via")
out.append("--                land_units_tables.man_entity) is NOT large / very_large (NOT")
out.append("--                large) - exactly the two invalid-target flags the ability")
out.append("--                carries (unit_is_commander_class, unit_is_large).")
out.append("--")
out.append("-- Sizes: " + ", ".join("%s=%d" % (n, len(t)) for n, t in tables) + ".")
out.append("-- ============================================================================")
out.append("FOURTH.class_keys = {")
for name, ks in tables:
    out.append("\t" + name + " = {")
    for k in ks:
        out.append('\t\t["' + k + '"] = true,')
    out.append("\t},")
out.append("}")
out.append("")
out.append("-- true when the engine's type() key of `unit` is a member of the named class")
out.append("-- list above. A missing / raising / non-string type() read is NOT a member.")
out.append("function FOURTH.class_member(unit, name)")
out.append("\tlocal tbl = FOURTH.class_keys[name]")
out.append("\tif tbl == nil then return false end")
out.append("\tlocal ok, t = pcall(function() return unit:type() end)")
out.append("\tif not ok or type(t) ~= \"string\" then return false end")
out.append("\treturn tbl[t] == true")
out.append("end")
out.append("")

open(HERE + "/classes_frag.lua", "w", encoding="utf-8", newline="").write("\n".join(out) + "\n")
print("wrote classes_frag.lua", sum(1 for _ in open(HERE + "/classes_frag.lua", encoding="utf-8")), "lines")
print("sizes:", {n: len(t) for n, t in tables})
print("total entries:", sum(len(t) for _, t in tables))
