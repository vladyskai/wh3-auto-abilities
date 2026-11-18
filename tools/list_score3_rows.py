#!/usr/bin/env python3
"""List every score-3 row of the night review files (docs\\audit_night\\review_*.md) with the entry's CURRENT trigger,
keys and fields read from the mod source, and whether the entry still exists. Read-only.

  uv run python tools/list_score3_rows.py > <out.tsv>
"""
import glob
import os
import re

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
SRC = os.path.join(ROOT, r"mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
src = open(SRC, encoding="utf-8").read()
ENTRY = re.compile(r'\t\{ marker = "([^"]+)", name = "([^"]+)", trigger = "([^"]+)",\n(.*?)\t\tox = 0, oy = 0 \},', re.S)
by_marker = {}
for m in ENTRY.finditer(src):
    keys = re.findall(r'"([^"]+)"', m.group(4).split("keys = {", 1)[1].split("}", 1)[0])
    extra = ";".join(l.strip().rstrip(",") for l in m.group(4).split("\n") if "=" in l and "badge" not in l
                     and "keys" not in l and not l.strip().startswith('"'))
    by_marker[m.group(1)] = (m.group(2), m.group(3), keys, extra)

print("file\tmarker\tability\tnow_trigger\tkeys\tfields\teffect\twhy\tbetter")
for f in sorted(glob.glob(os.path.join(ROOT, r"docs\audit_night\review_*.md"))):
    for line in open(f, encoding="utf-8"):
        if not line.startswith("| ") or "| 3 |" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0].isdigit():   # g1b has a leading row number
            cells = cells[1:]
        marker, ability, effect, score, why, better = cells[0], cells[1], cells[2], cells[3], cells[4], cells[5]
        if score != "3":
            continue
        e = by_marker.get(marker.strip("`"))
        now = e[1] if e else "GONE"
        keys = ",".join(e[2]) if e else "-"
        fields = e[3] if e else "-"
        print("\t".join([os.path.basename(f)[7:-3], marker.strip("`"), ability, now, keys, fields, effect, why, better]))
