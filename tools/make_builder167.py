#!/usr/bin/env python3
"""Build the round-167 build script from the round-166 one (no final period, the safer defaults).

Gate rebases (the user's ruling 2026-11-17: no final period on a one-sentence tooltip):
  * the round-166 gate pinned the bare return '... .. "."' and the ALL text with its period: both now pin the text
    without the period.
ROUND 167 GATE:
  * the RISKY table REGENERATED from the game data (tools/gen_risky_keys.py) and equal to the shipped text;
  * the family default skips a risky entry (FOURTH.entry_risky in the default_on rule);
  * no card sentence and no ALL text ends with a period.
No count gate moves (946 entries, 1,003 keys)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_short_cards_harness165\build_and_install166.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_periods_risky_harness166\build_and_install167.py"
R = [
    ("""assert ' .. " on A: " .. ' not in script_txt and '\\treturn table.concat(parts, "; ") .. "."' in script_txt, \\\n""",
     """assert ' .. " on A: " .. ' not in script_txt and '\\treturn table.concat(parts, "; ")   -- ROUND 166' in script_txt, \\\n"""),
    ("""assert 'FOURTH.ALL_TIP = "Arm or disarm every automatic ability of the selected unit(s)."\\n' in script_txt \\\n""",
     """assert 'FOURTH.ALL_TIP = "Arm or disarm every automatic ability of the selected unit(s)"\\n' in script_txt \\\n"""),
]
ANCHOR = ('      "wanderer; friendly-fire checks only on blasts that hit our units (%d keys); the card xml retired"\n'
          '      % (len(_sent166), _n166))\n')
ADD = ANCHOR + r'''# ROUND 167: no final period; rampage and self-damage abilities start on M (2026-11-17).
import gen_risky_keys as _gr167
_r167 = _gr167.derive(script_txt)
assert ('FOURTH.RISKY_TEXT = "%s"\n' % _gr167.text(_r167)) in script_txt, \
    "BUILD REFUSED (round 167): the RISKY table differs from the game data"
assert "\t\tand not FOURTH.entry_risky(ability)   -- ROUND 167: rampage and self-damage start on M\n" in script_txt, \
    "BUILD REFUSED (round 167): the family default no longer skips the risky entries"
_card167 = script_txt.split("FOURTH.CARD_TIP = {", 1)[1].split("\n}", 1)[0]
assert not re.findall(r'\.",\n', _card167), "BUILD REFUSED (round 167): a card sentence ends with a period"
assert '\treturn table.concat(parts, "; ")   -- ROUND 166' in script_txt and 'parts, "; ") .. "."' not in script_txt, \
    "BUILD REFUSED (round 167): the card ends with a period again"
assert 'selected unit(s)."' not in script_txt, "BUILD REFUSED (round 167): the ALL text ends with a period again"
print("ROUND 167 GATE OK: RISKY (%d keys) matches the game and keeps them on M by default; no final period on the "
      "cards or the ALL text" % len(_r167))
'''
src = open(SRC, encoding="utf-8").read()
for a, b in R:
    assert src.count(a) == 1, (a[:80], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src and "\u2014" not in ADD
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
