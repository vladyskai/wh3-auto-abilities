# -*- coding: utf-8 -*-
"""Derive the 327 auto-accepted abilities PROGRAMMATICALLY from WH3_ability_tracker.md.

Selects every section-3a inventory row whose status cell reads
`approved (auto: <trigger>)` (the standing auto-rules R1-R4 sweep of 2026-10-09,
provenance `_classify_wh3.py`). The trigger -> evaluator map:

    approved (auto: in-melee self)              -> melee_unwavering
    approved (auto: health<=75 (no melee gate)) -> ushoran_health
    approved (auto: charge and in-melee)        -> charge_or_melee

Rows sharing an ability NAME are grouped into ONE entry (base + DLC/summoned
twin keys ride one entry - the Foe-Seeker / Deathbringer convention already in
the file). The marker is derived from the (alphabetically first) key by the
same prefix/category strip the h90 round used; on a collision with an existing
mod marker (or an earlier new marker) the display NAME supplies the marker.

No hand-typed keys: every key comes from the tracker. Writes h91_entries.json.
"""
import io, re, json, os
from collections import OrderedDict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DESK = "C:/Users/vlady/Desktop"
TRACKER = DESK + "/WH3_ability_tracker.md"
MOD = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"

TRIG = {
    "approved (auto: in-melee self)": "melee_unwavering",
    "approved (auto: health<=75 (no melee gate))": "ushoran_health",
    "approved (auto: charge and in-melee)": "charge_or_melee",
}

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
    rows.append(dict(line=i + 1, name=cells[0].split("`")[0].strip(),
                     key=m.group(1), status=cells[1].strip("`").strip()))

auto = [r for r in rows if r["status"].startswith("approved (auto:")]
unknown = [r for r in auto if r["status"] not in TRIG]
if unknown:
    for r in unknown:
        print("UNKNOWN TRIGGER CODE:", r["line"], repr(r["status"]), r["key"])
    raise SystemExit("unknown trigger code(s) - stopping rather than inventing a mapping")

GAME = re.compile(r"^wh[0-9]*(?:_(?:main|dlc[0-9]+|cp[0-9]+|twa[0-9]+|pro[0-9]+))?_")
CATS = ["character_abilities_", "unit_abilities_", "lord_abilities_", "hero_abilities_",
        "weapon_abilities_", "item_abilities_", "armour_abilities_", "rune_abilities_",
        "quest_abilities_", "daemon_arms_abilities_", "daemon_head_abilities_",
        "spell_bound_prayer_", "spell_bound_", "ability_bound_prayer_", "bound_abilities_",
        "lord_active_", "hero_active_", "prisoners_",
        "daemon_legs_abilities_", "daemon_wings_abilities_", "daemon_body_abilities_",
        "qb_unit_abilities_", "character_active_", "item_active_", "mount_abilities_",
        "cataclysm_bound_", "pro_character_abilities_"]


def clean(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def key_marker(key):
    k = GAME.sub("", key)
    kl = k.lower()
    for c in sorted(CATS, key=len, reverse=True):
        if kl.startswith(c):
            return clean(k[len(c):])
    return clean(k)


grp = OrderedDict()
for r in auto:
    grp.setdefault(r["name"], []).append(r)

modsrc = io.open(MOD, encoding="utf-8").read()
used = set(re.findall(r'marker\s*=\s*"([^"]+)"', modsrc))

entries = []
fallback = []
unmappable = []
for name in sorted(grp.keys()):
    rs = sorted(grp[name], key=lambda r: r["key"])
    trigs = set(TRIG[r["status"]] for r in rs)
    if len(trigs) != 1:
        unmappable.append((name, sorted(trigs)))
        continue
    pref = key_marker(rs[0]["key"])
    mk = pref
    if mk in used:                      # collision with an existing / earlier marker
        mk = clean(name)
        fallback.append((name, pref, mk))
    if mk in used or mk == "" or not re.fullmatch(r"[a-z0-9_]+", mk):
        unmappable.append((name, "marker", pref, mk))
        continue
    used.add(mk)
    entries.append(dict(name=name, marker=mk, trigger=trigs.pop(),
                        keys=[r["key"] for r in rs], rows=[r["line"] for r in rs]))

print("auto rows (abilities):", len(auto))
print("entries:", len(entries), " keys:", sum(len(e["keys"]) for e in entries))
print("by trigger (rows):", dict(Counter(TRIG[r["status"]] for r in auto)))
print("by trigger (entries):", dict(Counter(e["trigger"] for e in entries)))
print("name-collision fallback markers:", fallback)
print("unmappable rows:", unmappable)
assert len(set(e["marker"] for e in entries)) == len(entries), "duplicate marker"

json.dump(entries, io.open(os.path.join(HERE, "h91_entries.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("written h91_entries.json")
