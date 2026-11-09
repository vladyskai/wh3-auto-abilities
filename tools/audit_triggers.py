#!/usr/bin/env python3
"""Audit every automated ability: does its trigger match the moment its effect pays off?

For each ABILITIES key, the effect comes from the game data (build_ability_database's own
effect text: stat lines plus who it affects), and the trigger from the mod. Each rule below is a
standing user rule or a mismatch already found once; a flagged row is a CANDIDATE for review,
never a decision (the user reserves trigger design).

  R1  a buff that only helps SHOOTING rides a trigger with no shooting arm      (round 131)
  R2  a buff that helps BOTH melee and shooting rides a melee-only trigger        (user, 2026-11-01:
      Embers of the Phoenix, Horn of Vaul, Enchanted Metallurgy "could use an upgrade")
  R3  a melee-only stat rides a trigger with a missile arm                        (rule 10)
  R4  an enemy speed reduction rides a trigger that is neither melee nor charge   (rule 10)
  R5  protection against SHOTS (missile resistance / block) rides a melee trigger (pays off when
      the unit is under fire; the mod reads is_under_missile_attack)
  R6  a morale effect (Leadership +, Unbreakable, Immune to Psychology) rides a
      trigger with no morale read                                                 (wavering triggers exist)
  R7  a speed buff on the unit itself rides a melee-only trigger                  (speed pays off before contact)

Run:  uv run --with openpyxl python tools/audit_triggers.py   ->  docs/WH3_trigger_audit_<date>.md
"""
import collections
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ability_database as bd

OUT = os.path.join(r"C:\Users\vlady\Desktop\WH3_mod\docs",
                   "WH3_trigger_audit_%s.md" % datetime.date.today().isoformat())

MELEE_ONLY_TRIG = {"melee_unwavering", "melee", "melee_low_morale", "melee_health75", "melee_skip_commanders",
                   "ally_melee_buff", "metallurgy_melee", "enemy_melee", "enemy_ground_melee",
                   "enemy_ground_melee_infantry", "enemy_melee_noncommander", "self_summon_melee", "glorious_death",
                   "verminking_wavering"}
SHOOT_TRIG = {"allies_firing_aura", "self_or_ally_shooting", "melee_or_self_or_ally_shooting",
              "melee_or_shooting_into_melee", "ally_ammo_low", "ally_missile", "no_enemy_in_range_within_boost",
              "melee_or_shooting_aura", "melee_or_shooting_self_or_ally", "self_shooting"}
MISSILE_ARM_TRIG = {"enemy_engaged_or_shot", "enemy_ground_area"}
MELEE_OR_CHARGE_TRIG = MELEE_ONLY_TRIG | {"charge_or_melee", "charge", "charge_only", "charge_or_wavering",
                                          "melee_or_self_or_ally_shooting", "melee_or_shooting_into_melee",
                                          "enemy_fast_near_ally"}  # round 135: the user's fast-enemy trigger
# Rows the user has explicitly ruled on for a rule: listed apart, never counted as candidates again.
RULED = {"R4": {
    "hunter_of_champions": "round 123: 'Hunter of champions is okay for enemy_engaged_or_shot'",
    "looming_dread": "round 135: 'Keep as is, but make sure the trigger filters for the enemy unit type' (Lord/Hero filter)",
    "book_of_secrets": "round 135: 'Keep as is' (no target filter in the game data)",
    "mark_of_the_monster": "round 135: 'Keep as is' (large single-entity filter)",
}}
RULED["R6"] = {m: "round 137: kept (%s)" % why for m, why in (
    ("change_or_die", "morale plus a combat stat, 'Keep in melee'"),
    ("rot_or_die", "morale plus a combat stat, 'Keep in melee'"),
    ("scrying_stone", "morale plus a combat stat, 'Keep in melee'"),
    ("shield_of_the_old_ones", "morale plus a combat stat, 'Keep in melee'"),
    ("the_liber_mortis", "morale plus a combat stat, 'Keep in melee'"),
    ("axe_of_men", "morale plus a combat stat, 'Keep in melee'"),
    ("ghoul_king_of_ushoran", "dedicated trigger, 'Keep all 5 for now'"),
    ("gulyas", "dedicated trigger, 'Keep all 5 for now'"),
    ("purge_the_weak", "dedicated trigger, 'Keep all 5 for now'"),
    ("slezuzus_voice", "dedicated trigger, 'Keep all 5 for now'"),
    ("verminous_fury", "dedicated trigger, 'Keep all 5 for now'"))}
MORALE_TRIG = {"wavering_self", "wavering_self_or_ally", "ally_wavering", "wavering_ally_range", "melee_low_morale",
               "charge_or_wavering", "ally_broken", "verminking_wavering", "wavering_aura"}

STAT = re.compile(r"([A-Z][A-Za-z\- .'/]+?):\s*([+\-][0-9.]+%?)")
MISSILE_UP = re.compile(r"^(Base Missile Damage|Armour-Piercing Missile Damage|Reload Skill|Accuracy|Range|"
                        r"Base Explosive Damage|Armour-Piercing Explosive Damage|scalar_missile_explosion_radius|Ammunition)$")
