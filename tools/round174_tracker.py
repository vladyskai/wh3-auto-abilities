#!/usr/bin/env python3
"""Round 174: the tracker's 28 inventory rows name their round-174 family, and section 10.52 records the round."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_xlsx_v57 as M  # noqa: E402  (nothing is written on import)

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
SECTION = """
### 10.52 Round 174 - the score 1-2 review, rows 24-50 (2026-11-18)

**Rulings (user, 2026-11-18):** "You may implement items 24 to 50"; read F, the spellcaster class (side session): "Okay,
then let's use the caster list". Round document `docs\\WH3_round174_review_rows.md`.

**Changes:**
- **Enemy-targeted:** Amber Bow and Gaze of Nagash on enemy_large_shot; Hand of Gods, Shem's Burning Gaze, Goggly Glare,
  Vindictive Glare on NEW enemy_large_value_shot; Don't Even Try It and Muster of Malevolents on enemy_single_drain; Cube
  of Darkness, Scroll of Leeching, The Vortex Shard, The Black Tongue on NEW enemy_spellcaster; the two Trickster items on
  NEW enemy_ground_spellcasters; Silence the Prey and Power Siphon on enemy_commander_value (commander class); Pageant of
  Shrikes on NEW enemy_missile_value; Chalice of Dark Rain on NEW enemy_ground_shooters; Transfix on NEW
  enemy_commander_wavering. The Hammer of Smednir is unchanged (row 43).
- **Ally-targeted:** Fury of Khaine (NEW ally_charge_melee), Verminous Fury (NEW ally_wavering_melee), Helping Hand (NEW
  ally_lord_melee), Inspired Marksmanship I-III (NEW ally_missile_shooting), Overseer of the Unseen (NEW ally_melee_risk),
  Whiplash! (NEW ally_beast_charge), Iron-Handed Captain (NEW ally_routing: routing allies are no longer skipped for it).
- **GENERATED spellcaster list** (865 land units, tools\\gen_spellcaster_keys.py).

**Arithmetic:** 937 entries / 992 keys / 111 families. Harness 173 full suite **7,304 checks / 0 failures**, run twice
byte-identical; RED 40/40. Pack md5 `c012cfbddab5240cb080b712d5217c0c`; workbook v57.
"""
s = open(P, encoding="utf-8", newline="").read()
crlf = "\r\n" in s
s = s.replace("\r\n", "\n")
n = 0
for key, (fam, _) in M.MOVED.items():
    pat = re.compile(r"(\n\| [^|\n]*`%s` \| )`implemented \([^`]*\)`( \|)" % re.escape(key))
    hits = len(pat.findall(s))
    assert hits == 1, (key, hits)
    s = pat.sub(lambda m: m.group(1) + "`implemented (%s, round 174)`" % fam + m.group(2), s)
    n += 1
anchor = "### 10.51 Round 173 - Null Stone and Rock Eye closed (2026-11-18)\n"
i = s.index(anchor)
ends = [x for x in (s.find("\n### ", i + len(anchor)), s.find("\n## ", i + len(anchor))) if x != -1]
end = min(ends) if ends else len(s)
s = s[:end].rstrip("\n") + "\n" + SECTION + s[end:]
assert "\u2014" not in SECTION and s.count("### 10.52 ") == 1
if crlf:
    s = s.replace("\n", "\r\n")
open(P, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows, section 10.52" % n)
