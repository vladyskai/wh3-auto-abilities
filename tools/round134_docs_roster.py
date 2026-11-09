#!/usr/bin/env python3
"""Round 134: the tracker rows and section 10.15 (no new family, so the database builder is unchanged)."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"

NOTE = " · **round 134 (2026-11-09):** audit batch 3, user ruling: \"%s\"."
CO = ("implemented (charge only: charge_only)",
      "When armed, fires in the charge window (running at an attack target 12 to 60 m away, impact within 4 s): cast on self. Not in melee.",
      "Charge only")
CM = ("implemented (charge, else in melee: charge_or_melee)",
      "When armed, fires in the charge window, else in melee: cast on self.",
      "Charge, else in melee")
SK = ("skipped (user decision 2026-11-09: a movement mode with no end time; when to use it is the player's choice)",
      "Not automated: removed from the mod.", "Stop automating")
ROWS = {k: CO for k in ("wh_pro04_unit_abilities_apocalyptic_charge", "wh2_dlc16_item_abilities_twilight_horn_i",
                        "wh_main_item_abilities_potion_of_speed", "wh_main_unit_abilities_blooood")}
ROWS.update({k: CM for k in ("wh_main_spell_bound_book_of_arkhan", "wh2_dlc17_rune_abilities_rune_of_speed",
                             "wh2_dlc17_rune_abilities_master_rune_of_speed", "wh2_dlc11_lord_abilities_lightning_reflexes",
                             "wh2_dlc12_lord_abilities_master_of_the_skies", "wh_main_item_abilities_pendant_of_slaanesh",
                             "wh_main_hero_abilities_slippery", "wh2_dlc11_lord_abilities_transfix")})
ROWS.update({k: SK for k in ("wh3_dlc25_unit_abilities_thunderburner", "wh3_dlc25_unit_abilities_thunderburner_upgraded")})

SECTION = """

### 10.15 Round 134 - audit batch 3: the speed buffs (2026-11-09)

**Rulings (2026-11-09), all three as recommended.**

- **Speed and charge buffs with no melee stat, "Charge only":** Apocalyptic Charge, Twilight Horn I, Potion of
  Speed, Blooood!
- **Speed plus a melee stat, "Charge, else in melee":** Book of Arkhan, Rune of Speed, Master Rune of Speed,
  Lightning Reflexes, Master of the Skies, Pendant of Slaanesh, Slippery, Transfix.
- **Thunderburner and Thunderburner Upgraded, "Stop automating":** a movement mode with no end time; removed.
- **Earlier decisions:** the 2026-10 questionnaire put each on "in melee"; no later ruling.

**Families (both existing).** `charge_only` 1 -> 5; `charge_or_melee` 28 -> 36. The charge window is the
existing detector: running, an attack target 12 to 60 m away, impact within 4 s.

**Arithmetic.**

- **Rows:** implemented 752 - 2 = **750 rows / 750 keys**; not implemented among the included 371 + 2 = **373**
  (24 skipped by user decision).
- **The mod:** **698 entries / 750 keys**; 56 families; melee_unwavering 342 -> 328.
- **Tests:** harness 133 full suite **5,785 checks / 0 failures**, run twice byte-identical. RED on the
  round-133 build: 10/10.
- **Install:** pack md5 `ecc56210716b57f8d5ab53dc442c263c`.
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
            c[2] = "skipped" if st.startswith("skipped") else "self"
            c[3] = pr
            c[4] = c[4] + NOTE % rule
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.15" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.15" % len(done))
