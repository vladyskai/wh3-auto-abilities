#!/usr/bin/env python3
"""Replay FREE AIM on the MAP rows of a battle log cut, for several safety margins and with / without SIDEWAYS shifts of
the path (read-only analysis; an APPROXIMATION: unit depth is estimated as men x 1.1 m2 / frontage, the range to the
start point is centre to point).

  python tools/replay_free_aim.py <log cut> <caster id> <bound m> <radius> <path> <offset>

For each margin (metres added to the wave radius) and each shift set it prints: in how many snapshots with a standing
enemy in range a path exists that is clear of our units, and how many enemy soldiers the best such path covers."""
import collections
import math
import re
import sys

ROW = re.compile(r"MAP t=([\d.]+) side=([PE]) (.*)$")
STEPS = 24


def parse(path):
    snaps = collections.OrderedDict()
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ROW.search(line)
        if not m:
            continue
        d = dict(kv.split("=", 1) for kv in m.group(3).split() if "=" in kv)
        try:
            d["x"], d["z"], d["w"], d["b"] = float(d["x"]), float(d["z"]), float(d["width"]), math.radians(float(d["bearing"]))
        except (KeyError, ValueError):
            continue
        d["side"] = m.group(2)
        d["men"] = int(d.get("men", "0/0").split("/")[0])
        d["depth"] = max(1.2, d["men"] * 1.1 / max(d["w"], 1.2))
        snaps.setdefault(float(m.group(1)), []).append(d)
    return snaps


def local(d, px, pz):
    """(across, along) of a point in the unit's own frame: across = along the frontage, along = along the facing."""
    fx, fz = math.sin(d["b"]), math.cos(d["b"])
    dx, dz = px - d["x"], pz - d["z"]
    return dx * fz - dz * fx, dx * fx + dz * fz


def rect_dist(d, px, pz):
    a, l = local(d, px, pz)
    ex, ez = max(0.0, abs(a) - d["w"] / 2), max(0.0, abs(l) - d["depth"] / 2)
    return math.hypot(ex, ez)


def seg_rect_gap(d, sx, sz, ex, ez):
    n = int(math.hypot(ex - sx, ez - sz)) + 1
    return min(rect_dist(d, sx + (ex - sx) * i / n, sz + (ez - sz) * i / n) for i in range(n + 1))


def soldiers(d, sx, sz, ex, ez, r):
    """soldiers of d within r of the segment (a 9 x 5 grid over its rectangle)"""
    fx, fz = math.sin(d["b"]), math.cos(d["b"])
    l2 = (ex - sx) ** 2 + (ez - sz) ** 2
    hit = 0
    for i in range(9):
        for j in range(5):
            a, l = (i / 8 - 0.5) * d["w"], (j / 4 - 0.5) * d["depth"]
            px, pz = d["x"] + a * fz + l * fx, d["z"] - a * fx + l * fz
            t = max(0.0, min(1.0, ((px - sx) * (ex - sx) + (pz - sz) * (ez - sz)) / l2))
            if math.hypot(px - (sx + t * (ex - sx)), pz - (sz + t * (ez - sz))) <= r:
                hit += 1
    return d["men"] * hit / 45.0


def main():
    path, cid = sys.argv[1], sys.argv[2]
    bound, r, plen, off = [float(x) for x in sys.argv[3:7]]
    snaps = parse(path)
    for shifts, sname in (((0,), "through the centre only (round 203)"), ((0, 4, -4, 8, -8, 12, -12, 16, -16, 20, -20), "with sideways shifts up to 20 m")):
        for margin in (10, 6, 3, 0):
            n_snap, n_ok, best_cov = 0, 0, []
            for t, rows in snaps.items():
                ours = [d for d in rows if d["side"] == "P" and d["men"] > 0 and d.get("id") != cid]
                c = next((d for d in rows if d["side"] == "P" and d.get("id") == cid and d["men"] > 0), None)
                if c is None:
                    continue
                ens = [e for e in rows if e["side"] == "E" and e["men"] > 0 and e.get("vis") == "1"]
                still = [e for e in ens if e.get("moving") == "0" and e.get("fly") != "1"
                         and math.hypot(e["x"] - c["x"], e["z"] - c["z"]) - e["w"] / 2 <= bound]
                if not still:
                    continue
                n_snap += 1
                best = 0.0
                for e in still:
                    back = off + e["w"] / 2
                    for k in range(STEPS):
                        a = math.radians(k * 360.0 / STEPS)
                        hx, hz = math.sin(a), math.cos(a)
                        for sh in shifts:
                            sx, sz = e["x"] - hx * back + hz * sh, e["z"] - hz * back - hx * sh
                            if math.hypot(sx - c["x"], sz - c["z"]) > bound:
                                continue
                            ex, ez = sx + hx * plen, sz + hz * plen
                            if any(seg_rect_gap(o, sx, sz, ex, ez) <= r + margin for o in ours):
                                continue
                            cov = sum(soldiers(x, sx, sz, ex, ez, r) for x in ens)
                            if cov > best:
                                best = cov
                if best >= 1:
                    n_ok += 1
                    best_cov.append(best)
            med = sorted(best_cov)[len(best_cov) // 2] if best_cov else 0
            print("%-40s margin %2d m: a clear path in %3d of %3d snapshots; soldiers covered: median %4.0f, best %4.0f"
                  % (sname, margin, n_ok, n_snap, med, max(best_cov) if best_cov else 0))


if __name__ == "__main__":
    main()
