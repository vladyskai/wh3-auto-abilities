"""Round 25: the diagnostic that cannot be inconclusive.

Round 24 proved the reporter call works but the battle contained no left-click on the ability, so
"no event" could mean either "battle components report nothing" or "this button's click is consumed".

Now:
  * AddScriptEventReporter() goes on the ability button AND its whole ancestor chain (a click may be
    attributed to a parent container - button_parent, SA_dial, ... - not to the button itself);
  * both click listeners are UNFILTERED but labelled: every event is logged with the component name
    and whether it belongs to our chain, capped so hovering/clicking elsewhere cannot flood the log;
  * the toggle fires for our button or any component in that chain, so the log tells us which
    component the engine attributes the right-click to.
"""
import re
from pathlib import Path

p = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
s = p.read_text(encoding="utf-8", errors="replace")
report = []

def rep(old, new, why, n=1):
    global s
    assert s.count(old) == n, f"anchor {n}x expected, found {s.count(old)}: {why}"
    s = s.replace(old, new)
    report.append("ok  " + why)

# --- 1. the chain table + the reporter walk
rep('local our_button_id = nil       -- its component id, for matching the script events',
    'local our_button_id = nil       -- its component id, for matching the script events\n'
    'local watch_chain = {}          -- the ability button and its ancestors, all reporting events',
    "watch_chain declared")

rep('''\t\t\tlocal ok_r, err_r = pcall(function() uic:AddScriptEventReporter() end)
\t\t\tlog("   AddScriptEventReporter() ok=" .. tostring(ok_r)
\t\t\t\t.. (ok_r and "" or (" error=" .. tostring(err_r))))''',
    '''\t\t\t-- ...and on every ancestor up to the HUD: a click may be attributed to a container
\t\t\t-- (button_parent, SA_dial, ...) rather than to the button itself, and a component only
\t\t\t-- reports what it has been asked to report.
\t\t\twatch_chain = {}
\t\t\tlocal node = uic
\t\t\tfor _ = 1, 7 do
\t\t\t\tif node == nil then break end
\t\t\t\tlocal ok_r, err_r = pcall(function() node:AddScriptEventReporter() end)
\t\t\t\tlocal ok_a, addr = pcall(function() return node:Address() end)
\t\t\t\tlocal ok_i, id = pcall(function() return node:Id() end)
\t\t\t\twatch_chain[#watch_chain + 1] = { addr = (ok_a and addr or nil),
\t\t\t\t\tid = (ok_i and tostring(id) or nil) }
\t\t\t\tlog("   event reporter on '" .. tostring(ok_i and id or "?") .. "' ok=" .. tostring(ok_r)
\t\t\t\t\t.. (ok_r and "" or (" error=" .. tostring(err_r))))
\t\t\t\tlocal ok_p, parent = pcall(function() return node:Parent() end)
\t\t\t\tif not ok_p or parent == nil then break end
\t\t\t\tlocal ok_w, wrapped = pcall(function() return UIComponent(parent) end)
\t\t\t\tif not ok_w or wrapped == nil then break end
\t\t\t\tnode = wrapped
\t\t\tend''',
    "reporter walk up the chain")

# --- 2. which chain entry (if any) a context belongs to
rep('''-- (1) THE EVENT THAT MATTERS: a right-click on the ability icon, now that the component
-- reports its events.''',
    '''-- Does this event belong to our chain? Returns the id of the matching component, or nil.
-- Compared by address first (what vanilla does) and by id second.
local function in_chain(context)
\tfor i = 1, #watch_chain do
\t\tlocal e = watch_chain[i]
\t\tif e.addr ~= nil and context.component ~= nil and context.component == e.addr then
\t\t\treturn e.id or "?"
\t\tend
\tend
\tfor i = 1, #watch_chain do
\t\tlocal e = watch_chain[i]
\t\tif e.id ~= nil and context.string == e.id then return e.id end
\tend
\treturn nil
end

-- (1) THE EVENT THAT MATTERS: a right-click on the ability icon, now that the component
-- reports its events.''',
    "in_chain helper")

# --- 3. the right-click listener: unfiltered but labelled, and it toggles for the whole chain
rep('''core:add_listener(
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
)''',
    '''local rclick_other = 0
core:add_listener(
\t"zz_deadly_onslaught_rclick",
\t"ComponentRClickUp",
\tfunction(context) return true end,          -- unfiltered ON PURPOSE: the log labels it
\tfunction(context)
\t\tlocal who = in_chain(context)
\t\tif who ~= nil then
\t\t\tlog("RCLICK: right-click came in on '" .. tostring(context.string) .. "' - in our chain ("
\t\t\t\t.. who .. ")")
\t\t\tset_auto(not AUTO_ENABLED, "right-click on the ability icon")
\t\telse
\t\t\tif rclick_other < 15 then
\t\t\t\trclick_other = rclick_other + 1
\t\t\t\tlog("RCLICK: right-click on '" .. tostring(context.string) .. "' - not ours")
\t\t\tend
\t\tend
\tend,
\ttrue
)''',
    "right-click listener: unfiltered, labelled, chain-wide")

# --- 4. the left-click control listener: the same treatment
rep('''core:add_listener(
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
)''',
    '''local lclick_other = 0
core:add_listener(
\t"zz_deadly_onslaught_lclick_control",
\t"ComponentLClickUp",
\tfunction(context) return true end,          -- unfiltered ON PURPOSE: the log labels it
\tfunction(context)
\t\tlocal who = in_chain(context)
\t\tif who ~= nil then
\t\t\tlog("CONTROL: left-click came in on '" .. tostring(context.string) .. "' - in our chain ("
\t\t\t\t.. who .. ") - component click events DO reach script in battle")
\t\telse
\t\t\tif lclick_other < 15 then
\t\t\t\tlclick_other = lclick_other + 1
\t\t\t\tlog("CONTROL: left-click on '" .. tostring(context.string) .. "' - not ours")
\t\t\tend
\t\tend
\tend,
\ttrue
)''',
    "left-click control listener: unfiltered, labelled")

p.write_text(s, encoding="utf-8", newline="")
for r in report:
    print(r)
print("   in_chain:", s.count("in_chain"), "| watch_chain:", s.count("watch_chain"))
