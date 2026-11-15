#!/usr/bin/env python3
"""Fact sheets for open abilities, straight from the game data (gamedata\\wh3): range, uses, recharge, wind-up, the
activated projectile (damage, AP, bonuses, shots, explosion, contact effect), the ability's own phases and their stat
effects, the game's invalid target / usage flags, and the tooltip.

  uv run python tools/fact_sheet_open.py <key> [<key> ...]
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402


def tsv(name, folder=GP.GAMEDATA):
    with open(os.path.join(folder, name), encoding="utf-8-sig") as f:
        h = f.readline().rstrip("\n").split("\t")
        f.readline()
        for line in f:
            yield dict(zip(h, line.rstrip("\n").split("\t")))


USA = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}
PRJ = {r["key"]: r for r in tsv("projectiles.tsv")}
EXP = {r["key"]: r for r in tsv("projectiles_explosions.tsv")}
PH = {r["id"]: r for r in tsv("phases.tsv")}
PJ = collections.defaultdict(list)
for r in tsv("phase_junc.tsv"):
    PJ[r["special_ability"]].append(r)
STAT = collections.defaultdict(list)
for r in tsv("special_ability_phase_stat_effects.tsv", GP.UIEFF):
    STAT[r["phase"]].append("%s %s %s" % (r["stat"], r["how"], r["value"]))
ATTR = collections.defaultdict(list)
for r in tsv("phase_attribute_effects.tsv", GP.UIEFF):
    v = list(r.values())
    ATTR[v[0]].append(" ".join(v[1:]))
TF = collections.defaultdict(list)
for r in tsv("special_ability_to_invalid_target_flags_tables.tsv"):
    v = list(r.values())
    TF[v[1]].append(v[0])
UF = collections.defaultdict(list)
for r in tsv("special_ability_to_invalid_usage_flags_tables.tsv"):
    UF[r["special_ability"]].append(r["invalid_usage_flag"])
LOC = {}
for r in tsv("unit_abilities.loc.tsv"):
    v = list(r.values())
    LOC[v[0]] = v[1]


def phase_text(pid):
    p = PH.get(pid, {})
    bits = ["%s %ss" % (pid, p.get("duration", "?"))]
    for k in ("damage_amount", "hp_change_frequency", "heal_amount", "max_damaged_entities", "execute_ratio"):
        if p.get(k) not in (None, "", "0", "0.0000", "0.0"):
            bits.append("%s=%s" % (k, p[k]))
    if p.get("cant_move") == "true":
        bits.append("cant_move")
    bits += STAT.get(pid, []) + ATTR.get(pid, [])
    return "; ".join(bits)


for key in sys.argv[1:]:
    a = USA.get(key)
    print("=" * 100)
    print(key, "|", LOC.get("unit_abilities_onscreen_name_" + key, ""))
    if a is None:
        print("  NOT IN unit_special_abilities")
        continue
    print("  range %s m (min %s) | uses %s | recharge %s s | wind-up %s s | active %s s | effect_range %s | enemies %s"
          % (a["target_intercept_range"], a["min_range"], a["num_uses"], a["recharge_time"], a["wind_up_time"],
             a["active_time"], a["effect_range"], a["num_effected_enemy_units"]))
    p = PRJ.get(a["activated_projectile"])
    if p:
        print("  projectile %s: dmg %s ap %s v_inf %s v_large %s | shots %s x burst %s x volley %s | explosion %s "
              "| contact %s | magical %s | air %s | allies %s | penetration %s | central %s"
              % (p["key"], p["damage"], p["ap_damage"], p["bonus_v_infantry"], p["bonus_v_large"], p["projectile_number"],
                 p["burst_size"], p["shots_per_volley"], p["explosion_type"] or "-", p["contact_stat_effect"] or "-",
                 p["is_magical"], p["can_target_airborne"], p["can_damage_allies"], p["projectile_penetration"],
                 p["prefer_central_targets"]))
        if p["contact_stat_effect"]:
            print("    contact phase:", phase_text(p["contact_stat_effect"]))
        e = EXP.get(p["explosion_type"])
        if e:
            print("    explosion: radius %s, dmg %s ap %s, affects allies %s, contact %s"
                  % (e.get("detonation_radius"), e.get("detonation_damage"), e.get("detonation_damage_ap"),
                     e.get("affects_allies"), e.get("contact_phase_effect")))
            if e.get("contact_phase_effect"):
                print("    explosion phase:", phase_text(e["contact_phase_effect"]))
    for j in sorted(PJ.get(key, []), key=lambda r: r["order"]):
        who = "/".join(w for w, f in (("self", "target_self"), ("friends", "target_friends"), ("enemies", "target_enemies"))
                       if j[f] == "true")
        print("  phase (%s): %s" % (who, phase_text(j["phase"])))
    print("  invalid targets:", ", ".join(TF.get(key, [])) or "-")
    print("  invalid usage:", ", ".join(UF.get(key, [])) or "-")
    print("  tooltip:", LOC.get("unit_abilities_tooltip_text_" + key, "")[:400])
