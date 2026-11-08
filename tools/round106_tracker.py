# -*- coding: utf-8 -*-
"""Round 106 - tracker updates: statuses for the 32, the two new triggers, the round note."""
import re, io

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
s = open(P, encoding="utf-8").read()

GROUND = "implemented (closest in-melee infantry, enemy ground)"
UNIT = "implemented (closest in-melee infantry, enemy unit)"

# key -> (status, trigger-col, logic, extra note)
IMPL = {
 "wh2_dlc10_item_bound_assault_of_stone": (GROUND, "Assault of Stone"),
 "wh3_main_weapon_abilities_axe_of_tor": (GROUND, "Axe of Tor"),
 "wh3_main_mount_bound_celestial_comet": (GROUND, "Celestial Comet"),
 "wh3_main_mount_bound_celestial_lightning": (GROUND, "Celestial Lightning"),
 "wh_dlc07_item_abilities_chalice_of_potions": (GROUND, "Chalice of Potions"),
 "wh3_main_spell_bound_comet_of_casandora": (GROUND, "Comet of Casandora"),
 "wh_dlc08_item_abilities_great_horn_of_dragon_ogre": (GROUND, "Dragon Ogre's Great Horn"),
 "wh3_dlc23_lord_abilities_flame_and_shadow": (GROUND, "Flame & Shadow"),
 "wh_dlc05_weapon_abilities_hawks_talon": (GROUND, "Hawk's Talon"),
 "wh2_dlc13_character_ability_ishas_rain": (GROUND, "Isha's Rain"),
 "wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded": (GROUND, "Klad Brakak"),
 "wh2_dlc10_spell_bound_lesser_doombolt": (UNIT, "Lesser Doombolt"),
 "wh3_dlc29_unit_abilities_lightning_strike": (GROUND, "Lightning Strike"),
 "wh_main_lord_abilities_lord_of_the_storm": (GROUND, "Lord of the Storm"),
 "wh3_dlc29_spell_bound_warp_lightning": (GROUND, "Master of Lightning"),
 "wh3_dlc29_unit_abilities_meteor_strike": (GROUND, "Meteor Strike"),
 "wh3_dlc25_lord_abilities_nemesis_crown": (GROUND, "Nemesis Crown"),
 "wh_main_spell_bound_piercing_bolts_of_burning": (GROUND, "Piercing Bolts of Burning"),
 "wh3_dlc25_character_abilities_pigeon_bomb": (GROUND, "Pigeon Bomb"),
 "wh2_main_spell_bound_rod_of_the_storm": (GROUND, "Rod of the Storm"),
 "wh3_dlc20_item_abilities_rod_of_torment": (UNIT, "Rod of Torment"),
 "wh2_dlc10_item_abilities_sceptre_of_stone": (GROUND, "Sceptre of Stone"),
 "wh3_twa08_spell_bound_searing_doom": (GROUND, "Searing Doom"),
 "wh3_dlc20_spell_bound_slicing_shards": (GROUND, "Slicing Shards"),
 "wh_dlc05_weapon_abilities_the_bow_of_loren": (GROUND, "The Bow of Loren"),
 "wh2_main_spell_bound_tome_of_furion": (UNIT, "Tome of Furion"),
 "wh2_dlc17_spell_bound_urannons_thunderbolt": (GROUND, "Urannon's Thunderbolt"),
 "wh2_main_spell_bound_wand_of_the_kharaidon": (UNIT, "Wand of the Kharaidon"),
 "wh3_main_weapon_abilities_the_traitors_sword": (UNIT, "Wolf's Howl"),
 "wh2_dlc11_lord_abilities_wraith_storm": (UNIT, "Wraith Storm"),
 "wh_main_spell_bound_soulfire": ("implemented (melee, skipping Lord/Hero-only fights)", "Soulfire"),
 "wh_dlc04_spell_bound_soulfire_upgraded": ("implemented (melee, skipping Lord/Hero-only fights)", "Soulfire"),
 "wh2_dlc15_unit_abilities_arachneruption": ("implemented (melee, skipping Lord/Hero-only fights)", "Arachneruption"),
}
SKIP = {
 "wh3_dlc20_cataclysm_bound_thorsens_thunderstorm": "Thorsen's Thunderstorm",
 "wh3_dlc27_cataclysm_bound_thorsens_thunderstorm": "Thorsen's Thunderstorm",
 "wh2_dlc16_unit_abilities_warp_lightning_rod": "Warp Lightning Rod",
}

LOGIC_BOMB = ("When armed, fires on the CLOSEST enemy inside the ability's own 70% bound that is "
              "IN MELEE and IS INFANTRY (battle_unit:is_infantry(), unit_class fallback, fail-closed); "
              "the strike is placed on that enemy's own ground (ground form).")
LOGIC_BOMB_UNIT = ("When armed, fires on the CLOSEST enemy inside the ability's own 70% bound that is "
                   "IN MELEE and IS INFANTRY (battle_unit:is_infantry(), unit_class fallback, fail-closed); "
                   "the row has no ground target, so the cast is on the enemy UNIT itself.")
LOGIC_SOUL = ("When armed, fires when THIS unit is in melee, unless every enemy it is engaged with is a "
              "Lord or Hero (the engagement set is read from the enemy enumerator, classified with the "
              "1,409-key commander set and logged); cast on SELF.")

