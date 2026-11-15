#!/usr/bin/env python3
"""Round 159: the tracker rows (28 implemented, 5 closed by the user) and section 10.37, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 159 (2026-11-15):** group E, user ruling \"%s\"."
MU = ("implemented (in melee: melee_unwavering)",
      "When armed, casts on self when this unit is in melee and not wavering (a blast centred on the caster that cannot "
      "hurt our units; the look-alikes Bloodstorm, Halo of Maidenly Wrath, Evisceration, Giant Leap, Gaze of Khorne).",
      "Like Bloodstorm")
MC = ("implemented (in melee, no friend near: melee_clear)",
      "When armed, casts on self when this unit is in melee and not wavering AND none of our other units are within %d m "
      "(its %d m blast, which hurts our units too, + 10 m).", "Melee, no friend near")
FD = ("implemented (flying over enemies: fly_dive)",
      "When armed, casts on self when this unit is FLYING, an enemy is within 7 m of its centre (70% of the 10 m blast) "
      "and none of our other units are within 20 m (the blast hurts our units too).", "Flying over enemies")
LA = "Look-alike set"
ROWS = {
    "wh2_dlc15_character_abilities_burp_of_grom_0": MU, "wh2_dlc15_character_abilities_burp_of_grom_1": MU,
    "wh2_dlc15_character_abilities_burp_of_grom_2": MU, "wh2_dlc15_item_abilities_blood_forged_armour": MU,
    "wh3_dlc23_item_abilities_daemon_flask_of_ashak": MU, "wh3_dlc29_mount_abilities_feaster_of_souls": MU,
    "wh3_dlc27_item_abilities_spurting_bile_blood": MU, "wh3_main_character_abilities_arsebelcher": MU,
    "wh3_dlc20_unit_abilities_violent_wind": MU, "wh3_dlc27_lord_abilities_whirlwind_of_pleasure": MU,
    "wh2_dlc14_weapon_abilities_whirl_of_weeping_blades": MU, "wh3_dlc25_character_abilities_hurricane_of_death": MU,
    "wh3_dlc26_unit_abilities_acid_vomit": MU,
    "wh3_main_character_abilities_groundbreaker": (MC[0], MC[1] % (20, 10), MC[2]),
    "wh3_main_lord_abilities_burning_rage": (MC[0], MC[1] % (25, 15), MC[2]),
    "wh2_dlc17_lord_abilities_bloodbeast": (MC[0], MC[1] % (25, 15), MC[2]),
    "wh2_dlc13_unit_abilities_emergency_vent": (MC[0], MC[1] % (25, 15), MC[2]),
    "wh3_dlc25_unit_abilities_marienburg_land_mines": (MC[0], MC[1] % (35, 25), MC[2]),
    "wh2_dlc15_unit_abilities_emberstorm": FD, "wh3_dlc24_unit_abilities_moon_flare": FD,
    "wh3_dlc26_unit_abilities_maneater_smoke_bomb": (
        "implemented (charge or melee: charge_or_melee)",
        "When armed, casts on self when this unit charges or is in melee (+24 melee defence, speed x1.25: the look-alike "
        "Smoke Bomb).", LA),
    "wh2_main_character_abilities_verminous_valour": (
        "implemented (wavering: wavering_self)", "When armed, casts on self when this unit is wavering (+8 morale, speed "
        "x1.25).", LA),
    "wh3_main_unit_abilities_stun_bomb": (
        "implemented (enemy in melee, on its ground: enemy_ground_melee)",
        "When armed, casts on the ground under the closest enemy within 52 m that is fighting in melee (enemies within "
        "35 m: melee attack and melee defence -24 for 31 s; one use).", LA),
    "wh2_dlc15_character_abilities_slimy_smoothie": (
        "implemented (hurt unit in the area, on its ground: health_aura_ground)",
        "When armed, casts on the ground under this unit or the most hurt friendly unit within 24 m (70% of the 35 m "
        "area) at or below 75% health (the look-alike Gulyas).", LA),
    "wh2_dlc11_item_abilities_slann_gold": (
        "implemented (most valuable Lord/Hero, the spellcaster proxy: enemy_commander_value)",
        "When armed, casts on the most valuable enemy Lord or Hero within 140 m (the game allows spellcasters only; a "
        "non-caster is refused by the engine; the look-alike Dweomer Leach Orb).", LA),
    "wh2_dlc14_lord_abilities_deathmasters_sigil": (
        "implemented (most valuable grounded Lord/Hero, none of ours near: enemy_commander_value)",
        "When armed, casts on the most valuable enemy Lord or Hero within 70 m that is not flying, with none of our units "
        "within 25 m of it (its 15 m blast hurts our units too, + 10 m).", LA),
    "wh_dlc08_item_abilities_ancient_frost_wyrm_scale": (
        "implemented (a blob attack with a vortex blast: enemy_blob_vortex)",
        "When armed and standing still, casts at the enemy infantry within 21 m where its 7 m frost vortex destroys the "
        "most value, when it covers enough soldiers and none of ours are within 17 m.", LA),
    "wh3_main_unit_abilities_necrotic_explosion": (
        "implemented (last stand, no friend near: last_stand_clear)",
        "When armed, casts on self when this unit is at 10% health or less in melee and none of our other units are "
        "within 25 m (the Nurglings destroy themselves; the 15 m blast hurts our units too, + 10 m).",
        "Close 5, Necrotic last"),
}
CLOSE = {
    "wh3_dlc29_lord_abilities_mist_form": "a teleport: where to go is the player's call",
    "wh3_dlc29_lord_abilities_warp_step": "a teleport: where to go is the player's call",
    "wh3_dlc27_unit_abilities_burrow": "a tunnelling teleport: where to go is the player's call",
    "wh2_main_weapon_abilities_sword_of_teclis": "the user's own 2026-10-08 skip (magic scope) kept; rule 10: it only "
                                                 "helps before a friendly spell",
    "wh2_dlc10_quest_abilities_unidentified_hydra_head": "a random effect; a 35 m blast for 45 s that hurts our units",
}
SECTION = """

