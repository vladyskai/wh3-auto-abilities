#!/usr/bin/env python3
"""Round 145: read the battlefield MAP rows the probe writes into the battle log and report what they show.

  uv run python tools/analyze_map_log.py <log or log cut> [--from <byte offset>] [--out <report.md>]
  uv run python tools/analyze_map_log.py --selftest

Never reads the live log whole: with --from it seeks to the byte offset first (cut the battle from the size the log had
before the battle, as CLAUDE.md says).

The report:
  1. READABILITY - per side, how often each read answered (width, bearing, officer, value, visibility, ...). This
     answers "do the reads work on ENEMY units at all?".
  2. VALUE - strategic_value() next to the game's multiplayer cost (main_units), and next to cost x health.
  3. FOOTPRINT - the estimated block depth: files = width / close spacing (unit_spacings, the land_units spacing key),
     ranks = men / files, depth = ranks x the vertical spacing. Depth is NOT a game read: it is an estimate.
  4. BLOBS - per snapshot, the point where a circle of radius R covers the most ENEMY INFANTRY soldiers (each unit's
     soldiers spread evenly over its estimated rectangle, turned by its bearing), with OUR soldiers inside the same
     circle counted next to it (friendly-fire risk). Radii 10, 15, 20 m (stand-ins until a real ability is chosen).
     Only enemies whose vis= is not 0 are used (an unreadable visibility is kept and counted apart).

Assumption, stated in the report: bearing b (degrees) faces the direction (sin b, cos b) on the X/Z ground plane; the
width runs across that. If the field log shows otherwise, flip it here.
"""
import collections
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402
import gen_unit_size_keys as SZ  # noqa: E402

ROW = re.compile(r"MAP t=(?P<t>[\d.]+) side=(?P<side>[PE]) (?P<rest>.*)$")
END = re.compile(r"MAP_END t=(?P<t>[\d.]+) own=(?P<own>\d+) enemy=(?P<en>\d+) alliance=(?P<al>\S+)")
FIELDS = ("x", "z", "ox", "oz", "bearing", "width", "men", "hp", "sv", "inf", "class", "vis", "melee", "moving", "fly",
          "routing", "type", "id")
RADII = (10, 15, 20)


def tsv(path):
    with open(path, encoding="utf-8-sig") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        f.readline()
        for line in f:
            c = line.rstrip("\n").split("\t")
            if len(c) >= len(hdr) // 2:
                yield dict(zip(hdr, c))


def load_tables():
    spacing_of, cost_of, men_of = {}, {}, {}
    for r in tsv(os.path.join(GP.GAMEDATA, "land_units.tsv")):
        spacing_of[r["key"]] = r.get("spacing", "")
    for r in tsv(os.path.join(GP.GAMEDATA, "main_units.tsv")):
        lu = r.get("land_unit", "")
        try:
            cost_of.setdefault(lu, float(r.get("multiplayer_cost", "") or "nan"))
            men_of.setdefault(lu, int(r.get("num_men", "0") or 0))
        except ValueError:
            pass
    sp = {}
    p = os.path.join(GP.GAMEDATA, "unit_spacings.tsv")
    if os.path.exists(p):
        for r in tsv(p):
            try:
                sp[r["key"]] = (float(r["close_formation_spacing_horizontal"]), float(r["close_formation_spacing_vertical"]))
            except (KeyError, ValueError):
                pass
    large, _single = SZ.derive()
    return spacing_of, cost_of, men_of, sp, set(large)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse(lines):
    snaps = collections.OrderedDict()
    ends = {}
    for line in lines:
        m = ROW.search(line)
        if m:
            d = {"t": float(m.group("t")), "side": m.group("side")}
            for kv in m.group("rest").split(" "):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    d[k] = v
            if "men" in d and "/" in d["men"]:
                d["men_alive"], d["men_initial"] = d["men"].split("/", 1)
            snaps.setdefault(d["t"], []).append(d)
            continue
        m = END.search(line)
        if m:
            ends[float(m.group("t"))] = (int(m.group("own")), int(m.group("en")), m.group("al"))
    return snaps, ends


def footprint(d, T):
    spacing_of, cost_of, men_of, sp, large = T
    w = num(d.get("width"))
    men = num(d.get("men_alive"))
    h_v = sp.get(spacing_of.get(d.get("type", ""), ""))
    if w is None or men is None or men <= 0:
        return None
    if men <= 1 or w < 3:
        r = max(w, 2.0)
        return r, r, "single"
    # field 2026-11-13: vehicles, monsters and cavalry blocks are not ranked infantry (land ships came out 575 m
    # deep); their footprint is taken as square (width x width)
    if not str(d.get("class", "")).startswith("inf") or d.get("type") in large:
        return w, w, "square (not ranked infantry)"
    if h_v is None:
        h_v = (1.5, 1.6)
        how = "est (default spacing)"
    else:
        how = "est"
    h, v = h_v
    files = max(1, int(round(w / h)))
    ranks = max(1, math.ceil(men / files))
    return w, ranks * v, how


