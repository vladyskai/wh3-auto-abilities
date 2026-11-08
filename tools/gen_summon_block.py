"""Generate the summon-round Lua blocks from the derived plan.

Writes:
  $TMPDIR/gen/new_entries.lua     - the ABILITIES entries (A + D + B + E + F)
  $TMPDIR/gen/commander_keys.lua  - the derived commander-class key set
  $TMPDIR/gen/plan.json           - counts + key lists for the harness/builder/xlsx
"""
import os, csv, json, re

T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")
ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
GEN = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Temp"), "gen")
os.makedirs(GEN, exist_ok=True)
MOD = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")

def load_tsv(p):
    rows = []
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if (r.get("key") or "").startswith("#"):
                continue
            rows.append(r)
    return rows

spec = {r["key"]: r for r in load_tsv(os.path.join(T, "unit_spec_abil.tsv"))}
uab = {r["key"]: r for r in load_tsv(os.path.join(T, "unit_abilities.tsv"))}
lu = {r["key"]: r for r in load_tsv(os.path.join(T, "db_land_units.tsv"))}
mu = {r["unit"]: r for r in load_tsv(os.path.join(T, "db_main_units.tsv"))}

def load_names(p):
    d = {}
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            k = r.get("key") or ""
            if k.startswith("#"):
                continue
            d[k] = r.get("text") or ""
    return d

names = load_names(os.path.join(T, "unit_abilities.loc.tsv"))

def fnum(v, d=0.0):
    try:
        return float(v)
    except Exception:
        return d

def truthy(v):
    return (v or "").strip().lower() in ("1", "true", "yes")

src = open(MOD, "r", encoding="utf-8").read()
i0 = src.find("local ABILITIES = {")
i1 = src.find("\n}\n", i0)
ab_span = src[i0:i1]
existing_markers = set(re.findall(r'\{ marker = "([a-z0-9_]+)"', ab_span))

def slug(s):
    s = s.lower()
    s = s.replace("&", " and ").replace("'", "").replace("\u2019", "")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s

# ---- the A batch: from the derived plan -------------------------------------
plan = json.load(open(os.path.join(ROOT, "audit", "_summon_round_plan.json")))
A_rows = [r for r in plan["A"]]
# merge the one broken-loc pair into the base entry
A_rows_by_name = {}
for r in A_rows:
    nm = r["name"]
    if nm.startswith("{{tr:"):
        nm = "Invocation of the Lichemaster"
    A_rows_by_name.setdefault(nm, []).append(r)

# ---- the nine, Eye of Khorne, D13, Nurgling Tide -----------------------------
NINE = [
    ("wh2_dlc16_lord_abilities_beast_pack", "Beast Pack"),
    ("wh2_dlc15_item_abilities_blacktoofs_conjuration", "Blacktoof's Conjuration"),
    ("wh2_dlc16_lord_abilities_call_to_gwindalor", "Call to Gwindalor"),
    ("wh2_dlc16_spell_bound_vampires_lesser_raise_dead", "Lesser Raise Dead"),
    ("wh2_dlc17_spell_bound_savage_dominion", "Savage Dominion"),
    ("wh3_dlc26_hero_abilities_savage_predators", "Savage Predators"),
    ("wh2_dlc16_hero_abilities_tide_of_death", "Tide of Death"),
    ("wh2_dlc16_hero_abilities_tide_of_pox", "Tide of Pox"),
    ("wh3_main_item_abilities_zak_aloooog", "Wake Da Idol"),
]
D13 = ["wh3_dlc29_spell_bound_the_dreaded_thirteenth",
       "wh3_dlc29_spell_bound_the_dreaded_thirteenth_1",
       "wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol",
       "wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1"]

entries = []   # (marker, name, trigger, keys, range_real, extra)

def add(marker, name, trigger, keys, range_real=None, extra=""):
    entries.append({"marker": marker, "name": name, "trigger": trigger,
                    "keys": keys, "range_real": range_real, "extra": extra})

used = set(existing_markers)
def unique(m):
    base, n = m, 2
    while m in used:
        m = base + "_" + str(n)
        n += 1
    used.add(m)
    return m

# A: one entry per display name; range = the largest non-negative real range in the group
A_entries = []
for nm in sorted(A_rows_by_name):
    rs = A_rows_by_name[nm]
    tirs = [x["tir"] for x in rs if x["tir"] and x["tir"] > 0]
    if tirs:
        rr = int(round(max(tirs)))
        extra = ""
    else:
        rr = None
        extra = "unbounded"
    keys = [x["key"] for x in rs]
    m = unique(slug(nm))
    add(m, nm, "enemy_ground_melee", keys, rr, extra)
    A_entries.append((m, nm, keys, rr, extra))

for key, nm in NINE:
    s = spec[key]
    rr = int(round(fnum(s["target_intercept_range"])))
    add(unique(slug(nm)), nm, "enemy_ground_melee", [key], rr)

# Eye of Khorne - unit form, finisher
add(unique("eye_of_khorne"), "Eye of Khorne", "enemy_low_health_noncommander",
    ["wh3_dlc26_lord_abilities_eye_of_khorne"], 50)
# The Dreaded Thirteenth - enemy-ground form, four keys, one entry
add(unique("the_dreaded_thirteenth"), "The Dreaded Thirteenth",
    "enemy_melee_noncommander", D13, 100)
