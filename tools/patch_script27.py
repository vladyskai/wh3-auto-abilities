"""Round 27: a keyboard toggle with a static icon change.

Channel: ShortcutTriggered / ShortcutPressed (proven live in round 26's firehose: they fired with
string=step_r / step_l / step_bck / step_fwd). Keyboard input is the one player input this game
delivers to script, and no vanilla script listens to either event, so nothing is being hijacked.

Feedback: the ability icon itself is repainted - static, no pulse/blink. Two paths, both vanilla:
the icon the button is already using is read off the component, and the armed look is another
ability icon whose path the game itself returned in round 26's component dump
(ui/battle ui/ability_icons/wh_main_spell_lil_waaagh_itchy_nuisance.png), so it is guaranteed to
resolve without shipping any asset.
"""
from pathlib import Path

p = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
s = p.read_text(encoding="utf-8", errors="replace")
report = []

def rep(old, new, why, n=1):
    global s
    assert s.count(old) == n, f"anchor {n}x expected, found {s.count(old)}: {why}"
    s = s.replace(old, new)
    report.append("ok  " + why)

# --- 1. the switch is turned OFF at start so the swap is visible when it happens
rep("local AUTO_ENABLED = true          -- <- the switch itself: ON. Round 26 subscribed to all 399",
    "local AUTO_ENABLED = false         -- <- the switch itself: OFF, so the keyboard test shows the\n"
    "                                   --    change (press the key -> armed -> the icon repaints)",
    "AUTO_ENABLED starts false for the test")

# --- 2. the icon swap replaces the pulse as the only feedback (static, no blinking)
rep("""-- Engine-rendered feedback, on the ability icon itself: the game's own pulse
-- highlight (the one the advice system uses), running while automatic mode is
-- armed. No custom image, no created component, nothing to paint.""",
    """-- THE FEEDBACK: a plain image swap on the ability icon. Static - no pulse, no blink.
-- The icon slot is the one the vanilla layout marks with icon_index = 8 (round 21's layout read).
-- Both paths are read off / given by the game, so nothing has to resolve a guessed skin path.
local ICON_INDEX = 8
local ARMED_ICON = "ui\\\\battle ui\\\\ability_icons\\\\wh_main_spell_lil_waaagh_itchy_nuisance.png"
local original_icon = nil          -- whatever the button was showing before we touched it

local function read_icon()
\tif our_button == nil then return nil end
\tlocal ok, path = pcall(function() return our_button:GetImagePath(ICON_INDEX) end)
\tif ok then return tostring(path) end
\treturn nil
end

local function set_armed_look(on)
\tif our_button == nil then return end
\tlocal target = on and ARMED_ICON or original_icon
\tif target == nil then
\t\tlog("icon swap skipped: we never read the original icon")
\t\treturn
\tend
\tlocal ok_s, err_s = pcall(function() our_button:SetImagePath(target, ICON_INDEX) end)
\tlocal back = read_icon()
\tlog("icon swap -> " .. (on and "ARMED look" or "original") .. " ok=" .. tostring(ok_s)
\t\t.. (ok_s and "" or (" error=" .. tostring(err_s))))
\tlog("   wanted: " .. tostring(target))
\tlog("   engine now reports: " .. tostring(back)
\t\t.. (tostring(back) == tostring(target) and "  (MATCHES)" or "  (does NOT match)"))
end""",
    "icon-swap feedback replaces the pulse")

rep("""\tlocal ok, err = pcall(function()
\t\tif AUTO_ENABLED then
\t\t\tour_button:StartPulseHighlight(80, nil)
\t\telse
\t\t\tour_button:StopPulseHighlight(nil)
\t\tend
\tend)

\tfeedback_on = AUTO_ENABLED
\tlog("ability icon feedback: " .. (AUTO_ENABLED and "pulsing (auto ON)" or "stopped (auto OFF)")
\t\t.. " ok=" .. tostring(ok) .. (ok and "" or (" error=" .. tostring(err))))""",
    "\tset_armed_look(AUTO_ENABLED)\n\tfeedback_on = AUTO_ENABLED",
    "apply_ability_feedback now does the swap")

# --- 3. no battle-start flash: the user asked for static icons
rep("""\t\t\tapply_ability_feedback()
\t\t\tif AUTO_ENABLED then arm_flash = 6 end""",
    """\t\t\toriginal_icon = read_icon()
\t\t\tlog("icon slot " .. tostring(ICON_INDEX) .. " currently shows: " .. tostring(original_icon))
\t\t\tapply_ability_feedback()""",
    "read the original icon instead of flashing")

rep("""\t-- end the \"automatic mode is live\" flash after ~3 s
\tif arm_flash ~= nil then
\t\tarm_flash = arm_flash - 1
\t\tif arm_flash <= 0 then
\t\t\tarm_flash = nil
\t\t\tlocal ok_s, err_s = pcall(function() our_button:StopPulseHighlight(nil) end)
\t\t\tlog(\"arm flash done - the ability icon is back to normal (ok=\" .. tostring(ok_s)
\t\t\t\t.. (ok_s and \"\" or (\" error=\" .. tostring(err_s))) .. \")\")
\t\tend
\tend
""", "", "flash block removed")

rep("local arm_flash = nil           -- ticks left of the \"auto is on\" flash at battle start\n", "",
    "arm_flash declaration removed")

# --- 4. the keyboard listeners
rep("-- (2) THE CONTROL: a left-click on the same icon",
    '''-- (2) THE KEYBOARD. Round 26's firehose proved these two events fire in battle and carry the
-- shortcut's name (string=step_r, step_l, step_bck, step_fwd); no vanilla script uses either, so
-- nothing is being hijacked. The camera-step keys are ignored - they fire while the player pans and
-- would toggle the switch by accident. Any other shortcut flips it, and the log names it, so we can
-- pin the exact key afterwards.
local shortcut_seen = 0

local function on_shortcut(event_name, context)
\tlocal name = tostring(context.string)
\tif string.sub(name, 1, 5) == "step_" then return end        -- camera nudges: ignore
\tshortcut_seen = shortcut_seen + 1
\tif shortcut_seen <= 60 then
\t\tlog("KEY " .. event_name .. " -> '" .. name .. "'")
\tend
\tset_auto(not AUTO_ENABLED, "keyboard shortcut '" .. name .. "'")
end

core:add_listener("zz_deadly_onslaught_shortcut", "ShortcutTriggered",
\tfunction(context) return true end,
\tfunction(context) on_shortcut("ShortcutTriggered", context) end, true)

core:add_listener("zz_deadly_onslaught_shortcut_pressed", "ShortcutPressed",
\tfunction(context) return true end,
\tfunction(context) on_shortcut("ShortcutPressed", context) end, true)

-- (3) THE CONTROL: a left-click on the same icon''',
    "keyboard listeners added")

# --- 5. log line wording (auto starts OFF now, and the hint lives in the tooltip)
rep('.. " | automatic activation starts " .. (AUTO_ENABLED and "ON" or "OFF"))',
    '.. " | automatic activation starts " .. (AUTO_ENABLED and "ON" or "OFF")\n'
    '\t.. " | press any shortcut key (not the arrow/step keys) to flip it")',
    "startup line mentions the key")

p.write_text(s, encoding="utf-8", newline="")
for r in report:
    print(r)
for tok in ("StartPulseHighlight", "arm_flash", "SetImagePath", "ShortcutTriggered", "ShortcutPressed"):
    print(f"   {tok}: {s.count(tok)}")
