#!/usr/bin/env python3
"""Round 131: the tracker rows and section 10.12, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"

AURA = "implemented (firing aura: allies_firing_aura)"
AP = ("When this unit or a friendly unit within %d m (70%% of the %d m aura) is shooting past its cast point: "
      "cast on self (the aura).")
NOTE = " · **round 131 (user ruling 2026-11-01):** %s"
ROWS = {
    "wh3_dlc25_lord_abilities_deranged_munitions_upgraded": (AURA, AP % (24, 35), "moved off the melee trigger: a shooting buff spent in melee did nothing; the caster counts."),
    "wh2_dlc11_character_abilities_ballistic_enchantment": (AURA, AP % (38, 55), "moved off the melee trigger; the caster counts."),
    "wh2_dlc13_lord_abilities_funnel_of_flame": (AURA, AP % (38, 55), "moved off the melee trigger; the caster counts."),
    "wh2_dlc13_lord_abilities_hail_of_fire": (AURA, AP % (38, 55), "moved off the melee trigger; the caster counts."),
    "wh2_main_item_abilities_the_guiding_eye": (AURA, AP % (38, 55), "moved off the melee trigger; the caster counts."),
    "wh3_dlc23_item_abilities_morgrims_eye": (AURA, AP % (24, 35), "moved off the melee trigger; the caster counts."),
    "wh3_main_character_abilities_locus_of_change": (AURA, AP % (38, 55), "moved off the melee trigger; the caster counts."),
    "wh_main_hero_abilities_ballistics_calibration": (None, "When this unit or a friendly unit within 38 m (70% of the 55 m aura) is shooting past its cast point: cast on the ground at the caster's own feet.",
        "the round-130 rule (2 allies) redone: 1 shooter is enough and the caster counts."),
    "wh3_dlc25_lord_abilities_deranged_munitions": ("implemented (self or a shooting ally: self_or_ally_shooting)",
        "When the caster is shooting past its cast point: cast on self; otherwise on the closest ally within 70 m (70% of 100 m) that is shooting past its cast point.",
        "\"Self, else a shooting ally\"."),
    "wh_main_unit_abilities_entrenchment": ("implemented (melee, or self or a shooting ally: melee_or_self_or_ally_shooting)",
        "In melee (the +20 physical resistance): cast on self. Otherwise when the caster is shooting: on self; otherwise on the closest ally within 105 m (70% of 150 m) that is shooting. The target cannot move for 44 s.",
        "shooting, and also in melee; \"Self, else a shooting ally\"."),
    "wh3_main_item_abilities_potion_of_farsight": ("implemented (out of range, inside the boosted range: no_enemy_in_range_within_boost)",
        "When no enemy is inside the unit's own missile range but at least one is inside range x 1.21 (the 70% rule on the +30% bonus): cast on self. Not in melee; ammunition left.",
        "the user's own design: the potion only helps when the enemy is just out of reach."),
}
STANCE = "skipped (user decision 2026-11-01: stances are not automated; a stance chooser is last priority)"
STANCES = ["wh2_dlc17_lord_abilities_master_predator", "wh3_dlc26_unit_abilities_immovable_bulwark",
           "wh3_dlc26_unit_abilities_unstoppable_choppas", "wh_dlc05_unit_abilities_the_shadows_coil",
           "wh_dlc05_unit_abilities_woven_mist", "wh3_dlc27_lord_abilities_chanson_of_caging",
           "wh3_dlc27_lord_abilities_the_dance_of_dreaming", "wh3_dlc27_lord_abilities_the_praise_of_slaanesh",
           "wh3_dlc27_lord_abilities_the_waltz_of_lethargy"]
for k in STANCES:
    ROWS[k] = (STANCE, "Not automated: a stance.", "\"For now, all stances should not have any automation ... the stance logic should evaluate all the available mutually exclusive stances to the unit and decide which to activate.\" Removed from the mod.")

SECTION = """

### 10.12 Round 131 - the shooting buffs leave the melee trigger; the stances leave the mod (2026-11-01)

**Rulings (2026-11-01).** On the ten shooting buffs that rode `melee_unwavering`: a shooting trigger for Deranged
Munitions, Enchanted Ballistics, Funnel of Flame, Hail of Fire, The Guiding Eye, Morgrim's Eye and Locus of Change;
Entrenchment "can be activated when in melee, because of the physical resistance". The auras: *"Fires when at least
1 ally (caster counts) inside the aura's 70% bound is shooting. Actually, the previous trigger where the trigger was
required 2 allies should be redone."* Deranged Munitions (base) and Entrenchment: *"Self, else a shooting ally"*.
Potion of Farsight, the user's own design: fire only when no enemy is in the unit's range but one would be with the
potion; the band is range x 1.21 (the 70% rule on the +30%). Stances: *"For now, all stances should not have any
automation"*; remove all 9 now.

