#!/usr/bin/env python3
"""Verify docs/WH3_ability_database_master.md against the tracker and the mod.

AIR-DROP ASSERTION (the user's requirement): the database's air-drop lines must
agree with the tracker and the mod, line for line. Concretely, for the family
`air_drop_on_infantry` this script FAILS if

  A1. the key set in the mod, in the tracker and in the database's §2 section
      is not the SAME 19 keys;
  A2. the database's §1.3 plain-English sentence is not the mod's own
      `FOURTH.TRIGGER_TIP.air_drop_on_infantry` string, verbatim;
  A3. the database's §2 "Plain English" sentence differs from that same string;
  A4. any of the 19 per-key lines does not carry that sentence in its
      "Fires: ..." clause;
  A5. any air-drop line still carries RETIRED machinery (the edge gap, the
      dwell, the measured delay, the velocity rebuild, the lead dials, the
      derived frontage) or lacks the 6 m centre rule;
  A6. any of the 19 tracker rows is not `implemented (...)`, is not filed under
      `air_drop_on_infantry`, or does not carry the in-force
      `AIR_DROP_CENTER_M = 6.0` statement in its status text;
  A7. the family's entry/key counts in §1.3 differ from the mod's own parse.

Plus the general gate the same round needs: EVERY key in the mod's ABILITIES
table has a §2 line in the database whose status reads `implemented`, and the
inventory/status reconciliation in §1.6 reports no disagreement with the mod.

Exit 0 = all assertions hold; exit 1 = at least one failed (printed).
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import collections
import re
import sys

sys.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import build_ability_database as bd

DB = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_database_master.md"
FAMILY = "air_drop_on_infantry"

RETIRED = ["0.10 m", "0.1 m", "AIR_DROP_EDGE_M", "AIR_DROP_DWELL", "AIR_DROP_DELAY",
           "AIR_DROP_ENEMY_LEAD", "AIR_DROP_CASTER_LEAD", "AIR_DROP_INHERIT",
           "AIR_DROP_MODEL_RADIUS", "AIR_DROP_FRONTAGE", "edge-to-edge", "ad_pair",
           "frontage", "dwell", "velocity", "cosine", "lead="]
LIVE = ["6 m", "centre"]          # the mod's own tooltip wording; the 6.0 m constant is
                                     # asserted separately against the family DESCRIPTION (A8)

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


src = open(DB, encoding="utf-8").read()
lines = src.split("\n")

# ------------------------------------------------------------------ parse the database
sec = {}
cur = None
hdr_re = re.compile(r"^### `([a-z0-9_]+)` — (\d+) entries / (\d+) keys")
row_re = re.compile(r"^\| (.*?) \| `([^`]+)` \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$")
plain_re = re.compile(r"^\*\*Plain English \(the sentence the mod ships in that ability's tooltip\):\*\* \*(.*?)\*\.?$")
for ln in lines:
    m = hdr_re.match(ln)
    if m:
        cur = m.group(1)
        sec[cur] = {"entries": int(m.group(2)), "keys": int(m.group(3)),
                    "plain": None, "desc": None, "rows": []}
        continue
    if cur:
        if (sec[cur]["desc"] is None and ln.strip() and not ln.startswith("|")
                and not ln.startswith("**Plain English") and not ln.startswith("**Cast target")):
            sec[cur]["desc"] = ln.strip()
            continue
        m = plain_re.match(ln)
        if m:
            sec[cur]["plain"] = m.group(1).rstrip(".")
            continue
        m = row_re.match(ln)
        if m:
            sec[cur]["rows"].append({"name": m.group(1), "key": m.group(2),
                                     "status": m.group(6), "trigger": m.group(7)})
        elif ln.startswith("## "):
            cur = None

tbl13 = {}
for ln in lines:
    m = re.match(r"^\| `([a-z0-9_]+)` \| (.*) \| (\d+) \| (\d+) \|$", ln)
    if m:
        tbl13[m.group(1)] = {"tip": m.group(2), "entries": int(m.group(3)), "keys": int(m.group(4))}

# ------------------------------------------------------------------ the sources
entries, consts, tips = bd.mod_entries()
by_fam = collections.defaultdict(list)
for e in entries:
    by_fam[e["trigger"]].append(e)
mod_ad_keys = [k for e in by_fam[FAMILY] for k in e["keys"]]
mod_ad_entries = len(by_fam[FAMILY])

tracker = bd.tracker_rows()
tr_ad = [r for r in tracker if r["group"] == FAMILY]
tr_ad_keys = [r["key"] for r in tr_ad]

# ------------------------------------------------------------------ A0 the army-bar gate
# The user's ruling (round 121, verbatim): "The triggers will not work if the
# ability is not in the ability wheel on the lower left corner of the battle
# screen ... Therefore, ALL ARMY ABILITIES PLEASE EXCLUDE." An army-bar ability
# (a key in the army_spec junction) has no wheel button, so
# perform_special_ability can never be called for it: it can never fire, and it
# has no business in the mod's ABILITIES table. No exceptions list.
ARMY_SPEC = GP.ARMY_SPEC
army = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            army.add(c[0].strip())
table_keys = set(k for e in entries for k in e["keys"])
army_hits = sorted(k for k in table_keys if k in army)
check(not army_hits,
      "A0: %d army-bar (army_spec junction) key(s) are in the mod's ABILITIES table - they have no "
      "battle-wheel button, so perform_special_ability can never be called for them: %s"
      % (len(army_hits), army_hits))

# ------------------------------------------------------------------ A1 key sets
db_ad = sec.get(FAMILY)
check(db_ad is not None, "A1: the database has no §2 section for `%s`" % FAMILY)
if db_ad:
    db_ad_keys = [r["key"] for r in db_ad["rows"]]
    check(sorted(db_ad_keys) == sorted(mod_ad_keys),
          "A1: §2 air-drop keys != the mod's keys\n    db-only: %s\n    mod-only: %s"
          % (sorted(set(db_ad_keys) - set(mod_ad_keys)), sorted(set(mod_ad_keys) - set(db_ad_keys))))
    check(sorted(tr_ad_keys) == sorted(mod_ad_keys),
          "A1: tracker air-drop keys != the mod's keys\n    tracker-only: %s\n    mod-only: %s"
          % (sorted(set(tr_ad_keys) - set(mod_ad_keys)), sorted(set(mod_ad_keys) - set(tr_ad_keys))))
    check(len(mod_ad_keys) == 19, "A1: the mod carries %d air-drop keys, expected 19" % len(mod_ad_keys))

# ------------------------------------------------------------------ A2/A3 the sentence
tip = tips.get(FAMILY)
check(bool(tip), "A2: the mod has no FOURTH.TRIGGER_TIP['%s']" % FAMILY)
if tip and FAMILY in tbl13:
    check(tbl13[FAMILY]["tip"] == tip.rstrip("."),
          "A2: §1.3 air-drop sentence != the mod's TRIGGER_TIP\n    db : %s\n    mod: %s"
          % (tbl13[FAMILY]["tip"], tip.rstrip(".")))
if tip and db_ad and db_ad["plain"]:
    check(db_ad["plain"] == tip.rstrip("."),
          "A3: §2 'Plain English' != the mod's TRIGGER_TIP\n    db : %s\n    mod: %s"
          % (db_ad["plain"], tip.rstrip(".")))

# ------------------------------------------------------------------ A4/A5 per-key lines
if db_ad and tip:
    for r in db_ad["rows"]:
        check(r["trigger"].startswith("Fires: " + tip.rstrip(".")),
              "A4: the line for `%s` does not carry the current air-drop sentence: %s"
              % (r["key"], r["trigger"][:160]))
if db_ad:
    ad_lines = [tbl13.get(FAMILY, {}).get("tip", "")] + ([db_ad["plain"]] if db_ad["plain"] else []) + \
               [r["trigger"] for r in db_ad["rows"]]
    for ln in ad_lines:
        low = ln.lower()
        for tok in RETIRED:
            check(tok.lower() not in low,
                  "A5: an air-drop line still carries retired machinery '%s': %s" % (tok, ln[:160]))
        for tok in LIVE:
            check(tok in low, "A5: an air-drop line lacks the live rule token '%s': %s"
                  % (tok, ln[:160]))

# ------------------------------------------------------------------ A6 the tracker rows
RULE_IN_FORCE_END = "THE TEXT THAT FOLLOWS IS HISTORY"
for r in tr_ad:
    check(r["status"].lower().startswith("implemented"),
          "A6: tracker row `%s` reads `%s`" % (r["key"], r["status"]))
    proposal = r["proposal"]
    head = proposal.split(RULE_IN_FORCE_END)[0]
    check(RULE_IN_FORCE_END in proposal,
          "A6: tracker row `%s` does not separate the rule in force from the history" % r["key"])
    check("AIR_DROP_CENTER_M = 6.0" in head,
          "A6: tracker row `%s` RULE-IN-FORCE prefix does not carry AIR_DROP_CENTER_M = 6.0" % r["key"])
    for tok in RETIRED:
        check(tok.lower() not in head.lower(),
              "A6: tracker row `%s` RULE-IN-FORCE prefix still carries '%s'" % (r["key"], tok))
check(len(tr_ad) == 19, "A6: the tracker carries %d air-drop rows, expected 19" % len(tr_ad))

# ------------------------------------------------------------------ A8 the constant
if db_ad:
    check(bool(db_ad["desc"]) and "AIR_DROP_CENTER_M = 6.0" in db_ad["desc"],
          "A8: the §2 air-drop family description does not state the live constant "
          "AIR_DROP_CENTER_M = 6.0: %s" % (str(db_ad["desc"])[:200]))

# ------------------------------------------------------------------ A7 the counts
if FAMILY in tbl13:
    check(tbl13[FAMILY]["entries"] == mod_ad_entries and tbl13[FAMILY]["keys"] == len(mod_ad_keys),
          "A7: §1.3 counts %d entries / %d keys; the mod parses %d / %d"
          % (tbl13[FAMILY]["entries"], tbl13[FAMILY]["keys"], mod_ad_entries, len(mod_ad_keys)))
if db_ad:
    check(db_ad["entries"] == mod_ad_entries and db_ad["keys"] == len(mod_ad_keys),
          "A7: §2 heading says %d entries / %d keys; the mod parses %d / %d"
          % (db_ad["entries"], db_ad["keys"], mod_ad_entries, len(mod_ad_keys)))

# ------------------------------------------------------------------ the general gate
mod_keys = set(k for e in entries for k in e["keys"])
db_rows = {}
for f, s in sec.items():
    for r in s["rows"]:
        db_rows.setdefault(r["key"], []).append((f, r))
missing = sorted(k for k in mod_keys if k not in db_rows)
check(not missing, "G1: mod keys with NO §2 line in the database: %s" % missing)
bad_status = sorted((k, db_rows[k][0][1]["status"]) for k in mod_keys
                    if k in db_rows and not db_rows[k][0][1]["status"].lower().startswith("implemented"))
check(not bad_status, "G1: mod keys whose §2 status is not `implemented`: %s" % bad_status)

check("Tracker status and the mod's table agree exactly." in src,
      "G2: §1.6 does not report exact agreement between the tracker and the mod "
      "(it still lists a disagreement)")
n_inv = re.search(r"\| Tracker inventory rows \(all three tables\) \| \*\*(\d+)\*\* \|", src)
n_keys = re.search(r"\| distinct ability keys in those rows \| (\d+) \|", src)
check(n_inv and int(n_inv.group(1)) >= 1801, "G2: the inventory row count is stale: %s"
      % (n_inv.group(1) if n_inv else "no line"))
check(n_keys and int(n_keys.group(1)) == 1800, "G2: distinct keys = %s, expected 1,800"
      % (n_keys.group(1) if n_keys else "no line"))

# ------------------------------------------------------------------ report
if fails:
    print("DATABASE VERIFY: %d FAILURE(S)" % len(fails))
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("DATABASE VERIFY OK")
print("  army-bar gate: 0 of %d mod keys are in the %d-key army_spec junction (they can never be cast)"
      % (len(table_keys), len(army)))
print("  air-drop: %d entries / %d keys in the mod, the tracker and the database - same key set"
      % (mod_ad_entries, len(mod_ad_keys)))
print("  sentence: %d chars, identical in the mod's TRIGGER_TIP, §1.3 and §2 (+ 19 per-key lines)"
      % len(tip))
print("  retired machinery: none in any air-drop line")
print("  every mod key (%d) has a §2 line whose status reads implemented" % len(mod_keys))
print("  inventory: %s rows / %s distinct keys" % (n_inv.group(1), n_keys.group(1)))
