#!/usr/bin/env python3
"""Round 128 field log: for every charge-gated cast, when did its button next read READY
(active/hover) while the caster was shown, versus the 120-type table hold? Reads every line."""
import re
A = r"C:\Users\vlady\Desktop\WH3_mod\archive\logs\2026-11-03_round128_battles.txt"
t = 0.0; b = 0; casts = {}; last_inv = {}; pending = None
att = re.compile(r"ATTEMPT (\S+) '([^']+)' on '([^']+)' ui id (\d+)")
hold = re.compile(r"charge gate (\S+): one use spent - the next attempt waits (\d+)s")
for line in open(A, encoding="utf-8", errors="replace"):
    if "new battle session" in line:
        b += 1; t = 0.0; casts = {}; last_inv = {}; continue
    m = re.search(r"at t=([0-9.]+)s", line)
    if m: t = float(m.group(1))
    m = att.search(line)
    if m: pending = (m.group(1), m.group(2), m.group(4)); continue
    m = hold.search(line)
    if m and pending and pending[0] == m.group(1):
        k = pending[1]
        prev = casts.get(k)
        casts[k] = {"t": t, "hold": int(m.group(2)), "seen_busy": None, "ready": None, "marker": m.group(1), "uid": pending[2]}
        print(f"b{b} {t:7.2f} CAST {m.group(1)} (unit {pending[2]}), hold {m.group(2)}s")
        continue
    if "INVENTORY button_ability" in line:
        mk = re.search(r"state='([^']+)' key='([^']+)'", line)
        if not mk: continue
        s, k = mk.groups()
        c = casts.get(k)
        if c is None: continue
        if s in ("inactive", "selected_inactive"): c["seen_busy"] = t
        elif s in ("active", "hover") and c["ready"] is None and t - c["t"] > 1.0:
            c["ready"] = t
            busy = c["seen_busy"]
            print(f"b{b} {t:7.2f}   {c['marker']} READY on screen {t-c['t']:6.2f}s after the cast "
                  f"(last seen busy {('%.2f' % (busy - c['t'])) if busy else 'never'}s after) vs hold {c['hold']}s")
