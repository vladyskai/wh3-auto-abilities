"""Round 24: the right-click, on the documented route (AddScriptEventReporter).

The wiki's UI tutorial (UI:Main Page) says it plainly: UIComponents only fire *some* events by
default (ComponentLClickUp); "there are more detailed events which are not fired by most
UIComponents by default" and AddScriptEventReporter() "cause[s] it to begin firing all events".
Vanilla uses it exactly that way in lib_movie_overlay.lua ("set the panel to report all script
events") and then listens for ComponentAnimationFinished. script/events.lua lists ComponentRClickUp
right next to ComponentLClickUp, so the event exists - it was simply never being reported for the
ability button. Rounds 15-21 listened for it without ever asking the engine to report it.

Also: AUTO_ENABLED goes back to false (the switch exists again), and the battle-start flash only
happens when auto is on.
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

# --- 1. the switch is switchable again: off by default, as asked (declaration already deduped)
assert s.count("local AUTO_ENABLED") == 1, "expected exactly one AUTO_ENABLED declaration"
rep("local AUTO_ENABLED = false", "local AUTO_ENABLED = false", "AUTO_ENABLED stays false")

# --- 2. the flash only makes sense when auto starts ON
rep("\t\t\tapply_ability_feedback()\n\t\t\tarm_flash = 6",
    "\t\t\tapply_ability_feedback()\n\t\t\tif AUTO_ENABLED then arm_flash = 6 end",
    "arm flash only when auto starts ON")

# --- 3. remember the button's id, and ASK THE ENGINE TO REPORT ITS EVENTS
rep("local our_button = nil          -- the component itself, for the feedback",
    "local our_button = nil          -- the component itself, for the feedback\n"
    "local our_button_id = nil       -- its component id, for matching the script events",
    "our_button_id declared")

rep("\t\tour_button = uic\n\t\t\tlog(\"   ^ that one is ours\")",
    "\t\tour_button = uic\n"
    "\t\t\tlocal ok_i2, id2 = pcall(function() return uic:Id() end)\n"
    "\t\t\tif ok_i2 then our_button_id = tostring(id2) end\n"
    "\t\t\tlog(\"   ^ that one is ours\")\n"
    "\n"
    "\t\t\t-- ASK THE ENGINE TO REPORT ITS EVENTS. Without this the component only emits the\n"
    "\t\t\t-- default ones (ComponentLClickUp); with it, all of them - which is the documented\n"
    "\t\t\t-- way to hear the mouse events (wiki UI:Main Page, and vanilla's own use of it in\n"
    "\t\t\t-- _lib/lib_movie_overlay.lua: \"set the panel to report all script events\").\n"
    "\t\t\tlocal ok_r, err_r = pcall(function() uic:AddScriptEventReporter() end)\n"
    "\t\t\tlog(\"   AddScriptEventReporter() ok=\" .. tostring(ok_r)\n"
    "\t\t\t\t.. (ok_r and \"\" or (\" error=\" .. tostring(err_r))))",
    "call AddScriptEventReporter on discovery")

# --- 4. the two listeners: the right-click (the toggle) and the left-click (the control)
rep('''-- (1) THE CONTROL: double-click the unit card.''',
    '''-- (1) THE EVENT THAT MATTERS: a right-click on the ability icon, now that the component
-- reports its events. script/events.lua declares ComponentRClickUp; this is the first time we are
-- actually asking for it. Matched by component id and by address, so whichever the context fills in
-- one of them will agree.
core:add_listener(
\t"zz_deadly_onslaught_rclick",
\t"ComponentRClickUp",
\tfunction(context)
\t\tif our_button == nil then return false end
\t\tif our_button_id ~= nil and context.string == our_button_id then return true end
\t\tlocal ok_a, addr = pcall(function() return our_button:Address() end)
\t\treturn ok_a and addr ~= nil and context.component == addr
\tend,
\tfunction(context)
\t\tlog("RCLICK: the engine reported a right-click on the ability icon ('"
\t\t\t.. tostring(context.string) .. "')")
\t\tset_auto(not AUTO_ENABLED, "right-click on the ability icon")
\tend,
\ttrue
)

-- (2) THE CONTROL: a left-click on the same icon, which happens whenever the ability is used -
-- so this one is seen without the player doing anything special. If this reports and the
-- right-click does not, the reporter works and the engine simply never raises the right-click.
core:add_listener(
\t"zz_deadly_onslaught_lclick_control",
\t"ComponentLClickUp",
\tfunction(context)
\t\tif our_button == nil then return false end
\t\tif our_button_id ~= nil and context.string == our_button_id then return true end
\t\tlocal ok_a, addr = pcall(function() return our_button:Address() end)
\t\treturn ok_a and addr ~= nil and context.component == addr
\tend,
\tfunction(context)
\t\tlog("CONTROL: left-click reported on the ability icon ('" .. tostring(context.string)
\t\t\t.. "') - the engine's event reporter is working")
\tend,
\ttrue
)

-- (3) THE SPARE: double-click the unit card.''',
    "rclick + lclick listeners installed")

p.write_text(s, encoding="utf-8", newline="")
for r in report:
    print(r)
for t in ("AddScriptEventReporter", "ComponentRClickUp", "our_button_id", "auto activation starts"):
    print(f"   {t}: {s.count(t)}")
print("   AUTO_ENABLED:", [l.strip() for l in s.splitlines() if l.startswith("local AUTO_ENABLED")][0])
