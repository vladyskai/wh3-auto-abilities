"""Build harness102.lua from harness101.lua: rename the env pair, re-base the
table-size pins onto the grown 642/682 table, adapt the handful of static gates
this round's code moved, add the HARNESS 102 section (all four summons triggers)
and its red control."""
import os, re

TEMP = os.path.expandvars(r"%LOCALAPPDATA%\Temp")
SRC = os.path.join(TEMP, "harness101.lua")
DST = os.path.join(TEMP, "harness102.lua")

s = open(SRC, encoding="utf-8").read()

def must(old, new, n=1, tag=""):
    global s
    c = s.count(old)
    assert c == n, "anchor %r hit %d (want %d) %s" % (old[:70], c, n, tag)
    s = s.replace(old, new)

# ---- 1. env pair + the harness-101 boundary constant ------------------------
must("H101_LIVE", "H102_LIVE", 5, "live env")
must("H101_ANN", "H102_ANN", 5, "ann env")
must('print("== harness 84: file mode ==")', 'print("== harness 102: file mode ==")', 1)
# NO new main-chunk local: the harness chunk sits at Lua's 200-local ceiling, so
# the harness-101 boundary count is a literal inside the new section.

# ---- 2. the table-size pins ------------------------------------------------
s = re.sub(r"(?<![0-9])573(?![0-9])", "642", s)
s = re.sub(r"(?<![0-9])599(?![0-9])", "682", s)

# ---- 3. the static gates this round's code moved ---------------------------
must("cp(s, 'trigger = \"enemy_ground_melee\"') == 1)",
     "cp(s, 'trigger = \"enemy_ground_melee\"') == 67)", 1, "melee count")
must('cp(s, "FOURTH.eg_enemy = best_enemy") == 1)',
     'cp(s, "FOURTH.eg_enemy = best_enemy") == 2)', 1, "eg set count")
must('check("0u " .. nm .. ": every Class-A entry carries its REAL range (range_real x96)",\n      cp97(s, "\\t\\trange_real = ") == 96)',
     'check("0u " .. nm .. ": every Class-A entry carries its REAL range (range_real x163)",\n      cp97(s, "\\t\\trange_real = ") == 163)', 1, "range_real count")
must("""  check("0u live: the pre-cast re-check is marker-prefixed and prints the REAL distance + bound",
    raw_find(live_src97, 'log("  " .. eg_marker_now .. " pre-cast re-check:', 1, true) ~= nil
    and raw_find(live_src97, '.. "m bound=" .. tostring(eg_bound_now) .. "m) - firing")', 1, true) ~= nil)""",
     """  check("0u live: the pre-cast re-check is marker-prefixed and prints the REAL distance + bound",
    raw_find(live_src97, 'log("  " .. eg_marker_now .. " pre-cast re-check:', 1, true) ~= nil
    and raw_find(live_src97, '.. "m bound=" .. eg_bound_text .. ") - firing")', 1, true) ~= nil)""", 1, "0u precast")
must("""    and raw_find(live_src96, '.. " bound=" .. tostring(eg_bound_now) .. "m) - cast not spent")', 1, true) ~= nil)""",
     """    and raw_find(live_src96, '.. " bound=" .. eg_bound_text .. ") - cast not spent")', 1, true) ~= nil)""", 1, "0t precast")
must("""    and raw_find(live_src96, '.. "m) - firing")', 1, true) ~= nil""",
     """    and raw_find(live_src96, '.. "m bound=" .. eg_bound_text .. ") - firing")', 1, true) ~= nil""", 1, "0t firing token")

# the bootstrap iteration count is 2 x #ABILITIES (642 now)
must("    a = (it == 1146)", "    a = (it == 1284)", 1, "A4a iterations")

# the OTHER two places that still pin the enemy_ground_melee count at 1
must("""      and cp97(s, 'trigger = "enemy_ground_melee"') == 1)""",
     """      and cp97(s, 'trigger = "enemy_ground_melee"') == 67)""", 1, "0u melee count")
must("""        and cp101(s, 'trigger = "enemy_ground_melee"') == (EXP.gate and 1 or 0))""",
     """        and cp101(s, 'trigger = "enemy_ground_melee"') == (RED_MODE and 1 or 67))""", 1, "0aa melee count")

# the three new tooltip wordings must be allowed in the harness-93 map check
must('    enemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground",\n',
     '    enemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground",\n'
     '    self_summon_melee = "When armed, fires when this unit itself is fighting in melee and the summon is cast on it",\n'
     '    enemy_low_health_noncommander = "When armed, fires on the lowest-health enemy in range that is below 20% health and is not a Lord or Hero",\n'
     '    enemy_melee_noncommander = "When armed, fires on the closest enemy in range that is fighting in melee and is not a Lord or Hero",\n', 1, "tip words")

# ---- 5. re-base the two PREVIOUS rounds' red-mode expectations --------------
# Their red snapshots are one generation older than ours: the pre-102 snapshot
# IS the shipped harness-101 build (573 entries / 599 keys, five boss keys gone,
# Gate of Khorne present), so those EXP tables must describe THAT file.
must("    EXP = { entries = 577, keys = 603, mu = 362, ush = 33, present = false }",
     "    EXP = { entries = 573, keys = 599, mu = 360, ush = 33, present = false }", 1, "h100 red EXP")
must("    EXP = { entries = 577, keys = 603, mu = 362, es = 89, gate = false, boss = true }",
     "    EXP = { entries = 573, keys = 599, mu = 360, es = 86, gate = true, boss = false }", 1, "h101 red EXP")
must('''    check("RED CONTROL (harness 101): on the pre-101 snapshot Gate of Khorne is absent, so every gate world fires "
      .. "NOTHING (ground " .. RED101.ground .. ", unit " .. RED101.fires .. ") while the SILENT worlds pass by "
      .. "design; the five boss keys are still carried and every green 0aa check would FAIL.", RED101.ground == 0)''',
     '''    check("RED CONTROL (harness 101): N/A for the harness-102 round - the harness-102 red snapshot IS the "
      .. "shipped harness-101 build, so Gate of Khorne is present there and its gate worlds fire by design "
      .. "(ground " .. RED101.ground .. ", unit " .. RED101.fires .. "). The summon-round red control lives in "
      .. "harness 102's own section.", true)''', 1, "h101 red aggregate")

# ---- 4. the mock's commander read -----------------------------------------
must("    function u:is_valid() touch(); return def.invalid ~= true end\n",
     "    function u:is_valid() touch(); return def.invalid ~= true end\n"
     "    -- HARNESS 102: the commander-class read. It is the FALLBACK - the\n"
     "    -- PRIMARY test is the derived key list matched on the PROVEN type()\n"
     "    -- read; a world models the fallback by taking type() away.\n"
     "    if not def.no_unit_class then\n"
     "      function u:unit_class()\n"
     "        touch()\n"
     "        if def.unit_class_raises then error(\"mock: unit_class refused\", 0) end\n"
     "        if def.unit_class ~= nil then return def.unit_class end\n"
     "        return \"inf_mel\"\n"
     "      end\n"
     "    end\n", 1, "mock unit_class")

open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("harness102 base written:", len(s), "bytes")
