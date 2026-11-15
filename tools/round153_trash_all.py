#!/usr/bin/env python3
"""Round 153 (harness 152): field rulings 2026-11-15 after the round-152 battle.

  * TRASH (user: "ignore trash units ... Unless there is a big blob"; "Value below 2"; "3 packed blocks"): a blob
    attack never takes an infantry target whose live value per soldier is below TRASH_VPS = 2 (the bottom 4% of
    infantry: Zombies, Skavenslaves, The Tithe, Skeletons, Clanrats), unless its blast covers at least
    TRASH_BLOB_LINES = 3 x the density line. An unreadable value is not treated as trash.
  * the ALL badge stays visible while ANY selected unit owns any ability of ours (it used to hide when the selected
    units shared no ability, because it followed the ability badges);
  * the ALL badge moves to the middle of the cloth under the portrait (the user's screenshot): offset (-855, -28);
  * a hover tooltip on the ALL badge (SetTooltipText, pcall'd: a template without tooltip support just shows none).
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def sub(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a))
    return s.replace(a, b)


BAND_OLD = 'FOURTH.BREATH_VALUE_BAND = 0.8   -- user ruling 2026-11-14: "within 20% of the best value"\n'
BAND_NEW = BAND_OLD + ('-- ROUND 153 (user rulings 2026-11-15: "ignore trash units ... Unless there is a big blob", "Value below 2",\n'
                       '-- "3 packed blocks"): a target worth less than TRASH_VPS per soldier (live value) is taken only when the\n'
                       '-- blast covers at least TRASH_BLOCKS packed blocks: 3 x (the blast area / PACKED_M2), about 100 soldiers\n'
                       '-- in a 5 m blast (the density line is HALF a packed block). An unreadable value is not trash.\n'
                       'FOURTH.TRASH_VPS = 2\n'
                       'FOURTH.TRASH_BLOCKS = 3\n'
                       'function FOURTH.blob_trash_ok(e, sc, r)\n'
                       '\tif e.vps == nil or e.vps >= FOURTH.TRASH_VPS then return true end\n'
                       '\treturn sc >= FOURTH.TRASH_BLOCKS * math.pi * r * r / FOURTH.PACKED_M2\n'
                       'end\n')
PICK_OLD = "\t\t\t\tif sc >= need then\n\t\t\t\t\tlocal v = FOURTH.blob_value(e, m, r, dmg)\n"
PICK_NEW = ("\t\t\t\tif sc >= need and FOURTH.blob_trash_ok(e, sc, r) then   -- ROUND 153: no trash unless a big blob\n"
            "\t\t\t\t\tlocal v = FOURTH.blob_value(e, m, r, dmg)\n")
RECHK_OLD = "\t\t\tlocal sc = FOURTH.blob_score(e, m, r)\n\t\t\treturn sc >= FOURTH.blob_need(r)\n"
RECHK_NEW = ("\t\t\tlocal sc = FOURTH.blob_score(e, m, r)\n"
             "\t\t\treturn sc >= FOURTH.blob_need(r) and FOURTH.blob_trash_ok(e, sc, r)   -- ROUND 153\n")

POS_OLD = "FOURTH.ALL_OX, FOURTH.ALL_OY = -880, 8\n"
POS_NEW = ("FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28   -- ROUND 153: the middle of the cloth (the user's second screenshot)\n"
           "FOURTH.ALL_TIP = \"ALL: arm or disarm every automatic ability of the selected unit(s). If any of them is on M, \"\n"
           "\t.. \"all go to A (automatic); if all are already on A, all go to M (manual).\"\n")
ANY_OLD = ('\tlocal any = false\n'
           '\tfor _, ability in ipairs(active_abilities_list()) do\n'
           '\t\tlocal s = ability_state[ability.marker]\n'
           '\t\tif s ~= nil and s.badge_shown == true then\n'
           '\t\t\tany = true\n'
           '\t\t\tbreak\n'
           '\t\tend\n'
           '\tend\n')
ANY_NEW = ('\t-- ROUND 153: shown while ANY selected unit owns any ability of ours (not only when ability badges show: two\n'
           '\t-- selected units with no shared ability show no ability badge, but ALL must stay)\n'
           '\tlocal any = FOURTH.all_selection_has_ours()\n')
TEXT_OLD = ('\t\t\tlocal ok_text = write_badge_letter(st, "ALL")\n'
            '\t\t\tif not ok_text then error("SetText raised", 0) end\n')
TEXT_NEW = TEXT_OLD + ('\t\t\t-- ROUND 153: the hover tooltip (a template without tooltip support simply shows none)\n'
                       '\t\t\tpcall(function() st.badge:SetTooltipText(FOURTH.ALL_TIP, true) end)\n')
CLICK_OLD = ('function FOURTH.all_click()\n'
             '\tlocal targets = {}\n'
             '\tfor i = 1, #selected_ui_ids do\n'
             '\t\tif selected_ui_ids[i] ~= nil then targets[#targets + 1] = selected_ui_ids[i] end\n'
             '\tend\n'
             '\tif #targets == 0 then\n'
             '\t\tif selection_callback_alive or selected_unit_id == nil then\n'
             '\t\t\tFOURTH.all_said("ALL click ignored: no unit selected")\n'
             '\t\t\treturn\n'
             '\t\tend\n'
             '\t\ttargets[1] = selected_unit_id\n'
             '\tend\n')
CLICK_NEW = ('-- ROUND 153: the selected units the ALL badge acts on (the engine\'s selection; the tracker only when the selection\n'
             '-- callback is not in charge), and whether any of them owns an ability of ours\n'
             'function FOURTH.all_targets()\n'
             '\tlocal targets = {}\n'
             '\tfor i = 1, #selected_ui_ids do\n'
             '\t\tif selected_ui_ids[i] ~= nil then targets[#targets + 1] = selected_ui_ids[i] end\n'
             '\tend\n'
             '\tif #targets == 0 and not selection_callback_alive and selected_unit_id ~= nil then\n'
             '\t\ttargets[1] = selected_unit_id\n'
             '\tend\n'
             '\treturn targets\n'
             'end\n\n'
             'function FOURTH.all_selection_has_ours()\n'
             '\tlocal targets = FOURTH.all_targets()\n'
             '\tfor i = 1, #targets do\n'
             '\t\tlocal list = owned_abilities_by_unit[tostring(targets[i])]\n'
             '\t\tif list ~= nil and #list > 0 then return true end\n'
             '\tend\n'
             '\treturn false\n'
             'end\n\n'
             'function FOURTH.all_click()\n'
             '\tlocal targets = FOURTH.all_targets()\n'
             '\tif #targets == 0 then\n'
             '\t\tFOURTH.all_said("ALL click ignored: no unit selected")\n'
             '\t\treturn\n'
             '\tend\n')

for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert "TRASH_VPS" not in s
    s = sub(s, BAND_OLD, BAND_NEW)
    s = sub(s, PICK_OLD, PICK_NEW)
    s = sub(s, RECHK_OLD, RECHK_NEW)
    s = sub(s, POS_OLD, POS_NEW)
    s = sub(s, ANY_OLD, ANY_NEW)
    s = sub(s, TEXT_OLD, TEXT_NEW)
    s = sub(s, CLICK_OLD, CLICK_NEW)
    assert "string.find" not in BAND_NEW + ANY_NEW + CLICK_NEW + TEXT_NEW
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)
