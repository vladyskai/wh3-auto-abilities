#!/usr/bin/env python3
"""Build harness192.lua from harness191.lua for round 193 (Scry-Orb on when_ready, the read-only pre-shot probe).
Older harnesses are never edited.

Edits: the banner, the rebases in COUNTS / TRIG / R (each names the pin and why), run_h192 and its call."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_closing_harness191\harness191.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_preshot_harness192\harness192.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h192_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 192 - ROUND 193: SCRY-ORB ON when_ready, THE READ-ONLY PRE-SHOT PROBE (WOULD CAST / WOULD CAST ENDED /
--   PRESHOT log lines, nothing cast).
--   Edited vs harness191: this banner, the rebases listed in tools/make_harness192.py, run_h192 and its call.
--   RED control: H192_LIVE / H192_ANN on docs/backups/round193/pre193_*.lua.
-- ============================================================================
"""
# entries 984 -> 985, keys 1037 -> 1038 (Scry-Orb), the badge-path walk 2 x 985
COUNTS = [("984", "985", None), ("1037", "1038", None), ("1968", "1970", 1)]
# family pins written as cp(s, 'trigger = "<family>"') == N: Scry-Orb joined when_ready
TRIG = [("when_ready", "20", "21")]
R = [
    # the charge gate's multi-use rows 346 -> 347: Scry-Orb (3 uses, 120 s)
    ("""blk ~= nil and cp103(blk, '"] = ') == (RED_MODE and 0 or 346))   -- HARNESS 172: Null Stone closed too""",
     """blk ~= nil and cp103(blk, '"] = ') == (RED_MODE and 0 or 347))   -- HARNESS 172: Null Stone closed too; HARNESS 192: + Scry-Orb""", 1),
    ("(it == 1970)   -- HARNESS 184: 2 x 988; HARNESS 191: 2 x 985",
     "(it == 1970)   -- HARNESS 184: 2 x 988; HARNESS 191: 2 x 984; HARNESS 192: 2 x 985", 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for old, new, want in COUNTS:
        pat = r"(?<!\d)%s(?!\d)" % old
        got = len(re.findall(pat, src))
        assert want is None or got == want, (old, got)
        src = re.sub(pat, new, src)
        print(old, "->", new, ":", got)
    for fam, old, new in TRIG:
        pat = r"""(\w*\(s\w*, 'trigger = "%s"'\) == )%s(?!\d)""" % (fam, old)
        got = len(re.findall(pat, src))
        src = re.sub(pat, r"\g<1>" + new, src)
        print(fam, old, "->", new, ":", got)
    for a, b, n in R:
        assert src.count(a) == n, (a[:80], src.count(a))
        src = src.replace(a, b)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h191()\n") == 1
    src = src.replace("\nrun_h191()\n", "\nrun_h191()\nrun_h192()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST, len(src), "bytes")


if __name__ == "__main__":
    main()