def samples(d, T, n=5):
    fp = footprint(d, T)
    x, z, b, men = num(d.get("x")), num(d.get("z")), num(d.get("bearing")), num(d.get("men_alive"))
    if fp is None or x is None or z is None or not men:
        return []
    w, depth, _ = fp
    b = math.radians(b or 0.0)
    fx, fz = math.sin(b), math.cos(b)        # facing (assumption)
    rx, rz = fz, -fx                         # across the front
    out = []
    for i in range(n):
        for j in range(n):
            a = (i + 0.5) / n - 0.5
            c = (j + 0.5) / n - 0.5
            out.append((x + rx * a * w + fx * c * depth, z + rz * a * w + fz * c * depth, men / (n * n)))
    return out


def is_infantry(d, T):
    # field 2026-11-13: is_infantry() and unit_class() both say infantry for Fell Bats, Devils of Swartzhafen, the
    # Varghulf and the Zombie Dragon. Infantry here = an infantry class, NOT in the generated large set, not flying,
    # at least 10 soldiers alive.
    men = num(d.get("men_alive")) or 0
    return (str(d.get("class", "")).startswith("inf") and d.get("type") not in T[4]
            and d.get("fly") != "1" and men >= 10)


def blobs(rows, T, R, safe=False):
    enemy = [d for d in rows if d["side"] == "E" and is_infantry(d, T) and d.get("vis") != "0"]
    ours = [d for d in rows if d["side"] == "P"]
    pts_e = [(d, samples(d, T)) for d in enemy]
    pts_o = [p for d in ours for p in samples(d, T)]
    cands = []
    for d, _ in pts_e:
        if num(d.get("x")) is not None:
            cands.append((num(d["x"]), num(d["z"])))
    for i in range(len(enemy)):
        for j in range(i + 1, len(enemy)):
            a, b = enemy[i], enemy[j]
            ax, az, bx, bz = num(a.get("x")), num(a.get("z")), num(b.get("x")), num(b.get("z"))
            if None not in (ax, az, bx, bz) and math.hypot(ax - bx, az - bz) <= 2 * R + 30:
                cands.append(((ax + bx) / 2, (az + bz) / 2))
    best = None
    for cx, cz in cands:
        got, units = 0.0, []
        for d, ps in pts_e:
            inside = sum(m for px, pz, m in ps if math.hypot(px - cx, pz - cz) <= R)
            if inside >= 1:
                got += inside
                units.append("%s(%d)" % (d.get("type", "?").split("_")[-1], round(inside)))
        friendly = sum(m for px, pz, m in pts_o if math.hypot(px - cx, pz - cz) <= R + 5)
        if safe and friendly >= 1:
            continue
        if best is None or got > best[0]:
            best = (got, cx, cz, units, friendly)
    return best


def report(snaps, ends, T):
    spacing_of, cost_of, men_of, sp, large = T
    L = ["# Battlefield map probe report", ""]
    allrows = [d for rows in snaps.values() for d in rows]
    L.append("Snapshots: %d; rows: %d (ours %d, enemy %d). Alliance read: %s." % (
        len(snaps), len(allrows), sum(1 for d in allrows if d["side"] == "P"),
        sum(1 for d in allrows if d["side"] == "E"),
        ", ".join(sorted(set(e[2] for e in ends.values()))) or "?"))
    L += ["", "## 1. Readability (share of rows where the read answered)", "",
          "| Read | Ours | Enemy |", "|---|---:|---:|"]
    for k in ("x", "ox", "bearing", "width", "men_alive", "hp", "sv", "inf", "vis", "melee", "moving", "fly", "routing"):
        cells = []
        for side in "PE":
            rs = [d for d in allrows if d["side"] == side]
            ok = sum(1 for d in rs if d.get(k) not in (None, "?", "-"))
            cells.append("%d%%" % (100 * ok / len(rs)) if rs else "-")
        L.append("| %s | %s | %s |" % (k, cells[0], cells[1]))
    vis = collections.Counter(d.get("vis") for d in allrows if d["side"] == "E")
    L.append("")
    L.append("Enemy visibility values: %s." % dict(vis))
    L += ["", "## 2. Value: strategic_value() next to the game's cost", ""]
    pairs = [(num(d.get("sv")), cost_of.get(d.get("type")), num(d.get("hp"))) for d in allrows]
    pairs = [p for p in pairs if p[0] is not None and p[1] is not None and not math.isnan(p[1])]
    if len(pairs) >= 3:
        def corr(a, b):
            ma, mb = sum(a) / len(a), sum(b) / len(b)
            va = math.sqrt(sum((x - ma) ** 2 for x in a)); vb = math.sqrt(sum((y - mb) ** 2 for y in b))
            return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) if va and vb else float("nan")
        sv = [p[0] for p in pairs]
        L.append("Rows with both: %d. Correlation with cost: %.2f; with cost x health: %.2f." % (
            len(pairs), corr(sv, [p[1] for p in pairs]), corr(sv, [p[1] * (p[2] or 1) for p in pairs])))
        per = collections.defaultdict(list)
        for d in allrows:
            if num(d.get("sv")) is not None:
                per[d.get("type")].append(num(d["sv"]))
        L += ["", "| Unit type | Cost | strategic_value (min / max) |", "|---|---:|---|"]
        for t2, vs in sorted(per.items(), key=lambda kv: -(cost_of.get(kv[0]) or 0))[:25]:
            L.append("| %s | %s | %.1f / %.1f |" % (t2, cost_of.get(t2, "?"), min(vs), max(vs)))
    else:
        L.append("strategic_value() did not answer often enough to compare (%d rows)." % len(pairs))
    L += ["", "## 3. Footprints (estimated depth; width is the engine's ordered width)", "",
          "| Unit type | Side | Width m | Men | Est. depth m | How |", "|---|---|---:|---:|---:|---|"]
    seen = set()
    for d in allrows:
        k = (d.get("type"), d["side"])
        if k in seen:
            continue
        fp = footprint(d, T)
        if fp is None:
            continue
        seen.add(k)
        L.append("| %s | %s | %.1f | %s | %.1f | %s |" % (k[0], k[1], fp[0], d.get("men_alive"), fp[1], fp[2]))
    L += ["", "## 4. Blobs: the best circle each snapshot (enemy infantry soldiers inside; ours within R + 5 m)", "",
          "Bearing assumption: facing (sin b, cos b) on X/Z.", ""]
    for R, safe in [(r, False) for r in RADII] + [(r, True) for r in RADII]:
        L += ["### Radius %d m%s" % (R, " - SAFE (none of ours within R + 5 m)" if safe else ""), "",
              "| t (s) | Enemy soldiers inside | Units | Centre (x, z) | Ours near |", "|---:|---:|---|---|---:|"]
        rowsR = []
        for t, rows in snaps.items():
            b = blobs(rows, T, R, safe)
            if b is not None and b[0] >= 1:
                rowsR.append((t, b))
        for t, b in sorted(rowsR, key=lambda tb: -tb[1][0])[:15]:
            L.append("| %.1f | %d | %s | %.0f, %.0f | %d |" % (t, round(b[0]), ", ".join(b[3]), b[1], b[2], round(b[4])))
        L.append("")
    return "\n".join(L) + "\n"


