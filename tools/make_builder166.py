#!/usr/bin/env python3
"""Build the round-166 build script from the round-165 one (the short cards).

Changes:
  * PACK CONTENTS: ui/common ui/special_ability_tooltip.twui.xml is no longer shipped (the user: remove the static
    'Automatic: click the M/A badge ...' note; the file existed only for that line, and the game's own current layout
    now applies). The pack holds four files; the build REFUSES a pack that carries the xml, and a script that still
    carries the old line.
  * ROUND 166 GATE:
      - every CARD_TIP sentence starts 'Fires' and carries no distance token ({IN_R}, {IN_A}, {CLEAR}, {W1}, {W2} ...);
        the card has no name and no 'on A:';
      - the ALL tooltip is exactly the user's sentence;
      - the wanderer safety loop skips the caster;
      - THE FRIENDLY-FIRE GATE (tools/ff_gate.py, user ruling 2026-11-17 "Vortex with affects_allies=false should have
        no friendly-fire check"): every entry on a family with a fixed friendly-fire check has a blast the game says
        can hit our units (vortex affects_allies, projectile can_damage_allies, explosion affects_allies, bombardment).
No count gate moves (946 entries, 1,003 keys)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_night_audit_harness164\build_and_install165.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_short_cards_harness165\build_and_install166.py"
XML = "ui/common ui/special_ability_tooltip.twui.xml"
R = [
    ("  ui/common ui/special_ability_tooltip.twui.xml    the tooltip's right-click line, filled in\n",
     "  (ROUND 166: ui/common ui/special_ability_tooltip.twui.xml is RETIRED - the game's own card layout ships)\n"),
    ('    (SRC_ROOT + "/ui/common ui/special_ability_tooltip.twui.xml",\n     "ui/common ui/special_ability_tooltip.twui.xml"),\n', ""),
    ('step("3 add the main script and the four ui files",', 'step("3 add the main script and the three ui files",'),
    ('t_raw = bytes(c.send({"GetPackedFileRawData": [key, "ui/common ui/special_ability_tooltip.twui.xml"]})["VecU8"])\n'
     't_txt = t_raw.decode("utf-8", "replace")\n',
     '# ROUND 166: the card xml is retired: nothing to read, and it must not be in the pack\n'
     'assert "%s" not in in_pack_paths, "BUILD REFUSED (round 166): the retired card xml is in the pack"\n'
     't_txt = ""\n' % XML),
    ('print(f"   tooltip hint line present                 : {HINT in t_txt}")\n',
     'print(f"   static card line retired (not in the pack): {HINT not in t_txt and HINT not in script_txt}")\n'),
    ('assert HINT in t_txt, "tooltip hint missing"\n',
     'assert HINT not in t_txt and HINT not in script_txt, "BUILD REFUSED (round 166): the static card line is back"\n'),
]
ANCHOR = ('      "the ground line and the badge card are in place; every range_real has its 70%% bound"\n'
          '      % (len(_u165), len(_t165), len(_used165)))\n')
ADD = ANCHOR + r'''# ROUND 166: the short cards, the short ALL text, the wanderer caster rule, the friendly-fire gate (2026-11-17).
import ff_gate as _ff166
_card166 = script_txt.split("FOURTH.CARD_TIP = {", 1)[1].split("\n}", 1)[0]
_sent166 = re.findall(r'\n\t[a-z_0-9]+ = "([^"]*)",', _card166)
assert len(_sent166) >= 95 and all(x.startswith("Fires") for x in _sent166), \
    "BUILD REFUSED (round 166): a card sentence does not start with 'Fires'"
for _tok166 in ("{IN_R}", "{IN_A}", "{IN_REACH}", "{CLEAR}", "{W1}", "{W2}", "{WPATH}", "{CMIN}", "{DIVE}"):
    assert _tok166 not in _card166, "BUILD REFUSED (round 166): a distance token is back on the card: " + _tok166
assert ' .. " on A: " .. ' not in script_txt and '\treturn table.concat(parts, "; ") .. "."' in script_txt, \
    "BUILD REFUSED (round 166): the card carries the name / 'on A:' again"
assert 'FOURTH.ALL_TIP = "Arm or disarm every automatic ability of the selected unit(s)."\n' in script_txt \
    and "ALL: arm or disarm" not in script_txt, "BUILD REFUSED (round 166): the ALL tooltip is not the user's sentence"
assert "\t\t\tif (oid == nil or oid ~= self_id) and FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n" \
    in script_txt, "BUILD REFUSED (round 166): the wanderer safety loop counts the caster again"
_bad166, _n166 = _ff166.violations(script_txt)
assert not _bad166, "BUILD REFUSED (round 166): a friendly-fire check on a blast that cannot hit our units: %s" % _bad166
print("ROUND 166 GATE OK: %d short card sentences, no distances, no name; the ALL text; the caster never blocks its "
      "wanderer; friendly-fire checks only on blasts that hit our units (%d keys); the card xml retired"
      % (len(_sent166), _n166))
'''
src = open(SRC, encoding="utf-8").read()
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
assert "\u2014" not in ADD
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
