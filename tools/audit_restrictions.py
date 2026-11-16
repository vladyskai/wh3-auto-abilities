#!/usr/bin/env python3
"""Night audit 2026-11-16: every game restriction flag on every automated key, against what the mod enforces.

The game's special_ability_to_invalid_target_flags (what may NOT be targeted) and _invalid_usage_flags (when the CASTER
may not use it). For each automated entry: the flags, and which of them the entry's family or fields honour. Prints the
unhandled ones grouped by flag; writes docs/WH3_restriction_audit_2026-11-17.md.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_restriction_audit_2026-11-17.md"


def tsv(n):
    f = open(os.path.join(GP.GAMEDATA, n), encoding="utf-8-sig")
    h = f.readline().rstrip("\n").split("\t")
    f.readline()
    return [dict(zip(h, l.rstrip("\n").split("\t"))) for l in f]


INV, USE = collections.defaultdict(set), collections.defaultdict(set)
for r in tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    INV[r["special_ability"]].add(r["invalid_target"])
for r in tsv("special_ability_to_invalid_usage_flags_tables.tsv"):
    USE[r["special_ability"]].add(r["invalid_usage_flag"])
USA = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}

S = open(SRC, encoding="utf-8").read()
tab = S.split("\nlocal ABILITIES = {", 1)[1] if "\nlocal ABILITIES = {" in S else S
ENTRIES = []
for m in re.finditer(r'\t\{ marker = "([^"]+)", name = "((?:[^"\\]|\\.)*)", trigger = "([^"]+)",(.*?)\n\t\tox = ', S, re.S):
    body = m.group(4)
    keys = re.findall(r'"([^"]+)"', body.split("keys = {", 1)[1].split("}", 1)[0]) if "keys = {" in body else []
    tc = re.search(r'target_class = "([^"]+)"', body)
    ENTRIES.append({"marker": m.group(1), "name": m.group(2), "fam": m.group(3), "keys": keys,
                    "cls": tc.group(1) if tc else None, "air_only": "air_only = true" in body,
                    "no_melee": "no_melee = true" in body})
print("entries parsed:", len(ENTRIES))

WW_NOMELEE = set(re.search(r'FOURTH\.WW_NOMELEE_TEXT = "([^"]*)"', S).group(1).split(";")) - {""}
SHOT_NOMELEE = set(k for k, a in re.findall(r"([a-z0-9_]+)=(\d),\d,[\d.]+", re.search(r'FOURTH\.SHOT_TEXT = "([^"]*)"', S).group(1)) if a == "1")
BLOB_SHOT = {}
for k, n, b, a, l, c, br, g, me in re.findall(r"([a-z0-9_]+)=(\d+),([\d.]+),([\d.]+),([\d.]+),(\d),(\d),(\d),(\d)",
                                               re.search(r'FOURTH\.BLOB_SHOT_TEXT = "([^"]*)"', S).group(1)):
    BLOB_SHOT[k] = (g == "1", me == "1")
# families whose candidate list holds only non-flying enemy infantry (the map's m.enemies)
NONFLY_LIST = {"enemy_blob", "enemy_blob_vortex", "enemy_area_drain", "enemy_infantry_shot", "enemy_wander"}
SELF_FAMS_HINT = ("melee", "charge", "wavering", "health", "under_fire", "tired", "when_ready", "self_", "glorious",
                  "ushoran", "blood_sacrifice", "eat_da_runts", "fly_dive", "last_stand")
SIEGE = {"on_a_platform", "climbing", "manning_equipment", "climbing_manning_eq_on_platform", "on_a_platform_only",
         "not_climbing_manning_eq_on_platform", "not_on_a_platform", "flying_over_platform", "flying_over_invalid_location"}
PHASE = {"phase_is_deployment", "phase_is_the_end_phase"}


def target_handled(e, flag, k):
    fam, cls = e["fam"], e["cls"]
    if flag in SIEGE:
        return "siege (not modelled)"
    if flag == "flying_currently":
        if cls in ("not_flying", "commander_ground"):
            return "class"
        if fam in NONFLY_LIST:
            return "family list (non-flying infantry)"
        return None
    if flag == "ground_unit":
        return "class" if cls == "flying" else None
    if flag in ("unit_is_not_commander_class", "hasnt_casting_ability"):
        return "class" if cls in ("commander", "commander_ground") else None
    if flag == "unit_is_not_single_entity":
        return "class" if cls in ("single", "large_single") else None
    if flag == "undead_unit":
        return "class" if cls == "not_undead" else None
    if flag == "is_not_missile_unit":
        return "class" if cls == "missile" else None
    if flag == "unit_is_not_large":
        return "class" if cls in ("large", "large_single") else None
    return None


def usage_handled(e, flag, k):
    fam = e["fam"]
    if flag in SIEGE:
        return "siege (not modelled)"
    if flag in PHASE:
        return "battle phase (never in the deployment / end phase poll)"
    if flag == "engaged_in_melee":
        if k in WW_NOMELEE or k in SHOT_NOMELEE or (k in BLOB_SHOT and BLOB_SHOT[k][1]) or e["no_melee"]:
            return "generated table / field"
        return None
    if flag == "grounded":
        if (k in BLOB_SHOT and BLOB_SHOT[k][0]) or fam == "fly_dive" or e["air_only"]:
            return "generated table / family"
        return None
    if flag == "flying_currently":
        return None
    return None


rows = []
for e in ENTRIES:
    for k in e["keys"]:
        for f in sorted(INV.get(k, ())):
            h = target_handled(e, f, k)
            rows.append(("target", f, e, k, h))
        for f in sorted(USE.get(k, ())):
            h = usage_handled(e, f, k)
            rows.append(("usage", f, e, k, h))
unh = [r for r in rows if r[4] is None]
by = collections.defaultdict(list)
for kind, f, e, k, h in unh:
    by[(kind, f)].append((e["fam"], e["marker"], k))
out = ["# Restriction audit (night of 2026-11-16 / 17)", "",
       "Every game restriction flag on every automated key (%d entries), against what the mod enforces. Flags the mod "
       "does not honour are listed below by flag. Siege flags (walls, platforms, manning equipment) and battle-phase flags "
       "are not modelled and are not listed." % len(ENTRIES), "",
       "| Kind | Flag | Unhandled keys |", "|---|---|---:|"]
for (kind, f), lst in sorted(by.items(), key=lambda kv: -len(kv[1])):
    out.append("| %s | `%s` | %d |" % (kind, f, len(lst)))
out.append("")
for (kind, f), lst in sorted(by.items(), key=lambda kv: -len(kv[1])):
    out.append("## %s `%s` (%d)" % (kind, f, len(lst)))
    out.append("")
    out.append("| Family | Marker | Key |")
    out.append("|---|---|---|")
    for fam, mk, k in sorted(lst):
        out.append("| `%s` | `%s` | `%s` |" % (fam, mk, k))
    out.append("")
open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("flags seen:", len(rows), "unhandled:", len(unh))
for (kind, f), lst in sorted(by.items(), key=lambda kv: -len(kv[1])):
    fams = collections.Counter(x[0] for x in lst)
    print("%-6s %-34s %3d  %s" % (kind, f, len(lst), dict(fams.most_common(6))))
print("wrote", OUT)