MELEE_STAT = re.compile(r"^(Melee Attack|Melee Defence|Base Weapon Damage|Armour-Piercing Weapon Damage|Charge Bonus|"
                        r"Bonus vs\. Infantry|Bonus vs\. Large|Weapon Strength)$")
SHOT_DEF = re.compile(r"^(Missile Resistance|Missile Block Chance)$")
SPEED = re.compile(r"^(Speed|Charge Speed|Acceleration)$")


def stats_of(effect):
    out = []
    for name, val in STAT.findall(effect or ""):
        out.append((name.strip(), val))
    return out


def main():
    entries, _, _ = bd.mod_entries()
    flags = collections.defaultdict(list)
    for e in entries:
        trig = e["trigger"]
        k = e["keys"][0]
        g = bd.game_data(k)
        eff = bd.effect_text(g)
        st = stats_of(eff)
        names = [n for n, _ in st]
        pos = [n for n, v in st if v.startswith("+")]
        neg = [n for n, v in st if v.startswith("-")]
        to_enemy = ("enemies" in eff.lower() or "(to enemies" in eff.lower()) and "allies" not in eff.lower()
        miss_up = [n for n in pos if MISSILE_UP.match(n)]
        melee_up = [n for n in pos if MELEE_STAT.match(n)]
        row = (e["name"], e["marker"], trig, eff.replace("|", "/")[:220])
        if miss_up and not melee_up and not to_enemy and trig not in SHOOT_TRIG:
            flags["R1"].append(row)
        if miss_up and melee_up and not to_enemy and trig in MELEE_ONLY_TRIG:
            flags["R2"].append(row)
        if trig in MISSILE_ARM_TRIG and names and all(MELEE_STAT.match(n) or n in ("Leadership",) for n in names) \
                and any(MELEE_STAT.match(n) for n in names):
            flags["R3"].append(row)
        if any(SPEED.match(n) for n in neg) and to_enemy and trig not in MELEE_OR_CHARGE_TRIG:
            flags["R4" + ("_ruled" if e["marker"] in RULED["R4"] else "")].append(row)
        if any(SHOT_DEF.match(n) for n in pos) and not any(MELEE_STAT.match(n) for n in pos) \
                and trig in MELEE_ONLY_TRIG and not to_enemy:
            flags["R5"].append(row)
        morale = ("Leadership" in pos or "Unbreakable (positive)" in eff or "Immune to Psychology" in eff)
        if morale and not to_enemy and trig not in MORALE_TRIG and not melee_up and not miss_up:
            flags["R6" + ("_ruled" if e["marker"] in RULED["R6"] else "")].append(row)
        # R8 (round 137): a vigour restorer (Fatigue minus, to self or allies) not on a fatigue trigger -
        # the user's one-by-one review ("the vigor buff is many times secondary to the other buffs")
        if re.search(r"Fatigue:\s*-", eff or "") and not to_enemy and trig != "tired":
            flags["R8"].append(row)
        if any(SPEED.match(n) for n in pos) and not to_enemy and trig in MELEE_ONLY_TRIG:
            flags["R7"].append(row)

    titles = {
        "R1": "R1. Shooting-only buffs on a trigger with no shooting arm",
        "R2": "R2. Melee AND shooting buffs on a melee-only trigger (the user asked to review these)",
        "R3": "R3. Melee-only debuffs on a trigger with a missile arm (rule 10)",
        "R4": "R4. Enemy slows on a trigger that is neither melee nor charge (rule 10)",
        "R5": "R5. Protection against shots on a melee-only trigger",
        "R6": "R6. Morale effects on a trigger with no morale read",
        "R7": "R7. Speed buffs on the unit itself on a melee-only trigger",
        "R8": "R8. Vigour restorers not on a fatigue trigger (the user's one-by-one review)",
    }
    L = ["# Trigger audit, %s" % datetime.date.today().isoformat(), "",
         "Every automated ability (%d entries) checked against the rules below by `tools/audit_triggers.py`. "
         "The effect is the game's own data; a flagged row is a candidate for review, not a decision." % len(entries),
         "", "| Rule | Candidates |", "|---|---:|"]
    for r in sorted(titles):
        L.append("| %s | %d |" % (titles[r], len(flags[r])))
    for r in sorted(titles):
        L += ["", "## " + titles[r], ""]
        if not flags[r]:
            L.append("None.")
            continue
        L += ["| Ability | Marker | Trigger now | Effect (game data) |", "|---|---|---|---|"]
        for n, m, t, eff in sorted(flags[r]):
            L.append("| %s | `%s` | `%s` | %s |" % (n, m, t, eff))
    for r in sorted(RULED):
        if flags[r + "_ruled"]:
            L += ["", "## %s: kept by the user's ruling (not candidates)" % r, "", "| Ability | Marker | Trigger | Ruling |", "|---|---|---|---|"]
            for n, m, t, eff in sorted(flags[r + "_ruled"]):
                L.append("| %s | `%s` | `%s` | %s |" % (n, m, t, RULED[r][m]))
    s = "\n".join(L) + "\n"
    assert "\u2014" not in s
    open(OUT, "w", encoding="utf-8", newline="\n").write(s)
    print("wrote", OUT)
    for r in sorted(titles):
        print("%s %3d  %s" % (r, len(flags[r]), titles[r]))


if __name__ == "__main__":
    main()
