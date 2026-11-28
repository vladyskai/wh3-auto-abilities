#!/usr/bin/env python3
"""Replay the enemy_wander rule (a placed blast that can hit our own units) on the MAP rows of a battle log cut.
Read-only analysis, an APPROXIMATION of the mod's own test: a unit is a circle of half its frontage, ranges are
measured centre to centre, the density line and the armour rule are NOT replayed.

  python tools/replay_wander_log.py <log cut> <caster id>[,<id>...] <range bound m> <blast radius m> [<drift m>]

Per snapshot (every 2 s) and caster one verdict:
  CASTER MOVING / NO ENEMY BLOCK IN RANGE / ONLY MOVING BLOCKS / BLOCKED BY OURS / CLEAR (a target existed)"""
import collections
import math
import re
import sys

ROW = re.compile(r"MAP t=([\d.]+) side=([PE]) (.*)$")
SAFE = 10.0
TRASH_VPS = 2.0


def parse(path):
    snaps = collections.OrderedDict()
    for line in open(path, encoding="utf-8", errors="replace"):
        m = ROW.search(line)
        if not m:
            continue
        d = dict(kv.split("=", 1) for kv in m.group(3).split() if "=" in kv)
        try:
            d["x"], d["z"] = float(d["x"]), float(d["z"])
            d["men"] = int(d.get("men", "0/0").split("/")[0])
            d["half"] = float(d.get("width", "0")) / 2.0
            d["sv"] = float(d.get("sv", "0"))
        except ValueError:
            continue
        d["side"] = m.group(2)
        snaps.setdefault(float(m.group(1)), []).append(d)
    return snaps


def main():
    path, casters = sys.argv[1], sys.argv[2].split(",")
    bound, radius = float(sys.argv[3]), float(sys.argv[4])
    drift = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
    need = radius + drift + SAFE
    tot = collections.Counter()
    blockers = collections.Counter()
    gaps = []
    per_time = collections.OrderedDict()
    for t, rows in parse(path).items():
        ours = [r for r in rows if r["side"] == "P" and r["men"] > 0]
        foes = [r for r in rows if r["side"] == "E" and r["men"] > 0]
        protected = [o for o in ours if not (o["men"] > 0 and o["sv"] / o["men"] < TRASH_VPS)]
        for cid in casters:
            c = next((o for o in ours if o.get("id") == cid), None)
            if c is None:
                continue
            if c.get("moving") == "1":
                tot["CASTER MOVING"] += 1
                continue
            blocks = [e for e in foes if e.get("vis") == "1" and e.get("inf") == "1" and e.get("fly") != "1"
                      and e["men"] >= 10 and math.hypot(e["x"] - c["x"], e["z"] - c["z"]) - e["half"] <= bound]
            if not blocks:
                tot["NO ENEMY BLOCK IN RANGE"] += 1
                continue
            still = [e for e in blocks if e.get("moving") == "0"]
            if not still:
                tot["ONLY MOVING BLOCKS"] += 1
                continue
            clear = False
            best_gap = None
            for e in still:
                near = None
                for o in protected:
                    if o is c and False:
                        continue
                    g = math.hypot(o["x"] - e["x"], o["z"] - e["z"]) - o["half"]
                    if near is None or g < near[0]:
                        near = (g, o)
                if near is None or near[0] > need:
                    clear = True
                else:
                    blockers[near[1].get("type", "?")] += 1
                    if best_gap is None or near[0] > best_gap:
                        best_gap = near[0]
            if clear:
                tot["CLEAR (a target existed)"] += 1
                per_time.setdefault(t, []).append(cid)
            else:
                tot["BLOCKED BY OURS"] += 1
                gaps.append(best_gap)
    print("rule replayed: none of our (non-expendable) units within %.0f m of the target (radius %.0f + drift %.0f + %.0f)"
          % (need, radius, drift, SAFE))
    for k, v in tot.most_common():
        print("%6d  %s" % (v, k))
    if gaps:
        gaps.sort()
        print("when blocked, the BEST standing block still had one of ours at: median %.1f m, largest %.1f m (need more than %.0f)"
              % (gaps[len(gaps) // 2], gaps[-1], need))
        for lim in (22, 17, 14, 12):
            print("   snapshots that would be clear with a %2d m keep-out: %d of %d blocked ones" % (lim, sum(1 for g in gaps if g > lim), len(gaps)))
    print("who stood too close most often:")
    for k, v in blockers.most_common(6):
        print("%6d  %s" % (v, k))
    print("clear moments (time: casters): " + "; ".join("%.0f: %s" % (t, ",".join(c)) for t, c in list(per_time.items())[:25]))


if __name__ == "__main__":
    main()
