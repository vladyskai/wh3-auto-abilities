# -*- coding: utf-8 -*-
"""Derive the blocks 7-9 backlog PROGRAMMATICALLY from WH3_ability_tracker.md.

Reads the section-3a inventory table and selects every row that:
  * carries an `approved (...)` status, OR
  * carries the `redesigned` / `pending review` backlog status,
and whose game key is NOT already in the mod's ABILITIES table (idempotent skip
of everything already shipped - notably the four Enchanted Metallurgy rows).

Groups rows that share a section-2 questionnaire item number into ONE entry
(base + upgraded / twin keys ride one entry, exactly like Deathbringer /
Foe-Seeker / Foe-Seeker-summoned in the shipped table). Writes h90_backlog.json
(row level) and h90_entries.json (entry level, with marker + trigger).

No hand-typed keys: every key comes from the tracker.

NOTE: run BEFORE the tracker statuses are flipped to `implemented (...)` it
yields the 69-entry / 73-key backlog; run AFTER the flip it yields ZERO rows
(the idempotency proof). The pre-flip result is preserved as h90_backlog.json /
h90_entries.json alongside this script.
"""
import io, re, json, os
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DESK = "C:/Users/vlady/Desktop"
TRACKER = DESK + "/WH3_ability_tracker.md"
MOD = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"

lines = io.open(TRACKER, encoding="utf-8").read().split("\n")
i3a = next(i for i, l in enumerate(lines) if l.startswith("### 3a."))
i3b = next(i for i, l in enumerate(lines) if l.startswith("### 3b."))

rows = []
for i in range(i3a, i3b):
    l = lines[i]
    if not l.startswith("|"):
        continue
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells) < 2:
        continue
    m = re.search(r"`([^`]+)`", cells[0])
    if not m:
        continue
    q = re.search(r"§2\s*#(\d+)", cells[4] if len(cells) > 4 else "")
    rows.append({"line": i + 1, "name": cells[0].split("`")[0].strip(),
                 "key": m.group(1), "status": cells[1].strip("`").strip(),
                 "q": q.group(1) if q else None})

modkeys = set(re.findall(r'"((?:wh|wh2|wh3)[a-z0-9_]+)"', io.open(MOD, encoding="utf-8").read()))

backlog = [r for r in rows
           if (r["status"].startswith("approved") or r["status"] in ("redesigned", "pending review"))
           and r["key"] not in modkeys]
skipped = [r for r in rows if r["status"].startswith("approved") and r["key"] in modkeys]

GAME = re.compile(r"^wh[0-9]*(?:_(?:main|dlc[0-9]+|cp[0-9]+|twa[0-9]+|pro[0-9]+))?_")
CATS = ["character_abilities_", "unit_abilities_", "lord_abilities_", "hero_abilities_",
        "weapon_abilities_", "item_abilities_", "armour_abilities_", "rune_abilities_",
        "quest_abilities_", "daemon_arms_abilities_", "daemon_head_abilities_",
        "spell_bound_prayer_", "spell_bound_", "ability_bound_prayer_", "bound_abilities_",
        "lord_active_", "hero_active_", "prisoners_"]

def marker_of(key):
    k = GAME.sub("", key)
    for c in sorted(CATS, key=len, reverse=True):
        if k.startswith(c):
            return k[len(c):]
    return k

def trigger_of(status, q):
    d = {"approved (in-melee self)": "melee_unwavering",
         "approved (in-melee self - auto, trivial)": "melee_unwavering",
         "approved (charge and in-melee)": "charge_or_melee",
         "approved (charge only)": "charge_only",
         "approved (wavering self)": "wavering_self",
         "approved (wavering self-or-ally in range)": "wavering_self_or_ally",
         "approved (charge or wavering)": "charge_or_wavering",
         "approved (health<=75, no melee gate)": "ushoran_health",
         "approved (in melee and health<=75)": "melee_health75",
         "approved (wavering ally in range)": "wavering_ally_range",
         "approved (melee self-or-ally / shooting ally in range)": "metallurgy_melee",
         "pending review": "melee_unwavering"}
    if status in d:
        return d[status]
    if status == "redesigned":
        return {"36": "wavering_self_or_ally", "46": "tired"}[q]
    raise SystemExit("unmapped status: " + status)

grp = OrderedDict()
for b in backlog:
    grp.setdefault(b["q"], []).append(b)

entries = []
for q, rs in grp.items():
    rs = sorted(rs, key=lambda r: r["key"])
    entries.append({"q": q, "marker": marker_of(rs[0]["key"]), "name": rs[0]["name"],
                    "trigger": trigger_of(rs[0]["status"], q),
                    "keys": [r["key"] for r in rs], "status": rs[0]["status"]})

print("3a approved rows already shipped (SKIP):", len(skipped))
for r in skipped:
    print("   SKIP", r["key"])
print("backlog rows/keys:", len(backlog), "entry-groups:", len(entries),
      "keys:", sum(len(e["keys"]) for e in entries))
print("triggers:", dict(Counter(e["trigger"] for e in entries)))

json.dump(backlog, io.open(os.path.join(HERE, "h90_backlog.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(entries, io.open(os.path.join(HERE, "h90_entries.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("written h90_backlog.json / h90_entries.json")
