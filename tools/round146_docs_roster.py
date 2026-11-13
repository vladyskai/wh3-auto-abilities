#!/usr/bin/env python3
"""Round 146: the tracker rows (77 on enemy_blob; a note on the 2 excluded snipes) and section 10.27; the database family
text."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_blob_tables as GB  # noqa: E402
import list_blob_candidates as LC  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
EXCLUDED = ("wh3_dlc26_character_abilities_dead_eye", "wh2_dlc13_lord_abilities_kill_shot")
NOTE = (" · **round 146 (2026-11-13):** the blob trigger, user rulings \"A. Density line\", \"10 m\", \"79 open "
        "attacks\".")
XNOTE = (" · **round 146 (2026-11-13):** NOT on the blob trigger: the game lets this shot target single-entity units "
         "only (unit_is_not_single_entity), so an infantry blob can never be its target. Still open.")
PM2 = GB.packed_m2()
# the 77 keys from the mod source (the newest workbook already marks them implemented); range and blast from the game
_src = open(r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua", encoding="utf-8").read()
_keys = GB.keys_in(_src)
_blast = GB.blast_table(_keys)
_sa = {r["key"]: r for r in GB.tsv("unit_spec_abil.tsv")}
rows = [{"key": k, "range": float(_sa[k]["target_intercept_range"]), "blast": _blast[k]} for k in _keys]
ROWS = {}
for r in rows:
    if r["key"] in EXCLUDED:
        continue
    bound = int(math.floor(r["range"] * 0.70 + 1e-9))
    need = max(1, int(math.floor(0.5 * math.pi * r["blast"] ** 2 / PM2 + 0.5)))
    ROWS[r["key"]] = ("implemented (infantry blob: enemy_blob)",
                      "When armed, fires at the densest visible enemy infantry within %d m when its %g m blast would hit "
                      "at least %d soldiers and none of ours are within %g m of the target." % (bound, r["blast"], need,
                                                                                               r["blast"] + 10))
assert len(ROWS) == 77
SECTION = """

### 10.27 Round 146 - the blob trigger (2026-11-13)

**Background:** the round-145 map probe and battle 1 (`docs/WH3_map_probe_battle1.md`) proved that every unit read
answers on both sides, that visibility works, and that the biggest blob was the enemy mobbing one of our own units.

**Rulings (2026-11-13).**

- **Rule: "A. Density line".** Fire at the best SAFE target when the blast around its centre covers at least half of
  what it covers inside a tightly packed infantry block (2.368 m2 per soldier, the game's default infantry spacing):
  17 soldiers for a 5 m blast, 66 for 10 m, 149 for 15 m.
- **Margin: "10 m".** No soldier of ours within the blast radius + 10 m of any part of the target unit.
- **Scope: "79 open attacks".** The open group B attacks whose projectile explodes; all 79 can hurt our units. 77 are
  built: Dead Eye and Focused Shot are excluded, because the game lets them target single-entity units only.

**Arithmetic.**

- **Rows:** implemented 777 + 77 = **854 rows / keys**; not implemented among the included 346 - 77 = **269**
  (27 skipped).
- **The mod:** 722 + 77 = **799 entries / 854 keys**; **74** families.
- **Tests:** harness 145 full suite **6,339 checks / 0 failures**, run twice byte-identical. RED 4/4.
- **Install:** pack md5 `1d2b92d73019956836328a35dd2ade5c`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k in list(ROWS) + list(EXCLUDED):
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if k in ROWS:
                c[1] = "`%s`" % ROWS[k][0]
                c[3] = ROWS[k][1]
                c[4] = c[4] + NOTE
            else:
                c[4] = c[4] + XNOTE
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
assert done == set(ROWS) | set(EXCLUDED), sorted(set(ROWS) | set(EXCLUDED) - done)
s = "\n".join(lines)
assert "### 10.27" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.27" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "self_recharging": '
NEW = ('        "enemy_blob": "The best SAFE visible enemy INFANTRY unit in range (an inf_* class, not in the generated large '
       'set, not flying, at least 10 men): no soldier of ours within the blast radius + 10 m of its estimated rectangle, '
       'and the blast around its centre covers at least half of what it covers inside a packed block. Casts on that '
       'enemy; the map is rebuilt and re-checked before the cast.",\n' + OLD)
assert d.count(OLD) == 1 and '"enemy_blob"' not in d
open(DBB, "w", encoding="utf-8", newline="").write(d.replace(OLD, NEW))
print("database builder: 1 family text")
