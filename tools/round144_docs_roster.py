#!/usr/bin/env python3
"""Round 144: the tracker rows (10 implemented + 3 decided) and section 10.26, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 144 (2026-11-13):** open batch 3, user ruling \"%s\"."
ROWS = {
    "wh3_dlc24_unit_abilities_hags_denial": ("implemented (last stand: self_last_stand)",
        "When armed, fires when the unit is at 10% health or less while in melee or under missile fire: cast on self.",
        "10%, melee or fire"),
    "wh2_dlc15_unit_abilities_mimic_ruinshelter": ("implemented (in melee: melee_unwavering)",
        "When armed, fires when the unit is in melee and not wavering: cast on self.", "in melee"),
    "wh3_main_banner_abilities_banner_of_hellfire": ("implemented (in melee: melee_unwavering)",
        "When armed, fires when the unit is in melee and not wavering: cast on self (the damage aura hits the enemies "
        "in contact).", "in melee"),
    "wh2_dlc15_unit_abilities_rock_bottom": ("implemented (no ammunition left: self_out_of_ammo)",
        "When armed, fires when the unit has no ammunition left: cast on self.", "wait until no ammo left"),
    "wh3_dlc29_item_abilities_morikhane_the_black_armour": ("implemented (under fire: under_fire)",
        "When armed, fires when the wearer is under missile fire: cast on self.", "under fire"),
    "wh2_dlc13_character_ability_hunters_call": ("implemented (melee or wavering aura: melee_or_wavering_aura)",
        "When armed, fires when the unit or a friendly unit within 24 m is in melee or wavering: cast on self.",
        "like Stand Your Ground"),
    "wh3_dlc29_item_abilities_icon_of_the_king": ("implemented (non-living aura heal: health_aura_self_undead)",
        "When armed, fires when the unit or a non-living friendly unit within 24 m is at 75% health or less: cast on "
        "self.", "heals only non-living allies"),
    "wh3_dlc25_item_abilities_the_gold_standard": ("implemented (hurt ally in melee: ally_hurt_melee)",
        "When armed, casts on the most hurt friendly unit within 70 m (75% health or less) that is in melee.",
        "the lowest-health ally in melee"),
    "wh3_dlc29_hero_active_ghostly_howl": ("implemented (wavering enemy: enemy_wavering)",
        "When armed, casts on the closest wavering enemy within 52 m (the game only allows an enemy below half "
        "morale).", "the closest wavering enemy"),
    "wh3_dlc24_unit_passive_petrifying_gaze": ("implemented (fast enemy: enemy_fast_near_ally)",
        "When armed, casts on the closest enemy within 35 m moving at 5 m/s or more within 40 m of one of our units.",
        "fast enemy (the immobiliser ruling)"),
}
STANCE = ("skipped (user decision 2026-11-13: a stance; stances are not automated, a stance chooser is last priority)",
          "Not automated: a stance.", "Skip all three (stances)")
DECIDED = {
    "wh_dlc05_unit_abilities_storm_of_blades": STANCE,
    "wh2_dlc16_unit_abilities_whirling_death": STANCE,
    "wh2_dlc09_item_abilities_cloak_of_the_dunes": ("rejected (stealth/escape effect)",
                                                    "Not automated: a stealth effect (2026-10-09 family ruling).",
                                                    "Skip all three (stealth)"),
}
SECTION = """

### 10.26 Round 144 - open batch 3: the rest of group C (2026-11-13)

**Earlier status:** "excluded (auto: no effect text available)", from before the game data could be read; no user
decision.

**Rulings (2026-11-13).**

- **Hag's Denial** (Cannot Die + damage resistance +40 for 44 s, one use): "10%, melee or fire" -> NEW
  `self_last_stand`. (Claude first proposed 50% and was rightly corrected: 50% did not match "about to die".)
- **Rock Bottom** (Rogue Idol RoR: refills 30% of its ammunition for 350 damage to itself): "wait until no ammo left"
  -> NEW `self_out_of_ammo`.
- **Ruinshelter**, **Banner of Hellfire:** in melee -> `melee_unwavering`. **Morikhane:** under fire -> `under_fire`.
- **Hunter's Call:** like Stand Your Ground -> `melee_or_wavering_aura` (24 m).
- **Icon of the King** (the game excludes living units): NEW `health_aura_self_undead` (the generated undead set).
- **The Gold Standard:** the lowest-health ally in melee -> NEW `ally_hurt_melee` (70 m).
- **Ghostly Howl** (the game only targets an enemy below half morale): NEW `enemy_wavering` (52 m).
- **Petrifying Gaze:** the round-136 immobiliser ruling -> `enemy_fast_near_ally` (35 m).
- **Skipped:** Storm of Blades and Whirling Death (stances on the Wardancer / Bladesinger units), Cloak of the Dunes
  (stealth, the 2026-10-09 family ruling).

**Arithmetic.**

- **Rows:** implemented 767 + 10 = **777 rows / keys**; not implemented among the included 356 - 10 = **346**
  (24 + 3 = **27 skipped**).
- **The mod:** 712 + 10 = **722 entries / 777 keys**; **73** families.
- **Tests:** harness 143 full suite **6,273 checks / 0 failures**, run twice byte-identical. RED 10/10.
- **Install:** pack md5 `826ef8834fbc437c35ecc86a298b931e`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, (st, pr, rule) in list(ROWS.items()) + list(DECIDED.items()):
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % st
            if k in DECIDED:
                c[2] = "skipped" if st.startswith("skipped") else "rejected"
            c[3] = pr
            c[4] = c[4] + NOTE % rule
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS) | set(DECIDED), sorted(set(ROWS) | set(DECIDED) - done)
s = "\n".join(lines)
assert "### 10.26" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.26" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "self_recharging": '
NEW = ('        "self_last_stand": "The unit\'s OWN health at or below 10% (`FOURTH.LAST_STAND_PCT`, fail-closed) while in '
       'melee or under missile fire. Casts on the unit itself.",\n'
       '        "self_out_of_ammo": "The unit\'s OWN `ammo_left()` reads 0 (no ammunition left). Casts on the unit itself.",\n'
       '        "health_aura_self_undead": "The OWNER or a NON-LIVING friendly unit (the generated undead set) inside the '
       'self-centred aura is at or below 75% health. Casts on the caster; re-checked before the cast.",\n'
       '        "ally_hurt_melee": "The lowest-health unit in range (owner or ally) at or below 75% health that is IN MELEE. '
       'Casts on that unit; re-checked (still in melee) before the cast.",\n'
       '        "enemy_wavering": "The closest enemy in range whose `is_wavering()` reads exactly true. Casts on that enemy; '
       're-checked (still wavering) before the cast.",\n' + OLD)
assert d.count(OLD) == 1 and "self_last_stand" not in d
d = d.replace(OLD, NEW)
OLD2 = '        "health_aura_self": "the caster",\n'
assert d.count(OLD2) == 1
d = d.replace(OLD2, OLD2 + '        "health_aura_self_undead": "the caster",\n')
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 5 family texts + 1 cast target")
