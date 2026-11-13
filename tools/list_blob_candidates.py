#!/usr/bin/env python3
"""Round 146: the open group B attacks that EXPLODE (the user's blob-trigger scope, 2026-11-13), from the game data:
key, name, real range, blast radius (projectiles_explosions.detonation_radius via the ability's activated projectile),
wind-up, uses, recharge, and the game's invalid-target flags. Writes docs/WH3_blob_candidates_<date>.md and returns the
rows to round146 tools.

  uv run --with openpyxl python tools/list_blob_candidates.py
"""
import collections
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402
import build_ability_database as bd  # noqa: E402
import gamedata_paths as GP  # noqa: E402
import make_progress_page as mp  # noqa: E402


def tsv(name):
    with open(os.path.join(GP.GAMEDATA, name), encoding="utf-8-sig") as f:
        h = f.readline().rstrip("\n").split("\t")
        f.readline()
        for line in f:
            yield dict(zip(h, line.rstrip("\n").split("\t")))


def candidates():
    P = {r["key"]: r for r in tsv("projectiles.tsv")}
    E = {r["key"]: r for r in tsv("projectiles_explosions.tsv")}
    flags = collections.defaultdict(list)
    for r in tsv("special_ability_to_invalid_target_flags_tables.tsv"):
        vals = list(r.values())
        flags[vals[1]].append(vals[0])
    ver, wbp = mp.newest_workbook()
    ws = openpyxl.load_workbook(wbp, read_only=True)["Abilities"]
    trk = {r["key"]: r for r in bd.tracker_rows()}
    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if str(row[17]) != "IN-WHEEL" or str(row[19]) == "IMPLEMENTED":
            continue
        keys = [k.strip() for k in str(row[2]).split(";") if k.strip()]
        st = (trk.get(keys[0]) or {}).get("status", "")
        if mp.group_of(st) != "open" or not mp.open_kind(st, keys[0]).startswith("B."):
            continue
        sp = bd.game_data(keys[0]).get("spec") or {}
        pr = P.get(sp.get("activated_projectile", ""))
        if not pr or not pr.get("explosion_type") or pr["explosion_type"] not in E:
            continue
        ex = E[pr["explosion_type"]]
        out.append({"name": row[1], "key": keys[0], "keys": keys,
                    "range": float(sp.get("target_intercept_range") or 0),
                    "blast": float(ex["detonation_radius"]),
                    "wind": float(sp.get("wind_up_time") or 0), "uses": int(float(sp.get("num_uses") or -1)),
                    "recharge": float(sp.get("recharge_time") or 0), "flags": sorted(flags.get(keys[0], [])),
                    "status": st})
    return out


def main():
    rows = candidates()
    L = ["# Blob-trigger candidates, %s" % datetime.date.today().isoformat(), "",
         "The open group B attacks whose projectile EXPLODES (%d). Range = target_intercept_range; blast = the explosion's "
         "detonation_radius." % len(rows), "",
         "| Ability | Key | Range m | Blast m | Wind-up s | Uses | Recharge s | Game target flags |",
         "|---|---|---:|---:|---:|---:|---:|---|"]
    for r in sorted(rows, key=lambda r: r["name"]):
        L.append("| %s | `%s` | %g | %g | %g | %d | %g | %s |" % (r["name"], r["key"], r["range"], r["blast"], r["wind"],
                                                             r["uses"], r["recharge"], ", ".join(r["flags"]) or "-"))
    fc = collections.Counter(f for r in rows for f in r["flags"])
    L += ["", "Flags: %s" % dict(fc), "Ranges: %s" % dict(collections.Counter(r["range"] for r in rows))]
    out = os.path.join(r"C:\Users\vlady\Desktop\WH3_mod\docs", "WH3_blob_candidates_%s.md" % datetime.date.today().isoformat())
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", out, len(rows), "rows")
    print("flags:", dict(fc))
    print("ranges:", dict(collections.Counter(r["range"] for r in rows)))
    print("keys per row >1:", [r["keys"] for r in rows if len(r["keys"]) > 1])
    print("uses:", dict(collections.Counter(r["uses"] for r in rows)))


if __name__ == "__main__":
    main()
