"""Re-open the master workbook and assert its structure. Read-only.

Run: python tools/verify_abilities_master.py [path]
"""
import os
import sys
import collections

from openpyxl import load_workbook

DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "WH3_abilities_master_v1_2026-10-17.xlsx")

path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
wb = load_workbook(path, read_only=True, data_only=True)
print("file:", path)
print("bytes:", os.path.getsize(path))
print("sheets:", wb.sheetnames)

ws = wb["Abilities"]
rows = list(ws.iter_rows(values_only=True))
header = rows[0]
data = rows[1:]
print("header columns:", len(header))
print("data rows:", len(data))

col = {name: i for i, name in enumerate(header)}
fail = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (("  " + detail) if detail else ""))
    if not ok:
        fail.append(name)


check("1,797 data rows", len(data) == 1797, "got %d" % len(data))
nums = [r[col["Item #"]] for r in data]
check("no duplicate item numbers", len(set(nums)) == len(nums), "distinct %d" % len(set(nums)))
check("item numbers 1..1797", sorted(nums) == list(range(1, 1798)))

names = [r[col["Ability name"]] for r in data]
keys = [r[col["Ability key(s)"]] for r in data]
check("every row has a name", all(isinstance(n, str) and n.strip() for n in names))
check("every row has at least one key", all(isinstance(k, str) and k.strip() for k in keys))
check("every row has IN-WHEEL/EXCLUDED", all(r[col["Status"]] in ("IN-WHEEL", "EXCLUDED") for r in data))

impl = [r for r in data if r[col["Implementation"]] == "IMPLEMENTED"]
outside = [r for r in data if r[col["Implementation"]] == "OUTSIDE-RULE-IMPLEMENTED"]
notimpl = [r for r in data if r[col["Implementation"]] == "NOT IMPLEMENTED"]
check("603 IMPLEMENTED", len(impl) == 603, "got %d" % len(impl))
check("2 OUTSIDE-RULE-IMPLEMENTED", len(outside) == 2, "got %d" % len(outside))
check("1,192 NOT IMPLEMENTED", len(notimpl) == 1192, "got %d" % len(notimpl))
check("every implemented row has a non-empty Trigger",
      all(isinstance(r[col["Trigger (as implemented)"]], str)
          and len(r[col["Trigger (as implemented)"]].strip()) > 40 for r in impl + outside))
check("non-implemented rows carry '-' as Trigger",
      all((r[col["Trigger (as implemented)"]] or "").strip() == "-" for r in notimpl))
check("every implemented row names its trigger family",
      all(isinstance(r[col["Trigger family"]], str) and r[col["Trigger family"]] != "-" for r in impl + outside))
check("in-wheel count 1,158", sum(1 for r in data if r[col["Status"]] == "IN-WHEEL") == 1158)
check("excluded count 639", sum(1 for r in data if r[col["Status"]] == "EXCLUDED") == 639)
check("implemented rows are all in-wheel except the 2 outside",
      sum(1 for r in impl if r[col["Status"]] != "IN-WHEEL") == 0)
check("outside-rule rows are all excluded",
      all(r[col["Status"]] == "EXCLUDED" for r in outside))

# tooltip fields never empty
tip_cols = ["Category / Targeting Type", "Uses", "Damage Per Second", "Stat Modifiers", "Duration",
            "Radius / Effect Area", "Movement Speed", "Range", "Phase Durations", "Cooldown",
            "Affects units if", "Can use if", "Tactical Overview", "Tooltip (full)",
            "Restrictions"]
empty = collections.Counter()
for r in data:
    for c in tip_cols:
        v = r[col[c]]
        if v is None or (isinstance(v, str) and not v.strip()):
            empty[c] += 1
check("no empty tooltip field cells", not empty, str(dict(empty)))

# Numbers sheet reconciliation
ns = wb["Numbers"]
nrows = list(ns.iter_rows(values_only=True))
flat = {str(r[1]).strip(): r for r in nrows if r[1]}
want = {
    "Total active abilities (the inventory)": 1797,
    "Excluded - not in the ability wheel": 639,
    "Included - in the ability wheel": 1158,
    "Implemented among the included": 603,
    "Not implemented among the included": 555,
    "Implemented but OUTSIDE the rule (reported separately)": 2,
    "All implemented in the mod (4 + 6)": 605,
}
ok = True
for label, n in want.items():
    got = flat.get(label, [None, None, None])[2]
    if got != n:
        ok = False
        print("   Numbers mismatch:", label, "expected", n, "got", got)
check("Numbers sheet reconciles with the recount (1797/639/1158/603/555/2)", ok)
check("Numbers sheet states the date", any("2026-10-17" in str(c) for row in nrows for c in row if c))
check("Numbers sheet carries the in-wheel definition",
      any(isinstance(c, str) and "IN THE ABILITY WHEEL" in c for row in nrows for c in row))

check("Changelog sheet present", "Changelog" in wb.sheetnames)
check("Definitions sheet present", "Definitions" in wb.sheetnames)
if "Changelog" in wb.sheetnames:
    ch = list(wb["Changelog"].iter_rows(values_only=True))
    check("Changelog first row is v1 2026-10-17",
          len(ch) > 1 and ch[1][0] == "2026-10-17" and ch[1][1] == "v1")
if "Definitions" in wb.sheetnames:
    df = list(wb["Definitions"].iter_rows(values_only=True))
    fams = [r[0] for r in df if r[0] and r[0] in (
        "melee_unwavering", "charge", "ally_heal", "enemy_engaged_or_shot", "eat_da_runts")]
    check("Definitions glossary lists evaluator families", len(fams) >= 5, str(fams[:6]))
    check("Definitions records the four absences",
          sum(1 for r in df if r[0] in ("No firing read", "No cooldown read",
                                        "No area-contents read", "No enemy-spell-cast event")) == 4)

# coverage table
cov = {}
for c in tip_cols[:-1]:
    n = 0
    for r in data:
        v = r[col[c]]
        if not isinstance(v, str):
            continue
        s = v.strip()
        if s in ("-", "", "unknown"):
            continue
        if c == "Range" and s.startswith("no range column"):
            continue
        n += 1
    cov[c] = n

print("\nCOVERAGE (populated rows of 1,797):")
for c in tip_cols[:-1]:
    print("  %-28s %5d" % (c, cov[c]))
print("  %-28s %5d" % ("Restrictions (flags found)", sum(1 for r in data if r[col["Restrictions"]] != "none found")))
unk = sum(1 for r in data for c in tip_cols if isinstance(r[col[c]], str) and r[col[c]].strip() == "unknown")
print("\ncells reading 'unknown':", unk)
print("trigger text length min/median/max:",
      min(len(r[col["Trigger (as implemented)"]]) for r in impl + outside),
      sorted(len(r[col["Trigger (as implemented)"]]) for r in impl + outside)[len(impl + outside) // 2],
      max(len(r[col["Trigger (as implemented)"]]) for r in impl + outside))
print("\nRESULT:", "ALL CHECKS PASSED" if not fail else ("FAILED: " + ", ".join(fail)))
sys.exit(0 if not fail else 1)
