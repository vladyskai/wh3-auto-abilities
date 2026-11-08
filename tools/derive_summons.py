"""Derive the summon class from the game's own data (unit_spec_abil + unit_abilities).

Prints, for every spawned_unit row: the targeting flags, the type label, decoy flag,
in-wheel verdict and whether the mod already implements the key.
"""
import os, sys, json, csv, re

T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")
MOD = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"

def load_tsv(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f, delimiter="\t")
        for r in rd:
            if r.get("key", "").startswith("#"):
                continue
            rows.append(r)
    return rows

spec = load_tsv(os.path.join(T, "unit_spec_abil.tsv"))
uab  = load_tsv(os.path.join(T, "unit_abilities.tsv"))
S = {r["key"]: r for r in spec}
U = {r["key"]: r for r in uab}

UNIT_SIDE = {"active", "bound", "lord", "character", "unit", "item", "rune", "weapon"}

def truthy(v):
    return (v or "").strip().lower() in ("1", "true", "yes")

def fnum(v, d=None):
    try:
        return float(v)
    except Exception:
        return d

# implemented keys from the mod
src = open(MOD, "r", encoding="utf-8").read()
impl_keys = set(re.findall(r'"((?:wh[0-9_][a-z0-9_]*))"', src))
ab_span_start = src.find("local ABILITIES = {")
ab_span_end = src.find("\n}\n", ab_span_start)
ab_span = src[ab_span_start:ab_span_end]
ab_keys = set(re.findall(r'"(wh[0-9a-z_]+)"', ab_span))

out = []
for key, r in S.items():
    if not (r.get("spawned_unit") or "").strip():
        continue
    u = U.get(key, {})
    out.append({
        "key": key,
        "type": (u.get("type") or "").strip(),
        "source_type": (u.get("source_type") or "").strip(),
        "icon": (u.get("icon_name") or "").strip(),
        "hidden": (u.get("is_hidden_in_ui") or "").strip(),
        "spawned": (r.get("spawned_unit") or "").strip(),
        "decoy": truthy(r.get("spawn_is_decoy")),
        "ground": truthy(r.get("target_ground")),
        "self": truthy(r.get("target_self")),
        "friends": truthy(r.get("target_friends")),
        "enemies": truthy(r.get("target_enemies")),
        "tir": fnum(r.get("target_intercept_range"), 0.0),
        "eff": fnum(r.get("effect_range"), 0.0),
        "ai": (r.get("ai_usage") or "").strip(),
        "uses": (r.get("num_uses") or "").strip(),
        "impl": key in ab_keys,
    })

print("total rows with spawned_unit:", len(out))
types = {}
for o in out:
    types[o["type"]] = types.get(o["type"], 0) + 1
print("by type:", json.dumps(types, indent=1, sort_keys=True))

def inwheel(o):
    return (o["source_type"] in UNIT_SIDE and o["icon"] != "" and o["hidden"].lower() != "true")

wheel = [o for o in out if inwheel(o)]
print("in-wheel spawned rows:", len(wheel), "keys")

print("\n== in-wheel, type wh_type_summon_unit, non-decoy ==")
sel = [o for o in wheel if o["type"] == "wh_type_summon_unit" and not o["decoy"]]
print("count:", len(sel))
for o in sorted(sel, key=lambda x: x["key"]):
    print("  %-70s ground=%-5s self=%-5s fr=%-5s en=%-5s tir=%-6s eff=%-5s ai=%-14s uses=%-3s impl=%s"
          % (o["key"], o["ground"], o["self"], o["friends"], o["enemies"], o["tir"], o["eff"], o["ai"], o["uses"], o["impl"]))

print("\n== the same set that is GROUND-castable (target_ground) ==")
g = [o for o in sel if o["ground"]]
print("count:", len(g))
for o in g:
    print("  ", o["key"], "impl" if o["impl"] else "NEW")

print("\n== wh_type_summon_unit non-decoy but NOT ground-castable ==")
ng = [o for o in sel if not o["ground"]]
print("count:", len(ng))
for o in ng:
    print("  %-70s self=%s friends=%s enemies=%s tir=%s impl=%s" % (o["key"], o["self"], o["friends"], o["enemies"], o["tir"], o["impl"]))

print("\n== illusions (spawn_is_decoy true), any type ==")
for o in out:
    if o["decoy"]:
        print("  ", o["key"], "type=", o["type"], "wheel=", inwheel(o), "impl=", o["impl"], "ground=", o["ground"])

print("\n== ALL spawned rows NOT of type wh_type_summon_unit (the unlabelled real spawners) ==")
unl = [o for o in wheel if o["type"] != "wh_type_summon_unit" and not o["decoy"]]
print("count:", len(unl))
for o in sorted(unl, key=lambda x: x["key"]):
    print("  %-70s type=%-22s ground=%-5s self=%-5s fr=%-5s en=%-5s tir=%-6s impl=%s"
          % (o["key"], o["type"], o["ground"], o["self"], o["friends"], o["enemies"], o["tir"], o["impl"]))
