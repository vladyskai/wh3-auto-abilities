#!/usr/bin/env python3
"""Build harness137.lua from harness136.lua for round 138 (the rarer target filters; Missile Mirror's shooting
trigger). Older harnesses are never edited.

Pin rebases (code lines only; comment lines untouched):
  enemy_engaged_or_shot 47 -> 46 (Missile Mirror to enemy_missile_shooting), target classes 16 -> 21;
  the harness-93 tooltip mirror gains the enemy_missile_shooting wording;
  harness 97 FAM INSIDE r15 (Entangle, now filtered to enemies on the ground): its enemy answers
  is_currently_flying() = false, so the inside world still proves the ground cast on the enemy.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_morale_harness136\harness136.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_rare_filters_harness137\harness137.lua"

BANNER = """-- ============================================================================
-- HARNESS 137 - ROUND 138: THE RARER TARGET FILTERS, MISSILE MIRROR SHOOTING.
--   Classes not_undead / missile / not_flying / commander on 5 entries;
--   enemy_missile_shooting (NEW) for Missile Mirror.
--   Edited vs harness136: this banner, the pin and world rebases listed in
--   tools/make_harness137.py, the tooltip mirror, run_h137 and its call.
--   RED control: H137_LIVE / H137_ANN on docs/backups/round138/pre138_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 137 (round 138): THE RARER TARGET FILTERS, MISSILE MIRROR SHOOTING.
--   E1/E2 Eternal Gaze: an undead enemy in melee -> no cast; a living one -> cast.
--   P1/P2 Void Pendulum: a regular unit -> no cast; a Lord -> cast.
--   G1-G3 Entangle (ground): on the ground -> ground cast; flying -> none;
--   flight unreadable -> none.
--   M1-M4 Missile Mirror: a missile enemy whose ammunition drops every poll and
--   is not in melee -> cast; no drop -> none; a non-missile unit -> none; in
--   melee -> none.
--   RED (pre-138 = round 137): E1, P1, G3 cast; M1 casts nothing.
-- ============================================================================
function run_h137()
  local L137 = os.getenv("H137_LIVE") or LIVE
  local A137 = os.getenv("H137_ANN") or ANN
  local RED137 = (os.getenv("H137_LIVE") ~= nil) or (os.getenv("H137_ANN") ~= nil)
  local GAZE = "wh3_dlc29_lord_abilities_gaze_of_usirian"
  local VOID = "wh3_main_item_abilities_void_pendulum"
  local ENT = "wh2_dlc10_character_abilities_entangle"
  local MIR = "wh3_dlc24_unit_bound_missile_mirror"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local LIVING = "wh_main_emp_inf_swordsmen"
  local UNDEAD = "wh_main_vmp_inf_zombie"
  local CMDR = "wh2_dlc09_tmb_cha_arkhan_0"
  local GUNS = "wh_main_emp_inf_handgunners"
  local pre137 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 137 - section 0zi: the round-138 tokens ==")
  if not RED137 then
    for _, f in ipairs({ { name = "live", path = L137 }, { name = "ann", path = A137 } }) do
      local s = read_file(f.path)
      check("0zi " .. f.name .. ": the classes, the undead table and the shooting trigger are wired (21 target classes)",
        raw_find(s, 'if cls == "not_undead" then return FOURTH.class_keys.undead[t] ~= true end', 1, true) ~= nil
        and raw_find(s, 'if cls == "missile" then return FOURTH.class_keys.missile[t] == true end', 1, true) ~= nil
        and raw_find(s, "FOURTH.class_keys.undead = {", 1, true) ~= nil
        and raw_find(s, "enemy_missile_shooting = FOURTH.evaluate_enemy_missile_shooting,", 1, true) ~= nil
        and cp(s, "\t\ttarget_class = ") == 21)
    end
  end

  local FILES = { { path = A137, tag = "[annotated] " }, { path = L137, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function fires_of(W, key)
    local n = 0
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1 end end
    for _, f in ipairs(W.ground_fires or {}) do if f.key == key then n = n + 1 end end
    return n
  end
  local function enemy_unit(W, uid)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end
  local function world(wname, units, enemies, arm, key, PATH, TAG, fly)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    if fly ~= nil then
      local u = enemy_unit(W, enemies[1].uid)
      if u ~= nil then
        local b = (fly == true)
        u.is_currently_flying = function() return b end
      end
    end
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function one(b, key, cdist, edef)
    local e = { uid = b + 5, melee = true }
    for k, v in pairs(edef) do e[k] = v end
    return { { name = CASTER, uid = b, owns = { key }, melee = false, dist = cdist } }, { e }
  end
  local DROPS = { 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81, 80 }
  -- name, builder, marker, key, GREEN, RED (nil = not RED), flight stub
  local WORLDS = {
    { "E1. Eternal Gaze: an UNDEAD enemy in melee -> no cast",
      function(b) return one(b, GAZE, 20, { name = UNDEAD }) end, "gaze_of_usirian", GAZE, 0, 1, nil },
    { "E2. Eternal Gaze: a living enemy in melee -> ONE cast",
      function(b) return one(b, GAZE, 20, { name = LIVING }) end, "gaze_of_usirian", GAZE, 1, nil, nil },
    { "P1. Void Pendulum: a regular enemy unit in melee -> no cast",
      function(b) return one(b, VOID, 20, { name = LIVING }) end, "void_pendulum", VOID, 0, 1, nil },
    { "P2. Void Pendulum: an enemy Lord in melee -> ONE cast",
      function(b) return one(b, VOID, 20, { name = CMDR }) end, "void_pendulum", VOID, 1, nil, nil },
    { "G1. Entangle: an enemy on the ground in melee -> ONE ground cast",
      function(b) return one(b, ENT, 5, { name = LIVING }) end, "entangle", ENT, 1, nil, false },
    { "G2. Entangle: the enemy is flying -> no cast",
      function(b) return one(b, ENT, 5, { name = LIVING }) end, "entangle", ENT, 0, nil, true },
    { "G3. Entangle: the flight read is missing -> no cast",
      function(b) return one(b, ENT, 5, { name = LIVING }) end, "entangle", ENT, 0, 1, nil },
    { "M1. Missile Mirror: handgunners shooting (ammunition drops every poll), not in melee -> ONE cast",
      function(b) return one(b, MIR, 30, { name = GUNS, melee = false, ammo_start = 100, ammo_seq = DROPS }) end,
      "unit_bound_missile_mirror", MIR, 1, 0, nil },
    { "M2. Missile Mirror: handgunners whose ammunition never drops -> no cast",
      function(b) return one(b, MIR, 30, { name = GUNS, melee = false, ammo_start = 100, ammo_seq = { 100 } }) end,
      "unit_bound_missile_mirror", MIR, 0, nil, nil },
    { "M3. Missile Mirror: a non-missile unit whose ammunition drops -> no cast",
      function(b) return one(b, MIR, 30, { name = LIVING, melee = false, ammo_start = 100, ammo_seq = DROPS }) end,
      "unit_bound_missile_mirror", MIR, 0, nil, nil },
    { "M4. Missile Mirror: shooting handgunners in melee -> no cast",
      function(b) return one(b, MIR, 30, { name = GUNS, melee = true, ammo_start = 100, ammo_seq = DROPS }) end,
      "unit_bound_missile_mirror", MIR, 0, nil, nil },
  }

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED137 then want = w[6] end
      if want ~= nil then
        local base = 14000 + i * 10
        local units, enemies = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, w[7])
        if W ~= nil then
          local got = fires_of(W, w[4])
          check(TAG .. w[1]:sub(1, 2) .. (RED137 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got,
            got == want)
          done(got == want)
          tally(W)
        end
      end
    end
  end

  if RED137 then
    check("RED CONTROL (harness 137): the pre-138 build ignores the rarer target rules and never sees a shooting enemy - "
      .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  else
    check("HARNESS 137: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 22 and n_ok == 22)
  end
  print("== HARNESS 137 done: " .. (checks - pre137) .. " checks in this section ==")
end
'''

PIN_RULES = [
    (r"(trigger = \"enemy_engaged_or_shot\"'\)) == 47\b", r"\1 == 46"),
    (r"\bes = 47\b", "es = 46"),
    (r"(target_class = \"\)) == 16\b", r"\1 == 21"),
]
WORLD_RULES = [
    ('    if not boot97(W, PATH, TAG, uid, FAM_.marker, "FAM " .. wname .. " ") then return nil end\n    polln(W, 3)\n',
     '    if not boot97(W, PATH, TAG, uid, FAM_.marker, "FAM " .. wname .. " ") then return nil end\n'
     '    if FAM_.marker == "entangle" then\n'
     '      local e = enemy_of97(W, euid)\n'
     '      if e ~= nil then e.is_currently_flying = function() return false end end\n'
     '    end\n'
     '    polln(W, 3)\n'),
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
for a, b in WORLD_RULES:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
TIP_OLD = '    wavering_aura = "When armed, fires when this unit or a friendly unit near it is wavering",\n'
TIP_NEW = TIP_OLD + '    enemy_missile_shooting = "When armed, fires on the closest enemy missile unit in range that is shooting",\n'
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h135()\nrun_h136()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h137()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