def selftest():
    T = load_tables()
    lines = [
        "MAP t=2.0 side=E id=1 type=wh_main_grn_inf_orc_boyz x=0.0 z=0.0 ox=? oz=? bearing=0 width=30.0 men=120/120 hp=1.00 sv=50.0 inf=1 class=inf_mel vis=1 melee=1 moving=0 fly=0 routing=0",
        "MAP t=2.0 side=E id=2 type=wh_main_grn_inf_orc_boyz x=12.0 z=4.0 ox=? oz=? bearing=0 width=30.0 men=120/120 hp=1.00 sv=50.0 inf=1 class=inf_mel vis=1 melee=1 moving=0 fly=0 routing=0",
        "MAP t=2.0 side=E id=3 type=wh_main_grn_inf_orc_boyz x=300.0 z=300.0 ox=? oz=? bearing=0 width=30.0 men=120/120 hp=1.00 sv=50.0 inf=1 class=inf_mel vis=0 melee=0 moving=0 fly=0 routing=0",
        "MAP t=2.0 side=P id=9 type=wh_main_emp_inf_swordsmen x=0.0 z=-12.0 ox=? oz=? bearing=180 width=29.4 men=110/120 hp=0.90 sv=40.0 inf=1 class=inf_mel vis=1 melee=1 moving=0 fly=0 routing=-",
        "MAP_END t=2.0 own=1 enemy=3 alliance=1",
    ]
    snaps, ends = parse(lines)
    b = blobs(snaps[2.0], T, 15)
    assert b is not None and b[0] > 120, b          # the two overlapping orc blocks, not one
    assert abs(b[1] - 6.0) < 0.1, b                 # centred between them (the pair midpoint)
    assert b[4] > 0, b                              # our swordsmen are close: friendly risk counted
    fp = footprint(snaps[2.0][0], T)
    assert fp is not None and abs(fp[1] - 23.0) < 1e-6, fp   # orcs: 30 m / 2.3 m -> 13 files; 120 / 13 -> 10 ranks x 2.3 m
    r = report(snaps, ends, T)
    assert "Readability" in r and "—" not in r
    print("SELFTEST OK: best 15 m circle %.0f enemy soldiers at (%.1f, %.1f), %d of ours near; orc depth %.1f m"
          % (b[0], b[1], b[2], b[4], fp[1]))


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    path = sys.argv[1]
    start = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    lines = []
    with open(path, "rb") as f:
        f.seek(start)
        for raw in f:
            if b"MAP" in raw:
                lines.append(raw.decode("utf-8", "replace").rstrip("\r\n"))
    snaps, ends = parse(lines)
    if not snaps:
        print("no MAP rows after byte", start)
        return
    r = report(snaps, ends, load_tables())
    if out:
        open(out, "w", encoding="utf-8", newline="\n").write(r)
        print("wrote", out)
    else:
        print(r)


if __name__ == "__main__":
    main()
