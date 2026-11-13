#!/usr/bin/env python3
"""Build harness139.lua from harness138.lua for round 140 (shooting and moving are incompatible unless the unit can
fire on the move; Blooood! on the NEW self_running). Older harnesses are never edited.

Pin rebases (code lines only; comment lines untouched):
  charge_only 5 -> 4 (Blooood! moved to self_running);
  the harness-93 tooltip mirror gains the self_running wording.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_stand_your_ground_harness138\harness138.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_moving_running_harness139\harness139.lua"

BANNER = """-- ============================================================================
-- HARNESS 139 - ROUND 140: SHOOTING AND MOVING; BLOOOOD! WHEN RUNNING.
--   QA battle 3: Boom! cast while the Hellcannon ran, 24 s after its last shot.
--   Edited vs harness138: this banner, the pin rebases listed in
--   tools/make_harness139.py, the tooltip mirror, run_h139 and its call.
--   RED control: H139_LIVE / H139_ANN on docs/backups/round140/pre140_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 139 (round 140): SHOOTING AND MOVING; BLOOOOD! WHEN RUNNING.
--   B1 Boom!: the Hellcannon shooting, standing still -> ONE cast at its cast
--   point. B2: shooting but MOVING -> no cast.
--   H1 Hail of Fire: an ally of Outriders (they fire on the move) moving and
--   shooting 30 m away -> ONE cast. H2: Handgunners moving and shooting -> none.
--   M1 Missile Mirror: enemy Handgunners whose ammunition drops but who are
--   moving -> no cast.
--   R1 Blooood!: the Hellcannon running -> ONE cast. R2: not running -> none.
--   RED (pre-140 = round 139): B2, H2 and M1 cast; R1 casts nothing.
-- ============================================================================
function run_h139()
  local L139 = os.getenv("H139_LIVE") or LIVE
  local A139 = os.getenv("H139_ANN") or ANN
  local RED139 = (os.getenv("H139_LIVE") ~= nil) or (os.getenv("H139_ANN") ~= nil)
  local BOOM = "wh_main_unit_abilities_boom"
  local BLOO = "wh_main_unit_abilities_blooood"
  local HAIL = "wh2_dlc13_lord_abilities_hail_of_fire"
  local MIR = "wh3_dlc24_unit_bound_missile_mirror"
  local HC = "wh_main_chs_art_hellcannon"       -- reload 12 s: cast point at poll 2 + 24
  local HG = "wh_main_emp_inf_handgunners"      -- reload 13 s, cannot fire on the move
  local OUT = "wh_main_emp_cav_outriders_0"     -- reload 13 s, fires on the move
  local LORD = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local pre139 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 139 - section 0zk: the round-140 tokens ==")
  if not RED139 then
    for _, f in ipairs({ { name = "live", path = L139 }, { name = "ann", path = A139 } }) do
      local s = read_file(f.path)
      check("0zk " .. f.name .. ": can_shoot_now guards every firing-flag read; Blooood! on self_running; the fire_move table exists",
        raw_find(s, "st.cast_point_passed == true and FOURTH.can_shoot_now(unit)", 1, true) ~= nil
        and raw_find(s, "st.firing ~= true or not FOURTH.can_shoot_now(unit)", 1, true) ~= nil
        and raw_find(s, "if not FOURTH.can_shoot_now(enemy) then return false end", 1, true) ~= nil
        and raw_find(s, 'name = "Blooood!", trigger = "self_running",', 1, true) ~= nil
        and raw_find(s, "FOURTH.class_keys.fire_move = {", 1, true) ~= nil
        and cp(s, 'trigger = "charge_only"') == 4)
    end
  end

  local FILES = { { path = A139, tag = "[annotated] " }, { path = L139, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function fires_of(W, key)
    local n = 0
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1 end end
    for _, f in ipairs(W.ground_fires or {}) do if f.key == key then n = n + 1 end end
    return n
  end
  local function world(wname, units, enemies, arm, key, PATH, TAG, polls)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, polls)
    return W
  end
  local function shooter(name, uid, start, extra)
    local d = { name = name, uid = uid, owns = {}, melee = false, ammo_start = start, ammo_seq = { start, start - 1 } }
    for k, v in pairs(extra or {}) do d[k] = v end
    return d
  end
  local DROPS = {}
  for i = 1, 40 do DROPS[i] = 100 - i end
  -- name, builder(b) -> units, enemies; marker; key; polls; GREEN; RED (nil = not RED)
  local WORLDS = {
    { "B1. Boom!: the Hellcannon shooting, standing still -> ONE cast",
      function(b) return { shooter(HC, b, 25, { owns = { BOOM } }) }, nil end, "boom", BOOM, 32, 1, nil },
    { "B2. Boom!: the Hellcannon shooting but MOVING -> no cast",
      function(b) return { shooter(HC, b, 25, { owns = { BOOM }, moving = true }) }, nil end, "boom", BOOM, 32, 0, 1 },
    { "H1. Hail of Fire: Outriders moving and shooting 30 m away (they fire on the move) -> ONE cast",
      function(b) return { { name = LORD, uid = b, owns = { HAIL }, melee = false }, shooter(OUT, b + 1, 100, { dist = 30, moving = true }) }, nil end,
      "hail_of_fire", HAIL, 32, 1, nil },
    { "H2. Hail of Fire: Handgunners moving and shooting 30 m away -> no cast",
      function(b) return { { name = LORD, uid = b, owns = { HAIL }, melee = false }, shooter(HG, b + 1, 100, { dist = 30, moving = true }) }, nil end,
      "hail_of_fire", HAIL, 32, 0, 1 },
    { "M1. Missile Mirror: enemy Handgunners whose ammunition drops but who are moving -> no cast",
      function(b) return { { name = LORD, uid = b, owns = { MIR }, melee = false, dist = 30 } },
        { { name = HG, uid = b + 5, melee = false, moving = true, ammo_start = 100, ammo_seq = DROPS } } end,
      "unit_bound_missile_mirror", MIR, 4, 0, 1 },
    { "R1. Blooood!: the Hellcannon running -> ONE cast",
      function(b) return { { name = HC, uid = b, owns = { BLOO }, melee = false, fast = true, moving = true } }, nil end,
      "blooood", BLOO, 4, 1, 0 },
    { "R2. Blooood!: the Hellcannon standing -> no cast",
      function(b) return { { name = HC, uid = b, owns = { BLOO }, melee = false, fast = false } }, nil end,
      "blooood", BLOO, 4, 0, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[6]
      if RED139 then want = w[7] end
      if want ~= nil then
        local base = 14200 + i * 10
        local units, enemies = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, w[5])
        if W ~= nil then
          local got = fires_of(W, w[4])
          local a = (got == want) or (want == 1 and got >= 1 and RED139)
          check(TAG .. w[1]:sub(1, 2) .. (RED139 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED139 then
    check("RED CONTROL (harness 139): the pre-140 build counts moving units as shooting and has no running trigger - "
      .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  else
    check("HARNESS 139: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 14 and n_ok == 14)
  end
  print("== HARNESS 139 done: " .. (checks - pre139) .. " checks in this section ==")
end
'''

PIN_RULES = [(r"(trigger = \"charge_only\"'\)) == 5\b", r"\1 == 4")]
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
TIP_OLD = '    melee_or_wavering_aura = "When armed, fires when this unit or a friendly unit near it is in melee or wavering",\n'
TIP_NEW = TIP_OLD + '    self_running = "When armed, fires when this unit is running",\n'
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h137()\nrun_h138()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h139()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
