"""Round 26: the firehose diagnostic build.

Subscribes to EVERY event the engine declares (399 names, read out of script/events.lua) and dumps
every component the HUD scan visits (id, state, visibility, animation, first image path). Events that
belong to our ability button's chain - or to Boris's unit card - are logged unconditionally, so the
per-event caps can never hide the thing we care about.
"""
import re
from pathlib import Path

NAMES = [n for n in Path(r"C:\Users\vlady\AppData\Local\Temp\wh3_eventnames.txt")
         .read_text(encoding="utf-8").split("\n") if n.strip()]
assert len(NAMES) == 399, len(NAMES)

p = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua")
s = p.read_text(encoding="utf-8", errors="replace")

# --- 1. the switch OFF for this test, so the toggle is visible if it happens
old = s[s.index("local AUTO_ENABLED = true"):s.index("local AUTO_ENABLED = true") + 340]
s = s.replace("local AUTO_ENABLED = true          -- <- the switch itself: ON by default",
              "local AUTO_ENABLED = false         -- <- switch OFF for the firehose test: a working toggle\n"
              "                                   --    is then visible (the icon pulses when armed)",
              1)
assert "local AUTO_ENABLED = false" in s

# --- 2. per-component detail in the scan
old_scan = '''\tlocal ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)'''
new_scan = '''\t-- DIAGNOSTIC: what is this component? Dumped for every component the scan visits, once.
\tif diag_scan_lines < 420 then
\t\tdiag_scan_lines = diag_scan_lines + 1
\t\tlocal ok_i, id = pcall(function() return uic:Id() end)
\t\tlocal ok_s, state = pcall(function() return uic:CurrentState() end)
\t\tlocal ok_v, vis = pcall(function() return uic:Visible() end)
\t\tlocal ok_a2, anim = pcall(function() return uic:CurrentAnimationId() end)
\t\tlocal ok_g, img = pcall(function() return uic:GetImagePath(0) end)
\t\tlog(string.format("COMP id='%s' state='%s' visible='%s' anim='%s' img0='%s'",
\t\t\ttostring(ok_i and id or "?"), tostring(ok_s and state or "?"),
\t\t\ttostring(ok_v and vis or "?"), tostring(ok_a2 and anim or "?"),
\t\t\ttostring(ok_g and img or "?")))
\tend

\tlocal ok_key, key = pcall(function() return uic:InterfaceFunction("AbilityKeyForScript") end)'''
assert s.count(old_scan) == 1
s = s.replace(old_scan, new_scan, 1)

# --- 3. the firehose itself, appended as section 10
events_lua = ",\n".join(f'\t"{n}"' for n in NAMES)
firehose = f'''

-- ============================================================================
-- 10. THE FIREHOSE (diagnostic build)
--     Every event name the engine declares in script/events.lua is subscribed to,
--     with a shared callback that logs the event, the component name and whatever
--     else the context carries. Events from our ability chain or from Boris's unit
--     card bypass the caps, so nothing we care about can be hidden by the limit.
-- ============================================================================

local diag_interesting_cap = 400      -- lines for events that touch our chain / our card
local diag_event_cap = 4              -- lines per event name, for everything else
local diag_total_cap = 5000
local diag_lines = 0
local diag_interesting = 0
local diag_counts = {{}}              -- event name -> occurrences seen
local diag_registered = 0
local diag_failed = 0

local function diag_describe(context)
\tlocal bits = {{}}
\tpcall(function() if context.string ~= nil then bits[#bits + 1] = "string=" .. tostring(context.string) end end)
\tpcall(function() if context.component ~= nil then bits[#bits + 1] = "component=" .. tostring(context.component) end end)
\tpcall(function() if context.unit ~= nil then bits[#bits + 1] = "unit=" .. tostring(context.unit) end end)
\tpcall(function() if context.faction ~= nil then bits[#bits + 1] = "faction=" .. tostring(context.faction) end end)
\tpcall(function() if context.bool ~= nil then bits[#bits + 1] = "bool=" .. tostring(context.bool) end end)
\treturn table.concat(bits, " ")
end

local function diag_callback(event_name)
\treturn function(context)
\t\tlocal n = (diag_counts[event_name] or 0) + 1
\t\tdiag_counts[event_name] = n

\t\tlocal who = nil
\t\tpcall(function() who = in_chain(context) end)
\t\tlocal is_card = our_unit_ui_id ~= nil and context ~= nil
\t\t\tand tostring(context.string) == tostring(our_unit_ui_id)

\t\tif (who ~= nil or is_card) and diag_interesting < diag_interesting_cap then
\t\t\tdiag_interesting = diag_interesting + 1
\t\t\tlog("EVENT* " .. event_name .. " on OUR component '" .. tostring(context.string) .. "'"
\t\t\t\t.. " " .. diag_describe(context))
\t\telseif n <= diag_event_cap and diag_lines < diag_total_cap then
\t\t\tdiag_lines = diag_lines + 1
\t\t\tlog("EVENT " .. event_name .. " " .. diag_describe(context))
\t\telseif n == diag_event_cap + 1 then
\t\t\tlog("EVENT " .. event_name .. " (further occurrences suppressed)")
\t\tend
\tend
end

local diag_events = {{
{events_lua}
}}

for i = 1, #diag_events do
\tlocal name = diag_events[i]
\tlocal ok = pcall(function()
\t\tcore:add_listener("zz_diag_" .. name, name, function() return true end,
\t\t\tdiag_callback(name), true)
\tend)
\tif ok then diag_registered = diag_registered + 1 else diag_failed = diag_failed + 1 end
end

log("DIAG: subscribed to " .. tostring(diag_registered) .. " of " .. tostring(#diag_events)
\t.. " event names (" .. tostring(diag_failed) .. " refused by the engine)")
log("DIAG: interesting events (our chain / our card) are logged without a cap")
'''

anchor = "-- ============================================================================\n-- 9. START IT UP"
assert anchor in s
s = s.replace(anchor, firehose.lstrip("\n") + "\n\n" + anchor, 1)

# the scan needs its counter declared before the scan function uses it
s = s.replace("local walk_visits = 0", "local walk_visits = 0\nlocal diag_scan_lines = 0", 1)
assert "diag_scan_lines = 0" in s

p.write_text(s, encoding="utf-8", newline="")
print("firehose installed")
print("   events subscribed:", s.count('"zz_diag_"'))
print("   AUTO_ENABLED:", [l.strip()[:60] for l in s.splitlines() if l.startswith("local AUTO_ENABLED")][0])
print("   lines:", len(s.splitlines()))
