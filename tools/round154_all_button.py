#!/usr/bin/env python3
"""Round 154: the ALL badge becomes the game's own bronze round toggle button (user ruling 2026-11-15, "Game round
button"), with the game's abilities icon, pressed while every ability of the selection is on A, plus Lua Console hooks
to move it in battle (zz_all_nudge / zz_all_set / zz_all_where). Patches the live source and the annotated copy
identically (the annotated copy's all_said logs nothing, so the hooks report through all_said)."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round154"

R = [
    ("FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28   -- ROUND 153: the middle of the cloth (the user's second screenshot)\n"
     "FOURTH.ALL_TIP = \"ALL: arm or disarm every automatic ability of the selected unit(s). If any of them is on M, \"\n"
     "\t.. \"all go to A (automatic); if all are already on A, all go to M (manual).\"\n",
     "-- ROUND 154: the game's round button is 38 x 38 (the text badge was 36 x 24): the same centre, 7 lower. An ESTIMATE:\n"
     "-- the user tunes it in battle with the Lua Console hooks below and the tuned pair replaces this line.\n"
     "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21\n"
     "FOURTH.ALL_TIP = \"ALL: arm or disarm every automatic ability of the selected unit(s). If any of them is on M, \"\n"
     "\t.. \"all go to A (automatic); if all are already on A, all go to M (manual). The button stays pressed while all \"\n"
     "\t.. \"of them are on A.\"\n"
     "-- ROUND 154 (user ruling 2026-11-15, \"Game round button\"): the game's own bronze round toggle button (the camera\n"
     "-- button's family, 38 x 38, ui3.pack) with the game's own abilities icon (the gold fist, ui2.pack); no letters.\n"
     "FOURTH.ALL_TEMPLATE = \"ui/templates/round_small_button_toggle\"\n"
     "FOURTH.ALL_ICON = \"ui/skins/default/icon_abilities.png\"\n"
     "-- the toggle's pressed family of states (the engine moves between them on hover and press by itself)\n"
     "FOURTH.ALL_PRESSED = { selected = true, selected_hover = true, selected_down = true, selected_down_off = true,\n"
     "\tselected_inactive = true }\n"),
    ("\t\t\tst.badge = UIComponent(badge_parent:CreateComponent(FOURTH.ALL_BADGE_ID, \"ui/templates/zz_auto_badge\"))\n"
     "\t\t\tif st.badge == nil then error(\"CreateComponent returned nothing\", 0) end\n"
     "\t\t\tst.badge:SetDockingPoint(0)\n"
     "\t\t\tst.badge:Resize(36, 24)\n"
     "\t\t\tfor i = 0, 4 do st.badge:SetImagePath(\"ui/zz_auto/blank.png\", i) end\n"
     "\t\t\tlocal ok_text = write_badge_letter(st, \"ALL\")\n"
     "\t\t\tif not ok_text then error(\"SetText raised\", 0) end\n",
     "\t\t\tst.badge = UIComponent(badge_parent:CreateComponent(FOURTH.ALL_BADGE_ID, FOURTH.ALL_TEMPLATE))\n"
     "\t\t\tif st.badge == nil then error(\"CreateComponent returned nothing\", 0) end\n"
     "\t\t\tst.badge:SetDockingPoint(0)\n"
     "\t\t\tst.badge:SetImagePath(FOURTH.ALL_ICON, 0)   -- ROUND 154: image 0 is the button's icon\n"),
    ("\t\tFOURTH.all_said(\"ALL badge: created left of the wheel\")\n"
     "\tend\n"
     "\tif st.shown ~= any then\n"
     "\t\tst.shown = any\n"
     "\t\tpcall(function() st.badge:SetVisible(any) end)\n"
     "\tend\n"
     "end\n",
     "\t\tFOURTH.all_said(\"ALL badge: created left of the wheel\")\n"
     "\tend\n"
     "\tif st.shown ~= any then\n"
     "\t\tst.shown = any\n"
     "\t\tpcall(function() st.badge:SetVisible(any) end)\n"
     "\tend\n"
     "\tif any then FOURTH.all_sync_pressed(st) end\n"
     "end\n"
     "\n"
     "-- ROUND 154: the button looks pressed exactly while every ability of ours the selection owns is armed. Only a\n"
     "-- WRONG family is corrected, so the engine's own hover and press looks are left alone.\n"
     "function FOURTH.all_armed_now()\n"
     "\tlocal targets, n = FOURTH.all_targets(), 0\n"
     "\tfor i = 1, #targets do\n"
     "\t\tfor _, entry in ipairs(owned_abilities_by_unit[tostring(targets[i])] or {}) do\n"
     "\t\t\tn = n + 1\n"
     "\t\t\tif not FOURTH.armed_slot(unit_slot(targets[i]), entry.marker) then return false end\n"
     "\t\tend\n"
     "\tend\n"
     "\treturn n > 0\n"
     "end\n"
     "\n"
     "function FOURTH.all_sync_pressed(st)\n"
     "\tlocal want = FOURTH.all_armed_now()\n"
     "\tlocal ok, cur = pcall(function() return st.badge:CurrentState() end)\n"
     "\tif not ok then return end\n"
     "\tif want ~= (FOURTH.ALL_PRESSED[tostring(cur)] == true) then\n"
     "\t\tpcall(function() st.badge:SetState(want and \"selected\" or \"active\") end)\n"
     "\tend\n"
     "end\n"
     "\n"
     "-- ROUND 154: in-battle tuning of the ALL button from the Lua Console (Shift+F3; the Modding Development Tools: Lua\n"
     "-- Console mod), like the ability badges' zz_badge_nudge. Each call moves it at once and reports \"ALL POS x,y\".\n"
     "--   zz_all_nudge(dx, dy)   move by dx right, dy down (negative = left / up)\n"
     "--   zz_all_set(x, y)       put it at x,y\n"
     "--   zz_all_where()         report where it is\n"
     "function zz_all_set(x, y)\n"
     "\tFOURTH.ALL_OX, FOURTH.ALL_OY = tonumber(x) or FOURTH.ALL_OX, tonumber(y) or FOURTH.ALL_OY\n"
     "\tlocal st = FOURTH.all_state\n"
     "\tif st.badge ~= nil then pcall(function() st.badge:SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY) end) end\n"
     "\tlocal m = \"ALL POS \" .. tostring(FOURTH.ALL_OX) .. \",\" .. tostring(FOURTH.ALL_OY)\n"
     "\tFOURTH.all_said(m)\n"
     "\treturn m\n"
     "end\n"
     "\n"
     "function zz_all_nudge(dx, dy)\n"
     "\treturn zz_all_set(FOURTH.ALL_OX + (tonumber(dx) or 0), FOURTH.ALL_OY + (tonumber(dy) or 0))\n"
     "end\n"
     "\n"
     "function zz_all_where()\n"
     "\treturn zz_all_set(FOURTH.ALL_OX, FOURTH.ALL_OY)\n"
     "end\n"),
]

os.makedirs(BK, exist_ok=True)
for path, tag in ((LIVE, "live"), (ANN, "ann")):
    bk = os.path.join(BK, "pre154_" + tag + ".lua")
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    s = open(bk, encoding="utf-8", newline="").read()
    for a, b in R:
        assert s.count(a) == 1, (tag, a[:80], s.count(a))
        s = s.replace(a, b)
    assert "\u2014" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(tag, "patched", len(s))
