"""Assemble harness110.lua from harness109.lua (one new numbered harness).

1. Extend the mock unit with the round-110 motion reads: is_moving(), a
   def-driven slow_speed(), a def-driven fast_speed(), a def-driven
   ordered_position() (DEFAULT UNCHANGED - vec(0) - so every earlier world keeps
   its exact order_gap arithmetic) and an optional bearing().
2. Record the new read counters on the world (moving_calls / speed_calls).
3. Move harness 109's call inside harness 110's suite and append the new section.
"""
import io
import shutil

SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261021_airdrop_centre_harness109/harness109.lua"
DST = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/harness110.lua"
SEC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/h110_section.lua"

s = io.open(SRC, encoding="utf-8", newline="").read()
assert "\r" not in s, "the source harness is CRLF - refusing"

# ---------------------------------------------------------------- 1. the mock
OLD_FAST = "    function u:is_moving_fast() touch(); return def.fast == true end\n"
NEW_FAST = '''    function u:is_moving_fast() touch(); return def.fast == true end
    -- HARNESS 110: THE MOTION READS THE AIR-DROP PREDICTION REBUILDS A VELOCITY
    -- FROM, answered exactly as battle_unit.lua documents them.
    --   def.moving      is_moving()        ("whether the unit is currently moving")
    --   def.moving_raises   ... the read cannot be taken (fail-closed world)
    --   def.fast        is_moving_fast()   ("moving fast (running/charging)")
    --   def.slow_speed  slow_speed()       m/s, default 4
    --   def.fast_speed  fast_speed()       m/s, default 7 (the harness-57 value)
    --   def.ordered     ordered_position() {x, y, z}; when ABSENT the answer stays
    --                   vec(0) - the pre-110 default - so the charge detector's
    --                   order_gap arithmetic of every earlier world is unchanged
    --   def.bearing     bearing()          degrees (the caster-only fallback)
    if not def.no_is_moving then
      function u:is_moving()
        touch()
        W.moving_calls[def.uid] = (W.moving_calls[def.uid] or 0) + 1
        if def.moving_raises then error("mock: is_moving refused", 0) end
        return def.moving == true
      end
    end
    function u:slow_speed()
      touch()
      W.speed_calls[def.uid] = (W.speed_calls[def.uid] or 0) + 1
      if def.slow_speed_raises then error("mock: slow_speed refused", 0) end
      if def.slow_speed ~= nil then return def.slow_speed end
      return 4
    end
    if def.bearing ~= nil or def.bearing_raises then
      function u:bearing()
        touch()
        if def.bearing_raises then error("mock: bearing refused", 0) end
        return def.bearing
      end
    end
'''
assert s.count(OLD_FAST) == 1
s = s.replace(OLD_FAST, NEW_FAST)

OLD_ORD = "    function u:ordered_position() touch(); return vec(0) end\n"
NEW_ORD = '''    function u:ordered_position()
      touch()
      if def.ordered_raises then error("mock: ordered_position refused", 0) end
      local o = def.ordered
      -- HARNESS 110: an explicit order. ABSENT -> vec(0), the pre-110 default,
      -- so no earlier world's behaviour moves.
      if o == nil then return vec(0) end
      return vec(0, o[1], o[2], o[3])
    end
'''
assert s.count(OLD_ORD) == 1
s = s.replace(OLD_ORD, NEW_ORD)

OLD_SPD = "    function u:fast_speed() touch(); return 7 end\n"
NEW_SPD = '''    function u:fast_speed()
      touch()
      W.speed_calls[def.uid] = (W.speed_calls[def.uid] or 0) + 1
      if def.fast_speed_raises then error("mock: fast_speed refused", 0) end
      if def.fast_speed ~= nil then return def.fast_speed end
      return 7
    end
'''
assert s.count(OLD_SPD) == 1
s = s.replace(OLD_SPD, NEW_SPD)

OLD_W = "    ground_fires = {},\n    position_raise_attempts = 0,\n"
NEW_W = ("    ground_fires = {},\n    position_raise_attempts = 0,\n"
         "    -- HARNESS 110: the motion-read instrumentation.\n"
         "    moving_calls = {},\n    speed_calls = {},\n")
assert s.count(OLD_W) == 1
s = s.replace(OLD_W, NEW_W)

# ------------------------------------------------- 3. the suite: 109 then 110
OLD_CALL = "\nrun_h109()\n"
assert s.count(OLD_CALL) == 1, "harness 109's own call is missing or duplicated"
s = s.replace(OLD_CALL, "\n-- HARNESS 110: harness 109's suite runs INSIDE the new one - its call moved to the\n-- very end of this file, after the new section.\n")

sec = io.open(SEC, encoding="utf-8", newline="").read()
assert "\r" not in sec

# the trailing summary block of harness 109 must move to the VERY end, after the
# new suite has run - otherwise it reports the count from before run_h110().
TAIL_SUMMARY = '''print("checks: " .. checks .. ", failures: " .. failures)
if failures == 0 then
  print("HARNESS OK - all checks passed")
else
  print("HARNESS FAILURES: " .. failures)
end'''
assert s.count(TAIL_SUMMARY) == 1, "the summary block moved"
s = s.replace(TAIL_SUMMARY, "")

s = s.rstrip() + "\n\n" + sec.rstrip() + "\n\nrun_h109()\nrun_h110()\n\n" + TAIL_SUMMARY + "\n"

io.open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST, len(s), "bytes")
