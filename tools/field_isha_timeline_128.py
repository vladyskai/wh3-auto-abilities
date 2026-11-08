#!/usr/bin/env python3
"""Round 128 field log: the full Isha's Rain timeline per battle (reads every line)."""
import re, sys
A = r"C:\Users\vlady\Desktop\WH3_mod\archive\logs\2026-11-03_round128_battles.txt"
t = 0.0; battle = 0; last_state = None; sel = None
rt = re.compile(r"at t=([0-9.]+)s"); hb = re.compile(r"\] (?:hb t=|tick )(\d+) \|")
for n, line in enumerate(open(A, encoding="utf-8", errors="replace"), 1):
    if "new battle session" in line:
        battle += 1; t = 0.0; last_state = None; print(f"\n===== battle {battle} (line {n})"); continue
    m = rt.search(line)
    if m: t = float(m.group(1))
    m = hb.search(line)
    if m and "hb t=" in line: t = max(t, float(m.group(1)))
    if "selected=" in line and "auto=selected=" in line:
        s = line.split("auto=selected=")[1].split(",")[0]
        if s != sel: sel = s; print(f"  t~{t:7.2f} L{n} tracker selected={s}")
    if "ishas_rain" not in line or "loaded. polling" in line: continue
    if "INVENTORY button_ability" in line:
        st = re.search(r"state='([^']+)'", line).group(1)
        if st != last_state: last_state = st; print(f"  t~{t:7.2f} L{n} BUTTON {st}")
        continue
    for k in ("ATTEMPT ishas", "ACCEPTED", "issued for 'wh2_dlc13_character_ability_ishas", "hold is released", "one use spent", "AUTO ishas", "REJECT", "refused", "not ready", "skip"):
        if k in line:
            print(f"  t~{t:7.2f} L{n} {line.strip()[27:200]}"); break
