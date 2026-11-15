#!/usr/bin/env python3
"""Round 156: the tracker rows (11 implemented) and section 10.34, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 156 (2026-11-15):** the magic missiles, user ruling \"%s\"."
LS = ("implemented (most valuable large, else most armour: enemy_large_shot)",
      "When armed, casts on the most valuable large enemy within %d m with none of our units within 10 m of it, otherwise "
      "on the most armoured such enemy infantry; the caster must be out of melee.", "Large first, then armour")
ROWS = {
    "wh2_dlc10_item_bound_blast": (LS[0], LS[1] % 70, LS[2]),
    "wh3_main_weapon_abilities_godkiller_pistol": (LS[0], LS[1] % 70, LS[2]),
    "wh_dlc03_weapon_abilities_hunting_spear": (LS[0], LS[1] % 140, LS[2]),
    "wh2_dlc17_rune_abilities_master_rune_of_flight": (LS[0], (LS[1] % 70) + " Never closer than 5 m (the game's "
                                                       "minimum range).", LS[2]),
    "wh3_dlc27_item_abilities_schalkains_teeth": (LS[0], LS[1] % 140, LS[2]),
    "wh3_dlc26_character_abilities_dead_eye": (
        "implemented (most valuable single entity: enemy_single_shot)",
        "When armed and standing still, casts on the most valuable single-entity enemy (lord, hero, single monster) "
        "within 105 m with none of our units within 10 m of it; the caster must be out of melee.",
        "Most valuable single"),
    "wh2_dlc13_lord_abilities_kill_shot": (
        "implemented (most valuable single entity, large first: enemy_single_shot)",
        "When armed and standing still, casts on the most valuable LARGE single-entity enemy within 175 m (any single "
        "entity when no large one qualifies) with none of our units within 10 m of it; the caster must be out of melee.",
        "Most valuable single"),
    "wh3_main_character_abilities_crippling_throw": (
        "implemented (enemy in melee or charging: enemy_melee_or_fast)",
        "When armed and out of melee, casts on the closest enemy within 84 m that is fighting in melee, otherwise on a "
        "fast enemy closing on our units.", "Split by effect"),
    "wh2_dlc17_weapon_abilities_the_golden_blowpipe_of_ptoohee": (
        "implemented (enemy in melee or charging: enemy_melee_or_fast)",
        "When armed, casts on the closest enemy within 140 m (not closer than 5 m) that is fighting in melee, otherwise "
        "on a fast enemy closing on our units.", "Split by effect"),
    "wh_dlc05_weapon_abilities_spear_of_kurnous": (
        "implemented (enemy in melee or shooting: enemy_melee_or_shooting)",
        "When armed, casts on the closest enemy within 140 m that is fighting in melee, otherwise on the closest enemy "
        "missile unit that is shooting.", "Split by effect"),
    "wh3_main_weapon_abilities_nuku_chos_crossbow": (
        "implemented (most valuable infantry: enemy_infantry_shot)",
        "When armed, standing still and out of melee, casts on the enemy infantry within 175 m worth the most per "
        "soldier, with none of our units within 10 m of it.", "Most valuable infantry"),
}
SECTION = """

### 10.34 Round 156 - open batch 4: the magic missiles (2026-11-15)

**Earlier status:** "excluded (impossible: no enemy-unit read)" or "excluded (auto: explosive projectile)", written
before the round-145 map existed; no user decision.

**Rulings (2026-11-15).**

- **AP shots** (Blast, Damned Pistol, Hunting Spear, Master Rune of Flight, Schalkain's Teeth): "Large first, then
  armour" -> NEW `enemy_large_shot`. Claude recommended large only; the user added the armour fallback.
- **Snipers** (Dead Eye, Focused Shot; the game allows single entities only): "Most valuable single" -> NEW
  `enemy_single_shot`, standing still. Focused Shot (+120 against large) takes a large one first.
- **Debuff throws:** "Split by effect" -> NEW `enemy_melee_or_fast` (Crippling Throw, the Golden Blowpipe: they slow
  the target) and NEW `enemy_melee_or_shooting` (Spear of Kurnous: blinded, accuracy and melee stats).
- **Bolt Storm:** "Most valuable infantry" -> NEW `enemy_infantry_shot`, standing still.
- **Safety** (in the approved options): none of our units within 10 m of a map target; the caster out of melee.

**Arithmetic.**

- **Rows:** implemented 854 + 11 = **865 rows / keys**; not implemented among the included 269 - 11 = **258**
  (27 skipped).
- **The mod:** 799 + 11 = **810 entries / 865 keys**; **80** families.
- **Tests:** harness 155 full suite **6,579 checks / 0 failures**, run twice byte-identical. RED 10/10.
- **Install:** pack md5 `4075645f56fcec8c08d10d53106fcf00`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, (st, pr, rule) in ROWS.items():
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % st
            c[3] = pr
            c[4] = c[4] + NOTE % rule
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.34" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION and not any("\u2014" in v for t in ROWS.values() for v in t)
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.34" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_wavering": '
NEW = ('        "enemy_large_shot": "The caster out of melee; the visible LARGE enemy in range with the highest live value '
       '(strategic_value), otherwise the visible enemy infantry in range with the highest armour; none of our units '
       'within 10 m of the target. Casts on that enemy; re-checked before the cast.",\n'
       '        "enemy_single_shot": "The caster STANDING STILL and out of melee; the visible single-entity enemy in range '
       '(the game\'s single-entity rule) with the highest live value, a large one first when the projectile favours '
       'large targets; none of our units within 10 m of it. Casts on that enemy; re-checked before the cast.",\n'
       '        "enemy_infantry_shot": "The caster STANDING STILL and out of melee; the visible enemy infantry in range with '
       'the highest live value per soldier; none of our units within 10 m of it. Casts on that enemy; re-checked before '
       'the cast.",\n'
       '        "enemy_melee_or_fast": "The closest enemy in range that is fighting in melee, otherwise a fast enemy closing '
       'on our units (the game\'s melee usage rule and minimum range honoured). Casts on that enemy; re-checked before '
       'the cast.",\n'
       '        "enemy_melee_or_shooting": "The closest enemy in range that is fighting in melee, otherwise the closest enemy '
       'missile unit in range that is shooting. Casts on that enemy; re-checked before the cast.",\n' + OLD)
assert d.count(OLD) == 1 and "enemy_large_shot" not in d
d = d.replace(OLD, NEW)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 5 family texts")
