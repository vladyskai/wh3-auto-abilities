r"""Round 147: add the unit address field to the round-145 map probe rows.
Applies the SAME text change to the live source and the annotated copy."""
import sys

FILES = [
    r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
    r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua",
]

OLD_HEAD = '''-- one unit's row: plain "key=value" pairs, one line, nothing but reads. For OUR
-- units the routing read is skipped (the player sees it, and the poll loop
-- already reads it every tick).
function FOURTH.map_row(u, side, t, alliance)'''

NEW_HEAD = '''-- ROUND 147 - THE ADDRESS PROBE (READ-ONLY; user request 2026-11-14, "Lua
-- address probe"). tostring() of the unit's script handle, logged as the LAST
-- field of every MAP row ("addr="). In most Lua builds it prints the memory
-- address of the handle ("userdata: 0x..."); the outside reader
-- tools/memprobe/memprobe.py then looks behind that address for the engine's
-- own unit, to find stats the script API does not give. Spaces become "_" so the
-- row stays plain key=value pairs. It reads nothing from the engine.
function FOURTH.map_addr(u)
	local s = "?"
	pcall(function() s = tostring(u) end)
	if type(s) ~= "string" then return "?" end
	local b = {}
	for i = 1, #s do
		local c = s:sub(i, i)
		if c == " " then c = "_" end
		b[i] = c
	end
	return table.concat(b)
end

-- one unit's row: plain "key=value" pairs, one line, nothing but reads. For OUR
-- units the routing read is skipped (the player sees it, and the poll loop
-- already reads it every tick).
function FOURTH.map_row(u, side, t, alliance)'''

OLD_TAIL = '''		.. " routing=" .. ((side == "P") and "-" or FOURTH.map_flag(function() return u:is_routing() end))
end'''
NEW_TAIL = '''		.. " routing=" .. ((side == "P") and "-" or FOURTH.map_flag(function() return u:is_routing() end))
		.. " addr=" .. FOURTH.map_addr(u)
end'''

for path in FILES:
    with open(path, "rb") as f:
        s = f.read().decode("utf-8")
    for old in (OLD_HEAD, OLD_TAIL):
        if s.count(old) != 1:
            sys.exit("anchor count %d in %s" % (s.count(old), path))
    s = s.replace(OLD_HEAD, NEW_HEAD).replace(OLD_TAIL, NEW_TAIL)
    with open(path, "wb") as f:
        f.write(s.encode("utf-8"))
    print("patched", path)
