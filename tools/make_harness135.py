#!/usr/bin/env python3
"""Build harness135.lua from harness134.lua for round 136 (audit batch 5: the melee hexes leave the missile
arm; the immobilisers on the fast-enemy trigger; Spearfisher's Net's not-flying filter). Older harnesses are
never edited.

Pin rebases (code lines only; comment lines untouched):
  enemy_engaged_or_shot 70 -> 47, enemy_melee 14 -> 34, enemy_fast_near_ally 4 -> 7, target classes 15 -> 16;
  harness 97 FAM INSIDE r20 (Sadistic Snare, now on enemy_fast_near_ally): its enemy is also MOVING (run
  speed default 7 m/s, 9 m from the caster), so the inside world still proves the cast at the enemy.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_enemy_slows_harness134\harness134.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_melee_hexes_harness135\harness135.lua"

BANNER = """-- ============================================================================
-- HARNESS 135 - ROUND 136: AUDIT BATCH 5, THE MELEE HEXES.
--   enemy_melee gains 20; enemy_fast_near_ally gains Gaze of Fate, Sadistic
--   Snare and Spearfisher's Net; Spearfisher's Net gets target_class not_flying.
--   Edited vs harness134: this banner, the pin and world rebases listed in
--   tools/make_harness135.py, run_h135 and its call.
--   RED control: H135_LIVE / H135_ANN on docs/backups/round136/pre136_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 135 (round 136): AUDIT BATCH 5, THE MELEE HEXES.
--   0zg tokens. G1/G2 Gaze of Fate, S1 Sadistic Snare, N1-N3 Spearfisher's Net
--   (not flying / flying / flight unreadable), H1/H2 Torment Blade, V1/V2
--   Virulent Contagion, T1 Trophy Heads (Lord filter kept).
--   RED (pre-136 = round 135): G1 and N1 cast nothing; G2, H1 and V1 cast.
-- ============================================================================
function run_h135()
  local L135 = os.getenv("H135_LIVE") or LIVE
  local A135 = os.getenv("H135_ANN") or ANN
  local RED135 = (os.getenv("H135_LIVE") ~= nil) or (os.getenv("H135_ANN") ~= nil)
  local GAZE = "wh3_main_lord_abilities_gaze_of_fate"            -- 100 m -> bound 70
  local SNARE = "wh3_dlc23_lord_abilities_sadistic_snare"        -- 20 m -> bound 14
  local NET = "wh2_dlc11_lord_abilities_spearfishers_net"        -- 100 m -> bound 70, not flying
  local TORM = "wh3_main_weapon_abilities_torment_blade"         -- 50 m -> bound 35
  local VIR = "wh3_main_lord_abilities_virulent_contagion"       -- 200 m -> bound 140
  local TROPHY = "wh2_main_lord_abilities_trophy_heads"          -- 150 m -> bound 105, Lord/Hero only
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local PLAIN = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local CMDR = "wh2_dlc09_tmb_cha_arkhan_0"
  local pre135 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 135 - section 0zg: the round-136 tokens ==")
  if not RED135 then
    for _, f in ipairs({ { name = "live", path = L135 }, { name = "ann", path = A135 } }) do
      local s = read_file(f.path)
      check("0zg " .. f.name .. ": counts enemy_melee 34, enemy_fast_near_ally 7, enemy_engaged_or_shot 47, 16 target classes",
        cp(s, 'trigger = "enemy_melee"') == 34 and cp(s, 'trigger = "enemy_fast_near_ally"') == 7
        and cp(s, 'trigger = "enemy_engaged_or_shot"') == 47 and cp(s, "\t\ttarget_class = ") == 16)
      check("0zg " .. f.name .. ": the not_flying class reads is_currently_flying() and only an exact false passes",
        raw_find(s, 'if cls == "not_flying" then', 1, true) ~= nil
        and raw_find(s, "return ok_f and fly == false", 1, true) ~= nil
        and raw_find(s, 'target_class = "not_flying"', 1, true) ~= nil)
    end
  end

  local FILES = { { path = A135, tag = "[annotated] " }, { path = L135, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function fires_of(W, key)
    local n = 0
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1 end end
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
        if fly == "raise" then
          u.is_currently_flying = function() error("mock: is_currently_flying refused", 0) end
        else
          local b = (fly == true)
          u.is_currently_flying = function() return b end
        end
      end
    end
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function fast(b, key, cdist)
    return { { name = CASTER, uid = b, owns = { key }, melee = false, dist = cdist } },
      { { name = "enemy_cavalry", uid = b + 5, melee = false, moving = true, fast_speed = 7 } }
  end
  local function hex(b, key, ename, edef)
    local e = { name = ename, uid = b + 5, melee = true }
    for k, v in pairs(edef or {}) do e[k] = v end
    return { { name = CASTER, uid = b, owns = { key }, melee = false, dist = 20 } }, { e }
  end
  -- name, builder, marker, key, GREEN, RED (nil = not RED), flight stub
  local WORLDS = {
    { "G1. Gaze of Fate: an enemy moving at 7 m/s, 30 m away -> ONE cast at it",
      function(b) return fast(b, GAZE, 30) end, "gaze_of_fate", GAZE, 1, 0, nil },
    { "G2. Gaze of Fate: an enemy standing in melee -> no cast (no melee arm now)",
      function(b) return hex(b, GAZE, PLAIN) end, "gaze_of_fate", GAZE, 0, 1, nil },
    { "S1. Sadistic Snare: a fast enemy 10 m away (bound 14) -> ONE cast",
      function(b) return fast(b, SNARE, 10) end, "sadistic_snare", SNARE, 1, nil, nil },
    { "N1. Spearfisher's Net: a fast enemy on the ground (flying = false) -> ONE cast",
      function(b) return fast(b, NET, 30) end, "spearfishers_net", NET, 1, 0, false },
    { "N2. Spearfisher's Net: the fast enemy is flying -> no cast",
      function(b) return fast(b, NET, 30) end, "spearfishers_net", NET, 0, nil, true },
    { "N3. Spearfisher's Net: the flight read raises -> no cast",
      function(b) return fast(b, NET, 30) end, "spearfishers_net", NET, 0, nil, "raise" },
    { "H1. Torment Blade: the enemy is only under missile fire -> no cast",
      function(b) return hex(b, TORM, PLAIN, { melee = false, missile = true }) end, "torment_blade", TORM, 0, 1, nil },
    { "H2. Torment Blade: the enemy is in melee -> ONE cast",
      function(b) return hex(b, TORM, PLAIN) end, "torment_blade", TORM, 1, nil, nil },
    { "V1. Virulent Contagion: the enemy is only under missile fire -> no cast",
      function(b) return hex(b, VIR, PLAIN, { melee = false, missile = true }) end, "virulent_contagion", VIR, 0, 1, nil },
    { "V2. Virulent Contagion: the enemy is in melee -> ONE cast",
      function(b) return hex(b, VIR, PLAIN) end, "virulent_contagion", VIR, 1, nil, nil },
    { "T1. Trophy Heads: a Lord in melee -> ONE cast (the Lord filter stays)",
      function(b) return hex(b, TROPHY, CMDR) end, "trophy_heads", TROPHY, 1, nil, nil },
  }

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED135 then want = w[6] end
      if want ~= nil then
        local base = 13800 + i * 10
        local units, enemies = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, w[7])
        if W ~= nil then
          local got = fires_of(W, w[4])
          local a = (got == want)
          if a and want == 1 then
            local t = W.fires[1].target
            a = (W.fires[1].uid == base) and t ~= nil and t.zz_uid == base + 5
          end
          check(TAG .. w[1]:sub(1, 2) .. (RED135 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ((want == 1) and " (aimed at the enemy)" or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end

  if RED135 then
    check("RED CONTROL (harness 135): the pre-136 build casts the melee hexes at shot enemies and the immobilisers in melee - "
      .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  else
    check("HARNESS 135: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 22 and n_ok == 22)
  end
  print("== HARNESS 135 done: " .. (checks - pre135) .. " checks in this section ==")
end
'''

PIN_RULES = [
    (r"(trigger = \"enemy_engaged_or_shot\"'\)) == 70\b", r"\1 == 47"),
    (r"\bes = 70\b", "es = 47"),
    (r"(trigger = \"enemy_melee\"'\)) == 14\b", r"\1 == 34"),
    (r"(trigger = \"enemy_fast_near_ally\"'\)) == 4\b", r"\1 == 7"),
    (r"(target_class = \"\)) == 15\b", r"\1 == 16"),
]
WORLD_RULES = [
    ('enemies = { { name = (FAM_.marker == "headhunt") and "wh2_dlc09_tmb_cha_arkhan_0" or "orc_boyz", uid = euid, melee = true } },',
     'enemies = { { name = (FAM_.marker == "headhunt") and "wh2_dlc09_tmb_cha_arkhan_0" or "orc_boyz", uid = euid, melee = true,\n'
     '                    moving = (FAM_.marker == "sadistic_snare") } },'),
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
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h133()\nrun_h134()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h135()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
