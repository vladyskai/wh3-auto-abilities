#!/usr/bin/env python3
"""Round 136: the tracker rows and section 10.17 (no new family; the database builder is unchanged)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ability_database as bd  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
NOTE = " · **round 136 (2026-11-09):** audit batch 5: %s"
EM = ("implemented (enemy-targeted: in-melee only: enemy_melee)",
      "When armed, fires at the closest enemy in range that is fighting in melee (an enemy only being shot does not count).",
      "user ruling \"Enemy in melee\".")
FA = ("implemented (enemy-targeted: fast enemy near our units: enemy_fast_near_ally)",
      "When armed, fires at an enemy in range that is moving with a run speed of 5 m/s or more within 40 m of one of your units.",
      "user ruling \"Fast enemy near us\" (cannot move roots the threat before contact).")
TO_MELEE = ["assassins_trophy", "lord_of_dragons", "beguile", "oath_of_vengeance", "ottos_scythe",
            "averland_runefang", "the_dark_master", "enfeebling_foe", "the_hammer_of_karak_drazh", "torment_blade",
            "trophy_heads", "willing_prey", "whip_of_agony", "fermented_fungi",
            "blight_swarm", "virulent_contagion", "virulent_contagion_upgraded", "dispatch_the_swarm_attack",
            "dispatch_the_swarm_attack_upgraded", "pestilent_potions"]
TO_FAST = ["gaze_of_fate", "sadistic_snare", "spearfishers_net"]

entries, _, _ = bd.mod_entries()
by_marker = {e["marker"]: e for e in entries}
ROWS = {}
for m in TO_MELEE:
    for k in by_marker[m]["keys"]:
        ROWS[k] = EM
for m in TO_FAST:
    for k in by_marker[m]["keys"]:
        ROWS[k] = FA
NET = "wh2_dlc11_lord_abilities_spearfishers_net"

SECTION = """

### 10.17 Round 136 - audit batch 5: the melee hexes (2026-11-09)

**Rulings (2026-11-09), all as recommended.**

- **"Enemy in melee" (20):** the pure melee hexes (Assassin's Trophy, Lord of Dragons, Master of Beguilement, Oath of
  Vengeance, Otto's Scythe, The Averland Runefang, The Dark Master, The Enfeebling Foe, The Hammer of Karak Drazh,
  Torment Blade, Trophy Heads, Willing Prey, Whip of Agony, Fermented Fungi) and the spreading melee-defence hexes
  (Blight Swarm, Virulent Contagion and Upgraded, Ravaging Swarm and Upgraded, Pestilent Potions).
- **"Fast enemy near us" (3):** Gaze of Fate, Sadistic Snare, Spearfisher's Net.
- **Spearfisher's Net's not-flying filter:** "Yes, add it now" (`target_class = "not_flying"`, is_currently_flying()
  read live, only an exact false passes).
- **Earlier decisions:** questionnaire approvals only.

**Arithmetic.**

- **Rows:** implemented 750 rows / keys and 373 not implemented, unchanged.
- **The mod:** 698 entries / 750 keys / 57 families; enemy_engaged_or_shot 70 -> 47, enemy_melee 14 -> 34,
  enemy_fast_near_ally 4 -> 7.
- **Tests:** harness 135 full suite **5,901 checks / 0 failures**, run twice byte-identical. RED on the
  round-135 build: 10/10.
- **Install:** pack md5 `104c049b22f675b1487f425eeb7fdb2e`.
"""

s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, (st, pr, note) in ROWS.items():
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            c[1] = "`%s`" % st
            c[2] = "enemy unit"
            c[3] = pr
            extra = " The target must be on the ground (the game's own rule)." if k == NET else ""
            c[4] = c[4] + NOTE % (note + extra)
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.17" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.17" % len(done))
