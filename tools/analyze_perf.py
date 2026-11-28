#!/usr/bin/env python3
"""Read the PERF lines of a battle (round 214's timing probe) and say where the mod's time went.

    python tools/analyze_perf.py <log file> [--from <byte offset>]

For every second of real time the mod logs how many milliseconds its UI timer and its polls took, split by job. This
prints the totals, the share of each job, the worst seconds, and how many of the worst seconds sit next to a
selection change (the 'selection:' / 'card ... selected' lines of the same log)."""
import re
import sys

PAT = re.compile(r"PERF 1s: ui (\d+) ticks ([\d.]+) ms \(worst tick ([\d.]+)\) \| walk (\d+)x ([\d.]+) ms \| cards ([\d.]+) ms "
                 r"\| select ([\d.]+) ms \| badges ([\d.]+) ms \| diag ([\d.]+) ms \| poll (\d+)x ([\d.]+) ms \(worst ([\d.]+)\)")
SEL = ("engine selection", "selected-tracker", "selection set", "click:")


def main():
    path = sys.argv[1]
    start = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
    rows, sel_lines = [], []
    with open(path, "rb") as f:
        f.seek(start)
        for n, raw in enumerate(f):
            line = raw.decode("utf-8", "replace")
            m = PAT.search(line)
            if m:
                g = m.groups()
                rows.append(dict(n=n, ticks=int(g[0]), ui=float(g[1]), worst=float(g[2]), walks=int(g[3]), walk=float(g[4]),
                                 cards=float(g[5]), select=float(g[6]), badges=float(g[7]), diag=float(g[8]),
                                 polls=int(g[9]), poll=float(g[10]), poll_worst=float(g[11])))
            elif any(s in line for s in SEL):
                sel_lines.append(n)
    if not rows:
        print("no PERF line found (is the test build ticked in the mod manager?)")
        return
    secs = len(rows)
    tot = {k: sum(r[k] for r in rows) for k in ("ui", "walk", "cards", "select", "badges", "diag", "poll")}
    rest = tot["ui"] - tot["walk"] - tot["cards"] - tot["select"] - tot["badges"] - tot["diag"]
    print("%d seconds measured" % secs)
    print("the mod's time per second of play: UI timer %.1f ms + polls %.1f ms = %.1f ms (%.2f%% of the second)"
          % (tot["ui"] / secs, tot["poll"] / secs, (tot["ui"] + tot["poll"]) / secs, (tot["ui"] + tot["poll"]) / secs / 10))
    print("where the UI timer's time went:")
    for k, v in (("the HUD walk", tot["walk"]), ("reading the unit cards", tot["cards"]), ("selection events", tot["select"]),
                 ("placing the letters and the button", tot["badges"]), ("the test build's own log sweeps", tot["diag"]),
                 ("the rest (the per-ability letter loops)", rest)):
        print("   %-42s %8.1f ms  %5.1f%%" % (k, v, 100 * v / tot["ui"] if tot["ui"] else 0))
    print("HUD walks: %d in %d seconds, %.1f ms each on average" % (sum(r["walks"] for r in rows), secs,
          tot["walk"] / max(1, sum(r["walks"] for r in rows))))
    print("the worst single UI tick: %.1f ms. The worst single poll: %.1f ms" % (max(r["worst"] for r in rows),
          max(r["poll_worst"] for r in rows)))
    for limit in (8, 16, 33):
        print("   seconds with a UI tick over %2d ms: %d" % (limit, sum(1 for r in rows if r["worst"] > limit)))
    worst = sorted(rows, key=lambda r: -r["worst"])[:10]
    print("the 10 worst seconds (worst tick, walks, walk ms, cards ms, a selection change within 60 log lines?):")
    for r in worst:
        near = any(abs(s - r["n"]) <= 60 for s in sel_lines)
        print("   %6.1f ms   walks %2d   walk %6.1f   cards %5.1f   diag %5.1f   poll %5.1f   selection near: %s"
              % (r["worst"], r["walks"], r["walk"], r["cards"], r["diag"], r["poll"], "yes" if near else "no"))


if __name__ == "__main__":
    main()