### 10.37 Round 159 - group E: the self-centred blasts, buffs and hexes (2026-11-15)

**Earlier status:** "excluded (auto: vortex)" (the 2026-10-09 R3 auto-exclusion; no user decision), except Sword of
Teclis (user, 2026-10-08: "Skip - it's a magic-resource ability (excluded scope)"). The blast facts come from the game's
vortex table (`gamedata\\wh3\\battle_vortexs.tsv`, extracted this round).

**Rulings (2026-11-15).**

- **13 blasts that cannot hurt our units** (Burp of Grom x3, Blood-Forged Armour, Daemon Flask of Ashak, Feaster of
  Souls, Spurting Bile-Blood, Arsebelcher, Violent Wind, Whirlwind of Pleasure, Whirl of Weeping Blades, Hurricane of
  Death, Acid Burps): "Like Bloodstorm" -> `melee_unwavering`.
- **5 blasts that do** (Groundbreaker, Burning Rage, Bloodbeast, Emergency Vent, Land Mine): "Melee, no friend near" ->
  NEW `melee_clear` (none of our other units within blast + 10 m; the GENERATED `FOURTH.VORTEX_TEXT`).
- **The Phoenix dives** (Emberstorm, Moon Flare; flying only): "Flying over enemies" -> NEW `fly_dive`. The first
  proposal ("in melee and flying") was corrected before the build: a flier that lands to fight is not flying.
- **Buffs and hexes:** "Look-alike set" -> Maneater Smoke Bomb `charge_or_melee`, Verminous Valour `wavering_self`,
  Heaven's Flash `enemy_ground_melee`, Slime Smoothie `health_aura_ground`, Slann Gold and Deathmaster's Sigil
  `enemy_commander_value` (the Sigil: NEW class `commander_ground`, target kept 25 m clear of our units), Ancient Chaos
  Frost Dragon Scale NEW `enemy_blob_vortex` (the blob rule with its 7 m vortex).
- **"Close 5, Necrotic last":** Necrotic Explosion -> NEW `last_stand_clear`; Mist Form, Shadowstrider, Deep Tunneling,
  Sword of Teclis and the Unidentified Hydra Head closed (`rejected`).

**Arithmetic.**

- **Rows:** implemented 889 + 28 = **917 rows / keys**; not implemented among the included 234 - 28 = **206**, of which
  27 + 5 = **32** skipped by the user. **Open: 0.**
- **The mod:** 834 + 26 = **860 entries / 917 keys**; **88** families.
- **Tests:** harness 158 full suite **6,760 checks / 0 failures**, run twice byte-identical. RED 22/22.
- **Install:** pack md5 `23b088aada7c4f68ab59601e6aabc1df`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k in list(ROWS) + list(CLOSE):
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if k in ROWS:
                st, pr, rule = ROWS[k]
                c[1] = "`%s`" % st
                c[3] = pr
                c[4] = c[4] + NOTE % rule
            else:
                c[1] = "`rejected (user 2026-11-15: \"Close 5, Necrotic last\"; %s)`" % CLOSE[k]
                c[3] = "Not automated (user decision 2026-11-15)."
                c[4] = c[4] + NOTE % "Close 5, Necrotic last"
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
want = set(ROWS) | set(CLOSE)
assert done == want, sorted(want - done)
s = "\n".join(lines)
assert "### 10.37" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows (%d implemented, %d closed) + section 10.37" % (len(done), len(ROWS), len(CLOSE)))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_wavering": '
NEW = ('        "melee_clear": "In melee and not wavering (the melee_unwavering rule) AND none of our OTHER units within the '
       'blast radius (the GENERATED VORTEX table: the game marks the blast affects_allies) + 10 m of the caster\'s centre. '
       'Cast on self.",\n'
       '        "fly_dive": "FLYING (is_currently_flying() exactly true: the game\'s grounded rule), a visible enemy within 70% '
       'of the blast radius of the caster\'s centre, and none of our other units within the blast radius + 10 m. Cast on '
       'self.",\n'
       '        "last_stand_clear": "Own health at or below 10% while in melee, and none of our other units within the '
       'blast radius + 10 m (the blast destroys the caster and hurts our units). Cast on self.",\n'
       '        "enemy_blob_vortex": "The enemy_blob rule with a VORTEX blast (the GENERATED VORTEX table): standing still; '
       'the visible enemy infantry in range where the blast destroys the most value, covering enough soldiers, none of '
       'ours within blast + 10 m. Casts on that enemy; re-checked before the cast.",\n' + OLD)
assert d.count(OLD) == 1 and "melee_clear" not in d
d = d.replace(OLD, NEW)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 4 family texts")
