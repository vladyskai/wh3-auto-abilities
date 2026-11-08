# -*- coding: utf-8 -*-
"""Round h91 edit: append the 327 auto-accepted abilities (311 entries / 327
keys) to the LIVE mod and the ANNOTATED reading copy.

Derived programmatically from WH3_ability_tracker.md section 3a (see
h91_derive.py): every row carrying an `approved (auto: <trigger>)` status, the
2026-10-09 standing auto-rules R1-R4 sweep. The three triggers all ride EXISTING
evaluators:

    in-melee self              -> melee_unwavering  (261 entries / 274 keys)
    health<=75 (no melee gate) -> ushoran_health     ( 36 entries /  37 keys)
    charge and in-melee        -> charge_or_melee    ( 14 entries /  16 keys)

Rows sharing an ability name ride ONE entry (base + DLC/summoned twin keys),
the Foe-Seeker convention. This is a BULK DATA APPEND: no new chunk-level
locals (the chunk sits at Lua's 200-local ceiling) and no logic change - the
diff is the table plus its comment header. LF only.
"""
import io, os, hashlib, json

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRIES = json.load(io.open(os.path.join(HERE, "h91_entries.json"), encoding="utf-8"))

DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN = DESK + "/WH3_auto_ability_annotated.lua"

# the last entry currently in the table (round h89), identical in both files -
# the anchor the new entries are inserted after.
ANCHOR = ('\t{ marker = "znarkharjas_ward", name = "Znarkharja\'s Ward", trigger = "melee_unwavering",\n'
          '\t\tbadge = "zz_auto_badge_znarkharjas_ward",\n'
          '\t\tkeys = { "wh3_dlc24_hero_abilities_znarkharjas_ward" },\n'
          '\t\tox = 0, oy = 0 },\n')

TRIG_LABEL = {
    "melee_unwavering": "-- in-melee self (the approved R1/R2 combat-buff + hex batch)",
    "ushoran_health": "-- health<=75, no melee gate (the R1 heal / replenish batch)",
    "charge_or_melee": "-- charge and in-melee (the R1 charge-bonus batch)",
}


def rd(p):
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    assert "\r" not in s, ("CRLF in " + p)
    return s


def esc(s):
    assert '"' not in s and "\\" not in s, ("unquotable name/key: " + s)
    return s


def entry_block(e):
    out = []
    out.append('\t{ marker = "%s", name = "%s", trigger = "%s",' % (e["marker"], esc(e["name"]), e["trigger"]))
    out.append('\t\tbadge = "zz_auto_badge_%s",' % e["marker"])
    ks = e["keys"]
    if len(ks) == 1:
        out.append('\t\tkeys = { "%s" },' % ks[0])
    else:
        out.append('\t\tkeys = { "%s",' % ks[0])
        for k in ks[1:-1]:
            out.append('\t\t\t"%s",' % k)
        out.append('\t\t\t"%s" },' % ks[-1])
    out.append('\t\tox = 0, oy = 0 },')
    return "\n".join(out) + "\n"


def build_block():
    out = []
    out.append("\t-- ============================================================================\n")
    out.append("\t-- THE 327 AUTO-ACCEPTED ABILITIES (this round) - the 2026-10-09 standing\n")
    out.append("\t-- auto-rules R1-R4 sweep (provenance: _classify_wh3.py). 311 entries /\n")
    out.append("\t-- 327 database keys, riding THREE EXISTING evaluators - no new trigger types\n")
    out.append("\t-- this round, so this is a DATA APPEND, not a logic change:\n")
    out.append("\t--   melee_unwavering  261 entries / 274 keys  (in-melee self)\n")
    out.append("\t--   ushoran_health     36 entries /  37 keys  (health <= 75%, no melee gate)\n")
    out.append("\t--   charge_or_melee    14 entries /  16 keys  (charge window OR in melee)\n")
    out.append("\t-- Base + DLC/summoned twin keys ride ONE entry (the Foe-Seeker convention);\n")
    out.append("\t-- every entry self-casts and its ox/oy stay at the top slot (0, 0) for the\n")
    out.append("\t-- wheel-slot fallback. Derived from WH3_ability_tracker.md section 3a.\n")
    out.append("\t-- ============================================================================\n")
    for trig in ("melee_unwavering", "ushoran_health", "charge_or_melee"):
        group = [e for e in ENTRIES if e["trigger"] == trig]
        group.sort(key=lambda e: e["name"].lower())
        out.append("\t%s (%d entries)\n" % (TRIG_LABEL[trig], len(group)))
        for e in group:
            out.append(entry_block(e))
    return "".join(out)


BLOCK = build_block()
assert BLOCK.count("\t{ marker = ") == len(ENTRIES), ("block entry count", BLOCK.count("\t{ marker = "))


def count(s, tok):
    n, at = 0, 1
    while True:
        i = s.find(tok, at)
        if i < 0:
            return n
        n += 1
        at = i + 1


def post(name, s, is_live):
    assert count(s, "\t{ marker = ") == 573, (name, "entries", count(s, "\t{ marker = "))
    assert count(s, 'trigger = "melee_unwavering"') == 216 + 261, (name, "mu", count(s, 'trigger = "melee_unwavering"'))
    assert count(s, 'trigger = "ushoran_health"') == 5 + 36, name
    assert count(s, 'trigger = "charge_or_melee"') == 15 + 14, name
    # every new marker / badge / key present
    for e in ENTRIES:
        assert 'marker = "%s"' % e["marker"] in s, name + " missing marker " + e["marker"]
        assert 'badge = "zz_auto_badge_%s"' % e["marker"] in s, name + " missing badge " + e["marker"]
        for k in e["keys"]:
            assert '"%s"' % k in s, name + " missing key " + k
    if not is_live:
        assert count(s, "log(") == 0, (name, "annotated has log()")
    assert count(s, "string.find(") == 0, name


def apply_to(path, is_live):
    s = rd(path)
    assert s.count(ANCHOR) == 1, (path, "anchor x%d" % s.count(ANCHOR))
    s = s.replace(ANCHOR, ANCHOR + BLOCK, 1)
    post(path, s, is_live)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    assert "\r" not in open(path, "rb").read().decode("utf-8"), "CRLF written"
    return s


live0 = rd(SRC_LIVE)
ann0 = rd(SRC_ANN)
# the pre-edit snapshots for the red control (the CURRENT shipped build)
io.open(os.path.join(HERE, "pre91_live.lua"), "w", encoding="utf-8", newline="\n").write(live0)
io.open(os.path.join(HERE, "pre91_ann.lua"), "w", encoding="utf-8", newline="\n").write(ann0)
print("pre91 snapshots:", len(live0), len(ann0), "bytes")

live = apply_to(SRC_LIVE, True)
ann = apply_to(SRC_ANN, False)
print("LIVE %d -> %d bytes" % (len(live0), len(live)))
print("ANN  %d -> %d bytes" % (len(ann0), len(ann)))
print("sha256 LIVE", hashlib.sha256(live.encode("utf-8")).hexdigest())
print("sha256 ANN ", hashlib.sha256(ann.encode("utf-8")).hexdigest())
print("ALL EDIT POSTCONDITIONS OK")
