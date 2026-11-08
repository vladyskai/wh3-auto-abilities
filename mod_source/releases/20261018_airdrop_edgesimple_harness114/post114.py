# Round 114 supersessions in the OLDER sections (exec'd by assemble114.py; uses
# its `must` helper and its `s`).
#
# The air-drop evaluator was REPLACED, so the rounds that designed, tuned and
# proved the old rule (108-112 in full, and round 107's family pins + its A1-A10
# worlds) no longer describe the code. Their check SLOTS stay - the running count
# and every later boundary pin depend on them - and answer as explicit N/A, the
# same discipline the reverted-feature rounds before this one used.

s = must(s,
         'air_drop_on_infantry = "When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it",',
         'air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more than 10 models is within 0.1 m of this unit\'s edge, airborne where the ability requires it",')

s = must(s,
         'and raw_find(s2, "air_drop_on_infantry = \\"When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it\\",", 1, true) ~= nil)',
         'and raw_find(s2, "air_drop_on_infantry = \\"When armed, fires when the nearest enemy unit with more than 10 models is within 0.1 m", 1, true) ~= nil)')

# the routing read now happens in the poll AND in the fast pass
s = must(s,
         'check(nm .. "defined once and called exactly once per poll (occurrences = " .. defines .. ", want 2)", defines == 2)',
         'check(nm .. "defined once and called from BOTH timers (the poll and the round-114 fast pass): occurrences = " .. defines .. ", want 3", defines == 3)')

# the 'gone' BREAK moved into the caller of FOURTH.try_pair
s = must(s, """    local at = raw_find(s, "gone_ids[#gone_ids + 1] = ui_id", 1, true)
    local inner_break = false
    if at ~= nil then
      inner_break = raw_find(string.sub(s, at, at + 80), "break", 1, true) ~= nil
    end
    check(nm .. "the INNER per-ability walk still BREAKS on 'gone' (collect immediately followed by break)",
      inner_break)""",
"""    -- ROUND 114: the collect lives in FOURTH.try_pair (it answers "gone"); the
    -- BREAK is in the caller, immediately after that answer.
    local at = raw_find(s, 'gone_ids) == "gone" then', 1, true)
    local inner_break = false
    if at ~= nil then
      inner_break = raw_find(string.sub(s, at, at + 80), "break", 1, true) ~= nil
    end
    check(nm .. "the per-ability walk still BREAKS on 'gone' (try_pair answers gone -> the caller breaks)",
      inner_break)""")

# round 107's serialisation worlds must still FIRE to prove the gate: under the
# new rule that means a 0.05 m edge gap, not 0.5 m, and an enemy worth counting.
s = must(s, "dist_by_target = { [11734] = 0.5 }", "dist_by_target = { [11734] = 0.05 }")
s = must(s, "dist_by_target = { [11737] = 0.5 }", "dist_by_target = { [11737] = 0.05 }", 2)
s = must(s, "{ { name = INF, uid = 11734, melee = true } })",
         "{ { name = INF, uid = 11734, melee = true, men_alive = 20 } })")
s = must(s, "enemies = { { name = INF, uid = 11737, melee = true } },",
         "enemies = { { name = INF, uid = 11737, melee = true, men_alive = 20 } },")

# round 107: N/A its 0y pins and the A1-A10 worlds (a textual rename of the check
# call inside that region - no upvalue games), keep S1/S2/S3 real
_a = s.index('print("== HARNESS 107 - section 0y:')
_b = s.index("    -- S1: THE MOONDIAL / WRAITH STORM PAIR", _a)
_region = s[_a:_b]
_n = _region.count("check(")
_region = _region.replace("check(", "check107na(")
s = s[:_a] + _region + s[_b:]
s = must(s, """  local function boot107(W, PATH, TAG, uid, marker, wname)""",
"""  -- ROUND 114: the slots of round 107's air-drop rule (its 0y pins and the
  -- A1-A10 worlds) are answered N/A - the rule they proved was replaced by the
  -- simple edge-gap comparison. S1/S2/S3 below still run FOR REAL.
  local function check107na(a, b)
    check("HARNESS 107 (round 114 supersession) N/A: " .. tostring(a), true)
  end
  local _na107 = 0
  local function boot107(W, PATH, TAG, uid, marker, wname)""")

for _nm, _n, _note in (
    ("run_h108", 66, "the 70% bound and its B1-B10 centre-test worlds"),
    ("run_h109", 99, "the 6 m horizontal CENTRE test and its worlds"),
    ("run_h110", 149, "the two-body projection and its worlds"),
    ("run_h111", 134, "the two caster lead dials and their worlds"),
    ("run_h112", 105, "the two enemy lead dials, the banded log and their worlds"),
):
    _i = s.index("\nfunction " + _nm + "()")
    _j = s.index("\nend\n", _i + 1)
    _new = ("\nfunction " + _nm + "()\n"
            "  -- ROUND 114: this section's whole subject - " + _note + " -\n"
            "  -- was DELETED from the evaluator with the design it tuned. The slots stay\n"
            "  -- so the running count and every later boundary pin are unchanged.\n"
            "  for _ = 1, " + str(_n) + " do\n"
            "    check(\"" + _nm.upper() + " (round 114): N/A - the air-drop rule this section "
            "proved was replaced by the simple edge-gap comparison\", true)\n"
            "  end\nend\n")
    s = s[: _i] + _new + s[_j + len("\nend\n"):]

print("supersessions applied")
