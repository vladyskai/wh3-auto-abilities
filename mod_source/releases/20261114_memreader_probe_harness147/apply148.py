r"""Round 148: the memreader probe (read-only, optional). Applies the SAME text change to the live
source and the annotated copy."""
import sys

FILES = [
    r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
    r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua",
]

ANCHOR_FN = '''-- one unit's row: plain "key=value" pairs, one line, nothing but reads. For OUR
-- units the routing read is skipped (the player sees it, and the poll loop
-- already reads it every tick).
function FOURTH.map_row(u, side, t, alliance)'''

NEW_BLOCK = '''-- ROUND 148 - THE MEMREADER PROBE (READ-ONLY, OPTIONAL; user approval 2026-11-14).
--   When the player has the "memreader Plus" mod enabled, its Lua table
--   (_G.memreader_plus) can read the game's memory. This probe reads three
--   engine fields of every unit on the map row, to prove the reads match what
--   the game shows (found in round 147 with the outside reader):
--     mr_lead = current leadership  [unit+8]+0x3B78  (signed whole number)
--     mr_hp   = current hit points  [[unit+8]+0x280]+0x5CC
--     mr_men  = men alive           [unit+8]+0xA4
--   "unit" is the address behind the script handle (memreader's ud_topointer,
--   the same address the addr= field prints). It only READS: it never writes,
--   hooks or calls a game function. Without memreader Plus nothing changes
--   (the fields read "-"). Every read is pcall'd; after FOURTH.MR_FAIL_LIMIT
--   failed units in a row it stops reading for the rest of the battle. Status
--   lines (present / absent / failed / off) join the map rows. No trigger
--   reads these values.
FOURTH.MR_UNIT_OFF = 0x8
FOURTH.MR_LEAD_OFF = 0x3B78
FOURTH.MR_MEN_OFF = 0xA4
FOURTH.MR_HP_PTR_OFF = 0x280
FOURTH.MR_HP_OFF = 0x5CC
FOURTH.MR_FAIL_LIMIT = 3
FOURTH.mr = nil
FOURTH.mr_state = nil
FOURTH.mr_fails = 0
FOURTH.mr_notes = {}

-- once per battle: is memreader Plus loaded, with the four functions we use?
function FOURTH.mr_check()
	if FOURTH.mr_state ~= nil then return end
	local m = nil
	pcall(function() m = _G.memreader_plus end)
	if type(m) == "table" and type(m.ud_topointer) == "function" and type(m.read_pointer) == "function"
		and type(m.read_int32) == "function" and type(m.is_null) == "function" then
		FOURTH.mr = m
		FOURTH.mr_state = "present"
		local v = "?"
		pcall(function() v = tostring(m.version) end)
		FOURTH.mr_notes[#FOURTH.mr_notes + 1] = "MEMREADER present version=" .. v
	else
		FOURTH.mr_state = "absent"
		FOURTH.mr_notes[#FOURTH.mr_notes + 1] = "MEMREADER absent (memreader Plus is not enabled; mr_ fields read -)"
	end
end

function FOURTH.mr_num(v)
	if type(v) == "number" then return string.format("%d", v) end
	return "?"
end

-- the three reads of one unit, as text for the map row
function FOURTH.mr_unit(u)
	if FOURTH.mr_state ~= "present" then return "-", "-", "-" end
	local ok, lead, hp, men = pcall(function()
		local m = FOURTH.mr
		local iface = m.ud_topointer(u)
		if iface == nil or m.is_null(iface) then error("no address behind the unit handle") end
		local obj = m.read_pointer(iface, FOURTH.MR_UNIT_OFF)
		if obj == nil or m.is_null(obj) then error("no engine unit behind the handle") end
		local l = m.read_int32(obj, FOURTH.MR_LEAD_OFF)
		local n = m.read_int32(obj, FOURTH.MR_MEN_OFF)
		local h = nil
		local hpo = m.read_pointer(obj, FOURTH.MR_HP_PTR_OFF)
		if hpo ~= nil and not m.is_null(hpo) then h = m.read_int32(hpo, FOURTH.MR_HP_OFF) end
		return l, h, n
	end)
	if not ok then
		FOURTH.mr_fails = FOURTH.mr_fails + 1
		if FOURTH.mr_fails == 1 then
			FOURTH.mr_notes[#FOURTH.mr_notes + 1] = "MEMREADER read failed: " .. tostring(lead)
		end
		if FOURTH.mr_fails >= FOURTH.MR_FAIL_LIMIT then
			FOURTH.mr_state = "off"
			FOURTH.mr_notes[#FOURTH.mr_notes + 1] = "MEMREADER off for this battle after "
				.. FOURTH.mr_fails .. " failed units in a row"
		end
		return "?", "?", "?"
	end
	FOURTH.mr_fails = 0
	return FOURTH.mr_num(lead), FOURTH.mr_num(hp), FOURTH.mr_num(men)
end

''' + ANCHOR_FN

OLD_SV = '''		.. " sv=" .. FOURTH.map_num(function() return u:strategic_value() end, "%.1f")
'''
NEW_SV = '''		.. " sv=" .. FOURTH.map_num(function() return u:strategic_value() end, "%.1f")
		.. " mr_lead=" .. ml .. " mr_hp=" .. mh .. " mr_men=" .. mm
'''
OLD_VIS = '''	if alliance ~= nil then vis = FOURTH.map_flag(function() return u:is_visible_to_alliance(alliance) end) end
	return "MAP t=" .. t'''
NEW_VIS = '''	if alliance ~= nil then vis = FOURTH.map_flag(function() return u:is_visible_to_alliance(alliance) end) end
	local ml, mh, mm = FOURTH.mr_unit(u)
	return "MAP t=" .. t'''
OLD_ROWS = '''	local alliance = FOURTH.map_alliance
	local rows, n_own, n_en = {}, 0, 0'''
NEW_ROWS = '''	local alliance = FOURTH.map_alliance
	FOURTH.mr_check()
	local rows, n_own, n_en = {}, 0, 0'''
OLD_END = '''	rows[#rows + 1] = "MAP_END t=" .. t .. " own=" .. n_own .. " enemy=" .. n_en'''
NEW_END = '''	for i = 1, #FOURTH.mr_notes do rows[#rows + 1] = FOURTH.mr_notes[i] end
	FOURTH.mr_notes = {}
	rows[#rows + 1] = "MAP_END t=" .. t .. " own=" .. n_own .. " enemy=" .. n_en'''

for path in FILES:
    s = open(path, "rb").read().decode("utf-8")
    for old in (ANCHOR_FN, OLD_SV, OLD_VIS, OLD_ROWS, OLD_END):
        if s.count(old) != 1:
            sys.exit("anchor count %d in %s:\n%s" % (s.count(old), path, old[:80]))
    s = (s.replace(ANCHOR_FN, NEW_BLOCK).replace(OLD_SV, NEW_SV).replace(OLD_VIS, NEW_VIS)
         .replace(OLD_ROWS, NEW_ROWS).replace(OLD_END, NEW_END))
    open(path, "wb").write(s.encode("utf-8"))
    print("patched", path)
