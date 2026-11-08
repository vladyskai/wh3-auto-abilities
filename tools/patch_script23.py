"""Round 23: the control is now a double-click on the unit card (the engine reports it to script).

Removes the dead right-click machinery (the property channel is measured dead: every read echoed
its own name, including icon_index which vanilla declares with a value) and installs the handler
for the engine's documented 'Double Click Unit Card' command.
"""
import re
from pathlib import Path

p = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
s = p.read_text(encoding="utf-8", errors="replace")
orig = s
report = []

def sub(pat, repl, why, count=1, flags=re.S):
    global s
    new, n = re.subn(pat, repl, s, count=count, flags=flags)
    assert n == count, f"FAILED ({n}/{count}): {why}"
    s = new
    report.append(f"   ok  {why}")

# ---- 1. the state: track WHICH unit we manage, so only its card toggles
sub(r"local target_key_by_unit = \{\}",
    "local target_key_by_unit = {}\nlocal our_unit_ui_id = nil      -- the ui id of the unit whose ability we manage",
    "track our_unit_ui_id")

sub(r"(\t\tif matching_key ~= nil then\n\t\t\tcarriers = carriers \+ 1\n\t\tend)",
    r"\1\n\t\tif matching_key ~= nil and our_unit_ui_id == nil then\n\t\t\tour_unit_ui_id = ui_id\n\t\tend",
    "record our_unit_ui_id when the carrier is found")

# ---- 2. drop the dead right-click locals
sub(r"local RCLICK_PREFIX = \"zz_auto_rclick\"\nlocal RCLICK_PROPERTY = \"zz_rclick\"\n"
    r"local LCLICK_PROPERTY = \"zz_lclick\".*\nlocal last_rclick = nil\nlocal last_lclick = nil\n",
    "-- The switch is flipped by a double-click on the unit card - the engine's own\n"
    "-- 'Double Click Unit Card' command, which it reports to script (round 22 proved the command\n"
    "-- channel works; the layout-property channel is dead, every read echoes its own name).\n",
    "right-click constants removed")

sub(r"local seen_rclick_names = \{\}\nlocal seen_ctx_events = \{\}\n", "", "seen_* tables removed")

sub(r"local function is_toggle_event\(name\).*?\nend\n\n", "", "is_toggle_event removed")

sub(r"local function check_rclick_property\(\).*?\nend\n\n\n",
    "", "check_rclick_property removed")

# ---- 3. the discovery block: keep key + id + chain, drop the property reads
sub(r"\t\t\t-- Three property reads, and together they answer everything:.*?tostring\(ok_r and ok_l and ok_i\) \.\. \"\)\"\)\n",
    "\t\t\t-- (Round 22: the property reads that used to live here are gone - every read echoed the\n"
    "\t\t\t-- property's own name, including icon_index which vanilla declares with a value, so script\n"
    "\t\t\t-- cannot observe what a layout sets. The chain above is what identified the button.)\n",
    "discovery property reads removed")

# ---- 4. replace the two dead listeners with the double-click handler
sub(r"-- \(1\) the direct script event, in case declaring rclick is what makes the engine raise it\n"
    r"core:add_listener\(.*?\n\)\n\n-- \(2\) the layout broadcast, if it surfaces to script as a context event\n"
    r"core:add_listener\(.*?\n\)\n",
    """-- (1) THE CONTROL: double-click the unit card.
-- battle.lua's command list, verbatim: "Double Click Unit Card - A unit card has been
-- double-clicked upon - get_unit() returns the subject unit". This is the engine reporting a
-- mouse gesture to script, on the one channel that is proven to work (round 22's log showed
-- 'Special Ability' arriving the same way). No layout, no property, nothing drawn: the engine
-- tells us, we flip the switch - and the pulse on the ability icon is the feedback.
bm:register_command_handler_callback("Double Click Unit Card", function(context)
\tlocal ok_u, unit = pcall(function() return context:get_unit() end)
\tif not ok_u or unit == nil then
\t\tlog("double-click on a unit card: the engine sent no unit with it")
\t\treturn
\tend

\tlocal ok_id, ui_id = pcall(function() return unit:unique_ui_id() end)
\tif not ok_id then ui_id = nil end

\tif our_unit_ui_id == nil then
\t\tlog("double-click on a unit card (ui id " .. tostring(ui_id) .. ") - we have no ability "
\t\t\t.. "carrier yet, so nothing to toggle")
\t\treturn
\tend

\tif tostring(ui_id) ~= tostring(our_unit_ui_id) then
\t\tlog("double-click on a unit card (ui id " .. tostring(ui_id) .. ") - not the carrier of "
\t\t\t.. "Deadly Onslaught (ui id " .. tostring(our_unit_ui_id) .. "), nothing to toggle")
\t\treturn
\tend

\tset_auto(not AUTO_ENABLED, "double-click on the unit card")
end, "zz_deadly_onslaught_card_doubleclick")
""",
    "right-click listeners -> double-click command handler")

# ---- 5. the ui tick must no longer poll a property
sub(r"\n\n\t-- the right-click itself: a UI call, so this is the right clock for it\n\tcheck_rclick_property\(\)",
    "", "ui tick: property poll call removed")

# ---- 6. the tooltip hint should describe the gesture that now works
assert s != orig, "nothing changed?!"
p.write_text(s, encoding="utf-8", newline="")

for line in report:
    print(line)

for token in ("check_rclick_property", "RCLICK_PROPERTY", "zz_rclick", "ComponentRClickUp",
              "ContextTriggerEvent", "seen_rclick_names", "is_toggle_event"):
    n = s.count(token)
    print(f"   leftover '{token}': {n}" + ("   <-- must be 0" if n else ""))
print(f"   Double Click Unit Card handler: {s.count('Double Click Unit Card')} (want 1)")
print(f"   lines now: {len(s.splitlines())} (was {len(orig.splitlines())})")
