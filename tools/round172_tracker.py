#!/usr/bin/env python3
"""Round 172: the tracker's three inventory rows name their round-172 family, and section 10.50 records the round."""
import re

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
MOVED = {
    "wh_dlc05_item_abilities_horn_of_the_wild_hunt": "army_charge",
    "wh3_main_character_abilities_ursuns_roar": "aura_charge",
    "wh_main_character_abilities_waaagh": "army_charge_or_melee",
}
SECTION = """
### 10.50 Round 172 - rows 1, 3 and 5 of the review as RULED in the doc (2026-11-18)

**Why:** round 171 built the first proposals for these rows; `docs\\WH3_low_score_review_2026-11-17.md` already carried
the user's rulings (user: "I feel like you ignored the current version of the WH_3_low_score_review"; "Yes, fix them
now"). Round document `docs\\WH3_round172_ruled_rows.md`.

**Changes:**
- **Horn of the Wild Hunt (row 1, army_charge):** 3 of our units charging or in fresh contact, or every living unit
  when the army has fewer than 3.
- **Ursun's Roar, the charge key (row 3, aura_charge):** ONE unit, the caster or any unit within its 24 m aura,
  charging, in fresh contact or wavering ("Agreed, and include the wavering").
- **Waaagh!, the wh_main key (row 5):** NEW family army_charge_or_melee: the army charge as Horn, OR the same count in
  melee.

**Arithmetic:** 939 entries / 994 keys / 102 families. Harness 171 full suite **7,240 checks / 0 failures**, run twice
byte-identical; RED 20/20. Pack md5 `239b195b95d7734233d50a7ed1c75698`; workbook v55.
"""
s = open(P, encoding="utf-8", newline="").read()
crlf = "\r\n" in s
s = s.replace("\r\n", "\n")
for key, fam in MOVED.items():
    pat = re.compile(r"(\n\| [^|\n]*`%s` \| )`implemented \([^`]*\)`( \|)" % re.escape(key))
    assert len(pat.findall(s)) == 1, key
    s = pat.sub(lambda m: m.group(1) + "`implemented (%s, round 172)`" % fam + m.group(2), s)
anchor = "### 10.49 Round 171 - the score 1-2 review, rows 1-15 and 21 (2026-11-17)\n"
i = s.index(anchor)
j = s.find("\n### ", i + len(anchor))
k = s.find("\n## ", i + len(anchor))
ends = [x for x in (j, k) if x != -1]
end = min(ends) if ends else len(s)
body = s[:end].rstrip("\n") + "\n"
s = body + SECTION + s[end:] if end < len(s) else body + SECTION
assert "\u2014" not in SECTION and s.count("### 10.50 ") == 1
if crlf:
    s = s.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(s)
print("tracker: 3 rows, section 10.50")
