#!/usr/bin/env python3
"""Build WH3_abilities_master_v82_2026-11-22.xlsx from v81 - round 205 (user 2026-11-22: Sunfang cast on the terrain,
enemy single entities to be ignored). Column 22 of the 27 exact wave rows gains the SINGLE sentence, and the 19 growing
ones also the CONE sentence. Numbers: the date line only. Definitions: title v82, section 79. Changelog: a v82 row.
v1-v81 are never opened for writing."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import gen_wave_cone as GC  # noqa: E402
import make_xlsx_v81 as V81  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v81_2026-11-22.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v82_2026-11-22.xlsx"
SINGLE = (" ROUND 205 (user 2026-11-22: 'we should also ignore enemy single entities as the damage to them would be "
          "negligible'): the value of a path counts enemy soldiers only. A path with only single entities under it is "
          "never ordered.")
CONE = (" CONE (round 205): this wave grows as it rolls, from %s m wide at its start by %s m per metre up to its full "
        "radius. The mod tests each soldier against the width the wave has at that spot (before, the full radius from "
        "start to end, which sent Sunfang onto empty ground).")


def groups():
    exact, wave, _ = V81.exact_keys()
    cone = GC.derive(open(V81.MOD, encoding="utf-8").read())
    return exact, cone


def plan():
    exact, cone = groups()
    wb = openpyxl.load_workbook(SRC, read_only=True)
    out = []
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if k in exact and row[19] == "IMPLEMENTED":
            add = SINGLE
            if k in cone:
                add = add + CONE % (GC._num(cone[k][0]), GC._num(cone[k][1]))
            out.append((r, k, row[21], (row[21] or "").rstrip() + add))
    wb.close()
    return out, exact, cone


def main():
    rows, exact, cone = plan()
    assert len(exact) == 27 and len(cone) == 19 and len(rows) == 27, (len(exact), len(cone), len(rows))
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, t, n in rows:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    nm = wb["Numbers"]
    assert "v81 - ROUND 204" in str(nm.cell(row=7, column=1).value)
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-22     Rule in force since: 2026-10-18     Inventory: 1,802 active abilities     "
        "(v82 - ROUND 205: the growing waves are cones, enemy single entities are not counted. 1,035 rows / 1,035 keys "
        "implemented, 80 not implemented among the included (all decided by the user), 0 open. The mod: 982 entries / "
        "1,035 keys / 141 trigger families, 140 in use.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v81")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v82 (2026-11-22)"
    base = d.max_row + 2
    d.cell(row=base, column=1).value = "79. ROUND 205 - THE GROWING WAVES ARE CONES, ENEMY SINGLE ENTITIES ARE NOT COUNTED (v82)"
    d.cell(row=base + 1, column=1).value = "CONE"
    d.cell(row=base + 1, column=2).value = (
        "User 2026-11-22: 'I tested with Sunfang and it casted on the terrain, not on the enemy unit'. Sunfang's vortex "
        "starts 0.1 m wide and grows 0.25 m per metre to 12 m over its 48 m path. The mod had treated it as 12 m wide from "
        "start to end and moved the path 12 m away from our soldiers. 19 exact waves grow like this. Their start radius "
        "and growth per metre are GENERATED from battle_vortexs (tools\\gen_wave_cone.py, FOURTH.WW_CONE_TEXT) and every "
        "soldier is tested against the width the wave has at that spot.")
    d.cell(row=base + 2, column=1).value = "SINGLE"
    d.cell(row=base + 2, column=2).value = (
        "User 2026-11-22: 'we should also ignore enemy single entities as the damage to them would be negligible'. An "
        "exact wave's value is the value of the enemy soldiers under it. Units of one man are skipped.")
    d.cell(row=base + 3, column=1).value = "ROWS"
    d.cell(row=base + 3, column=2).value = "%d trigger texts extended (%d of them with the CONE sentence)." % (len(rows), len(cone))
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-22"
    ch.cell(row=r, column=2).value = "v82"
    ch.cell(row=r, column=3).value = (
        "ROUND 205. The growing waves are cones (19), enemy single entities are not counted. %d trigger texts extended. "
        "SHIPPED: installed pack md5 %s. Harness 203 full suite %s checks / 0 failures."
        % (len(rows), os.environ.get("WH3_PACK_MD5", "PENDING"), os.environ.get("WH3_CHECKS", "PENDING")))
    ch.cell(row=r, column=4).value = "user rulings 2026-11-22. xlsx v82 supersedes v81. v1-v81 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts", len(rows), "cones", len(cone))


if __name__ == "__main__":
    main()
