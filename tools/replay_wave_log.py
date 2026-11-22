#!/usr/bin/env python3
"""Replay the enemy_wave rule on the MAP rows of a battle log cut (read-only analysis, an APPROXIMATION of the mod's
own test: unit rectangles are replaced by circles of half the frontage, the range is measured centre to centre).

  python tools/replay_wave_log.py <log cut> <caster id>[,<caster id>...] <range bound m> <radius> <path> <offset> <buf>

Per snapshot and caster it prints one verdict:
  NO ENEMY IN RANGE / ONLY MOVING OR FLYING / BLOCKED BY OURS / CLEAR (the mod would have had a target)
and at the end the totals, plus who blocked most often."""
import collections
import math
import re
import sys

ROW = re.compile(r"MAP t=([\d.]+) side=([PE]) (.*)$")
SAFE = 10.0


def parse(path):
    snaps = collections.OrderedDict()
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ROW.search(line)
        if not m:
            continue
        d = dict(kv.split("=", 1) for kv in m.group(3).split() if "=" in kv)
        try:
            d["x"], d["z"] = float(d["x"]), float(d["z"])
        except (KeyError, ValueError):
            continue
        d["side"] = m.group(2)
        d["men"] = int(d.get("men", "0/0").split("/")[0])
        try:
            d["half"] = float(d.get("width", "0")) / 2.0
        except ValueError:
            d["half"] = 0.0
        snaps.setdefault(float(m.group(1)), []).append(d)
    return snaps


def pt_seg(px, pz, sx, sz, ex, ez):
    l2 = (ex - sx) ** 2 + (ez - sz) ** 2
    if l2 <= 0:
        return math.hypot(px - sx, pz - sz)
    t = max(0.0, min(1.0, ((px - sx) * (ex - sx) + (pz - sz) * (ez - sz)) / l2))
    return math.hypot(px - (sx + t * (ex - sx)), pz - (sz + t * (ez - sz)))


def main():
    path, casters = sys.argv[1], sys.argv[2].split(",")
    bound, r, plen, off, buf = [float(x) for x in sys.argv[3:8]]
    snaps = parse(path)
    tot = collections.Counter()
    blockers = collections.Counter()
    clear_at = []
    for t, rows in snaps.items():
        ours = [d for d in rows if d["side"] == "P" and d["men"] > 0 and d.get("routing") != "1"]
        enemies = [d for d in rows if d["side"] == "E" and d["men"] > 0 and d.get("vis") == "1"]
        for cid in casters:
            c = next((d for d in ours if d.get("id") == cid), None)
            if c is None:
                tot[(cid, "CASTER DEAD OR ROUTING")] += 1
                continue
            in_range = [e for e in enemies if math.hypot(e["x"] - c["x"], e["z"] - c["z"]) - e["half"] <= bound]
            if not in_range:
                tot[(cid, "NO ENEMY IN RANGE")] += 1
                continue
            still = [e for e in in_range if e.get("moving") == "0" and e.get("fly") != "1"]
            if not still:
                tot[(cid, "ONLY MOVING OR FLYING ENEMIES IN RANGE")] += 1
                continue
            clear = []
            for e in still:
                dx, dz = e["x"] - c["x"], e["z"] - c["z"]
                ln = math.hypot(dx, dz)
                if ln < 0.5:
                    continue
                hx, hz = dx / ln, dz / ln
                back = off + e["half"]
                sx, sz = e["x"] - hx * back, e["z"] - hz * back
                ex, ez = sx + hx * plen, sz + hz * plen
                hit = None
                for o in ours:
                    if o.get("id") == cid:
                        continue
                    if pt_seg(o["x"], o["z"], sx, sz, ex, ez) - o["half"] <= r + SAFE + buf:
                        hit = o
                        break
                if hit is None:
                    clear.append(e)
                else:
                    blockers[hit.get("type", "?")] += 1
            if clear:
                tot[(cid, "CLEAR: a standing target with a free path")] += 1
                clear_at.append((t, cid, clear[0].get("type"), c.get("moving"), c.get("melee")))
            else:
                tot[(cid, "BLOCKED: one of our units stands in every path")] += 1
    print("snapshots:", len(snaps))
    for (cid, what), n in sorted(tot.items()):
        print("  caster %s  %-50s %4d" % (cid, what, n))
    print("most frequent blockers:", blockers.most_common(6))
    print("clear moments (t, caster, target, caster moving, caster melee):")
    for x in clear_at[:40]:
        print("  ", x)
    print("clear moments in total:", len(clear_at))


if __name__ == "__main__":
    main()
