#!/usr/bin/env python3
"""Build harness165.lua from harness164.lua for round 166 (the short cards). Older harnesses are never edited.

Rebases (each one a text the user asked to change on 2026-11-17):
  * harness 152 AP2a and harness 153 BT1a (the ALL badge's tooltip): they looked for 'ALL: arm or disarm' and 'The button
    stays pressed while all of them are on A.'; the tooltip is now only 'Arm or disarm every automatic ability of the
    selected unit(s).' (the user's marked-up screenshot). Both now look for that sentence.
  * harness 164 CD1 (every card whole): the card began '<name> on A: '; it now begins 'Fires ' (no name, no 'on A:').
  * harness 164 CD2 (the exact long cards): the same twelve abilities, pinned on their short cards.
  * harness 164 CARD print: removed (harness 165 SC prints the cards; one copy per run).
  * harness 93 D4a/D4b (the shipped twui.xml carried the static line): the file is retired (the user: remove the
    'Automatic: click the M/A badge ...' note); D4a now pins that the source file is gone, D4b that no copy carries
    the old sentence.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_night_audit_harness164\harness164.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_short_cards_harness165\harness165.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h165_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 165 - ROUND 166: THE SHORT CARDS (the card on every M/A badge in a
--   few words, the short ALL tooltip, the static card line retired, the caster
--   never blocks its own wanderer).
--   Edited vs harness164: this banner, the rebases listed in tools/make_harness165.py
--   (AP2a, BT1a, CD1, CD2, the CARD print, D4a/D4b), run_h165 and its call.
--   RED control: H165_LIVE / H165_ANN on docs/backups/round166/pre166_*.lua.
-- ============================================================================
"""
NEW_ALL = "Arm or disarm every automatic ability of the selected unit(s)."
R = [
    ('            and raw_find(rec.tooltip, "ALL: arm or disarm", 1, true) ~= nil)\n',
     '            and raw_find(rec.tooltip, "%s", 1, true) ~= nil)   -- HARNESS 165: the short ALL text\n' % NEW_ALL),
    ('          and raw_find(rec.tooltip, "The button stays pressed while all of them are on A.", 1, true) ~= nil)\n',
     '          and raw_find(rec.tooltip, "%s", 1, true) ~= nil)   -- HARNESS 165: the short ALL text\n' % NEW_ALL),
    ('        local ok = type(c) == "string" and c:sub(1, #tostring(e.name) + 7) == tostring(e.name) .. " on A: "\n',
     '        local ok = type(c) == "string" and c:sub(1, 6) == "Fires "   -- HARNESS 165: no name, no \'on A:\'\n'),
    ('        if TAG == "[live] " and not RED164 then print("CARD " .. tostring(e.marker) .. ": " .. tostring(c)) end\n',
     ''),
    ('      local exact = by.deadly_onslaught == "Deadly Onslaught on A: fires when this unit runs at the enemy it is "\n'
     '          .. "attacking, 12 to 60 m away and at most 4 s from contact, or when it is in melee."\n'
     '        and by.entice == "Entice on A: fires when this unit is in melee and not wavering; not below 50% health."\n'
     '        and by.bloodbeast == "Bloodbeast on A: fires when this unit is in melee and not wavering, with none of your "\n'
     '          .. "other units within 25 m of it."\n'
     '        and has("helping_hand", "; the ally must be a Lord or Hero.")\n'
     '        and has("eye_of_the_storm", "; only when this unit is a large unit.")\n'
     '        and has("curse_of_djaf", "; only at or below 50% health.")\n'
     '        and has("unholy_clamour", "or a friendly unit anywhere on the field, is wavering")\n'
     '        and has("sunfang", ", with none of your other units within 22 m of the path.")\n'
     '        and has("wrath_of_manann", "within 16 m of the path at its start, widening to 33 m at its end")\n'
     '        and has("emberstorm", "none of your other units within 20 m.")\n'
     '        and not has("eye_of_khorne", "the ally must")\n'
     '        and has("blue_fire", "; not while this unit is in melee.")\n',
     '      -- HARNESS 165: the same twelve abilities on their short cards\n'
     '      local exact = by.deadly_onslaught == "Fires when charging or in melee."\n'
     '        and by.entice == "Fires in melee unless wavering; not below 50% health."\n'
     '        and by.bloodbeast == "Fires in melee unless wavering, clear of allies."\n'
     '        and has("helping_hand", "; Lord or Hero allies only.")\n'
     '        and has("eye_of_the_storm", "; only in large form.")\n'
     '        and has("curse_of_djaf", "; only at 50% health or less.")\n'
     '        and has("unholy_clamour", "Fires when it or any ally wavers.")\n'
     '        and has("sunfang", "down the path with the most enemies, clear of allies.")\n'
     '        and has("wrath_of_manann", "down the path with the most enemies, clear of allies")\n'
     '        and has("emberstorm", "Fires while flying over an enemy, clear of allies.")\n'
     '        and not has("eye_of_khorne", "allies only")\n'
     '        and has("blue_fire", "; not in melee.")\n'),
    ('  local twui_src   = read_file(TWUI_PATH)\n',
     '  -- HARNESS 165: the twui.xml is retired (round 166); a missing file reads as empty\n'
     '  local twui_f     = io.open(TWUI_PATH, "r")\n'
     '  local twui_src   = twui_f and twui_f:read("*a") or ""\n'
     '  if twui_f then twui_f:close() end\n'),
    ('  check("D4a: the twui.xml carries the NEW short line", raw_find(twui_src, NEW_LINE, 1, true) ~= nil)\n',
     '  check("D4a: the twui.xml is retired: no source file, no static card line (HARNESS 165)", twui_f == nil\n'
     '    and raw_find(twui_src, NEW_LINE, 1, true) == nil)\n'),
]
src = open(SRC, encoding="utf-8").read()
for a, b in R:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h164()\n") == 1
src = src.replace("\nrun_h164()\n", "\nrun_h164()\nrun_h165()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