- `allies_firing_aura` now counts the caster and needs 1 shooter (Ballistics Calibration included): 8 entries.
- `self_or_ally_shooting` (NEW): Deranged Munitions. `melee_or_self_or_ally_shooting` (NEW): Entrenchment.
- `no_enemy_in_range_within_boost` (NEW): Potion of Farsight.
- Removed (skipped by user decision): Master Predator, Immovable Bulwark, Unstoppable Choppas, The Shadow's Coil,
  Woven Mist, Chanson of Caging, The Dance of Dreaming, The Praise of Slaanesh, The Waltz of Lethargy.

**Arithmetic.** Implemented rows 761 - 9 = **752 rows / 752 keys**; not implemented among the included 362 + 9 =
**371** (13 + 9 = 22 skipped by user decision). The mod: 709 -> **700 entries**, 761 -> **752 keys**, 49 -> **52
trigger families**, melee_unwavering 373 -> 354. Harness 130 full suite: **5,638 checks / 0 failures**, run twice
byte-identical; RED on the round-130 build 8/8. Installed pack md5 `b7efc16df23c1a00f71eb7880dc244ca`.
"""


def rewrite(line, key, status, proposal, note):
    c = line.strip().strip("|").split("|")
    c = [x.strip() for x in c]
    assert len(c) >= 5 and "`%s`" % key in c[0], (key, c[:2])
    if status:
        c[1] = "`%s`" % status
    if key in STANCES:
        c[2] = "skipped"
    elif status:
        c[2] = "ally_unit" if "shooting ally" in status else "self"
    c[3] = proposal
    c[4] = c[4] + NOTE % note
    return "| " + " | ".join(c) + " |"


lines = open(TRACKER, encoding="utf-8", newline="").read().split("\n")
done = set()
for i, l in enumerate(lines):
    for k, (st, pr, nt) in ROWS.items():
        if l.startswith("| ") and ("`%s` |" % k) in l and l.split("|")[1].strip().endswith("`%s`" % k):
            assert k not in done, k
            lines[i] = rewrite(l, k, st, pr, nt)
            done.add(k)
assert done == set(ROWS), set(ROWS) - done
s = "\n".join(lines)
assert "### 10.12" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.12" % len(done))

d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "allies_firing_aura": "At least `FOURTH.BALLISTICS_MIN_FIRING` (2) allies inside the aura bound are SHOOTING past their cast point (first shot + 0.5 x their reload). Cast on the ground at the caster\'s own position.",\n'
NEW = ('        "allies_firing_aura": "At least `FOURTH.FIRING_AURA_MIN` (1) unit inside the aura bound, the caster counting, is SHOOTING past its cast point (first shot + 0.5 x its reload). Ballistics Calibration is cast on the ground at the caster\'s own position; the other auras on the caster.",\n'
       '        "self_or_ally_shooting": "The caster SHOOTING past its cast point: cast on itself. Otherwise the closest ally in range that is shooting past its cast point: cast on that ally.",\n'
       '        "melee_or_self_or_ally_shooting": "In melee and not wavering (as melee_unwavering): cast on itself. Otherwise as self_or_ally_shooting (the caster shooting, else the closest shooting ally in range).",\n'
       '        "no_enemy_in_range_within_boost": "Not in melee, ammunition left, NO live enemy inside the unit\'s own missile_range(), and at least one inside missile_range x `FOURTH.FARSIGHT_BAND` (1 + 0.30 x 0.70 = 1.21). Casts on the unit itself.",\n')
CT_OLD = '        "allies_firing_aura": "the ground at the caster\'s own position (ground form)",\n'
CT_NEW = ('        "allies_firing_aura": "the caster (Ballistics Calibration: the ground at the caster\'s own position)",\n'
          '        "self_or_ally_shooting": "the caster when it shoots, otherwise the closest shooting ally",\n'
          '        "melee_or_self_or_ally_shooting": "the caster in melee or when it shoots, otherwise the closest shooting ally",\n')
for a, b in ((OLD, NEW), (CT_OLD, CT_NEW)):
    assert d.count(a) == 1, a[:60]
    d = d.replace(a, b)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 4 family texts + 3 cast targets")
