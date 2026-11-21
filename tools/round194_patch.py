#!/usr/bin/env python3
"""Round 194 (user rulings 2026-11-21), both copies (the live source and the annotated reading copy):

REMEMBERED M/A STATES (option A: "implement", per unit type and ability). Every badge or ALL click that changes a switch
also records it for the unit's TYPE in a small text file next to the game (FOURTH.REMEMBER_FILE). At the next battle a
unit with no switch of its own takes its type's remembered state before the family default. Only switches that differ
from the default are stored, so a click back to the default removes the line. The reset ("Do it the MCT route. MCT
should not be a requirement for the mod to work, only needed for this button") lives in a separate MCT settings script
that empties the file. The battle script never needs MCT.

The remembered states live on each ability entry (ability.remembered[unit type] = true/false, nil when none), because
is_armed sits above the FOURTH table in the file and can reach ability_for() but not FOURTH. A unit's type is read only
for an ability that has a remembered state, so a battle with an empty file reads nothing new.
TEST-ONLY: ZZ_AUTO_TEST_NO_REMEMBER (the harness sets it for every older world) switches reading and writing off,
ZZ_AUTO_TEST_REMEMBER_FILE points a test at its own file.
Backups: docs/backups/round194/pre194_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round194"

BLOCK = """-- ============================================================================
-- ROUND 194 - REMEMBERED M/A STATES (user 2026-11-21: "implement", option A:
-- per unit type and ability). A click that changes a switch also records it
-- for the unit's TYPE (unit:type()) in FOURTH.REMEMBER_FILE, a small text file
-- next to the game: one line per switch, "<unit type> <marker> A|M". The next
-- battle reads it at load: a unit with no switch of its own takes its type's
-- remembered state before the family default (is_armed, FOURTH.armed_slot).
-- The states live on each ability entry (ability.remembered[unit type]).
-- Only a switch that DIFFERS from the default is stored: clicking back to the
-- default removes the line. The reset empties the file: the optional MCT
-- settings script does it (user: "MCT should not be a requirement for the mod
-- to work, only needed for this button"). Without MCT nothing here changes.
-- TEST-ONLY: ZZ_AUTO_TEST_NO_REMEMBER switches reading and writing off,
-- ZZ_AUTO_TEST_REMEMBER_FILE points a test at its own file.
-- ============================================================================
FOURTH.REMEMBER_FILE = "smart_ability_autocast_settings.txt"

function FOURTH.remember_on() return ZZ_AUTO_TEST_NO_REMEMBER ~= true end
function FOURTH.remember_path() return ZZ_AUTO_TEST_REMEMBER_FILE or FOURTH.REMEMBER_FILE end

function FOURTH.load_remembered()
	for _, a in ipairs(ABILITIES) do a.remembered = nil end
	if not FOURTH.remember_on() then return end
	local ok, fh = pcall(io.open, FOURTH.remember_path(), "r")
	if not ok or fh == nil then return end
	local n = 0
	pcall(function()
		for line in fh:lines() do
			local t, m, v = string.match(line, "^(%S+)%s+(%S+)%s+([AM])%s*$")
			local a = (t ~= nil) and ability_for(m) or nil
			if a ~= nil then
				a.remembered = a.remembered or {}
				a.remembered[t] = (v == "A")
				n = n + 1
			end
		end
	end)
	pcall(function() fh:close() end)
	log("REMEMBER: " .. tostring(n) .. " remembered switch(es) read from " .. FOURTH.remember_path())
end

function FOURTH.save_remembered()
	if not FOURTH.remember_on() then return end
	local lines = {}
	for _, a in ipairs(ABILITIES) do
		for t, v in pairs(a.remembered or {}) do lines[#lines + 1] = t .. " " .. a.marker .. " " .. (v and "A" or "M") end
	end
	table.sort(lines)
	local ok, fh = pcall(io.open, FOURTH.remember_path(), "w")
	if not ok or fh == nil then
		log("REMEMBER: could not write " .. FOURTH.remember_path())
		return
	end
	pcall(function() fh:write(table.concat(lines, "\\n") .. ((#lines > 0) and "\\n" or "")) end)
	pcall(function() fh:close() end)
end

function FOURTH.unit_type_of_slot(slot)
	local u = units_by_ui_id[tostring(slot)]
	if u == nil then return nil end
	local ok, t = pcall(function() return u:type() end)
	if ok and type(t) == "string" then return t end
	return nil
end

-- the remembered switch of this unit's type for this ability, or nil (no type read when the ability has none)
function FOURTH.remembered_value(slot, marker)
	local a = ability_for(marker)
	if a == nil or a.remembered == nil then return nil end
	local t = FOURTH.unit_type_of_slot(slot)
	if t == nil then return nil end
	return a.remembered[t]
end

-- a click changed (unit, ability) to value: record it for the unit's type
function FOURTH.remember(ui_id, marker, value)
	if not FOURTH.remember_on() then return end
	local a = ability_for(marker)
	local t = FOURTH.unit_type_of_slot(ui_id)
	if a == nil or t == nil then return end
	a.remembered = a.remembered or {}
	if (value == true) == (a.default_on == true) then
		a.remembered[t] = nil
	else
		a.remembered[t] = (value == true)
	end
	if next(a.remembered) == nil then a.remembered = nil end
	FOURTH.save_remembered()
end

FOURTH.load_remembered()

local function set_auto_for_unit(ui_id, marker, value)
"""

EDITS = [
    # the switch writes through FOURTH.remember
    ("\tper[marker] = value == true\n\tlog(\"AUTO \" .. tostring(marker) .. \" for unit \" .. tostring(ui_id) .. \": now \"\n",
     "\tper[marker] = value == true\n\tFOURTH.remember(ui_id, marker, value)   -- ROUND 194: remembered for the unit's type\n"
     "\tlog(\"AUTO \" .. tostring(marker) .. \" for unit \" .. tostring(ui_id) .. \": now \"\n"),
    # reader 1 (above FOURTH in the file): the entry's remembered table, read through ability_for
    ("\t-- ROUND 151: an ability whose trigger family starts ARMED (user ruling 2026-11-14) is on until clicked off\n"
     "\tlocal a = ability_for(marker)\n"
     "\treturn a ~= nil and a.default_on == true\n",
     "\t-- ROUND 151: an ability whose trigger family starts ARMED (user ruling 2026-11-14) is on until clicked off\n"
     "\tlocal a = ability_for(marker)\n"
     "\tif a ~= nil and a.remembered ~= nil then   -- ROUND 194: the type's remembered switch comes first\n"
     "\t\tlocal ok_t, t = pcall(function() return unit:type() end)\n"
     "\t\tif ok_t and t ~= nil and a.remembered[t] ~= nil then return a.remembered[t] end\n"
     "\tend\n"
     "\treturn a ~= nil and a.default_on == true\n"),
    # reader 2
    ("function FOURTH.armed_slot(slot, marker)\n\tlocal per = armed[slot]\n"
     "\tif per ~= nil and per[marker] ~= nil then return per[marker] == true end\n",
     "function FOURTH.armed_slot(slot, marker)\n\tlocal per = armed[slot]\n"
     "\tif per ~= nil and per[marker] ~= nil then return per[marker] == true end\n"
     "\tlocal rv = FOURTH.remembered_value(slot, marker)   -- ROUND 194: the type's remembered switch\n"
     "\tif rv ~= nil then return rv end\n"),
]


def reading_copy(text):
    """The reading copy stays log-free: each log line becomes a comment without the word log followed by '('."""
    out = []
    for line in text.split("\n"):
        stripped = line.lstrip("\t")
        if stripped.startswith("log("):
            line = line[:len(line) - len(stripped)] + "-- (live file only) logs " + stripped[4:]
        out.append(line)
    return "\n".join(out)


def patch(path, ann):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 194 - REMEMBERED M/A STATES" not in s, "already patched: " + path
    anchor = "\nlocal function set_auto_for_unit(ui_id, marker, value)\n"
    assert s.count(anchor) == 1, path
    s = s.replace(anchor, "\n" + (reading_copy(BLOCK) if ann else BLOCK))
    for a, b in EDITS:
        if ann and a.startswith("\tper[marker] = value == true\n\tlog("):
            continue   # the reading copy's switch has no log line: handled below
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    if ann:
        a = "\tper[marker] = value == true\n"
        assert s.count(a) == 1, (path, "ann switch", s.count(a))
        s = s.replace(a, a + "\tFOURTH.remember(ui_id, marker, value)   -- ROUND 194: remembered for the unit's type\n")
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre194_live.lua"), (ANN, "pre194_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, False)
    patch(ANN, True)


if __name__ == "__main__":
    main()
