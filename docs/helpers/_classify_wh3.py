#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify every `proposed` / `proposed (FF)` row in the WH3 ability tracker
under the widened standing auto-rules R1-R4.

Data: tracker  C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md
      game-data effect tables  %LOCALAPPDATA%/Temp/wh3
      (grouped2.json = effect family; unit_spec_abil.tsv = targeting/engine flags;
       phase_junc.tsv + phases.tsv = the real mechanical effect phases)
"""
import re, json, csv, collections, os

DESK = r"C:/Users/vlady/Desktop"
DUMP = os.path.expandvars(r"%LOCALAPPDATA%/Temp/wh3")
TRACKER = os.path.join(DESK, "WH3_ability_tracker.md")

# ---------------------------------------------------------------- parse tracker
txt = open(TRACKER, encoding="utf-8").read().splitlines()
def fl(pred, s=0):
    for i in range(s, len(txt)):
        if pred(txt[i]):
            return i
    return -1
i3a = fl(lambda l: l.startswith("### 3a."))
i3b = fl(lambda l: l.startswith("### 3b."))
i3c = fl(lambda l: l.startswith("### 3c."))
rowre = re.compile(r"^\|\s*(.*?)\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|")

def parse(lo, hi):
    out = []
    for ln in range(lo, hi):
        m = rowre.match(txt[ln])
        if not m:
            continue
        parts = [p.strip() for p in txt[ln].strip().strip("|").split("|")]
        out.append(dict(line=ln + 1, name=m.group(1), key=m.group(2),
                        status=m.group(3),
                        group=parts[2] if len(parts) > 2 else "",
                        prop=parts[3] if len(parts) > 3 else "",
                        notes=parts[4] if len(parts) > 4 else ""))
    return out

rows = parse(i3a, i3b) + parse(i3b, i3c)

# ---------------------------------------------------------------- game data
g2 = json.load(open(os.path.join(DUMP, "grouped2.json"), encoding="utf-8"))
FAM = {r[0]: r[4] for r in g2}

USPEC = {}
with open(os.path.join(DUMP, "unit_spec_abil.tsv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row.get("key"):
            USPEC[row["key"]] = row

PJ = collections.defaultdict(list)
with open(os.path.join(DUMP, "phase_junc.tsv"), encoding="utf-8") as f:
    for ln in f:
        if ln.startswith("#") or ln.startswith("order") or not ln.strip():
            continue
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 6:
            PJ[p[1]].append(p[5])

PH = {}
with open(os.path.join(DUMP, "phases.tsv"), encoding="utf-8") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        if row.get("id"):
            PH[row["id"]] = row

def fnum(s):
    try:
        return float(s)
    except Exception:
        return 0.0

def phase_summary(key):
    agg = dict(n=0, neg=False, pos=False, dmg=False, heal=False,
               affallies=False, affenemies=False, resurrect=False,
               fatigue=False, imbue=False)
    for pid in PJ.get(key, []):
        p = PH.get(pid)
        if not p:
            continue
        agg["n"] += 1
        if p.get("effect_type") == "negative": agg["neg"] = True
        if p.get("effect_type") == "positive": agg["pos"] = True
        if fnum(p.get("damage_amount", "0")) > 0 or fnum(p.get("max_damaged_entities", "0")) > 0:
            agg["dmg"] = True
        if fnum(p.get("heal_amount", "0")) > 0 or fnum(p.get("barrier_heal_amount", "0")) > 0:
            agg["heal"] = True
        if p.get("affects_allies") == "true": agg["affallies"] = True
        if p.get("affects_enemies") == "true": agg["affenemies"] = True
        if p.get("resurrect") == "true": agg["resurrect"] = True
        if fnum(p.get("fatigue_change_ratio", "0")) != 0: agg["fatigue"] = True
        if p.get("imbue_magical") == "true" or p.get("imbue_ignition") == "true" or p.get("imbue_contact") == "true":
            agg["imbue"] = True
    return agg

# ---------------------------------------------------------------- rule tables
ACCEPT_FAM = {
    # R1 positive buffs -> in-melee self
    "augment_melee_self": "in-melee self",
    "augment_melee": "in-melee self",
    "augment_melee_area": "in-melee self",
    "augment_defense_melee": "in-melee self",
    "augment_defense_melee_area": "in-melee self",
    "augment_morale": "in-melee self",
    "augment_morale_area": "in-melee self",
    "augment_self_area": "in-melee self",
    "augment_ranged": "in-melee self",
    "augment_ranged_area": "in-melee self",
    "augment_defense_ranged": "in-melee self",
    "augment_defense_ranged_area": "in-melee self",
    "augment_spellcasting": "in-melee self",
    "augment_support_self": "in-melee self",
    "aoe_centred_on_self": "in-melee self",
    # R1 charge family
    "augment_charge_self": "charge and in-melee",
    "augment_charge": "charge and in-melee",
    "augment_charged_at": "charge and in-melee",
    "augment_charged_at_area": "charge and in-melee",
    # R1 heals
    "healing": "health<=75 (no melee gate)",
    "healing_area": "health<=75 (no melee gate)",
    "healing_single_use": "health<=75 (no melee gate)",
    "augment_melee_healing": "in melee and health<=75",
    # R2 enemy debuffs -> in-melee self
    "hex_melee": "in-melee self",
    "hex_melee_area": "in-melee self",
    "hex_melee_area_self": "in-melee self",
    "hex_morale": "in-melee self",
    "hex_morale_area": "in-melee self",
    "hex_armour": "in-melee self",
    "hex_armour_area": "in-melee self",
    "hex_speed": "in-melee self",
    "hex_speed_area": "in-melee self",
    "hex_speed_under_fire": "in-melee self",
    "hex_speed_charging_at": "in-melee self",
    "hex_ranged": "in-melee self",
    "hex_ranged_area": "in-melee self",
    "hex_spellcaster": "in-melee self",
    "hex_spellcasting": "in-melee self",
    "hex_flying_area": "in-melee self",
}
EXCLUDE_FAM = {
    "hex_ranged_summon": "summon/transform",
    "threatened": "summon",
    "aoe_bombardment": "bombardment (placed attack)",
    "aoe": "explosive / placed AoE",
    "aoe_ap": "explosive / placed AoE",
    "vortex": "vortex",
    "vortex_ap": "vortex",
    "vortex_wind": "vortex",
    "vortex_wind_ap": "vortex",
    "vortex_breath": "vortex / breath",
    "vortex_breath_ap": "vortex / breath",
    "vortex_flying_only": "vortex",
    "vortex_low_morale": "vortex",
    "projectile_explosive": "explosive projectile",
    "projectile_explosive_ap": "explosive projectile",
    "always_use_only_land": "explosive / breath attack",
}
FLAG_FAM = {
    "full_hide": "stealth/escape effect",
    "tzarkan": "transform/shapechange",
    "qb_master_of_souls": "quest-scripted ability (ambiguous)",
}
GENERIC_GLOSS = {
    "in-melee self": "self/ally combat buff — fire when in melee",
    "charge and in-melee": "charge bonus — fire in the charge window or in melee",
    "health<=75 (no melee gate)": "heal / replenish — fire at <=75% health",
    "in melee and health<=75": "heal + melee buff — fire in melee at <=75% health",
}

BUCKETS = {"accept": [], "exclude": [], "flag": []}

def classify(r):
    key = r["key"]
    fam = FAM.get(key, "")
    grp, prop, notes = r["group"], r["prop"], r["notes"]
    us = USPEC.get(key, {})
    low = (r["name"] + " " + prop + " " + notes).lower()
    ps = phase_summary(key)

    def put(b, reason):
        r["bucket"] = b
        r["reason"] = reason
        BUCKETS[b].append(r)

    # ---------- R4: do not auto-decide ----------
    if r["status"] == "proposed (FF)":
        return put("flag", "friendly fire (FF-parked block)")
    if re.search(r"\brampage\b", low):
        return put("flag", "rampage (loss of control)")
    if fam == "full_hide" or re.search(r"\b(hide|stealth|stalk|unspottable|escape|conceal)\b", low):
        return put("flag", "stealth/escape/stalk effect")
    if fam in ("tzarkan",) or "transform" in low or "shapechange" in low \
       or (us.get("spawned_unit") and re.search(r"(human_form|_form|form_|transformation)", key + " " + r["name"].lower())):
        return put("flag", "transform/shapechange")
    is_area = fam.endswith("_area") or fam == "aoe_centred_on_self" or "ground" in notes
    enemy_unit_only = ("enemy unit" in notes) and ("ground" not in notes)
    if ps["neg"] and ps["dmg"] and ps["affallies"] and is_area and not enemy_unit_only:
        return put("flag", "friendly fire (own-troop damage)")
    if ps["neg"] and ps["pos"]:
        return put("flag", "mixed positive-and-negative effect")
    # ---------- R3: clear unsuitable families -> auto-exclude ----------
    if notes.lower().find("army") >= 0 and re.search(r"(^|[^a-z])army([^a-z]|$)", notes.lower()):
        return put("exclude", "army-bar ability (standing rule 10)")
    if fam in EXCLUDE_FAM:
        return put("exclude", EXCLUDE_FAM[fam])
    # ONE genuine sourcing attempt via the game-data effect tables (engine flags)
    if us.get("spawned_unit"):
        return put("exclude", "summon")
    if us.get("vortex"):
        return put("exclude", "vortex")
    if us.get("bombardment"):
        return put("exclude", "bombardment (placed attack)")
    if re.search(r"cast on the ground\b", prop) and "under the target" not in prop \
       and "target's position" not in prop:
        return put("exclude", "ground-target-only")
    if re.search(r"\bcataclysm\b", key):
        return put("exclude", "cataclysm ability")
    if fam == "":
        return put("exclude", "no effect text available (unsourceable)")
    # ---------- R2 / R1: accept ----------
    if fam in ACCEPT_FAM:
        return put("accept", ACCEPT_FAM[fam])
    if fam in FLAG_FAM:
        return put("flag", FLAG_FAM[fam])
    return put("flag", "ambiguous / mixed net effect (needs the user)")

for r in rows:
    if r["status"] in ("proposed", "proposed (FF)"):
        classify(r)

if __name__ == "__main__":
    print("TOTAL scanned :", sum(len(v) for v in BUCKETS.values()))
    print("accept        :", len(BUCKETS["accept"]))
    print("exclude       :", len(BUCKETS["exclude"]))
    print("flag          :", len(BUCKETS["flag"]))
    print("\n--- accept by trigger ---")
    for k, v in collections.Counter(x["reason"] for x in BUCKETS["accept"]).most_common():
        print(f"{v:4d}  {k}")
    print("\n--- exclude reasons ---")
    for k, v in collections.Counter(x["reason"] for x in BUCKETS["exclude"]).most_common():
        print(f"{v:4d}  {k}")
    print("\n--- flag reasons ---")
    for k, v in collections.Counter(x["reason"] for x in BUCKETS["flag"]).most_common():
        print(f"{v:4d}  {k}")
    print("\n--- flag residual families (non-FF) ---")
    for k, v in collections.Counter((FAM.get(x['key']) or '<empty>') for x in BUCKETS["flag"] if x["status"] != "proposed (FF)").most_common():
        print(f"{v:4d}  {k}")
