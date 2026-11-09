#!/usr/bin/env python3
"""Build harness136.lua from harness135.lua for round 137 (audit batch 6: morale). Older harnesses are never
edited.

Pin rebases (code lines only; comment lines untouched):
  melee_unwavering 328 -> 314 (9 to the new wavering_aura, 5 to wavering_ally_range),
  wavering_ally_range 1 -> 6, ally_range_real fields 46 -> 51 (the five new ally bounds);
  the harness-93 tooltip mirror gains the wavering_aura wording.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_melee_hexes_harness135\harness135.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_morale_harness136\harness136.lua"

BANNER = """-- ============================================================================
-- HARNESS 136 - ROUND 137: AUDIT BATCH 6, MORALE.
--   wavering_aura (NEW, 9 entries); wavering_ally_range gains 5.
--   Edited vs harness135: this banner, the pin rebases listed in
--   tools/make_harness136.py, the tooltip mirror, run_h136 and its call.
--   RED control: H136_LIVE / H136_ANN on docs/backups/round137/pre137_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 136 (round 137): AUDIT BATCH 6, MORALE.
--   0zh tokens. R1-R6 Rally! (aura 35 m -> 24 m): the caster wavering casts;
--   an ally wavering at 20 m casts; at 30 m does not; in melee with nobody
--   wavering does not; an unreadable morale does not; a ROUTING ally does not.
--   U1 Unholy Clamour: an ally wavering 150 m away (whole army) casts.
--   M1 Mirror (Cold-Blooded): an ally wavering 10 m away does not (self only);
--   M2 the caster wavering casts.
--   C1 Crown of Command: a wavering ally 60 m away (bound 70 m) -> cast ON that
--   ally. C2 Tacticians, Rally!: no wavering ally -> no cast, even in melee.
--   RED (pre-137 = round 136): R2 and C1 cast nothing; R4 casts (the old
--   in-melee trigger).
-- ============================================================================
function run_h136()
  local L136 = os.getenv("H136_LIVE") or LIVE
  local A136 = os.getenv("H136_ANN") or ANN
  local RED136 = (os.getenv("H136_LIVE") ~= nil) or (os.getenv("H136_ANN") ~= nil)
  local RALLY = "wh_main_character_abilities_rally"
  local CLAM = "wh2_main_mount_abilities_unholy_clamour"
  local MIRROR = "wh2_dlc15_unit_abilities_mimic_cold_blooded"
  local CROWN = "wh_main_item_abilities_crown_of_command"
  local TACT = "wh3_dlc24_character_abilities_tacticians_rally"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local PLAIN = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local pre136 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 136 - section 0zh: the round-137 tokens ==")
  if not RED136 then
    for _, f in ipairs({ { name = "live", path = L136 }, { name = "ann", path = A136 } }) do
      local s = read_file(f.path)
      check("0zh " .. f.name .. ": wavering_aura is wired; counts 9 / wavering_ally_range 6 / melee_unwavering 314",
        raw_find(s, "wavering_aura = FOURTH.evaluate_wavering_aura,", 1, true) ~= nil
        and cp(s, 'trigger = "wavering_aura"') == 9 and cp(s, 'trigger = "wavering_ally_range"') == 6
        and cp(s, 'trigger = "melee_unwavering"') == 314)
    end
  end

  local FILES = { { path = A136, tag = "[annotated] " }, { path = L136, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function fires_of(W, key)
    local n = 0
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1 end end
    return n
  end
  local function world(wname, units, arm, key, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = { { id = "b1", key = key } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  -- caster def extras, ally def (nil = no ally)
  local function two(b, key, cdef, adef)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, wavering = false }
    for k, v in pairs(cdef or {}) do c[k] = v end
    local units = { c }
    if adef ~= nil then
      local a = { name = PLAIN, uid = b + 1, owns = {}, melee = false, wavering = false }
      for k, v in pairs(adef) do a[k] = v end
      units[2] = a
    end
    return units
  end
  -- name, units(b), marker, key, GREEN casts, RED casts (nil = not RED), target: "self" / "ally"
  local WORLDS = {
    { "R1. Rally!: the caster is wavering -> ONE cast on the caster",
      function(b) return two(b, RALLY, { wavering = true }) end, "rally", RALLY, 1, nil, "self" },
    { "R2. Rally!: an ally 20 m away is wavering (bound 24 m) -> ONE cast on the caster",
      function(b) return two(b, RALLY, nil, { wavering = true, dist = 20 }) end, "rally", RALLY, 1, 0, "self" },
    { "R3. Rally!: the wavering ally is 30 m away -> no cast",
      function(b) return two(b, RALLY, nil, { wavering = true, dist = 30 }) end, "rally", RALLY, 0, nil, nil },
    { "R4. Rally!: the caster in melee, nobody wavering -> no cast",
      function(b) return two(b, RALLY, { melee = true }, { dist = 10 }) end, "rally", RALLY, 0, 1, nil },
    { "R5. Rally!: the caster's morale is unreadable -> no cast",
      function(b) return two(b, RALLY, { wavering_raises = true }) end, "rally", RALLY, 0, nil, nil },
    { "R6. Rally!: the only wavering ally is ROUTING -> no cast",
      function(b) return two(b, RALLY, nil, { wavering = true, routing = true, dist = 10 }) end, "rally", RALLY, 0, nil, nil },
    { "U1. Unholy Clamour: an ally wavering 150 m away (whole army) -> ONE cast",
      function(b) return two(b, CLAM, nil, { wavering = true, dist = 150 }) end, "unholy_clamour", CLAM, 1, nil, "self" },
    { "M1. Mirror (Cold-Blooded): an ally wavering 10 m away -> no cast (self only)",
      function(b) return two(b, MIRROR, nil, { wavering = true, dist = 10 }) end, "mimic_cold_blooded", MIRROR, 0, nil, nil },
    { "M2. Mirror (Cold-Blooded): the caster is wavering -> ONE cast",
      function(b) return two(b, MIRROR, { wavering = true }) end, "mimic_cold_blooded", MIRROR, 1, nil, "self" },
    { "C1. Crown of Command: an ally wavering 60 m away (bound 70 m) -> ONE cast ON that ally",
      function(b) return two(b, CROWN, nil, { wavering = true, dist = 60 }) end, "crown_of_command", CROWN, 1, 0, "ally" },
    { "C2. Tacticians, Rally!: in melee, nobody wavering -> no cast",
      function(b) return two(b, TACT, { melee = true }, { dist = 10 }) end, "tacticians_rally", TACT, 0, nil, nil },
  }

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED136 then want = w[6] end
      if want ~= nil then
        local base = 13900 + i * 10
        local W = world(w[1], w[2](base), { base, w[3] }, w[4], f.path, TAG)
        if W ~= nil then
          local got = fires_of(W, w[4])
          local a = (got == want)
          if a and want == 1 and not RED136 then
            local t = W.fires[1].target
            local tid = nil
            if t ~= nil then pcall(function() tid = tostring(t:unique_ui_id()) end) end
            if w[7] == "self" then
              a = (W.fires[1].uid == base) and (t == nil or tid == tostring(base))
            else
              a = (W.fires[1].uid == base) and tid == tostring(base + 1)
            end
          end
          check(TAG .. w[1]:sub(1, 2) .. (RED136 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ((want == 1 and not RED136) and (" (on the " .. w[7] .. ")") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end

  if RED136 then
    check("RED CONTROL (harness 136): the pre-137 build casts the morale abilities in melee, not on wavering - "
      .. n_ok .. "/" .. n_all, n_all == 6 and n_ok == 6)
  else
    check("HARNESS 136: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 22 and n_ok == 22)
  end
  print("== HARNESS 136 done: " .. (checks - pre136) .. " checks in this section ==")
end
'''

PIN_RULES = [
    (r"(trigger = \"melee_unwavering\"'\)) == 328\b", r"\1 == 314"),
    (r"\bmu == 328\b", "mu == 314"),
    (r"\bmu = 328\b", "mu = 314"),
    (r"(trigger = \"wavering_ally_range\"'\)) == 1\b", r"\1 == 6"),
    (r"(ally_range_real = \"\)) == 46\b", r"\1 == 51"),
]
src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed, hits = [], {a: 0 for a, _ in PIN_RULES}
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b in PIN_RULES:
        new2, n = re.subn(a, b, new)
        if n:
            hits[a] += n
            new = new2
    if new != ln:
        changed.append((i + 1, ln.strip()[:110], new.strip()[:110]))
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed), "| rules with no hit:", [a for a, v in hits.items() if v == 0])
for n, old, new in changed:
    print("  L%-6d OLD %s\n          NEW %s" % (n, old, new))
TIP_OLD = '    enemy_fast_near_ally = "When armed, fires on a fast enemy unit moving close to your units",\n'
TIP_NEW = TIP_OLD + '    wavering_aura = "When armed, fires when this unit or a friendly unit near it is wavering",\n'
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h134()\nrun_h135()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h136()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
