#!/usr/bin/env python3
"""How many soldiers of each unit lie under ONE given cone, snapshot by snapshot (read-only analysis).

  python tools/replay_cone_cast.py <log cut> <start x> <start z> <bearing> <radius> <path> <start radius> <growth>
                                   <t from> <t to>

It shows what a cast was aimed at (the snapshot of the order) and what stood there while the wave rolled."""
import math
import sys

import replay_cone as RC


def main():
    path = sys.argv[1]
    sx, sz, brg, r, plen, r0, g, t0, t1 = [float(x) for x in sys.argv[2:11]]
    hx, hz = math.sin(math.radians(brg)), math.cos(math.radians(brg))
    for t, rows in RC.parse(path).items():
        if not (t0 <= t <= t1):
            continue
        parts = []
        for d in rows:
            if d["men"] > 1:
                parts.append("%s%s %s moving=%s: %3.0f of %d" % (d["side"], d.get("id"), d.get("type", "?")[-16:], d.get("moving"),
                                                               RC.cover(d, sx, sz, hx, hz, plen, r, r0, g), d["men"]))
        print("t=%4.0f  " % t + " | ".join(parts))


if __name__ == "__main__":
    main()
