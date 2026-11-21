#!/usr/bin/env python3
"""Round 193: read the pre-shot probe out of a battle log (read-only).

    python tools/analyze_preshot.py <log> [--from <byte offset>]

For every ranged unit of ours: each WOULD CAST episode ends either at the first shot (PRESHOT 'held X s before the
first shot') or without one (WOULD CAST ENDED, with the reason). First shots that came with no would-cast before them
are counted too. The question it answers: had a buff been cast at WOULD CAST, how often would a shot have followed,
and after how long?"""
import collections
import re
import statistics
import sys

WOULD = re.compile(r"WOULD CAST (unit \S+ '[^']+') at t=([\d.]+)s")
ENDED = re.compile(r"WOULD CAST ENDED (unit \S+ '[^']+') at t=([\d.]+)s after ([\d.]+)s with no shot \(([^)]*)\)")
HELD = re.compile(r"PRESHOT (unit \S+ '[^']+'): the condition held ([\d.]+)s before the first shot")
NONE = re.compile(r"PRESHOT (unit \S+ '[^']+'): the first shot at t=([\d.]+)s came with no would-cast")


def main():
    path = sys.argv[1]
    start = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
    with open(path, "rb") as f:
        f.seek(start)
        text = f.read().decode("utf-8", "replace")
    held, ended, none = [], [], []
    why = collections.Counter()
    per = collections.defaultdict(lambda: [0, 0, 0])
    for line in text.splitlines():
        m = ENDED.search(line)
        if m:
            ended.append(float(m.group(3)))
            why[m.group(4)] += 1
            per[m.group(1)][1] += 1
            continue
        m = HELD.search(line)
        if m:
            held.append(float(m.group(2)))
            per[m.group(1)][0] += 1
            continue
        m = NONE.search(line)
        if m:
            none.append(m.group(1))
            per[m.group(1)][2] += 1
    episodes = len(held) + len(ended)
    print("would-cast episodes:", episodes)
    print("  followed by a first shot:", len(held),
          ("(%.0f%%)" % (100.0 * len(held) / episodes)) if episodes else "")
    if held:
        print("  warning before the shot: median %.2fs, min %.2fs, max %.2fs" % (statistics.median(held), min(held), max(held)))
    print("  ended with no shot:", len(ended), dict(why.most_common()))
    print("first shots with no would-cast before them:", len(none))
    print("\nper unit: shots after a would-cast / would-casts with no shot / shots with no would-cast")
    for u, (a, b, c) in sorted(per.items()):
        print("  %-70s %3d %3d %3d" % (u, a, b, c))


if __name__ == "__main__":
    main()
