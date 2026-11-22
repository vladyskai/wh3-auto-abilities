#!/usr/bin/env python3
"""Replay the EXACT-WAVE search (round 205: a cone, at most 5 of our soldiers under it, enemy single entities not
counted) on the MAP rows of a battle log cut, for several CANDIDATE SETS (read-only analysis, an approximation: the
unit rectangles use the mod's own depth estimate with the default infantry spacing).

  python tools/replay_cone.py <log cut> <caster id> <bound m> <radius> <path> <offset> <start radius> <growth per m>

Candidate sets:
  A  round 205: 24 headings x 7 sideways shifts, the start <offset + half extent> before the enemy's centre
  B  A + two more start distances (half extent, and 0 = the start on the enemy's centre)
  C  B with 48 headings (every 7.5 degrees)
Per snapshot with a standing enemy in range it prints the enemy soldiers under the best cone of each set."""
import collections
import math
import re
import sys

ROW = re.compile(r"MAP t=([\d.]+) side=([PE]) (.*)$")
OWN_MAX = 5
SHIFTS = (0, 6, -6, 12, -12, 18, -18)


def parse(path):
    snaps = collections.OrderedDict()
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ROW.search(line)
        if not m:
            continue
        d = dict(kv.split("=", 1) for kv in m.group(3).split() if "=" in kv)
        try:
            d["x"], d["z"], d["w"], b = float(d["x"]), float(d["z"]), float(d["width"]), math.radians(float(d["bearing"]))
        except (KeyError, ValueError):
            continue
        d["side"] = m.group(2)
        d["men"] = int(d.get("men", "0/0").split("/")[0])
        if d["men"] <= 1 or d["w"] < 3:
            d["w"] = max(d["w"], 2.0)
            d["depth"] = d["w"]
        else:
            files = max(1, int(d["w"] / 1.48 + 0.5))
            d["depth"] = math.ceil(d["men"] / files) * 1.6
        d["fx"], d["fz"] = math.sin(b), math.cos(b)
        d["half"] = math.hypot(d["w"], d["depth"]) / 2
        pts = []
        na, nc = max(1, min(10, int(d["w"] / 3 + 0.5))), max(1, min(6, int(d["depth"] / 3 + 0.5)))
        for i in range(na):
            a = (i + 0.5) / na - 0.5
            for j in range(nc):
                c = (j + 0.5) / nc - 0.5
                pts.append((d["x"] + d["fz"] * a * d["w"] + d["fx"] * c * d["depth"],
                            d["z"] - d["fx"] * a * d["w"] + d["fz"] * c * d["depth"]))
        d["pts"] = pts
        snaps.setdefault(float(m.group(1)), []).append(d)
    return snaps


def cover(d, sx, sz, hx, hz, plen, r, r0, g):
    hit = 0
    for px, pz in d["pts"]:
        t = (px - sx) * hx + (pz - sz) * hz
        t = 0.0 if t < 0 else (plen if t > plen else t)
        rr = min(r, r0 + g * t)
        if (px - sx - hx * t) ** 2 + (pz - sz - hz * t) ** 2 <= rr * rr:
            hit += 1
    return d["men"] * hit / len(d["pts"])


def best(c, e_list, ens, ours, bound, r, plen, off, r0, g, steps, backs):
    top = (0.0, None)
    for e in e_list:
        for k in range(steps):
            a = math.radians(k * 360.0 / steps)
            hx, hz = math.sin(a), math.cos(a)
            for back in backs(e):
                for sh in SHIFTS:
                    sx, sz = e["x"] - hx * back + hz * sh, e["z"] - hz * back - hx * sh
                    if math.hypot(sx - c["x"], sz - c["z"]) > bound:
                        continue
                    own = 0.0
                    for o in ours:
                        own += cover(o, sx, sz, hx, hz, plen, r, r0, g)
                        if own > OWN_MAX:
                            break
                    if own > OWN_MAX:
                        continue
                    val = sum(cover(x, sx, sz, hx, hz, plen, r, r0, g) for x in ens if x["men"] > 1)
                    if val > top[0]:
                        top = (val, (round(sx, 1), round(sz, 1), k * 360.0 / steps, back, sh))
    return top


def main():
    path, cid = sys.argv[1], sys.argv[2]
    bound, r, plen, off, r0, g = [float(x) for x in sys.argv[3:9]]
    snaps = parse(path)
    sets = (("A", 24, lambda e: (off + e["half"],)), ("B", 24, lambda e: (off + e["half"], e["half"], 0.0)),
            ("C", 48, lambda e: (off + e["half"], e["half"], 0.0)))
    tot = collections.defaultdict(list)
    for t, rows in snaps.items():
        c = next((d for d in rows if d["side"] == "P" and d.get("id") == cid and d["men"] > 0), None)
        if c is None:
            continue
        ours = [d for d in rows if d["side"] == "P" and d["men"] > 1 and d.get("id") != cid]
        ens = [e for e in rows if e["side"] == "E" and e["men"] > 0 and e.get("vis") == "1"]
        still = [e for e in ens if e.get("moving") == "0" and e.get("fly") != "1"
                 and math.hypot(e["x"] - c["x"], e["z"] - c["z"]) - e["half"] <= bound]
        if not still:
            continue
        line = "t=%5.0f" % t
        for name, steps, backs in sets:
            val, how = best(c, still, ens, ours, bound, r, plen, off, r0, g, steps, backs)
            tot[name].append(val)
            line += "  %s %4.0f %s" % (name, val, how)
        print(line)
    for name in ("A", "B", "C"):
        v = sorted(tot[name])
        if v:
            print("set %s: snapshots %d, median %.0f, mean %.0f, best %.0f" % (name, len(v), v[len(v) // 2], sum(v) / len(v), v[-1]))


if __name__ == "__main__":
    main()