changed = 0
out = []
for line in s.split("\n"):
    hit = None
    m = re.match(r"^\| ([^|]+?) `([a-z0-9_!]+)` \| `([^`]*)` \|", line)
    if m:
        key = m.group(2)
        if key in IMPL:
            hit = ("impl", key)
        elif key in SKIP:
            hit = ("skip", key)
    if hit is None:
        out.append(line)
        continue
    kind, key = hit
    parts = line.split("|")
    # parts: ['', ' Name `key` ', ' `status` ', ' trigger ', ' logic ', ' notes ', '']
    if kind == "impl":
        status, name = IMPL[key]
        trig = "melee_skip_commanders" if "soulfire" in key or "arachneruption" in key else "enemy_ground_melee_infantry"
        logic = LOGIC_SOUL if trig == "melee_skip_commanders" else (LOGIC_BOMB_UNIT if status == UNIT else LOGIC_BOMB)
        parts[2] = " `%s` " % status
        parts[3] = " %s " % trig
        parts[4] = " %s " % logic
        note = " · **round 106 (2026-10-18):** implemented (harness 106)"
        if len(parts) > 5:
            parts[5] = parts[5].rstrip() + note + " "
    else:
        parts[2] = " `skipped (round 106: %s)` " % (
            "army-bar ability (army_spec junction) - out of wheel scope"
            if "thorsens" in key else "no enemy target: target flags all false, range 0 - self-centred")
    out.append("|".join(parts))
    changed += 1
s = "\n".join(out)
print("rows rewritten:", changed)

# the two new trigger rows in the trigger glossary table
anchor = "| `enemy_melee_noncommander` | the closest enemy inside the 70% bound in melee that is NOT a Lord or Hero | ground form on that enemy's position |"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + "\n"
  "| `melee_skip_commanders` | **round 106** - the caster is IN MELEE, unless EVERY enemy it is engaged with is a Lord or Hero (the engagement set = alive + is_in_melee + edge-to-edge `unit_distance` <= 12 m, each classified with the 1,409-key commander set; logged, deduped by note) | self cast (`perform_special_ability(key, self)`) |\n"
  "| `enemy_ground_melee_infantry` | **round 106** - the CLOSEST enemy inside the ability's own 70% bound that is IN MELEE and IS INFANTRY (`battle_unit:is_infantry()`, `unit_class` exact-match fallback, fail-closed) | ground form on that enemy's position for the 24 ground-targeted keys; the unit form on the enemy for the 6 unit-targeted keys |")

# the round note, before the legend
legend = "**Legend — Status column:**"
assert s.count(legend) == 1
note = """**Update 2026-10-18 (harness 106 — THE BOMBARDMENT ROUND).** Two user-approved families are **implemented and shipping**. **(1) Soulfire** (`wh_main_spell_bound_soulfire` + `wh_dlc04_spell_bound_soulfire_upgraded`, ONE entry) and **Arachneruption** (`wh2_dlc15_unit_abilities_arachneruption`) on the NEW trigger **`melee_skip_commanders`**: fire when the caster is IN MELEE, but **SKIP when every enemy it is engaged with is a Lord or a Hero**. The engagement set is read from the game's enemy enumerator (alive + `is_in_melee()` + edge-to-edge `unit_distance()` <= **12 m** `FOURTH.ENGAGE_CONTACT_M`), each member classified by the existing **1,409-key commander set** (`unit_class() == \"com\"` fallback, fail-closed), and the judged set is **logged** (type + commander flag + the real distance) once per (unit, marker) and again only when it changes. With nothing readable in contact the caster's `current_target()` is the fallback; with neither, the plain in-melee rule fires and says so. **(2) 30 of the user's 32 bombardment abilities** on the NEW trigger **`enemy_ground_melee_infantry`**: the **CLOSEST enemy inside the ability's own 70% bound that is IN MELEE and IS INFANTRY**. Infantry is a **REAL read** - `battle_unit:is_infantry()` (API dump: \"Returns whether this is a unit of infantry\"), with `battle_unit:unit_class()` exact-match against `inf_mel` / `inf_mis` / `inf_spr` as the fallback and **FAIL CLOSED** when neither answers - the same READ-first discipline as the commander set (a derived 942-key list would miss DLC keys; the engine read cannot). The cast follows EACH row's own flags: **24 ground-targeted keys** use `perform_special_ability_ground(key, enemy position)`, **6 unit-targeted keys** (Lesser Doombolt, Rod of Torment, Tome of Furion, Wand of the Kharaidon, Wolf's Howl, Wraith Storm) use `perform_special_ability(key, enemy)`. The chosen enemy is re-checked immediately before the cast (alive, in melee, still infantry, inside the bound). **TWO OF THE 32 ARE REPORTED, NOT IMPLEMENTED:** **Thorsen's Thunderstorm** (both keys sit in `army_spec` - an ARMY-bar ability, out of wheel scope) and **Warp Lightning Rod** (target flags all false, `target_intercept_range` 0 - no enemy target exists to cast at; it is the same self-centred shape as Soulfire). **R1-R4 research** is in `docs/WH3_bombardment_research.md`. **Counts:** ABILITIES **643 -> 675 entries**, **687 -> 721 keys**, **43 -> 45 evaluators**; `enemy_ground_melee_infantry` **30**, `melee_skip_commanders` **2**. Spreadsheet: `docs/WH3_abilities_master_v7_2026-10-17.xlsx` (v7 supersedes v6; v1-v6 unchanged).

"""
s = s.replace(legend, note + legend, 1)
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker written")
