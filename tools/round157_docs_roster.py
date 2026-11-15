#!/usr/bin/env python3
"""Round 157: the tracker rows (12 implemented) and section 10.35, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
NOTE = " · **round 157 (2026-11-15):** the drains and the Executioner, user ruling \"%s\"."
DS = ("implemented (most valuable single entity, standing still: enemy_single_drain)",
      "When armed and standing still, casts on the most valuable single-entity enemy (lord, hero, single monster) "
      "within %d m, even one fighting our units (a direct effect cannot hit them).",
      "Most valuable single + Standing still")
DRAINS = ["wh2_dlc09_spell_death_spirit_leech_bound", "wh3_dlc25_spell_bound_spirit_leech",
          "wh3_dlc25_spell_bound_spirit_leech_gunnery_school", "wh3_main_spell_bound_spirit_leech",
          "wh3_twa08_spell_bound_spirit_leech_great_unclean_one_ror", "wh2_main_item_abilities_the_liber_bubonicus",
          "wh3_dlc25_item_abilities_deaths_timekeeper", "wh3_main_spell_bound_rancid_visitations",
          "wh_dlc06_character_abilities_effagee_of_da_git"]
ROWS = {k: (DS[0], DS[1] % 70, DS[2]) for k in DRAINS}
ROWS["wh3_dlc29_item_abilities_punch_dagger"] = (DS[0], DS[1] % 10, DS[2])
ROWS["wh3_dlc24_lord_abilities_the_emperors_executioner"] = (
    "implemented (at the execute line: enemy_execute)",
    "When armed, casts on the most valuable enemy Lord or Hero within 35 m whose health is at or below 20% (the "
    "execute line).", "At the execute line")
ROWS["wh3_dlc24_lord_abilities_the_emperors_executioner_upgrade"] = (
    "implemented (at the execute line: enemy_execute)",
    "When armed, casts on the most valuable single-entity enemy within 35 m whose health is at or below 33% (the "
    "execute line).", "At the execute line")
SECTION = """

### 10.35 Round 157 - open batch 5: the drains and the Executioner (2026-11-15)

**Earlier status:** "excluded (impossible: no enemy-unit read)", written before the round-145 map; no user decision.

**Rulings (2026-11-15).**

- **The drains** (Spirit Leech x5, The Liber Bubonicus, Death's Timekeeper, Rancid Visitations, 'Effagee' of da Git,
  Punch-Dagger; about 870 damage on ONE model over 10-15 s, the game's max_damaged_entities = 1): "Most valuable
  single" -> NEW `enemy_single_drain`, and "Standing still". No 10 m margin: a direct effect cannot hit our units.
- **The Emperor's Executioner** (732 damage; execute_ratio 0.2 base, Lord/Hero only; 0.33 upgrade): "At the execute
  line" -> NEW `enemy_execute`.
- **Readings marked as unchecked in the proposal:** max_damaged_entities = one model per tick, and execute_ratio =
  killed outright below the line. Both come from the field names.

**Arithmetic.**

- **Rows:** implemented 865 + 12 = **877 rows / keys**; not implemented among the included 258 - 12 = **246**
  (27 skipped).
- **The mod:** 810 + 12 = **822 entries / 877 keys**; **82** families.
- **Tests:** harness 156 full suite **6,618 checks / 0 failures**, run twice byte-identical. RED 8/8.
- **Install:** pack md5 `c387bc7df174378acbaaa443eabe9894`.
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
assert "### 10.35" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.35" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_wavering": '
NEW = ('        "enemy_single_drain": "The caster STANDING STILL; the visible single-entity enemy in range (lord, hero, '
       'single monster) with the highest live value, even one fighting our units (a direct effect cannot hit them). '
       'Casts on that enemy; re-checked before the cast.",\n'
       '        "enemy_execute": "The most valuable enemy in range whose health is at or below the generated execute line '
       '(20% base, Lord/Hero only; 33% upgrade, single entities). Casts on that enemy; re-checked before the cast.",\n'
       + OLD)
assert d.count(OLD) == 1 and "enemy_single_drain" not in d
d = d.replace(OLD, NEW)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 2 family texts")
