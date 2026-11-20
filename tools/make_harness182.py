#!/usr/bin/env python3
"""Build harness182.lua from harness181.lua for round 183 (the rule-shut review, rows 1-9). Older harnesses are never
edited.

Rebases: see R (each names the pin and why)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_finishers_harness181\harness181.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut1_harness182\harness182.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h182_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 182 - ROUND 183: THE RULE-SHUT REVIEW, ROWS 1-9 (Defiling Deluge, Murderous
--   Exhortations, Rod of Corruption, Wail of Malice on enemy_melee_near; Plaguereaper,
--   Reaper of Souls on melee_health75; Shard Blade, Web of Shadows, Warp-Quake on
--   melee_unwavering).
--   Edited vs harness181: this banner, the rebases listed in tools/make_harness182.py,
--   run_h182 and its call.
--   RED control: H182_LIVE / H182_ANN on docs/backups/round183/pre183_*.lua.
-- ============================================================================
"""
R = [
    ("(it == 1872)   -- HARNESS 177: 2 x 936", "(it == 1890)   -- HARNESS 182: 2 x 945", 1),
    # the charge gate: 6 new multi-use keys (Defiling Deluge, Murderous Exhortations, Rod of Corruption, Wail of
    # Malice, Plaguereaper, Shard Blade)
    ("""cp103(blk, '"] = ') == (RED_MODE and 0 or 326))""", """cp103(blk, '"] = ') == (RED_MODE and 0 or 332))""", 1),
    # melee_health75 2 -> 4 (Plaguereaper, Reaper of Souls)
    ("""(s, 'trigger = "melee_health75"') == 2""", """(s, 'trigger = "melee_health75"') == 4""", 4),
]
import re  # noqa: E402
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
# the entry and key counts: 936 -> 945 entries, 989 -> 998 keys (the 9 new entries, one key each);
# melee_unwavering 265 -> 268 (Shard Blade, Web of Shadows, Warp-Quake)
for old, new, want in (("936", "945", 93), ("989", "998", 11), ("265", "268", 17)):
    pat = r"(?<!\d)%s(?!\d)" % old
    got = len(re.findall(pat, src))
    assert got == want, (old, got)
    src = re.sub(pat, new, src)
    print(old, "->", new, ":", got)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h181()\n") == 1
src = src.replace("\nrun_h181()\n", "\nrun_h181()\nrun_h182()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
