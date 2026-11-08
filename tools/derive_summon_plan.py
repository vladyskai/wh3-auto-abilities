"""Build the summon-round plan from the game's own data.

Outputs audit/_summon_round_plan.json:
  A : remaining wh_type_summon_unit, non-decoy, ground-castable, in-wheel, not boss-only, not implemented
  A_not_ground : the same label set that cannot take a ground point (with reason)
  illusions : the four decoy rows
  D : the nine unlabelled real spawners (named by the user)
  E : Eye of Khorne row
  F : the four Dreaded Thirteenth keys
  B : Nurgling Tide row
"""
import os, csv, json, re

T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")
ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
MOD = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")

def load_tsv(p):
    rows = []
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if (r.get("key") or "").startswith("#"):
                continue
            rows.append(r)
    return rows

def load_pairs(p, a="key", b="text"):
    d = {}
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            k = r.get(a) or ""
            if k.startswith("#"):
                continue
            d[k] = r.get(b) or ""
    return d

spec = {r["key"]: r for r in load_tsv(os.path.join(T, "unit_spec_abil.tsv"))}
uab = {r["key"]: r for r in load_tsv(os.path.join(T, "unit_abilities.tsv"))}
names = load_pairs(os.path.join(T, "unit_abilities.loc.tsv"), "key", "text")
if not names:
    names = load_pairs(os.path.join(ROOT, "archive", "research", "wh3", "unit_abilities.loc.tsv"), "key", "text")

# grant junctions (boss-only test)
grants = {}
with open(os.path.join(ROOT, "archive", "research", "wh3", "land_abil.tsv"), "r", encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        a = r.get("ability") or ""
        if a.startswith("#"):
            continue
        grants.setdefault(a, set()).add(r.get("land_unit") or "")

src = open(MOD, "r", encoding="utf-8").read()
i0 = src.find("local ABILITIES = {")
i1 = src.find("\n}\n", i0)
ab_span = src[i0:i1]
ab_keys = set(re.findall(r'"(wh[0-9a-z_]+)"', ab_span))

UNIT_SIDE = {"active", "bound", "lord", "character", "unit", "item", "rune", "weapon"}
OUT_OF_SCOPE_FAMILY = ("_army_abilities_", "_quest_abilities_")

def truthy(v):
    return (v or "").strip().lower() in ("1", "true", "yes")

def fnum(v, d=0.0):
    try:
        return float(v)
    except Exception:
        return d

def inwheel(key, r, u):
    if (u.get("source_type") or "").strip() not in UNIT_SIDE:
        return False, "source_type=%s" % (u.get("source_type") or "")
    if not (u.get("icon_name") or "").strip():
        return False, "no icon_name"
    if (u.get("is_hidden_in_ui") or "").strip().lower() == "true":
        return False, "is_hidden_in_ui"
    for fam in OUT_OF_SCOPE_FAMILY:
        if fam in key:
            return False, "family %s" % fam
    return True, ""

def boss_only(key):
    g = grants.get(key)
    if not g:
        return False, None
    return all("_boss" in x for x in g), sorted(g)

rows = []
for key, s in spec.items():
    if not (s.get("spawned_unit") or "").strip():
        continue
    u = uab.get(key, {})
    ok, why = inwheel(key, s, u)
    rows.append({
        "key": key,
        "name": names.get("unit_abilities_onscreen_name_" + key) or names.get(key) or key,
        "type": (u.get("type") or "").strip(),
        "source_type": (u.get("source_type") or "").strip(),
        "inwheel": ok,
        "why_not": why,
        "decoy": truthy(s.get("spawn_is_decoy")),
        "ground": truthy(s.get("target_ground")),
        "self": truthy(s.get("target_self")),
        "friends": truthy(s.get("target_friends")),
        "enemies": truthy(s.get("target_enemies")),
        "affect_self": truthy(s.get("affect_self")),
        "tir": fnum(s.get("target_intercept_range")),
        "eff": fnum(s.get("effect_range")),
        "ai": (s.get("ai_usage") or "").strip(),
        "uses": (s.get("num_uses") or "").strip(),
        "spawned": (s.get("spawned_unit") or "").strip(),
        "impl": key in ab_keys,
        "boss_only": boss_only(key)[0],
        "grants": boss_only(key)[1],
    })

A_all = [r for r in rows if r["inwheel"] and not r["decoy"] and r["type"] == "wh_type_summon_unit"]
A = [r for r in A_all if r["ground"] and not r["boss_only"] and not r["impl"]]
A_no_ground = [r for r in A_all if not r["ground"] and not r["boss_only"] and not r["impl"]]
A_impl = [r for r in A_all if r["impl"]]

def group(rows_):
    g = {}
    for r in rows_:
        g.setdefault(r["name"], []).append(r)
    return g

print("A: %d keys in %d display-name groups" % (len(A), len(group(A))))
for name, rs in sorted(group(A).items()):
    print("  %-42s %s" % (name[:42], ", ".join(x["key"] for x in rs)))
print()
print("A_not_ground: %d keys" % len(A_no_ground))
for r in A_no_ground:
    print("  %-58s ground=%s self=%s fr=%s en=%s aff=%s eff=%s name=%s"
          % (r["key"], r["ground"], r["self"], r["friends"], r["enemies"], r["affect_self"], r["eff"], r["name"]))
print()
print("A already implemented:", [r["key"] for r in A_impl])
print("boss_only in the label set:", [r["key"] for r in A_all if r["boss_only"]])
print()
print("distinct tir in A:", sorted({r["tir"] for r in A}))
print("distinct tir in the nine:", sorted({spec[k]["target_intercept_range"] for k in [
    "wh2_dlc16_lord_abilities_beast_pack", "wh2_dlc15_item_abilities_blacktoofs_conjuration",
    "wh2_dlc16_lord_abilities_call_to_gwindalor", "wh2_dlc16_spell_bound_vampires_lesser_raise_dead",
    "wh2_dlc17_spell_bound_savage_dominion", "wh3_dlc26_hero_abilities_savage_predators",
    "wh2_dlc16_hero_abilities_tide_of_death", "wh2_dlc16_hero_abilities_tide_of_pox",
    "wh3_main_item_abilities_zak_aloooog"]}))

plan = {"A": A, "A_not_ground": A_no_ground, "A_impl": A_impl,
        "illusions": [r for r in rows if r["decoy"]],
        "rows": rows}
with open(os.path.join(ROOT, "audit", "_summon_round_plan.json"), "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=1)
print("\nwrote audit/_summon_round_plan.json")