# Nurgling Tide - SELF cast
add(unique("nurgling_tide"), "Nurgling Tide", "self_summon_melee",
    ["wh3_main_lord_abilities_nurgling_tide"], None)

lines = []
lines.append("\t-- ============================================================================")
lines.append("\t-- THE SUMMON ROUND (harness 102 / v102).")
lines.append("\t-- (A) THE REST OF THE wh_type_summon_unit CLASS - every in-wheel, non-illusion,")
lines.append("\t-- GROUND-CASTABLE summon derived from the game's own data (spawned_unit set +")
lines.append("\t-- type wh_type_summon_unit + spawn_is_decoy false + target_ground true + in-wheel")
lines.append("\t-- + not boss-only + not already implemented): %d entries / %d keys." % (len(A_entries), sum(len(x[2]) for x in A_entries)))
lines.append("\t-- They ride the PROVEN enemy_ground_melee trigger (Gate of Khorne's): the closest")
lines.append("\t-- FIGHTING enemy inside each ability's own 70%% bound, summon placed on THAT")
lines.append("\t-- ENEMY's ground. (D) THE NINE unlabelled real spawners, same trigger, same cast")
lines.append("\t-- form. (E) Eye of Khorne is a FINISHER (enemy_low_health_noncommander) and")
lines.append("\t-- casts through the UNIT form (target_enemies = true, target_ground = false).")
lines.append("\t-- (F) The Dreaded Thirteenth (4 keys, one entry) is an explosion+summon on")
lines.append("\t-- enemy_melee_noncommander, placed on the enemy's ground. (B) Nurgling Tide is")
lines.append("\t-- the ONE self-target summon (self_summon_melee, cast on SELF).")
lines.append("\t-- The four ILLUSIONS are NOT here: they are engine-refused while engaged in")
lines.append("\t-- melee, so a melee trigger can never fire them (excluded, see the tracker).")
lines.append("\t-- ============================================================================")
for e in entries:
    tag = " enemy_ground_melee (A)" if e["trigger"] == "enemy_ground_melee" and len(e["keys"]) >= 1 and e["name"] in A_rows_by_name else ""
    if e["trigger"] == "enemy_ground_melee" and e["name"] not in A_rows_by_name:
        tag = " enemy_ground_melee (D)"
    disp = e["name"].replace('"', '\\"')
    lines.append('\t{ marker = "%s", name = "%s", trigger = "%s",%s' % (e["marker"], disp, e["trigger"], ""))
    lines.append('\t\tbadge = "zz_auto_badge_%s",' % e["marker"])
    if len(e["keys"]) == 1:
        lines.append('\t\tkeys = { "%s" },' % e["keys"][0])
    else:
        lines.append('\t\tkeys = {')
        for j, k in enumerate(e["keys"]):
            lines.append('\t\t\t"%s"%s' % (k, "," if j < len(e["keys"]) - 1 else " },"))
    if e["range_real"] is not None:
        lines.append("\t\trange_real = %d," % e["range_real"])
    if e["extra"] == "unbounded":
        lines.append("\t\tunbounded = true,")
    lines.append("\t\tox = 0, oy = 0 },")
lines.append("")
block = "\n".join(lines) + "\n"
open(os.path.join(GEN, "new_entries.lua"), "w", encoding="utf-8", newline="\n").write(block)

# ---- the derived commander-class key set ------------------------------------
cmdr = set()
for k, r in lu.items():
    if r["class"] == "com":
        cmdr.add(k)
for k, r in mu.items():
    if r["caste"] in ("lord", "hero"):
        lk = r["land_unit"]
        if lk:
            cmdr.add(lk)
cmlines = []
cmlines.append("\t-- THE DERIVED COMMANDER (LORD/HERO) KEY SET ... %d keys" % len(cmdr))
for k in sorted(cmdr):
    cmlines.append('\t\t["%s"] = true,' % k)
cmblock = "\n".join(cmlines) + "\n"
open(os.path.join(GEN, "commander_keys.lua"), "w", encoding="utf-8", newline="\n").write(cmblock)

out = {
    "entries": entries,
    "A_entries": [{"marker": m, "name": n, "keys": ks, "range_real": rr, "unbounded": ex == "unbounded"}
                  for (m, n, ks, rr, ex) in A_entries],
    "A_keys": [k for e in A_entries for k in e[2]],
    "D_keys": [k for k, _ in NINE],
    "E_keys": ["wh3_dlc26_lord_abilities_eye_of_khorne"],
    "F_keys": D13,
    "B_keys": ["wh3_main_lord_abilities_nurgling_tide"],
    "commander_n": len(cmdr),
    "counts": {
        "entries": len(entries),
        "keys": sum(len(e["keys"]) for e in entries),
        "A": len(A_entries),
        "A_keys": sum(len(x[2]) for x in A_entries),
    },
}
json.dump(out, open(os.path.join(GEN, "plan.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(out["counts"], indent=1))
print("A entries:", len(A_entries), " keys:", sum(len(x[2]) for x in A_entries))
print("entries at all:", len(entries), "keys at all:", sum(len(e["keys"]) for e in entries))
print("commander keys:", len(cmdr))
print("markers:", ", ".join(e["marker"] for e in entries))
