"""Round 111, take 2: the dials live in a FILE-LOCAL `FOURTH` table, so the
harness cannot poke them through a global. Each world that needs a non-default
dial therefore loads a VARIANT of the same source: the file's two constant lines
substituted, nothing else touched - exactly the one-line edit the user would make
in the field. The helper is defined once, at the top level of the harness-110
section, and reused by the round-111 section.

Also removes the (ineffective) global-poke block added by the first attempt.
"""
import io

P110 = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/h110_section.lua"
P111 = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/h111_section.lua"

s = io.open(P110, encoding="utf-8", newline="").read()
assert "\r" not in s

# ---------------------------------------------------------------- 1. the helper
OLD_HEAD = """-- ============================================================================
function run_h110()
"""
NEW_HEAD = """-- ============================================================================
-- THE DIAL VARIANTS (round 111). FOURTH is a FILE-LOCAL table, so a world cannot
-- reach the two caster dials through a global; instead it loads a copy of the
-- same source with ONLY the two constant lines substituted - precisely the edit
-- the user makes in the field. Nothing else in the file changes, so a variant
-- world differs from the shipped build in exactly one number. A build without the
-- dials (the RED CONTROL snapshot, or the round-110 annotated tree) has no such
-- lines: the original path is returned unchanged, and the world tests the old
-- build as it is.
VAR_DIR_111 = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/variants"

local function replace_all_111(s2, needle, repl)
  local out, at = {}, 1
  while true do
    local i, j = raw_find(s2, needle, at, true)
    if i == nil then break end
    out[#out + 1] = s2:sub(at, i - 1)
    out[#out + 1] = repl
    at = j + 1
  end
  out[#out + 1] = s2:sub(at)
  return table.concat(out)
end

function harness_variant(path, lead, delay, tag)
  if lead == nil and delay == nil then return path end
  local txt = read_file(path)
  local t_lead = "\\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\\n"
  local t_del = "\\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\\n"
  if raw_find(txt, t_lead, 1, true) == nil or raw_find(txt, t_del, 1, true) == nil then
    return path
  end
  if lead ~= nil then
    txt = replace_all_111(txt, t_lead, "\\nFOURTH.AIR_DROP_CASTER_LEAD = " .. string.format("%.2f", lead) .. "\\n")
  end
  if delay ~= nil then
    txt = replace_all_111(txt, t_del, "\\nFOURTH.AIR_DROP_CASTER_DELAY_S = " .. string.format("%.2f", delay) .. "\\n")
  end
  local dst = VAR_DIR_111 .. "/" .. tag .. ".lua"
  local f = assert(io.open(dst, "w"))
  f:write(txt)
  f:close()
  return dst
end

function run_h110()
"""
assert s.count(OLD_HEAD) == 1
s = s.replace(OLD_HEAD, NEW_HEAD)

# ------------------------------------------- 2. boot110 loads the variant, not a poke
OLD_B = """    -- ROUND 111: pin the caster's lead for the worlds written against the
    -- round-110 rule (lead 1.0). Read by FOURTH.ad_lead on every call, so this
    -- is the same dial the shipped default sets.
    if knobs ~= nil and FOURTH ~= nil then
      if knobs.lead ~= nil then FOURTH.AIR_DROP_CASTER_LEAD = knobs.lead end
      if knobs.delay ~= nil then FOURTH.AIR_DROP_CASTER_DELAY_S = knobs.delay end
    end
"""
NEW_B = """    -- ROUND 111: pin the caster's lead for the worlds written against the
    -- round-110 rule (lead 1.0) by loading a one-line VARIANT of the same file.
    local load_path = PATH
    if knobs ~= nil then
      load_path = harness_variant(PATH, knobs.lead, knobs.delay,
        wname .. (TAG == "[live] " and "_live" or "_ann"))
    end
"""
assert s.count(OLD_B) == 1
s = s.replace(OLD_B, "")

OLD_L = """  local function boot110(W, PATH, TAG, uid, marker, wname, knobs)
    local ok = pcall(load_world, W, PATH)
"""
NEW_L = """  local function boot110(W, PATH, TAG, uid, marker, wname, knobs)
    local load_path = PATH
    if knobs ~= nil then
      load_path = harness_variant(PATH, knobs.lead, knobs.delay,
        wname .. (TAG == "[live] " and "_live" or "_ann"))
    end
    local ok = pcall(load_world, W, load_path)
"""
assert s.count(OLD_L) == 1
s = s.replace(OLD_L, NEW_L)

io.open(P110, "w", encoding="utf-8", newline="\n").write(s)
print("patched", P110)

# ---------------------------------------------------------------- h111 section
t = io.open(P111, encoding="utf-8", newline="").read()
assert "\r" not in t

OLD_A = """  -- THE DIALS, SET ON THE LOADED SOURCE. FOURTH is a global the mod defines at
  -- load, and ad_lead reads both dials on EVERY call, so this is exactly the
  -- state a one-line constant edit produces - no test-only code path.
  local function apply111(knobs)
    if knobs == nil or FOURTH == nil then return end
    if knobs.lead ~= nil then FOURTH.AIR_DROP_CASTER_LEAD = knobs.lead end
    if knobs.delay ~= nil then FOURTH.AIR_DROP_CASTER_DELAY_S = knobs.delay end
  end
"""
NEW_A = """  -- THE DIALS, AS A ONE-LINE VARIANT OF THE SAME SOURCE (harness_variant, defined
  -- above run_h110). FOURTH is a FILE-LOCAL table, so this is the only faithful
  -- way to change a dial: the file the world loads differs from the shipped build
  -- in exactly the constant line under test.
  local function dial_path111(PATH, knobs, wname)
    if knobs == nil then return PATH end
    return harness_variant(PATH, knobs.lead, knobs.delay,
      "h111_" .. wname .. (PATH == LIVE and "_live" or "_ann"))
  end
"""
assert t.count(OLD_A) == 1
t = t.replace(OLD_A, NEW_A)

OLD_BOOT = """  local function boot111(W, PATH, TAG, uid, marker, wname, knobs)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    apply111(knobs)
"""
NEW_BOOT = """  local function boot111(W, PATH, TAG, uid, marker, wname, knobs)
    local load_path = dial_path111(PATH, knobs, wname)
    local ok = pcall(load_world, W, load_path)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
"""
assert t.count(OLD_BOOT) == 1
t = t.replace(OLD_BOOT, NEW_BOOT)

io.open(P111, "w", encoding="utf-8", newline="\n").write(t)
print("patched", P111)
