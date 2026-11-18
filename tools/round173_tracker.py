#!/usr/bin/env python3
"""Round 173: the tracker's two inventory rows read 'skipped (user decision 2026-11-18 ...)', and section 10.51."""
import re

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
CLOSED = {
    "wh3_dlc27_item_abilities_null_stone": "'Close Null stone, Rock Eye.'",
    "wh3_main_item_passive_rock_eye": "'Close Null stone, Rock Eye.'",
}
SECTION = """
### 10.51 Round 173 - Null Stone and Rock Eye closed (2026-11-18)

**Ruling (user, 2026-11-18):** "Close Null stone, Rock Eye." (review rows 18 and 16). Round document
`docs\\WH3_round173_close_two.md`.

**Arithmetic:** 937 entries / 992 keys / 102 families; implemented 992, not implemented 131 (47 skipped). Harness 172
full suite **7,251 checks / 0 failures**, run twice byte-identical; RED 4/4. Pack md5 `b64667d0b84ef3257f3943c7ccc4a7ca`;
workbook v56.
"""
s = open(P, encoding="utf-8", newline="").read()
crlf = "\r\n" in s
s = s.replace("\r\n", "\n")
for key, why in CLOSED.items():
    pat = re.compile(r"(\n\| [^|\n]*`%s` \| )`implemented \([^`]*\)`( \|)" % re.escape(key))
    assert len(pat.findall(s)) == 1, key
    s = pat.sub(lambda m: m.group(1) + "`skipped (user decision 2026-11-18: closed, %s)`" % why + m.group(2), s)
anchor = "### 10.50 Round 172 - rows 1, 3 and 5 of the review as RULED in the doc (2026-11-18)\n"
i = s.index(anchor)
ends = [x for x in (s.find("\n### ", i + len(anchor)), s.find("\n## ", i + len(anchor))) if x != -1]
end = min(ends) if ends else len(s)
s = s[:end].rstrip("\n") + "\n" + SECTION + s[end:]
assert "\u2014" not in SECTION and s.count("### 10.51 ") == 1
if crlf:
    s = s.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(s)
print("tracker: 2 rows, section 10.51")
